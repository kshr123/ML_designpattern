"""定数定義モジュール

プロジェクト全体で使用する定数を定義します。
"""

from enum import Enum


class PLATFORM_ENUM(Enum):
    """プラットフォーム環境の列挙型"""

    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    LOCAL = "local"

    @classmethod
    def has_value(cls, value: str) -> bool:
        """
        指定された値が列挙型に含まれているかチェック

        Args:
            value: チェックする値

        Returns:
            値が列挙型に含まれていればTrue
        """
        return value in {item.value for item in cls}


class CONSTANTS:
    """プロジェクト定数"""

    # デフォルトプラットフォーム
    DEFAULT_PLATFORM = PLATFORM_ENUM.LOCAL.value

    # デフォルトMySQLポート
    DEFAULT_MYSQL_PORT = 3306

    # デフォルトデータベース名
    DEFAULT_DATABASE_NAME = "sample_db"

    # デフォルトバッチ待機時間（秒）
    DEFAULT_BATCH_WAIT_TIME = 60

    # デフォルトワーカースレッド数
    DEFAULT_WORKER_THREADS = 4

    # Iris特徴量の次元数
    IRIS_FEATURE_DIM = 4

    # Irisクラス数
    IRIS_NUM_CLASSES = 3
