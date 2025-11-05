"""
モデルの学習と評価を行うモジュール。

このモジュールはCNNモデルの学習ループと評価ループを提供します。
"""

from typing import Dict

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader


def evaluate_model(
    model: nn.Module,
    test_loader: DataLoader,
    device: str = "cpu",
) -> Dict[str, float]:
    """
    モデルをテストデータで評価する。

    Args:
        model: 評価対象のモデル
        test_loader: テストデータのDataLoader
        device: デバイス（"cpu" or "cuda"）

    Returns:
        dict: 評価メトリクス（loss, accuracy）

    Examples:
        >>> model = SimpleCNN()
        >>> # test_loaderを作成
        >>> metrics = evaluate_model(model, test_loader, device="cpu")
        >>> "loss" in metrics
        True
        >>> "accuracy" in metrics
        True
    """
    model.eval()  # 評価モード
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():  # 勾配計算を無効化
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            # 順伝播
            outputs = model(images)
            loss = criterion(outputs, labels)

            # 損失を累積
            total_loss += loss.item()

            # 精度計算
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    # 平均損失と精度を計算
    avg_loss = total_loss / len(test_loader)
    accuracy = 100.0 * correct / total

    return {
        "loss": float(avg_loss),
        "accuracy": float(accuracy),
    }


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    epochs: int = 5,
    learning_rate: float = 0.001,
    device: str = "cpu",
) -> Dict[str, float]:
    """
    モデルを学習する。

    Args:
        model: 学習対象のモデル
        train_loader: 学習データのDataLoader
        test_loader: テストデータのDataLoader
        epochs: エポック数（デフォルト: 5）
        learning_rate: 学習率（デフォルト: 0.001）
        device: デバイス（"cpu" or "cuda"）

    Returns:
        dict: 最終的なテストメトリクス（test_loss, test_accuracy）

    Examples:
        >>> model = SimpleCNN()
        >>> # train_loader, test_loaderを作成
        >>> metrics = train_model(
        ...     model,
        ...     train_loader,
        ...     test_loader,
        ...     epochs=1,
        ...     device="cpu"
        ... )
        >>> "test_loss" in metrics
        True
        >>> "test_accuracy" in metrics
        True
    """
    model = model.to(device)
    model.train()  # 学習モード

    # 損失関数と最適化アルゴリズム
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # 学習ループ
    for epoch in range(epochs):
        running_loss = 0.0

        for i, (images, labels) in enumerate(train_loader):
            images = images.to(device)
            labels = labels.to(device)

            # 勾配をゼロにリセット
            optimizer.zero_grad()

            # 順伝播
            outputs = model(images)
            loss = criterion(outputs, labels)

            # 逆伝播
            loss.backward()

            # パラメータ更新
            optimizer.step()

            # 損失を累積
            running_loss += loss.item()

        # エポックごとの平均損失を表示
        avg_epoch_loss = running_loss / len(train_loader)
        print(f"Epoch [{epoch + 1}/{epochs}], Loss: {avg_epoch_loss:.4f}")

    # 最終評価
    final_metrics = evaluate_model(model, test_loader, device)

    return {
        "test_loss": final_metrics["loss"],
        "test_accuracy": final_metrics["accuracy"],
    }
