"""
PyTorchモデルのONNXエクスポートと検証モジュール。

このモジュールはPyTorchモデルをONNX形式にエクスポートし、
エクスポートされたモデルを検証する機能を提供します。
"""

from typing import Tuple

import numpy as np
import onnxruntime as rt  # type: ignore[import-untyped]
import torch
import torch.nn as nn


def export_to_onnx(
    model: nn.Module,
    onnx_path: str,
    input_shape: Tuple[int, int, int, int] = (1, 3, 32, 32),
) -> None:
    """
    PyTorchモデルをONNX形式にエクスポートする。

    Args:
        model: エクスポート対象のモデル
        onnx_path: ONNX保存先パス（.onnx拡張子）
        input_shape: 入力テンソルの形状（デフォルト: (1, 3, 32, 32)）

    Examples:
        >>> from cifar10_cnn.model import SimpleCNN
        >>> model = SimpleCNN()
        >>> export_to_onnx(model, "model.onnx")

    Notes:
        - モデルは自動的に評価モードに切り替わります
        - 入力名: "input"
        - 出力名: "output"
    """
    model.eval()  # 評価モードに切り替え

    # ダミー入力を作成
    dummy_input = torch.randn(*input_shape)

    # ONNX形式にエクスポート
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        verbose=False,
        input_names=["input"],
        output_names=["output"],
        export_params=True,
        dynamic_axes={
            "input": {0: "batch_size"},  # バッチサイズを可変にする
            "output": {0: "batch_size"},
        },
    )


def validate_onnx_model(
    pytorch_model: nn.Module,
    onnx_path: str,
    test_input: torch.Tensor,
) -> bool:
    """
    ONNXモデルとPyTorchモデルの予測が一致するか検証する。

    Args:
        pytorch_model: PyTorchモデル
        onnx_path: ONNXモデルのパス
        test_input: テスト用入力テンソル (batch_size, 3, 32, 32)

    Returns:
        bool: 全サンプルで予測クラスが一致すればTrue、そうでなければFalse

    Examples:
        >>> from cifar10_cnn.model import SimpleCNN
        >>> model = SimpleCNN()
        >>> export_to_onnx(model, "model.onnx")
        >>> test_input = torch.randn(2, 3, 32, 32)
        >>> is_valid = validate_onnx_model(model, "model.onnx", test_input)
        >>> is_valid
        True

    Notes:
        - PyTorchとONNX Runtimeの予測クラスを比較します
        - クラス予測が一致すればTrueを返します
    """
    pytorch_model.eval()

    # PyTorchモデルでの予測
    with torch.no_grad():
        pytorch_output = pytorch_model(test_input)
        _, pytorch_predicted = torch.max(pytorch_output, 1)

    # ONNX Runtimeで推論
    session = rt.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])

    # 入力データをnumpy配列に変換
    onnx_input = test_input.numpy()

    # ONNX推論の実行
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    onnx_output = session.run([output_name], {input_name: onnx_input})[0]

    # ONNXの出力から予測クラスを取得
    onnx_predicted = np.argmax(onnx_output, axis=1)

    # PyTorchとONNXの予測クラスが一致するか確認
    pytorch_predicted_np = pytorch_predicted.numpy()
    return np.array_equal(pytorch_predicted_np, onnx_predicted)
