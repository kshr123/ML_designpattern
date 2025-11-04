"""
Database Layer

データベース接続とセッション管理を行います。
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# データベース接続URL
# テスト環境ではSQLite、本番環境ではPostgreSQLを使用
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./model_db.sqlite"  # デフォルトはSQLite（開発用）
)

# エンジンの作成
# SQLiteの場合はcheck_same_threadを無効化
connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

# セッションファクトリの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORMモデルのベースクラス
Base = declarative_base()


def get_db():
    """
    データベースセッションを取得する依存性注入用関数

    FastAPIのDepends()で使用します。
    リクエストごとに新しいセッションを作成し、レスポンス後に自動的にクローズします。

    Yields:
        Session: データベースセッション
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
