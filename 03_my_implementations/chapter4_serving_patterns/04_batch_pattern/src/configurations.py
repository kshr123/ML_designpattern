"""設定管理モジュール

環境変数から設定を読み込み、プロジェクト全体で使用する設定クラスを提供します。
"""

import json
import os
from logging import getLogger
from pathlib import Path

from src.constants import CONSTANTS, PLATFORM_ENUM

logger = getLogger(__name__)


class PlatformConfigurations:
    """プラットフォーム設定クラス"""

    # プラットフォーム環境
    platform = os.getenv("PLATFORM", CONSTANTS.DEFAULT_PLATFORM)

    # プラットフォームのバリデーション
    if not PLATFORM_ENUM.has_value(platform):
        raise ValueError(
            f"PLATFORM must be one of {[v.value for v in PLATFORM_ENUM.__members__.values()]}"
        )

    # MySQL接続情報
    mysql_username = os.getenv("MYSQL_USER", "root")
    mysql_password = os.getenv("MYSQL_PASSWORD", "password")
    mysql_port = int(os.getenv("MYSQL_PORT", CONSTANTS.DEFAULT_MYSQL_PORT))
    mysql_database = os.getenv("MYSQL_DATABASE", CONSTANTS.DEFAULT_DATABASE_NAME)
    mysql_server = os.getenv("MYSQL_SERVER", "localhost")

    # SQLAlchemy用データベースURL
    sql_alchemy_database_url = (
        f"mysql+pymysql://{mysql_username}:{mysql_password}@"
        f"{mysql_server}:{mysql_port}/{mysql_database}?charset=utf8mb4"
    )

    # サンプルデータパス
    sample_data_path = os.getenv("SAMPLE_DATA_PATH", "models/data.json")

    # サンプルデータの読み込み（ファイルが存在する場合のみ）
    sample_data = []
    if Path(sample_data_path).exists():
        with open(sample_data_path, "r") as f:
            sample_data = json.load(f)


class APIConfigurations:
    """API設定クラス"""

    title = os.getenv("API_TITLE", "BatchPattern")
    description = os.getenv("API_DESCRIPTION", "Batch Pattern for ML System Design Patterns")
    version = os.getenv("API_VERSION", "0.1.0")


class ModelConfigurations:
    """モデル設定クラス"""

    model_filepath = os.getenv("MODEL_FILEPATH", "models/iris_svc.onnx")
    label_filepath = os.getenv("LABEL_FILEPATH", "models/label.json")


class BatchConfigurations:
    """バッチジョブ設定クラス"""

    # バッチ実行前の待機時間（秒）
    wait_time = int(os.getenv("BATCH_WAIT_TIME", CONSTANTS.DEFAULT_BATCH_WAIT_TIME))

    # 並列処理のワーカースレッド数
    worker_threads = int(os.getenv("WORKER_THREADS", CONSTANTS.DEFAULT_WORKER_THREADS))


# ログ出力（デバッグ用）
logger.info(f"PlatformConfigurations.platform: {PlatformConfigurations.platform}")
logger.info(f"PlatformConfigurations.mysql_server: {PlatformConfigurations.mysql_server}")
logger.info(
    f"PlatformConfigurations.sql_alchemy_database_url: "
    f"{PlatformConfigurations.sql_alchemy_database_url}"
)
logger.info(f"ModelConfigurations.model_filepath: {ModelConfigurations.model_filepath}")
logger.info(f"ModelConfigurations.label_filepath: {ModelConfigurations.label_filepath}")
logger.info(f"BatchConfigurations.wait_time: {BatchConfigurations.wait_time}")
logger.info(f"BatchConfigurations.worker_threads: {BatchConfigurations.worker_threads}")
