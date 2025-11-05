"""
trainerモジュールのユニットテスト。

モデルの学習と外れ値率の評価機能をテストします。
"""

from sklearn.pipeline import Pipeline

from iris_sklearn_outlier.data_loader import load_iris_data
from iris_sklearn_outlier.model import create_ocs_pipeline
from iris_sklearn_outlier.trainer import evaluate_model, train_model


class TestTrainModel:
    """Test cases for train_model function."""

    def test_train_model_returns_fitted_pipeline(self) -> None:
        """Test that train_model returns a fitted Pipeline."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        assert isinstance(fitted_pipeline, Pipeline), "Should return a Pipeline"
        assert hasattr(fitted_pipeline.named_steps["scaler"], "mean_"), "Scaler should be fitted"
        assert hasattr(fitted_pipeline.named_steps["ocs"], "support_"), "OCS should be fitted"

    def test_train_model_has_support_vectors(self) -> None:
        """Test that trained model has support vectors."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        n_support = len(fitted_pipeline.named_steps["ocs"].support_)
        assert n_support > 0, "Model should have support vectors"

    def test_train_model_can_predict(self) -> None:
        """Test that trained model can make predictions."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        predictions = fitted_pipeline.predict(X)

        assert predictions.shape == (150,), "Should predict for all 150 samples"
        assert all(pred in [1, -1] for pred in predictions), "Predictions should be 1 or -1"

    def test_train_model_decision_function(self) -> None:
        """Test that trained model can compute decision function."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        scores = fitted_pipeline.decision_function(X)

        assert scores.shape == (150,), "Should compute scores for all 150 samples"
        assert scores.dtype.kind == "f", "Scores should be floating point"


class TestEvaluateModel:
    """Test cases for evaluate_model function."""

    def test_evaluate_model_returns_float(self) -> None:
        """Test that evaluate_model returns a float value."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        outlier_rate = evaluate_model(fitted_pipeline, X)

        assert isinstance(outlier_rate, float), "Should return a float"

    def test_evaluate_model_in_valid_range(self) -> None:
        """Test that outlier_rate is in valid range [0, 1]."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        outlier_rate = evaluate_model(fitted_pipeline, X)

        assert 0.0 <= outlier_rate <= 1.0, f"Outlier rate should be in [0, 1], got {outlier_rate}"

    def test_evaluate_model_reasonable_outlier_rate(self) -> None:
        """Test that outlier_rate is reasonable for default nu=0.1."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline(nu=0.1)
        fitted_pipeline = train_model(pipeline, X)

        outlier_rate = evaluate_model(fitted_pipeline, X)

        # With nu=0.1, expect roughly 10% outliers (within margin)
        assert 0.0 <= outlier_rate <= 0.2, f"Outlier rate should be ~0.1, got {outlier_rate}"

    def test_evaluate_model_with_different_nu(self) -> None:
        """Test that higher nu leads to higher outlier rate."""
        X = load_iris_data()

        # Low nu
        pipeline_low = create_ocs_pipeline(nu=0.05)
        fitted_low = train_model(pipeline_low, X)
        outlier_rate_low = evaluate_model(fitted_low, X)

        # High nu
        pipeline_high = create_ocs_pipeline(nu=0.2)
        fitted_high = train_model(pipeline_high, X)
        outlier_rate_high = evaluate_model(fitted_high, X)

        # Higher nu should generally lead to higher outlier rate
        assert (
            outlier_rate_low <= outlier_rate_high + 0.05
        ), "Higher nu should increase outlier rate"

    def test_evaluate_model_reproducibility(self) -> None:
        """Test that evaluation produces same results on same data."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        outlier_rate1 = evaluate_model(fitted_pipeline, X)
        outlier_rate2 = evaluate_model(fitted_pipeline, X)

        assert outlier_rate1 == outlier_rate2, "Outlier rate should be reproducible"

    def test_evaluate_model_counts_outliers(self) -> None:
        """Test that outlier_rate correctly counts outliers."""
        X = load_iris_data()

        pipeline = create_ocs_pipeline()
        fitted_pipeline = train_model(pipeline, X)

        predictions = fitted_pipeline.predict(X)
        n_outliers = sum(1 for pred in predictions if pred == -1)
        expected_rate = n_outliers / len(X)

        actual_rate = evaluate_model(fitted_pipeline, X)

        assert abs(actual_rate - expected_rate) < 1e-6, "Outlier rate should match manual count"
