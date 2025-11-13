# Prep-Pred Pattern 仕様書

## 1. 要件定義

### 1.1 機能要件

#### FR-1: 前処理サービス（Prep Service）
- [ ] Base64エンコードされた画像をデコード
- [ ] PIL Imageオブジェクトへの変換
- [ ] 画像のリサイズ（224×224ピクセル）
- [ ] ImageNet標準の正規化（平均・標準偏差）
- [ ] チャンネル順序の変換（HWC → CHW）
- [ ] numpy配列への変換（shape: (1, 3, 224, 224)）
- [ ] 推論サービスへのgRPC/HTTP通信
- [ ] 推論結果の後処理（softmax）
- [ ] ラベルマッピング（ImageNet 1000クラス）

#### FR-2: 推論サービス（Pred Service）
- [ ] ONNX Runtime Serverの起動
- [ ] ResNet50モデルの読み込み
- [ ] gRPC/HTTPエンドポイントの公開
- [ ] 前処理済みデータの受信
- [ ] ONNX推論の実行
- [ ] ロジット（生の出力）の返却

#### FR-3: APIエンドポイント
- [ ] GET /health - ヘルスチェック
- [ ] GET /metadata - データとモデルのメタデータ
- [ ] GET /label - ImageNetラベル一覧取得
- [ ] GET /predict/test - テスト画像で推論（確率）
- [ ] GET /predict/test/label - テスト画像で推論（ラベル）
- [ ] POST /predict - Base64画像で推論（確率）
- [ ] POST /predict/label - Base64画像で推論（ラベル）

### 1.2 非機能要件

#### NFR-1: パフォーマンス
- **前処理レイテンシ**: < 100ms（画像デコード+前処理）
- **推論レイテンシ**: < 500ms（ResNet50推論）
- **End-to-Endレイテンシ**: < 1秒（全体）

#### NFR-2: スケーラビリティ
- **前処理サービス**: CPU最適化、水平スケール可能
- **推論サービス**: GPU最適化、独立してスケール可能
- **通信**: gRPCによる高速通信

#### NFR-3: 可用性
- **ヘルスチェック**: 各サービスで実装
- **自動再起動**: Docker Composeのrestart: always

#### NFR-4: 保守性
- **モジュール分離**: 前処理と推論の完全分離
- **トランスフォーマー**: joblib pklで永続化・再利用可能
- **ラベルマッピング**: JSONファイルで外部管理

## 2. アーキテクチャ設計

### 2.1 システム構成

```
Client
  ↓ POST /predict/label (Base64画像)
┌────────────────────────────────────────┐
│  Prep Service (Port 8000)              │
│  - FastAPI                             │
│  - 画像デコード（Base64 → PIL Image）  │
│  - 前処理（リサイズ、正規化）           │
│  - gRPCクライアント                     │
│  - Softmax後処理                        │
│  - ラベルマッピング                     │
└──────────┬─────────────────────────────┘
           ↓ gRPC (Port 50051)
           ↓ numpy配列 (1, 3, 224, 224)
┌────────────────────────────────────────┐
│  Pred Service (Port 8001/50051)        │
│  - ONNX Runtime Server                 │
│  - ResNet50モデル（約100MB）            │
│  - gRPCサーバー                         │
│  - ImageNet 1000クラス分類              │
└──────────┬─────────────────────────────┘
           ↓ ロジット (1000次元ベクトル)
         結果
```

### 2.2 コンポーネント設計

#### Prep Service
```python
src/
├── app/
│   ├── routers.py          # FastAPIルーター
│   └── app.py              # FastAPIアプリケーション
├── ml/
│   ├── transformers.py     # 前処理・後処理トランスフォーマー
│   └── prediction.py       # 推論クライアント（gRPC）
├── proto/                  # Protocol Buffers定義
├── constants.py            # 定数定義
└── configurations.py       # 環境変数読み込み
```

#### Pred Service
```python
resnet50_onnx_runtime/
├── models/
│   └── resnet50-v1-12.onnx           # ResNet50モデル（約100MB）
└── onnx_runtime_server_entrypoint.sh # 起動スクリプト
```

### 2.3 技術スタック

#### Prep Service
- **Python**: 3.13
- **Webフレームワーク**: FastAPI 0.104.0+
- **画像処理**: Pillow 10.0.0+
- **前処理**: numpy 2.0.0+、scikit-learn 1.3.0+
- **gRPCクライアント**: grpcio 1.59.0+、protobuf 4.24.0+
- **バリデーション**: Pydantic 2.0+
- **永続化**: joblib 1.3.0+

#### Pred Service
- **ランタイム**: ONNX Runtime Server 1.16.0+
- **モデル**: ResNet50（ImageNet学習済み）
- **通信**: gRPC、HTTP REST API

## 3. API仕様

### 3.1 Prep Service エンドポイント

#### GET /health
**概要**: ヘルスチェック

**リクエスト**: なし

**レスポンス**:
```json
{
  "health": "ok"
}
```

---

#### GET /metadata
**概要**: データとモデルのメタデータ

**リクエスト**: なし

**レスポンス**:
```json
{
  "data_type": "str",
  "data_structure": "(1,1)",
  "data_sample": "base64 encoded image file",
  "prediction_type": "float32",
  "prediction_structure": "(1,1000)",
  "prediction_sample": "[0.07093159, 0.01558308, ...]"
}
```

---

#### GET /label
**概要**: ImageNetラベル一覧取得（1000クラス）

**リクエスト**: なし

**レスポンス**:
```json
[
  "background",
  "tench",
  "goldfish",
  ...
  "toilet tissue"
]
```

---

#### GET /predict/test
**概要**: テスト画像で推論（確率）

**リクエスト**: なし（内部のサンプル画像を使用）

**レスポンス**:
```json
{
  "prediction": [[0.00123, 0.00456, ..., 0.98765]]
}
```

---

#### GET /predict/test/label
**概要**: テスト画像で推論（ラベル）

**リクエスト**: なし（内部のサンプル画像を使用）

**レスポンス**:
```json
{
  "prediction": "Siamese cat"
}
```

---

#### POST /predict
**概要**: Base64画像で推論（確率）

**リクエスト**:
```json
{
  "data": "base64_encoded_image_string"
}
```

**レスポンス**:
```json
{
  "prediction": [[0.00123, 0.00456, ..., 0.98765]]
}
```

---

#### POST /predict/label
**概要**: Base64画像で推論（ラベル名）

**リクエスト**:
```json
{
  "data": "base64_encoded_image_string"
}
```

**レスポンス**:
```json
{
  "prediction": "Siamese cat"
}
```

### 3.2 Pred Service エンドポイント

#### gRPC Predict
**概要**: ONNX推論実行

**プロトコル**: gRPC（Protocol Buffers）

**入力**:
- Tensor: float32, shape (1, 3, 224, 224)

**出力**:
- Tensor: float32, shape (1, 1000) - ロジット

#### HTTP REST API
**概要**: HTTP経由での推論（オプション）

**エンドポイント**: POST /v1/models/resnet50:predict

## 4. データモデル

### 4.1 入力データ

#### 画像データ
```python
class Data(BaseModel):
    data: str  # Base64エンコードされた画像
```

**対応形式**:
- JPEG
- PNG
- その他PIL対応形式

**前処理後の形状**:
- Shape: `(1, 3, 224, 224)`
- dtype: `float32`
- Range: 正規化済み（ImageNet平均・標準偏差）

### 4.2 出力データ

#### 確率分布
```python
List[List[float]]  # shape: (1, 1000)
```

#### ラベル
```python
str  # ImageNetクラス名（例: "Siamese cat"）
```

## 5. 前処理仕様

### 5.1 PytorchImagePreprocessTransformer

**目的**: PyTorch/ImageNet標準の前処理

**パラメータ**:
- `image_size`: (224, 224) - リサイズサイズ
- `prediction_shape`: (1, 3, 224, 224) - 出力形状
- `mean_vec`: [0.485, 0.456, 0.406] - ImageNet平均（RGB）
- `stddev_vec`: [0.229, 0.224, 0.225] - ImageNet標準偏差（RGB）

**処理ステップ**:
1. PIL ImageまたはnumpyArray → 224x224にリサイズ
2. numpy配列に変換（HWC形式）
3. チャンネル順序変換（HWC → CHW）
4. ピクセル値正規化（[0-255] → [0-1]）
5. ImageNet標準化: `(pixel / 255 - mean) / stddev`
6. 形状変換: `(1, 3, 224, 224)`

**入力**:
- PIL Image または numpy array

**出力**:
- numpy array, dtype: float32, shape: (1, 3, 224, 224)

### 5.2 SoftmaxTransformer

**目的**: ロジットを確率に変換

**処理ステップ**:
1. ロジット（1000次元ベクトル）を受信
2. Softmax関数を適用: `exp(x) / sum(exp(x))`
3. 確率分布を返却（合計1.0）

**入力**:
- numpy array または List[float], shape: (1, 1000)

**出力**:
- numpy array, dtype: float32, shape: (1, 1000)

## 6. 通信仕様

### 6.1 gRPC通信（Prep → Pred）

**プロトコル**: Protocol Buffers 3

**メッセージ定義**:
```protobuf
message PredictRequest {
  map<string, TensorProto> inputs = 1;
}

message PredictResponse {
  map<string, TensorProto> outputs = 1;
}
```

**通信フロー**:
1. Prepサービスが前処理済みデータをTensorProtoに変換
2. gRPCでPredサービスにリクエスト送信
3. Predサービスが推論実行
4. 推論結果（ロジット）をTensorProtoで返却
5. Prepサービスがロジットをsoftmax変換

**接続情報**:
- ホスト: `pred` (Docker Compose内) または `localhost`
- ポート: `50051`

### 6.2 HTTP通信（Client → Prep）

**プロトコル**: HTTP/1.1、JSON

**Content-Type**: `application/json`

**認証**: なし（このパターンでは省略）

## 7. モデル仕様

### 7.1 ResNet50

**アーキテクチャ**: ResNet-50（Deep Residual Networks）

**学習データ**: ImageNet ILSVRC2012（1000クラス）

**入力**:
- Shape: (1, 3, 224, 224)
- dtype: float32
- 正規化: ImageNet標準（mean/stddev）

**出力**:
- Shape: (1, 1000)
- dtype: float32
- 値: ロジット（生の出力、softmax前）

**モデルファイル**:
- 形式: ONNX (`.onnx`)
- サイズ: 約100MB
- ダウンロード元: ONNX Model Zoo

### 7.2 ImageNetラベル

**クラス数**: 1000クラス

**形式**: JSON配列

**例**:
```json
[
  "background",
  "tench",
  "goldfish",
  ...
  "bolete",
  "ear",
  "toilet tissue"
]
```

## 8. 環境変数

### 8.1 Prep Service

| 環境変数 | デフォルト | 説明 |
|---------|-----------|------|
| `PLATFORM` | `docker_compose` | 実行環境識別 |
| `API_ADDRESS` | `pred` | 推論サービスのホスト名 |
| `HTTP_PORT` | `8000` | PrepサービスのHTTPポート |
| `GRPC_PORT` | `50051` | 推論サービスのgRPCポート |

### 8.2 Pred Service

| 環境変数 | デフォルト | 説明 |
|---------|-----------|------|
| `HTTP_PORT` | `8001` | ONNX Runtime HTTPポート |
| `GRPC_PORT` | `50051` | ONNX Runtime gRPCポート |

## 9. Docker構成

### 9.1 Prep Service

**Dockerfile.prep**:
- ベースイメージ: `python:3.13-slim`
- パッケージマネージャー: uv
- 依存関係: FastAPI、Pillow、numpy、grpcio、joblib
- エントリーポイント: `uvicorn src.app.app:app --host 0.0.0.0 --port 8000`

### 9.2 Pred Service

**Dockerfile.pred**:
- ベースイメージ: `mcr.microsoft.com/onnxruntime/server:latest`
- モデル: `resnet50-v1-12.onnx`
- エントリーポイント: `onnxruntime_server --model_path=/models/resnet50-v1-12.onnx`

### 9.3 Docker Compose

**サービス構成**:
1. `prep` - 前処理サービス（Port 8000）
2. `pred` - 推論サービス（Port 8001, 50051）

**依存関係**:
- `prep` depends_on `pred`

## 10. 成功基準

### 10.1 機能面
- [ ] 全APIエンドポイントが正常に動作
- [ ] Base64画像を正しくデコード・前処理
- [ ] gRPC通信が正常に動作
- [ ] ImageNet 1000クラス分類が正しく動作
- [ ] テスト画像（猫）を「Siamese cat」として正しく分類

### 10.2 性能面
- [ ] 前処理レイテンシ < 100ms
- [ ] 推論レイテンシ < 500ms
- [ ] End-to-Endレイテンシ < 1秒

### 10.3 品質面
- [ ] ユニットテスト: 全層で作成
- [ ] 統合テスト: Prep→Pred通信の検証
- [ ] E2Eテスト: クライアント→Prep→Pred→レスポンス
- [ ] コードカバレッジ: 80%以上

### 10.4 運用面
- [ ] Docker Composeで簡単に起動
- [ ] ヘルスチェックエンドポイント実装
- [ ] エラーハンドリングの実装
- [ ] ログ出力の実装

## 11. 制約事項

### 11.1 技術的制約
- ResNet50モデルは約100MBと大きい（ダウンロード時間に注意）
- GPU推論は本実装では対象外（ONNX Runtime CPUモード）
- Apple Siliconでは一部パッケージの互換性問題の可能性

### 11.2 運用上の制約
- gRPC通信はローカルネットワーク内のみ（認証なし）
- Base64エンコードによる画像送信は大きなデータ量になる可能性

## 12. 今後の拡張

- [ ] GPU推論対応（ONNX Runtime GPU）
- [ ] バッチ推論対応（複数画像の同時処理）
- [ ] 認証・認可の追加
- [ ] メトリクス収集（Prometheus）
- [ ] モデルバージョニング
- [ ] A/Bテスト対応

---

**作成日**: 2025-11-13
**バージョン**: 1.0.0
