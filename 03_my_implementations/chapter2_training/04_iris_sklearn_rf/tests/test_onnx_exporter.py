"""
onnx_exporterモジュールのユニットテスト。

ONNXモデルのエクスポートと検証機能をテストします。
"""

import os
import tempfile

import pytest

from iris_sklearn_rf.data_loader import load_iris_data, split_data
from iris_sklearn_rf.model import create_rf_pipeline
from iris_sklearn_rf.onnx_exporter import export_to_onnx, validate_onnx_model
from iris_sklearn_rf.trainer import train_model


class TestExportToONNX:
    """Test cases for export_to_onnx function."""

    def test_export_to_onnx_creates_file(self) -> None:
        """Test that export_to_onnx creates an ONNX file."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            assert os.path.exists(onnx_path), "ONNX file should be created"

    def test_export_to_onnx_file_not_empty(self) -> None:
        """Test that exported ONNX file is not empty."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            file_size = os.path.getsize(onnx_path)
            assert file_size > 0, "ONNX file should not be empty"
            assert file_size > 1000, "ONNX file should have reasonable size (>1KB)"

    def test_export_to_onnx_with_custom_path(self) -> None:
        """Test that export_to_onnx works with custom file path."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        with tempfile.TemporaryDirectory() as tmpdir:
            custom_name = "random_forest_iris.onnx"
            onnx_path = os.path.join(tmpdir, custom_name)
            export_to_onnx(fitted_pipeline, onnx_path)

            assert os.path.exists(onnx_path), "ONNX file with custom name should be created"
            assert os.path.basename(onnx_path) == custom_name, "File should have custom name"

    def test_export_to_onnx_requires_fitted_model(self) -> None:
        """Test that export_to_onnx raises error for unfitted model."""
        pipeline = create_rf_pipeline()  # Not fitted

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")

            # Should raise an error because model is not fitted
            with pytest.raises(Exception):  # Will be sklearn's NotFittedError or similar
                export_to_onnx(pipeline, onnx_path)


class TestValidateONNXModel:
    """Test cases for validate_onnx_model function."""

    def test_validate_onnx_model_predictions_match(self) -> None:
        """Test that ONNX model predictions match sklearn predictions."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            # Test on a few samples
            X_sample = X_test[:5]
            is_valid = validate_onnx_model(fitted_pipeline, onnx_path, X_sample)

            assert is_valid, "ONNX predictions should match sklearn predictions"

    def test_validate_onnx_model_with_full_test_set(self) -> None:
        """Test ONNX validation with full test set."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            is_valid = validate_onnx_model(fitted_pipeline, onnx_path, X_test)

            assert is_valid, "ONNX should match sklearn on full test set"

    def test_validate_onnx_model_with_single_sample(self) -> None:
        """Test ONNX validation with a single sample."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            X_single = X_test[:1]  # Single sample
            is_valid = validate_onnx_model(fitted_pipeline, onnx_path, X_single)

            assert is_valid, "ONNX should work with single sample"

    def test_validate_onnx_model_handles_different_models(self) -> None:
        """Test ONNX validation with models trained with different parameters."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        # Train model with different parameters
        pipeline = create_rf_pipeline(n_estimators=50, max_depth=5)
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            X_sample = X_test[:10]
            is_valid = validate_onnx_model(fitted_pipeline, onnx_path, X_sample)

            assert is_valid, "ONNX should work with different model parameters"

    def test_validate_onnx_model_returns_boolean(self) -> None:
        """Test that validate_onnx_model returns a boolean."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(fitted_pipeline, onnx_path)

            result = validate_onnx_model(fitted_pipeline, onnx_path, X_test[:5])

            assert isinstance(result, bool), "Should return a boolean value"
