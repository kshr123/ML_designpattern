"""推論ロジックのテスト"""
import json
from pathlib import Path

import numpy as np
import pytest

from src.ml.prediction import Classifier, Data


class TestClassifier:
    """分類器のテストクラス"""

    @pytest.fixture
    def model_filepath(self) -> str:
        """モデルファイルパス"""
        return "models/iris_svc.onnx"

    @pytest.fixture
    def label_filepath(self) -> str:
        """ラベルファイルパス"""
        return "models/label.json"

    @pytest.fixture
    def classifier(self, model_filepath: str, label_filepath: str) -> Classifier:
        """分類器のインスタンス"""
        return Classifier(
            model_filepath=model_filepath,
            label_filepath=label_filepath,
        )

    def test_load_model_success(self, model_filepath: str, label_filepath: str):
        """モデルファイルを正常に読み込める"""
        # Act
        classifier = Classifier(
            model_filepath=model_filepath,
            label_filepath=label_filepath,
        )

        # Assert
        assert classifier.classifier is not None
        assert classifier.input_name is not None
        assert classifier.output_name is not None

    def test_load_label_success(self, model_filepath: str, label_filepath: str):
        """ラベルファイルを正常に読み込める"""
        # Act
        classifier = Classifier(
            model_filepath=model_filepath,
            label_filepath=label_filepath,
        )

        # Assert
        assert classifier.label is not None
        assert len(classifier.label) == 3
        assert "0" in classifier.label
        assert "1" in classifier.label
        assert "2" in classifier.label

    def test_predict_setosa(self, classifier: Classifier):
        """Setosaの推論ができる"""
        # Arrange
        data = [[5.1, 3.5, 1.4, 0.2]]

        # Act
        prediction = classifier.predict(data)

        # Assert
        assert prediction is not None
        assert len(prediction) == 3
        assert prediction[0] > 0.9  # Setosaの確率が高い

    def test_predict_versicolor(self, classifier: Classifier):
        """Versicolorの推論ができる"""
        # Arrange
        data = [[5.9, 3.0, 4.2, 1.5]]

        # Act
        prediction = classifier.predict(data)

        # Assert
        assert prediction is not None
        assert len(prediction) == 3
        assert prediction[1] > 0.5  # Versicolorの確率が高い

    def test_predict_virginica(self, classifier: Classifier):
        """Virginicaの推論ができる"""
        # Arrange
        data = [[6.7, 3.0, 5.2, 2.3]]

        # Act
        prediction = classifier.predict(data)

        # Assert
        assert prediction is not None
        assert len(prediction) == 3
        assert prediction[2] > 0.5  # Virginicaの確率が高い

    def test_predict_label_setosa(self, classifier: Classifier):
        """Setosaのラベル推論ができる"""
        # Arrange
        data = [[5.1, 3.5, 1.4, 0.2]]

        # Act
        label = classifier.predict_label(data)

        # Assert
        assert label == "setosa"

    def test_predict_label_versicolor(self, classifier: Classifier):
        """Versicolorのラベル推論ができる"""
        # Arrange
        data = [[5.9, 3.0, 4.2, 1.5]]

        # Act
        label = classifier.predict_label(data)

        # Assert
        assert label == "versicolor"

    def test_predict_label_virginica(self, classifier: Classifier):
        """Virginicaのラベル推論ができる"""
        # Arrange
        data = [[6.7, 3.0, 5.2, 2.3]]

        # Act
        label = classifier.predict_label(data)

        # Assert
        assert label == "virginica"

    def test_predict_with_invalid_data_shape(self, classifier: Classifier):
        """無効なデータ形状で推論するとエラーが発生する"""
        # Arrange
        data = [[5.1, 3.5, 1.4]]  # 3次元（正しくは4次元）

        # Act & Assert
        with pytest.raises(Exception):
            classifier.predict(data)


class TestData:
    """データモデルのテストクラス"""

    def test_data_default(self):
        """デフォルトデータが設定されている"""
        # Act
        data = Data()

        # Assert
        assert data.data == [[5.1, 3.5, 1.4, 0.2]]

    def test_data_custom(self):
        """カスタムデータを設定できる"""
        # Arrange
        custom_data = [[6.0, 3.0, 4.0, 1.0]]

        # Act
        data = Data(data=custom_data)

        # Assert
        assert data.data == custom_data
