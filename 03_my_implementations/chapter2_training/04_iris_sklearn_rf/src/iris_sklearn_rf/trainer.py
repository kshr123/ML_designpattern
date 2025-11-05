"""
Model training and evaluation module.

This module provides functions to train and evaluate machine learning models.
"""

from typing import Dict

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline


def train_model(pipeline: Pipeline, X_train: np.ndarray, y_train: np.ndarray) -> Pipeline:
    """
    Train the model pipeline.

    Args:
        pipeline: Scikit-learn Pipeline to train
        X_train: Training feature matrix
        y_train: Training target vector

    Returns:
        Pipeline: Fitted pipeline
    """
    pipeline.fit(X_train, y_train)
    return pipeline


def evaluate_model(pipeline: Pipeline, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
    """
    Evaluate the trained model.

    Args:
        pipeline: Fitted scikit-learn Pipeline
        X_test: Test feature matrix
        y_test: Test target vector

    Returns:
        Dict[str, float]: Dictionary containing evaluation metrics:
            - accuracy: Overall accuracy
            - f1_score_macro: Macro-averaged F1 score
            - f1_score_weighted: Weighted F1 score
            - precision_macro: Macro-averaged precision
            - recall_macro: Macro-averaged recall
    """
    # Make predictions
    y_pred = pipeline.predict(X_test)

    # Calculate metrics
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_score_macro": f1_score(y_test, y_pred, average="macro"),
        "f1_score_weighted": f1_score(y_test, y_pred, average="weighted"),
        "precision_macro": precision_score(y_test, y_pred, average="macro"),
        "recall_macro": recall_score(y_test, y_pred, average="macro"),
    }

    return metrics
