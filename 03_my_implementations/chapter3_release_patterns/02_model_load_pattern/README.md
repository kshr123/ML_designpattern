# Model-Load Pattern（モデル読み込みパターン）

## 📖 概要

Model-Load Patternは、**モデルファイルを外部ストレージ（GCS等）から起動時に読み込む**デザインパターンです。Dockerイメージにモデルを焼き込まず、起動時にダウンロードすることで、イメージサイズを小さく保ち、モデルの更新を柔軟に行えます。

## 🎯 解決する課題

### Model-in-Imageパターンの課題

- **イメージサイズが大きい**: 大きなモデルファイルをDockerイメージに含めるため、イメージサイズが肥大化
- **モデル更新のたびにイメージ再ビルド**: モデルを更新するたびにDockerイメージを再ビルド・再デプロイ
- **複数モデルの管理が困難**: 複数のモデルバージョンを管理する場合、それぞれ別のイメージが必要

### Model-Load Patternの利点

- ✅ **イメージサイズが小さい**: モデルファイルを含まないため、イメージが軽量
- ✅ **モデル更新が柔軟**: GCS上のモデルを更新するだけで、イメージ再ビルド不要
- ✅ **複数モデルの管理が容易**: 環境変数でモデルパスを指定するだけで切り替え可能

## 🏗️ アーキテクチャ

### システム構成

```
┌─────────────────────────────────────────────────────────────┐
│                         Kubernetes Pod                       │
│                                                               │
│  ┌─────────────────────┐                                    │
│  │  InitContainer      │  1. Pod起動前に実行                │
│  │  (model-loader)     │                                     │
│  │                     │  2. GCSからモデルダウンロード       │
│  │  ┌───────────────┐ │                                     │
│  │  │ GCS Client    │ │  3. emptyDirに保存                 │
│  │  └───────────────┘ │                                     │
│  └──────────┬──────────┘                                    │
│             │                                                 │
│             ▼ モデルファイルをemptyDirに保存                 │
│  ┌─────────────────────┐                                    │
│  │   emptyDir          │  Pod内の一時共有ストレージ          │
│  │  (model-storage)    │                                     │
│  │                     │  ・Pod起動時に作成                  │
│  │  iris_svc.onnx      │  ・Pod削除時に消える                │
│  └──────────┬──────────┘                                    │
│             │                                                 │
│             ▼ モデルファイルを読み込み                        │
│  ┌─────────────────────┐                                    │
│  │  Main Container     │  4. emptyDirからモデル読み込み      │
│  │  (api)              │                                     │
│  │                     │  5. FastAPIでHTTP推論サービス提供  │
│  │  ┌───────────────┐ │                                     │
│  │  │ FastAPI       │ │                                     │
│  │  │ + ONNX Runtime│ │                                     │
│  │  └───────────────┘ │                                     │
│  └─────────────────────┘                                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                         ▲
                         │ HTTP Request
                         │
                    ┌────┴─────┐
                    │  Service │  LoadBalancer
                    │  (8000)  │
                    └──────────┘
```

### データフロー

```
1. Pod起動
   ↓
2. InitContainer起動
   ├─ GCSに接続
   ├─ モデルファイルをダウンロード (iris_svc.onnx)
   └─ emptyDirに保存 (/workdir/models/iris_svc.onnx)
   ↓
3. InitContainer完了
   ↓
4. Main Container起動
   ├─ emptyDirからモデル読み込み
   ├─ label.jsonを読み込み (/workdir/config/label.json)
   ├─ ONNX Runtimeでモデルをロード
   └─ FastAPI起動 (0.0.0.0:8000)
   ↓
5. Readiness Probe成功
   ↓
6. Serviceのエンドポイントに追加
   ↓
7. トラフィックを受付開始
```

## 🔧 技術スタック

### Python環境

- **Python**: 3.13
- **パッケージマネージャー**: uv
- **主要ライブラリ**:
  - FastAPI 0.111.0+ (Webフレームワーク)
  - uvicorn (ASGIサーバー)
  - ONNX Runtime 1.19.0+ (推論エンジン)
  - google-cloud-storage (GCSクライアント)
  - click (CLIフレームワーク)
  - numpy (数値計算)

### インフラ

- **コンテナ**: Docker
- **オーケストレーション**: Kubernetes (minikube)
- **ストレージ**: Google Cloud Storage (GCS)
- **負荷分散**: Kubernetes Service (LoadBalancer)
- **オートスケーリング**: HorizontalPodAutoscaler (HPA)

### Kubernetesリソース

| リソース | 役割 |
|---------|------|
| **Namespace** | リソースの論理的分離 |
| **Deployment** | Pod管理（レプリカ、ローリングアップデート） |
| **InitContainer** | Pod起動前にモデルをダウンロード |
| **emptyDir** | InitContainerとMain Container間でファイル共有 |
| **Service** | 負荷分散とネットワークアクセス |
| **HPA** | CPU/メモリベースの自動スケーリング |
| **Liveness Probe** | コンテナの生存確認（失敗で再起動） |
| **Readiness Probe** | トラフィック受付可能か確認 |

## 📁 プロジェクト構成

```
02_model_load_pattern/
├── SPECIFICATION.md          # 仕様書（要件、アーキテクチャ、API設計）
├── README.md                 # このファイル
├── pyproject.toml            # Pythonプロジェクト設定
├── uv.lock                   # 依存関係ロックファイル
│
├── src/                      # アプリケーションコード
│   ├── __init__.py
│   ├── main.py               # FastAPIアプリケーション
│   ├── api/                  # APIエンドポイント
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── prediction.py
│   ├── ml/                   # 機械学習モジュール
│   │   ├── __init__.py
│   │   └── prediction.py     # ONNX推論クラス
│   └── configurations/       # 設定管理
│       ├── __init__.py
│       └── constants.py
│
├── model_loader/             # InitContainer用コード
│   ├── main.py               # GCSダウンロードスクリプト
│   ├── entrypoint.sh         # エントリーポイント
│   ├── requirements.txt      # 依存関係
│   └── Dockerfile            # InitContainer用Dockerfile
│
├── models/                   # モデルファイル
│   └── label.json            # ラベルファイル（Dockerイメージに含む）
│
├── Dockerfile                # Main Container用Dockerfile
├── run.sh                    # FastAPI起動スクリプト
├── requirements.txt          # 依存関係
│
├── k8s/                      # Kubernetes設定ファイル
│   ├── namespace.yml         # Namespace定義
│   ├── deployment.yml        # Deployment定義
│   ├── service.yml           # Service定義
│   └── hpa.yml               # HPA定義
│
└── tests/                    # テストコード
    ├── __init__.py
    ├── test_model_loader.py      # InitContainerのテスト
    ├── test_data_loader.py       # データローダーのテスト
    ├── test_prediction.py        # 推論ロジックのテスト
    ├── test_api.py               # APIエンドポイントのテスト
    ├── test_configuration.py     # 設定のテスト
    └── test_results/             # テスト結果
        ├── README.md             # pytest出力の読み方
        └── full_test_results.txt # 全テスト結果（28/28成功、100%カバレッジ）
```

## 🚀 セットアップ

### 1. 環境構築

```bash
cd 03_my_implementations/chapter3_release_patterns/02_model_load_pattern

# Pythonバージョン確認
cat .python-version  # 3.13

# 仮想環境の作成と有効化
uv venv
source .venv/bin/activate

# 依存関係のインストール
uv pip install -r requirements.txt
uv pip install pytest pytest-cov  # テストツール
```

### 2. Dockerイメージのビルド

```bash
# minikubeのDocker環境を使用
eval $(minikube docker-env)

# InitContainer用イメージのビルド
docker build -t model-load-pattern-loader:latest -f model_loader/Dockerfile .

# Main Container用イメージのビルド
docker build -t model-load-pattern-api:latest -f Dockerfile .
```

### 3. Kubernetesへのデプロイ

```bash
# minikube起動
minikube start

# Namespaceの作成
kubectl apply -f k8s/namespace.yml

# Deploymentの作成
kubectl apply -f k8s/deployment.yml

# Serviceの作成
kubectl apply -f k8s/service.yml

# HPAの作成
kubectl apply -f k8s/hpa.yml

# Pod起動確認
kubectl get pods -n model-load-pattern -w
```

### 4. 動作確認

```bash
# ServiceのURLを取得（バックグラウンドで実行）
minikube service model-load-pattern-service -n model-load-pattern --url

# ヘルスチェック
curl -X GET http://127.0.0.1:63173/health
# → {"health":"ok"}

# Iris setosaの予測
curl -X POST http://127.0.0.1:63173/predict \
  -H "Content-Type: application/json" \
  -d '{"data": [[5.1, 3.5, 1.4, 0.2]]}'
# → {"prediction":[0.9709315896034241,0.015583082102239132,0.013485366478562355]}
# → setosa: 97.09% ✅

# Iris virginicaの予測
curl -X POST http://127.0.0.1:63173/predict \
  -H "Content-Type: application/json" \
  -d '{"data": [[6.3, 3.3, 6.0, 2.5]]}'
# → {"prediction":[0.01729963906109333,0.010310438461601734,0.972389817237854]}
# → virginica: 97.24% ✅
```

## 🧪 テスト

### テスト実行

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ付きテスト
pytest tests/ -v --cov=src --cov-report=html

# 結果: 28/28テスト成功、100%カバレッジ ✅
```

### テスト構成

| テストモジュール | テスト対象 | テスト数 |
|----------------|----------|---------|
| `test_model_loader.py` | InitContainer（GCSダウンロード） | 6 |
| `test_data_loader.py` | データローダー | 3 |
| `test_prediction.py` | ONNX推論ロジック | 8 |
| `test_api.py` | FastAPIエンドポイント | 9 |
| `test_configuration.py` | 設定管理 | 2 |

## 🎓 学んだこと

### 1. InitContainerの役割

InitContainerは、Main Containerの起動前に実行される特殊なコンテナです。今回の実装を通して以下を学びました：

- **用途**: 前処理、データダウンロード、設定ファイル生成等
- **実行順序**: InitContainer完了後にMain Container起動
- **データ共有**: emptyDirでMain Containerとデータを共有
- **失敗時の挙動**: InitContainerが失敗するとPod起動がブロックされる

### 2. emptyDirの特性

emptyDirは、Pod内のコンテナ間でデータを共有する一時ストレージです：

- **ライフサイクル**: Pod起動時に作成、Pod削除時に消える
- **用途**: 一時ファイル、キャッシュ、コンテナ間データ共有
- **注意点**: 既存ファイルを上書きする

**重要な教訓**: emptyDirをマウントすると、Dockerイメージに含まれていたファイルが隠される！

今回、`/workdir/models`をemptyDirでマウントしたため、Dockerイメージ内の`/workdir/models/label.json`が見えなくなりました。解決策として、`label.json`を別ディレクトリ（`/workdir/config/`）に配置しました。

### 3. Liveness ProbeとReadiness Probe

Kubernetesの2つのヘルスチェック機能を理解しました：

| Probe | 役割 | 失敗時の挙動 |
|-------|------|-------------|
| **Liveness Probe** | コンテナが生きているか確認 | コンテナを再起動 |
| **Readiness Probe** | トラフィックを受け付けられるか確認 | Serviceのエンドポイントから除外 |

**設定のベストプラクティス**:
- `initialDelaySeconds`: アプリケーション起動時間を考慮
- `periodSeconds`: チェック間隔（短すぎると負荷増）
- `timeoutSeconds`: タイムアウト時間（ネットワーク遅延を考慮）

### 4. HPA（HorizontalPodAutoscaler）

CPU/メモリベースの自動スケーリングを学びました：

```yaml
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # CPU使用率70%を超えたらスケールアウト

  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80  # メモリ使用率80%を超えたらスケールアウト
```

**注意点**:
- HPAを使用するには、Deployment でリソース`requests`が必須
- minikubeでは`metrics-server`が必要（アドオンで有効化）

### 5. Model-in-Image vs Model-Load

2つのパターンの使い分けを理解しました：

| 観点 | Model-in-Image | Model-Load |
|-----|----------------|-----------|
| **イメージサイズ** | 大きい（モデル込み） | 小さい（モデル別） |
| **起動速度** | 速い | 遅い（ダウンロード時間） |
| **モデル更新** | イメージ再ビルド必要 | GCS更新のみ |
| **複雑さ** | シンプル | やや複雑（InitContainer必要） |
| **適用場面** | 小規模モデル、頻繁な更新なし | 大規模モデル、頻繁な更新 |

### 6. uvicornとFastAPIの関係

**FastAPI**（フレームワーク）と**uvicorn**（ASGIサーバー）の役割分担を理解しました：

- **FastAPI**: アプリケーションのロジック、ルーティング、データ検証
- **uvicorn**: HTTP通信の処理、リクエスト/レスポンスのハンドリング

**レストランの例え**:
- FastAPI = レシピ本と調理道具
- uvicorn = レストランの建物と接客係

### 7. TDDサイクルの実践

今回のプロジェクトでTDD（Test-Driven Development）を実践しました：

1. **Red**: テストを先に書き、失敗することを確認
2. **Green**: テストを通すための最小限の実装
3. **Refactor**: コードを改善し、テストがGreenであることを確認

**成果**:
- 28/28テスト成功 ✅
- 100%カバレッジ ✅
- バグの早期発見
- リファクタリングの安全性

### 8. YAMLファイルのコメント

初見の人が理解できるように、すべてのYAMLファイルに詳細なコメントを記載しました：

- ✅ ファイル冒頭にヘッダーコメント（役割と目的）
- ✅ 各セクションにコメント（何を設定しているか）
- ✅ 重要な設定項目にinlineコメント

**教訓**: YAMLファイルは設定の意図が分かりにくいため、コメントでドキュメント化することが重要。

## 🐛 トラブルシューティング

### 問題1: Podが`CrashLoopBackOff`

**症状**:
```
NAME                                  READY   STATUS             RESTARTS      AGE
model-load-pattern-xxx-yyy            0/1     CrashLoopBackOff   4 (3s ago)    106s
```

**原因**: `label.json`ファイルが見つからない

**詳細**:
- Dockerイメージに`/workdir/models/label.json`をコピーしていた
- deployment.ymlで`/workdir/models`をemptyDirでマウントしていた
- emptyDirのマウントにより、Dockerイメージ内のファイルが隠された

**解決方法**:
```bash
# Dockerfile を修正
RUN mkdir -p /workdir/config
COPY models/label.json /workdir/config/label.json
ENV LABEL_FILEPATH=/workdir/config/label.json

# deployment.yml を修正
env:
  - name: LABEL_FILEPATH
    value: "/workdir/config/label.json"

# Dockerイメージ再ビルド
docker build -t model-load-pattern-api:latest -f Dockerfile .

# Deployment再適用
kubectl apply -f k8s/deployment.yml
```

### 問題2: HPAのメトリクスが`<unknown>`

**症状**:
```
NAME                     TARGETS                                     MINPODS   MAXPODS   REPLICAS
model-load-pattern-hpa   cpu: <unknown>/70%, memory: <unknown>/80%   2         5         2
```

**原因**: metrics-serverが起動していない

**解決方法**:
```bash
# metrics-serverアドオンを有効化
minikube addons enable metrics-server

# 確認
kubectl get deployment metrics-server -n kube-system
```

## 🔗 関連ドキュメント

- [SPECIFICATION.md](./SPECIFICATION.md) - 仕様書
- [Chapter 3 README](../README.md) - Chapter全体の概要
- [Model-in-Image Pattern](../01_model_in_image/README.md) - 前のパターン

## 📊 成果物

- ✅ TDD完了（28/28テスト成功、100%カバレッジ）
- ✅ Dockerイメージ作成（InitContainer + Main Container）
- ✅ Kubernetesマニフェスト作成（Namespace, Deployment, Service, HPA）
- ✅ 動作確認完了（/health, /predict）
- ✅ ドキュメント整備（SPECIFICATION.md, README.md, YAMLコメント）

**完了日**: 2025-11-13
