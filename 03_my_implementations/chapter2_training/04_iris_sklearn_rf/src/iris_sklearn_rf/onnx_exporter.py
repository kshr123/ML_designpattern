"""
ONNX export and validation module.

This module provides functions to export scikit-learn models to ONNX format
and validate the exported models.
"""

import numpy as np
import onnxruntime as rt
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.pipeline import Pipeline


def export_to_onnx(pipeline: Pipeline, onnx_path: str) -> None:
    """
    Export a scikit-learn pipeline to ONNX format.

    Args:
        pipeline: Fitted scikit-learn Pipeline
        onnx_path: Path where to save the ONNX model

    Raises:
        Exception: If the model is not fitted or conversion fails
    """
    # Define input type (4 features for Iris dataset)
    initial_type = [("float_input", FloatTensorType([None, 4]))]

    # Convert to ONNX
    onnx_model = convert_sklearn(pipeline, initial_types=initial_type)

    # Save to file
    with open(onnx_path, "wb") as f:
        f.write(onnx_model.SerializeToString())


def validate_onnx_model(
    pipeline: Pipeline, onnx_path: str, X_test: np.ndarray, tolerance: float = 1e-5
) -> bool:
    """
    Validate that ONNX model predictions match scikit-learn predictions.

    Args:
        pipeline: Original fitted scikit-learn Pipeline
        onnx_path: Path to the ONNX model file
        X_test: Test data to validate predictions
        tolerance: Tolerance for numerical differences (not used for classification)

    Returns:
        bool: True if predictions match, False otherwise
    """
    # Get sklearn predictions
    sklearn_pred = pipeline.predict(X_test)

    # Load ONNX model and get predictions
    sess = rt.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    input_name = sess.get_inputs()[0].name
    label_name = sess.get_outputs()[0].name

    # ONNX expects float32
    X_test_float32 = X_test.astype(np.float32)
    onnx_pred = sess.run([label_name], {input_name: X_test_float32})[0]

    # Compare predictions
    return np.array_equal(sklearn_pred, onnx_pred)
