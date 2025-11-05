"""
Irisデータセットの読み込みモジュール。

このモジュールはIrisデータセットの読み込み機能を提供します。
外れ値検出（教師なし学習）のため、ラベルは使用せず特徴量のみを返します。
"""

import numpy as np
from sklearn.datasets import load_iris  # type: ignore[import-untyped]


def load_iris_data() -> np.ndarray:
    """
    Irisデータセットを読み込む。

    外れ値検出では全データを正常データとして扱うため、
    特徴量のみを返し、ラベルは返さない。

    Returns:
        np.ndarray: 特徴量行列 (150, 4) - float32型
            - 各行はサンプル
            - 各列は特徴量（sepal length, sepal width, petal length, petal width）

    Examples:
        >>> X = load_iris_data()
        >>> X.shape
        (150, 4)
        >>> X.dtype
        dtype('float32')
    """
    iris = load_iris()
    X = iris.data.astype(np.float32)
    return X  # type: ignore[no-any-return]
