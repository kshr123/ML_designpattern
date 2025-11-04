"""
CRUD Layer

データベース操作のビジネスロジックを実装します。
Create, Read, Update, Delete の操作を提供します。
"""

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from src.db import models, schemas


# ==================== Project CRUD ====================


def select_project_all(db: Session) -> List[models.Project]:
    """
    全プロジェクトを取得

    Args:
        db: データベースセッション

    Returns:
        プロジェクトのリスト
    """
    return db.query(models.Project).all()


def select_project_by_id(db: Session, project_id: str) -> Optional[models.Project]:
    """
    IDでプロジェクトを取得

    Args:
        db: データベースセッション
        project_id: プロジェクトID

    Returns:
        プロジェクト、または存在しない場合はNone
    """
    return db.query(models.Project).filter(models.Project.project_id == project_id).first()


def select_project_by_name(db: Session, project_name: str) -> Optional[models.Project]:
    """
    名前でプロジェクトを取得

    Args:
        db: データベースセッション
        project_name: プロジェクト名

    Returns:
        プロジェクト、または存在しない場合はNone
    """
    return db.query(models.Project).filter(models.Project.project_name == project_name).first()


def add_project(
    db: Session,
    project_name: str,
    description: Optional[str] = None,
    commit: bool = True,
) -> models.Project:
    """
    プロジェクトを作成

    同名のプロジェクトが既に存在する場合は、既存のプロジェクトを返します。

    Args:
        db: データベースセッション
        project_name: プロジェクト名
        description: プロジェクトの説明
        commit: トランザクションをコミットするか

    Returns:
        作成されたプロジェクト（または既存のプロジェクト）
    """
    # 既存チェック
    exists = select_project_by_name(db=db, project_name=project_name)
    if exists:
        return exists

    # 新規作成
    project_id = str(uuid.uuid4())[:6]
    data = models.Project(
        project_id=project_id,
        project_name=project_name,
        description=description,
    )
    db.add(data)

    if commit:
        db.commit()
        db.refresh(data)

    return data


# ==================== Model CRUD ====================


def select_model_all(db: Session) -> List[models.Model]:
    """
    全モデルを取得

    Args:
        db: データベースセッション

    Returns:
        モデルのリスト
    """
    return db.query(models.Model).all()


def select_model_by_id(db: Session, model_id: str) -> Optional[models.Model]:
    """
    IDでモデルを取得

    Args:
        db: データベースセッション
        model_id: モデルID

    Returns:
        モデル、または存在しない場合はNone
    """
    return db.query(models.Model).filter(models.Model.model_id == model_id).first()


def select_model_by_project_id(db: Session, project_id: str) -> List[models.Model]:
    """
    プロジェクトIDでモデルを取得

    Args:
        db: データベースセッション
        project_id: プロジェクトID

    Returns:
        モデルのリスト
    """
    return db.query(models.Model).filter(models.Model.project_id == project_id).all()


def select_model_by_project_name(db: Session, project_name: str) -> List[models.Model]:
    """
    プロジェクト名でモデルを取得

    Args:
        db: データベースセッション
        project_name: プロジェクト名

    Returns:
        モデルのリスト
    """
    project = select_project_by_name(db=db, project_name=project_name)
    if not project:
        return []
    return db.query(models.Model).filter(models.Model.project_id == project.project_id).all()


def select_model_by_name(db: Session, model_name: str) -> List[models.Model]:
    """
    モデル名でモデルを取得

    Args:
        db: データベースセッション
        model_name: モデル名

    Returns:
        モデルのリスト
    """
    return db.query(models.Model).filter(models.Model.model_name == model_name).all()


def add_model(
    db: Session,
    project_id: str,
    model_name: str,
    description: Optional[str] = None,
    commit: bool = True,
) -> models.Model:
    """
    モデルを作成

    同一プロジェクト内で同名のモデルが既に存在する場合は、既存のモデルを返します。

    Args:
        db: データベースセッション
        project_id: プロジェクトID
        model_name: モデル名
        description: モデルの説明
        commit: トランザクションをコミットするか

    Returns:
        作成されたモデル（または既存のモデル）
    """
    # 同一プロジェクト内での重複チェック
    models_in_project = select_model_by_project_id(db=db, project_id=project_id)
    for model in models_in_project:
        if model.model_name == model_name:
            return model

    # 新規作成
    model_id = str(uuid.uuid4())[:6]
    data = models.Model(
        model_id=model_id,
        project_id=project_id,
        model_name=model_name,
        description=description,
    )
    db.add(data)

    if commit:
        db.commit()
        db.refresh(data)

    return data


# ==================== Experiment CRUD ====================


def select_experiment_all(db: Session) -> List[models.Experiment]:
    """
    全実験を取得

    Args:
        db: データベースセッション

    Returns:
        実験のリスト
    """
    return db.query(models.Experiment).all()


def select_experiment_by_id(db: Session, experiment_id: str) -> Optional[models.Experiment]:
    """
    IDで実験を取得

    Args:
        db: データベースセッション
        experiment_id: 実験ID

    Returns:
        実験、または存在しない場合はNone
    """
    return db.query(models.Experiment).filter(models.Experiment.experiment_id == experiment_id).first()


def select_experiment_by_model_version_id(db: Session, model_version_id: str) -> Optional[models.Experiment]:
    """
    モデルバージョンIDで実験を取得

    Args:
        db: データベースセッション
        model_version_id: モデルバージョンID

    Returns:
        実験、または存在しない場合はNone
    """
    return db.query(models.Experiment).filter(models.Experiment.model_version_id == model_version_id).first()


def select_experiment_by_model_id(db: Session, model_id: str) -> List[models.Experiment]:
    """
    モデルIDで実験を取得

    Args:
        db: データベースセッション
        model_id: モデルID

    Returns:
        実験のリスト
    """
    return db.query(models.Experiment).filter(models.Experiment.model_id == model_id).all()


def select_experiment_by_project_id(db: Session, project_id: str) -> List[tuple]:
    """
    プロジェクトIDで実験を取得

    ExperimentとModelをJOINして取得します。

    Args:
        db: データベースセッション
        project_id: プロジェクトID

    Returns:
        実験のリスト
    """
    return (
        db.query(models.Experiment, models.Model)
        .filter(models.Model.project_id == project_id)
        .filter(models.Experiment.model_id == models.Model.model_id)
        .all()
    )


def add_experiment(
    db: Session,
    model_version_id: str,
    model_id: str,
    parameters: Optional[Dict[str, Any]] = None,
    training_dataset: Optional[str] = None,
    validation_dataset: Optional[str] = None,
    test_dataset: Optional[str] = None,
    evaluations: Optional[Dict[str, Any]] = None,
    artifact_file_paths: Optional[Dict[str, Any]] = None,
    commit: bool = True,
) -> models.Experiment:
    """
    実験を作成

    Args:
        db: データベースセッション
        model_version_id: モデルバージョンID
        model_id: モデルID
        parameters: 学習パラメータ
        training_dataset: 学習データセットのパス
        validation_dataset: 検証データセットのパス
        test_dataset: テストデータセットのパス
        evaluations: 評価結果
        artifact_file_paths: モデルファイルのパス
        commit: トランザクションをコミットするか

    Returns:
        作成された実験
    """
    experiment_id = str(uuid.uuid4())[:6]
    data = models.Experiment(
        experiment_id=experiment_id,
        model_version_id=model_version_id,
        model_id=model_id,
        parameters=parameters,
        training_dataset=training_dataset,
        validation_dataset=validation_dataset,
        test_dataset=test_dataset,
        evaluations=evaluations,
        artifact_file_paths=artifact_file_paths,
    )
    db.add(data)

    if commit:
        db.commit()
        db.refresh(data)

    return data


def update_experiment_evaluation(
    db: Session,
    experiment_id: str,
    evaluations: Dict[str, Any],
) -> models.Experiment:
    """
    実験の評価結果を更新

    既存の評価結果に新しい評価結果をマージします。

    Args:
        db: データベースセッション
        experiment_id: 実験ID
        evaluations: 新しい評価結果

    Returns:
        更新された実験
    """
    data = select_experiment_by_id(db=db, experiment_id=experiment_id)

    if data.evaluations is None:
        data.evaluations = evaluations
    else:
        # 既存の評価結果に新しい評価結果をマージ
        # SQLiteのJSON型の更新を確実にするため、新しいdictを作成
        updated_evaluations = dict(data.evaluations)
        updated_evaluations.update(evaluations)
        data.evaluations = updated_evaluations

    db.commit()
    db.refresh(data)

    return data


def update_experiment_artifact_file_paths(
    db: Session,
    experiment_id: str,
    artifact_file_paths: Dict[str, Any],
) -> models.Experiment:
    """
    実験のモデルファイルパスを更新

    既存のファイルパスに新しいファイルパスをマージします。

    Args:
        db: データベースセッション
        experiment_id: 実験ID
        artifact_file_paths: 新しいモデルファイルのパス

    Returns:
        更新された実験
    """
    data = select_experiment_by_id(db=db, experiment_id=experiment_id)

    if data.artifact_file_paths is None:
        data.artifact_file_paths = artifact_file_paths
    else:
        # 既存のファイルパスに新しいファイルパスをマージ
        # SQLiteのJSON型の更新を確実にするため、新しいdictを作成
        updated_paths = dict(data.artifact_file_paths)
        updated_paths.update(artifact_file_paths)
        data.artifact_file_paths = updated_paths

    db.commit()
    db.refresh(data)

    return data
