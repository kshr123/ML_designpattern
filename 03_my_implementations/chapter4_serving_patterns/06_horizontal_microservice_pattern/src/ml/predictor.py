"""ONNX Runtime推論

各専門サービスで使用する推論クライアント
"""

from typing import List

import numpy as np
import onnxruntime as ort


class ONNXPredictor:
    """ONNX Runtime推論クライアント"""

    def __init__(self, model_path: str):
        """初期化

        Args:
            model_path: ONNXモデルのパス
        """
        self.model_path = model_path
        self.session = ort.InferenceSession(model_path)

        # 入出力名を取得
        self.input_name = self.session.get_inputs()[0].name
        self.output_names = [output.name for output in self.session.get_outputs()]

    def predict(self, data: List[List[float]]) -> List[float]:
        """推論実行

        Args:
            data: 入力データ（Iris特徴量）

        Returns:
            バイナリ分類の確率 [そのクラスである確率, そのクラスでない確率]
        """
        # NumPy配列に変換
        input_data = np.array(data, dtype=np.float32)

        # 推論実行
        outputs = self.session.run(self.output_names, {self.input_name: input_data})

        # outputs[1]は確率値（dict形式）を含む
        # 例: [{0: 0.98, 1: 0.02}]
        prob_dict = outputs[1][0]

        # dictから確率リストに変換
        probs = [prob_dict[i] for i in sorted(prob_dict.keys())]

        return probs
