"""
モデルの学習と評価モジュール。

このモジュールは機械学習モデルの学習と評価を行う機能を提供します。
"""

from typing import Dict

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline


def train_model(pipeline: Pipeline, X_train: np.ndarray, y_train: np.ndarray) -> Pipeline:
    """
    モデルパイプラインを学習する。

    Args:
        pipeline: 学習するscikit-learn Pipeline
        X_train: 訓練用特徴量行列
        y_train: 訓練用ターゲットベクトル

    Returns:
        Pipeline: 学習済みパイプライン
    """
    pipeline.fit(X_train, y_train)
    return pipeline


def evaluate_model(pipeline: Pipeline, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
    """
    学習済みモデルを評価する。

    Args:
        pipeline: 学習済みscikit-learn Pipeline
        X_test: テスト用特徴量行列
        y_test: テスト用ターゲットベクトル

    Returns:
        Dict[str, float]: 評価メトリクスの辞書:
            - accuracy: 全体の正解率
            - f1_score_macro: マクロ平均F1スコア
            - f1_score_weighted: 重み付きF1スコア
            - precision_macro: マクロ平均適合率
            - recall_macro: マクロ平均再現率
    """
    # 予測の実行
    y_pred = pipeline.predict(X_test)

    # メトリクスの計算
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_score_macro": f1_score(y_test, y_pred, average="macro"),
        "f1_score_weighted": f1_score(y_test, y_pred, average="weighted"),
        "precision_macro": precision_score(y_test, y_pred, average="macro"),
        "recall_macro": recall_score(y_test, y_pred, average="macro"),
    }

    return metrics
