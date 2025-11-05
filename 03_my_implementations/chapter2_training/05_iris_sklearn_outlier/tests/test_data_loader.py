"""
data_loaderモジュールのユニットテスト。

Irisデータセットの読み込み機能をテストします。
"""

import numpy as np

from iris_sklearn_outlier.data_loader import load_iris_data


class TestLoadIrisData:
    """Test cases for load_iris_data function."""

    def test_load_iris_data_returns_ndarray(self) -> None:
        """Test that load_iris_data returns a numpy array."""
        X = load_iris_data()

        assert isinstance(X, np.ndarray), "Should return a numpy array"

    def test_load_iris_data_shape(self) -> None:
        """Test that Iris data has correct shape (150, 4)."""
        X = load_iris_data()

        assert X.shape == (150, 4), f"Expected shape (150, 4), got {X.shape}"

    def test_load_iris_data_dtype(self) -> None:
        """Test that data is float32 type."""
        X = load_iris_data()

        assert X.dtype == np.float32, f"Expected float32, got {X.dtype}"

    def test_load_iris_data_no_nan(self) -> None:
        """Test that data contains no NaN values."""
        X = load_iris_data()

        assert not np.isnan(X).any(), "Data should not contain NaN values"

    def test_load_iris_data_positive_values(self) -> None:
        """Test that all values are positive (Iris characteristics)."""
        X = load_iris_data()

        assert np.all(X >= 0), "All values should be non-negative"

    def test_load_iris_data_consistency(self) -> None:
        """Test that multiple calls return the same data."""
        X1 = load_iris_data()
        X2 = load_iris_data()

        np.testing.assert_array_equal(X1, X2, err_msg="Data should be consistent")
