"""
Tests for evaluator module
"""

import pytest

from iris_sklearn_svc.data_loader import get_data
from iris_sklearn_svc.evaluator import evaluate_model
from iris_sklearn_svc.model import build_pipeline
from iris_sklearn_svc.trainer import train_model


class TestEvaluateModel:
    """Tests for evaluate_model function"""

    @pytest.fixture
    def trained_model_and_data(self):
        """学習済みモデルとテストデータを準備"""
        # データ読み込み
        x_train, x_test, y_train, y_test = get_data(test_size=0.3, random_state=42)

        # モデル学習
        pipeline = build_pipeline()
        trained_model = train_model(pipeline, x_train, y_train)

        return trained_model, x_test, y_test

    def test_evaluate_model_returns_dict(self, trained_model_and_data):
        """評価結果が辞書で返されることを確認"""
        trained_model, x_test, y_test = trained_model_and_data
        metrics = evaluate_model(trained_model, x_test, y_test)

        assert isinstance(metrics, dict)

    def test_metrics_contains_required_keys(self, trained_model_and_data):
        """評価結果に必要なキーが含まれることを確認"""
        trained_model, x_test, y_test = trained_model_and_data
        metrics = evaluate_model(trained_model, x_test, y_test)

        # 必須のキー
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics

    def test_accuracy_is_float(self, trained_model_and_data):
        """accuracyがfloat型であることを確認"""
        trained_model, x_test, y_test = trained_model_and_data
        metrics = evaluate_model(trained_model, x_test, y_test)

        assert isinstance(metrics["accuracy"], float)

    def test_precision_is_float(self, trained_model_and_data):
        """precisionがfloat型であることを確認"""
        trained_model, x_test, y_test = trained_model_and_data
        metrics = evaluate_model(trained_model, x_test, y_test)

        assert isinstance(metrics["precision"], float)

    def test_recall_is_float(self, trained_model_and_data):
        """recallがfloat型であることを確認"""
        trained_model, x_test, y_test = trained_model_and_data
        metrics = evaluate_model(trained_model, x_test, y_test)

        assert isinstance(metrics["recall"], float)

    def test_metrics_are_in_valid_range(self, trained_model_and_data):
        """評価指標が0-1の範囲内であることを確認"""
        trained_model, x_test, y_test = trained_model_and_data
        metrics = evaluate_model(trained_model, x_test, y_test)

        # 全ての指標は0-1の範囲
        assert 0.0 <= metrics["accuracy"] <= 1.0
        assert 0.0 <= metrics["precision"] <= 1.0
        assert 0.0 <= metrics["recall"] <= 1.0

    def test_model_achieves_good_accuracy(self, trained_model_and_data):
        """モデルが良好な精度を達成することを確認"""
        trained_model, x_test, y_test = trained_model_and_data
        metrics = evaluate_model(trained_model, x_test, y_test)

        # Irisデータセットは簡単なので、test精度も90%以上期待
        assert metrics["accuracy"] > 0.9

    def test_precision_and_recall_are_reasonable(self, trained_model_and_data):
        """precisionとrecallが妥当な値であることを確認"""
        trained_model, x_test, y_test = trained_model_and_data
        metrics = evaluate_model(trained_model, x_test, y_test)

        # 良いモデルなのでprecisionとrecallも高いはず
        assert metrics["precision"] > 0.85
        assert metrics["recall"] > 0.85

    def test_reproducibility(self, trained_model_and_data):
        """同じモデル・データで評価すると同じ結果が得られることを確認"""
        trained_model, x_test, y_test = trained_model_and_data

        # 2回評価
        metrics1 = evaluate_model(trained_model, x_test, y_test)
        metrics2 = evaluate_model(trained_model, x_test, y_test)

        # 同じ結果
        assert metrics1["accuracy"] == metrics2["accuracy"]
        assert metrics1["precision"] == metrics2["precision"]
        assert metrics1["recall"] == metrics2["recall"]

    def test_metrics_consistency(self, trained_model_and_data):
        """評価指標の一貫性を確認（F1スコアの計算で検証）"""
        trained_model, x_test, y_test = trained_model_and_data
        metrics = evaluate_model(trained_model, x_test, y_test)

        # F1スコアを計算（2 * precision * recall / (precision + recall)）
        precision = metrics["precision"]
        recall = metrics["recall"]

        if precision + recall > 0:
            f1_score = 2 * precision * recall / (precision + recall)
            # F1スコアは0-1の範囲
            assert 0.0 <= f1_score <= 1.0
