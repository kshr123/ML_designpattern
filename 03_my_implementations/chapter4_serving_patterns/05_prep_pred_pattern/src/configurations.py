"""設定管理モジュール

環境変数から設定を読み込み、各種設定クラスを提供します。
"""

import os
from logging import getLogger
from pathlib import Path

from PIL import Image
from src.constants import PLATFORM_ENUM

logger = getLogger(__name__)


class PlatformConfigurations:
    """プラットフォーム設定クラス"""

    platform = os.getenv("PLATFORM", PLATFORM_ENUM.DOCKER_COMPOSE.value)

    if not PLATFORM_ENUM.has_value(platform):
        raise ValueError(
            f"PLATFORM must be one of {[v.value for v in PLATFORM_ENUM.__members__.values()]}"
        )


class APIConfigurations:
    """FastAPI設定クラス"""

    title = os.getenv("API_TITLE", "Prep-Pred Pattern")
    description = os.getenv("API_DESCRIPTION", "前処理・推論分離パターン - ResNet50画像分類")
    version = os.getenv("API_VERSION", "0.1.0")


class ModelConfigurations:
    """モデル設定クラス"""

    # 推論サービス接続情報
    api_address = os.getenv("API_ADDRESS", "pred")
    grpc_port = int(os.getenv("GRPC_PORT", 50051))
    http_port = int(os.getenv("HTTP_PORT", 8001))

    # ファイルパス
    base_path = Path(__file__).parent.parent
    data_path = base_path / "data"
    models_path = base_path / "models"

    label_path = os.getenv(
        "LABEL_PATH",
        str(data_path / "image_net_labels.json"),
    )

    sample_image_path = os.getenv(
        "SAMPLE_IMAGE_PATH",
        str(data_path / "cat.jpg"),
    )

    preprocess_transformer_path = os.getenv(
        "PREPROCESS_TRANSFORMER_PATH",
        str(models_path / "preprocess_transformer.pkl"),
    )

    softmax_transformer_path = os.getenv(
        "SOFTMAX_TRANSFORMER_PATH",
        str(models_path / "softmax_transformer.pkl"),
    )

    # ONNX設定
    onnx_input_name = os.getenv("ONNX_INPUT_NAME", "input")
    onnx_output_name = os.getenv("ONNX_OUTPUT_NAME", "output")

    # サンプル画像（ファイルが存在する場合のみ読み込み）
    sample_image = None
    if Path(sample_image_path).exists():
        sample_image = Image.open(sample_image_path)
        logger.info(f"Sample image loaded from {sample_image_path}")
    else:
        logger.warning(f"Sample image not found at {sample_image_path}")


# ログ出力
logger.info(f"{PlatformConfigurations.__name__}: platform={PlatformConfigurations.platform}")
logger.info(
    f"{APIConfigurations.__name__}: title={APIConfigurations.title}, "
    f"version={APIConfigurations.version}"
)
logger.info(
    f"{ModelConfigurations.__name__}: api_address={ModelConfigurations.api_address}, "
    f"grpc_port={ModelConfigurations.grpc_port}"
)
