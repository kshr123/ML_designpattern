"""推論ロジック - ONNXモデルを使った分類"""
import json
from logging import getLogger
from typing import Dict, List

import numpy as np
import onnxruntime as rt
from pydantic import BaseModel

from src.configurations import ModelConfigurations

logger = getLogger(__name__)


class Data(BaseModel):
    """推論リクエストのデータモデル"""

    data: List[List[float]] = [[5.1, 3.5, 1.4, 0.2]]


class Classifier:
    """ONNXモデルによる分類器"""

    def __init__(self, model_filepath: str, label_filepath: str):
        """
        分類器の初期化

        Args:
            model_filepath: ONNXモデルファイルのパス
            label_filepath: ラベルファイル（JSON）のパス
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
        """ONNXモデルをロードする"""
        logger.info(f"load model from {self.model_filepath}")
        self.classifier = rt.InferenceSession(self.model_filepath)
        self.input_name = self.classifier.get_inputs()[0].name
        self.output_name = self.classifier.get_outputs()[0].name
        logger.info(f"model loaded successfully")

    def load_label(self) -> None:
        """ラベルファイル（JSON）をロードする"""
        logger.info(f"load label from {self.label_filepath}")
        with open(self.label_filepath, "r") as f:
            self.label = json.load(f)
        logger.info(f"label: {self.label}")

    def predict(self, data: List[List[float]]) -> np.ndarray:
        """
        推論を実行して確率値を返す

        Args:
            data: 入力データ（shape: [batch_size, 4]）

        Returns:
            各クラスの確率値（shape: [3]）
        """
        np_data = np.array(data).astype(np.float32)
        prediction = self.classifier.run(None, {self.input_name: np_data})
        output = np.array(list(prediction[1][0].values()))
        logger.info(f"predict proba: {output}")
        return output

    def predict_label(self, data: List[List[float]]) -> str:
        """
        推論を実行してラベル名を返す

        Args:
            data: 入力データ（shape: [batch_size, 4]）

        Returns:
            予測されたクラスのラベル名
        """
        prediction = self.predict(data)
        argmax = int(np.argmax(np.array(prediction)))
        return self.label[str(argmax)]


# グローバルインスタンス（アプリケーション起動時に初期化）
classifier = Classifier(
    model_filepath=ModelConfigurations.model_filepath,
    label_filepath=ModelConfigurations.label_filepath,
)
