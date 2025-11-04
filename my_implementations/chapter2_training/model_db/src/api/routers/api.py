"""
API Router

プロジェクト、モデル、実験に関するAPIエンドポイントを提供します。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db import cruds, schemas
from src.db.database import get_db

router = APIRouter()


# ==================== Project Endpoints ====================


@router.get("/projects/all", response_model=list[schemas.Project])
def project_all(db: Session = Depends(get_db)):
    """
    全プロジェクトを取得

    Returns:
        プロジェクトのリスト
    """
    return cruds.select_project_all(db=db)


@router.get("/projects/id/{project_id}", response_model=schemas.Project)
def project_by_id(project_id: str, db: Session = Depends(get_db)):
    """
    IDでプロジェクトを取得

    Args:
        project_id: プロジェクトID

    Returns:
        プロジェクト情報
    """
    return cruds.select_project_by_id(db=db, project_id=project_id)


@router.get("/projects/name/{project_name}", response_model=schemas.Project)
def project_by_name(project_name: str, db: Session = Depends(get_db)):
    """
    名前でプロジェクトを取得

    Args:
        project_name: プロジェクト名

    Returns:
        プロジェクト情報
    """
    return cruds.select_project_by_name(db=db, project_name=project_name)


@router.post("/projects", response_model=schemas.Project)
def add_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """
    プロジェクトを作成

    Args:
        project: プロジェクト作成リクエスト

    Returns:
        作成されたプロジェクト情報
    """
    return cruds.add_project(
        db=db,
        project_name=project.project_name,
        description=project.description,
        commit=True,
    )


# ==================== Model Endpoints ====================


@router.get("/models/all", response_model=list[schemas.Model])
def model_all(db: Session = Depends(get_db)):
    """
    全モデルを取得

    Returns:
        モデルのリスト
    """
    return cruds.select_model_all(db=db)


@router.get("/models/id/{model_id}", response_model=schemas.Model)
def model_by_id(model_id: str, db: Session = Depends(get_db)):
    """
    IDでモデルを取得

    Args:
        model_id: モデルID

    Returns:
        モデル情報
    """
    return cruds.select_model_by_id(db=db, model_id=model_id)


@router.get("/models/project-id/{project_id}", response_model=list[schemas.Model])
def model_by_project_id(project_id: str, db: Session = Depends(get_db)):
    """
    プロジェクトIDでモデルを取得

    Args:
        project_id: プロジェクトID

    Returns:
        モデルのリスト
    """
    return cruds.select_model_by_project_id(db=db, project_id=project_id)


@router.get("/models/name/{model_name}", response_model=list[schemas.Model])
def model_by_name(model_name: str, db: Session = Depends(get_db)):
    """
    モデル名でモデルを取得

    Args:
        model_name: モデル名

    Returns:
        モデルのリスト
    """
    return cruds.select_model_by_name(db=db, model_name=model_name)


@router.get("/models/project-name/{project_name}", response_model=list[schemas.Model])
def model_by_project_name(project_name: str, db: Session = Depends(get_db)):
    """
    プロジェクト名でモデルを取得

    Args:
        project_name: プロジェクト名

    Returns:
        モデルのリスト
    """
    return cruds.select_model_by_project_name(db=db, project_name=project_name)


@router.post("/models", response_model=schemas.Model)
def add_model(model: schemas.ModelCreate, db: Session = Depends(get_db)):
    """
    モデルを作成

    Args:
        model: モデル作成リクエスト

    Returns:
        作成されたモデル情報
    """
    return cruds.add_model(
        db=db,
        project_id=model.project_id,
        model_name=model.model_name,
        description=model.description,
        commit=True,
    )


# ==================== Experiment Endpoints ====================


@router.get("/experiments/all", response_model=list[schemas.Experiment])
def experiment_all(db: Session = Depends(get_db)):
    """
    全実験を取得

    Returns:
        実験のリスト
    """
    return cruds.select_experiment_all(db=db)


@router.get("/experiments/id/{experiment_id}", response_model=schemas.Experiment)
def experiment_by_id(experiment_id: str, db: Session = Depends(get_db)):
    """
    IDで実験を取得

    Args:
        experiment_id: 実験ID

    Returns:
        実験情報
    """
    return cruds.select_experiment_by_id(db=db, experiment_id=experiment_id)


@router.get("/experiments/model-version-id/{model_version_id}", response_model=schemas.Experiment)
def experiment_by_model_version_id(model_version_id: str, db: Session = Depends(get_db)):
    """
    モデルバージョンIDで実験を取得

    Args:
        model_version_id: モデルバージョンID

    Returns:
        実験情報
    """
    return cruds.select_experiment_by_model_version_id(db=db, model_version_id=model_version_id)


@router.get("/experiments/model-id/{model_id}", response_model=list[schemas.Experiment])
def experiment_by_model_id(model_id: str, db: Session = Depends(get_db)):
    """
    モデルIDで実験を取得

    Args:
        model_id: モデルID

    Returns:
        実験のリスト
    """
    return cruds.select_experiment_by_model_id(db=db, model_id=model_id)


@router.get("/experiments/project-id/{project_id}")
def experiment_by_project_id(project_id: str, db: Session = Depends(get_db)):
    """
    プロジェクトIDで実験を取得

    Args:
        project_id: プロジェクトID

    Returns:
        実験のリスト
    """
    return cruds.select_experiment_by_project_id(db=db, project_id=project_id)


@router.post("/experiments", response_model=schemas.Experiment)
def add_experiment(experiment: schemas.ExperimentCreate, db: Session = Depends(get_db)):
    """
    実験を作成

    Args:
        experiment: 実験作成リクエスト

    Returns:
        作成された実験情報
    """
    return cruds.add_experiment(
        db=db,
        model_version_id=experiment.model_version_id,
        model_id=experiment.model_id,
        parameters=experiment.parameters,
        training_dataset=experiment.training_dataset,
        validation_dataset=experiment.validation_dataset,
        test_dataset=experiment.test_dataset,
        evaluations=experiment.evaluations,
        artifact_file_paths=experiment.artifact_file_paths,
        commit=True,
    )


@router.post("/experiments/evaluations/{experiment_id}", response_model=schemas.Experiment)
def update_evaluations(
    experiment_id: str,
    evaluations: schemas.ExperimentEvaluations,
    db: Session = Depends(get_db),
):
    """
    実験の評価結果を更新

    Args:
        experiment_id: 実験ID
        evaluations: 新しい評価結果

    Returns:
        更新された実験情報
    """
    return cruds.update_experiment_evaluation(
        db=db,
        experiment_id=experiment_id,
        evaluations=evaluations.evaluations,
    )


@router.post("/experiments/artifact-file-paths/{experiment_id}", response_model=schemas.Experiment)
def update_artifact_file_paths(
    experiment_id: str,
    artifact_file_paths: schemas.ExperimentArtifactFilePaths,
    db: Session = Depends(get_db),
):
    """
    実験のモデルファイルパスを更新

    Args:
        experiment_id: 実験ID
        artifact_file_paths: 新しいモデルファイルのパス

    Returns:
        更新された実験情報
    """
    return cruds.update_experiment_artifact_file_paths(
        db=db,
        experiment_id=experiment_id,
        artifact_file_paths=artifact_file_paths.artifact_file_paths,
    )
