"""Model Builder のユニットテスト"""

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from iris_binary.model import build_svc_pipeline


class TestModelBuilder:
    """Model Builder のテストクラス"""

    def test_build_pipeline(self):
        """パイプラインが正しく構築される"""
        pipeline = build_svc_pipeline()

        assert isinstance(pipeline, Pipeline)
        assert len(pipeline.steps) == 2

    def test_pipeline_has_scaler(self):
        """StandardScalerが含まれる"""
        pipeline = build_svc_pipeline()

        step_names = [name for name, _ in pipeline.steps]
        assert "scaler" in step_names

        scaler = pipeline.named_steps["scaler"]
        assert isinstance(scaler, StandardScaler)

    def test_pipeline_has_svc(self):
        """SVCが含まれる"""
        pipeline = build_svc_pipeline()

        step_names = [name for name, _ in pipeline.steps]
        assert "svc" in step_names

        svc = pipeline.named_steps["svc"]
        assert isinstance(svc, SVC)

    def test_svc_has_probability(self):
        """SVCのprobabilityがTrueである"""
        pipeline = build_svc_pipeline()

        svc = pipeline.named_steps["svc"]
        assert svc.probability is True

    def test_pipeline_step_order(self):
        """パイプラインのステップ順序が正しい"""
        pipeline = build_svc_pipeline()

        step_names = [name for name, _ in pipeline.steps]
        assert step_names == ["scaler", "svc"]
