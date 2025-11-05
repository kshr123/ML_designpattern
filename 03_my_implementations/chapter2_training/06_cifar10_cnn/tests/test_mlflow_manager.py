"""
MLflowマネージャーモジュールのテスト。

MLflowを使った実験管理機能をテストします。
"""

import tempfile

import mlflow
import pytest
import torch.nn as nn

from cifar10_cnn.mlflow_manager import log_metrics, log_model, log_params
from cifar10_cnn.model import SimpleCNN


@pytest.fixture
def model() -> nn.Module:
    """テスト用のモデルを作成する。"""
    return SimpleCNN()


@pytest.fixture
def mlflow_tracking_uri() -> str:
    """一時的なMLflow tracking URIを作成する。"""
    temp_dir = tempfile.mkdtemp()
    tracking_uri = f"file://{temp_dir}/mlruns"
    mlflow.set_tracking_uri(tracking_uri)
    return tracking_uri


class TestLogParams:
    """log_params関数のテスト。"""

    def test_log_params_accepts_dict(self, mlflow_tracking_uri: str) -> None:
        """log_params関数が辞書を受け取ることを確認する。"""
        with mlflow.start_run():
            params = {"epochs": 5, "batch_size": 32, "learning_rate": 0.001}
            # エラーが発生しないことを確認
            log_params(params)

    def test_log_params_logs_to_mlflow(self, mlflow_tracking_uri: str) -> None:
        """log_params関数がMLflowにパラメータを記録することを確認する。"""
        with mlflow.start_run() as run:
            params = {"epochs": 5, "batch_size": 32}
            log_params(params)

            # MLflowから記録したパラメータを取得
            run_data = mlflow.get_run(run.info.run_id)
            logged_params = run_data.data.params

            assert "epochs" in logged_params
            assert logged_params["epochs"] == "5"
            assert "batch_size" in logged_params
            assert logged_params["batch_size"] == "32"

    def test_log_params_handles_various_types(self, mlflow_tracking_uri: str) -> None:
        """log_params関数が様々な型のパラメータを処理できることを確認する。"""
        with mlflow.start_run():
            params = {
                "int_param": 100,
                "float_param": 0.001,
                "str_param": "Adam",
                "bool_param": True,
            }
            # エラーが発生しないことを確認
            log_params(params)


class TestLogMetrics:
    """log_metrics関数のテスト。"""

    def test_log_metrics_accepts_dict(self, mlflow_tracking_uri: str) -> None:
        """log_metrics関数が辞書を受け取ることを確認する。"""
        with mlflow.start_run():
            metrics = {"test_loss": 0.5, "test_accuracy": 75.0}
            # エラーが発生しないことを確認
            log_metrics(metrics)

    def test_log_metrics_logs_to_mlflow(self, mlflow_tracking_uri: str) -> None:
        """log_metrics関数がMLflowにメトリクスを記録することを確認する。"""
        with mlflow.start_run() as run:
            metrics = {"test_loss": 0.5, "test_accuracy": 75.0}
            log_metrics(metrics)

            # MLflowから記録したメトリクスを取得
            run_data = mlflow.get_run(run.info.run_id)
            logged_metrics = run_data.data.metrics

            assert "test_loss" in logged_metrics
            assert logged_metrics["test_loss"] == 0.5
            assert "test_accuracy" in logged_metrics
            assert logged_metrics["test_accuracy"] == 75.0

    def test_log_metrics_accepts_float_values(self, mlflow_tracking_uri: str) -> None:
        """log_metrics関数が浮動小数点数の値を受け取ることを確認する。"""
        with mlflow.start_run():
            metrics = {"accuracy": 0.85, "loss": 1.23}
            # エラーが発生しないことを確認
            log_metrics(metrics)


class TestLogModel:
    """log_model関数のテスト。"""

    def test_log_model_accepts_model(self, model: nn.Module, mlflow_tracking_uri: str) -> None:
        """log_model関数がモデルを受け取ることを確認する。"""
        with mlflow.start_run():
            # エラーが発生しないことを確認
            log_model(model, artifact_path="model")

    def test_log_model_logs_to_mlflow(self, model: nn.Module, mlflow_tracking_uri: str) -> None:
        """log_model関数がMLflowにモデルを記録することを確認する。"""
        with mlflow.start_run() as run:
            log_model(model, artifact_path="model")

            # MLflowから記録したアーティファクトを取得
            client = mlflow.tracking.MlflowClient()
            artifacts = client.list_artifacts(run.info.run_id, path="model")

            # モデル関連のファイルが存在することを確認
            assert len(artifacts) > 0

    def test_log_model_with_custom_artifact_path(
        self, model: nn.Module, mlflow_tracking_uri: str
    ) -> None:
        """log_model関数がカスタムartifact_pathで動作することを確認する。"""
        with mlflow.start_run() as run:
            custom_path = "custom_model_path"
            log_model(model, artifact_path=custom_path)

            # MLflowから記録したアーティファクトを取得
            client = mlflow.tracking.MlflowClient()
            artifacts = client.list_artifacts(run.info.run_id, path=custom_path)

            # モデル関連のファイルが存在することを確認
            assert len(artifacts) > 0
