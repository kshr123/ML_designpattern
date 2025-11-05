"""MLflow Manager のユニットテスト"""

import os
import tempfile

import mlflow
import pytest

from iris_binary.data_loader import IrisTarget, load_and_transform_data
from iris_binary.mlflow_manager import log_experiment
from iris_binary.model import build_svc_pipeline
from iris_binary.trainer import evaluate_model, train_model


class TestMLflowManager:
    """MLflow Manager のテストクラス"""

    @pytest.fixture
    def mlflow_test_env(self):
        """テスト用MLflow環境"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracking_uri = f"file://{tmpdir}/mlruns"
            mlflow.set_tracking_uri(tracking_uri)

            # 実験作成
            experiment_name = "test_iris_binary"
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
            else:
                experiment_id = experiment.experiment_id

            mlflow.set_experiment(experiment_name)

            yield {
                "tracking_uri": tracking_uri,
                "experiment_id": experiment_id,
                "experiment_name": experiment_name,
            }

    @pytest.fixture
    def trained_model_and_metrics(self):
        """学習済みモデルと評価指標"""
        X_train, X_test, y_train, y_test = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.SETOSA, random_state=42
        )
        model = build_svc_pipeline()
        train_model(model, X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test)
        return model, metrics

    def test_log_experiment(self, mlflow_test_env, trained_model_and_metrics):
        """実験がMLflowに記録される"""
        model, metrics = trained_model_and_metrics

        with mlflow.start_run():
            run_id = log_experiment(
                model=model,
                metrics=metrics,
                target_iris=IrisTarget.SETOSA,
                onnx_path=None,  # ONNXはスキップ
            )

            assert run_id is not None
            assert len(run_id) > 0

    def test_log_parameters(self, mlflow_test_env, trained_model_and_metrics):
        """パラメータがログ記録される"""
        model, metrics = trained_model_and_metrics

        with mlflow.start_run() as run:
            log_experiment(
                model=model,
                metrics=metrics,
                target_iris=IrisTarget.SETOSA,
                onnx_path=None,
            )

            run_data = mlflow.get_run(run.info.run_id).data

            assert "normalize" in run_data.params
            assert run_data.params["normalize"] == "StandardScaler"

            assert "model" in run_data.params
            assert run_data.params["model"] == "svc"

            assert "target_iris" in run_data.params
            assert run_data.params["target_iris"] == "setosa"

    def test_log_metrics(self, mlflow_test_env, trained_model_and_metrics):
        """メトリクスがログ記録される"""
        model, metrics = trained_model_and_metrics

        with mlflow.start_run() as run:
            log_experiment(
                model=model,
                metrics=metrics,
                target_iris=IrisTarget.SETOSA,
                onnx_path=None,
            )

            run_data = mlflow.get_run(run.info.run_id).data

            assert "accuracy" in run_data.metrics
            assert "precision" in run_data.metrics
            assert "recall" in run_data.metrics

            # メトリクスの値が合理的
            assert 0.0 <= run_data.metrics["accuracy"] <= 1.0
            assert 0.0 <= run_data.metrics["precision"] <= 1.0
            assert 0.0 <= run_data.metrics["recall"] <= 1.0

    def test_log_model(self, mlflow_test_env, trained_model_and_metrics):
        """モデルがログ記録される（log_model呼び出しが成功する）"""
        model, metrics = trained_model_and_metrics

        with mlflow.start_run():
            run_id = log_experiment(
                model=model,
                metrics=metrics,
                target_iris=IrisTarget.SETOSA,
                onnx_path=None,
            )

        # run_idが返される
        assert run_id is not None
        assert len(run_id) > 0

        # Runデータが取得できる
        run_data = mlflow.get_run(run_id)
        assert run_data is not None

    def test_log_onnx_artifact(self, mlflow_test_env, trained_model_and_metrics):
        """ONNXファイルがartifactとして記録される"""
        model, metrics = trained_model_and_metrics

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")

            # ダミーONNXファイル作成
            with open(onnx_path, "wb") as f:
                f.write(b"dummy onnx content")

            with mlflow.start_run() as run:
                log_experiment(
                    model=model,
                    metrics=metrics,
                    target_iris=IrisTarget.SETOSA,
                    onnx_path=onnx_path,
                )

                # ONNXファイルがartifactとして保存される
                client = mlflow.tracking.MlflowClient()
                artifacts = client.list_artifacts(run.info.run_id)

                artifact_paths = [artifact.path for artifact in artifacts]
                onnx_artifacts = [p for p in artifact_paths if p.endswith(".onnx")]

                assert len(onnx_artifacts) > 0
