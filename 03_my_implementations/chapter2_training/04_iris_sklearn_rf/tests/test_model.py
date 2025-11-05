"""
modelモジュールのユニットテスト。

モデルパイプラインの構築と設定をテストします。
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from iris_sklearn_rf.model import create_rf_pipeline


class TestCreateRFPipeline:
    """Test cases for create_rf_pipeline function."""

    def test_create_rf_pipeline_returns_pipeline(self) -> None:
        """Test that create_rf_pipeline returns a Pipeline object."""
        pipeline = create_rf_pipeline()

        assert isinstance(pipeline, Pipeline), "Should return a Pipeline object"

    def test_create_rf_pipeline_has_correct_steps(self) -> None:
        """Test that pipeline has correct steps (scaler and classifier)."""
        pipeline = create_rf_pipeline()

        assert len(pipeline.steps) == 2, "Pipeline should have 2 steps"

        # Check step names
        step_names = [name for name, _ in pipeline.steps]
        assert "scaler" in step_names, "Pipeline should have 'scaler' step"
        assert "classifier" in step_names, "Pipeline should have 'classifier' step"

    def test_create_rf_pipeline_scaler_type(self) -> None:
        """Test that the scaler step uses StandardScaler."""
        pipeline = create_rf_pipeline()

        scaler = pipeline.named_steps["scaler"]
        assert isinstance(scaler, StandardScaler), "Scaler step should be StandardScaler"

    def test_create_rf_pipeline_classifier_type(self) -> None:
        """Test that the classifier step uses RandomForestClassifier."""
        pipeline = create_rf_pipeline()

        classifier = pipeline.named_steps["classifier"]
        assert isinstance(
            classifier, RandomForestClassifier
        ), "Classifier should be RandomForestClassifier"

    def test_create_rf_pipeline_default_parameters(self) -> None:
        """Test that RandomForestClassifier has correct default parameters."""
        pipeline = create_rf_pipeline()

        classifier = pipeline.named_steps["classifier"]

        assert classifier.n_estimators == 100, "Default n_estimators should be 100"
        assert classifier.random_state == 42, "Default random_state should be 42"

    def test_create_rf_pipeline_custom_parameters(self) -> None:
        """Test that custom parameters are correctly set."""
        pipeline = create_rf_pipeline(
            n_estimators=200, max_depth=10, min_samples_split=5, random_state=123
        )

        classifier = pipeline.named_steps["classifier"]

        assert classifier.n_estimators == 200, "n_estimators should be 200"
        assert classifier.max_depth == 10, "max_depth should be 10"
        assert classifier.min_samples_split == 5, "min_samples_split should be 5"
        assert classifier.random_state == 123, "random_state should be 123"

    def test_create_rf_pipeline_max_depth_none(self) -> None:
        """Test that max_depth can be None (unlimited depth)."""
        pipeline = create_rf_pipeline(max_depth=None)

        classifier = pipeline.named_steps["classifier"]
        assert classifier.max_depth is None, "max_depth should be None"

    def test_create_rf_pipeline_can_fit(self) -> None:
        """Test that the pipeline can be fitted with sample data."""
        import numpy as np

        pipeline = create_rf_pipeline()

        # Create simple test data
        X = np.array([[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6], [4, 5, 6, 7]])
        y = np.array([0, 1, 2, 0])

        # Should not raise an exception
        pipeline.fit(X, y)

        # Check that pipeline is fitted
        assert hasattr(pipeline.named_steps["scaler"], "mean_"), "Scaler should be fitted"
        assert hasattr(
            pipeline.named_steps["classifier"], "classes_"
        ), "Classifier should be fitted"

    def test_create_rf_pipeline_can_predict(self) -> None:
        """Test that the fitted pipeline can make predictions."""
        import numpy as np

        pipeline = create_rf_pipeline()

        # Create simple test data
        X_train = np.array([[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6], [4, 5, 6, 7]])
        y_train = np.array([0, 1, 2, 0])
        X_test = np.array([[1.5, 2.5, 3.5, 4.5]])

        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)

        assert predictions.shape == (1,), "Should predict for 1 sample"
        assert predictions[0] in [0, 1, 2], "Prediction should be one of the classes"
