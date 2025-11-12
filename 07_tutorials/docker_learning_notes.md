# Docker学習ノート

**最終更新**: 2025-11-06
**目的**: Dockerチュートリアルで学んだ内容の復習用メモ

---

## 📚 学習済みステップ

### ✅ Step 1-3: Docker基礎（前回）
- Hello World
- Nginx
- Pythonアプリ（HTTPServer）

詳細は [docker_tutorial_session_log.md](./docker_tutorial_session_log.md) を参照

---

## ✅ Step 4: FastAPI in Docker（2025-11-06）

### 学んだこと

#### 1. requirements.txt
- **形式**: uvとpipの両方で使える共通フォーマット
- **pip**: `pip install -r requirements.txt`
- **uv**: `uv pip install -r requirements.txt`
- Dockerでは伝統的にpipを使うことが多い

#### 2. uvicornとは
- **役割**: FastAPIを動かすASGIサーバー
- **比喩**:
  - FastAPI = レストランのメニューとレシピ
  - uvicorn = レストランの建物と接客スタッフ
- Step 3のHTTPServerと同じ役割だが、より高機能

#### 3. 実装内容
- FastAPIアプリケーション（3つのエンドポイント）
  - `/` - ルートエンドポイント
  - `/health` - ヘルスチェック
  - `/items/{item_id}` - パラメータ付きエンドポイント
- Docker化
- ポートマッピング（8000:8000）
- 動作確認

---

## ✅ Step 5: ボリュームマウント（2025-11-06）

### 学んだこと

#### 1. ボリュームマウントの基本
- **構文**: `-v ホストのパス:コンテナのパス`
- **双方向**: ホスト↔コンテナで読み書き可能
- **永続化**: コンテナを削除してもデータは残る

#### 2. 実践例
1. **ホスト→コンテナの読み込み**
   - ホストで作成したファイルをコンテナから読める

2. **コンテナ→ホストの書き込み**
   - コンテナで作成したファイルがホストに保存される

3. **Pythonスクリプトのログ保存**
   - コンテナ内のアプリがログをホストに永続化

#### 3. ボリュームマウントの3つの用途

| 用途 | 説明 | 例 |
|------|------|-----|
| **データ永続化** | コンテナが削除されてもデータが残る | ログ、データベース、設定ファイル |
| **開発時のホットリロード** | コード変更が即座に反映 | app.pyをマウント → 編集 → 即反映 |
| **設定ファイルの注入** | 環境ごとに異なる設定を外部から注入 | 本番/開発/テスト環境 |

---

## ✅ Step 5 補足: 開発時のホットリロード（2025-11-06）

### 問題意識
> 「開発時はコードをマウントすることで、リビルド不要で開発できる」についてもっと詳しく知りたい

### 従来の方法 vs ボリュームマウント

#### 従来の方法（コードをイメージに焼き込む）
```dockerfile
COPY app.py .  # コードをイメージに含める
```
**変更のたびに**:
1. `docker build` ← 時間がかかる
2. `docker stop` + `docker rm`
3. `docker run`

#### ボリュームマウントを使う方法
```bash
docker run -v ./app.py:/app/app.py ...
```
**変更のたびに**:
1. ホストでファイルを編集
2. 自動的に反映（uvicorn --reload使用時）
3. または `docker restart` だけ（buildより速い）

### 実際のデモ結果

#### 変更前（バージョン1）
- `/` → `"バージョン1: 最初のメッセージ"`
- `/status` → `"version": "1.0"`

#### コード編集後（docker build なし！）
- `/` → `"🚀 バージョン2: コードを変更しました！リビルドなし！"`
- `/status` → `"version": "2.0", "hot_reload": "enabled"`
- `/new-endpoint` → 新しいエンドポイントが動作！

### ポイント
- Dockerfileで`COPY app.py`を**しない**
- uvicornに`--reload`オプションを付ける
- ボリュームマウントで起動
- コード編集 → `docker restart` → 反映！

---

## ✅ 重要な概念: docker restart の理解（2025-11-06）

### 質問
> restartはbuildされているものに対して行うコマンド？

### 答え
**No！** `docker restart`は**コンテナ**に対するコマンド。**イメージ（buildされたもの）**ではない。

### 用語の整理

```
【Dockerfile】
    ↓ docker build
【イメージ】← 読み取り専用の設計図/テンプレート
    ↓ docker run
【コンテナ】← 実行中のインスタンス/プロセス
    ↓ docker restart
【コンテナを停止→起動】
※イメージは変更されない
※ボリュームマウントされたファイルは最新版が読まれる
```

### 図解

```
┌─────────────────────────────────────────┐
│  Dockerfile                              │
│  ├─ FROM python:3.13-slim               │
│  ├─ COPY requirements.txt .             │
│  └─ RUN pip install ...                 │
└─────────────────────────────────────────┘
              ↓ docker build
┌─────────────────────────────────────────┐
│  イメージ (fastapi-dev:latest)          │ ← 設計図/テンプレート
│  - 読み取り専用                          │
│  - 何度でも使い回せる                    │
└─────────────────────────────────────────┘
              ↓ docker run
┌─────────────────────────────────────────┐
│  コンテナ (fastapi-dev)                  │ ← 実行中のインスタンス
│  - 読み書き可能                          │
│  - プロセスが動いている                  │
│  - ボリュームマウント設定を持つ          │
└─────────────────────────────────────────┘
              ↓ docker restart
         【コンテナを停止→起動】
         ※イメージは変更されない
```

### docker restart の動作

1. **コンテナのプロセスを停止**（`docker stop`相当）
2. **同じコンテナを再び起動**（`docker start`相当）

**重要ポイント**:
- ✅ コンテナの設定（ボリュームマウント、環境変数など）は**保持される**
- ✅ ボリュームマウントされたファイルは**最新の状態で読み込まれる**
- ✅ イメージは**変更されない**
- ❌ コンテナは**再作成されない**（同じコンテナを再利用）

### 使い分けの比較表

| コマンド | 対象 | 目的 | いつ使う |
|---------|------|------|---------|
| `docker build` | **Dockerfile** → イメージ | イメージを作成/更新 | Dockerfile, requirements.txt を変更したとき |
| `docker run` | イメージ → **コンテナ** | 新しいコンテナを作成・起動 | 初回起動、または設定を変えたいとき |
| `docker restart` | **コンテナ** | コンテナを再起動 | マウントしたファイルを再読み込みしたいとき |
| `docker stop` | **コンテナ** | コンテナを停止 | 一時的に止めたいとき |
| `docker start` | **コンテナ** | 停止中のコンテナを起動 | 停止したコンテナを再開したいとき |

### 変更内容別の対応

| 変更内容 | 必要なコマンド | 理由 |
|---------|--------------|------|
| **アプリのコード**（app.py） | `docker restart` のみ | ボリュームマウントでホストのファイルを参照しているから |
| **依存関係**（requirements.txt） | `docker build` → `docker run` | パッケージはイメージに焼き込まれるから |
| **Dockerfile** | `docker build` → `docker run` | イメージの構造が変わるから |

---

## 🎓 開発フローのまとめ

### 初回セットアップ
```bash
# 1. イメージをビルド
docker build -t fastapi-dev .

# 2. イメージからコンテナを作成・起動
docker run -d --name fastapi-dev -v ./app.py:/app/app.py fastapi-dev
```

### コード変更時（ボリュームマウント使用）
```bash
# 1. ホストでapp.pyを編集
nano app.py

# 2. コンテナを再起動（buildは不要！）
docker restart fastapi-dev
```

### 依存関係変更時
```bash
# 1. requirements.txtを編集
nano requirements.txt

# 2. イメージを再ビルド
docker build -t fastapi-dev .

# 3. 古いコンテナを削除して新しいコンテナを起動
docker stop fastapi-dev && docker rm fastapi-dev
docker run -d --name fastapi-dev -v ./app.py:/app/app.py fastapi-dev
```

---

## 💡 開発時の注意点

### --reloadオプション
- **開発環境**: `uvicorn app:app --reload` ← ファイル変更を自動検知
- **本番環境**: `uvicorn app:app` ← reloadなし（セキュリティ・パフォーマンス）

### ボリュームマウントの使い分け
- **開発**: コードをマウント → 編集が即反映
- **本番**: コードをイメージに焼き込む → セキュリティ・パフォーマンス重視

---

---

## ✅ Step 6: Docker Compose（2025-11-06）

### 学んだこと

#### 1. Docker Composeとは
- **目的**: 複数のコンテナを一括で管理
- **使用例**: WebアプリとDB、APIとRedis など
- **メリット**:
  - 1つのコマンドで複数サービスを起動/停止
  - サービス間の依存関係を定義できる
  - ネットワークが自動で構築される

#### 2. 実装内容

**構成**: FastAPI + Redis（アクセスカウンター）

**作成したファイル** (`07_tutorials/docker-compose-demo/`):
- `app.py` - FastAPIアプリ（Redisと連携）
- `requirements.txt` - 依存関係（fastapi, uvicorn, redis）
- `Dockerfile` - FastAPIのイメージ定義
- `docker-compose.yml` - サービス定義（web, redis）

#### 3. docker-compose.yml の構造

```yaml
version: '3.8'

services:
  web:                      # サービス名
    build: .                # Dockerfileから構築
    ports:
      - "8000:8000"         # ポートマッピング
    environment:
      - REDIS_HOST=redis    # 環境変数
    depends_on:
      - redis               # 依存関係
    volumes:
      - ./app.py:/app/app.py  # ボリュームマウント

  redis:                    # サービス名
    image: redis:7-alpine   # 公式イメージ
    ports:
      - "6379:6379"
```

#### 4. 主要コマンド

| コマンド | 説明 |
|---------|------|
| `docker compose up -d --build` | ビルドして起動（バックグラウンド） |
| `docker compose ps` | 実行中のサービス一覧 |
| `docker compose logs` | 全サービスのログ表示 |
| `docker compose logs <service>` | 特定サービスのログ |
| `docker compose stop` | サービスを停止 |
| `docker compose down` | サービスを停止して削除 |
| `docker compose restart` | サービスを再起動 |

#### 5. 動作確認結果

✅ **正常に動作確認できたこと**:
- FastAPIとRedisが正常に起動
- サービス間の通信が成功
- アクセスカウンター機能が動作
  - `/count` を叩くたびに数字が増加（1, 2, 3...）
  - `/reset` でカウンターがリセット
  - Redisにデータが永続化されている

#### 6. サービス名での接続

**重要な概念**:
```python
# app.py内
redis_host = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=redis_host, ...)
```

- Docker Composeでは**サービス名**がホスト名になる
- `redis`というサービス名で定義 → `redis`というホスト名で接続可能
- 手動でIPアドレスを指定する必要がない

#### 7. Docker Compose vs 手動起動

**手動で起動する場合**:
```bash
docker network create mynetwork
docker run -d --name redis --network mynetwork redis:7-alpine
docker run -d --name web --network mynetwork -p 8000:8000 fastapi-app
```

**Docker Composeを使う場合**:
```bash
docker compose up -d
```

→ **圧倒的に簡単！**

---

## 🎯 重要な概念: クライアント vs サーバー（2025-11-06）

### 質問
> `app.py`で`import redis`しているけど、`docker-compose.yml`でも`redis`を記載しないといけないの？

### 答え
**両方必要！** この2つの`redis`は**全く別物**です。

### 2つのredisの違い

#### 1. `import redis` → Pythonライブラリ（クライアント）

```python
import redis  # ← Redisクライアントライブラリ
r = redis.Redis(host="redis", port=6379)
```

- **種類**: クライアントライブラリ（接続ツール）
- **インストール**: `pip install redis` (requirements.txt)
- **役割**: Redisサーバーに**接続**してコマンドを送る
- **例**: 📱 電話機（サーバーに電話をかける道具）

#### 2. `docker-compose.yml`の`redis:` → Redisサーバー

```yaml
services:
  redis:  # ← Redisサーバー（サービス）
    image: redis:7-alpine
```

- **種類**: サーバー本体（データベース）
- **起動**: `docker compose up -d`
- **役割**: データを**保存・管理**する
- **例**: 🏢 電話交換局（実際に通信を処理する場所）

### クライアント-サーバー構成

```
┌─────────────────────────────────────┐
│  webコンテナ（FastAPI）             │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ app.py                      │   │
│  │                             │   │
│  │ import redis  ← クライアント │   │
│  │ r = redis.Redis(            │   │
│  │   host="redis"  ← 接続先    │   │
│  │ )                           │   │
│  │                             │   │
│  │ r.incr("visit_count")       │   │
│  └─────────────────────────────┘   │
│              ↓ コマンド送信         │
└──────────────┼──────────────────────┘
               ↓
┌──────────────┼──────────────────────┐
│  redisコンテナ（Redisサーバー）     │
│              ↓                      │
│  ┌─────────────────────────────┐   │
│  │ Redis Server                │   │
│  │                             │   │
│  │ メモリに保存:               │   │
│  │ visit_count = 5             │   │
│  │                             │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### 両方必要な理由

| 必要なもの | 場所 | 役割 |
|-----------|------|------|
| redisライブラリ | `requirements.txt` | クライアント（接続ツール） |
| redisサーバー | `docker-compose.yml` | サーバー（データ保存） |

**電話のアナロジー**:
- 📱 電話機（クライアント）だけあっても、交換局（サーバー）がなければ通話できない
- 🏢 交換局（サーバー）だけあっても、電話機（クライアント）がなければ使えない

### Redisの特徴

| 項目 | 説明 |
|------|------|
| **保存場所** | **メモリ（RAM）** に保存 |
| **速度** | 超高速（ディスクアクセス不要） |
| **データ型** | 文字列、リスト、セット、ハッシュなど |
| **用途** | キャッシュ、セッション管理、カウンター、ランキング |
| **永続化** | オプションでディスクにも保存可能 |

### 今回の実装での使い方

```python
# カウンターをインクリメント
count = r.incr("visit_count")  # visit_countを1増やす

# カウンターをリセット
r.set("visit_count", 0)
```

**データの保存場所**:
- ✅ Redisコンテナの**メモリ内**
- ⚠️ コンテナを削除すると**データも消える**（今回はボリューム未設定）

---

## 🎯 Step 6 補足: 自動リロードの制限（2025-11-06）

### 問題
ボリュームマウントと`--reload`オプションを設定したが、macOSのDocker Desktop環境では自動リロードが機能しない。

### 原因
macOSのファイルシステムとDocker Desktopの同期が遅く、WatchFilesがリアルタイムで変更を検知できない（既知の問題）。

### 確認できたこと
- ✅ **ボリュームマウント**: 正常に機能（ファイルは同期されている）
- ✅ **手動リロード**: `docker compose restart web` で変更が反映される
- ✅ **uvicorn --reload**: 設定は正しい（Linux環境では機能する）

### 実用的な解決策

**開発時の推奨ワークフロー**:
```bash
# コードを変更後、手動でリロード
docker compose restart web

# または、ホスト側で直接FastAPIを動かす（Dockerは本番のみ）
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

---

## ⚠️ トラブルシューティング

### Bashコマンドが実行できなくなった（2025-11-06）

**症状**:
- すべてのBashコマンドが`Exit code 1`で失敗
- `echo "test"`のような最もシンプルなコマンドも失敗

**原因**:
- バックグラウンドで実行中のBashプロセス（minikube service）が原因の可能性
- セッション状態が壊れている

**対処法**:
1. Claude Codeセッションを再起動
2. バックグラウンドプロセスをクリーンアップ

**回避策**:
- Readツール、Writeツール、Editツールは正常に動作
- ファイル操作は問題なし

---

## 📝 次のステップ（セッション再起動後）

### Step 6 の続き
- [ ] Docker Composeで起動中のサービスを確認
- [ ] ボリュームマウントでコードを変更して反映確認
- [ ] docker compose down でクリーンアップ

### Step 7以降
- [ ] Docker Compose の高度な使い方（ネットワーク、ボリューム）
- [ ] 環境変数ファイル（.env）の使い方
- [ ] 本番環境向けの設定

---

## 🔄 セッション再開時の手順

### 1. 状況確認
```bash
cd /Users/kotaro/Desktop/dev/ML_designpattern/07_tutorials/docker-compose-demo
docker compose ps
docker compose logs
```

### 2. サービスが停止している場合
```bash
docker compose up -d
```

### 3. サービスが起動中の場合
そのまま続きから開始

### 4. クリーンアップが必要な場合
```bash
docker compose down
docker compose down --volumes  # ボリュームも削除
```

---

## ✅ Step 7: 環境変数ファイル（.env）の使い方（2025-11-06）

### 学んだこと

#### 1. .envファイルの役割

環境変数を外部ファイルで管理することで、**機密情報を安全に管理**し、**環境ごとに設定を切り替える**ことができる。

| ファイル | 用途 | Gitで管理 |
|---------|------|----------|
| `.env` | 実際の機密情報（API Key、パスワードなど） | ❌ No (.gitignoreに追加) |
| `.env.example` | サンプル（チーム共有用） | ✅ Yes |

#### 2. docker-compose.ymlでの環境変数の使い方

**方法1: 個別に指定**
```yaml
environment:
  - APP_NAME=${APP_NAME}
  - API_KEY=${API_KEY}
```

**方法2: env_fileで一括指定（シンプル）**
```yaml
env_file:
  - .env
```

#### 3. 実装内容

**作成したファイル** (`07_tutorials/docker-compose-advanced/`):
- `app.py` - 環境変数を使うFastAPIアプリ
- `.env` - 実際の機密情報（Gitignore）
- `.env.example` - サンプルファイル（Git管理）
- `.gitignore` - .envを除外

**機能**:
- ✅ 環境変数から設定を読み込み（APP_NAME, API_KEY, DATABASE_URL, DEBUG_MODE）
- ✅ APIキー認証機能
- ✅ 機密情報のマスク表示
- ✅ .env編集でdocker compose down/upで環境切り替え

#### 4. セキュリティのポイント

- ✅ `.gitignore`に`.env`を追加
- ✅ `.env.example`をサンプルとして提供
- ✅ 機密情報はマスク表示
- ✅ 本番環境では安全な値を使用

---

## 🎯 重要な概念: Dockerfileとdocker-compose.ymlの関係（2025-11-06）

### 質問
> Docker Composeを使うときのDockerfileの用途は？どのタイミングで何がDockerfileを読み込んでいるの？

### 答え

**Dockerfileを読み込むのは**: `docker compose up --build` または `docker compose build` を実行したとき

**誰が読み込むか**: Docker Composeが`build:`ディレクティブを見つけたら、`docker build`コマンドを**内部的に実行**する

---

### docker-compose.ymlの2つのパターン

#### パターン1: `build:` を使う（Dockerfileから構築）

```yaml
services:
  web:
    build: .  # ← Dockerfileからイメージを構築
    ports:
      - "8000:8000"
```

**内部的に実行される**:
```bash
docker build -t docker-compose-advanced-web .
docker run -d -p 8000:8000 docker-compose-advanced-web
```

#### パターン2: `image:` を使う（既存イメージを使用）

```yaml
services:
  redis:
    image: redis:7-alpine  # ← Docker Hubから既存イメージを取得
    ports:
      - "6379:6379"
```

**内部的に実行される**:
```bash
docker pull redis:7-alpine  # Docker Hubからダウンロード
docker run -d -p 6379:6379 redis:7-alpine
```

---

### 実行タイミング

| コマンド | Dockerfileを読む？ | イメージを作る？ | コンテナを起動？ |
|---------|-------------------|----------------|----------------|
| `docker compose up --build` | ✅ 毎回 | ✅ Yes | ✅ Yes |
| `docker compose up` | ⚠️ イメージがない場合のみ | ⚠️ 必要な場合のみ | ✅ Yes |
| `docker compose build` | ✅ Yes | ✅ Yes | ❌ No |
| `docker compose start` | ❌ No | ❌ No | ✅ Yes（既存コンテナのみ） |

---

### 実行フロー（docker compose up --build）

```
ユーザー: docker compose up --build
    ↓
Step 1: docker-compose.yml を読み込む
    ↓
Step 2a: build: . を発見
    → Dockerfileを読み込む
    → docker build -t web .
    → イメージ "web" を作成
    ↓
Step 2b: image: redis:7-alpine を発見
    → docker pull redis:7-alpine
    ↓
Step 3: ネットワークを作成
    ↓
Step 4: コンテナを起動
    → docker run ... web
    → docker run ... redis
```

---

### Dockerfileのビルドプロセス

**ビルドログの例**:
```
#2 [internal] load build definition from Dockerfile  ← Dockerfileを読み込み
#7 [1/5] FROM docker.io/library/python:3.13-slim    ← ベースイメージ
#9 [2/5] WORKDIR /app                               ← 作業ディレクトリ
#8 [3/5] COPY requirements.txt .                    ← requirements.txtコピー
#10 [4/5] RUN pip install --no-cache-dir ...        ← パッケージインストール
#11 [5/5] COPY app.py .                             ← app.pyコピー
#12 exporting to image                              ← イメージ作成
```

**重要ポイント**:
- `CACHED` と表示されるステップは前回のビルド結果を再利用
- Dockerのレイヤーキャッシュが機能

---

### Dockerfileとdocker-compose.ymlの役割分担

| ファイル | 役割 | 例 |
|---------|------|-----|
| **Dockerfile** | イメージを作るための**設計図/レシピ** | `FROM python:3.13-slim`<br>`RUN pip install ...` |
| **docker-compose.yml** | 複数サービスを**まとめて管理する設定ファイル** | `build: .`<br>`ports: "8000:8000"` |

---

### build vs image の使い分け

| 用途 | 使うディレクティブ | 例 |
|------|-------------------|-----|
| **自分でカスタマイズしたイメージ** | `build: .` | FastAPIアプリ、カスタムPythonアプリ |
| **公式イメージをそのまま使う** | `image: redis:7-alpine` | Redis、PostgreSQL、Nginx |

---

### よくある誤解と正しい理解

#### ❌ 誤解1: "docker-compose.ymlにコードを書く"
**✅ 正しい理解**: docker-compose.ymlは**設定ファイル**。コードやアプリの実装はDockerfileで管理。

#### ❌ 誤解2: "コンテナ起動時に毎回Dockerfileを読む"
**✅ 正しい理解**: Dockerfileは**イメージ作成時のみ**読まれる。コンテナ起動時は既存のイメージを使用。

#### ❌ 誤解3: "Dockerfileを変更したら、docker compose upで反映される"
**✅ 正しい理解**: `docker compose up`だけでは反映されない。`--build`フラグが必要。

```bash
# ❌ Dockerfileの変更が反映されない
docker compose up

# ✅ Dockerfileの変更が反映される
docker compose up --build
```

---

## 📝 Docker学習のまとめ（2025-11-06）

### 学習完了項目

#### ✅ Docker基礎（Step 1-3）
- Hello World
- Nginx
- Pythonアプリ（HTTPServer）

#### ✅ Step 4: FastAPI in Docker
- requirements.txt
- uvicornの役割
- Docker化
- ポートマッピング

#### ✅ Step 5: ボリュームマウント
- データ永続化
- 開発時のホットリロード
- 設定ファイルの注入

#### ✅ Step 6: Docker Compose基礎
- 複数コンテナの一括管理（FastAPI + Redis）
- サービス間通信（サービス名でDNS解決）
- 依存関係の定義（depends_on）
- クライアント vs サーバーの理解（redisライブラリ vs Redisサーバー）

#### ✅ Step 7: 環境変数ファイル（.env）
- 機密情報の安全な管理
- 環境ごとの設定切り替え
- .gitignoreでセキュリティ確保
- APIキー認証の実装

#### ✅ Dockerfileとdocker-compose.ymlの関係
- ビルドタイミングの理解
- build vs imageの使い分け
- 実行フローの把握

---

### 次のステップ

**Kubernetes（K8s）への移行**:
- ✅ Docker基礎を習得
- ✅ Docker Composeで複数コンテナ管理を理解
- → **次**: Kubernetesで本番環境向けのオーケストレーション

---

## 📚 関連ファイル

- [Dockerチュートリアル本体](./01_docker_basics.md)
- [セッションログ（社内デモ用）](./docker_tutorial_session_log.md)
- [Model-in-Image Pattern実装](../03_my_implementations/chapter3_release_patterns/01_model_in_image/)
- [Docker Compose基礎デモ](./docker-compose-demo/)
- [Docker Compose高度な機能デモ](./docker-compose-advanced/)
