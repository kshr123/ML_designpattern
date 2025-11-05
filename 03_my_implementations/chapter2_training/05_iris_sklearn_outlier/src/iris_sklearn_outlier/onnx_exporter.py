"""
ONNXエクスポートと検証モジュール。

このモジュールはscikit-learnモデルをONNX形式にエクスポートし、
エクスポートされたモデルを検証する機能を提供します。
"""

import numpy as np
import onnxruntime as rt  # type: ignore[import-untyped]
from skl2onnx import convert_sklearn  # type: ignore[import-untyped]
from skl2onnx.common.data_types import FloatTensorType  # type: ignore[import-untyped]
from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]


def export_to_onnx(pipeline: Pipeline, onnx_path: str) -> None:
    """
    scikit-learnパイプラインをONNX形式にエクスポートする。

    Args:
        pipeline: 学習済みscikit-learn Pipeline
        onnx_path: ONNXモデルの保存先パス（.onnx拡張子）

    Raises:
        Exception: モデルが未学習の場合

    Examples:
        >>> from iris_sklearn_outlier.data_loader import load_iris_data
        >>> from iris_sklearn_outlier.model import create_ocs_pipeline
        >>> from iris_sklearn_outlier.trainer import train_model
        >>> import tempfile
        >>> import os
        >>> X = load_iris_data()
        >>> pipeline = create_ocs_pipeline()
        >>> fitted_pipeline = train_model(pipeline, X)
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     onnx_path = os.path.join(tmpdir, "model.onnx")
        ...     export_to_onnx(fitted_pipeline, onnx_path)
        ...     os.path.exists(onnx_path)
        True

    Notes:
        - 入力: FloatTensorType([None, 4]) - バッチサイズ可変、4特徴量
        - 出力: label（予測クラス）とscore（決定関数値）
        - ONNXモデルは異なるフレームワーク間での相互運用に便利
    """
    # Iris データは4つの特徴量を持つ
    # None はバッチサイズが可変であることを示す
    initial_type = [("float_input", FloatTensorType([None, 4]))]

    # scikit-learnモデルをONNX形式に変換
    onnx_model = convert_sklearn(pipeline, initial_types=initial_type)

    # ONNX形式でファイルに保存
    with open(onnx_path, "wb") as f:
        f.write(onnx_model.SerializeToString())


def validate_onnx_model(
    pipeline: Pipeline,
    onnx_path: str,
    X_test: np.ndarray,
) -> bool:
    """
    ONNXモデルとscikit-learnモデルの予測結果が一致することを検証する。

    Args:
        pipeline: 学習済みscikit-learn Pipeline
        onnx_path: ONNXモデルのパス
        X_test: テスト用特徴量行列 (n_samples, 4)

    Returns:
        bool: 全サンプルで予測が一致すればTrue、そうでなければFalse

    Examples:
        >>> from iris_sklearn_outlier.data_loader import load_iris_data
        >>> from iris_sklearn_outlier.model import create_ocs_pipeline
        >>> from iris_sklearn_outlier.trainer import train_model
        >>> import tempfile
        >>> import os
        >>> X = load_iris_data()
        >>> pipeline = create_ocs_pipeline()
        >>> fitted_pipeline = train_model(pipeline, X)
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     onnx_path = os.path.join(tmpdir, "model.onnx")
        ...     export_to_onnx(fitted_pipeline, onnx_path)
        ...     is_valid = validate_onnx_model(fitted_pipeline, onnx_path, X[:5])
        ...     is_valid
        True

    Notes:
        - ONNXRuntimeを使用してONNXモデルで推論
        - label出力を比較（+1 or -1）
        - 浮動小数点誤差は許容しない（厳密な一致を要求）
    """
    # scikit-learnモデルでの予測
    sklearn_predictions = pipeline.predict(X_test)

    # ONNXモデルのロードと推論
    session = rt.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])

    # ONNX推論の実行
    # 入力名は "float_input"、出力名は "label"
    input_name = session.get_inputs()[0].name
    label_name = session.get_outputs()[0].name

    onnx_predictions = session.run([label_name], {input_name: X_test.astype(np.float32)})[0]

    # ONNXの出力は (n, 1) の形状なので、flattenして (n,) にする
    onnx_predictions = onnx_predictions.flatten()

    # 予測結果の比較
    return np.array_equal(sklearn_predictions, onnx_predictions)
