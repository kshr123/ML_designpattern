# Prep-Pred Pattern - ソースコード全体概要

## 📚 このディレクトリについて

このディレクトリには、**Prep-Pred Pattern（前処理・推論分離パターン）** の実装コードが含まれています。

Prep-Pred Patternは、機械学習の推論システムを**2つのサービスに分離**するデザインパターンです：

- **Prep Service（前処理サービス）**: 画像の前処理と後処理を担当
- **Pred Service（推論サービス）**: ONNXモデルによる推論を担当

## 🏗️ アーキテクチャ全体図

```
┌─────────────────────────────────────────────────────────────┐
│                        ユーザー                              │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Request
                         │ GET /predict/test/label
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Prep Service (このディレクトリのコード)                    │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │   app/   │ → │   ml/    │ → │  proto/  │               │
│  │ FastAPI  │   │ 前処理   │   │  gRPC    │               │
│  │ ルーター │   │ 後処理   │   │ 通信     │               │
│  └──────────┘   └──────────┘   └──────────┘               │
│       │              │               │                       │
│       │              │               │ gRPC Request          │
│       │              │               │ (TensorProto)         │
│       │              │               ↓                       │
└───────┼──────────────┼───────────────┼───────────────────────┘
        │              │               │
        │              │               │
┌───────┼──────────────┼───────────────┼───────────────────────┐
│       │              │               │                       │
│  Pred Service (ONNX Runtime Server)  │                       │
│       │              │               │                       │
│       │              │          ┌────┴─────┐                │
│       │              │          │ ONNX推論 │                │
│       │              │          │ ResNet50 │                │
│       │              │          └────┬─────┘                │
│       │              │               │ gRPC Response         │
│       │              │               │ (TensorProto)         │
└───────┼──────────────┼───────────────┼───────────────────────┘
        │              │               │
        │              │               ↓
        │              │          後処理（Softmax）
        │              ↓
        │         確率 → ラベル名
        ↓
   {"prediction": "web site"}
```

## 📁 ディレクトリ構成

```
src/
├── README.md                    # このファイル（全体概要）
│
├── app/                         # FastAPIアプリケーション
│   ├── README.md               # FastAPI関連の説明
│   ├── app.py                  # FastAPIアプリ本体
│   └── routers/
│       └── routers.py          # APIエンドポイント定義
│
├── ml/                          # 機械学習ロジック
│   ├── README.md               # ML処理の説明
│   ├── prediction.py           # 推論ロジック（gRPC通信含む）
│   └── transformers.py         # 前処理・後処理の変換器
│
├── proto/                       # Protocol Buffers定義
│   ├── README.md               # gRPC通信の説明
│   ├── predict.proto           # リクエスト/レスポンス定義
│   ├── prediction_service.proto # gRPCサービス定義
│   └── *_pb2.py                # 自動生成されたPythonコード
│
├── configurations.py            # 環境変数の設定
├── constants.py                # 定数定義
└── utils/                       # ユーティリティ
```

## 🔄 データフロー（簡単な例）

### 例：猫の画像を推論する場合

```python
# 1. ユーザーがHTTPリクエストを送信
GET /predict/test/label

# 2. app/routers/routers.py でリクエストを受信
def predict_test_label():
    classifier = get_classifier()           # Classifierインスタンスを取得
    prediction = classifier.predict_label(cat_image)  # 推論実行
    return {"prediction": prediction}

# 3. ml/prediction.py で前処理 + gRPC通信
class Classifier:
    def predict_label(self, data: Image):
        # 3-1. 前処理: 猫の画像 → [1, 3, 224, 224]のnumpy配列
        preprocessed = self.preprocess_transformer.transform(data)

        # 3-2. gRPCリクエスト作成
        request = PredictRequest()
        request.inputs["input"].dims = [1, 3, 224, 224]
        request.inputs["input"].raw_data = preprocessed.tobytes()

        # 3-3. Pred ServiceにgRPCで送信（proto/ のコードを使用）
        response = self.stub.Predict(request)  # ← ★ネットワーク通信★

        # 3-4. レスポンスから推論結果を取得
        output = response.outputs["output"].raw_data

        # 3-5. 後処理: ロジット → 確率 → ラベル名
        probabilities = self.softmax_transformer.transform(output)
        label = self.label[argmax(probabilities)]  # "tabby cat"

        return label

# 4. HTTPレスポンスを返す
{"prediction": "tabby cat"}
```

## 🚀 主要なクラスとその役割

### 1. FastAPIApplication (`app/app.py`)
- **役割**: HTTPサーバーとして動作
- **やること**: ユーザーからのHTTPリクエストを受け付ける

### 2. APIRouter (`app/routers/routers.py`)
- **役割**: エンドポイントの定義
- **やること**: `/predict/test/label` などのURLパスを処理

### 3. Classifier (`ml/prediction.py`)
- **役割**: 推論のメインロジック
- **やること**:
  - 前処理（画像 → テンソル）
  - gRPC通信（Pred Serviceへ送信）
  - 後処理（確率 → ラベル名）

### 4. PytorchImagePreprocessTransformer (`ml/transformers.py`)
- **役割**: 画像の前処理
- **やること**: PIL Image → ResNet50用のnumpy配列に変換

### 5. SoftmaxTransformer (`ml/transformers.py`)
- **役割**: 後処理
- **やること**: ロジット（生の出力値） → 確率分布に変換

### 6. Protocol Buffers (`proto/`)
- **役割**: gRPC通信のデータ形式定義
- **やること**: PredictRequest/PredictResponse の構造を定義

## 🔑 重要な概念

### gRPC通信とは？
HTTPの代わりに使う、高速な通信方式です。

```python
# 通常のHTTP（遅い）
response = requests.post("http://pred:8001/predict", json=data)

# gRPC（速い）
response = stub.Predict(request)  # バイナリ形式で送信
```

### Protocol Buffersとは？
JSONの代わりに使う、コンパクトなデータ形式です。

```python
# JSON（サイズ大きい）
{"inputs": {"input": {"dims": [1,3,224,224], "data": "..."}}}

# Protocol Buffers（サイズ小さい）
request.inputs["input"].dims = [1, 3, 224, 224]
# → バイナリ形式で約1/3のサイズに圧縮
```

### mapフィールドとは？
辞書（dict）のように、名前でデータを管理する仕組みです。

```python
# Pythonの辞書みたいに使える
request.inputs["input"] = tensor1    # "input"という名前で保存
request.inputs["mask"] = tensor2     # "mask"という名前で保存

# 取り出すのも簡単
output = response.outputs["probabilities"]
```

## 📖 各ディレクトリの詳細

各ディレクトリには専用のREADMEがあります：

- **app/**: FastAPIアプリケーションの実装 → [app/README.md](./app/README.md)
- **ml/**: 機械学習の前処理・後処理・推論ロジック → [ml/README.md](./ml/README.md)
- **proto/**: Protocol BuffersとgRPC通信 → [proto/README.md](./proto/README.md)

## 🛠️ 開発時の注意点

### Protocol Buffersファイルの再生成

`.proto`ファイルを変更したら、Pythonコードを再生成する必要があります：

```bash
# 一時的な仮想環境を作成（protobuf 4.25.3互換）
python3 -m venv .venv_temp
source .venv_temp/bin/activate
pip install grpcio==1.60.0 grpcio-tools==1.60.0 protobuf==4.25.3

# protoファイルをコンパイル
cd src/proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. *.proto

# インポート文を修正（手動）
# 'import onnx_ml_pb2' → 'from src.proto import onnx_ml_pb2'
```

### 環境変数

`docker-compose.yml`で設定する環境変数：

```yaml
environment:
  - API_ADDRESS=pred        # Pred Serviceのホスト名
  - GRPC_PORT=50051         # gRPCポート番号
  - ONNX_INPUT_NAME=input   # ONNXモデルの入力名
  - ONNX_OUTPUT_NAME=output # ONNXモデルの出力名
```

## 🎯 まとめ

このPrep-Pred Patternの実装は、以下の3つの主要部分から構成されています：

1. **app/**: ユーザーからのHTTPリクエストを受け付ける
2. **ml/**: 画像の前処理・後処理と、Pred Serviceとの通信
3. **proto/**: gRPC通信のデータ形式定義

全体として、**前処理と推論を分離することで、それぞれを独立してスケールできる**というメリットがあります。
