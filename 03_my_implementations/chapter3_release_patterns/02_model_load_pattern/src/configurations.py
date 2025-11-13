"""設定管理 - 環境変数からの設定読み込み"""
import os
from logging import getLogger

logger = getLogger(__name__)


class APIConfigurations:
    """API設定"""

    title = os.getenv("API_TITLE", "Model-Load Pattern API")
    description = os.getenv(
        "API_DESCRIPTION", "Machine learning system serving with model-load pattern"
    )
    version = os.getenv("API_VERSION", "0.1.0")


class ModelConfigurations:
    """モデル設定"""

    # 環境変数からモデルファイルパスを取得（デフォルト: models/iris_svc.onnx）
    model_filepath = os.getenv("MODEL_FILEPATH", "models/iris_svc.onnx")

    # 環境変数からラベルファイルパスを取得（デフォルト: models/label.json）
    label_filepath = os.getenv("LABEL_FILEPATH", "models/label.json")


# ログ出力
logger.info(f"APIConfigurations: title={APIConfigurations.title}")
logger.info(f"ModelConfigurations: model_filepath={ModelConfigurations.model_filepath}")
logger.info(f"ModelConfigurations: label_filepath={ModelConfigurations.label_filepath}")
