"""
modelモジュールのユニットテスト。

One-Class SVMモデルパイプラインの構築と設定をテストします。
"""

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

from iris_sklearn_outlier.model import create_ocs_pipeline


class TestCreateOCSPipeline:
    """Test cases for create_ocs_pipeline function."""

    def test_create_ocs_pipeline_returns_pipeline(self) -> None:
        """Test that create_ocs_pipeline returns a Pipeline object."""
        pipeline = create_ocs_pipeline()

        assert isinstance(pipeline, Pipeline), "Should return a Pipeline object"

    def test_create_ocs_pipeline_has_correct_steps(self) -> None:
        """Test that pipeline has correct steps (scaler and ocs)."""
        pipeline = create_ocs_pipeline()

        assert len(pipeline.steps) == 2, "Pipeline should have 2 steps"

        # Check step names
        step_names = [name for name, _ in pipeline.steps]
        assert "scaler" in step_names, "Pipeline should have 'scaler' step"
        assert "ocs" in step_names, "Pipeline should have 'ocs' step"

    def test_create_ocs_pipeline_scaler_type(self) -> None:
        """Test that the scaler step uses StandardScaler."""
        pipeline = create_ocs_pipeline()

        scaler = pipeline.named_steps["scaler"]
        assert isinstance(scaler, StandardScaler), "Scaler step should be StandardScaler"

    def test_create_ocs_pipeline_ocs_type(self) -> None:
        """Test that the ocs step uses OneClassSVM."""
        pipeline = create_ocs_pipeline()

        ocs = pipeline.named_steps["ocs"]
        assert isinstance(ocs, OneClassSVM), "OCS step should be OneClassSVM"

    def test_create_ocs_pipeline_default_parameters(self) -> None:
        """Test that OneClassSVM has correct default parameters."""
        pipeline = create_ocs_pipeline()

        ocs = pipeline.named_steps["ocs"]

        assert ocs.nu == 0.1, "Default nu should be 0.1"
        assert ocs.gamma == "auto", "Default gamma should be 'auto'"
        assert ocs.kernel == "rbf", "Default kernel should be 'rbf'"

    def test_create_ocs_pipeline_custom_nu(self) -> None:
        """Test that custom nu parameter is correctly set."""
        pipeline = create_ocs_pipeline(nu=0.2)

        ocs = pipeline.named_steps["ocs"]
        assert ocs.nu == 0.2, "nu should be 0.2"

    def test_create_ocs_pipeline_custom_gamma(self) -> None:
        """Test that custom gamma parameter is correctly set."""
        pipeline = create_ocs_pipeline(gamma=0.001)

        ocs = pipeline.named_steps["ocs"]
        assert ocs.gamma == 0.001, "gamma should be 0.001"

    def test_create_ocs_pipeline_custom_kernel(self) -> None:
        """Test that custom kernel parameter is correctly set."""
        pipeline = create_ocs_pipeline(kernel="linear")

        ocs = pipeline.named_steps["ocs"]
        assert ocs.kernel == "linear", "kernel should be 'linear'"

    def test_create_ocs_pipeline_can_fit(self) -> None:
        """Test that the pipeline can be fitted with sample data."""
        import numpy as np

        pipeline = create_ocs_pipeline()

        # Create simple test data (正常データのみ)
        X = np.array([[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6], [4, 5, 6, 7]], dtype=np.float32)

        # Should not raise an exception
        pipeline.fit(X)

        # Check that pipeline is fitted
        assert hasattr(pipeline.named_steps["scaler"], "mean_"), "Scaler should be fitted"
        assert hasattr(pipeline.named_steps["ocs"], "support_"), "OCS should be fitted"

    def test_create_ocs_pipeline_can_predict(self) -> None:
        """Test that the fitted pipeline can make predictions."""
        import numpy as np

        pipeline = create_ocs_pipeline()

        # Create simple test data
        X_train = np.array(
            [[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6], [4, 5, 6, 7]], dtype=np.float32
        )
        X_test = np.array([[1.5, 2.5, 3.5, 4.5]], dtype=np.float32)

        pipeline.fit(X_train)
        predictions = pipeline.predict(X_test)

        assert predictions.shape == (1,), "Should predict for 1 sample"
        assert predictions[0] in [1, -1], "Prediction should be 1 (inlier) or -1 (outlier)"
