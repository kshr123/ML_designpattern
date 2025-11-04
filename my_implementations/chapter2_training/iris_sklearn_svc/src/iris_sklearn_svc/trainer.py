"""
Trainer module for model training
"""

import numpy as np
from sklearn.pipeline import Pipeline


def train_model(pipeline: Pipeline, x_train: np.ndarray, y_train: np.ndarray) -> Pipeline:
    """
    パイプラインを学習

    Args:
        pipeline (Pipeline): 未学習のscikit-learnパイプライン
        x_train (np.ndarray): 学習用特徴量データ
        y_train (np.ndarray): 学習用ラベルデータ

    Returns:
        Pipeline: 学習済みパイプライン
    """
    # パイプライン全体を学習（StandardScaler + SVC）
    pipeline.fit(x_train, y_train)

    return pipeline
