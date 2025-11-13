"""
推論モジュール

ONNX Runtimeを使用したIris分類モデルの推論を行います。
"""

import json
from typing import Dict, List

import numpy as np
import onnxruntime as rt
from pydantic import BaseModel

from src.configurations.constants import ModelConfigurations


class Data(BaseModel):
    """
    入力データモデル

    Irisの4つの特徴量を受け取ります。
    """

    data: List[List[float]] = [[5.1, 3.5, 1.4, 0.2]]


class Classifier:
    """
    ONNX分類器クラス

    ONNXモデルを読み込み、推論を実行します。
    """

    def __init__(
        self,
        model_filepath: str,
        label_filepath: str,
    ):
        """
        Classifierの初期化

        Args:
            model_filepath: ONNXモデルファイルのパス
            label_filepath: ラベルファイルのパス
        """
        self.model_filepath: str = model_filepath
        self.label_filepath: str = label_filepath
        self.classifier = None
        self.label: Dict[str, str] = {}
        self.input_name: str = ""
        self.output_name: str = ""

        self.load_model()
        self.load_label()

    def load_model(self):
        """ONNXモデルを読み込む"""
        self.classifier = rt.InferenceSession(self.model_filepath)
        self.input_name = self.classifier.get_inputs()[0].name
        self.output_name = self.classifier.get_outputs()[0].name

    def load_label(self):
        """ラベルファイルを読み込む"""
        with open(self.label_filepath, "r") as f:
            self.label = json.load(f)

    def predict(self, data: List[List[float]]) -> np.ndarray:
        """
        推論を実行（確率値を返す）

        Args:
            data: 入力データ [[sepal_length, sepal_width, petal_length, petal_width]]

        Returns:
            確率値の配列 [setosa確率, versicolor確率, virginica確率]
        """
        np_data = np.array(data).astype(np.float32)
        prediction = self.classifier.run(None, {self.input_name: np_data})
        # prediction[1]は辞書形式で確率値を含む
        output = np.array(list(prediction[1][0].values()))
        return output

    def predict_label(self, data: List[List[float]]) -> str:
        """
        推論を実行（ラベル名を返す）

        Args:
            data: 入力データ [[sepal_length, sepal_width, petal_length, petal_width]]

        Returns:
            ラベル名 ("setosa" | "versicolor" | "virginica")
        """
        prediction = self.predict(data=data)
        argmax = int(np.argmax(np.array(prediction)))
        return self.label[str(argmax)]


# グローバルインスタンス（アプリケーション起動時に1度だけ初期化）
classifier = Classifier(
    model_filepath=ModelConfigurations.model_filepath,
    label_filepath=ModelConfigurations.label_filepath,
)
