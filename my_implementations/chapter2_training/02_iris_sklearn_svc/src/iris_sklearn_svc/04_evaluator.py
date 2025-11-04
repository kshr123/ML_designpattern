"""
Evaluator module for model evaluation
"""

from typing import Dict

import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.pipeline import Pipeline


def evaluate_model(
    trained_model: Pipeline, x_test: np.ndarray, y_test: np.ndarray
) -> Dict[str, float]:
    """
    学習済みモデルを評価

    Args:
        trained_model (Pipeline): 学習済みscikit-learnパイプライン
        x_test (np.ndarray): テスト用特徴量データ
        y_test (np.ndarray): テスト用ラベルデータ

    Returns:
        Dict[str, float]: 評価指標の辞書
            - accuracy: 正解率
            - precision: 適合率（マクロ平均）
            - recall: 再現率（マクロ平均）
    """
    # 予測
    y_pred = trained_model.predict(x_test)

    # 評価指標の計算
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="macro")
    recall = recall_score(y_test, y_pred, average="macro")

    # 結果を辞書で返す
    metrics = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
    }

    return metrics
