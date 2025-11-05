"""
CNNモデルのテスト。

SimpleCNNモデルの構造と動作をテストします。
"""

import torch
import torch.nn as nn

from cifar10_cnn.model import SimpleCNN, create_simple_cnn


class TestSimpleCNN:
    """SimpleCNNモデルのテスト。"""

    def test_simple_cnn_is_module(self) -> None:
        """SimpleCNNがnn.Moduleを継承していることを確認する。"""
        model = SimpleCNN()
        assert isinstance(model, nn.Module)

    def test_simple_cnn_forward_output_shape(self) -> None:
        """SimpleCNNのforwardメソッドが正しい形状の出力を返すことを確認する。"""
        model = SimpleCNN()
        batch_size = 4
        # CIFAR-10画像の形状: (batch, 3, 32, 32)
        x = torch.randn(batch_size, 3, 32, 32)

        output = model(x)

        # 出力形状: (batch, 10) - 10クラス分類
        assert output.shape == (batch_size, 10)

    def test_simple_cnn_output_dtype(self) -> None:
        """SimpleCNNの出力がfloat型であることを確認する。"""
        model = SimpleCNN()
        x = torch.randn(1, 3, 32, 32)

        output = model(x)

        assert output.dtype == torch.float32

    def test_simple_cnn_has_conv_layers(self) -> None:
        """SimpleCNNが畳み込み層を持つことを確認する。"""
        model = SimpleCNN()

        # conv1, conv2が存在することを確認
        assert hasattr(model, "conv1")
        assert hasattr(model, "conv2")
        assert isinstance(model.conv1, nn.Conv2d)
        assert isinstance(model.conv2, nn.Conv2d)

    def test_simple_cnn_has_fc_layers(self) -> None:
        """SimpleCNNが全結合層を持つことを確認する。"""
        model = SimpleCNN()

        # fc1, fc2, fc3が存在することを確認
        assert hasattr(model, "fc1")
        assert hasattr(model, "fc2")
        assert hasattr(model, "fc3")
        assert isinstance(model.fc1, nn.Linear)
        assert isinstance(model.fc2, nn.Linear)
        assert isinstance(model.fc3, nn.Linear)

    def test_simple_cnn_has_pool_layer(self) -> None:
        """SimpleCNNがプーリング層を持つことを確認する。"""
        model = SimpleCNN()

        assert hasattr(model, "pool")
        assert isinstance(model.pool, nn.MaxPool2d)

    def test_simple_cnn_batch_processing(self) -> None:
        """SimpleCNNが異なるバッチサイズで処理できることを確認する。"""
        model = SimpleCNN()

        for batch_size in [1, 4, 16, 32]:
            x = torch.randn(batch_size, 3, 32, 32)
            output = model(x)
            assert output.shape == (batch_size, 10)


class TestCreateSimpleCNN:
    """create_simple_cnn関数のテスト。"""

    def test_create_simple_cnn_returns_model(self) -> None:
        """create_simple_cnn関数がモデルを返すことを確認する。"""
        model = create_simple_cnn()
        assert isinstance(model, nn.Module)
        assert isinstance(model, SimpleCNN)

    def test_create_simple_cnn_model_is_trainable(self) -> None:
        """create_simple_cnnで作成したモデルが学習可能であることを確認する。"""
        model = create_simple_cnn()

        # パラメータが存在することを確認
        params = list(model.parameters())
        assert len(params) > 0

        # パラメータがrequires_grad=Trueであることを確認
        for param in params:
            assert param.requires_grad is True

    def test_create_simple_cnn_forward_pass(self) -> None:
        """create_simple_cnnで作成したモデルでforward passができることを確認する。"""
        model = create_simple_cnn()
        x = torch.randn(2, 3, 32, 32)

        output = model(x)

        assert output.shape == (2, 10)
        assert not torch.isnan(output).any()
