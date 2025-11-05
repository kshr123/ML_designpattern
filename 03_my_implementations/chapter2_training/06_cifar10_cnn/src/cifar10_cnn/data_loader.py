"""
CIFAR-10データセットの読み込みと前処理モジュール。

このモジュールはtorchvisionを使ってCIFAR-10データセットをダウンロード・読み込み、
適切な前処理を施してDataLoaderを作成します。
"""

from typing import Tuple

from torch.utils.data import DataLoader
from torchvision import datasets, transforms


def get_transforms() -> transforms.Compose:
    """
    画像変換のCompose objectを作成する。

    CIFAR-10用の標準的な前処理を行います：
    - ToTensor: PIL ImageをTensorに変換（[0, 255] → [0.0, 1.0]）
    - Normalize: CIFAR-10の平均と標準偏差で正規化

    Returns:
        transforms.Compose: 変換のCompose object

    Examples:
        >>> transform = get_transforms()
        >>> # transformをDatasetに渡して使用
    """
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.4914, 0.4822, 0.4465),  # CIFAR-10の平均
                std=(0.2023, 0.1994, 0.2010),  # CIFAR-10の標準偏差
            ),
        ]
    )
    return transform


def load_cifar10_data(
    batch_size: int = 32,
    data_dir: str = "./data",
) -> Tuple[DataLoader, DataLoader]:
    """
    CIFAR-10データセットを読み込み、DataLoaderを作成する。

    Args:
        batch_size: バッチサイズ（デフォルト: 32）
        data_dir: データ保存ディレクトリ（デフォルト: "./data"）

    Returns:
        (train_loader, test_loader): 学習用とテスト用のDataLoaderのタプル

    Examples:
        >>> train_loader, test_loader = load_cifar10_data(batch_size=64)
        >>> # 最初のバッチを取得
        >>> images, labels = next(iter(train_loader))
        >>> images.shape
        torch.Size([64, 3, 32, 32])

    Notes:
        - 初回実行時はデータセットがダウンロードされます
        - 学習データ: 50,000枚
        - テストデータ: 10,000枚
        - 画像サイズ: 32×32 RGB
        - クラス数: 10
    """
    transform = get_transforms()

    # CIFAR-10学習データセットをダウンロード・読み込み
    train_dataset = datasets.CIFAR10(
        root=data_dir,
        train=True,
        download=True,
        transform=transform,
    )

    # CIFAR-10テストデータセットをダウンロード・読み込み
    test_dataset = datasets.CIFAR10(
        root=data_dir,
        train=False,
        download=True,
        transform=transform,
    )

    # DataLoaderを作成
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,  # 学習時はシャッフル
        num_workers=0,  # マルチプロセス不使用（互換性のため）
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,  # テスト時はシャッフルしない
        num_workers=0,
    )

    return train_loader, test_loader
