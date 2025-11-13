"""pytestフィクスチャ定義モジュール

テスト用の共通フィクスチャを定義します。
"""

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.app import app
from src.db import models
from src.db.database import Base, get_db

# テスト用MySQLデータベース
# Docker Composeで起動したmysql_testコンテナに接続（ポート3307）
SQLALCHEMY_TEST_DATABASE_URL = "mysql+pymysql://test_user:test_password@localhost:3307/test_db?charset=utf8mb4"

# テスト用エンジンとセッション
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    pool_recycle=3600,  # コネクションプールのリサイクル時間（秒）
    echo=False,  # SQL出力を無効化
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    テスト用データベースセッションフィクスチャ

    各テスト関数ごとにデータベースを作成・削除します。

    Yields:
        テスト用データベースセッション
    """
    # モデルが確実にインポートされていることを保証
    # （models.Item がBase.metadataに登録されるようにする）
    models.Item  # noqa: B018 - 明示的にクラスを参照してメタデータ登録を確実にする

    # テーブル作成
    Base.metadata.create_all(bind=test_engine)

    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # テーブル削除
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> TestClient:
    """
    FastAPIテストクライアントフィクスチャ

    Args:
        test_db: テスト用データベースセッション

    Returns:
        FastAPIテストクライアント
    """

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)


@pytest.fixture
def sample_item_data() -> dict:
    """
    サンプルアイテムデータフィクスチャ

    Returns:
        サンプルデータ
    """
    return {"values": [5.1, 3.5, 1.4, 0.2]}


@pytest.fixture
def sample_items_data() -> list:
    """
    複数サンプルアイテムデータフィクスチャ

    Returns:
        サンプルデータのリスト
    """
    return [
        {"values": [5.1, 3.5, 1.4, 0.2]},  # setosa
        {"values": [6.3, 3.3, 6.0, 2.5]},  # virginica
        {"values": [5.9, 3.0, 5.1, 1.8]},  # virginica
    ]


@pytest.fixture
def sample_prediction() -> dict:
    """
    サンプル推論結果フィクスチャ

    Returns:
        サンプル推論結果
    """
    return {"0": 0.971, "1": 0.016, "2": 0.013}


# 環境変数設定（テスト用）
@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """テスト用環境変数を設定"""
    os.environ["MYSQL_SERVER"] = "localhost"
    os.environ["MYSQL_USER"] = "test_user"
    os.environ["MYSQL_PASSWORD"] = "test_password"
    os.environ["MYSQL_DATABASE"] = "test_db"
    os.environ["MODEL_FILEPATH"] = "models/iris_svc.onnx"
    os.environ["LABEL_FILEPATH"] = "models/label.json"
    os.environ["BATCH_WAIT_TIME"] = "0"  # テスト用：待機なし
    os.environ["WORKER_THREADS"] = "2"  # テスト用：2スレッド
