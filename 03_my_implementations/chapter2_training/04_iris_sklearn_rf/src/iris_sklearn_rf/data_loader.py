"""
Irisデータセットの読み込みモジュール。

このモジュールはIrisデータセットの読み込みと、
訓練/テストセットへの分割機能を提供します。
"""

from typing import Tuple

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split


def load_iris_data() -> Tuple[np.ndarray, np.ndarray]:
    """
    Irisデータセットを読み込む。

    Returns:
        Tuple[np.ndarray, np.ndarray]: (X, y)のタプル
            - X: 特徴量行列 (150, 4)
            - y: ターゲットベクトル (150,) - 3クラス (0, 1, 2)
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
    データを訓練セットとテストセットに分割する。

    Args:
        X: 特徴量行列
        y: ターゲットベクトル
        test_size: テストセットの割合
        random_state: 再現性のための乱数シード
        stratify: Trueの場合、クラス分布を維持して分割

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
            X_train, X_test, y_train, y_test
    """
    stratify_param = y if stratify else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify_param
    )

    return X_train, X_test, y_train, y_test
