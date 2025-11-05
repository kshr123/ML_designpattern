"""
モデルの学習と評価モジュール。

このモジュールはOne-Class SVMモデルの学習と外れ値率の評価を行う機能を提供します。
"""

import numpy as np
from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]


def train_model(pipeline: Pipeline, X: np.ndarray) -> Pipeline:
    """
    One-Class SVMモデルを学習する。

    教師なし学習のため、ラベルyは不要。
    全データを正常データとして学習し、その分布の境界を学習する。

    Args:
        pipeline: 未学習のscikit-learn Pipeline
        X: 学習用特徴量行列 (n_samples, n_features)

    Returns:
        Pipeline: 学習済みパイプライン

    Examples:
        >>> from iris_sklearn_outlier.data_loader import load_iris_data
        >>> from iris_sklearn_outlier.model import create_ocs_pipeline
        >>> X = load_iris_data()
        >>> pipeline = create_ocs_pipeline()
        >>> fitted_pipeline = train_model(pipeline, X)
        >>> hasattr(fitted_pipeline.named_steps["ocs"], "support_")
        True

    Notes:
        - fit(X)のみを呼び出す（yは不要）
        - 学習後、モデルはサポートベクターを保持する
        - 予測時は決定境界を基準に正常/外れ値を判定
    """
    pipeline.fit(X)
    return pipeline


def evaluate_model(pipeline: Pipeline, X: np.ndarray) -> float:
    """
    学習済みモデルを評価し、外れ値率を算出する。

    外れ値率 = (外れ値と判定されたサンプル数) / (全サンプル数)

    Args:
        pipeline: 学習済みscikit-learn Pipeline
        X: 評価用特徴量行列 (n_samples, n_features)

    Returns:
        float: 外れ値率（0.0 ~ 1.0）
            - 0.0: 全てのサンプルが正常
            - 1.0: 全てのサンプルが外れ値

    Examples:
        >>> from iris_sklearn_outlier.data_loader import load_iris_data
        >>> from iris_sklearn_outlier.model import create_ocs_pipeline
        >>> X = load_iris_data()
        >>> pipeline = create_ocs_pipeline(nu=0.1)
        >>> fitted_pipeline = train_model(pipeline, X)
        >>> outlier_rate = evaluate_model(fitted_pipeline, X)
        >>> 0.0 <= outlier_rate <= 0.2  # nu=0.1なので約10%前後
        True

    Notes:
        - 予測結果: +1（正常）、-1（外れ値）
        - 外れ値率はnuパラメータに大きく影響される
        - 学習データで評価すると、nuに近い値になることが期待される
    """
    predictions = pipeline.predict(X)
    n_outliers = sum(1 for pred in predictions if pred == -1)
    outlier_rate = n_outliers / len(X)
    return float(outlier_rate)
