"""
Unit tests for data_loader module.

Tests the data loading and splitting functionality for the Iris dataset.
"""

import numpy as np

from iris_sklearn_rf.data_loader import load_iris_data, split_data


class TestLoadIrisData:
    """Test cases for load_iris_data function."""

    def test_load_iris_data_returns_correct_shape(self) -> None:
        """Test that load_iris_data returns data with correct shape."""
        X, y = load_iris_data()

        assert X.shape == (150, 4), "X should have shape (150, 4)"
        assert y.shape == (150,), "y should have shape (150,)"

    def test_load_iris_data_returns_correct_types(self) -> None:
        """Test that load_iris_data returns correct data types."""
        X, y = load_iris_data()

        assert isinstance(X, np.ndarray), "X should be numpy array"
        assert isinstance(y, np.ndarray), "y should be numpy array"

    def test_load_iris_data_has_three_classes(self) -> None:
        """Test that the dataset has exactly 3 classes."""
        X, y = load_iris_data()

        unique_classes = np.unique(y)
        assert len(unique_classes) == 3, "Should have 3 unique classes"
        assert set(unique_classes) == {0, 1, 2}, "Classes should be 0, 1, 2"

    def test_load_iris_data_feature_range(self) -> None:
        """Test that features are within reasonable range."""
        X, y = load_iris_data()

        # Iris features should be positive and within reasonable range
        assert np.all(X >= 0), "All features should be non-negative"
        assert np.all(X < 10), "All features should be less than 10"


class TestSplitData:
    """Test cases for split_data function."""

    def test_split_data_returns_correct_shapes(self) -> None:
        """Test that split_data returns correct train/test split."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        # 80/20 split of 150 samples
        assert X_train.shape[0] == 120, "Training set should have 120 samples"
        assert X_test.shape[0] == 30, "Test set should have 30 samples"
        assert y_train.shape[0] == 120, "Training labels should have 120 samples"
        assert y_test.shape[0] == 30, "Test labels should have 30 samples"

    def test_split_data_preserves_features(self) -> None:
        """Test that split_data preserves number of features."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        assert X_train.shape[1] == 4, "Training features should have 4 dimensions"
        assert X_test.shape[1] == 4, "Test features should have 4 dimensions"

    def test_split_data_is_stratified(self) -> None:
        """Test that split_data maintains class distribution (stratified)."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(
            X, y, test_size=0.2, random_state=42, stratify=True
        )

        # Check that all classes are present in both train and test
        train_classes = set(np.unique(y_train))
        test_classes = set(np.unique(y_test))

        assert train_classes == {0, 1, 2}, "All classes should be in training set"
        assert test_classes == {0, 1, 2}, "All classes should be in test set"

        # Check approximate class balance
        for cls in [0, 1, 2]:
            train_ratio = np.sum(y_train == cls) / len(y_train)
            test_ratio = np.sum(y_test == cls) / len(y_test)
            # Both should be approximately 1/3
            assert 0.25 < train_ratio < 0.42, f"Class {cls} ratio in train should be ~1/3"
            assert 0.25 < test_ratio < 0.42, f"Class {cls} ratio in test should be ~1/3"

    def test_split_data_reproducibility(self) -> None:
        """Test that split_data with same random_state produces same split."""
        X, y = load_iris_data()

        X_train1, X_test1, y_train1, y_test1 = split_data(X, y, test_size=0.2, random_state=42)
        X_train2, X_test2, y_train2, y_test2 = split_data(X, y, test_size=0.2, random_state=42)

        np.testing.assert_array_equal(X_train1, X_train2, err_msg="Train X should be identical")
        np.testing.assert_array_equal(X_test1, X_test2, err_msg="Test X should be identical")
        np.testing.assert_array_equal(y_train1, y_train2, err_msg="Train y should be identical")
        np.testing.assert_array_equal(y_test1, y_test2, err_msg="Test y should be identical")

    def test_split_data_no_overlap(self) -> None:
        """Test that train and test sets don't overlap."""
        X, y = load_iris_data()
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

        # Check total samples
        total_samples = X_train.shape[0] + X_test.shape[0]
        assert total_samples == X.shape[0], "Train + test should equal total samples"
