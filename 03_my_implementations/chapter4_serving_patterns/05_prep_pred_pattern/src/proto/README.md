# proto/ - Protocol Buffers と gRPC通信

## 📚 このディレクトリについて

このディレクトリには、**Prep ServiceとPred Serviceの間の通信**を定義するProtocol Buffersファイルが含まれています。

Protocol Buffers（protobuf）は、データをコンパクトに送受信するためのフォーマットで、gRPC通信で使用されます。

## 📁 ファイル構成

```
proto/
├── README.md                       # このファイル
│
├── predict.proto                   # リクエスト/レスポンスの定義
├── prediction_service.proto        # gRPCサービスの定義
├── onnx-ml.proto                   # ONNXデータ型の定義
│
├── predict_pb2.py                  # predict.proto から自動生成
├── predict_pb2_grpc.py             # predict.proto のgRPC部分
├── prediction_service_pb2.py       # prediction_service.proto から自動生成
├── prediction_service_pb2_grpc.py  # prediction_service.proto のgRPC部分
├── onnx_ml_pb2.py                  # onnx-ml.proto から自動生成
└── onnx_ml_pb2_grpc.py             # onnx-ml.proto のgRPC部分
```

**重要**: `*_pb2.py`ファイルは自動生成されるため、直接編集しないでください。

## 🔄 通信フロー全体図

```
┌─────────────────────────────────────────────────────────────┐
│  Prep Service (prediction.py)                               │
│                                                              │
│  # 1. gRPCリクエスト作成                                    │
│  request = PredictRequest()                                 │
│  request.inputs["input"].dims = [1, 3, 224, 224]            │
│  request.inputs["input"].data_type = 1  # float32           │
│  request.inputs["input"].raw_data = image_bytes             │
│                                                              │
│  # リクエストの中身（Protocol Buffers形式）                │
│  PredictRequest {                                           │
│    inputs: {                                                │
│      "input": TensorProto {                                 │
│        dims: [1, 3, 224, 224]                               │
│        data_type: FLOAT (1)                                 │
│        raw_data: <150,528バイトのバイナリ>                  │
│      }                                                       │
│    }                                                         │
│  }                                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ gRPC通信（バイナリ形式）
                         │ ネットワーク: pred:50051
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Pred Service (ONNX Runtime Server)                         │
│                                                              │
│  # 2. リクエストを受信して推論                              │
│  def Predict(request):                                      │
│      inputs = request.inputs["input"]                       │
│      # ResNet50モデルで推論                                 │
│      outputs = model.run(inputs)                            │
│                                                              │
│      # レスポンス作成                                       │
│      response = PredictResponse()                           │
│      response.outputs["output"].dims = [1, 1000]            │
│      response.outputs["output"].data_type = 1               │
│      response.outputs["output"].raw_data = outputs.tobytes()│
│      return response                                        │
│                                                              │
│  # レスポンスの中身（Protocol Buffers形式）                │
│  PredictResponse {                                          │
│    outputs: {                                               │
│      "output": TensorProto {                                │
│        dims: [1, 1000]                                      │
│        data_type: FLOAT (1)                                 │
│        raw_data: <4,000バイトのバイナリ>                    │
│      }                                                       │
│    }                                                         │
│  }                                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ gRPC通信（バイナリ形式）
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Prep Service (prediction.py)                               │
│                                                              │
│  # 3. レスポンスを受信                                      │
│  response = stub.Predict(request)                           │
│  output = np.frombuffer(                                    │
│      response.outputs["output"].raw_data,                   │
│      dtype=np.float32                                       │
│  )                                                           │
│  # → (1000,) numpy配列                                      │
└─────────────────────────────────────────────────────────────┘
```

## 📄 predict.proto - リクエスト/レスポンス定義

このファイルは、「どんなデータを送受信するか」を定義します。

### ファイル内容

```protobuf
syntax = "proto3";

import "onnx-ml.proto";

package onnxruntime.server;

// 推論リクエスト
message PredictRequest {
  // 入力テンソルのマップ
  // キー: テンソル名（例: "input"）
  // 値: TensorProto（画像データなど）
  map<string, onnx.TensorProto> inputs = 2;

  // 出力フィルター（省略可）
  repeated string output_filter = 3;
}

// 推論レスポンス
message PredictResponse {
  // 出力テンソルのマップ
  // キー: テンソル名（例: "output"）
  // 値: TensorProto（推論結果）
  map<string, onnx.TensorProto> outputs = 1;
}
```

### 重要なポイント: map フィールド

`map<string, TensorProto>`は、Pythonの辞書のように使えます：

```python
# リクエスト作成
request = PredictRequest()

# 辞書のように値を設定
request.inputs["input"].dims.extend([1, 3, 224, 224])
request.inputs["input"].data_type = 1
request.inputs["input"].raw_data = image_bytes

# 複数の入力も可能
request.inputs["mask"].dims.extend([1, 1, 224, 224])
request.inputs["labels"].data = label_data
```

### なぜmapを使うの？

```python
# mapを使わない場合（配列）
request.inputs[0]  # これは何のデータ？分からない...
request.inputs[1]  # これも分からない...

# mapを使う場合
request.inputs["input"]      # 画像データ
request.inputs["mask"]       # マスクデータ
request.inputs["metadata"]   # メタデータ
# → 名前で識別できる！
```

## 📄 prediction_service.proto - gRPCサービス定義

このファイルは、「どんなメソッドが呼び出せるか」を定義します。

### ファイル内容

```protobuf
syntax = "proto3";

import "predict.proto";

package onnxruntime.server;

// 推論サービス
service PredictionService {
  // 推論メソッド
  rpc Predict(PredictRequest) returns (PredictResponse);
}
```

### 使い方（Pythonコード）

```python
import grpc
from src.proto import predict_pb2, prediction_service_pb2_grpc

# 1. gRPC接続を確立
channel = grpc.insecure_channel("pred:50051")

# 2. スタブ（リモコン）を作成
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

# 3. リクエスト作成
request = predict_pb2.PredictRequest()
request.inputs["input"].dims.extend([1, 3, 224, 224])
request.inputs["input"].raw_data = image_bytes

# 4. Predict メソッドを呼び出し
response = stub.Predict(request)
# ↑ ネットワーク通信が発生！

# 5. レスポンス取得
output = response.outputs["output"].raw_data
```

## 📄 onnx-ml.proto - ONNXデータ型定義

このファイルは、ONNX Runtime Serverで使うデータ型を定義します（ONNXの標準定義）。

### 主要な型: TensorProto

```protobuf
message TensorProto {
  // テンソルの次元
  // 例: [1, 3, 224, 224]
  repeated int64 dims = 1;

  // データ型
  // 1 = FLOAT, 2 = UINT8, 3 = INT8, など
  int32 data_type = 2;

  // 生データ（バイナリ形式）
  bytes raw_data = 9;

  // その他のフィールド...
}
```

### Pythonでの使い方

```python
from src.proto import onnx_ml_pb2

# TensorProto作成
tensor = onnx_ml_pb2.TensorProto()

# 次元を設定
tensor.dims.extend([1, 3, 224, 224])
# または
# tensor.dims.append(1)
# tensor.dims.append(3)
# tensor.dims.append(224)
# tensor.dims.append(224)

# データ型を設定
tensor.data_type = 1  # FLOAT

# データを設定
import numpy as np
array = np.random.rand(1, 3, 224, 224).astype(np.float32)
tensor.raw_data = array.tobytes()

# サイズ確認
print(len(tensor.raw_data))  # 150,528 bytes
# = 1 * 3 * 224 * 224 * 4 bytes (float32)
```

## 🔧 Protocol Buffersファイルの再生成

`.proto`ファイルを変更したら、Pythonコードを再生成する必要があります。

### 手順

```bash
# 1. 一時的な仮想環境を作成（protobuf 4.25.3互換）
python3 -m venv .venv_temp
source .venv_temp/bin/activate

# 2. grpcio-toolsをインストール
pip install grpcio==1.60.0 grpcio-tools==1.60.0 protobuf==4.25.3

# 3. src/protoディレクトリに移動
cd src/proto

# 4. protoファイルをコンパイル
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  predict.proto prediction_service.proto onnx-ml.proto

# 5. インポート文を修正（手動）
# 生成されたファイルの import 文を修正:
# 'import onnx_ml_pb2' → 'from src.proto import onnx_ml_pb2'
# 'import predict_pb2' → 'from src.proto import predict_pb2'

# 6. 一時環境を削除
deactivate
cd ../..
rm -rf .venv_temp
```

### なぜ手動修正が必要？

`protoc`は相対インポートを生成しますが、Pythonプロジェクトでは絶対インポートが必要です：

```python
# protocが生成するコード（相対インポート）
import onnx_ml_pb2 as onnx__ml__pb2
# → ModuleNotFoundError!

# 修正後（絶対インポート）
from src.proto import onnx_ml_pb2 as onnx__ml__pb2
# → OK!
```

## 🔑 重要な概念

### Protocol Buffers vs JSON

| 特徴 | JSON | Protocol Buffers |
|------|------|------------------|
| **可読性** | ○ 人間が読める | × バイナリで読めない |
| **サイズ** | 大きい | 小さい（約1/3） |
| **速度** | 遅い | 速い（約5倍） |
| **型安全性** | × ゆるい | ○ 厳格 |
| **スキーマ** | なし | .proto ファイルで定義 |

**例: 同じデータのサイズ比較**

```json
// JSON: 約500バイト
{
  "inputs": {
    "input": {
      "dims": [1, 3, 224, 224],
      "dataType": 1,
      "rawData": "base64encodeddata..."
    }
  }
}
```

```python
# Protocol Buffers: 約150バイト
request.inputs["input"].dims = [1, 3, 224, 224]
request.inputs["input"].data_type = 1
request.inputs["input"].raw_data = image_bytes
# → バイナリ形式で約1/3のサイズ
```

### gRPC vs REST API

| 特徴 | REST API | gRPC |
|------|----------|------|
| **プロトコル** | HTTP/1.1 | HTTP/2 |
| **データ形式** | JSON（テキスト） | Protocol Buffers（バイナリ） |
| **速度** | 遅い | 速い |
| **ストリーミング** | × 難しい | ○ 簡単 |
| **ブラウザサポート** | ○ すべてのブラウザ | △ 限定的 |

**コード比較**

```python
# REST API（HTTPリクエスト）
import requests

response = requests.post(
    "http://pred:8001/predict",
    json={"inputs": {"input": {"dims": [1,3,224,224], ...}}}
)
output = response.json()["outputs"]["output"]

# gRPC
import grpc

channel = grpc.insecure_channel("pred:50051")
stub = PredictionServiceStub(channel)

request = PredictRequest()
request.inputs["input"].dims.extend([1, 3, 224, 224])

response = stub.Predict(request)
output = response.outputs["output"]
# → 約3倍速い！
```

## 🛠️ デバッグのヒント

### リクエスト/レスポンスの中身を確認

```python
# リクエストの内容を表示
print(request)
# PredictRequest {
#   inputs: {
#     "input": TensorProto {
#       dims: [1, 3, 224, 224]
#       data_type: 1
#       raw_data: "<150528 bytes>"
#     }
#   }
# }

# レスポンスの内容を表示
print(response)
# PredictResponse {
#   outputs: {
#     "output": TensorProto {
#       dims: [1, 1000]
#       data_type: 1
#       raw_data: "<4000 bytes>"
#     }
#   }
# }
```

### バイナリデータのサイズ確認

```python
# 送信データのサイズ
print(f"Request size: {len(request.SerializeToString())} bytes")

# 受信データのサイズ
print(f"Response size: {len(response.SerializeToString())} bytes")

# 生データのサイズ
print(f"Raw data size: {len(request.inputs['input'].raw_data)} bytes")
# 1 * 3 * 224 * 224 * 4 = 150,528 bytes
```

### gRPC接続エラーのデバッグ

```python
import grpc

try:
    channel = grpc.insecure_channel("pred:50051")
    stub = PredictionServiceStub(channel)
    response = stub.Predict(request, timeout=10)  # 10秒タイムアウト
except grpc.RpcError as e:
    print(f"gRPC error: {e.code()}")  # UNAVAILABLE, DEADLINE_EXCEEDED, など
    print(f"Details: {e.details()}")
```

## 🎯 まとめ

`proto/`ディレクトリは、Prep ServiceとPred Serviceの通信プロトコルを定義します：

- **predict.proto**: リクエスト/レスポンスのデータ構造
- **prediction_service.proto**: gRPCサービスのメソッド定義
- **onnx-ml.proto**: ONNXデータ型の定義

Protocol Buffersを使うことで、**JSONより小さく速いデータ通信**が実現できます。

これにより、機械学習の推論のような大量データのやり取りでも、効率的な通信が可能になります。
