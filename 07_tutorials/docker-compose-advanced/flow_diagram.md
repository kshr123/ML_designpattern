# Docker Compose実行フローの図解

## タイミング1: `docker compose up --build`

```
┌─────────────────────────────────────────────────────────┐
│ ユーザーがコマンド実行                                  │
│ $ docker compose up --build                             │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│ Step 1: docker-compose.yml を読み込む                   │
│ Docker Composeが設定ファイルをパース                    │
└────────────────┬────────────────────────────────────────┘
                 ↓
         サービスごとに処理
                 ↓
    ┌────────────┴────────────┐
    ↓                         ↓
┌─────────────────┐   ┌──────────────────┐
│ webサービス     │   │ redisサービス    │
│ build: .        │   │ image: redis     │
└────┬────────────┘   └────┬─────────────┘
     ↓                     ↓
┌─────────────────────────────────────────┐
│ Step 2a: Dockerfileを読み込む           │
│ → docker build -t web .                 │
│                                         │
│ Dockerfileの各命令を実行:               │
│ 1. FROM python:3.13-slim                │
│ 2. WORKDIR /app                         │
│ 3. COPY requirements.txt .              │
│ 4. RUN pip install ...                  │
│ 5. COPY app.py .                        │
│ 6. EXPOSE 8000                          │
│ 7. CMD ["uvicorn", ...]                 │
│                                         │
│ → イメージ "web" を作成                 │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Step 2b: Docker Hubからpull             │
│ → docker pull redis:7-alpine            │
│                                         │
│ → イメージ "redis:7-alpine" を取得      │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Step 3: ネットワークを作成              │
│ → docker network create ...             │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ Step 4: コンテナを起動                  │
│ → docker run ... web                    │
│ → docker run ... redis                  │
└─────────────────────────────────────────┘
```

## タイミング2: `docker compose up`（--buildなし）

```
┌─────────────────────────────────────────┐
│ $ docker compose up                     │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ イメージが存在するか確認                │
└────┬────────────────────────────────────┘
     ↓
     ┌────────────┴────────────┐
     ↓ YES                     ↓ NO
┌─────────────────┐   ┌──────────────────┐
│ 既存イメージ使用│   │ Dockerfileから   │
│ （ビルドしない）│   │ ビルド実行       │
└────┬────────────┘   └────┬─────────────┘
     └─────────────┬────────┘
                   ↓
          ┌──────────────────┐
          │ コンテナ起動     │
          └──────────────────┘
```

## タイミング3: `docker compose build`

```
┌─────────────────────────────────────────┐
│ $ docker compose build                  │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ イメージをビルドするだけ                │
│ （コンテナは起動しない）                │
│                                         │
│ → docker build -t web .                 │
└─────────────────────────────────────────┘
```

---

## 比較表: コマンドごとの動作

| コマンド | Dockerfileを読む？ | イメージを作る？ | コンテナを起動？ |
|---------|-------------------|----------------|----------------|
| `docker compose up --build` | ✅ 毎回 | ✅ Yes | ✅ Yes |
| `docker compose up` | ⚠️ イメージがない場合のみ | ⚠️ 必要な場合のみ | ✅ Yes |
| `docker compose build` | ✅ Yes | ✅ Yes | ❌ No |
| `docker compose start` | ❌ No | ❌ No | ✅ Yes（既存コンテナのみ） |

---

## 実際の例: webサービスのビルドプロセス

### 1. docker-compose.yml

```yaml
services:
  web:
    build: .        # ← カレントディレクトリのDockerfileを使う
    ports:
      - "8000:8000"
```

### 2. Dockerfileの内容

```dockerfile
FROM python:3.13-slim     # ベースイメージ
WORKDIR /app              # 作業ディレクトリ
COPY requirements.txt .   # ファイルコピー
RUN pip install ...       # パッケージインストール
COPY app.py .             # アプリコピー
CMD ["uvicorn", ...]      # 起動コマンド
```

### 3. 実行される内部コマンド

```bash
# docker compose up --build を実行すると...

# 1. Dockerfileからイメージをビルド
docker build -t docker-compose-advanced-web .

# 2. ビルドされたイメージからコンテナを起動
docker run -d \
  --name docker-compose-advanced-web-1 \
  -p 8000:8000 \
  -e APP_NAME=ProductionApp \
  -e API_KEY=xxx \
  docker-compose-advanced-web
```

---

## よくある誤解 vs 正しい理解

### ❌ 誤解1: "docker-compose.ymlにコードを書く"
**正しい理解**: docker-compose.ymlは**設定ファイル**。コードやアプリの実装はDockerfileで管理。

### ❌ 誤解2: "コンテナ起動時に毎回Dockerfileを読む"
**正しい理解**: Dockerfileは**イメージ作成時のみ**読まれる。コンテナ起動時は既存のイメージを使用。

### ❌ 誤解3: "Dockerfileがなくてもdocker compose upできる"
**正しい理解**: `build:`を使う場合はDockerfileが**必須**。`image:`を使う場合は不要。

---

## 🔍 buildディレクティブの詳細オプション

```yaml
services:
  web:
    build:
      context: .                    # Dockerfileの場所
      dockerfile: Dockerfile.dev    # 別名のDockerfileを使う
      args:                         # ビルド引数
        - PYTHON_VERSION=3.13
        - ENV=development
```
