# Synchronous Pattern 仕様書

## 1. 要件定義

### 1.1 機能要件

**基本機能:**
- [ ] TensorFlow SavedModel形式でIris分類モデルを作成
- [ ] TensorFlow Servingで同期推論サービスを公開
- [ ] gRPC（ポート8500）とREST（ポート8501）の両方で推論可能
- [ ] Iris 3クラス分類（setosa, versicolor, virginica）

**エンドポイント:**
- [ ] `GET /v1/models/iris` - モデル情報取得
- [ ] `GET /v1/models/iris/metadata` - モデルメタデータ取得
- [ ] `POST /v1/models/iris:predict` - REST推論
- [ ] `gRPC PredictionService/Predict` - gRPC推論

### 1.2 非機能要件

**パフォーマンス:**
- レスポンスタイム: < 100ms（gRPC）、< 150ms（REST）
- スループット: > 100 req/sec
- 同時接続数: > 50

**可用性:**
- コンテナ起動時間: < 30秒
- ヘルスチェック: HTTP GET /v1/models/iris で確認可能

**スケーラビリティ:**
- 複数インスタンスのデプロイが可能（ステートレス）
- 水平スケーリング対応

**セキュリティ:**
- モデルファイルはDockerイメージに組み込み（改ざん防止）
- 入力データのバリデーション（TensorFlow Servingが実施）

## 2. アーキテクチャ設計

### 2.1 システム構成

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

### 2.2 コンポーネント設計

**1. モデル作成（build_model.py）**
- 役割: TensorFlow/KerasでIrisモデルを学習してSavedModel形式で保存
- 入力: Irisデータセット
- 出力: `saved_model/iris/1/` ディレクトリ
- 処理フロー:
  1. Irisデータセットをロード
  2. TensorFlow/Kerasでモデル構築・学習
  3. SavedModel形式でエクスポート（@tf.functionでserving signature定義）

**2. TensorFlow Serving**
- 役割: 同期推論サービス
- 入力: gRPC/RESTリクエスト
- 出力: 推論結果（確率値またはラベル）
- 処理フロー:
  1. リクエスト受信（gRPC or REST）
  2. 入力データのバリデーション
  3. モデル推論
  4. レスポンス返却

**3. gRPCクライアント（client/grpc_client.py）**
- 役割: gRPCプロトコルで推論リクエスト
- 処理フロー:
  1. PredictRequest生成
  2. gRPCチャネル確立
  3. Predict RPC呼び出し
  4. PredictResponse処理

**4. RESTクライアント（client/rest_client.py）**
- 役割: REST APIで推論リクエスト
- 処理フロー:
  1. JSON形式のリクエストボディ作成
  2. HTTP POST /v1/models/iris:predict
  3. JSON形式のレスポンス処理

### 2.3 技術スタック

**ランタイム:**
- Python: 3.13
- TensorFlow: 2.15.0+
- TensorFlow Serving: 2.15.0+

**フレームワーク・ライブラリ:**
- TensorFlow/Keras: モデル構築・学習
- gRPC: バイナリ通信
- Protocol Buffers: データシリアライゼーション
- scikit-learn: Irisデータセット取得

**開発ツール:**
- pytest: テストフレームワーク
- grpcio: gRPCライブラリ
- requests: RESTクライアント

## 3. API仕様

### 3.1 REST API

#### 3.1.1 モデル情報取得

**エンドポイント:**
```
GET /v1/models/iris
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

#### 3.1.2 メタデータ取得

**エンドポイント:**
```
GET /v1/models/iris/metadata
```

**レスポンス:**
```json
{
  "model_spec": {
    "name": "iris",
    "signature_name": "",
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
                "dim": [
                  {"size": "-1"},
                  {"size": "4"}
                ]
              },
              "name": "serving_default_input:0"
            }
          },
          "outputs": {
            "output": {
              "dtype": "DT_FLOAT",
              "tensor_shape": {
                "dim": [
                  {"size": "-1"},
                  {"size": "3"}
                ]
              },
              "name": "StatefulPartitionedCall:0"
            }
          },
          "method_name": "tensorflow/serving/predict"
        }
      }
    }
  }
}
```

#### 3.1.3 推論実行

**エンドポイント:**
```
POST /v1/models/iris:predict
POST /v1/models/iris/versions/1:predict
```

**リクエストボディ:**
```json
{
  "instances": [
    [5.1, 3.5, 1.4, 0.2],
    [6.3, 3.3, 6.0, 2.5]
  ]
}
```

または

```json
{
  "inputs": {
    "input": [
      [5.1, 3.5, 1.4, 0.2],
      [6.3, 3.3, 6.0, 2.5]
    ]
  }
}
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

### 3.2 gRPC API

#### 3.2.1 Predict RPC

**サービス:**
```protobuf
service PredictionService {
  rpc Predict(PredictRequest) returns (PredictResponse);
}
```

**リクエスト:**
```python
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

request = predict_pb2.PredictRequest()
request.model_spec.name = 'iris'
request.model_spec.signature_name = 'serving_default'
request.inputs['input'].CopyFrom(
    tf.make_tensor_proto([[5.1, 3.5, 1.4, 0.2]], shape=[1, 4])
)
```

**レスポンス:**
```python
response = stub.Predict(request, timeout=10.0)
outputs = response.outputs['output'].float_val
# [0.97, 0.02, 0.01]
```

## 4. データモデル

### 4.1 入力データ

**REST:**
```json
{
  "instances": [
    [sepal_length, sepal_width, petal_length, petal_width]
  ]
}
```

**gRPC:**
```python
tf.TensorProto:
  dtype: DT_FLOAT
  tensor_shape: [batch_size, 4]
  float_val: [sepal_length, sepal_width, petal_length, petal_width, ...]
```

**値の範囲:**
- sepal_length: 4.3 ~ 7.9 (cm)
- sepal_width: 2.0 ~ 4.4 (cm)
- petal_length: 1.0 ~ 6.9 (cm)
- petal_width: 0.1 ~ 2.5 (cm)

### 4.2 出力データ

**クラスラベル:**
- 0: setosa
- 1: versicolor
- 2: virginica

**出力形式（確率値）:**
```json
[
  [prob_setosa, prob_versicolor, prob_virginica]
]
```

**値の範囲:**
- 各確率値: 0.0 ~ 1.0
- 合計: 1.0

## 5. ディレクトリ構造

```
02_synchronous_pattern/
├── SPECIFICATION.md          # 本ファイル
├── README.md                 # プロジェクトドキュメント
├── Dockerfile                # マルチステージビルド
├── build_model.py            # モデル作成スクリプト
├── requirements.txt          # Python依存関係
├── tf_serving_entrypoint.sh  # TensorFlow Serving起動スクリプト
├── client/                   # クライアントコード
│   ├── __init__.py
│   ├── grpc_client.py        # gRPCクライアント
│   ├── rest_client.py        # RESTクライアント
│   └── requirements.txt      # クライアント依存関係
├── tests/                    # テストコード
│   ├── __init__.py
│   ├── test_model.py         # モデルテスト
│   ├── test_grpc_client.py   # gRPCテスト
│   └── test_rest_client.py   # RESTテスト
└── saved_model/              # SavedModel（生成物）
    └── iris/
        └── 1/
            ├── saved_model.pb
            └── variables/
```

## 6. 環境変数

| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| `PORT` | `8500` | gRPCポート |
| `REST_API_PORT` | `8501` | RESTポート |
| `MODEL_NAME` | `iris` | モデル名 |
| `MODEL_BASE_PATH` | `/models/iris` | モデルベースパス |

## 7. 成功基準

### 7.1 機能要件

- [ ] TensorFlow SavedModelが正常に作成される
- [ ] Dockerイメージが正常にビルドされる
- [ ] TensorFlow Servingが起動する（30秒以内）
- [ ] gRPCエンドポイント（8500）が応答する
- [ ] RESTエンドポイント（8501）が応答する
- [ ] 推論精度: > 95%（テストデータ）

### 7.2 非機能要件

- [ ] レスポンスタイム < 100ms（gRPC）
- [ ] レスポンスタイム < 150ms（REST）
- [ ] 全テストケースがパス
- [ ] コードカバレッジ: > 80%

### 7.3 ドキュメント

- [ ] SPECIFICATION.md作成
- [ ] README.md作成
- [ ] コード内コメント（日本語）
- [ ] API使用例の提供

## 8. Web Single Patternとの違い

| 項目 | Web Single Pattern | Synchronous Pattern |
|------|-------------------|-------------------|
| **推論サーバー** | FastAPI + gunicorn + uvicorn | **TensorFlow Serving** |
| **モデル形式** | ONNX | **TensorFlow SavedModel** |
| **プロトコル** | REST のみ | **gRPC + REST** |
| **カスタマイズ性** | 高い（Pythonで自由に実装） | 低い（TF Servingの制約あり） |
| **パフォーマンス** | 普通 | **高速（gRPC）** |
| **学習コスト** | 低い | 高い |
| **ユースケース** | カスタムロジックが必要 | **TensorFlowモデルの高速推論** |

## 9. 参考

- [TensorFlow Serving](https://www.tensorflow.org/tfx/guide/serving)
- [gRPC](https://grpc.io/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)
- [参考実装](../../../01_reference/chapter4_serving_patterns/synchronous_pattern/)
