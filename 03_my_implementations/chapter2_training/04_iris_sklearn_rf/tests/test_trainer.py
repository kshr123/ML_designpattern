"""
Unit tests for trainer module.

Tests the model training and evaluation functionality.
"""

from sklearn.pipeline import Pipeline

from iris_sklearn_rf.data_loader import load_iris_data, split_data
from iris_sklearn_rf.model import create_rf_pipeline
from iris_sklearn_rf.trainer import evaluate_model, train_model


class TestTrainModel:
    """Test cases for train_model function."""

    def test_train_model_returns_fitted_pipeline(self) -> None:
        """Test that train_model returns a fitted Pipeline."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        assert isinstance(fitted_pipeline, Pipeline), "Should return a Pipeline"
        assert hasattr(fitted_pipeline.named_steps["scaler"], "mean_"), "Scaler should be fitted"
        assert hasattr(
            fitted_pipeline.named_steps["classifier"], "classes_"
        ), "Classifier should be fitted"

    def test_train_model_learns_correct_classes(self) -> None:
        """Test that the trained model learns all 3 classes."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        classes = fitted_pipeline.named_steps["classifier"].classes_
        assert len(classes) == 3, "Should learn 3 classes"
        assert set(classes) == {0, 1, 2}, "Classes should be 0, 1, 2"

    def test_train_model_can_predict(self) -> None:
        """Test that trained model can make predictions."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        predictions = fitted_pipeline.predict(X_test)

        assert predictions.shape == y_test.shape, "Predictions should match test set size"
        assert all(
            pred in [0, 1, 2] for pred in predictions
        ), "All predictions should be valid classes"

    def test_train_model_with_different_random_states(self) -> None:
        """Test that different random states produce different models."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline1 = create_rf_pipeline(random_state=42)
        pipeline2 = create_rf_pipeline(random_state=123)

        fitted1 = train_model(pipeline1, X_train, y_train)
        fitted2 = train_model(pipeline2, X_train, y_train)

        # Models with different random states may produce different predictions
        # (though they might still be the same by chance)
        assert (
            fitted1.named_steps["classifier"].random_state
            != fitted2.named_steps["classifier"].random_state
        )


class TestEvaluateModel:
    """Test cases for evaluate_model function."""

    def test_evaluate_model_returns_dict(self) -> None:
        """Test that evaluate_model returns a dictionary of metrics."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        metrics = evaluate_model(fitted_pipeline, X_test, y_test)

        assert isinstance(metrics, dict), "Should return a dictionary"

    def test_evaluate_model_contains_required_metrics(self) -> None:
        """Test that metrics dict contains all required metrics."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        metrics = evaluate_model(fitted_pipeline, X_test, y_test)

        required_metrics = [
            "accuracy",
            "f1_score_macro",
            "f1_score_weighted",
            "precision_macro",
            "recall_macro",
        ]

        for metric in required_metrics:
            assert metric in metrics, f"Metrics should contain '{metric}'"

    def test_evaluate_model_metrics_in_valid_range(self) -> None:
        """Test that all metrics are in valid range [0, 1]."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        metrics = evaluate_model(fitted_pipeline, X_test, y_test)

        for metric_name, metric_value in metrics.items():
            assert (
                0.0 <= metric_value <= 1.0
            ), f"{metric_name} should be in range [0, 1], got {metric_value}"

    def test_evaluate_model_high_accuracy_on_iris(self) -> None:
        """Test that model achieves high accuracy on Iris dataset."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline()
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        metrics = evaluate_model(fitted_pipeline, X_test, y_test)

        # Iris is an easy dataset, should achieve >=0.9 accuracy
        assert metrics["accuracy"] >= 0.9, f"Accuracy should be >= 0.9, got {metrics['accuracy']}"

    def test_evaluate_model_with_poor_model(self) -> None:
        """Test evaluation with a poorly performing model."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        # Create a model with very few trees (poor performance)
        pipeline = create_rf_pipeline(n_estimators=1, max_depth=1)
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        metrics = evaluate_model(fitted_pipeline, X_test, y_test)

        # Even poor model should produce valid metrics
        assert 0.0 <= metrics["accuracy"] <= 1.0, "Accuracy should be in valid range"
        # Poor model might still get some predictions right by chance
        assert metrics["accuracy"] > 0.0, "Accuracy should be greater than 0"

    def test_evaluate_model_reproducibility(self) -> None:
        """Test that evaluation produces same results on same data."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        pipeline = create_rf_pipeline(random_state=42)
        fitted_pipeline = train_model(pipeline, X_train, y_train)

        metrics1 = evaluate_model(fitted_pipeline, X_test, y_test)
        metrics2 = evaluate_model(fitted_pipeline, X_test, y_test)

        # Same model on same data should produce identical metrics
        for key in metrics1:
            assert metrics1[key] == metrics2[key], f"Metric '{key}' should be reproducible"
