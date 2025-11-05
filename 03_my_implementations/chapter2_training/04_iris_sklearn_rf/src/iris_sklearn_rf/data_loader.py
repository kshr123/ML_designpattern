"""
Data loading module for Iris dataset.

This module provides functions to load the Iris dataset and split it into
training and testing sets.
"""

from typing import Tuple

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split


def load_iris_data() -> Tuple[np.ndarray, np.ndarray]:
    """
    Load the Iris dataset.

    Returns:
        Tuple[np.ndarray, np.ndarray]: A tuple of (X, y) where:
            - X: Feature matrix of shape (150, 4)
            - y: Target vector of shape (150,) with 3 classes (0, 1, 2)
    """
    iris = load_iris()
    X = iris.data
    y = iris.target
    return X, y


def split_data(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: int = 42,
    stratify: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split data into training and testing sets.

    Args:
        X: Feature matrix
        y: Target vector
        test_size: Proportion of the dataset to include in the test split
        random_state: Random state for reproducibility
        stratify: If True, stratify the split to maintain class distribution

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
            X_train, X_test, y_train, y_test
    """
    stratify_param = y if stratify else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify_param
    )

    return X_train, X_test, y_train, y_test
