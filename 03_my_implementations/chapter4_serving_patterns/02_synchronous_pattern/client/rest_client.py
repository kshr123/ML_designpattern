#!/usr/bin/env python3
"""
RESTクライアント

TensorFlow ServingのREST APIエンドポイントを使用して推論を実行します。
HTTP/JSONベースなので実装がシンプルですが、gRPCよりは遅いです。

Usage:
    python rest_client.py --host localhost --port 8501
"""

import argparse
import time
from typing import Dict, List, Tuple

import numpy as np
import requests


class IrisRESTClient:
    """TensorFlow Serving RESTクライアント"""

    def __init__(self, host: str = "localhost", port: int = 8501, model_name: str = "iris"):
        """
        Args:
            host: TensorFlow Servingのホスト
            port: RESTポート（デフォルト: 8501）
            model_name: モデル名
        """
        self.host = host
        self.port = port
        self.model_name = model_name
        self.base_url = f"http://{host}:{port}/v1/models/{model_name}"

    def get_model_status(self) -> Dict:
        """
        モデルのステータスを取得する

        Returns:
            Dict: モデルステータス情報
        """
        url = self.base_url
        print(f"Getting model status from {url}...")

        try:
            response = requests.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting model status: {e}")
            raise

    def get_model_metadata(self) -> Dict:
        """
        モデルのメタデータを取得する

        Returns:
            Dict: モデルメタデータ（入出力のシグネチャ情報）
        """
        url = f"{self.base_url}/metadata"
        print(f"Getting model metadata from {url}...")

        try:
            response = requests.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting model metadata: {e}")
            raise

    def predict(
        self,
        data: List[List[float]],
        timeout: float = 10.0,
    ) -> Tuple[np.ndarray, float]:
        """
        推論を実行する（instances形式）

        Args:
            data: 入力データ [[sepal_length, sepal_width, petal_length, petal_width], ...]
            timeout: タイムアウト（秒）

        Returns:
            Tuple[np.ndarray, float]: (推論結果, レスポンスタイム)
        """
        url = f"{self.base_url}:predict"

        # リクエストボディ（instances形式）
        payload = {
            "instances": data
        }

        # 推論実行（レスポンスタイム測定）
        start_time = time.time()
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response_time = time.time() - start_time
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise

        # レスポンスから推論結果を取得
        result = response.json()
        predictions = np.array(result["predictions"])

        return predictions, response_time

    def predict_with_inputs(
        self,
        data: List[List[float]],
        timeout: float = 10.0,
    ) -> Tuple[np.ndarray, float]:
        """
        推論を実行する（inputs形式）

        Args:
            data: 入力データ
            timeout: タイムアウト（秒）

        Returns:
            Tuple[np.ndarray, float]: (推論結果, レスポンスタイム)
        """
        url = f"{self.base_url}:predict"

        # リクエストボディ（inputs形式）
        payload = {
            "inputs": {
                "input": data
            }
        }

        # 推論実行
        start_time = time.time()
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response_time = time.time() - start_time
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise

        # レスポンスから推論結果を取得
        result = response.json()
        predictions = np.array(result["predictions"])

        return predictions, response_time

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
    parser = argparse.ArgumentParser(description="TensorFlow Serving REST Client for Iris")
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="TensorFlow Serving host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="REST port (default: 8501)",
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
    client = IrisRESTClient(host=args.host, port=args.port, model_name=args.model_name)

    try:
        print("\n========================================")
        print("🔮 Iris Classification - REST Client")
        print("========================================\n")

        # 0. モデルステータス確認
        print("0️⃣ Model Status:")
        status = client.get_model_status()
        print(f"  {status}\n")

        # 1. モデルメタデータ確認
        print("1️⃣ Model Metadata:")
        metadata = client.get_model_metadata()
        print(f"  Model: {metadata.get('model_spec', {}).get('name')}")
        print(f"  Version: {metadata.get('model_spec', {}).get('version')}\n")

        # 2. 確率値で推論（instances形式）
        print("2️⃣ Prediction with probabilities (instances format):")
        probabilities, response_time = client.predict(test_data)

        for i, (data, prob) in enumerate(zip(test_data, probabilities)):
            print(f"\n  Sample {i+1}: {data}")
            print(f"    Probabilities: {prob}")
            print(f"    Predicted class: {np.argmax(prob)}")
            print(f"    Response time: {response_time*1000:.2f}ms")

        # 3. 確率値で推論（inputs形式）
        print("\n3️⃣ Prediction with probabilities (inputs format):")
        probabilities, response_time = client.predict_with_inputs(test_data)

        for i, (data, prob) in enumerate(zip(test_data, probabilities)):
            print(f"\n  Sample {i+1}: {data}")
            print(f"    Probabilities: {prob}")
            print(f"    Response time: {response_time*1000:.2f}ms")

        # 4. クラス名で推論
        print("\n4️⃣ Prediction with class names:")
        class_names, response_time = client.predict_class(test_data)

        for i, (data, class_name) in enumerate(zip(test_data, class_names)):
            print(f"\n  Sample {i+1}: {data}")
            print(f"    Predicted: {class_name}")
            print(f"    Response time: {response_time*1000:.2f}ms")

        print("\n========================================")
        print("✅ REST Client Test Completed")
        print("========================================\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
