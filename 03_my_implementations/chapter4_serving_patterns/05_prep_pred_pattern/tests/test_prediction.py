"""推論層テスト（prediction.py用）

TDDアプローチ:
1. Red Phase: このテストを実行して失敗することを確認
2. Green Phase: src/ml/prediction.py を実装してテストをパス
3. Refactor Phase: コードを改善
"""

import json
from unittest.mock import MagicMock, Mock, patch

import numpy as np
from PIL import Image

# テスト対象のインポート（実装前なのでImportErrorになる）
from src.ml.prediction import Classifier, Data


class TestData:
    """Dataモデルのテスト"""

    def test_data_model_with_default(self):
        """デフォルト値でDataモデルを作成できる"""
        data = Data()
        assert data.data is not None

    def test_data_model_with_custom_value(self):
        """カスタム値でDataモデルを作成できる"""
        test_image = Image.new("RGB", (100, 100), color=(255, 0, 0))
        data = Data(data=test_image)
        assert data.data == test_image


class TestClassifierInit:
    """Classifierの初期化テスト"""

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_init_with_default_params(self, mock_open, mock_grpc_channel, mock_joblib_load):
        """デフォルトパラメータで初期化できる"""
        # モックの設定
        mock_preprocess_transformer = Mock()
        mock_softmax_transformer = Mock()
        mock_joblib_load.side_effect = [
            mock_preprocess_transformer,
            mock_softmax_transformer,
        ]
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(["cat", "dog"])

        classifier = Classifier(
            preprocess_transformer_path="/test/preprocess.pkl",
            softmax_transformer_path="/test/softmax.pkl",
            label_path="/test/labels.json",
            serving_address="localhost:50051",
        )

        assert classifier.serving_address == "localhost:50051"
        assert classifier.onnx_input_name == "input"
        assert classifier.onnx_output_name == "output"
        assert classifier.preprocess_transformer is not None
        assert classifier.softmax_transformer is not None
        assert len(classifier.label) > 0

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_init_with_custom_params(self, mock_open, mock_grpc_channel, mock_joblib_load):
        """カスタムパラメータで初期化できる"""
        mock_preprocess_transformer = Mock()
        mock_softmax_transformer = Mock()
        mock_joblib_load.side_effect = [
            mock_preprocess_transformer,
            mock_softmax_transformer,
        ]
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(["cat", "dog"])

        classifier = Classifier(
            preprocess_transformer_path="/custom/preprocess.pkl",
            softmax_transformer_path="/custom/softmax.pkl",
            label_path="/custom/labels.json",
            serving_address="pred:50051",
            onnx_input_name="custom_input",
            onnx_output_name="custom_output",
        )

        assert classifier.serving_address == "pred:50051"
        assert classifier.onnx_input_name == "custom_input"
        assert classifier.onnx_output_name == "custom_output"


class TestClassifierLoadModel:
    """モデル読み込みテスト"""

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_load_preprocess_transformer(self, mock_open, mock_grpc_channel, mock_joblib_load):
        """前処理transformerを読み込める"""
        mock_preprocess = Mock()
        mock_softmax = Mock()
        mock_joblib_load.side_effect = [mock_preprocess, mock_softmax]
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(["cat"])

        classifier = Classifier(
            preprocess_transformer_path="/test/preprocess.pkl",
            softmax_transformer_path="/test/softmax.pkl",
            label_path="/test/labels.json",
        )

        assert classifier.preprocess_transformer == mock_preprocess

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_load_softmax_transformer(self, mock_open, mock_grpc_channel, mock_joblib_load):
        """Softmax transformerを読み込める"""
        mock_preprocess = Mock()
        mock_softmax = Mock()
        mock_joblib_load.side_effect = [mock_preprocess, mock_softmax]
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(["cat"])

        classifier = Classifier(
            preprocess_transformer_path="/test/preprocess.pkl",
            softmax_transformer_path="/test/softmax.pkl",
            label_path="/test/labels.json",
        )

        assert classifier.softmax_transformer == mock_softmax


class TestClassifierLoadLabel:
    """ラベル読み込みテスト"""

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open", new_callable=MagicMock)
    def test_load_label_from_json(self, mock_open, mock_grpc_channel, mock_joblib_load):
        """JSONファイルからラベルを読み込める"""
        mock_preprocess = Mock()
        mock_softmax = Mock()
        mock_joblib_load.side_effect = [mock_preprocess, mock_softmax]

        # JSONデータのモック
        test_labels = ["cat", "dog", "bird"]
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps(test_labels)
        mock_open.return_value = mock_file

        classifier = Classifier(
            preprocess_transformer_path="/test/preprocess.pkl",
            softmax_transformer_path="/test/softmax.pkl",
            label_path="/test/labels.json",
        )

        # json.load()を使うので、read()ではなくjson.load()をモック
        with patch("json.load", return_value=test_labels):
            classifier.load_label()
            assert classifier.label == test_labels

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_load_imagenet_1000_labels(self, mock_open, mock_grpc_channel, mock_joblib_load):
        """ImageNet 1000クラスのラベルを読み込める"""
        mock_preprocess = Mock()
        mock_softmax = Mock()
        mock_joblib_load.side_effect = [mock_preprocess, mock_softmax]

        # ImageNet 1000クラス分のダミーラベル
        imagenet_labels = [f"class_{i}" for i in range(1000)]
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        with patch("json.load", return_value=imagenet_labels):
            classifier = Classifier(
                preprocess_transformer_path="/test/preprocess.pkl",
                softmax_transformer_path="/test/softmax.pkl",
                label_path="/test/imagenet_labels.json",
            )

            assert len(classifier.label) == 1000
            assert classifier.label[0] == "class_0"
            assert classifier.label[999] == "class_999"


class TestClassifierPredict:
    """推論メソッドのテスト"""

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_predict_returns_probabilities(self, mock_open, mock_grpc_channel, mock_joblib_load):
        """推論結果が確率として返される"""
        # モックの設定
        mock_preprocess = Mock()
        mock_softmax = Mock()
        mock_joblib_load.side_effect = [mock_preprocess, mock_softmax]
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        with patch("json.load", return_value=["cat", "dog"]):
            classifier = Classifier(
                preprocess_transformer_path="/test/preprocess.pkl",
                softmax_transformer_path="/test/softmax.pkl",
                label_path="/test/labels.json",
            )

            # 前処理の出力をモック
            preprocessed_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
            mock_preprocess.transform.return_value = preprocessed_data

            # gRPCレスポンスをモック
            mock_response = Mock()
            logits = np.random.randn(1, 1000).astype(np.float32)
            mock_response.outputs = {"output": Mock(raw_data=logits.tobytes(), dtype=np.float32)}
            classifier.stub = Mock()
            classifier.stub.Predict.return_value = mock_response

            # Softmax出力をモック
            probabilities = np.random.rand(1, 1000).astype(np.float32)
            probabilities /= probabilities.sum()  # 合計を1.0に正規化
            mock_softmax.transform.return_value = probabilities

            # 推論実行
            test_image = Image.new("RGB", (300, 300), color=(255, 0, 0))
            result = classifier.predict(test_image)

            # 結果の検証
            assert isinstance(result, list)
            assert len(result) > 0

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_predict_probability_sum_to_one(self, mock_open, mock_grpc_channel, mock_joblib_load):
        """推論結果の確率の合計が1.0になる"""
        mock_preprocess = Mock()
        mock_softmax = Mock()
        mock_joblib_load.side_effect = [mock_preprocess, mock_softmax]
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        with patch("json.load", return_value=["cat"] * 1000):
            classifier = Classifier(
                preprocess_transformer_path="/test/preprocess.pkl",
                softmax_transformer_path="/test/softmax.pkl",
                label_path="/test/labels.json",
            )

            preprocessed_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
            mock_preprocess.transform.return_value = preprocessed_data

            mock_response = Mock()
            logits = np.random.randn(1, 1000).astype(np.float32)
            mock_response.outputs = {"output": Mock(raw_data=logits.tobytes(), dtype=np.float32)}
            classifier.stub = Mock()
            classifier.stub.Predict.return_value = mock_response

            # 正しく正規化された確率分布
            probabilities = np.random.rand(1, 1000).astype(np.float32)
            probabilities /= probabilities.sum()
            mock_softmax.transform.return_value = probabilities

            test_image = Image.new("RGB", (224, 224))
            result = classifier.predict(test_image)

            # 確率の合計が1.0に近いことを確認
            assert np.isclose(np.sum(result), 1.0, atol=1e-5)

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_predict_calls_preprocess_transformer(
        self, mock_open, mock_grpc_channel, mock_joblib_load
    ):
        """推論時に前処理transformerが呼ばれる"""
        mock_preprocess = Mock()
        mock_softmax = Mock()
        mock_joblib_load.side_effect = [mock_preprocess, mock_softmax]
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        with patch("json.load", return_value=["cat"]):
            classifier = Classifier(
                preprocess_transformer_path="/test/preprocess.pkl",
                softmax_transformer_path="/test/softmax.pkl",
                label_path="/test/labels.json",
            )

            preprocessed_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
            mock_preprocess.transform.return_value = preprocessed_data

            mock_response = Mock()
            logits = np.random.randn(1, 1000).astype(np.float32)
            mock_response.outputs = {"output": Mock(raw_data=logits.tobytes(), dtype=np.float32)}
            classifier.stub = Mock()
            classifier.stub.Predict.return_value = mock_response

            probabilities = np.random.rand(1, 1000).astype(np.float32)
            mock_softmax.transform.return_value = probabilities

            test_image = Image.new("RGB", (224, 224))
            classifier.predict(test_image)

            # 前処理が呼ばれたことを確認
            mock_preprocess.transform.assert_called_once_with(test_image)

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_predict_calls_softmax_transformer(
        self, mock_open, mock_grpc_channel, mock_joblib_load
    ):
        """推論時にSoftmax transformerが呼ばれる"""
        mock_preprocess = Mock()
        mock_softmax = Mock()
        mock_joblib_load.side_effect = [mock_preprocess, mock_softmax]
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        with patch("json.load", return_value=["cat"]):
            classifier = Classifier(
                preprocess_transformer_path="/test/preprocess.pkl",
                softmax_transformer_path="/test/softmax.pkl",
                label_path="/test/labels.json",
            )

            preprocessed_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
            mock_preprocess.transform.return_value = preprocessed_data

            mock_response = Mock()
            logits = np.random.randn(1, 1000).astype(np.float32)
            mock_response.outputs = {"output": Mock(raw_data=logits.tobytes(), dtype=np.float32)}
            classifier.stub = Mock()
            classifier.stub.Predict.return_value = mock_response

            probabilities = np.random.rand(1, 1000).astype(np.float32)
            mock_softmax.transform.return_value = probabilities

            test_image = Image.new("RGB", (224, 224))
            classifier.predict(test_image)

            # Softmax transformerが呼ばれたことを確認
            assert mock_softmax.transform.called


class TestClassifierPredictLabel:
    """ラベル推論メソッドのテスト"""

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_predict_label_returns_string(self, mock_open, mock_grpc_channel, mock_joblib_load):
        """ラベル推論結果が文字列として返される"""
        mock_preprocess = Mock()
        mock_softmax = Mock()
        mock_joblib_load.side_effect = [mock_preprocess, mock_softmax]
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        test_labels = ["cat", "dog", "bird"]
        with patch("json.load", return_value=test_labels):
            classifier = Classifier(
                preprocess_transformer_path="/test/preprocess.pkl",
                softmax_transformer_path="/test/softmax.pkl",
                label_path="/test/labels.json",
            )

            preprocessed_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
            mock_preprocess.transform.return_value = preprocessed_data

            mock_response = Mock()
            logits = np.array([[1.0, 5.0, 2.0]]).astype(np.float32)  # dogが最大
            mock_response.outputs = {"output": Mock(raw_data=logits.tobytes(), dtype=np.float32)}
            classifier.stub = Mock()
            classifier.stub.Predict.return_value = mock_response

            # 確率分布をモック（dogが最大）
            probabilities = np.array([[0.1, 0.8, 0.1]])
            mock_softmax.transform.return_value = probabilities

            test_image = Image.new("RGB", (224, 224))
            result = classifier.predict_label(test_image)

            assert isinstance(result, str)
            assert result in test_labels

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_predict_label_returns_correct_label(
        self, mock_open, mock_grpc_channel, mock_joblib_load
    ):
        """最大確率のクラスのラベルが返される"""
        mock_preprocess = Mock()
        mock_softmax = Mock()
        mock_joblib_load.side_effect = [mock_preprocess, mock_softmax]
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        test_labels = ["cat", "dog", "bird"]
        with patch("json.load", return_value=test_labels):
            classifier = Classifier(
                preprocess_transformer_path="/test/preprocess.pkl",
                softmax_transformer_path="/test/softmax.pkl",
                label_path="/test/labels.json",
            )

            preprocessed_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
            mock_preprocess.transform.return_value = preprocessed_data

            mock_response = Mock()
            logits = np.array([[1.0, 5.0, 2.0]]).astype(np.float32)
            mock_response.outputs = {"output": Mock(raw_data=logits.tobytes(), dtype=np.float32)}
            classifier.stub = Mock()
            classifier.stub.Predict.return_value = mock_response

            # index=1 (dog) が最大
            probabilities = np.array([[0.1, 0.8, 0.1]])
            mock_softmax.transform.return_value = probabilities

            test_image = Image.new("RGB", (224, 224))
            result = classifier.predict_label(test_image)

            assert result == "dog"


class TestClassifierGrpcCommunication:
    """gRPC通信のテスト"""

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_grpc_request_format(self, mock_open, mock_grpc_channel, mock_joblib_load):
        """gRPCリクエストが正しいフォーマットで送信される"""
        mock_preprocess = Mock()
        mock_softmax = Mock()
        mock_joblib_load.side_effect = [mock_preprocess, mock_softmax]
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        with patch("json.load", return_value=["cat"]):
            classifier = Classifier(
                preprocess_transformer_path="/test/preprocess.pkl",
                softmax_transformer_path="/test/softmax.pkl",
                label_path="/test/labels.json",
            )

            preprocessed_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
            mock_preprocess.transform.return_value = preprocessed_data

            mock_stub = Mock()
            mock_response = Mock()
            logits = np.random.randn(1, 1000).astype(np.float32)
            mock_response.outputs = {"output": Mock(raw_data=logits.tobytes(), dtype=np.float32)}
            mock_stub.Predict.return_value = mock_response
            classifier.stub = mock_stub

            probabilities = np.random.rand(1, 1000).astype(np.float32)
            mock_softmax.transform.return_value = probabilities

            test_image = Image.new("RGB", (224, 224))
            classifier.predict(test_image)

            # gRPC Predictが呼ばれたことを確認
            assert mock_stub.Predict.called

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_grpc_channel_creation(self, mock_open, mock_grpc_channel, mock_joblib_load):
        """gRPCチャネルが正しいアドレスで作成される"""
        mock_preprocess = Mock()
        mock_softmax = Mock()
        mock_joblib_load.side_effect = [mock_preprocess, mock_softmax]
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        with patch("json.load", return_value=["cat"]):
            Classifier(
                preprocess_transformer_path="/test/preprocess.pkl",
                softmax_transformer_path="/test/softmax.pkl",
                label_path="/test/labels.json",
                serving_address="pred:50051",
            )

            # gRPCチャネルが正しいアドレスで作成されたことを確認
            mock_grpc_channel.assert_called_once_with("pred:50051")


class TestClassifierIntegration:
    """統合テスト（モックを最小限にする）"""

    @patch("src.ml.prediction.joblib.load")
    @patch("src.ml.prediction.grpc.insecure_channel")
    @patch("builtins.open")
    def test_end_to_end_prediction_flow(self, mock_open, mock_grpc_channel, mock_joblib_load):
        """画像入力から確率出力までの一連のフローが動作する"""
        from src.ml.transformers import (
            PytorchImagePreprocessTransformer,
            SoftmaxTransformer,
        )

        # 実際のtransformerを使用
        preprocess_transformer = PytorchImagePreprocessTransformer()
        softmax_transformer = SoftmaxTransformer()

        mock_joblib_load.side_effect = [preprocess_transformer, softmax_transformer]
        mock_file = MagicMock()
        mock_open.return_value = mock_file

        imagenet_labels = [f"class_{i}" for i in range(1000)]
        with patch("json.load", return_value=imagenet_labels):
            classifier = Classifier(
                preprocess_transformer_path="/test/preprocess.pkl",
                softmax_transformer_path="/test/softmax.pkl",
                label_path="/test/imagenet_labels.json",
            )

            # gRPCレスポンスをモック
            mock_stub = Mock()
            logits = np.random.randn(1, 1000).astype(np.float32)
            mock_response = Mock()
            mock_response.outputs = {"output": Mock(raw_data=logits.tobytes(), dtype=np.float32)}
            mock_stub.Predict.return_value = mock_response
            classifier.stub = mock_stub

            # 実際の画像で推論
            test_image = Image.new("RGB", (300, 300), color=(255, 128, 0))
            result = classifier.predict(test_image)

            # 結果の検証
            assert isinstance(result, list)
            assert len(result) == 1
            assert len(result[0]) == 1000
            assert np.isclose(np.sum(result), 1.0, atol=1e-5)

            # ラベル推論も動作することを確認
            label = classifier.predict_label(test_image)
            assert isinstance(label, str)
            assert label in imagenet_labels
