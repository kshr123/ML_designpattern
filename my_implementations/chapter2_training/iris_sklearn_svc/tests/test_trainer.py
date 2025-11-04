"""
Tests for trainer module
"""

import numpy as np
import pytest
from sklearn.pipeline import Pipeline

from iris_sklearn_svc.data_loader import get_data
from iris_sklearn_svc.model import build_pipeline
from iris_sklearn_svc.trainer import train_model


class TestTrainModel:
    """Tests for train_model function"""

    @pytest.fixture
    def sample_data(self):
        """テスト用のサンプルデータを準備"""
        x_train, x_test, y_train, y_test = get_data(test_size=0.3, random_state=42)
        return x_train, y_train

    @pytest.fixture
    def pipeline(self):
        """テスト用のパイプラインを準備"""
        return build_pipeline()

    def test_train_model_returns_pipeline(self, pipeline, sample_data):
        """学習後のパイプラインが返されることを確認"""
        x_train, y_train = sample_data
        trained_pipeline = train_model(pipeline, x_train, y_train)

        assert isinstance(trained_pipeline, Pipeline)

    def test_trained_model_is_fitted(self, pipeline, sample_data):
        """学習後のモデルがfitされていることを確認"""
        x_train, y_train = sample_data
        trained_pipeline = train_model(pipeline, x_train, y_train)

        # fitされている場合、predictが呼べる
        predictions = trained_pipeline.predict(x_train)
        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == len(y_train)

    def test_trained_model_can_predict_probabilities(self, pipeline, sample_data):
        """学習後のモデルが確率予測できることを確認"""
        x_train, y_train = sample_data
        trained_pipeline = train_model(pipeline, x_train, y_train)

        # probability=Trueなので確率予測が可能
        probabilities = trained_pipeline.predict_proba(x_train)
        assert isinstance(probabilities, np.ndarray)
        assert probabilities.shape == (len(y_train), 3)  # 3クラス分類

        # 確率の合計は1
        np.testing.assert_array_almost_equal(
            probabilities.sum(axis=1), np.ones(len(y_train)), decimal=5
        )

    def test_predictions_are_valid_classes(self, pipeline, sample_data):
        """予測結果が有効なクラスラベルであることを確認"""
        x_train, y_train = sample_data
        trained_pipeline = train_model(pipeline, x_train, y_train)

        predictions = trained_pipeline.predict(x_train)

        # 予測は0, 1, 2のいずれか
        unique_predictions = np.unique(predictions)
        assert all(pred in [0, 1, 2] for pred in unique_predictions)

    def test_model_achieves_reasonable_accuracy(self, pipeline, sample_data):
        """学習後のモデルが合理的な精度を達成することを確認"""
        x_train, y_train = sample_data
        trained_pipeline = train_model(pipeline, x_train, y_train)

        predictions = trained_pipeline.predict(x_train)
        accuracy = (predictions == y_train).sum() / len(y_train)

        # Irisデータセットは簡単なので、train精度は90%以上期待
        assert accuracy > 0.9

    def test_scaler_is_fitted(self, pipeline, sample_data):
        """StandardScalerが学習されていることを確認"""
        x_train, y_train = sample_data
        trained_pipeline = train_model(pipeline, x_train, y_train)

        scaler = trained_pipeline.named_steps["scaler"]

        # fitされている場合、mean_とscale_が設定されている
        assert hasattr(scaler, "mean_")
        assert hasattr(scaler, "scale_")
        assert scaler.mean_ is not None
        assert scaler.scale_ is not None

    def test_svc_is_fitted(self, pipeline, sample_data):
        """SVCが学習されていることを確認"""
        x_train, y_train = sample_data
        trained_pipeline = train_model(pipeline, x_train, y_train)

        svc = trained_pipeline.named_steps["svc"]

        # fitされている場合、support_vectors_が設定されている
        assert hasattr(svc, "support_vectors_")
        assert svc.support_vectors_ is not None
        assert len(svc.support_vectors_) > 0

    def test_reproducibility(self, sample_data):
        """同じデータで学習すると同じ結果が得られることを確認"""
        x_train, y_train = sample_data

        # 2つの独立したパイプラインを学習
        pipeline1 = build_pipeline()
        pipeline2 = build_pipeline()

        trained1 = train_model(pipeline1, x_train, y_train)
        trained2 = train_model(pipeline2, x_train, y_train)

        # 同じ入力に対して同じ予測をする
        predictions1 = trained1.predict(x_train)
        predictions2 = trained2.predict(x_train)

        np.testing.assert_array_equal(predictions1, predictions2)
