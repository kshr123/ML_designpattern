"""
推論ロジックのユニットテスト

このモジュールはClassifierクラスの機能をテストします。
- モデルの読み込み
- ラベルの読み込み
- 推論（確率値）
- 推論（ラベル名）
"""

import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import pytest

from src.model_in_image.prediction import Classifier, Data


# テスト用の定数
TEST_MODEL_PATH = Path(__file__).parent.parent / "models" / "iris_svc.onnx"
TEST_LABEL_PATH = Path(__file__).parent.parent / "models" / "label.json"

# Irisデータセットのサンプルデータ（setosa）
SAMPLE_SETOSA = [[5.1, 3.5, 1.4, 0.2]]
# Irisデータセットのサンプルデータ（versicolor）
SAMPLE_VERSICOLOR = [[5.9, 3.0, 4.2, 1.5]]
# Irisデータセットのサンプルデータ（virginica）
SAMPLE_VIRGINICA = [[6.3, 2.9, 5.6, 1.8]]


class TestData:
    """Dataモデルのテスト"""

    def test_data_model_default(self):
        """デフォルト値が正しく設定されているかテスト"""
        data = Data()
        assert data.data == [[5.1, 3.5, 1.4, 0.2]]
        assert isinstance(data.data, list)
        assert isinstance(data.data[0], list)
        assert all(isinstance(x, float) for x in data.data[0])

    def test_data_model_custom(self):
        """カスタムデータが正しく設定されているかテスト"""
        custom_data = [[1.0, 2.0, 3.0, 4.0]]
        data = Data(data=custom_data)
        assert data.data == custom_data


class TestClassifier:
    """Classifierクラスのテスト"""

    @pytest.fixture
    def classifier(self) -> Classifier:
        """テスト用のClassifierインスタンスを返すフィクスチャ"""
        return Classifier(
            model_filepath=str(TEST_MODEL_PATH),
            label_filepath=str(TEST_LABEL_PATH),
        )

    def test_classifier_initialization(self, classifier: Classifier):
        """Classifierが正しく初期化されるかテスト"""
        assert classifier.model_filepath == str(TEST_MODEL_PATH)
        assert classifier.label_filepath == str(TEST_LABEL_PATH)
        assert classifier.classifier is not None
        assert classifier.label is not None
        assert classifier.input_name != ""
        assert classifier.output_name != ""

    def test_load_model(self, classifier: Classifier):
        """モデルが正しく読み込まれるかテスト"""
        assert classifier.classifier is not None
        # ONNXRuntimeのInferenceSessionが作成されていることを確認
        assert hasattr(classifier.classifier, "run")
        assert hasattr(classifier.classifier, "get_inputs")
        assert hasattr(classifier.classifier, "get_outputs")

    def test_load_label(self, classifier: Classifier):
        """ラベルが正しく読み込まれるかテスト"""
        assert isinstance(classifier.label, dict)
        assert "0" in classifier.label
        assert "1" in classifier.label
        assert "2" in classifier.label
        assert classifier.label["0"] == "setosa"
        assert classifier.label["1"] == "versicolor"
        assert classifier.label["2"] == "virginica"

    def test_predict_shape(self, classifier: Classifier):
        """推論結果の形状が正しいかテスト"""
        prediction = classifier.predict(data=SAMPLE_SETOSA)
        assert isinstance(prediction, np.ndarray)
        assert prediction.shape == (3,)  # 3クラス分の確率
        assert len(prediction) == 3

    def test_predict_probability_range(self, classifier: Classifier):
        """推論結果が確率値の範囲（0-1）にあるかテスト"""
        prediction = classifier.predict(data=SAMPLE_SETOSA)
        assert np.all(prediction >= 0.0)
        assert np.all(prediction <= 1.0)
        # 確率の合計が1に近いかテスト（SVMの場合、完全に1にならない場合がある）
        assert np.isclose(np.sum(prediction), 1.0, atol=0.1)

    def test_predict_setosa(self, classifier: Classifier):
        """setosaの推論が正しいかテスト"""
        prediction = classifier.predict(data=SAMPLE_SETOSA)
        # setosa（クラス0）の確率が最も高いことを確認
        assert np.argmax(prediction) == 0
        assert prediction[0] > 0.5  # setosaの確率が50%以上

    def test_predict_versicolor(self, classifier: Classifier):
        """versicolorの推論が正しいかテスト"""
        prediction = classifier.predict(data=SAMPLE_VERSICOLOR)
        # versicolor（クラス1）の確率が最も高いことを確認
        assert np.argmax(prediction) == 1
        assert prediction[1] > 0.5

    def test_predict_virginica(self, classifier: Classifier):
        """virginicaの推論が正しいかテスト"""
        prediction = classifier.predict(data=SAMPLE_VIRGINICA)
        # virginica（クラス2）の確率が最も高いことを確認
        assert np.argmax(prediction) == 2
        assert prediction[2] > 0.5

    def test_predict_label_setosa(self, classifier: Classifier):
        """setosaのラベル推論が正しいかテスト"""
        label = classifier.predict_label(data=SAMPLE_SETOSA)
        assert isinstance(label, str)
        assert label == "setosa"

    def test_predict_label_versicolor(self, classifier: Classifier):
        """versicolorのラベル推論が正しいかテスト"""
        label = classifier.predict_label(data=SAMPLE_VERSICOLOR)
        assert label == "versicolor"

    def test_predict_label_virginica(self, classifier: Classifier):
        """virginicaのラベル推論が正しいかテスト"""
        label = classifier.predict_label(data=SAMPLE_VIRGINICA)
        assert label == "virginica"

    def test_predict_multiple_samples(self, classifier: Classifier):
        """複数サンプルの推論が正しいかテスト"""
        # 注意: SVMモデルは通常バッチ推論をサポートしない
        # 1サンプルずつ推論する必要がある
        prediction1 = classifier.predict(data=SAMPLE_SETOSA)
        prediction2 = classifier.predict(data=SAMPLE_VERSICOLOR)

        assert prediction1.shape == (3,)
        assert prediction2.shape == (3,)
        assert np.argmax(prediction1) == 0  # setosa
        assert np.argmax(prediction2) == 1  # versicolor

    def test_predict_invalid_shape(self, classifier: Classifier):
        """不正な入力形状でエラーが発生するかテスト"""
        with pytest.raises(Exception):  # ONNXRuntimeがExceptionを投げる
            # 特徴量が3つしかない（正しくは4つ）
            invalid_data = [[5.1, 3.5, 1.4]]
            classifier.predict(data=invalid_data)

    def test_predict_invalid_type(self, classifier: Classifier):
        """不正な入力型でエラーが発生するかテスト"""
        with pytest.raises((TypeError, ValueError, Exception)):
            # 文字列データ
            invalid_data = [["a", "b", "c", "d"]]  # type: ignore
            classifier.predict(data=invalid_data)

    def test_model_file_not_found(self):
        """モデルファイルが存在しない場合にエラーが発生するかテスト"""
        with pytest.raises(Exception):
            Classifier(
                model_filepath="/nonexistent/model.onnx",
                label_filepath=str(TEST_LABEL_PATH),
            )

    def test_label_file_not_found(self):
        """ラベルファイルが存在しない場合にエラーが発生するかテスト"""
        with pytest.raises(FileNotFoundError):
            Classifier(
                model_filepath=str(TEST_MODEL_PATH),
                label_filepath="/nonexistent/label.json",
            )
