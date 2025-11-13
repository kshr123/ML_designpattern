#!/usr/bin/env python3
"""
Iris分類モデル作成スクリプト

TensorFlow/Kerasを使用してIris分類モデルを学習し、
TensorFlow Serving用のSavedModel形式でエクスポートします。

Usage:
    python build_model.py
"""

import argparse
import os
from typing import Tuple

import numpy as np
import tensorflow as tf
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def load_iris_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Irisデータセットを読み込んで訓練用とテスト用に分割する

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
            (X_train, X_test, y_train, y_test)
    """
    print("Loading Iris dataset...")
    iris = datasets.load_iris()
    X = iris.data.astype(np.float32)
    y = iris.target

    # 訓練データとテストデータに分割（80:20）
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")

    return X_train, X_test, y_train, y_test


def normalize_data(
    X_train: np.ndarray, X_test: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    データを正規化する（平均0、分散1）

    Args:
        X_train: 訓練データ
        X_test: テストデータ

    Returns:
        Tuple[np.ndarray, np.ndarray]: 正規化された (X_train, X_test)
    """
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled.astype(np.float32), X_test_scaled.astype(np.float32)


def build_model(input_shape: int, num_classes: int) -> tf.keras.Model:
    """
    TensorFlow/Kerasモデルを構築する

    Args:
        input_shape: 入力特徴量の次元数
        num_classes: クラス数

    Returns:
        tf.keras.Model: コンパイル済みモデル
    """
    print("Building model...")

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(input_shape,), name="input"),
        tf.keras.layers.Dense(64, activation="relu", name="dense1"),
        tf.keras.layers.Dropout(0.2, name="dropout1"),
        tf.keras.layers.Dense(32, activation="relu", name="dense2"),
        tf.keras.layers.Dropout(0.2, name="dropout2"),
        tf.keras.layers.Dense(num_classes, activation="softmax", name="output"),
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.summary()

    return model


def train_model(
    model: tf.keras.Model,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    epochs: int = 100,
    batch_size: int = 16,
) -> tf.keras.callbacks.History:
    """
    モデルを学習する

    Args:
        model: 学習対象のモデル
        X_train: 訓練データ
        y_train: 訓練ラベル
        X_test: テストデータ
        y_test: テストラベル
        epochs: エポック数
        batch_size: バッチサイズ

    Returns:
        tf.keras.callbacks.History: 学習履歴
    """
    print("Training model...")

    # Early Stoppingコールバック
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=10,
        restore_best_weights=True,
    )

    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_test, y_test),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[early_stopping],
        verbose=1,
    )

    return history


def evaluate_model(
    model: tf.keras.Model, X_test: np.ndarray, y_test: np.ndarray
) -> None:
    """
    モデルを評価する

    Args:
        model: 評価対象のモデル
        X_test: テストデータ
        y_test: テストラベル
    """
    print("\nEvaluating model...")
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Loss: {test_loss:.4f}")
    print(f"Test Accuracy: {test_accuracy:.4f}")


def export_model(model: tf.keras.Model, export_path: str) -> None:
    """
    モデルをSavedModel形式でエクスポートする

    TensorFlow Serving用のserving signatureを定義します。

    Args:
        model: エクスポート対象のモデル
        export_path: エクスポート先ディレクトリパス
    """
    print(f"\nExporting model to {export_path}...")

    # SavedModel形式でエクスポート
    # TensorFlow Servingはデフォルトで "serving_default" signatureを使用
    tf.saved_model.save(model, export_path)

    print(f"Model exported successfully to {export_path}")

    # エクスポートされたモデルの情報を表示
    print("\nSavedModel structure:")
    os.system(f"ls -lh {export_path}")

    # Signature情報を表示
    print("\nModel signatures:")
    os.system(f"saved_model_cli show --dir {export_path} --tag_set serve --signature_def serving_default")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="Build and export Iris classification model")
    parser.add_argument(
        "--export-dir",
        type=str,
        default="saved_model/iris",
        help="Directory to export SavedModel (default: saved_model/iris)",
    )
    parser.add_argument(
        "--version",
        type=int,
        default=1,
        help="Model version number (default: 1)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Number of training epochs (default: 100)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Batch size for training (default: 16)",
    )

    args = parser.parse_args()

    # エクスポートパスを構築（バージョン番号を含む）
    export_path = os.path.join(args.export_dir, str(args.version))

    # データ読み込み
    X_train, X_test, y_train, y_test = load_iris_data()

    # データ正規化
    X_train, X_test = normalize_data(X_train, X_test)

    # モデル構築
    model = build_model(input_shape=4, num_classes=3)

    # モデル学習
    history = train_model(
        model,
        X_train,
        y_train,
        X_test,
        y_test,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )

    # モデル評価
    evaluate_model(model, X_test, y_test)

    # モデルエクスポート
    export_model(model, export_path)

    print("\n✅ Model creation completed successfully!")
    print(f"📦 SavedModel location: {export_path}")
    print("\n📝 Next steps:")
    print("  1. Build Docker image with TensorFlow Serving")
    print("  2. Run TensorFlow Serving container")
    print("  3. Test inference with gRPC and REST clients")


if __name__ == "__main__":
    main()
