"""
Model definition module for Random Forest classifier.

This module provides functions to create a scikit-learn Pipeline with
StandardScaler and RandomForestClassifier.
"""

from typing import Optional

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def create_rf_pipeline(
    n_estimators: int = 100,
    max_depth: Optional[int] = None,
    min_samples_split: int = 2,
    min_samples_leaf: int = 1,
    random_state: int = 42,
) -> Pipeline:
    """
    Create a Random Forest classification pipeline.

    The pipeline consists of:
    1. StandardScaler: Normalize features to mean=0, std=1
    2. RandomForestClassifier: Ensemble classifier

    Args:
        n_estimators: Number of trees in the forest
        max_depth: Maximum depth of trees (None for unlimited)
        min_samples_split: Minimum samples required to split an internal node
        min_samples_leaf: Minimum samples required to be at a leaf node
        random_state: Random state for reproducibility

    Returns:
        Pipeline: A scikit-learn Pipeline object
    """
    # Create the scaler
    scaler = StandardScaler()

    # Create the classifier
    classifier = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
    )

    # Create the pipeline
    pipeline = Pipeline([("scaler", scaler), ("classifier", classifier)])

    return pipeline
