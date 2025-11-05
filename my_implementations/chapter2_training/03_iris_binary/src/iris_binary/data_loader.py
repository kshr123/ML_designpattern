"""Data Loader - データ読み込みと二値化"""

from enum import Enum
from typing import Tuple

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split


class IrisTarget(Enum):
    """Irisのターゲットクラス"""

    SETOSA = 0
    VERSICOLOR = 1
    VIRGINICA = 2


def load_and_transform_data(
    test_size: float = 0.3,
    target_iris: IrisTarget = IrisTarget.SETOSA,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Irisデータセットを読み込み、二値分類用に変換する

    Args:
        test_size: テストデータの割合
        target_iris: 陽性とするクラス
        random_state: 乱数シード

    Returns:
        X_train, X_test, y_train, y_test
    """
    # データ読み込み
    iris = load_iris()
    X = iris.data
    y = iris.target

    # 二値化: target_irisを0（陽性）、その他を1（陰性）に変換
    pos_index = np.where(y == target_iris.value)
    neg_index = np.where(y != target_iris.value)
    y[pos_index] = 0
    y[neg_index] = 1

    # train/test分割
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, shuffle=True
    )

    # float32に変換
    X_train = np.array(X_train).astype("float32")
    X_test = np.array(X_test).astype("float32")
    y_train = np.array(y_train).astype("float32")
    y_test = np.array(y_test).astype("float32")

    return X_train, X_test, y_train, y_test
