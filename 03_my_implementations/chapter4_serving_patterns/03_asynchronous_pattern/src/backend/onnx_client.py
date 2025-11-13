"""ONNX Runtime クライアント

ONNXモデルで推論を実行する
"""

import json
from pathlib import Path
from typing import List, Optional

import numpy as np
import onnxruntime as ort


class ONNXClient:
    """ONNX Runtime クライアント"""

    def __init__(self, model_path: str = "models/iris_svc.onnx", label_path: str = "models/label.json"):
        """初期化

        Args:
            model_path: ONNXモデルのパス
            label_path: ラベル定義のパス
        """
        self.model_path = model_path
        self.label_path = label_path

        # ONNX Runtimeセッション
        self.session = ort.InferenceSession(model_path)

        # ラベル読み込み
        with open(label_path, "r") as f:
            label_data = json.load(f)
            self.class_names = {int(k): v for k, v in label_data.items()}

        # 入出力名を取得
        self.input_name = self.session.get_inputs()[0].name
        self.output_names = [output.name for output in self.session.get_outputs()]

    def predict(self, data: List[List[float]], timeout: int = 10) -> Optional[List[dict]]:
        """推論実行

        Args:
            data: 入力データ（Iris特徴量のリスト）
            timeout: タイムアウト（秒）※ONNXでは未使用

        Returns:
            推論結果のリスト（各要素に prediction, class_name, probabilities を含む）
            エラー時はNone
        """
        try:
            # NumPy配列に変換
            input_data = np.array(data, dtype=np.float32)

            # 推論実行
            outputs = self.session.run(self.output_names, {self.input_name: input_data})

            # predictions: クラス番号、probabilities: 確率値（dictのリスト）
            predictions = outputs[0]  # shape: (batch_size,)
            probabilities = outputs[1]  # list of dicts: [{0: prob0, 1: prob1, 2: prob2}]

            # 結果を整形
            results = []
            for pred, prob_dict in zip(predictions, probabilities):
                prediction = int(pred)
                class_name = self.class_names.get(prediction, "unknown")

                # dictから確率リストに変換（クラス順にソート）
                prob_list = [prob_dict[i] for i in sorted(prob_dict.keys())]

                results.append(
                    {
                        "prediction": prediction,
                        "class_name": class_name,
                        "probabilities": prob_list,
                    }
                )

            return results

        except Exception as e:
            print(f"ONNX prediction error: {e}")
            return None

    def close(self) -> None:
        """クリーンアップ（ONNX Runtimeでは不要だが互換性のため）"""
        pass
