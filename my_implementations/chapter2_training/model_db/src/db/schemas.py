"""
Schema Layer

PydanticモデルによるAPIのリクエスト/レスポンス構造定義。
データバリデーションとシリアライゼーションを提供します。
"""

import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


# ==================== Project Schemas ====================


class ProjectBase(BaseModel):
    """プロジェクトの基本情報"""

    project_name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """プロジェクト作成時のリクエストスキーマ"""

    pass


class Project(ProjectBase):
    """プロジェクトのレスポンススキーマ"""

    project_id: str
    created_datetime: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Model Schemas ====================


class ModelBase(BaseModel):
    """モデルの基本情報"""

    project_id: str
    model_name: str
    description: Optional[str] = None


class ModelCreate(ModelBase):
    """モデル作成時のリクエストスキーマ"""

    pass


class Model(ModelBase):
    """モデルのレスポンススキーマ"""

    model_id: str
    created_datetime: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Experiment Schemas ====================


class ExperimentBase(BaseModel):
    """実験の基本情報"""

    model_id: str
    model_version_id: str
    parameters: Optional[Dict[str, Any]] = None
    training_dataset: Optional[str] = None
    validation_dataset: Optional[str] = None
    test_dataset: Optional[str] = None
    evaluations: Optional[Dict[str, Any]] = None
    artifact_file_paths: Optional[Dict[str, Any]] = None


class ExperimentCreate(ExperimentBase):
    """実験作成時のリクエストスキーマ"""

    pass


class ExperimentEvaluations(BaseModel):
    """実験の評価結果更新用スキーマ"""

    evaluations: Dict[str, Any]


class ExperimentArtifactFilePaths(BaseModel):
    """実験のモデルファイルパス更新用スキーマ"""

    artifact_file_paths: Dict[str, Any]


class Experiment(ExperimentBase):
    """実験のレスポンススキーマ"""

    experiment_id: str
    created_datetime: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
