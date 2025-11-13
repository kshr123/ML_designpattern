"""
設定管理モジュール

環境変数の読み込みと設定値の管理を行います。
"""

import os


class ModelConfigurations:
    """モデル設定"""

    model_filepath = os.getenv("MODEL_FILEPATH", "models/iris_svc.onnx")
    label_filepath = os.getenv("LABEL_FILEPATH", "models/label.json")


class APIConfigurations:
    """API設定"""

    title = os.getenv("API_TITLE", "Web Single Pattern")
    description = os.getenv("API_DESCRIPTION", "Iris classification API using Web Single Pattern")
    version = os.getenv("API_VERSION", "0.1.0")
