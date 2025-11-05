"""
CNNモデル定義モジュール。

このモジュールはCIFAR-10画像分類用のシンプルなCNNモデルを定義します。
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleCNN(nn.Module):
    """
    CIFAR-10用のシンプルなCNNモデル。

    アーキテクチャ:
        - Conv2d(3→6, kernel=5)
        - ReLU
        - MaxPool2d(2, 2)
        - Conv2d(6→16, kernel=5)
        - ReLU
        - MaxPool2d(2, 2)
        - Flatten
        - Linear(400→120)
        - ReLU
        - Linear(120→84)
        - ReLU
        - Linear(84→10)

    Examples:
        >>> model = SimpleCNN()
        >>> x = torch.randn(1, 3, 32, 32)
        >>> output = model(x)
        >>> output.shape
        torch.Size([1, 10])
    """

    def __init__(self) -> None:
        """SimpleCNNモデルを初期化する。"""
        super(SimpleCNN, self).__init__()

        # 畳み込み層1: 3チャネル → 6チャネル
        self.conv1 = nn.Conv2d(3, 6, kernel_size=5)

        # プーリング層: 2x2 MaxPooling
        self.pool = nn.MaxPool2d(2, 2)

        # 畳み込み層2: 6チャネル → 16チャネル
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)

        # 全結合層1: 400 → 120
        # 計算: 16チャネル × 5×5ピクセル = 400
        self.fc1 = nn.Linear(16 * 5 * 5, 120)

        # 全結合層2: 120 → 84
        self.fc2 = nn.Linear(120, 84)

        # 全結合層3: 84 → 10（10クラス分類）
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        順伝播を実行する。

        Args:
            x: 入力テンソル (batch_size, 3, 32, 32)

        Returns:
            torch.Tensor: 出力テンソル (batch_size, 10)

        Examples:
            >>> model = SimpleCNN()
            >>> x = torch.randn(4, 3, 32, 32)
            >>> output = model(x)
            >>> output.shape
            torch.Size([4, 10])
        """
        # 畳み込み層1 + ReLU + プーリング
        # (batch, 3, 32, 32) → (batch, 6, 28, 28) → (batch, 6, 14, 14)
        x = self.pool(F.relu(self.conv1(x)))

        # 畳み込み層2 + ReLU + プーリング
        # (batch, 6, 14, 14) → (batch, 16, 10, 10) → (batch, 16, 5, 5)
        x = self.pool(F.relu(self.conv2(x)))

        # 平坦化
        # (batch, 16, 5, 5) → (batch, 400)
        x = x.view(-1, 16 * 5 * 5)

        # 全結合層1 + ReLU
        # (batch, 400) → (batch, 120)
        x = F.relu(self.fc1(x))

        # 全結合層2 + ReLU
        # (batch, 120) → (batch, 84)
        x = F.relu(self.fc2(x))

        # 全結合層3（出力層）
        # (batch, 84) → (batch, 10)
        x = self.fc3(x)

        return x


def create_simple_cnn() -> nn.Module:
    """
    SimpleCNNモデルを作成する。

    Returns:
        nn.Module: 初期化されたSimpleCNNモデル

    Examples:
        >>> model = create_simple_cnn()
        >>> isinstance(model, SimpleCNN)
        True
        >>> x = torch.randn(2, 3, 32, 32)
        >>> output = model(x)
        >>> output.shape
        torch.Size([2, 10])
    """
    model = SimpleCNN()
    return model
