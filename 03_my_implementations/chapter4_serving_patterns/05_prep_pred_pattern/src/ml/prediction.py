"""推論層（Prediction Layer）

ONNX Runtime ServerとgRPC通信して推論を実行する。

クラス:
- Data: 入力データモデル（Pydantic）
- Classifier: 画像分類器（前処理→推論→後処理）

フロー:
1. 画像を前処理（PytorchImagePreprocessTransformer）
2. numpy配列をTensorProtoに変換
3. gRPCでONNX Runtime Serverに推論リクエスト
4. レスポンスからロジットを取得
5. Softmax変換で確率分布に変換
6. ラベル名を返す（オプション）
"""

import json
from logging import getLogger
from typing import Any, List

import grpc
import joblib
import numpy as np
from PIL import Image
from pydantic import BaseModel
from src.configurations import ModelConfigurations
from src.ml.transformers import PytorchImagePreprocessTransformer, SoftmaxTransformer
from src.proto import onnx_ml_pb2, predict_pb2, prediction_service_pb2_grpc

logger = getLogger(__name__)


class Data(BaseModel):
    """入力データモデル

    Attributes:
        data: 画像データ（PIL ImageまたはBase64文字列）
    """
    # デフォルト値は小さな赤色画像（テスト用）
    data: Any = Image.new("RGB", (10, 10), color=(255, 0, 0))


class Classifier(object):
    """画像分類器
    
    ONNX Runtime ServerとgRPC通信して推論を実行する。
    
    Attributes:
        preprocess_transformer: 前処理transformer（画像→tensor）
        softmax_transformer: 後処理transformer（ロジット→確率）
        label: ImageNetラベルリスト（1000クラス）
        channel: gRPCチャネル
        stub: gRPCスタブ（PredictionService）
    """

    def __init__(
        self,
        preprocess_transformer_path: str = "/prep_pred_pattern/models/preprocess_transformer.pkl",
        softmax_transformer_path: str = "/prep_pred_pattern/models/softmax_transformer.pkl",
        label_path: str = "/prep_pred_pattern/data/image_net_labels.json",
        serving_address: str = "localhost:50051",
        onnx_input_name: str = "input",
        onnx_output_name: str = "output",
    ):
        """初期化
        
        Args:
            preprocess_transformer_path: 前処理transformerのパス
            softmax_transformer_path: Softmax transformerのパス
            label_path: ImageNetラベルファイルのパス
            serving_address: ONNX Runtime Serverのアドレス（host:port）
            onnx_input_name: ONNXモデルの入力名
            onnx_output_name: ONNXモデルの出力名
        """
        self.preprocess_transformer_path: str = preprocess_transformer_path
        self.softmax_transformer_path: str = softmax_transformer_path
        self.preprocess_transformer: PytorchImagePreprocessTransformer = None
        self.softmax_transformer: SoftmaxTransformer = None

        self.serving_address = serving_address
        self.channel = grpc.insecure_channel(self.serving_address)
        self.stub = prediction_service_pb2_grpc.PredictionServiceStub(self.channel)

        self.label_path = label_path
        self.label: List[str] = []

        self.onnx_input_name: str = onnx_input_name
        self.onnx_output_name: str = onnx_output_name

        self.load_model()
        self.load_label()

    def load_model(self):
        """モデル（transformer）を読み込む
        
        - 前処理transformer（画像→tensor）
        - Softmax transformer（ロジット→確率）
        """
        logger.info(f"load preprocess in {self.preprocess_transformer_path}")
        self.preprocess_transformer = joblib.load(self.preprocess_transformer_path)
        logger.info(f"initialized preprocess")

        logger.info(f"load postprocess in {self.softmax_transformer_path}")
        self.softmax_transformer = joblib.load(self.softmax_transformer_path)
        logger.info(f"initialized postprocess")

    def load_label(self):
        """ImageNetラベルを読み込む
        
        JSONファイルから1000クラスのラベルリストを読み込む。
        """
        logger.info(f"load label in {self.label_path}")
        with open(self.label_path, "r") as f:
            self.label = json.load(f)
        logger.info(f"label: {self.label}")

    def predict(self, data: Image) -> List[float]:
        """推論実行（確率を返す）
        
        フロー:
        1. 画像を前処理
        2. numpy配列をTensorProtoに変換
        3. gRPCでONNX Runtime Serverに推論リクエスト
        4. レスポンスからロジットを取得
        5. Softmax変換で確率分布に変換
        
        Args:
            data: PIL Image
            
        Returns:
            確率分布リスト [[p1, p2, ..., p1000]]
        """
        # 前処理: PIL Image → (1, 3, 224, 224) numpy配列
        preprocessed = self.preprocess_transformer.transform(data)

        # TensorProtoの作成
        input_tensor = onnx_ml_pb2.TensorProto()
        input_tensor.dims.extend(preprocessed.shape)
        input_tensor.data_type = 1  # float32
        input_tensor.raw_data = preprocessed.tobytes()

        # gRPCリクエストメッセージの作成
        request_message = predict_pb2.PredictRequest()
        request_message.inputs[self.onnx_input_name].data_type = input_tensor.data_type
        request_message.inputs[self.onnx_input_name].dims.extend(preprocessed.shape)
        request_message.inputs[self.onnx_input_name].raw_data = input_tensor.raw_data

        # gRPCで推論リクエスト送信
        response = self.stub.Predict(request_message)
        
        # レスポンスからロジットを取得
        output = np.frombuffer(response.outputs[self.onnx_output_name].raw_data, dtype=np.float32)

        # Softmax変換: ロジット → 確率分布
        softmax = self.softmax_transformer.transform(output).tolist()

        logger.info(f"predict proba {softmax}")
        return softmax

    def predict_label(self, data: Image) -> str:
        """推論実行（ラベル名を返す）
        
        確率が最大のクラスのラベル名を返す。
        
        Args:
            data: PIL Image
            
        Returns:
            クラス名（例: "Siamese cat"）
        """
        softmax = self.predict(data=data)
        argmax = int(np.argmax(np.array(softmax)[0]))
        return self.label[argmax]


# グローバルインスタンス（FastAPIから使用）
# テスト時はモックを使用するため、ここでは初期化しない
# 実際の使用時（FastAPI起動時）に初期化する
classifier = None


def get_classifier() -> Classifier:
    """Classifierインスタンスを取得（遅延初期化）

    テスト時にモックしやすいように、グローバル変数は直接初期化せず、
    この関数経由で取得する。

    Returns:
        Classifierインスタンス
    """
    global classifier
    if classifier is None:
        classifier = Classifier(
            preprocess_transformer_path=ModelConfigurations().preprocess_transformer_path,
            softmax_transformer_path=ModelConfigurations().softmax_transformer_path,
            label_path=ModelConfigurations().label_path,
            serving_address=f"{ModelConfigurations.api_address}:{ModelConfigurations.grpc_port}",
            onnx_input_name=ModelConfigurations().onnx_input_name,
            onnx_output_name=ModelConfigurations().onnx_output_name,
        )
    return classifier
