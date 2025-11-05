"""
推論ロジックモジュール

このモジュールはONNXモデルを読み込み、推論を実行します。
- Data: 入力データのPydanticモデル
- Classifier: 推論を実行するクラス
"""

import json
from logging import getLogger
from pathlib import Path
from typing import Dict, List

import numpy as np
import onnxruntime as rt
from pydantic import BaseModel

logger = getLogger(__name__)


class Data(BaseModel):
    """
    推論用の入力データモデル

    Attributes:
        data: 特徴量の2次元配列（デフォルト: Irisのsetosaサンプル）
    """

    data: List[List[float]] = [[5.1, 3.5, 1.4, 0.2]]


class Classifier:
    """
    ONNX モデルを使用した分類器クラス

    このクラスはONNXモデルとラベルファイルを読み込み、
    推論を実行します。

    Attributes:
        model_filepath: ONNXモデルファイルのパス
        label_filepath: ラベルファイル（JSON）のパス
        classifier: ONNXRuntimeの推論セッション
        label: クラスインデックスとラベル名のマッピング
        input_name: モデルの入力名
        output_name: モデルの出力名
    """

    def __init__(self, model_filepath: str, label_filepath: str):
        """
        Classifierを初期化する

        Args:
            model_filepath: ONNXモデルファイルのパス
            label_filepath: ラベルファイル（JSON）のパス
        """
        self.model_filepath: str = model_filepath
        self.label_filepath: str = label_filepath
        self.classifier: rt.InferenceSession = None  # type: ignore
        self.label: Dict[str, str] = {}
        self.input_name: str = ""
        self.output_name: str = ""

        self.load_model()
        self.load_label()

    def load_model(self) -> None:
        """
        ONNXモデルを読み込む

        Raises:
            FileNotFoundError: モデルファイルが見つからない場合
            Exception: モデルの読み込みに失敗した場合
        """
        logger.info(f"モデルを読み込みます: {self.model_filepath}")

        if not Path(self.model_filepath).exists():
            raise FileNotFoundError(f"モデルファイルが見つかりません: {self.model_filepath}")

        try:
            self.classifier = rt.InferenceSession(self.model_filepath)
            self.input_name = self.classifier.get_inputs()[0].name
            self.output_name = self.classifier.get_outputs()[0].name
            logger.info("モデルの読み込みが完了しました")
            logger.info(f"入力名: {self.input_name}, 出力名: {self.output_name}")
        except Exception as e:
            logger.error(f"モデルの読み込みに失敗しました: {e}")
            raise

    def load_label(self) -> None:
        """
        ラベルファイルを読み込む

        Raises:
            FileNotFoundError: ラベルファイルが見つからない場合
            json.JSONDecodeError: JSONの解析に失敗した場合
        """
        logger.info(f"ラベルを読み込みます: {self.label_filepath}")

        if not Path(self.label_filepath).exists():
            raise FileNotFoundError(f"ラベルファイルが見つかりません: {self.label_filepath}")

        try:
            with open(self.label_filepath, "r", encoding="utf-8") as f:
                self.label = json.load(f)
            logger.info(f"ラベルの読み込みが完了しました: {self.label}")
        except json.JSONDecodeError as e:
            logger.error(f"ラベルファイルの解析に失敗しました: {e}")
            raise
        except Exception as e:
            logger.error(f"ラベルファイルの読み込みに失敗しました: {e}")
            raise

    def predict(self, data: List[List[float]]) -> np.ndarray:
        """
        推論を実行して確率値を返す

        Args:
            data: 特徴量の2次元配列 (N, 4)

        Returns:
            各クラスの確率値の配列 (3,)

        Raises:
            ValueError: 入力データの形状が不正な場合
            Exception: 推論に失敗した場合
        """
        try:
            # データをnumpy配列に変換
            np_data = np.array(data).astype(np.float32)

            # 推論実行
            prediction = self.classifier.run(None, {self.input_name: np_data})

            # SVMモデルの出力は2番目の要素に確率が入っている
            # prediction[1]は辞書型で、キーが各クラス、値が確率
            if isinstance(prediction[1], list) and len(prediction[1]) > 0:
                probabilities = prediction[1][0]
                if isinstance(probabilities, dict):
                    # 辞書の値を配列に変換（クラス順）
                    output = np.array(list(probabilities.values()))
                else:
                    output = np.array(probabilities)
            else:
                # フォールバック: prediction[1]を直接使用
                output = np.array(prediction[1])

            logger.info(f"推論結果: {output}")
            return output

        except Exception as e:
            logger.error(f"推論に失敗しました: {e}")
            raise

    def predict_label(self, data: List[List[float]]) -> str:
        """
        推論を実行してラベル名を返す

        Args:
            data: 特徴量の2次元配列 (N, 4)

        Returns:
            予測されたクラスのラベル名

        Raises:
            ValueError: 入力データの形状が不正な場合
            KeyError: ラベルが見つからない場合
            Exception: 推論に失敗した場合
        """
        try:
            # 確率値を取得
            prediction = self.predict(data=data)

            # 最大確率のクラスインデックスを取得
            argmax = int(np.argmax(prediction))

            # ラベル名を取得
            label = self.label[str(argmax)]
            logger.info(f"予測ラベル: {label} (クラス: {argmax})")

            return label

        except KeyError as e:
            logger.error(f"ラベルが見つかりません: {e}")
            raise
        except Exception as e:
            logger.error(f"ラベル推論に失敗しました: {e}")
            raise
