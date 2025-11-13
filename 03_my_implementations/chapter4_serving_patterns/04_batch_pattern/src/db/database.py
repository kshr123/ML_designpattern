"""データベース接続管理モジュール

SQLAlchemyのエンジン、セッション、Baseクラスを提供します。
"""

from contextlib import contextmanager
from logging import getLogger

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from src.configurations import PlatformConfigurations

logger = getLogger(__name__)

# SQLAlchemyエンジンの作成
engine = create_engine(
    PlatformConfigurations.sql_alchemy_database_url,
    pool_recycle=3600,  # コネクションプールのリサイクル時間（秒）
    echo=False,  # SQL出力を無効化（本番環境ではFalse推奨）
)

# セッションファクトリの作成
SessionLocal = sessionmaker(
    autocommit=False,  # 明示的なコミット必須
    autoflush=False,  # 明示的なフラッシュ必須
    bind=engine,
)

# Baseクラスの作成（モデル定義で継承）
Base = declarative_base()


def get_db() -> Session:
    """
    FastAPI依存性注入用のデータベースセッション取得関数

    Yields:
        データベースセッション

    使用例:
        @app.get("/")
        def read_root(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_context_db() -> Session:
    """
    コンテキストマネージャー用のデータベースセッション取得関数

    バッチジョブなどで使用。

    Yields:
        データベースセッション

    使用例:
        with get_context_db() as db:
            items = db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """
    全テーブルを作成する関数

    開発・テスト用。本番環境ではAlembicなどのマイグレーションツールを使用推奨。
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")


def drop_tables():
    """
    全テーブルを削除する関数

    テスト用。本番環境では使用しないこと。
    """
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped.")
