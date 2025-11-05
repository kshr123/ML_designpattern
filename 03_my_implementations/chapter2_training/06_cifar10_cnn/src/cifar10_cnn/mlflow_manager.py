"""
MLflowを使った実験管理モジュール。

このモジュールはMLflowにパラメータ、メトリクス、モデルを記録する機能を提供します。
"""

from typing import Any, Dict

import mlflow
import mlflow.pytorch
import torch.nn as nn


def log_params(params: Dict[str, Any]) -> None:
    """
    パラメータをMLflowに記録する。

    Args:
        params: 記録するパラメータの辞書

    Examples:
        >>> with mlflow.start_run():
        ...     log_params({"epochs": 5, "batch_size": 32, "learning_rate": 0.001})
    """
    mlflow.log_params(params)


def log_metrics(metrics: Dict[str, float]) -> None:
    """
    メトリクスをMLflowに記録する。

    Args:
        metrics: 記録するメトリクスの辞書

    Examples:
        >>> with mlflow.start_run():
        ...     log_metrics({"test_loss": 0.5, "test_accuracy": 75.0})
    """
    mlflow.log_metrics(metrics)


def log_model(model: nn.Module, artifact_path: str = "model") -> None:
    """
    モデルをMLflowに記録する。

    Args:
        model: 記録するPyTorchモデル
        artifact_path: アーティファクトのパス（デフォルト: "model"）

    Examples:
        >>> from cifar10_cnn.model import SimpleCNN
        >>> model = SimpleCNN()
        >>> with mlflow.start_run():
        ...     log_model(model, artifact_path="model")
    """
    mlflow.pytorch.log_model(model, artifact_path)
