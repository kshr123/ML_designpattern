"""MLflow Manager - MLflowでの実験管理"""

from typing import Dict, Optional

import mlflow
import mlflow.sklearn
from sklearn.pipeline import Pipeline

from iris_binary.data_loader import IrisTarget


def log_experiment(
    model: Pipeline,
    metrics: Dict[str, float],
    target_iris: IrisTarget,
    onnx_path: Optional[str] = None,
) -> str:
    """
    実験結果をMLflowに記録する

    Args:
        model: 学習済みモデル
        metrics: 評価指標
        target_iris: ターゲットクラス
        onnx_path: ONNXファイルのパス（Noneの場合はスキップ）

    Returns:
        Run ID
    """
    # パラメータの記録
    mlflow.log_param("normalize", "StandardScaler")
    mlflow.log_param("model", "svc")
    mlflow.log_param("target_iris", target_iris.name.lower())

    # メトリクスの記録
    mlflow.log_metric("accuracy", metrics["accuracy"])
    mlflow.log_metric("precision", metrics["precision"])
    mlflow.log_metric("recall", metrics["recall"])

    # モデルの記録
    mlflow.sklearn.log_model(model, artifact_path="model")

    # ONNXファイルの記録（オプション）
    if onnx_path is not None:
        mlflow.log_artifact(onnx_path)

    # Run IDを返す
    active_run = mlflow.active_run()
    if active_run is None:
        raise RuntimeError("No active MLflow run")
    return str(active_run.info.run_id)
