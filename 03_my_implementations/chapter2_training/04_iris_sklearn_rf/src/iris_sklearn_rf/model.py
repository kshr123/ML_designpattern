"""
ランダムフォレスト分類器のモデル定義モジュール。

このモジュールはStandardScalerとRandomForestClassifierを
組み合わせたscikit-learn Pipelineを作成する機能を提供します。
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
    ランダムフォレスト分類パイプラインを作成する。

    パイプラインの構成:
    1. StandardScaler: 特徴量を平均0、分散1に正規化
    2. RandomForestClassifier: アンサンブル分類器

    Args:
        n_estimators: フォレスト内の決定木の数
        max_depth: 木の最大深さ（Noneで無制限）
        min_samples_split: 内部ノード分割に必要な最小サンプル数
        min_samples_leaf: 葉ノードに必要な最小サンプル数
        random_state: 再現性のための乱数シード

    Returns:
        Pipeline: scikit-learn Pipelineオブジェクト
    """
    # スケーラーの作成
    scaler = StandardScaler()

    # 分類器の作成
    classifier = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
    )

    # パイプラインの作成
    pipeline = Pipeline([("scaler", scaler), ("classifier", classifier)])

    return pipeline
