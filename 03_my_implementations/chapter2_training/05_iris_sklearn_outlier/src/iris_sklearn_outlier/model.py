"""
One-Class SVM外れ値検出モデルの定義モジュール。

このモジュールはStandardScalerとOneClassSVMを
組み合わせたscikit-learn Pipelineを作成する機能を提供します。
"""

from typing import Union

from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]
from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]
from sklearn.svm import OneClassSVM  # type: ignore[import-untyped]


def create_ocs_pipeline(
    nu: float = 0.1,
    gamma: Union[str, float] = "auto",
    kernel: str = "rbf",
) -> Pipeline:
    """
    One-Class SVM外れ値検出パイプラインを作成する。

    パイプラインの構成:
    1. StandardScaler: 特徴量を平均0、分散1に正規化
    2. OneClassSVM: 外れ値検出（教師なし学習）

    Args:
        nu: 外れ値の上限割合（0 < nu <= 1）
            - 小さいほど外れ値が少なくなる
            - デフォルト: 0.1 (約10%を外れ値として許容)
        gamma: RBFカーネルのパラメータ
            - "auto": 1/n_features を使用
            - float: カスタム値を指定
            - デフォルト: "auto"
        kernel: カーネル関数
            - "rbf": 放射基底関数カーネル（非線形）
            - "linear": 線形カーネル
            - "poly": 多項式カーネル
            - "sigmoid": シグモイドカーネル
            - デフォルト: "rbf"

    Returns:
        Pipeline: StandardScaler + OneClassSVM のパイプライン

    Examples:
        >>> # デフォルトパラメータでパイプライン作成
        >>> pipeline = create_ocs_pipeline()
        >>> pipeline.named_steps["ocs"].nu
        0.1

        >>> # カスタムパラメータでパイプライン作成
        >>> pipeline = create_ocs_pipeline(nu=0.2, gamma=0.001, kernel="linear")
        >>> pipeline.named_steps["ocs"].nu
        0.2

    Notes:
        - nuパラメータは外れ値の割合を制御する重要なハイパーパラメータ
        - 正常データのみで学習し、境界外のデータを外れ値として検出
        - 予測結果: +1（正常）、-1（外れ値）
    """
    steps = [
        ("scaler", StandardScaler()),
        ("ocs", OneClassSVM(nu=nu, gamma=gamma, kernel=kernel)),
    ]
    pipeline = Pipeline(steps=steps)
    return pipeline
