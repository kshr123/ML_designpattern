"""
Predictionモジュールのテスト

このモジュールは、ONNX推論ロジックをテストします。
"""

import json
from typing import Dict, List

import numpy as np
import pytest


class TestDataModel:
    """Dataモデルのテスト"""

    def test_data_model_default(self):
        """Dataモデルのデフォルト値が正しい"""
        from src.ml.prediction import Data

        data = Data()
        assert data.data == [[5.1, 3.5, 1.4, 0.2]]

    def test_data_model_custom(self):
        """Dataモデルにカスタム値を設定できる"""
        from src.ml.prediction import Data

        custom_data = [[1.0, 2.0, 3.0, 4.0]]
        data = Data(data=custom_data)
        assert data.data == custom_data


class TestClassifier:
    """Classifierクラスのテスト"""

    @pytest.fixture
    def model_filepath(self):
        """モデルファイルのパス"""
        return "models/iris_svc.onnx"

    @pytest.fixture
    def label_filepath(self):
        """ラベルファイルのパス"""
        return "models/label.json"

    @pytest.fixture
    def classifier(self, model_filepath, label_filepath):
        """Classifierインスタンス"""
        from src.ml.prediction import Classifier

        return Classifier(
            model_filepath=model_filepath,
            label_filepath=label_filepath,
        )

    def test_classifier_initialization(self, classifier):
        """Classifierが正しく初期化される"""
        assert classifier.classifier is not None
        assert classifier.label is not None
        assert classifier.input_name != ""
        assert classifier.output_name != ""

    def test_load_model(self, model_filepath, label_filepath):
        """モデルファイルを正しく読み込める"""
        from src.ml.prediction import Classifier

        classifier = Classifier(
            model_filepath=model_filepath,
            label_filepath=label_filepath,
        )
        assert classifier.classifier is not None

    def test_load_label(self, model_filepath, label_filepath):
        """ラベルファイルを正しく読み込める"""
        from src.ml.prediction import Classifier

        classifier = Classifier(
            model_filepath=model_filepath,
            label_filepath=label_filepath,
        )
        assert isinstance(classifier.label, dict)
        assert "0" in classifier.label
        assert "1" in classifier.label
        assert "2" in classifier.label

    def test_predict_setosa(self, classifier):
        """Iris setosaの推論が正しい"""
        # Iris setosa のサンプルデータ
        data = [[5.1, 3.5, 1.4, 0.2]]
        prediction = classifier.predict(data)

        assert isinstance(prediction, np.ndarray)
        assert len(prediction) == 3
        # setosa（index 0）の確率が最も高い
        assert np.argmax(prediction) == 0

    def test_predict_versicolor(self, classifier):
        """Iris versicolorの推論が正しい"""
        # Iris versicolor のサンプルデータ
        data = [[5.9, 3.0, 5.1, 1.8]]
        prediction = classifier.predict(data)

        assert isinstance(prediction, np.ndarray)
        assert len(prediction) == 3
        # versicolor または virginica（index 1 or 2）の確率が高い
        assert np.argmax(prediction) in [1, 2]

    def test_predict_virginica(self, classifier):
        """Iris virginicaの推論が正しい"""
        # Iris virginica のサンプルデータ
        data = [[6.3, 3.3, 6.0, 2.5]]
        prediction = classifier.predict(data)

        assert isinstance(prediction, np.ndarray)
        assert len(prediction) == 3
        # virginica（index 2）の確率が最も高い
        assert np.argmax(prediction) == 2

    def test_predict_label_setosa(self, classifier):
        """Iris setosaのラベル予測が正しい"""
        data = [[5.1, 3.5, 1.4, 0.2]]
        label = classifier.predict_label(data)

        assert isinstance(label, str)
        assert label == "setosa"

    def test_predict_label_virginica(self, classifier):
        """Iris virginicaのラベル予測が正しい"""
        data = [[6.3, 3.3, 6.0, 2.5]]
        label = classifier.predict_label(data)

        assert isinstance(label, str)
        assert label == "virginica"

    def test_predict_returns_probabilities(self, classifier):
        """predict()が確率値を返す"""
        data = [[5.1, 3.5, 1.4, 0.2]]
        prediction = classifier.predict(data)

        # 確率値の合計が1に近い
        assert 0.99 <= np.sum(prediction) <= 1.01

    def test_predict_output_shape(self, classifier):
        """predict()の出力形状が正しい"""
        data = [[5.1, 3.5, 1.4, 0.2]]
        prediction = classifier.predict(data)

        assert prediction.shape == (3,)
