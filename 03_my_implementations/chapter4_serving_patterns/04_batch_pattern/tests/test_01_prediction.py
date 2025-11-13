"""推論層のユニットテスト

ONNX Runtime推論クラスのテストを実施します。
"""

import pytest

from src.ml.prediction import Classifier, classifier


class TestClassifier:
    """Classifierクラスのテスト"""

    def test_load_model(self):
        """モデルが正しくロードされることをテスト"""
        assert classifier.classifier is not None
        assert classifier.input_name != ""
        assert classifier.output_name != ""

    def test_load_label(self):
        """ラベルが正しくロードされることをテスト"""
        assert len(classifier.label) == 3
        assert classifier.label["0"] == "setosa"
        assert classifier.label["1"] == "versicolor"
        assert classifier.label["2"] == "virginica"

    def test_predict_setosa(self):
        """setosaの推論をテスト"""
        data = [[5.1, 3.5, 1.4, 0.2]]
        prediction = classifier.predict(data)

        # 確率値が3次元であることを確認
        assert len(prediction) == 3

        # 各確率値が0-1の範囲であることを確認
        for prob in prediction:
            assert 0.0 <= prob <= 1.0

        # 確率値の合計が1に近いことを確認
        assert abs(sum(prediction) - 1.0) < 0.01

    def test_predict_virginica(self):
        """virginicaの推論をテスト"""
        data = [[6.3, 3.3, 6.0, 2.5]]
        prediction = classifier.predict(data)

        # 確率値が3次元であることを確認
        assert len(prediction) == 3

        # virginica（クラス2）の確率が最も高いことを確認
        assert prediction.argmax() == 2

    def test_predict_dict(self):
        """Dict形式の推論をテスト"""
        data = [[5.1, 3.5, 1.4, 0.2]]
        prediction_dict = classifier.predict_dict(data)

        # Dict形式であることを確認
        assert isinstance(prediction_dict, dict)

        # キーが"0", "1", "2"であることを確認
        assert set(prediction_dict.keys()) == {"0", "1", "2"}

        # 値が確率値（float）であることを確認
        for value in prediction_dict.values():
            assert isinstance(value, float)
            assert 0.0 <= value <= 1.0

    def test_predict_label_setosa(self):
        """setosaのラベル推論をテスト"""
        data = [[5.1, 3.5, 1.4, 0.2]]
        label = classifier.predict_label(data)

        assert label == "setosa"

    def test_predict_label_virginica(self):
        """virginicaのラベル推論をテスト"""
        data = [[6.3, 3.3, 6.0, 2.5]]
        label = classifier.predict_label(data)

        assert label == "virginica"

    def test_get_metadata(self):
        """メタデータ取得をテスト"""
        metadata = classifier.get_metadata()

        assert metadata["model_name"] == "iris_svc"
        assert metadata["model_type"] == "ONNX"
        assert metadata["input_dim"] == 4
        assert metadata["output_dim"] == 3
        assert metadata["labels"] == {"0": "setosa", "1": "versicolor", "2": "virginica"}

    def test_multiple_predictions(self):
        """複数データの推論をテスト"""
        data_list = [
            [5.1, 3.5, 1.4, 0.2],  # setosa
            [6.3, 3.3, 6.0, 2.5],  # virginica
            [5.9, 3.0, 5.1, 1.8],  # virginica
        ]

        for data in data_list:
            prediction = classifier.predict([data])
            assert len(prediction) == 3
            assert 0.0 <= prediction.min() <= 1.0
            assert 0.0 <= prediction.max() <= 1.0
