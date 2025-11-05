"""
Main training script for Iris Random Forest classification.

This script performs the complete training pipeline:
1. Load and split data
2. Train Random Forest model
3. Evaluate model performance
4. Log experiment to MLflow
5. Export model to ONNX format
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
    """Run the complete training pipeline."""
    # Set random seed for reproducibility
    random_state = 42

    # Hyperparameters
    n_estimators = 100
    max_depth = None  # Unlimited depth
    test_size = 0.2

    print("=" * 80)
    print("Iris Random Forest Classification - Training Pipeline")
    print("=" * 80)

    # 1. Load and split data
    print("\n[1/5] Loading data...")
    X, y = load_iris_data()
    print(f"  - Dataset shape: {X.shape}")
    print(f"  - Number of classes: {len(set(y))}")

    X_train, X_test, y_train, y_test = split_data(
        X, y, test_size=test_size, random_state=random_state, stratify=True
    )
    print(f"  - Train set: {X_train.shape[0]} samples")
    print(f"  - Test set: {X_test.shape[0]} samples")

    # 2. Create and train model
    print("\n[2/5] Training model...")
    pipeline = create_rf_pipeline(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state
    )
    fitted_pipeline = train_model(pipeline, X_train, y_train)
    print(f"  - Model: RandomForestClassifier")
    print(f"  - n_estimators: {n_estimators}")
    print(f"  - max_depth: {max_depth}")

    # 3. Evaluate model
    print("\n[3/5] Evaluating model...")
    metrics = evaluate_model(fitted_pipeline, X_test, y_test)
    print("  - Metrics:")
    for metric_name, metric_value in metrics.items():
        print(f"    - {metric_name}: {metric_value:.4f}")

    # 4. Log to MLflow
    print("\n[4/5] Logging to MLflow...")
    experiment_name = "iris_random_forest"
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth if max_depth is not None else "None")
        mlflow.log_param("random_state", random_state)
        mlflow.log_param("test_size", test_size)

        # Log metrics
        for metric_name, metric_value in metrics.items():
            mlflow.log_metric(metric_name, metric_value)

        # Log model
        mlflow.sklearn.log_model(fitted_pipeline, "model")

        # Get run ID for reference
        run_id = mlflow.active_run().info.run_id
        print(f"  - MLflow run ID: {run_id}")
        print(f"  - Experiment: {experiment_name}")

    # 5. Export to ONNX
    print("\n[5/5] Exporting to ONNX...")
    onnx_dir = Path("models")
    onnx_dir.mkdir(exist_ok=True)
    onnx_path = onnx_dir / "iris_rf.onnx"

    export_to_onnx(fitted_pipeline, str(onnx_path))
    print(f"  - ONNX model saved to: {onnx_path}")

    # Validate ONNX model
    is_valid = validate_onnx_model(fitted_pipeline, str(onnx_path), X_test)
    if is_valid:
        print("  - ONNX validation: ✓ PASSED")
    else:
        print("  - ONNX validation: ✗ FAILED")

    print("\n" + "=" * 80)
    print("Training pipeline completed successfully!")
    print("=" * 80)
    print(f"\nTo view results in MLflow UI, run:")
    print(f"  mlflow ui --backend-store-uri ./mlruns")


if __name__ == "__main__":
    main()
