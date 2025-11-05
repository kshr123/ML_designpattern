"""Trainer - モデルの学習と評価"""

from typing import Dict

import numpy as np
from sklearn import metrics
from sklearn.pipeline import Pipeline


def train_model(model: Pipeline, X_train: np.ndarray, y_train: np.ndarray) -> None:
    """
    モデルを学習する

    Args:
        model: scikit-learnパイプライン
        X_train: 訓練データ（特徴量）
        y_train: 訓練データ（ラベル）
    """
    model.fit(X_train, y_train)


def evaluate_model(model: Pipeline, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
    """
    モデルを評価する

    Args:
        model: 学習済みモデル
        X_test: テストデータ（特徴量）
        y_test: テストデータ（ラベル）

    Returns:
        評価指標の辞書
    """
    predictions = model.predict(X_test)

    accuracy = metrics.accuracy_score(y_test, predictions)
    precision = metrics.precision_score(y_test, predictions, average="micro")
    recall = metrics.recall_score(y_test, predictions, average="micro")

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
    }
