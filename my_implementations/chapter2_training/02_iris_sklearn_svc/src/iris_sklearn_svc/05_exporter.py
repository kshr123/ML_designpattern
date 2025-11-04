"""
Exporter module for ONNX conversion
"""

from sklearn.pipeline import Pipeline
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType


def export_to_onnx(trained_model: Pipeline, output_path: str) -> None:
    """
    学習済みモデルをONNX形式に変換して保存

    Args:
        trained_model (Pipeline): 学習済みscikit-learnパイプライン
        output_path (str): 出力ファイルパス（.onnx）
    """
    # 入力の型と形状を定義
    # Irisデータセットは4次元特徴量、batch_sizeはNone（可変）
    initial_type = [("float_input", FloatTensorType([None, 4]))]

    # scikit-learnモデルをONNXに変換
    onnx_model = convert_sklearn(trained_model, initial_types=initial_type)

    # ONNXモデルをファイルに保存
    with open(output_path, "wb") as f:
        f.write(onnx_model.SerializeToString())
