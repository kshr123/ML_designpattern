"""
Model Layer

SQLAlchemyを使用したデータベーステーブル定義。
Project → Model → Experiment の3階層構造を定義します。
"""

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.types import JSON

from src.db.database import Base


class Project(Base):
    """
    プロジェクトテーブル

    機械学習プロジェクトの情報を管理します。
    """

    __tablename__ = "projects"

    project_id = Column(
        String(255),
        primary_key=True,
        comment="プロジェクト一意識別子",
    )
    project_name = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="プロジェクト名",
    )
    description = Column(
        Text,
        nullable=True,
        comment="プロジェクトの説明",
    )
    created_datetime = Column(
        DateTime(timezone=True),
        server_default=current_timestamp(),
        nullable=False,
        comment="作成日時",
    )


class Model(Base):
    """
    モデルテーブル

    プロジェクト配下の機械学習モデルの情報を管理します。
    """

    __tablename__ = "models"

    model_id = Column(
        String(255),
        primary_key=True,
        comment="モデル一意識別子",
    )
    project_id = Column(
        String(255),
        ForeignKey("projects.project_id"),
        nullable=False,
        comment="プロジェクトID（外部キー）",
    )
    model_name = Column(
        String(255),
        nullable=False,
        comment="モデル名",
    )
    description = Column(
        Text,
        nullable=True,
        comment="モデルの説明",
    )
    created_datetime = Column(
        DateTime(timezone=True),
        server_default=current_timestamp(),
        nullable=False,
        comment="作成日時",
    )


class Experiment(Base):
    """
    実験テーブル

    モデルの学習実験記録を管理します。
    パラメータ、データセット、評価結果、モデルファイルパスなどを保存します。
    """

    __tablename__ = "experiments"

    experiment_id = Column(
        String(255),
        primary_key=True,
        comment="実験一意識別子",
    )
    model_id = Column(
        String(255),
        ForeignKey("models.model_id"),
        nullable=False,
        comment="モデルID（外部キー）",
    )
    model_version_id = Column(
        String(255),
        nullable=False,
        comment="モデルバージョンID",
    )
    parameters = Column(
        JSON,
        nullable=True,
        comment="学習パラメータ（JSON形式）",
    )
    training_dataset = Column(
        Text,
        nullable=True,
        comment="学習データセットのパス",
    )
    validation_dataset = Column(
        Text,
        nullable=True,
        comment="検証データセットのパス",
    )
    test_dataset = Column(
        Text,
        nullable=True,
        comment="テストデータセットのパス",
    )
    evaluations = Column(
        JSON,
        nullable=True,
        comment="評価結果（JSON形式）",
    )
    artifact_file_paths = Column(
        JSON,
        nullable=True,
        comment="モデルファイルのパス（JSON形式）",
    )
    created_datetime = Column(
        DateTime(timezone=True),
        server_default=current_timestamp(),
        nullable=False,
        comment="作成日時",
    )
