"""
onnx_exporterモジュールのユニットテスト。

ONNXモデルのエクスポートと検証機能をテストします。
"""

import os
import tempfile

import pytest

from iris_sklearn_outlier.data_loader import load_iris_data
from iris_sklearn_outlier.model import create_ocs_pipeline
from iris_sklearn_outlier.onnx_exporter import export_to_onnx, validate_onnx_model
from iris_sklearn_outlier.trainer import train_model


class TestExportToONNX:
    """Test cases for export_to_onnx function."""

    def test_export_to_onnx_creates_file(self) -> None:
        """Test that export_to_onnx creates an ONNX file."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            assert os.path.exists(onnx_path), "ONNX file should be created"

    def test_export_to_onnx_file_not_empty(self) -> None:
        """Test that exported ONNX file is not empty."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            file_size = os.path.getsize(onnx_path)
            assert file_size > 0, "ONNX file should not be empty"
            assert file_size > 1000, "ONNX file should have reasonable size (>1KB)"

    def test_export_to_onnx_with_custom_path(self) -> None:
        """Test that export_to_onnx works with custom file path."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        with tempfile.TemporaryDirectory() as tmpdir:
            custom_name = "one_class_svm_iris.onnx"
            onnx_path = os.path.join(tmpdir, custom_name)
            export_to_onnx(fitted_pipeline, onnx_path)

            assert os.path.exists(onnx_path), "ONNX file with custom name should be created"
            assert os.path.basename(onnx_path) == custom_name, "File should have custom name"

    def test_export_to_onnx_requires_fitted_model(self) -> None:
        """Test that export_to_onnx raises error for unfitted model."""
        pipeline = create_ocs_pipeline()  # Not fitted

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")

            # Should raise an error because model is not fitted
            with pytest.raises(Exception):  # Will be sklearn's NotFittedError or similar
                export_to_onnx(pipeline, onnx_path)


class TestValidateONNXModel:
    """Test cases for validate_onnx_model function."""

    def test_validate_onnx_model_predictions_match(self) -> None:
        """Test that ONNX model predictions match sklearn predictions."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            # Test on a few samples
            X_sample = X[:5]
            is_valid = validate_onnx_model(fitted_pipeline, onnx_path, X_sample)

            assert is_valid, "ONNX predictions should match sklearn predictions"

    def test_validate_onnx_model_with_full_dataset(self) -> None:
        """Test ONNX validation with full Iris dataset."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            is_valid = validate_onnx_model(fitted_pipeline, onnx_path, X)

            assert is_valid, "ONNX should match sklearn on full dataset"

    def test_validate_onnx_model_with_single_sample(self) -> None:
        """Test ONNX validation with a single sample."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            X_single = X[:1]  # Single sample
            is_valid = validate_onnx_model(fitted_pipeline, onnx_path, X_single)

            assert is_valid, "ONNX should work with single sample"

    def test_validate_onnx_model_handles_different_nu(self) -> None:
        """Test ONNX validation with models trained with different nu values."""
        X = load_iris_data()

        # Train model with different nu
        pipeline = create_ocs_pipeline(nu=0.15)
        fitted_pipeline = train_model(pipeline, X)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            X_sample = X[:10]
            is_valid = validate_onnx_model(fitted_pipeline, onnx_path, X_sample)

            assert is_valid, "ONNX should work with different nu parameters"

    def test_validate_onnx_model_returns_boolean(self) -> None:
        """Test that validate_onnx_model returns a boolean."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            result = validate_onnx_model(fitted_pipeline, onnx_path, X[:5])

            assert isinstance(result, bool), "Should return a boolean value"
