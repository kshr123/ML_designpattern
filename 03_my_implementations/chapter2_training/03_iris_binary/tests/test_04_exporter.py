"""ONNX Exporter のユニットテスト"""

import os
import tempfile

import numpy as np
import onnxruntime as rt
import pytest

from iris_binary.data_loader import IrisTarget, load_and_transform_data
from iris_binary.exporter import export_to_onnx
from iris_binary.model import build_svc_pipeline
from iris_binary.trainer import train_model


class TestONNXExporter:
    """ONNX Exporter のテストクラス"""

    @pytest.fixture
    def trained_model(self):
        """学習済みモデル"""
        X_train, _, y_train, _ = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.SETOSA, random_state=42
        )
        model = build_svc_pipeline()
        train_model(model, X_train, y_train)
        return model

    @pytest.fixture
    def test_data(self):
        """テストデータ"""
        _, X_test, _, y_test = load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.SETOSA, random_state=42
        )
        return X_test, y_test

    def test_export_to_onnx(self, trained_model):
        """ONNXファイルが作成される"""
        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")

            export_to_onnx(trained_model, onnx_path)

            assert os.path.exists(onnx_path)
            assert os.path.getsize(onnx_path) > 0

    def test_onnx_loadable(self, trained_model):
        """ONNXファイルが読み込める"""
        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")

            export_to_onnx(trained_model, onnx_path)

            # onnxruntimeでロードできる
            sess = rt.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
            assert sess is not None

    def test_onnx_inference(self, trained_model, test_data):
        """ONNX推論が実行できる"""
        X_test, _ = test_data

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(trained_model, onnx_path)

            sess = rt.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
            input_name = sess.get_inputs()[0].name

            # 推論実行
            onnx_pred = sess.run(None, {input_name: X_test[:5]})

            assert onnx_pred is not None
            assert len(onnx_pred) > 0

    def test_sklearn_onnx_consistency(self, trained_model, test_data):
        """scikit-learnとONNXの予測結果が一致する"""
        X_test, _ = test_data

        # scikit-learn予測
        sklearn_pred = trained_model.predict(X_test[:10])

        # ONNX予測
        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(trained_model, onnx_path)

            sess = rt.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
            input_name = sess.get_inputs()[0].name
            label_name = sess.get_outputs()[0].name

            onnx_pred = sess.run([label_name], {input_name: X_test[:10]})[0]

        # 予測結果が一致する
        np.testing.assert_array_equal(sklearn_pred, onnx_pred)

    def test_onnx_probability_output(self, trained_model, test_data):
        """ONNX推論で確率出力が得られる"""
        X_test, _ = test_data

        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = os.path.join(tmpdir, "model.onnx")
            export_to_onnx(trained_model, onnx_path)

            sess = rt.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
            input_name = sess.get_inputs()[0].name

            # 確率出力
            outputs = sess.run(None, {input_name: X_test[:5]})

            # 2つの出力（ラベル + 確率）
            assert len(outputs) == 2

            probabilities = outputs[1]
            assert probabilities is not None
            assert len(probabilities) == 5

            # 確率が0〜1の範囲
            for prob_dict in probabilities:
                for prob in prob_dict.values():
                    assert 0.0 <= prob <= 1.0
