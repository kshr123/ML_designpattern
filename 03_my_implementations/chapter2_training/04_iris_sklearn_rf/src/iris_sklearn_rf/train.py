"""
Irisランダムフォレスト分類のメイン学習スクリプト。

このスクリプトは以下の完全な学習パイプラインを実行します:
1. データの読み込みと分割
2. ランダムフォレストモデルの学習
3. モデル性能の評価
4. MLflowへの実験記録
5. モデルのONNX形式へのエクスポート
"""

import os
from pathlib import Path

import mlflow
import mlflow.sklearn

from iris_sklearn_rf.data_loader import load_iris_data, split_data
from iris_sklearn_rf.model import create_rf_pipeline
from iris_sklearn_rf.onnx_exporter import export_to_onnx, validate_onnx_model
from iris_sklearn_rf.trainer import evaluate_model, train_model


def main() -> None:
    """完全な学習パイプラインを実行する。"""
    # 再現性のための乱数シード設定
    random_state = 42

    # ハイパーパラメータ
    n_estimators = 100
    max_depth = None  # 深さ無制限
    test_size = 0.2

    print("=" * 80)
    print("Iris Random Forest Classification - Training Pipeline")
    print("=" * 80)

    # 1. データの読み込みと分割
    print("\n[1/5] データを読み込み中...")
    X, y = load_iris_data()
    print(f"  - データセット形状: {X.shape}")
    print(f"  - クラス数: {len(set(y))}")

    X_train, X_test, y_train, y_test = split_data(
        X, y, test_size=test_size, random_state=random_state, stratify=True
    )
    print(f"  - 訓練セット: {X_train.shape[0]} サンプル")
    print(f"  - テストセット: {X_test.shape[0]} サンプル")

    # 2. モデルの作成と学習
    print("\n[2/5] モデルを学習中...")
    pipeline = create_rf_pipeline(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state
    )
    fitted_pipeline = train_model(pipeline, X_train, y_train)
    print(f"  - モデル: RandomForestClassifier")
    print(f"  - n_estimators: {n_estimators}")
    print(f"  - max_depth: {max_depth}")

    # 3. モデルの評価
    print("\n[3/5] モデルを評価中...")
    metrics = evaluate_model(fitted_pipeline, X_test, y_test)
    print("  - メトリクス:")
    for metric_name, metric_value in metrics.items():
        print(f"    - {metric_name}: {metric_value:.4f}")

    # 4. MLflowへのログ記録
    print("\n[4/5] MLflowにログ記録中...")
    experiment_name = "iris_random_forest"
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run():
        # パラメータの記録
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth if max_depth is not None else "None")
        mlflow.log_param("random_state", random_state)
        mlflow.log_param("test_size", test_size)

        # メトリクスの記録
        for metric_name, metric_value in metrics.items():
            mlflow.log_metric(metric_name, metric_value)

        # モデルの記録
        mlflow.sklearn.log_model(fitted_pipeline, "model")

        # 参照用にRun IDを取得
        run_id = mlflow.active_run().info.run_id
        print(f"  - MLflow run ID: {run_id}")
        print(f"  - 実験名: {experiment_name}")

    # 5. ONNXへのエクスポート
    print("\n[5/5] ONNXにエクスポート中...")
    onnx_dir = Path("models")
    onnx_dir.mkdir(exist_ok=True)
    onnx_path = onnx_dir / "iris_rf.onnx"

    export_to_onnx(fitted_pipeline, str(onnx_path))
    print(f"  - ONNXモデル保存先: {onnx_path}")

    # ONNXモデルの検証
    is_valid = validate_onnx_model(fitted_pipeline, str(onnx_path), X_test)
    if is_valid:
        print("  - ONNX検証: ✓ 成功")
    else:
        print("  - ONNX検証: ✗ 失敗")

    print("\n" + "=" * 80)
    print("学習パイプラインが正常に完了しました！")
    print("=" * 80)
    print(f"\nMLflow UIで結果を確認するには、以下を実行:")
    print(f"  mlflow ui --backend-store-uri ./mlruns")


if __name__ == "__main__":
    main()
