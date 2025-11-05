"""Trainer のユニットテスト"""

import numpy as np
import pytest

from iris_binary.data_loader import IrisTarget, load_and_transform_data
from iris_binary.model import build_svc_pipeline
from iris_binary.trainer import evaluate_model, train_model


class TestTrainer:
    """Trainer のテストクラス"""

    @pytest.fixture
    def sample_data(self):
        """テスト用データ"""
        return load_and_transform_data(
            test_size=0.3, target_iris=IrisTarget.SETOSA, random_state=42
        )

    @pytest.fixture
    def trained_model(self, sample_data):
        """学習済みモデル"""
        X_train, _, y_train, _ = sample_data
        model = build_svc_pipeline()
        train_model(model, X_train, y_train)
        return model

    def test_train_model(self, sample_data):
        """モデルが学習できる"""
        X_train, _, y_train, _ = sample_data
        model = build_svc_pipeline()

        # 学習前はfittedではない
        assert not hasattr(model.named_steps["svc"], "support_vectors_")

        train_model(model, X_train, y_train)

        # 学習後はfittedである
        assert hasattr(model.named_steps["svc"], "support_vectors_")

    def test_evaluate_model(self, sample_data, trained_model):
        """評価指標が計算できる"""
        _, X_test, _, y_test = sample_data

        metrics = evaluate_model(trained_model, X_test, y_test)

        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics

    def test_metrics_range(self, sample_data, trained_model):
        """評価指標が0〜1の範囲である"""
        _, X_test, _, y_test = sample_data

        metrics = evaluate_model(trained_model, X_test, y_test)

        for metric_name, value in metrics.items():
            assert 0.0 <= value <= 1.0, f"{metric_name} is out of range: {value}"

    def test_prediction_shape(self, sample_data, trained_model):
        """予測結果の形状が正しい"""
        _, X_test, _, y_test = sample_data

        predictions = trained_model.predict(X_test)

        assert len(predictions) == len(y_test)
        assert predictions.shape == y_test.shape

    def test_prediction_binary(self, sample_data, trained_model):
        """予測結果が二値（0 or 1）である"""
        _, X_test, _, _ = sample_data

        predictions = trained_model.predict(X_test)

        assert set(np.unique(predictions)) <= {0, 1}

    def test_high_accuracy_setosa(self, sample_data, trained_model):
        """setosaの分類精度が高い（> 0.90）"""
        _, X_test, _, y_test = sample_data

        metrics = evaluate_model(trained_model, X_test, y_test)

        # setosaは線形分離可能なため、高精度が期待される
        assert metrics["accuracy"] > 0.90
