# Model-in-Image Pattern

モデルファイルをDockerイメージに組み込むリリースパターンの実装

## 📋 概要

このパターンでは、学習済みモデルファイル（ONNX）とラベルファイルをDockerイメージに含めて、デプロイ時にイメージをPullするだけでモデルと推論サーバーを配備できるようにします。

### Model-in-Image Patternの特徴

**メリット** ✅
- モデルとアプリケーションのバージョンが一致する
- 起動が高速（外部からのモデルダウンロードが不要）
- シンプルなデプロイメントフロー
- オフライン環境でも動作可能

**デメリット** ⚠️
- イメージサイズが大きくなる
- モデル更新のたびにイメージの再ビルドが必要
- モデルファイルが大きい場合、ビルド・プッシュに時間がかかる

## 🎯 実装内容

- **モデル**: Chapter 2で学習したIris SVM分類モデル（ONNX形式）
- **API**: FastAPI による REST API
- **推論ランタイム**: ONNX Runtime
- **コンテナ**: Docker
- **オーケストレーション**: Kubernetes (minikube)

## 📁 プロジェクト構成

```
01_model_in_image/
├── SPECIFICATION.md          # 仕様書
├── README.md                 # このファイル
├── pyproject.toml            # 依存関係管理
├── Dockerfile                # Dockerイメージ定義
├── .dockerignore             # Docker除外ファイル
├── run.sh                    # アプリケーション起動スクリプト
├── src/
│   ├── model_in_image/
│   │   ├── __init__.py
│   │   ├── configurations.py # 設定管理
│   │   ├── data_models.py    # Pydanticモデル
│   │   ├── prediction.py     # 推論ロジック
│   │   └── app.py            # FastAPI アプリケーション
├── models/
│   ├── iris_svc.onnx         # 学習済みモデル
│   └── label.json            # ラベルマッピング
├── k8s/
│   ├── namespace.yml         # Kubernetes Namespace
│   ├── deployment.yml        # Deployment定義
│   ├── service.yml           # Service定義（NodePort）
│   └── hpa.yml               # Horizontal Pod Autoscaler
└── tests/
    ├── test_01_configurations.py
    ├── test_02_data_models.py
    ├── test_03_prediction.py
    └── test_04_app.py
```

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────────┐
│         Kubernetes Cluster (minikube)       │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │     Namespace: model-in-image         │ │
│  │                                       │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │   Service (NodePort: 30080)     │ │ │
│  │  └──────────────┬──────────────────┘ │ │
│  │                 │                     │ │
│  │  ┌──────────────▼──────────────────┐ │ │
│  │  │   Deployment (replicas: 2)      │ │ │
│  │  │                                 │ │ │
│  │  │  ┌───────────┐  ┌───────────┐  │ │ │
│  │  │  │  Pod 1    │  │  Pod 2    │  │ │ │
│  │  │  │           │  │           │  │ │ │
│  │  │  │ FastAPI   │  │ FastAPI   │  │ │ │
│  │  │  │ ONNX RT   │  │ ONNX RT   │  │ │ │
│  │  │  │ Model ✓   │  │ Model ✓   │  │ │ │
│  │  │  └───────────┘  └───────────┘  │ │ │
│  │  └─────────────────────────────────┘ │ │
│  │                                       │ │
│  │  ┌─────────────────────────────────┐ │ │
│  │  │   HPA (2-10 replicas)           │ │ │
│  │  └─────────────────────────────────┘ │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
          │
          │ NodePort :30080
          ▼
    Client (curl)
```

## 🚀 セットアップと実行

### 1. 環境準備

```bash
# Python 3.13の仮想環境を作成
uv venv
source .venv/bin/activate

# 依存関係をインストール
uv pip install fastapi uvicorn[standard] numpy scikit-learn onnxruntime pydantic python-dotenv pytest pytest-cov black ruff mypy
```

### 2. テスト実行

```bash
# すべてのテストを実行
pytest tests/ -v

# カバレッジ付きテスト
pytest tests/ -v --cov=src --cov-report=html
```

### 3. Dockerイメージのビルド

```bash
# イメージをビルド
docker build -t model-in-image-pattern:v1.0 .

# イメージを確認
docker images | grep model-in-image-pattern
```

### 4. ローカルでのテスト

```bash
# コンテナを起動
docker run -d -p 8000:8000 --name model-in-image-test model-in-image-pattern:v1.0

# ヘルスチェック
curl http://localhost:8000/health

# 推論テスト
curl -X POST http://localhost:8000/predict/label \
  -H "Content-Type: application/json" \
  -d '{"data": [[5.1, 3.5, 1.4, 0.2]]}'

# コンテナを停止・削除
docker stop model-in-image-test
docker rm model-in-image-test
```

### 5. Kubernetesへのデプロイ

```bash
# minikubeを起動
/opt/homebrew/bin/minikube start

# Dockerイメージをminikubeにロード
/opt/homebrew/bin/minikube image load model-in-image-pattern:v1.0

# Kubernetesリソースを作成
/opt/homebrew/bin/kubectl apply -f k8s/namespace.yml
/opt/homebrew/bin/kubectl apply -f k8s/deployment.yml
/opt/homebrew/bin/kubectl apply -f k8s/service.yml
/opt/homebrew/bin/kubectl apply -f k8s/hpa.yml

# デプロイメント状態を確認
/opt/homebrew/bin/kubectl get all -n model-in-image

# サービスURLを取得（別ターミナルで実行）
/opt/homebrew/bin/minikube service model-in-image-service -n model-in-image --url
# 出力例: http://127.0.0.1:xxxxx

# APIテスト
curl http://127.0.0.1:xxxxx/health
curl -X POST http://127.0.0.1:xxxxx/predict/label \
  -H "Content-Type: application/json" \
  -d '{"data": [[5.1, 3.5, 1.4, 0.2]]}'
```

## 📊 API仕様

### ヘルスチェックエンドポイント

```bash
GET /health

# レスポンス
{
  "health": "ok"
}
```

### 推論エンドポイント（ラベル）

```bash
POST /predict/label
Content-Type: application/json

# リクエスト
{
  "data": [[5.1, 3.5, 1.4, 0.2]]
}

# レスポンス
{
  "prediction": "setosa"
}
```

### 推論エンドポイント（確率付き）

```bash
POST /predict/proba

# リクエスト
{
  "data": [[5.1, 3.5, 1.4, 0.2]]
}

# レスポンス
{
  "prediction": [
    {
      "label": "setosa",
      "probability": 0.99
    },
    {
      "label": "versicolor",
      "probability": 0.01
    },
    {
      "label": "virginica",
      "probability": 0.00
    }
  ]
}
```

## 🧪 検証結果

### デプロイメント成功確認

```bash
$ /opt/homebrew/bin/kubectl get all -n model-in-image

NAME                                            READY   STATUS    RESTARTS   AGE
pod/model-in-image-deployment-cd779d4d6-96zfv   1/1     Running   0          41s
pod/model-in-image-deployment-cd779d4d6-nsj7k   1/1     Running   0          41s

NAME                             TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
service/model-in-image-service   NodePort   10.109.140.40   <none>        8000:30080/TCP   27s

NAME                                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/model-in-image-deployment   2/2     2            2           41s
```

### 推論テスト結果

```bash
# Setosa
$ curl -X POST http://127.0.0.1:63875/predict/label \
  -H "Content-Type: application/json" \
  -d '{"data": [[5.1, 3.5, 1.4, 0.2]]}'
{"prediction":"setosa"}

# Versicolor
$ curl -X POST http://127.0.0.1:63875/predict/label \
  -H "Content-Type: application/json" \
  -d '{"data": [[6.7, 3.1, 4.7, 1.5]]}'
{"prediction":"versicolor"}

# Virginica
$ curl -X POST http://127.0.0.1:63875/predict/label \
  -H "Content-Type: application/json" \
  -d '{"data": [[7.2, 3.6, 6.1, 2.5]]}'
{"prediction":"virginica"}
```

すべての品種で正しい推論結果が得られました ✅

## 💡 学んだこと

### 1. Model-in-Image Patternの設計

- モデルファイルをイメージに含めることで、バージョン管理がシンプルになる
- アプリケーションとモデルの整合性が保証される
- ただし、モデルサイズが大きいとビルド時間が長くなる

### 2. Dockerイメージ最適化

- **マルチステージビルド**: 不要なファイルを含めない
- **.dockerignore**: テストファイルやドキュメントを除外
- **PYTHONPATH**: `pip install -e .`の代わりにPYTHONPATHを使用
  - README.mdがdockerignoreされているため、hatchlingのビルドが失敗する問題を回避

### 3. Kubernetesのリソース設計

- **Deployment**: レプリカ数を指定してスケールアウト
- **Service (NodePort)**: 外部からのアクセスを可能にする
- **HPA**: CPU/メモリ使用率に基づいて自動スケーリング
- **リソース制限**: requests/limitsで適切なリソース配分

### 4. ヘルスチェックの重要性

- **Dockerのヘルスチェック**: コンテナの健全性を監視
- **KubernetesのProbe**:
  - `livenessProbe`: コンテナが動作しているか
  - `readinessProbe`: トラフィックを受け入れられるか

### 5. トラブルシューティング

#### ModuleNotFoundError
- **問題**: `ModuleNotFoundError: No module named 'model_in_image'`
- **原因**: Pythonモジュールのインポートパスが正しくない
- **解決**: `ENV PYTHONPATH=/app/src` をDockerfileに追加

#### README.mdが必要
- **問題**: `pip install -e .`でREADME.mdが見つからない
- **原因**: .dockerignoreでREADME.mdを除外していた
- **解決**: PYTHONPATH方式に切り替えて、pip installを不要にした

## 🔗 関連ドキュメント

- [SPECIFICATION.md](./SPECIFICATION.md) - 詳細な仕様書
- [参考コード](../../../01_reference/chapter3_release_patterns/model_in_image_pattern/)
- [04_notes/09_docker_kubernetes_basics.md](../../../04_notes/09_docker_kubernetes_basics.md) - Docker & Kubernetes基礎ガイド
- [07_tutorials/03_model_in_image_hands_on.md](../../../07_tutorials/03_model_in_image_hands_on.md) - ハンズオンチュートリアル

## 📚 次のステップ

- **Model-Load Pattern**: モデルを外部ストレージから動的にロード
- **Build Pattern**: モデルとアプリケーションを分離してビルド
- **その他のリリースパターン**: Blue/Green、Canary、A/B Testing
