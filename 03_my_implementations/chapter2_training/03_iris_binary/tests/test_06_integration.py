"""統合テスト（E2E）"""

import os
import tempfile

import mlflow
import numpy as np
import onnxruntime as rt
import pytest

from iris_binary.data_loader import IrisTarget, load_and_transform_data
from iris_binary.exporter import export_to_onnx
from iris_binary.mlflow_manager import log_experiment
from iris_binary.model import build_svc_pipeline
from iris_binary.trainer import evaluate_model, train_model


class TestIntegration:
    """統合テスト（E2E）"""

    @pytest.fixture
    def mlflow_test_env(self):
        """テスト用MLflow環境"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracking_uri = f"file://{tmpdir}/mlruns"
            mlflow.set_tracking_uri(tracking_uri)

            experiment_name = "test_integration"
            mlflow.set_experiment(experiment_name)

            yield tracking_uri

    def test_e2e_pipeline_setosa(self, mlflow_test_env):
        """E2Eパイプライン（setosa）"""
        # 1. データ読み込み
        X_train, X_test, y_train, y_test = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.SETOSA, random_state=42
        )

        # 2. モデル構築
        model = build_svc_pipeline()

        # 3. 学習
        train_model(model, X_train, y_train)

        # 4. 評価
        metrics = evaluate_model(model, X_test, y_test)
        assert metrics["accuracy"] > 0.90

        # 5. ONNX変換
        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(model, onnx_path)
            assert os.path.exists(onnx_path)

            # 6. ONNX推論検証
            sess = rt.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
            input_name = sess.get_inputs()[0].name
            label_name = sess.get_outputs()[0].name

            sklearn_pred = model.predict(X_test[:10])
            onnx_pred = sess.run([label_name], {input_name: X_test[:10]})[0]
            np.testing.assert_array_equal(sklearn_pred, onnx_pred)

            # 7. MLflow記録
            with mlflow.start_run():
                run_id = log_experiment(
                    model=model,
                    metrics=metrics,
                    target_iris=IrisTarget.SETOSA,
                    onnx_path=onnx_path,
                )
                assert run_id is not None

    def test_e2e_pipeline_versicolor(self, mlflow_test_env):
        """E2Eパイプライン（versicolor）"""
        X_train, X_test, y_train, y_test = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.VERSICOLOR, random_state=42
        )

        model = build_svc_pipeline()
        train_model(model, X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test)

        # versicolorは分離が難しいため、精度は低め
        assert metrics["accuracy"] > 0.70

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(model, onnx_path)

            with mlflow.start_run():
                run_id = log_experiment(
                    model=model,
                    metrics=metrics,
                    target_iris=IrisTarget.VERSICOLOR,
                    onnx_path=onnx_path,
                )
                assert run_id is not None

    def test_e2e_pipeline_virginica(self, mlflow_test_env):
        """E2Eパイプライン（virginica）"""
        X_train, X_test, y_train, y_test = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.VIRGINICA, random_state=42
        )

        model = build_svc_pipeline()
        train_model(model, X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test)

        assert metrics["accuracy"] > 0.70

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(model, onnx_path)

            with mlflow.start_run():
                run_id = log_experiment(
                    model=model,
                    metrics=metrics,
                    target_iris=IrisTarget.VIRGINICA,
                    onnx_path=onnx_path,
                )
                assert run_id is not None

    def test_compare_targets(self, mlflow_test_env):
        """3種類のtarget_irisで比較"""
        results = {}

        for target in [IrisTarget.SETOSA, IrisTarget.VERSICOLOR, IrisTarget.VIRGINICA]:
            X_train, X_test, y_train, y_test = load_and_transform_data(
                test_size=0.3, target_iris=target, random_state=42
            )

            model = build_svc_pipeline()
            train_model(model, X_train, y_train)
            metrics = evaluate_model(model, X_test, y_test)

            results[target.name] = metrics

        # setosaが最も高精度
        assert results["SETOSA"]["accuracy"] >= results["VERSICOLOR"]["accuracy"]
        assert results["SETOSA"]["accuracy"] >= results["VIRGINICA"]["accuracy"]

        # 全てのターゲットで学習が成功
        for target, metrics in results.items():
            assert metrics["accuracy"] > 0.70, f"{target} accuracy is too low"

    def test_mlflow_experiment_tracking(self, mlflow_test_env):
        """MLflowで複数実験を追跡できる"""
        experiment_name = "multi_run_test"
        mlflow.set_experiment(experiment_name)

        run_ids = []

        # 3回実行
        for target in [IrisTarget.SETOSA, IrisTarget.VERSICOLOR, IrisTarget.VIRGINICA]:
            X_train, X_test, y_train, y_test = load_and_transform_data(
                test_size=0.3, target_iris=target, random_state=42
            )

            model = build_svc_pipeline()
            train_model(model, X_train, y_train)
            metrics = evaluate_model(model, X_test, y_test)

            with mlflow.start_run():
                run_id = log_experiment(
                    model=model, metrics=metrics, target_iris=target, onnx_path=None
                )
                run_ids.append(run_id)

        # 3つのRunが記録される
        assert len(run_ids) == 3
        assert len(set(run_ids)) == 3  # すべて異なるRun ID

        # 実験データを取得
        experiment = mlflow.get_experiment_by_name(experiment_name)
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])

        assert len(runs) == 3
