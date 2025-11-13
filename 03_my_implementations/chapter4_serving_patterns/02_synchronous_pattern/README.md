# Synchronous Pattern - Iris分類（TensorFlow Serving）

## 📋 概要

Synchronous PatternはTensorFlow Servingを使用してモデルをデプロイし、gRPC/REST APIで同期的に推論を行うパターンです。

このプロジェクトでは、TensorFlow SavedModel形式のIris分類モデルを使用し、TensorFlow Servingで高速な推論サービスを提供します。

## 🏗️ アーキテクチャ

### システム構成

```
┌─────────────────────────────────────────────────────────┐
│                  クライアント                            │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    gRPC (8500)             REST (8501)
         │                       │
         └───────────┬───────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│         TensorFlow Serving Container                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  tensorflow_model_server                                │
│    │                                                    │
│    ├─ gRPC Server (8500)                               │
│    │    - PredictionService                            │
│    │    - ModelService                                 │
│    │                                                    │
│    └─ REST API Server (8501)                           │
│         - /v1/models/iris                              │
│         - /v1/models/iris/metadata                     │
│         - /v1/models/iris:predict                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  SavedModel                                     │  │
│  │  /models/iris/1/                                │  │
│  │    ├── saved_model.pb                           │  │
│  │    └── variables/                               │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### コンポーネント

| コンポーネント | 役割 | ファイル |
|--------------|------|---------|
| **TensorFlow Serving** | 推論サーバー | Dockerfile |
| **SavedModel** | TensorFlowモデル | build_model.py |
| **gRPCクライアント** | 高速バイナリ通信 | client/grpc_client.py |
| **RESTクライアント** | HTTP/JSON通信 | client/rest_client.py |

## 🛠️ 技術スタック

### ランタイム
- **Python**: 3.11（モデル作成用）
- **Docker**: コンテナ化
- **TensorFlow Serving**: 2.15.0+ (推論サーバー)

### フレームワーク・ライブラリ
- **TensorFlow**: 2.15.0 (モデル学習・SavedModel作成)
- **gRPC**: 高速バイナリプロトコル
- **Protocol Buffers**: データシリアライゼーション
- **scikit-learn**: Irisデータセット

### モデル
- **形式**: TensorFlow SavedModel
- **入力**: `(batch_size, 4)` - 4つの特徴量
- **出力**: `(batch_size, 3)` - 3クラスの確率値
- **精度**: 96.67%

## 🚀 セットアップ

### 前提条件

- Python 3.11
- Docker
- uv (Pythonパッケージマネージャー)

### 1. モデル作成

**重要**: TensorFlow 2.20.0にはPython 3.12/3.13互換性の問題があるため、Python 3.11とTensorFlow 2.15.0を使用します。

```bash
# Python 3.11の仮想環境を作成
echo "3.11" > .python-version
uv venv
source .venv/bin/activate  # macOS/Linux

# 依存関係のインストール（タイムアウト値を増やす）
UV_HTTP_TIMEOUT=600 uv pip install -r requirements.txt

# モデルを作成
python build_model.py

# 出力: saved_model/iris/1/
```

**モデル作成結果:**
```
Test Accuracy: 0.9667 (96.67%)
Test Loss: 0.1218
SavedModel location: saved_model/iris/1
```

### 2. Dockerイメージのビルド

```bash
docker build -t synchronous-pattern:latest .
```

### 3. コンテナの起動（x86_64のみ）

**⚠️ Apple Silicon (ARM64) の制限事項**

TensorFlow Servingの公式Dockerイメージはx86_64アーキテクチャ専用です。Apple Silicon (M1/M2/M3) MacではRosetta 2でのエミュレーションが不完全で、"Illegal instruction"エラーが発生します。

**x86_64システムでの起動:**
```bash
docker run -d \
  --name synchronous-pattern \
  -p 8500:8500 \
  -p 8501:8501 \
  synchronous-pattern:latest
```

**Apple Siliconユーザーの対応方法:**

1. **クラウドにデプロイ** (推奨)
   - AWS EC2 (x86_64インスタンス)
   - Google Cloud Run
   - Azure Container Instances

2. **x86_64エミュレーション**
   ```bash
   docker run -d \
     --platform linux/amd64 \
     --name synchronous-pattern \
     -p 8500:8500 \
     -p 8501:8501 \
     synchronous-pattern:latest
   ```
   ただし、これでも動作する保証はありません。

3. **ローカルテスト**
   - 公式ドキュメントとクライアントコードで学習
   - 実際のデプロイはクラウド環境で実施

## 📡 API仕様

### REST API

#### 1. モデルステータス取得

```bash
curl http://localhost:8501/v1/models/iris
```

**レスポンス:**
```json
{
  "model_version_status": [
    {
      "version": "1",
      "state": "AVAILABLE",
      "status": {
        "error_code": "OK",
        "error_message": ""
      }
    }
  ]
}
```

#### 2. モデルメタデータ取得

```bash
curl http://localhost:8501/v1/models/iris/metadata
```

**レスポンス:**
```json
{
  "model_spec": {
    "name": "iris",
    "version": "1"
  },
  "metadata": {
    "signature_def": {
      "signature_def": {
        "serving_default": {
          "inputs": {
            "input": {
              "dtype": "DT_FLOAT",
              "tensor_shape": {
                "dim": [{"size": "-1"}, {"size": "4"}]
              }
            }
          },
          "outputs": {
            "output": {
              "dtype": "DT_FLOAT",
              "tensor_shape": {
                "dim": [{"size": "-1"}, {"size": "3"}]
              }
            }
          }
        }
      }
    }
  }
}
```

#### 3. 推論実行

```bash
curl -X POST http://localhost:8501/v1/models/iris:predict \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [
      [5.1, 3.5, 1.4, 0.2],
      [6.3, 3.3, 6.0, 2.5]
    ]
  }'
```

**レスポンス:**
```json
{
  "predictions": [
    [0.97, 0.02, 0.01],
    [0.01, 0.02, 0.97]
  ]
}
```

### gRPC API

gRPCクライアントの実装例は `client/grpc_client.py` を参照してください。

## 🧪 クライアントの使用方法

### クライアント依存関係のインストール

```bash
cd client
UV_HTTP_TIMEOUT=600 uv venv
source .venv/bin/activate
UV_HTTP_TIMEOUT=600 uv pip install -r requirements.txt
```

### RESTクライアント

```bash
python rest_client.py --host localhost --port 8501
```

**出力例:**
```
========================================
🔮 Iris Classification - REST Client
========================================

0️⃣ Model Status:
  {...}

1️⃣ Model Metadata:
  Model: iris
  Version: 1

2️⃣ Prediction with probabilities (instances format):
  Sample 1: [5.1, 3.5, 1.4, 0.2]
    Probabilities: [0.97, 0.02, 0.01]
    Predicted class: 0
    Response time: 25.43ms

...
```

### gRPCクライアント

```bash
python grpc_client.py --host localhost --port 8500
```

**出力例:**
```
========================================
🔮 Iris Classification - gRPC Client
========================================

1️⃣ Prediction with probabilities:
  Sample 1: [5.1, 3.5, 1.4, 0.2]
    Probabilities: [0.97, 0.02, 0.01]
    Predicted class: 0
    Response time: 12.54ms

2️⃣ Prediction with class names:
  Sample 1: [5.1, 3.5, 1.4, 0.2]
    Predicted: setosa
    Response time: 12.54ms
```

## 🎓 学んだこと

### 1. TensorFlow SavedModelの構造

**SavedModelの要素:**
- `saved_model.pb`: 計算グラフとメタデータ
- `variables/`: モデルの重み
- `assets/`: 追加リソース（オプション）

**serving signatureの重要性:**
```python
# TensorFlow 2.xでは自動的に"serving_default"が作成される
tf.saved_model.save(model, export_path)
```

### 2. TensorFlow Servingのメリット

**なぜTensorFlow Servingを使うのか？**

| 項目 | FastAPI + ONNX | TensorFlow Serving |
|------|---------------|-------------------|
| カスタマイズ性 | ✅ 高い | ❌ 低い |
| パフォーマンス | 普通 | ✅ 高速 |
| バッチ処理 | 手動実装 | ✅ 自動最適化 |
| モデル更新 | コード変更必要 | ✅ ホットスワップ |
| gRPC対応 | 手動実装 | ✅ 組み込み済み |

**TensorFlow Servingが適している場合:**
- TensorFlowモデルの本番デプロイ
- 高スループットが必要
- モデルの頻繁な更新
- gRPCで低レイテンシが必要

### 3. gRPC vs REST

**gRPC の利点:**
- ✅ バイナリプロトコル（HTTPより高速）
- ✅ HTTP/2ベース（多重化、ストリーミング）
- ✅ 強く型付けされたAPI（Protocol Buffers）
- ✅ 言語間の互換性

**REST の利点:**
- ✅ シンプル（curlで簡単にテスト）
- ✅ ブラウザから直接アクセス可能
- ✅ デバッグが容易
- ✅ ファイアウォールフレンドリー

**レスポンスタイム比較（想定）:**
- gRPC: 10-20ms
- REST: 20-40ms

### 4. Python 3.12/3.13とTensorFlow 2.20の互換性問題

**遭遇した問題:**
```
TypeError: this __dict__ descriptor does not support '_DictWrapper' objects
```

**原因:**
- Python 3.12以降で`typing`モジュールの内部実装が変更
- TensorFlow 2.20.0のSavedModel exportコードが未対応

**解決策:**
1. **Python 3.11を使用** (推奨)
2. **TensorFlow 2.15.0を使用**
3. NumPy < 2.0.0に制限

**requirements.txt:**
```
tensorflow==2.15.0
numpy>=1.24.0,<2.0.0
scikit-learn>=1.3.0
```

### 5. Docker Multi-stage Buildの課題

**当初の設計:**
```dockerfile
# Stage 1: モデルビルド
FROM python:3.11-slim AS builder
RUN pip install tensorflow
RUN python build_model.py

# Stage 2: Serving
FROM tensorflow/serving:latest
COPY --from=builder /build/saved_model /models
```

**問題点:**
- TensorFlow (191MB) のダウンロードタイムアウト
- ビルド時間が長い（5分以上）
- ネットワーク依存性

**改善した設計:**
```dockerfile
# ローカルでモデルをビルド
FROM tensorflow/serving:latest
COPY ./saved_model/iris /models/iris
```

**メリット:**
- ビルド時間短縮（数秒）
- ネットワーク不要
- 明確な責任分離（モデル作成とデプロイ）

### 6. Apple Silicon (ARM64) の制限

**問題:**
TensorFlow ServingはARM64アーキテクチャに対応していない

**学び:**
- プロダクション環境はx86_64が主流
- ローカル開発とクラウドデプロイの環境差を意識
- クロスプラットフォーム対応の重要性

**実務での対応:**
- 開発はDockerなしでテスト（クライアントのみ）
- CI/CDでx86_64環境でビルド・テスト
- 本番環境はクラウド（x86_64）

## 📊 Web Single Patternとの違い

| 項目 | Web Single Pattern | Synchronous Pattern |
|------|-------------------|-------------------|\n| **推論サーバー** | FastAPI + gunicorn | **TensorFlow Serving** |
| **モデル形式** | ONNX | **TensorFlow SavedModel** |
| **プロトコル** | REST のみ | **gRPC + REST** |
| **カスタマイズ性** | 高い | 低い |
| **パフォーマンス** | 普通 | **高速** |
| **学習コスト** | 低い | 高い |
| **ユースケース** | カスタムロジック必要 | **TensorFlowモデルの高速推論** |
| **バッチ最適化** | 手動実装 | **自動** |
| **モデル更新** | コード変更必要 | **ホットスワップ** |

## 📚 参考

- **仕様書**: [SPECIFICATION.md](./SPECIFICATION.md)
- **参考コード**: [01_reference/chapter4_serving_patterns/synchronous_pattern/](../../01_reference/chapter4_serving_patterns/synchronous_pattern/)
- **TensorFlow Serving**: https://www.tensorflow.org/tfx/guide/serving
- **gRPC**: https://grpc.io/
- **Protocol Buffers**: https://developers.google.com/protocol-buffers

## 📝 トラブルシューティング

### モデル作成でエラーが発生する

**問題:** `TypeError: this __dict__ descriptor does not support '_DictWrapper' objects`

**解決策:**
```bash
# Python 3.11を使用
echo "3.11" > .python-version
rm -rf .venv
uv venv
source .venv/bin/activate
UV_HTTP_TIMEOUT=600 uv pip install -r requirements.txt
```

### Dockerコンテナが起動しない（Apple Silicon）

**問題:** `Illegal instruction`

**解決策:**
- クラウド環境（x86_64）にデプロイ
- ローカルではクライアントコードのみ動作確認
- ドキュメントで学習

### TensorFlowのインストールがタイムアウトする

**問題:** `ReadTimeoutError: HTTPSConnectionPool`

**解決策:**
```bash
# タイムアウト値を増やす
UV_HTTP_TIMEOUT=600 uv pip install -r requirements.txt
```

## 📄 ライセンス

このプロジェクトは学習目的で作成されたものです。

---

**実装日**: 2025-11-13
**開発者**: kshr123
**パターン**: Synchronous Pattern (Chapter 4: Serving Patterns)
