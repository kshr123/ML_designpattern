#!/usr/bin/env python3
"""
gRPCクライアント

TensorFlow ServingのgRPCエンドポイントを使用して推論を実行します。
gRPCはバイナリプロトコルでRESTより高速です。

Usage:
    python grpc_client.py --host localhost --port 8500
"""

import argparse
import time
from typing import List, Tuple

import grpc
import numpy as np
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2_grpc
import tensorflow as tf


class IrisGRPCClient:
    """TensorFlow Serving gRPCクライアント"""

    def __init__(self, host: str = "localhost", port: int = 8500, model_name: str = "iris"):
        """
        Args:
            host: TensorFlow Servingのホスト
            port: gRPCポート（デフォルト: 8500）
            model_name: モデル名
        """
        self.host = host
        self.port = port
        self.model_name = model_name
        self.server_url = f"{host}:{port}"
        self.channel = None
        self.stub = None

    def connect(self) -> None:
        """gRPCチャネルを確立する"""
        print(f"Connecting to TensorFlow Serving at {self.server_url}...")
        self.channel = grpc.insecure_channel(self.server_url)
        self.stub = prediction_service_pb2_grpc.PredictionServiceStub(self.channel)
        print("✅ Connected successfully")

    def close(self) -> None:
        """gRPCチャネルを閉じる"""
        if self.channel:
            self.channel.close()
            print("Connection closed")

    def predict(
        self,
        data: List[List[float]],
        signature_name: str = "serving_default",
        timeout: float = 10.0,
    ) -> Tuple[np.ndarray, float]:
        """
        推論を実行する

        Args:
            data: 入力データ [[sepal_length, sepal_width, petal_length, petal_width], ...]
            signature_name: Serving signature名
            timeout: タイムアウト（秒）

        Returns:
            Tuple[np.ndarray, float]: (推論結果, レスポンスタイム)
        """
        if not self.stub:
            raise RuntimeError("Not connected. Call connect() first.")

        # PredictRequestを作成
        request = predict_pb2.PredictRequest()
        request.model_spec.name = self.model_name
        request.model_spec.signature_name = signature_name

        # 入力データをTensorProtoに変換
        input_data = np.array(data, dtype=np.float32)
        request.inputs["input"].CopyFrom(
            tf.make_tensor_proto(input_data, shape=input_data.shape)
        )

        # 推論実行（レスポンスタイム測定）
        start_time = time.time()
        try:
            response = self.stub.Predict(request, timeout=timeout)
            response_time = time.time() - start_time
        except grpc.RpcError as e:
            print(f"❌ gRPC Error: {e.code()} - {e.details()}")
            raise

        # レスポンスから推論結果を取得
        output = tf.make_ndarray(response.outputs["output"])

        return output, response_time

    def predict_class(
        self, data: List[List[float]], class_names: List[str] = None
    ) -> Tuple[List[str], float]:
        """
        推論を実行してクラス名を返す

        Args:
            data: 入力データ
            class_names: クラス名リスト（デフォルト: ["setosa", "versicolor", "virginica"]）

        Returns:
            Tuple[List[str], float]: (予測クラス名のリスト, レスポンスタイム)
        """
        if class_names is None:
            class_names = ["setosa", "versicolor", "virginica"]

        # 推論実行
        probabilities, response_time = self.predict(data)

        # 最大確率のインデックスを取得
        predicted_classes = []
        for prob in probabilities:
            class_idx = np.argmax(prob)
            predicted_classes.append(class_names[class_idx])

        return predicted_classes, response_time


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="TensorFlow Serving gRPC Client for Iris")
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="TensorFlow Serving host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8500,
        help="gRPC port (default: 8500)",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="iris",
        help="Model name (default: iris)",
    )

    args = parser.parse_args()

    # テストデータ（Iris setosa、versicolor、virginica の代表例）
    test_data = [
        [5.1, 3.5, 1.4, 0.2],  # setosa
        [6.3, 3.3, 4.7, 1.6],  # versicolor
        [6.3, 3.3, 6.0, 2.5],  # virginica
    ]

    # クライアント初期化
    client = IrisGRPCClient(host=args.host, port=args.port, model_name=args.model_name)

    try:
        # 接続
        client.connect()

        print("\n========================================")
        print("🔮 Iris Classification - gRPC Client")
        print("========================================\n")

        # 1. 確率値で推論
        print("1️⃣ Prediction with probabilities:")
        probabilities, response_time = client.predict(test_data)

        for i, (data, prob) in enumerate(zip(test_data, probabilities)):
            print(f"\n  Sample {i+1}: {data}")
            print(f"    Probabilities: {prob}")
            print(f"    Predicted class: {np.argmax(prob)}")
            print(f"    Response time: {response_time*1000:.2f}ms")

        # 2. クラス名で推論
        print("\n2️⃣ Prediction with class names:")
        class_names, response_time = client.predict_class(test_data)

        for i, (data, class_name) in enumerate(zip(test_data, class_names)):
            print(f"\n  Sample {i+1}: {data}")
            print(f"    Predicted: {class_name}")
            print(f"    Response time: {response_time*1000:.2f}ms")

        print("\n========================================")
        print("✅ gRPC Client Test Completed")
        print("========================================\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

    finally:
        # 接続を閉じる
        client.close()


if __name__ == "__main__":
    main()
