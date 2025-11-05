"""
データローダーモジュールのテスト。

CIFAR-10データセットの読み込みと前処理をテストします。
"""

from torch.utils.data import DataLoader

from cifar10_cnn.data_loader import get_transforms, load_cifar10_data


class TestTransforms:
    """画像変換のテスト。"""

    def test_get_transforms_returns_compose(self) -> None:
        """get_transforms関数がCompose型を返すことを確認する。"""
        transform = get_transforms()
        assert transform is not None
        # Composeオブジェクトであることを確認
        assert hasattr(transform, "transforms")

    def test_transforms_has_totensor(self) -> None:
        """変換にToTensorが含まれることを確認する。"""
        transform = get_transforms()
        # ToTensorが含まれていることを確認
        transform_names = [t.__class__.__name__ for t in transform.transforms]
        assert "ToTensor" in transform_names

    def test_transforms_has_normalize(self) -> None:
        """変換にNormalizeが含まれることを確認する。"""
        transform = get_transforms()
        # Normalizeが含まれていることを確認
        transform_names = [t.__class__.__name__ for t in transform.transforms]
        assert "Normalize" in transform_names


class TestLoadCifar10Data:
    """CIFAR-10データ読み込みのテスト。"""

    def test_load_cifar10_data_returns_tuple(self) -> None:
        """load_cifar10_data関数がタプルを返すことを確認する。"""
        result = load_cifar10_data(batch_size=4)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_load_cifar10_data_returns_dataloaders(self) -> None:
        """load_cifar10_data関数がDataLoaderを返すことを確認する。"""
        train_loader, test_loader = load_cifar10_data(batch_size=4)
        assert isinstance(train_loader, DataLoader)
        assert isinstance(test_loader, DataLoader)

    def test_train_loader_batch_size(self) -> None:
        """学習DataLoaderのバッチサイズが正しいことを確認する。"""
        batch_size = 8
        train_loader, _ = load_cifar10_data(batch_size=batch_size)
        assert train_loader.batch_size == batch_size

    def test_test_loader_batch_size(self) -> None:
        """テストDataLoaderのバッチサイズが正しいことを確認する。"""
        batch_size = 8
        _, test_loader = load_cifar10_data(batch_size=batch_size)
        assert test_loader.batch_size == batch_size

    def test_train_loader_yields_correct_shape(self) -> None:
        """学習DataLoaderが正しい形状のデータを返すことを確認する。"""
        batch_size = 4
        train_loader, _ = load_cifar10_data(batch_size=batch_size)

        # 最初のバッチを取得
        images, labels = next(iter(train_loader))

        # 画像の形状確認: (batch_size, 3, 32, 32)
        assert images.shape == (batch_size, 3, 32, 32)
        # ラベルの形状確認: (batch_size,)
        assert labels.shape == (batch_size,)

    def test_test_loader_yields_correct_shape(self) -> None:
        """テストDataLoaderが正しい形状のデータを返すことを確認する。"""
        batch_size = 4
        _, test_loader = load_cifar10_data(batch_size=batch_size)

        # 最初のバッチを取得
        images, labels = next(iter(test_loader))

        # 画像の形状確認: (batch_size, 3, 32, 32)
        assert images.shape == (batch_size, 3, 32, 32)
        # ラベルの形状確認: (batch_size,)
        assert labels.shape == (batch_size,)

    def test_labels_range(self) -> None:
        """ラベルが0-9の範囲であることを確認する。"""
        train_loader, _ = load_cifar10_data(batch_size=100)
        _, labels = next(iter(train_loader))

        assert labels.min() >= 0
        assert labels.max() < 10

    def test_images_normalized(self) -> None:
        """画像が正規化されていることを確認する（平均0付近、標準偏差1付近）。"""
        train_loader, _ = load_cifar10_data(batch_size=1000)
        images, _ = next(iter(train_loader))

        # 正規化により、平均は0付近、標準偏差は1付近になるはず
        mean = images.mean()
        std = images.std()

        # 許容範囲内であることを確認（完全に0と1ではないが近い値）
        assert -0.5 < mean < 0.5
        assert 0.5 < std < 1.5

    def test_data_dir_parameter(self) -> None:
        """data_dirパラメータが正しく機能することを確認する。"""
        custom_dir = "./test_data"
        train_loader, test_loader = load_cifar10_data(batch_size=4, data_dir=custom_dir)
        assert train_loader is not None
        assert test_loader is not None
