"""設定管理

環境変数からアプリケーション設定を読み込む
"""

import os
from typing import Dict


class ProxyConfig:
    """Proxyサービスの設定"""

    port = int(os.getenv("PORT", "9000"))

    # 各サービスのURL（環境変数から取得）
    service_setosa = os.getenv("SERVICE_SETOSA", "http://localhost:8000")
    service_versicolor = os.getenv("SERVICE_VERSICOLOR", "http://localhost:8001")
    service_virginica = os.getenv("SERVICE_VIRGINICA", "http://localhost:8002")

    @classmethod
    def get_services(cls) -> Dict[str, str]:
        """サービスのマッピングを取得"""
        return {
            "setosa": cls.service_setosa,
            "versicolor": cls.service_versicolor,
            "virginica": cls.service_virginica,
        }


class ServiceConfig:
    """各専門サービスの設定"""

    port = int(os.getenv("PORT", "8000"))
    mode = os.getenv("MODE", "setosa")  # setosa, versicolor, virginica

    # モデルファイルパス
    model_dir = "models"

    @classmethod
    def get_model_path(cls) -> str:
        """モードに応じたモデルパスを取得"""
        if cls.mode == "setosa":
            return f"{cls.model_dir}/iris_svc_0_setosa.onnx"
        elif cls.mode == "versicolor":
            return f"{cls.model_dir}/iris_svc_0_versicolor.onnx"
        elif cls.mode == "virginica":
            return f"{cls.model_dir}/iris_svc_0_virginica.onnx"
        else:
            raise ValueError(f"Invalid mode: {cls.mode}")


class AppConfig:
    """共通アプリケーション設定"""

    title = "Horizontal Microservice Pattern"
    version = "1.0.0"
    test_data = [[5.1, 3.5, 1.4, 0.2]]  # Iris setosaのサンプル
