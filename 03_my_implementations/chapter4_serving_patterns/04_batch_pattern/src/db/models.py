"""SQLAlchemyモデル定義モジュール

データベーステーブルのORMモデルを定義します。
"""

from sqlalchemy import JSON, Column, Integer, TIMESTAMP
from sqlalchemy.sql import func

from src.db.database import Base


class Item(Base):
    """
    アイテムテーブル

    推論対象データと推論結果を保存するテーブル。
    """

    __tablename__ = "items"

    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="アイテムID")

    # データカラム
    values = Column(JSON, nullable=False, comment="入力特徴量（JSON形式）")

    # 推論結果カラム（初期値はNULL）
    prediction = Column(JSON, nullable=True, comment="推論結果（JSON形式）")

    # タイムスタンプ
    created_datetime = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="作成日時",
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"<Item(id={self.id}, values={self.values}, "
            f"prediction={self.prediction}, created_datetime={self.created_datetime})>"
        )
