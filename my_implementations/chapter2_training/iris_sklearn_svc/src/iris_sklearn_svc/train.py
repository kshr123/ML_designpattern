"""
Main training script with MLflow integration
"""

import argparse

import mlflow

from iris_sklearn_svc.data_loader import get_data
from iris_sklearn_svc.evaluator import evaluate_model
from iris_sklearn_svc.exporter import export_to_onnx
from iris_sklearn_svc.model import build_pipeline
from iris_sklearn_svc.trainer import train_model


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(description="Train Iris SVM classifier with MLflow tracking")
    parser.add_argument(
        "--test_size",
        type=float,
        default=0.3,
        help="Test data ratio (0.0-1.0). Default: 0.3",
    )
    parser.add_argument(
        "--random_state",
        type=int,
        default=42,
        help="Random seed for reproducibility. Default: 42",
    )
    parser.add_argument(
        "--mlflow_experiment_name",
        type=str,
        default="iris_svc",
        help="MLflow experiment name. Default: iris_svc",
    )
    return parser.parse_args()


def main() -> None:
    """メイン処理"""
    # コマンドライン引数を解析
    args = parse_args()

    # MLflow実験の設定
    mlflow.set_experiment(args.mlflow_experiment_name)

    # MLflowランの開始
    with mlflow.start_run():
        # パラメータをログ
        mlflow.log_param("test_size", args.test_size)
        mlflow.log_param("random_state", args.random_state)

        # 1. データ読み込み
        print("📊 Loading Iris dataset...")
        x_train, x_test, y_train, y_test = get_data(
            test_size=args.test_size, random_state=args.random_state
        )
        print(f"  Train samples: {len(x_train)}, Test samples: {len(x_test)}")

        # 2. モデル構築
        print("🏗️  Building pipeline...")
        pipeline = build_pipeline()
        print("  Pipeline: StandardScaler -> SVC(kernel='rbf', probability=True)")

        # 3. モデル学習
        print("🎓 Training model...")
        trained_model = train_model(pipeline, x_train, y_train)
        print("  Training completed!")

        # 4. モデル評価
        print("📈 Evaluating model...")
        metrics = evaluate_model(trained_model, x_test, y_test)
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")

        # メトリクスをMLflowにログ
        mlflow.log_metric("accuracy", metrics["accuracy"])
        mlflow.log_metric("precision", metrics["precision"])
        mlflow.log_metric("recall", metrics["recall"])

        # 5. モデルエクスポート（ONNX）
        print("💾 Exporting model to ONNX...")
        output_path = "model.onnx"
        export_to_onnx(trained_model, output_path)
        print(f"  Model saved to: {output_path}")

        # ONNXモデルをMLflowにログ
        mlflow.log_artifact(output_path)

        # scikit-learnモデルもMLflowに保存
        mlflow.sklearn.log_model(trained_model, "model")

        print("\n✅ Training pipeline completed successfully!")
        active_run = mlflow.active_run()
        if active_run:
            print(f"📊 MLflow Run ID: {active_run.info.run_id}")


if __name__ == "__main__":
    main()
