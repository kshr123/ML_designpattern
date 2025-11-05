"""
ONNXエクスポーターモジュールのテスト。

PyTorchモデルのONNXエクスポートと検証をテストします。
"""

import os
import tempfile

import pytest
import torch
import torch.nn as nn

from cifar10_cnn.model import SimpleCNN
from cifar10_cnn.onnx_exporter import export_to_onnx, validate_onnx_model


@pytest.fixture
def model() -> nn.Module:
    """テスト用のモデルを作成する。"""
    return SimpleCNN()


@pytest.fixture
def temp_onnx_path() -> str:
    """一時的なONNXファイルパスを作成する。"""
    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as f:
        path = f.name
    yield path
    # テスト後にファイルを削除
    if os.path.exists(path):
        os.remove(path)


class TestExportToOnnx:
    """export_to_onnx関数のテスト。"""

    def test_export_to_onnx_creates_file(self, model: nn.Module, temp_onnx_path: str) -> None:
        """export_to_onnx関数がONNXファイルを作成することを確認する。"""
        export_to_onnx(model, temp_onnx_path)

        assert os.path.exists(temp_onnx_path)

    def test_export_to_onnx_file_not_empty(self, model: nn.Module, temp_onnx_path: str) -> None:
        """export_to_onnx関数が空でないONNXファイルを作成することを確認する。"""
        export_to_onnx(model, temp_onnx_path)

        # ファイルサイズが0より大きいことを確認
        file_size = os.path.getsize(temp_onnx_path)
        assert file_size > 0

    def test_export_to_onnx_with_custom_input_shape(
        self, model: nn.Module, temp_onnx_path: str
    ) -> None:
        """export_to_onnx関数がカスタム入力形状で動作することを確認する。"""
        custom_shape = (2, 3, 32, 32)  # バッチサイズ2
        export_to_onnx(model, temp_onnx_path, input_shape=custom_shape)

        assert os.path.exists(temp_onnx_path)

    def test_export_to_onnx_eval_mode(self, model: nn.Module, temp_onnx_path: str) -> None:
        """export_to_onnx関数がモデルを評価モードにすることを確認する。"""
        # 学習モードにする
        model.train()

        export_to_onnx(model, temp_onnx_path)

        # エクスポート後も評価モードになっていることを確認
        assert not model.training


class TestValidateOnnxModel:
    """validate_onnx_model関数のテスト。"""

    def test_validate_onnx_model_returns_bool(self, model: nn.Module, temp_onnx_path: str) -> None:
        """validate_onnx_model関数がboolを返すことを確認する。"""
        export_to_onnx(model, temp_onnx_path)

        test_input = torch.randn(1, 3, 32, 32)
        result = validate_onnx_model(model, temp_onnx_path, test_input)

        assert isinstance(result, bool)

    def test_validate_onnx_model_returns_true_for_valid_model(
        self, model: nn.Module, temp_onnx_path: str
    ) -> None:
        """validate_onnx_model関数が有効なモデルに対してTrueを返すことを確認する。"""
        export_to_onnx(model, temp_onnx_path)

        test_input = torch.randn(1, 3, 32, 32)
        result = validate_onnx_model(model, temp_onnx_path, test_input)

        assert result is True

    def test_validate_onnx_model_with_different_batch_sizes(
        self, model: nn.Module, temp_onnx_path: str
    ) -> None:
        """validate_onnx_model関数が異なるバッチサイズで動作することを確認する。"""
        export_to_onnx(model, temp_onnx_path)

        for batch_size in [1, 2, 4]:
            test_input = torch.randn(batch_size, 3, 32, 32)
            result = validate_onnx_model(model, temp_onnx_path, test_input)
            assert result is True

    def test_validate_onnx_model_output_matches_pytorch(
        self, model: nn.Module, temp_onnx_path: str
    ) -> None:
        """validate_onnx_modelがPyTorchとONNXの出力が一致することを確認する。"""
        model.eval()
        export_to_onnx(model, temp_onnx_path)

        test_input = torch.randn(2, 3, 32, 32)

        # validate_onnx_modelがTrueを返せば、出力が一致していることを意味する
        result = validate_onnx_model(model, temp_onnx_path, test_input)
        assert result is True
