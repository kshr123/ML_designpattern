"""推論モジュール

ONNX Runtimeを使用したIris分類モデルの推論を提供します。
"""

import json
from logging import getLogger
from typing import Dict, List

import numpy as np
import onnxruntime as rt
from pydantic import BaseModel

from src.configurations import ModelConfigurations
from src.constants import CONSTANTS

logger = getLogger(__name__)


class Data(BaseModel):
    """推論入力データのスキーマ"""

    data: List[List[float]] = [[5.1, 3.5, 1.4, 0.2]]


class Classifier:
    """
    ONNX Runtime推論クラス

    Irisデータセットの3クラス分類モデルを読み込み、推論を実行します。
    """

    def __init__(self, model_filepath: str, label_filepath: str):
        """
        初期化

        Args:
            model_filepath: ONNXモデルファイルパス
            label_filepath: ラベルファイル（JSON）パス
        """
        self.model_filepath = model_filepath
        self.label_filepath = label_filepath
        self.classifier = None
        self.label: Dict[str, str] = {}
        self.input_name = ""
        self.output_name = ""

        self.load_model()
        self.load_label()

    def load_model(self) -> None:
        """ONNXモデルを読み込む"""
        logger.info(f"Loading model from {self.model_filepath}")
        self.classifier = rt.InferenceSession(self.model_filepath)
        self.input_name = self.classifier.get_inputs()[0].name
        self.output_name = self.classifier.get_outputs()[0].name
        logger.info(f"Model loaded successfully. Input: {self.input_name}, Output: {self.output_name}")

    def load_label(self) -> None:
        """ラベルファイルを読み込む"""
        logger.info(f"Loading labels from {self.label_filepath}")
        with open(self.label_filepath, "r") as f:
            self.label = json.load(f)
        logger.info(f"Labels loaded: {self.label}")

    def predict(self, data: List[List[float]]) -> np.ndarray:
        """
        推論を実行（確率値を返す）

        Args:
            data: 入力データ [[feature1, feature2, feature3, feature4]]

        Returns:
            各クラスの確率値（ndarray）
        """
        np_data = np.array(data).astype(np.float32)
        prediction = self.classifier.run(None, {self.input_name: np_data})

        # ONNX Runtimeの出力形式: prediction[1][0]が確率値のdict
        # 例: {0: 0.971, 1: 0.016, 2: 0.013}
        output = np.array(list(prediction[1][0].values()))
        logger.info(f"Prediction probabilities: {output}")

        return output

    def predict_dict(self, data: List[List[float]]) -> Dict[str, float]:
        """
        推論を実行（Dict形式で確率値を返す）

        Args:
            data: 入力データ [[feature1, feature2, feature3, feature4]]

        Returns:
            {"0": 0.971, "1": 0.016, "2": 0.013}
        """
        prediction = self.predict(data)
        result = {str(i): float(prob) for i, prob in enumerate(prediction)}
        logger.info(f"Prediction result: {result}")
        return result

    def predict_label(self, data: List[List[float]]) -> str:
        """
        推論を実行（クラスラベルを返す）

        Args:
            data: 入力データ [[feature1, feature2, feature3, feature4]]

        Returns:
            クラスラベル（"setosa", "versicolor", "virginica"）
        """
        prediction = self.predict(data)
        argmax = int(np.argmax(prediction))
        label = self.label[str(argmax)]
        logger.info(f"Predicted label: {label} (class {argmax})")
        return label

    def get_metadata(self) -> Dict[str, any]:
        """
        モデルメタデータを取得

        Returns:
            モデル情報のDict
        """
        return {
            "model_name": "iris_svc",
            "model_type": "ONNX",
            "input_dim": CONSTANTS.IRIS_FEATURE_DIM,
            "output_dim": CONSTANTS.IRIS_NUM_CLASSES,
            "labels": self.label,
        }


# グローバルインスタンス（起動時に1回だけロード）
classifier = Classifier(
    model_filepath=ModelConfigurations.model_filepath,
    label_filepath=ModelConfigurations.label_filepath,
)
