"""
Data loader module for Iris dataset
"""

from typing import Tuple

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split


def get_data(
    test_size: float = 0.3, random_state: int = 42
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Irisデータセットを読み込み、train/testに分割

    Args:
        test_size (float): テストデータの割合（0.0-1.0）
        random_state (int): 乱数シード

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
            x_train, x_test, y_train, y_test
    """
    iris = load_iris()
    data = iris.data
    target = iris.target

    x_train, x_test, y_train, y_test = train_test_split(
        data, target, shuffle=True, test_size=test_size, random_state=random_state
    )

    # float32に変換
    x_train = np.array(x_train).astype("float32")
    y_train = np.array(y_train).astype("float32")
    x_test = np.array(x_test).astype("float32")
    y_test = np.array(y_test).astype("float32")

    return x_train, x_test, y_train, y_test
