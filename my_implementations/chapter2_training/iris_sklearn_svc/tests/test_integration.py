"""
Integration tests for the complete ML pipeline

これらのテストは、全モジュールを連携させた動作を確認します。
- データ読み込み → モデル構築 → 学習 → 評価 → エクスポート の一連の流れ
- ONNXモデルの実際の推論動作
"""

import tempfile
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import pytest

from iris_sklearn_svc.data_loader import get_data
from iris_sklearn_svc.evaluator import evaluate_model
from iris_sklearn_svc.exporter import export_to_onnx
from iris_sklearn_svc.model import build_pipeline
from iris_sklearn_svc.trainer import train_model


class TestEndToEndPipeline:
    """エンドツーエンドのパイプラインテスト"""

    def test_complete_training_pipeline(self):
        """
        データ読み込みからモデルエクスポートまでの完全なパイプラインが
        エラーなく実行できることを確認
        """
        # 1. データ読み込み
        x_train, x_test, y_train, y_test = get_data(test_size=0.3, random_state=42)

        # 2. モデル構築
        pipeline = build_pipeline()

        # 3. モデル学習
        trained_model = train_model(pipeline, x_train, y_train)

        # 4. モデル評価
        metrics = evaluate_model(trained_model, x_test, y_test)

        # 5. モデルエクスポート
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_model.onnx"
            export_to_onnx(trained_model, str(output_path))

            # ファイルが作成されていることを確認
            assert output_path.exists()

        # メトリクスが妥当な範囲内であることを確認
        assert metrics["accuracy"] >= 0.8
        assert metrics["precision"] >= 0.8
        assert metrics["recall"] >= 0.8

    def test_pipeline_produces_consistent_results(self):
        """
        同じパラメータで実行した場合、一貫した結果が得られることを確認
        （再現性のテスト）
        """
        # 1回目の実行
        x_train_1, x_test_1, y_train_1, y_test_1 = get_data(test_size=0.3, random_state=42)
        pipeline_1 = build_pipeline()
        trained_model_1 = train_model(pipeline_1, x_train_1, y_train_1)
        metrics_1 = evaluate_model(trained_model_1, x_test_1, y_test_1)

        # 2回目の実行
        x_train_2, x_test_2, y_train_2, y_test_2 = get_data(test_size=0.3, random_state=42)
        pipeline_2 = build_pipeline()
        trained_model_2 = train_model(pipeline_2, x_train_2, y_train_2)
        metrics_2 = evaluate_model(trained_model_2, x_test_2, y_test_2)

        # メトリクスが完全に一致することを確認
        assert metrics_1["accuracy"] == metrics_2["accuracy"]
        assert metrics_1["precision"] == metrics_2["precision"]
        assert metrics_1["recall"] == metrics_2["recall"]

    def test_pipeline_with_different_random_states(self):
        """
        異なるrandom_stateで実行した場合、異なるデータ分割になることを確認
        """
        # random_state=42
        x_train_1, x_test_1, y_train_1, y_test_1 = get_data(test_size=0.3, random_state=42)

        # random_state=123
        x_train_2, x_test_2, y_train_2, y_test_2 = get_data(test_size=0.3, random_state=123)

        # データが異なることを確認（少なくとも1つの要素が異なる）
        assert not np.array_equal(x_train_1, x_train_2)


class TestONNXInference:
    """ONNXモデルの推論テスト"""

    @pytest.fixture
    def trained_pipeline_and_test_data(self):
        """学習済みパイプラインとテストデータを準備"""
        x_train, x_test, y_train, y_test = get_data(test_size=0.3, random_state=42)
        pipeline = build_pipeline()
        trained_model = train_model(pipeline, x_train, y_train)
        return trained_model, x_test, y_test

    @pytest.fixture
    def onnx_model_path(self, trained_pipeline_and_test_data):
        """ONNXモデルを一時ファイルに保存"""
        trained_model, _, _ = trained_pipeline_and_test_data
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_model.onnx"
            export_to_onnx(trained_model, str(output_path))
            yield str(output_path)

    def test_onnx_model_can_perform_inference(self, onnx_model_path):
        """ONNXモデルで推論が実行できることを確認"""
        # ONNXモデルをロード
        session = ort.InferenceSession(onnx_model_path)

        # テストデータを準備（1サンプル）
        test_input = np.array([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32)

        # 推論実行
        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: test_input})

        # 出力が存在することを確認
        assert outputs is not None
        assert len(outputs) >= 1  # 少なくともラベル出力がある

    def test_onnx_inference_matches_sklearn_prediction(
        self, trained_pipeline_and_test_data, onnx_model_path
    ):
        """
        ONNXモデルの推論結果がscikit-learnモデルの予測と一致することを確認
        """
        trained_model, x_test, _ = trained_pipeline_and_test_data

        # scikit-learnで予測
        sklearn_predictions = trained_model.predict(x_test)

        # ONNXで推論
        session = ort.InferenceSession(onnx_model_path)
        input_name = session.get_inputs()[0].name
        x_test_float32 = x_test.astype(np.float32)
        onnx_outputs = session.run(None, {input_name: x_test_float32})
        onnx_predictions = onnx_outputs[0]  # ラベル出力

        # 予測結果が一致することを確認
        assert np.array_equal(sklearn_predictions, onnx_predictions)

    def test_onnx_probability_output(self, trained_pipeline_and_test_data, onnx_model_path):
        """
        ONNXモデルが確率出力を持つことを確認
        （probability=Trueで学習しているため）
        """
        trained_model, x_test, _ = trained_pipeline_and_test_data

        # ONNXで推論
        session = ort.InferenceSession(onnx_model_path)
        input_name = session.get_inputs()[0].name
        x_test_float32 = x_test[:5].astype(np.float32)  # 最初の5サンプル
        onnx_outputs = session.run(None, {input_name: x_test_float32})

        # 確率出力（通常は2番目の出力）
        assert len(onnx_outputs) >= 2  # ラベルと確率の両方
        probabilities = onnx_outputs[1]

        # 確率の形式を確認
        assert len(probabilities) == 5  # 5サンプル分
        for prob_dict in probabilities:
            # 各サンプルはクラスごとの確率を持つ
            assert isinstance(prob_dict, dict)
            # 確率の合計が1に近いことを確認
            total_prob = sum(prob_dict.values())
            assert 0.99 <= total_prob <= 1.01

    def test_onnx_model_handles_batch_inference(self, onnx_model_path):
        """ONNXモデルがバッチ推論に対応していることを確認"""
        session = ort.InferenceSession(onnx_model_path)
        input_name = session.get_inputs()[0].name

        # 異なるバッチサイズでテスト
        for batch_size in [1, 5, 10, 20]:
            test_input = np.random.rand(batch_size, 4).astype(np.float32)
            outputs = session.run(None, {input_name: test_input})
            predictions = outputs[0]

            # バッチサイズ分の予測が返されることを確認
            assert len(predictions) == batch_size


class TestPipelineEdgeCases:
    """エッジケースのテスト"""

    def test_pipeline_with_minimum_test_size(self):
        """最小のテストサイズでもパイプラインが動作することを確認"""
        x_train, x_test, y_train, y_test = get_data(test_size=0.1, random_state=42)
        pipeline = build_pipeline()
        trained_model = train_model(pipeline, x_train, y_train)
        metrics = evaluate_model(trained_model, x_test, y_test)

        # テストサンプルが少なくてもメトリクスが計算できる
        assert 0.0 <= metrics["accuracy"] <= 1.0
        assert 0.0 <= metrics["precision"] <= 1.0
        assert 0.0 <= metrics["recall"] <= 1.0

    def test_pipeline_with_maximum_test_size(self):
        """大きめのテストサイズでもパイプラインが動作することを確認"""
        x_train, x_test, y_train, y_test = get_data(test_size=0.5, random_state=42)
        pipeline = build_pipeline()
        trained_model = train_model(pipeline, x_train, y_train)
        metrics = evaluate_model(trained_model, x_test, y_test)

        # 学習データとテストデータが半々でも動作する
        assert 0.0 <= metrics["accuracy"] <= 1.0
        assert 0.0 <= metrics["precision"] <= 1.0
        assert 0.0 <= metrics["recall"] <= 1.0

    def test_exported_onnx_model_is_valid(self):
        """エクスポートされたONNXモデルが妥当であることを確認"""
        x_train, x_test, y_train, y_test = get_data(test_size=0.3, random_state=42)
        pipeline = build_pipeline()
        trained_model = train_model(pipeline, x_train, y_train)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_model.onnx"
            export_to_onnx(trained_model, str(output_path))

            # ONNXモデルをロードして検証
            onnx_model = onnx.load(str(output_path))
            onnx.checker.check_model(onnx_model)  # 例外が発生しなければOK
