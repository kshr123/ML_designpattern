"""MLflow実験の実行スクリプト"""

import os
import tempfile
from argparse import ArgumentParser

import mlflow

from iris_binary.data_loader import IrisTarget, load_and_transform_data
from iris_binary.exporter import export_to_onnx
from iris_binary.mlflow_manager import log_experiment
from iris_binary.model import build_svc_pipeline
from iris_binary.trainer import evaluate_model, train_model


def main():
    parser = ArgumentParser(description="Iris Binary Classification with MLflow")
    parser.add_argument(
        "--test_size",
        type=float,
        default=0.3,
        help="Test data ratio (default: 0.3)",
    )
    parser.add_argument(
        "--target_iris",
        type=str,
        choices=["setosa", "versicolor", "virginica"],
        default="setosa",
        help="Target iris class for positive label",
    )
    parser.add_argument(
        "--tracking_uri",
        type=str,
        default="./mlruns",
        help="MLflow tracking URI (default: ./mlruns)",
    )
    parser.add_argument(
        "--experiment_name",
        type=str,
        default="iris_binary_classification",
        help="MLflow experiment name",
    )
    args = parser.parse_args()

    # ターゲットクラスの変換
    if args.target_iris == "setosa":
        target_iris = IrisTarget.SETOSA
    elif args.target_iris == "versicolor":
        target_iris = IrisTarget.VERSICOLOR
    elif args.target_iris == "virginica":
        target_iris = IrisTarget.VIRGINICA
    else:
        raise ValueError(f"Invalid target_iris: {args.target_iris}")

    # MLflow設定
    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experiment_name)

    print(f"🚀 Starting experiment: {args.experiment_name}")
    print(f"📊 Target class: {args.target_iris}")
    print(f"📁 Tracking URI: {args.tracking_uri}")
    print()

    # データ読み込み
    print("📥 Loading data...")
    X_train, X_test, y_train, y_test = load_and_transform_data(
        test_size=args.test_size, target_iris=target_iris, random_state=42
    )
    print(f"   Train samples: {len(X_train)}, Test samples: {len(X_test)}")

    # モデル構築
    print("🏗️  Building model...")
    model = build_svc_pipeline()

    # 学習
    print("🎓 Training model...")
    train_model(model, X_train, y_train)

    # 評価
    print("📊 Evaluating model...")
    metrics = evaluate_model(model, X_test, y_test)
    print(f"   Accuracy:  {metrics['accuracy']:.4f}")
    print(f"   Precision: {metrics['precision']:.4f}")
    print(f"   Recall:    {metrics['recall']:.4f}")

    # ONNX変換
    print("🔄 Converting to ONNX...")
    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as f:
        onnx_path = f.name

    export_to_onnx(model, onnx_path)
    print(f"   ONNX saved: {onnx_path}")

    # MLflow記録
    print("📝 Logging to MLflow...")
    with mlflow.start_run():
        run_id = log_experiment(
            model=model, metrics=metrics, target_iris=target_iris, onnx_path=onnx_path
        )
        print(f"   Run ID: {run_id}")

    # 一時ファイルの削除
    os.unlink(onnx_path)

    print()
    print("✅ Experiment completed successfully!")
    print(f"🌐 View results: mlflow ui --port 5000")
    print(f"   Then open: http://localhost:5000")


if __name__ == "__main__":
    main()
