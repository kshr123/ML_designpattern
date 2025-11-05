"""
トレーナーモジュールのテスト。

モデルの学習と評価の機能をテストします。
"""

import pytest
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from cifar10_cnn.model import SimpleCNN
from cifar10_cnn.trainer import evaluate_model, train_model


@pytest.fixture
def dummy_data() -> tuple[DataLoader, DataLoader]:
    """ダミーのDataLoaderを作成する。"""
    # 小さなダミーデータセット
    train_images = torch.randn(100, 3, 32, 32)
    train_labels = torch.randint(0, 10, (100,))
    train_dataset = TensorDataset(train_images, train_labels)
    train_loader = DataLoader(train_dataset, batch_size=10, shuffle=True)

    test_images = torch.randn(20, 3, 32, 32)
    test_labels = torch.randint(0, 10, (20,))
    test_dataset = TensorDataset(test_images, test_labels)
    test_loader = DataLoader(test_dataset, batch_size=10, shuffle=False)

    return train_loader, test_loader


@pytest.fixture
def model() -> nn.Module:
    """テスト用のモデルを作成する。"""
    return SimpleCNN()


class TestEvaluateModel:
    """evaluate_model関数のテスト。"""

    def test_evaluate_model_returns_dict(
        self, model: nn.Module, dummy_data: tuple[DataLoader, DataLoader]
    ) -> None:
        """evaluate_model関数が辞書を返すことを確認する。"""
        _, test_loader = dummy_data
        result = evaluate_model(model, test_loader, device="cpu")

        assert isinstance(result, dict)

    def test_evaluate_model_returns_loss(
        self, model: nn.Module, dummy_data: tuple[DataLoader, DataLoader]
    ) -> None:
        """evaluate_model関数がlossを返すことを確認する。"""
        _, test_loader = dummy_data
        result = evaluate_model(model, test_loader, device="cpu")

        assert "loss" in result
        assert isinstance(result["loss"], float)
        assert result["loss"] > 0

    def test_evaluate_model_returns_accuracy(
        self, model: nn.Module, dummy_data: tuple[DataLoader, DataLoader]
    ) -> None:
        """evaluate_model関数がaccuracyを返すことを確認する。"""
        _, test_loader = dummy_data
        result = evaluate_model(model, test_loader, device="cpu")

        assert "accuracy" in result
        assert isinstance(result["accuracy"], float)
        assert 0 <= result["accuracy"] <= 100

    def test_evaluate_model_no_gradient(
        self, model: nn.Module, dummy_data: tuple[DataLoader, DataLoader]
    ) -> None:
        """evaluate_model実行中に勾配が計算されないことを確認する。"""
        _, test_loader = dummy_data

        # 評価前のパラメータ状態を保存
        params_before = [p.clone() for p in model.parameters()]

        # 評価実行
        evaluate_model(model, test_loader, device="cpu")

        # パラメータが変更されていないことを確認
        params_after = list(model.parameters())
        for pb, pa in zip(params_before, params_after):
            assert torch.equal(pb, pa)


class TestTrainModel:
    """train_model関数のテスト。"""

    def test_train_model_returns_dict(
        self, model: nn.Module, dummy_data: tuple[DataLoader, DataLoader]
    ) -> None:
        """train_model関数が辞書を返すことを確認する。"""
        train_loader, test_loader = dummy_data
        result = train_model(
            model,
            train_loader,
            test_loader,
            epochs=1,
            learning_rate=0.001,
            device="cpu",
        )

        assert isinstance(result, dict)

    def test_train_model_returns_metrics(
        self, model: nn.Module, dummy_data: tuple[DataLoader, DataLoader]
    ) -> None:
        """train_model関数がtest_lossとtest_accuracyを返すことを確認する。"""
        train_loader, test_loader = dummy_data
        result = train_model(
            model,
            train_loader,
            test_loader,
            epochs=1,
            learning_rate=0.001,
            device="cpu",
        )

        assert "test_loss" in result
        assert "test_accuracy" in result
        assert isinstance(result["test_loss"], float)
        assert isinstance(result["test_accuracy"], float)

    def test_train_model_updates_parameters(
        self, model: nn.Module, dummy_data: tuple[DataLoader, DataLoader]
    ) -> None:
        """train_model関数がモデルのパラメータを更新することを確認する。"""
        train_loader, test_loader = dummy_data

        # 学習前のパラメータ状態を保存
        params_before = [p.clone() for p in model.parameters()]

        # 学習実行
        train_model(
            model,
            train_loader,
            test_loader,
            epochs=1,
            learning_rate=0.001,
            device="cpu",
        )

        # パラメータが更新されていることを確認
        params_after = list(model.parameters())
        params_changed = False
        for pb, pa in zip(params_before, params_after):
            if not torch.equal(pb, pa):
                params_changed = True
                break

        assert params_changed, "パラメータが更新されていません"

    def test_train_model_epochs_parameter(
        self, model: nn.Module, dummy_data: tuple[DataLoader, DataLoader]
    ) -> None:
        """train_model関数のepochsパラメータが機能することを確認する。"""
        train_loader, test_loader = dummy_data

        # 異なるepochs数で学習
        result = train_model(
            model,
            train_loader,
            test_loader,
            epochs=2,
            learning_rate=0.001,
            device="cpu",
        )

        # エラーなく完了することを確認
        assert result is not None

    def test_train_model_learning_rate_parameter(
        self, model: nn.Module, dummy_data: tuple[DataLoader, DataLoader]
    ) -> None:
        """train_model関数のlearning_rateパラメータが機能することを確認する。"""
        train_loader, test_loader = dummy_data

        # 異なる学習率で学習
        result = train_model(
            model,
            train_loader,
            test_loader,
            epochs=1,
            learning_rate=0.01,
            device="cpu",
        )

        # エラーなく完了することを確認
        assert result is not None
