"""
Model definition module for Iris classification
"""

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def build_pipeline() -> Pipeline:
    """
    scikit-learn パイプラインを構築

    パイプラインは以下の2ステップで構成される:
    1. StandardScaler: 特徴量の標準化
    2. SVC: サポートベクターマシン分類器（RBFカーネル、確率出力有効）

    Returns:
        Pipeline: 学習可能なscikit-learnパイプライン
    """
    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("svc", SVC(kernel="rbf", probability=True, random_state=42)),
        ]
    )

    return pipeline
