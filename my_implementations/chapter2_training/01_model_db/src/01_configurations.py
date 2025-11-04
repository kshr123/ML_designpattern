"""
Configuration Module

環境変数から設定を読み込みます。
"""

import os


class Settings:
    """アプリケーション設定"""

    # データベース設定
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "model_db")

    # テスト環境ではSQLiteを使用
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"

    @property
    def database_url(self) -> str:
        """データベース接続URL"""
        if self.TESTING:
            return "sqlite:///./test.db"
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
