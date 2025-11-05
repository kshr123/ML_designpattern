"""
ONNXエクスポートと検証モジュール。

このモジュールはscikit-learnモデルをONNX形式にエクスポートし、
エクスポートされたモデルを検証する機能を提供します。
"""

import numpy as np
import onnxruntime as rt
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.pipeline import Pipeline


def export_to_onnx(pipeline: Pipeline, onnx_path: str) -> None:
    """
    scikit-learnパイプラインをONNX形式にエクスポートする。

    Args:
        pipeline: 学習済みscikit-learn Pipeline
        onnx_path: ONNXモデルの保存先パス

    Raises:
        Exception: モデルが未学習または変換に失敗した場合
    """
    # 入力タイプの定義（Irisデータセットは4特徴量）
    initial_type = [("float_input", FloatTensorType([None, 4]))]

    # ONNXに変換
    onnx_model = convert_sklearn(pipeline, initial_types=initial_type)

    # ファイルに保存
    with open(onnx_path, "wb") as f:
        f.write(onnx_model.SerializeToString())


def validate_onnx_model(
    pipeline: Pipeline, onnx_path: str, X_test: np.ndarray, tolerance: float = 1e-5
) -> bool:
    """
    ONNXモデルの予測がscikit-learnの予測と一致することを検証する。

    Args:
        pipeline: 元の学習済みscikit-learn Pipeline
        onnx_path: ONNXモデルファイルのパス
        X_test: 予測を検証するテストデータ
        tolerance: 数値差の許容誤差（分類では未使用）

    Returns:
        bool: 予測が一致すればTrue、そうでなければFalse
    """
    # scikit-learnの予測を取得
    sklearn_pred = pipeline.predict(X_test)

    # ONNXモデルをロードして予測を取得
    sess = rt.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    input_name = sess.get_inputs()[0].name
    label_name = sess.get_outputs()[0].name

    # ONNXはfloat32を期待
    X_test_float32 = X_test.astype(np.float32)
    onnx_pred = sess.run([label_name], {input_name: X_test_float32})[0]

    # 予測を比較
    return np.array_equal(sklearn_pred, onnx_pred)
