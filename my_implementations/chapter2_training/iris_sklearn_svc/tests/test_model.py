"""
Tests for model module
"""

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from iris_sklearn_svc.model import build_pipeline


class TestBuildPipeline:
    """Tests for build_pipeline function"""

    def test_build_pipeline_returns_pipeline(self):
        """パイプラインオブジェクトが返されることを確認"""
        pipeline = build_pipeline()

        assert isinstance(pipeline, Pipeline)

    def test_pipeline_has_two_steps(self):
        """パイプラインが2つのステップを持つことを確認"""
        pipeline = build_pipeline()

        # パイプラインのステップ数は2（scaler + classifier）
        assert len(pipeline.steps) == 2

    def test_first_step_is_scaler(self):
        """最初のステップがStandardScalerであることを確認"""
        pipeline = build_pipeline()

        # 最初のステップの名前と型を確認
        step_name, step_transformer = pipeline.steps[0]
        assert step_name == "scaler"
        assert isinstance(step_transformer, StandardScaler)

    def test_second_step_is_svc(self):
        """2番目のステップがSVCであることを確認"""
        pipeline = build_pipeline()

        # 2番目のステップの名前と型を確認
        step_name, step_estimator = pipeline.steps[1]
        assert step_name == "svc"
        assert isinstance(step_estimator, SVC)

    def test_svc_has_probability_enabled(self):
        """SVCのprobabilityがTrueに設定されていることを確認"""
        pipeline = build_pipeline()

        # SVCのprobabilityパラメータを確認
        svc = pipeline.named_steps["svc"]
        assert svc.probability is True

    def test_svc_has_rbf_kernel(self):
        """SVCがRBFカーネルを使用していることを確認"""
        pipeline = build_pipeline()

        svc = pipeline.named_steps["svc"]
        assert svc.kernel == "rbf"

    def test_pipeline_has_random_state(self):
        """SVCにrandom_stateが設定されていることを確認（再現性）"""
        pipeline = build_pipeline()

        svc = pipeline.named_steps["svc"]
        assert svc.random_state is not None
        assert isinstance(svc.random_state, int)

    def test_pipeline_reproducibility(self):
        """同じパイプラインが複数回生成できることを確認"""
        pipeline1 = build_pipeline()
        pipeline2 = build_pipeline()

        # 両方ともPipelineオブジェクトである
        assert isinstance(pipeline1, Pipeline)
        assert isinstance(pipeline2, Pipeline)

        # ステップ構成が同じ
        assert len(pipeline1.steps) == len(pipeline2.steps)
        assert pipeline1.steps[0][0] == pipeline2.steps[0][0]
        assert pipeline1.steps[1][0] == pipeline2.steps[1][0]
