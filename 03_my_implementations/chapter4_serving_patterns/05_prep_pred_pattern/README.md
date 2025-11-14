# Prep-Pred Pattern（前処理・推論分離パターン）

## 📚 パターン概要

**Prep-Pred Pattern**は、機械学習の推論システムを**前処理（Prep）**と**推論（Pred）**の2つのサービスに分離するデザインパターンです。

### なぜ分離するのか？

1. **独立したスケーリング**: 前処理と推論で必要なリソースが異なる
   - 前処理: CPU集約的（画像変換、正規化など）
   - 推論: GPU集約的（ニューラルネットワーク計算）

2. **柔軟な更新**: 前処理ロジックの変更時に推論サーバーを再起動不要

3. **再利用性**: 同じ推論サーバーを複数の前処理サービスから利用可能

## 🏗️ アーキテクチャ

```
┌──────────────┐  HTTP    ┌──────────────┐  gRPC    ┌──────────────┐
│   ユーザー   │ -------> │ Prep Service │ -------> │ Pred Service │
│  (Client)    │          │  (FastAPI)   │          │(ONNX Runtime)│
└──────────────┘          └──────────────┘          └──────────────┘
                               │                          │
                               │                          │
                          画像前処理                  モデル推論
                          - リサイズ                - ResNet50
                          - 正規化                  - ImageNet 1000クラス
                          - Softmax後処理           - gRPCサービス
```

### サービス構成

#### Prep Service（前処理サービス）
- **役割**: 画像の前処理と後処理
- **技術**: FastAPI + Python
- **ポート**: 8002
- **処理内容**:
  - 画像のリサイズ・正規化
  - gRPCでPred Serviceに送信
  - Softmax変換で確率に変換

#### Pred Service（推論サービス）
- **役割**: ONNXモデルによる推論
- **技術**: ONNX Runtime Server
- **ポート**: 50051 (gRPC), 8001 (HTTP)
- **モデル**: ResNet50 (ImageNet)

## 🚀 実装内容

### 主要技術

- **gRPC**: 高速な通信プロトコル（HTTP/2ベース）
- **Protocol Buffers**: 効率的なバイナリデータ形式
- **ONNX Runtime**: 高速な推論エンジン
- **FastAPI**: モダンなPython Webフレームワーク
- **Docker Compose**: マルチコンテナ管理

### ディレクトリ構成

```
05_prep_pred_pattern/
├── src/
│   ├── app/                 # FastAPIアプリケーション
│   │   ├── app.py          # FastAPIメインファイル
│   │   └── routers/        # APIエンドポイント
│   ├── ml/                  # 機械学習ロジック
│   │   ├── prediction.py   # 推論ロジック + gRPC通信
│   │   └── transformers.py # 前処理・後処理
│   └── proto/               # Protocol Buffers定義
│       ├── predict.proto   # リクエスト/レスポンス定義
│       └── *.py            # 自動生成されたPythonコード
├── docker-compose.yml       # サービス構成
├── Dockerfile.prep          # Prep Serviceイメージ
├── Dockerfile.pred          # Pred Serviceイメージ
└── tests/                   # テストコード
```

詳細なコード説明は各ディレクトリのREADME.mdを参照してください：
- [src/README.md](./src/README.md) - 全体アーキテクチャ
- [src/app/README.md](./src/app/README.md) - FastAPI詳細
- [src/ml/README.md](./src/ml/README.md) - ML処理詳細
- [src/proto/README.md](./src/proto/README.md) - gRPC通信詳細

## 🔧 セットアップと実行

### 前提条件

- Docker Desktop
- Python 3.13
- uv（Pythonパッケージマネージャー）

### 1. 環境構築

```bash
# プロジェクトディレクトリに移動
cd 03_my_implementations/chapter4_serving_patterns/05_prep_pred_pattern

# 仮想環境セットアップ
echo "3.13" > .python-version
uv venv
source .venv/bin/activate

# 依存関係インストール
uv pip install -r requirements.txt

# 開発ツールインストール
uv pip install pytest pytest-cov black ruff mypy
```

### 2. Dockerコンテナ起動

```bash
# コンテナビルド & 起動
docker compose up --build

# バックグラウンドで起動
docker compose up -d
```

### 3. 動作確認

```bash
# ヘルスチェック
curl http://localhost:8002/health
# 出力: {"health":"healthy"}

# テスト画像で推論（ラベル名）
curl http://localhost:8002/predict/test/label
# 出力: {"prediction":"web site"}

# Swagger UI（ブラウザで開く）
open http://localhost:8002/docs
```

### 4. クリーンアップ

```bash
# コンテナ停止
docker compose down

# ボリューム含めて完全削除
docker compose down -v

# イメージも削除
docker compose down --rmi all
```

## 🧪 テスト

### ユニットテスト実行

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ付き
pytest tests/ --cov=src --cov-report=term-missing
```

### テストカバレッジ

- **Transformers**: 100%カバレッジ
- **Prediction**: 主要フローをカバー
- **API Endpoints**: 全エンドポイントをテスト

## 📊 API仕様

### エンドポイント一覧

| エンドポイント | メソッド | 説明 | レスポンス例 |
|---------------|---------|------|-------------|
| `/health` | GET | ヘルスチェック | `{"health":"healthy"}` |
| `/metadata` | GET | API仕様情報 | メタデータJSON |
| `/label` | GET | ImageNetラベル一覧 | 1000クラスのラベル |
| `/predict/test` | GET | テスト推論（確率） | 確率分布 |
| `/predict/test/label` | GET | テスト推論（ラベル） | `{"prediction":"web site"}` |
| `/predict` | POST | 画像推論（確率） | 確率分布 |
| `/predict/label` | POST | 画像推論（ラベル） | ラベル名 |

### リクエスト例（POSTエンドポイント）

```bash
# 画像をBase64エンコード
IMAGE_BASE64=$(base64 -i cat.jpg)

# POSTリクエスト送信
curl -X POST http://localhost:8002/predict/label \
  -H "Content-Type: application/json" \
  -d "{\"data\": \"$IMAGE_BASE64\"}"

# 出力: {"prediction":"tabby cat"}
```

## 🔑 学習ポイント

### 1. gRPC通信

- HTTP/1.1よりも高速（HTTP/2ベース）
- Protocol Buffersでデータをバイナリ化
- JSONと比較して約3倍速い

### 2. Protocol Buffers

- JSONより小さく高速なデータ形式
- `.proto`ファイルでスキーマを定義
- 型安全性が高い

### 3. マイクロサービスアーキテクチャ

- サービスごとに独立してスケーリング可能
- 責務の分離（前処理 vs 推論）
- 各サービスを異なる言語で実装可能

### 4. Protocol Buffers Map Fields

```python
# mapフィールドの使用例
request.inputs["input"].dims = [1, 3, 224, 224]
request.inputs["input"].data_type = 1
request.inputs["input"].raw_data = image_bytes
```

## 🐛 トラブルシューティング

### Protocol Buffers バージョンエラー

**エラー**: `ImportError: cannot import name 'runtime_version'`

**原因**: protobuf 6.xで生成したファイルをprotobuf 4.25.3で実行

**解決策**: protobuf 4.25.3で再生成
```bash
python3 -m venv .venv_temp
source .venv_temp/bin/activate
pip install grpcio==1.60.0 grpcio-tools==1.60.0 protobuf==4.25.3
cd src/proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. *.proto
# インポート文を手動修正: 'import onnx_ml_pb2' → 'from src.proto import onnx_ml_pb2'
```

### Map Field Access Error

**エラー**: `TypeError: list indices must be integers or slices, not str`

**原因**: protobuf 4.x では map field の値に直接アクセスする必要がある

**解決策**:
```python
# ❌ 間違い（CopyFromを使う）
tensor = TensorProto()
request.inputs["input"].CopyFrom(tensor)

# ✅ 正解（直接フィールドを設定）
request.inputs["input"].dims.extend([1, 3, 224, 224])
request.inputs["input"].data_type = 1
request.inputs["input"].raw_data = bytes_data
```

## 📈 パフォーマンス

### 通信速度比較

| 方式 | サイズ | 速度 | 特徴 |
|------|-------|------|------|
| REST API (JSON) | 100% | 1x | 可読性高い |
| gRPC (Protocol Buffers) | 30% | 3x | 高速・コンパクト |

### レスポンスタイム

- テスト画像推論: ~100-200ms
  - 前処理: ~10ms
  - gRPC通信: ~5ms
  - ONNX推論: ~80-180ms
  - 後処理: ~5ms

## 🎯 次のステップ

このパターンを理解したら、以下のパターンも学習してみましょう：

1. **Data Cache Pattern**: 前処理結果のキャッシュ
2. **Prediction Cache Pattern**: 推論結果のキャッシュ
3. **Horizontal Microservice Pattern**: 複数モデルの並列実行

## 📚 参考資料

- [Protocol Buffers公式ドキュメント](https://protobuf.dev/)
- [gRPC公式サイト](https://grpc.io/)
- [ONNX Runtime Server](https://github.com/microsoft/onnx-server)
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)

---

**実装日**: 2025-11-14
**学習時間**: 約4-5時間
**難易度**: ⭐⭐⭐⭐ (4/5) - Protocol BuffersとgRPCの理解が必要
