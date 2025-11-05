"""
Iris外れ値検出のメイン学習スクリプト。

このスクリプトは以下の完全な学習パイプラインを実行します:
1. データの読み込み
2. One-Class SVMモデルの学習
3. 外れ値率の評価
4. MLflowへの実験記録
5. モデルのONNX形式へのエクスポート
"""

import os

import mlflow
import mlflow.sklearn

from iris_sklearn_outlier.data_loader import load_iris_data
from iris_sklearn_outlier.model import create_ocs_pipeline
from iris_sklearn_outlier.onnx_exporter import export_to_onnx, validate_onnx_model
from iris_sklearn_outlier.trainer import evaluate_model, train_model


def main() -> None:
    """完全な学習パイプラインを実行する。"""
    print("\n" + "=" * 80)
    print("Iris外れ値検出 学習パイプライン")
    print("=" * 80)

    # MLflow実験ID（環境変数から取得、デフォルトは0）
    mlflow_experiment_id = int(os.getenv("MLFLOW_EXPERIMENT_ID", 0))

    # ハイパーパラメータ
    nu = 0.1  # 外れ値の上限割合
    gamma = "auto"  # RBFカーネルパラメータ
    kernel = "rbf"  # カーネル関数

    # 1. データの読み込み
    print("\n[1/5] データを読み込み中...")
    X = load_iris_data()
    print(f"  ✓ データ形状: {X.shape}")
    print(f"  ✓ データ型: {X.dtype}")

    # 2. モデルの作成と学習
    print("\n[2/5] モデルを学習中...")
    pipeline = create_ocs_pipeline(nu=nu, gamma=gamma, kernel=kernel)
    fitted_pipeline = train_model(pipeline, X)
    n_support = len(fitted_pipeline.named_steps["ocs"].support_)
    print("  ✓ 学習完了")
    print(f"  ✓ サポートベクター数: {n_support}")

    # 3. モデルの評価
    print("\n[3/5] モデルを評価中...")
    outlier_rate = evaluate_model(fitted_pipeline, X)
    n_outliers = int(outlier_rate * len(X))
    n_inliers = len(X) - n_outliers
    print(f"  ✓ 外れ値率: {outlier_rate:.4f} ({n_outliers}/{len(X)} サンプル)")
    print(f"  ✓ 正常データ: {n_inliers} サンプル")

    # 4. MLflowへの実験記録
    print("\n[4/5] MLflowに記録中...")

    # パラメータの記録
    mlflow.log_param("normalize", "StandardScaler")
    mlflow.log_param("model", "one_class_svm")
    mlflow.log_param("nu", nu)
    mlflow.log_param("gamma", gamma)
    mlflow.log_param("kernel", kernel)

    # メトリクスの記録
    mlflow.log_metric("outlier_rate", outlier_rate)
    mlflow.log_metric("n_support_vectors", n_support)
    mlflow.log_metric("n_outliers", n_outliers)
    mlflow.log_metric("n_inliers", n_inliers)

    # モデルの記録
    mlflow.sklearn.log_model(fitted_pipeline, "model")
    print("  ✓ パラメータとメトリクスを記録")

    # 5. ONNXエクスポート
    print("\n[5/5] ONNXモデルをエクスポート中...")
    onnx_name = f"iris_ocs_{mlflow_experiment_id}.onnx"
    onnx_path = os.path.join("/tmp/", onnx_name)

    export_to_onnx(fitted_pipeline, onnx_path)
    print(f"  ✓ ONNXモデル作成: {onnx_path}")

    # ONNX検証
    is_valid = validate_onnx_model(fitted_pipeline, onnx_path, X[:10])
    print(f"  ✓ ONNX検証: {'成功' if is_valid else '失敗'}")

    # ONNXモデルをMLflowに記録
    mlflow.log_artifact(onnx_path)
    print("  ✓ ONNXモデルをMLflowに記録")

    # 完了
    print("\n" + "=" * 80)
    print("✅ 学習パイプライン完了")
    print("=" * 80)
    print("\n📊 結果サマリー:")
    print(f"  - 外れ値率: {outlier_rate:.4f}")
    print(f"  - サポートベクター数: {n_support}")
    print(f"  - MLflow実験ID: {mlflow_experiment_id}")
    print(f"  - ONNXモデル: {onnx_name}")
    print()


if __name__ == "__main__":
    main()
