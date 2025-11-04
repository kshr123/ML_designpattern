"""
Tests for data_loader module
"""

import numpy as np

from iris_sklearn_svc.data_loader import get_data


class TestGetData:
    """Tests for get_data function"""

    def test_get_data_returns_four_arrays(self):
        """データロードが4つのndarrayを返すことを確認"""
        x_train, x_test, y_train, y_test = get_data(test_size=0.3, random_state=42)

        assert isinstance(x_train, np.ndarray)
        assert isinstance(x_test, np.ndarray)
        assert isinstance(y_train, np.ndarray)
        assert isinstance(y_test, np.ndarray)

    def test_train_test_split_ratio(self):
        """train/testの分割比率が正しいことを確認"""
        test_size = 0.3
        x_train, x_test, y_train, y_test = get_data(test_size=test_size, random_state=42)

        total_samples = len(x_train) + len(x_test)
        actual_test_ratio = len(x_test) / total_samples

        # 150個のデータなので、0.3なら45個がtest（誤差±1）
        assert abs(actual_test_ratio - test_size) < 0.02

    def test_data_shapes(self):
        """データの形状が正しいことを確認"""
        x_train, x_test, y_train, y_test = get_data(test_size=0.3, random_state=42)

        # Irisデータセットは4次元特徴量
        assert x_train.shape[1] == 4
        assert x_test.shape[1] == 4

        # y は1次元
        assert y_train.ndim == 1
        assert y_test.ndim == 1

        # x と y のサンプル数は一致
        assert len(x_train) == len(y_train)
        assert len(x_test) == len(y_test)

    def test_data_types(self):
        """データ型がfloat32であることを確認"""
        x_train, x_test, y_train, y_test = get_data(test_size=0.3, random_state=42)

        assert x_train.dtype == np.float32
        assert x_test.dtype == np.float32
        assert y_train.dtype == np.float32
        assert y_test.dtype == np.float32

    def test_reproducibility(self):
        """同じrandom_stateで同じ結果が得られることを確認"""
        x_train1, x_test1, y_train1, y_test1 = get_data(test_size=0.3, random_state=42)
        x_train2, x_test2, y_train2, y_test2 = get_data(test_size=0.3, random_state=42)

        np.testing.assert_array_equal(x_train1, x_train2)
        np.testing.assert_array_equal(x_test1, x_test2)
        np.testing.assert_array_equal(y_train1, y_train2)
        np.testing.assert_array_equal(y_test1, y_test2)

    def test_different_test_size(self):
        """異なるtest_sizeが正しく適用されることを確認"""
        x_train1, x_test1, _, _ = get_data(test_size=0.2, random_state=42)
        x_train2, x_test2, _, _ = get_data(test_size=0.4, random_state=42)

        # test_sizeが大きいほどtestデータが多い
        assert len(x_test1) < len(x_test2)
        assert len(x_train1) > len(x_train2)

    def test_class_labels(self):
        """クラスラベルが0, 1, 2であることを確認"""
        _, _, y_train, y_test = get_data(test_size=0.3, random_state=42)

        all_labels = np.concatenate([y_train, y_test])
        unique_labels = np.unique(all_labels)

        # Irisデータセットは3クラス（0, 1, 2）
        assert len(unique_labels) == 3
        assert set(unique_labels) == {0.0, 1.0, 2.0}
