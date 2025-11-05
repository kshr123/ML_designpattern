"""
CIFAR-10 CNN学習のメインスクリプト。

このスクリプトはCIFAR-10データセットでCNNモデルを学習し、
MLflowで実験を管理し、ONNXモデルをエクスポートします。
"""

import os

import mlflow
import torch

from cifar10_cnn.data_loader import load_cifar10_data
from cifar10_cnn.mlflow_manager import log_metrics, log_model, log_params
from cifar10_cnn.model import create_simple_cnn
from cifar10_cnn.onnx_exporter import export_to_onnx, validate_onnx_model
from cifar10_cnn.trainer import train_model


def main() -> None:
    """
    CIFAR-10 CNN学習のメインパイプライン。

    手順:
        1. データ読み込み
        2. モデル作成
        3. モデル学習
        4. ONNXエクスポート
        5. MLflow記録
    """
    print("=" * 80)
    print("CIFAR-10 CNN 学習パイプライン")
    print("=" * 80)
    print()

    # ハイパーパラメータ
    batch_size = 32
    epochs = 5
    learning_rate = 0.001

    # デバイス設定（GPU利用可能なら自動的に使用）
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用デバイス: {device}")
    print()

    # [1/5] データ読み込み
    print("[1/5] データを読み込み中...")
    train_loader, test_loader = load_cifar10_data(batch_size=batch_size)
    print(f"  ✓ 学習データ: {len(train_loader.dataset)} サンプル")
    print(f"  ✓ テストデータ: {len(test_loader.dataset)} サンプル")
    print()

    # [2/5] モデル作成
    print("[2/5] モデルを作成中...")
    model = create_simple_cnn()
    print("  ✓ モデル: SimpleCNN")
    print(f"  ✓ パラメータ数: {sum(p.numel() for p in model.parameters()):,}")
    print()

    # [3/5] モデル学習
    print("[3/5] モデルを学習中...")
    print(f"  エポック数: {epochs}")
    print(f"  バッチサイズ: {batch_size}")
    print(f"  学習率: {learning_rate}")
    print()

    metrics = train_model(
        model,
        train_loader,
        test_loader,
        epochs=epochs,
        learning_rate=learning_rate,
        device=device,
    )

    test_loss = metrics["test_loss"]
    test_accuracy = metrics["test_accuracy"]

    print()
    print(f"  ✓ テスト損失: {test_loss:.4f}")
    print(f"  ✓ テスト精度: {test_accuracy:.2f}%")
    print()

    # [4/5] ONNXエクスポート
    print("[4/5] ONNXモデルをエクスポート中...")
    os.makedirs("models", exist_ok=True)
    onnx_path = "models/cifar10_cnn.onnx"

    export_to_onnx(model, onnx_path)
    print(f"  ✓ ONNXモデル作成: {onnx_path}")

    # ONNX検証
    test_input = torch.randn(4, 3, 32, 32)
    is_valid = validate_onnx_model(model, onnx_path, test_input)

    if is_valid:
        print("  ✓ ONNX検証: 成功")
    else:
        print("  ✗ ONNX検証: 失敗")
    print()

    # [5/5] MLflow記録
    print("[5/5] MLflowに記録中...")

    mlflow.set_experiment("cifar10_cnn")

    with mlflow.start_run():
        # パラメータを記録
        params = {
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "optimizer": "Adam",
            "model": "SimpleCNN",
            "device": device,
        }
        log_params(params)

        # メトリクスを記録
        log_metrics(metrics)

        # モデルを記録
        log_model(model, artifact_path="model")

        # ONNXモデルも記録
        mlflow.log_artifact(onnx_path, artifact_path="onnx")

        print("  ✓ パラメータとメトリクスを記録")
        print("  ✓ モデルとONNXを記録")

    print()
    print("=" * 80)
    print("✅ 学習パイプライン完了")
    print("=" * 80)
    print()
    print("📊 結果サマリー:")
    print(f"  - テスト精度: {test_accuracy:.2f}%")
    print(f"  - テスト損失: {test_loss:.4f}")
    print(f"  - ONNXモデル: {onnx_path}")
    print("  - MLflow実験: cifar10_cnn")
    print()


if __name__ == "__main__":
    main()
