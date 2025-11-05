"""ONNX Exporter - ONNXモデルの変換とエクスポート"""

from sklearn.pipeline import Pipeline
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType


def export_to_onnx(model: Pipeline, filepath: str) -> None:
    """
    scikit-learnモデルをONNX形式に変換して保存する

    Args:
        model: 学習済みscikit-learnパイプライン
        filepath: 保存先のファイルパス
    """
    # 入力の型を定義（4特徴量のfloat型）
    initial_type = [("float_input", FloatTensorType([None, 4]))]

    # ONNX変換
    onnx_model = convert_sklearn(model, initial_types=initial_type)

    # ファイル保存
    with open(filepath, "wb") as f:
        f.write(onnx_model.SerializeToString())
