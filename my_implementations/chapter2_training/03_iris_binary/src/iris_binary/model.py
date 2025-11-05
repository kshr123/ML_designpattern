"""Model Builder - SVCパイプラインの構築"""

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def build_svc_pipeline() -> Pipeline:
    """
    StandardScaler + SVC のパイプラインを構築する

    Returns:
        Pipeline: scikit-learnパイプライン
    """
    steps = [
        ("scaler", StandardScaler()),
        ("svc", SVC(probability=True)),
    ]

    pipeline = Pipeline(steps=steps)

    return pipeline
