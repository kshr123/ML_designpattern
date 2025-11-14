# ml/ - 機械学習ロジック

## 📚 このディレクトリについて

このディレクトリには、**Prep Service（前処理サービス）** の機械学習ロジックが含まれています。

主な役割：
- 画像の前処理（PIL Image → ResNet50用のテンソル）
- Pred Service（ONNX Runtime Server）とのgRPC通信
- 推論結果の後処理（ロジット → 確率 → ラベル名）

## 📁 ファイル構成

```
ml/
├── README.md           # このファイル
├── prediction.py       # 推論ロジック + gRPC通信
└── transformers.py     # 前処理・後処理の変換器
```

## 🔄 処理フロー全体図

```
┌─────────────────────────────────────────────────────────────┐
│  入力: PIL Image（猫の画像）                                │
│  例: cat.jpg (224x224, RGB)                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  1. 前処理（transformers.py）                               │
│                                                              │
│     PytorchImagePreprocessTransformer                       │
│     ・リサイズ: 224x224                                     │
│     ・正規化: ImageNet統計で標準化                          │
│     ・次元変換: (H,W,C) → (N,C,H,W)                        │
│                                                              │
│     入力: PIL Image (224, 224, 3)                           │
│     出力: numpy配列 (1, 3, 224, 224)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  2. gRPC通信準備（prediction.py）                           │
│                                                              │
│     numpy配列 → TensorProto                                 │
│     request.inputs["input"].dims = [1, 3, 224, 224]         │
│     request.inputs["input"].raw_data = array.tobytes()      │
└────────────────────────┬────────────────────────────────────┘
                         │ gRPCリクエスト
                         │ (バイナリデータ)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Pred Service（ONNX Runtime Server）                     │
│                                                              │
│     ResNet50モデルで推論                                    │
│     入力: (1, 3, 224, 224) tensor                           │
│     出力: (1, 1000) logits（ロジット）                      │
└────────────────────────┬────────────────────────────────────┘
                         │ gRPCレスポンス
                         │ (バイナリデータ)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 後処理（prediction.py + transformers.py）               │
│                                                              │
│     TensorProto → numpy配列                                 │
│     logits = np.frombuffer(response.outputs["output"])      │
│                                                              │
│     SoftmaxTransformer                                      │
│     logits → probabilities（確率分布）                      │
│     例: [0.0001, 0.82, 0.0003, ...]                        │
│                                                              │
│     確率が最大のクラスを取得                                │
│     argmax = 281  # tabby catのクラスID                    │
│     label = labels[281]  # "tabby cat"                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  出力: "tabby cat"                                          │
└─────────────────────────────────────────────────────────────┘
```

## 📄 transformers.py - 前処理・後処理

### PytorchImagePreprocessTransformer - 画像前処理

ResNet50に入力する前に、画像を正しい形式に変換します。

#### 処理内容

```python
class PytorchImagePreprocessTransformer:
    """
    PyTorch ResNet50用の画像前処理

    処理ステップ:
    1. リサイズ: 256x256に拡大
    2. 中央クロップ: 224x224に切り出し
    3. numpy配列化: PIL Image → numpy
    4. 正規化: ImageNetの統計値で標準化
       - mean = [0.485, 0.456, 0.406]
       - std = [0.229, 0.224, 0.225]
    5. 次元変換: (H, W, C) → (N, C, H, W)
       - H: 高さ, W: 幅, C: チャネル, N: バッチサイズ
    """

    def transform(self, data: Image) -> np.ndarray:
        # 1. リサイズ
        data = data.resize((256, 256))

        # 2. 中央クロップ（224x224）
        width, height = data.size
        left = (width - 224) // 2
        top = (height - 224) // 2
        data = data.crop((left, top, left + 224, top + 224))

        # 3. numpy配列化
        data = np.array(data)  # (224, 224, 3)

        # 4. 正規化
        data = data / 255.0  # [0, 255] → [0, 1]
        data = (data - self.mean) / self.std

        # 5. 次元変換
        data = np.transpose(data, (2, 0, 1))  # (H,W,C) → (C,H,W)
        data = np.expand_dims(data, axis=0)   # (C,H,W) → (N,C,H,W)

        return data  # (1, 3, 224, 224)
```

#### 具体例

```python
# 入力: 猫の画像
cat_image = Image.open("cat.jpg")  # (500, 400, 3) RGB

# 前処理実行
transformer = PytorchImagePreprocessTransformer()
preprocessed = transformer.transform(cat_image)

# 出力: ResNet50用のテンソル
print(preprocessed.shape)  # (1, 3, 224, 224)
print(preprocessed.dtype)  # float32
print(preprocessed.min(), preprocessed.max())  # 約-2.0 ~ 2.0
```

### SoftmaxTransformer - 確率分布への変換

モデルの生出力（ロジット）を確率分布に変換します。

#### 処理内容

```python
class SoftmaxTransformer:
    """
    ロジットを確率分布に変換

    Softmax関数:
    p_i = exp(x_i) / Σexp(x_j)

    例:
    logits = [2.0, 1.0, 0.1]
    →
    probabilities = [0.659, 0.242, 0.099]  # 合計 = 1.0
    """

    def transform(self, data: np.ndarray) -> np.ndarray:
        # 数値安定性のため、最大値を引く
        data = data - np.max(data)

        # Softmax計算
        exp_data = np.exp(data)
        sum_exp_data = np.sum(exp_data)
        probabilities = exp_data / sum_exp_data

        return probabilities.reshape(1, -1)  # (1, 1000)
```

#### 具体例

```python
# 入力: ONNXモデルの出力（ロジット）
logits = np.array([2.3, 5.1, 1.2, 3.4, ...])  # 1000個

# Softmax変換
transformer = SoftmaxTransformer()
probabilities = transformer.transform(logits)

# 出力: 確率分布
print(probabilities.shape)  # (1, 1000)
print(probabilities.sum())  # 1.0（合計100%）
print(probabilities.max())  # 0.82（最大確率82%）

# 最も確率が高いクラス
top_class = np.argmax(probabilities)  # 281
print(labels[top_class])  # "tabby cat"
```

## 📄 prediction.py - 推論ロジック

### Classifierクラス - メインロジック

画像分類の全体フローを制御するクラスです。

#### 初期化

```python
class Classifier:
    def __init__(
        self,
        serving_address: str = "pred:50051",
        onnx_input_name: str = "input",
        onnx_output_name: str = "output",
    ):
        """
        初期化処理

        1. gRPC接続の確立
        2. 前処理transformerの読み込み
        3. 後処理transformerの読み込み
        4. ImageNetラベルの読み込み
        """
        # gRPC接続
        self.channel = grpc.insecure_channel(serving_address)
        self.stub = PredictionServiceStub(self.channel)

        # モデル読み込み
        self.preprocess_transformer = joblib.load("preprocess.pkl")
        self.softmax_transformer = joblib.load("softmax.pkl")

        # ラベル読み込み
        with open("labels.json") as f:
            self.label = json.load(f)  # 1000個のラベル
```

#### predict() - 確率を返す

```python
def predict(self, data: Image) -> List[float]:
    """
    画像から確率分布を取得

    フロー:
    1. 前処理: PIL Image → (1,3,224,224) numpy配列
    2. gRPCリクエスト作成
    3. Pred Serviceに送信
    4. レスポンス受信
    5. 後処理: ロジット → 確率

    Args:
        data: PIL Image（猫の画像など）

    Returns:
        確率分布 [[0.001, 0.82, 0.003, ...]]
        1000クラスの確率リスト
    """
    # 1. 前処理
    preprocessed = self.preprocess_transformer.transform(data)
    # → (1, 3, 224, 224) numpy配列

    # 2. gRPCリクエスト作成
    request = PredictRequest()
    request.inputs["input"].dims.extend([1, 3, 224, 224])
    request.inputs["input"].data_type = 1  # float32
    request.inputs["input"].raw_data = preprocessed.tobytes()

    # 3. gRPCで送信
    response = self.stub.Predict(request)
    # ← Pred Serviceで推論実行

    # 4. レスポンス取得
    output = np.frombuffer(
        response.outputs["output"].raw_data,
        dtype=np.float32
    )
    # → (1000,) numpy配列（ロジット）

    # 5. 後処理
    probabilities = self.softmax_transformer.transform(output)
    # → (1, 1000) 確率分布

    return probabilities.tolist()
```

#### predict_label() - ラベル名を返す

```python
def predict_label(self, data: Image) -> str:
    """
    画像からラベル名を取得

    predict()を内部で呼び出し、
    最も確率が高いクラスのラベル名を返す

    Args:
        data: PIL Image

    Returns:
        ラベル名（例: "tabby cat"）
    """
    # 確率分布を取得
    probabilities = self.predict(data)
    # [[0.001, 0.82, 0.003, ...]]

    # 最も確率が高いクラスのインデックス
    argmax = int(np.argmax(probabilities))
    # → 281

    # ラベル名を返す
    return self.label[argmax]
    # → "tabby cat"
```

### 具体的な使用例

```python
# 初期化（起動時に1回）
classifier = Classifier(
    serving_address="pred:50051",
    onnx_input_name="input",
    onnx_output_name="output"
)

# 推論実行（リクエストごと）
cat_image = Image.open("cat.jpg")

# パターン1: 確率分布を取得
probabilities = classifier.predict(cat_image)
print(probabilities[0][:5])
# [0.001, 0.003, 0.820, 0.002, 0.005]

# パターン2: ラベル名を取得
label = classifier.predict_label(cat_image)
print(label)
# "tabby cat"
```

## 🔑 重要な概念

### 1. gRPC通信の仕組み

```python
# 1. 接続確立（初期化時に1回）
channel = grpc.insecure_channel("pred:50051")
stub = PredictionServiceStub(channel)

# 2. リクエスト作成
request = PredictRequest()
request.inputs["input"].dims = [1, 3, 224, 224]
request.inputs["input"].raw_data = image_bytes

# 3. 送信（同期的に待機）
response = stub.Predict(request)
# ↑ここでネットワーク通信が発生
# Pred Serviceから応答が返るまで待つ

# 4. レスポンス取得
output = response.outputs["output"].raw_data
```

### 2. データ型の変換

```python
# PIL Image → numpy配列
image = Image.open("cat.jpg")
array = np.array(image)  # (224, 224, 3)

# numpy配列 → bytes（gRPC送信用）
array_bytes = array.tobytes()

# bytes → numpy配列（gRPC受信後）
array = np.frombuffer(array_bytes, dtype=np.float32)

# numpy配列 → Pythonリスト（JSON用）
list_data = array.tolist()
```

### 3. シングルトンパターン

```python
# グローバル変数（最初はNone）
classifier = None

def get_classifier():
    """
    Classifierインスタンスを取得

    初回のみ初期化し、2回目以降は再利用
    → メモリ効率が良い
    → モデル読み込みが1回だけ
    """
    global classifier
    if classifier is None:
        # 初回のみ初期化
        classifier = Classifier(...)
    return classifier
```

## 🛠️ 開発時のヒント

### デバッグ用のログ

```python
import logging

logger = logging.getLogger(__name__)

def predict(self, data: Image):
    logger.info("Starting prediction")
    preprocessed = self.preprocess_transformer.transform(data)
    logger.info(f"Preprocessed shape: {preprocessed.shape}")

    response = self.stub.Predict(request)
    logger.info(f"Received response from Pred Service")

    return probabilities
```

### エラーハンドリング

```python
def predict(self, data: Image):
    try:
        preprocessed = self.preprocess_transformer.transform(data)
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        raise

    try:
        response = self.stub.Predict(request)
    except grpc.RpcError as e:
        logger.error(f"gRPC call failed: {e}")
        raise

    return probabilities
```

### ユニットテスト

```python
def test_preprocess_transformer():
    # テスト画像作成
    image = Image.new("RGB", (224, 224), color=(255, 0, 0))

    # 前処理実行
    transformer = PytorchImagePreprocessTransformer()
    result = transformer.transform(image)

    # 検証
    assert result.shape == (1, 3, 224, 224)
    assert result.dtype == np.float32
```

## 🎯 まとめ

`ml/`ディレクトリは、Prep Serviceの中核となる機械学習ロジックを提供します：

- **transformers.py**: 前処理（画像→テンソル）と後処理（ロジット→確率）
- **prediction.py**: gRPC通信による推論の実行と結果の整形

全体として、「画像を入力したらラベル名を返す」というシンプルなインターフェースを提供しつつ、内部では複雑な前処理・gRPC通信・後処理を実行しています。
