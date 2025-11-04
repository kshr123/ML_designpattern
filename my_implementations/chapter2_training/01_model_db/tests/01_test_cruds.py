"""
CRUD層のユニットテスト

このテストでは、データベース操作のビジネスロジックをテストします。
TDD - Redフェーズ：まず失敗するテストを書きます。
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.database import Base
from src.db import cruds, models


# テスト用インメモリデータベース
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """テスト用データベースセッションを作成"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # テーブル作成
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


class TestProjectCRUD:
    """プロジェクト関連のCRUD操作テスト"""

    def test_add_project_success(self, db_session):
        """プロジェクト作成が成功する"""
        project = cruds.add_project(
            db=db_session,
            project_name="test_project",
            description="Test description",
            commit=True,
        )

        assert project.project_id is not None
        assert project.project_name == "test_project"
        assert project.description == "Test description"
        assert project.created_datetime is not None

    def test_add_project_duplicate_returns_existing(self, db_session):
        """同名プロジェクトを作成すると既存のプロジェクトが返される"""
        project1 = cruds.add_project(
            db=db_session,
            project_name="duplicate_project",
            description="First",
            commit=True,
        )

        project2 = cruds.add_project(
            db=db_session,
            project_name="duplicate_project",
            description="Second",
            commit=True,
        )

        assert project1.project_id == project2.project_id
        assert project2.description == "First"  # 既存のものが返される

    def test_select_project_all(self, db_session):
        """全プロジェクトを取得できる"""
        cruds.add_project(db=db_session, project_name="project1", commit=True)
        cruds.add_project(db=db_session, project_name="project2", commit=True)

        projects = cruds.select_project_all(db=db_session)

        assert len(projects) == 2
        assert projects[0].project_name == "project1"
        assert projects[1].project_name == "project2"

    def test_select_project_by_id(self, db_session):
        """IDでプロジェクトを取得できる"""
        created_project = cruds.add_project(
            db=db_session,
            project_name="test_project",
            commit=True,
        )

        found_project = cruds.select_project_by_id(
            db=db_session,
            project_id=created_project.project_id,
        )

        assert found_project is not None
        assert found_project.project_id == created_project.project_id
        assert found_project.project_name == "test_project"

    def test_select_project_by_name(self, db_session):
        """名前でプロジェクトを取得できる"""
        cruds.add_project(db=db_session, project_name="unique_project", commit=True)

        found_project = cruds.select_project_by_name(
            db=db_session,
            project_name="unique_project",
        )

        assert found_project is not None
        assert found_project.project_name == "unique_project"

    def test_select_project_by_name_not_found(self, db_session):
        """存在しない名前で検索するとNoneが返る"""
        found_project = cruds.select_project_by_name(
            db=db_session,
            project_name="nonexistent",
        )

        assert found_project is None


class TestModelCRUD:
    """モデル関連のCRUD操作テスト"""

    def test_add_model_success(self, db_session):
        """モデル作成が成功する"""
        project = cruds.add_project(db=db_session, project_name="test_project", commit=True)

        model = cruds.add_model(
            db=db_session,
            project_id=project.project_id,
            model_name="test_model",
            description="Model description",
            commit=True,
        )

        assert model.model_id is not None
        assert model.project_id == project.project_id
        assert model.model_name == "test_model"
        assert model.description == "Model description"
        assert model.created_datetime is not None

    def test_add_model_duplicate_in_project_returns_existing(self, db_session):
        """同一プロジェクト内で同名モデルを作成すると既存が返される"""
        project = cruds.add_project(db=db_session, project_name="test_project", commit=True)

        model1 = cruds.add_model(
            db=db_session,
            project_id=project.project_id,
            model_name="duplicate_model",
            description="First",
            commit=True,
        )

        model2 = cruds.add_model(
            db=db_session,
            project_id=project.project_id,
            model_name="duplicate_model",
            description="Second",
            commit=True,
        )

        assert model1.model_id == model2.model_id
        assert model2.description == "First"

    def test_select_model_all(self, db_session):
        """全モデルを取得できる"""
        project = cruds.add_project(db=db_session, project_name="test_project", commit=True)

        cruds.add_model(db=db_session, project_id=project.project_id, model_name="model1", commit=True)
        cruds.add_model(db=db_session, project_id=project.project_id, model_name="model2", commit=True)

        models = cruds.select_model_all(db=db_session)

        assert len(models) == 2

    def test_select_model_by_id(self, db_session):
        """IDでモデルを取得できる"""
        project = cruds.add_project(db=db_session, project_name="test_project", commit=True)
        created_model = cruds.add_model(
            db=db_session,
            project_id=project.project_id,
            model_name="test_model",
            commit=True,
        )

        found_model = cruds.select_model_by_id(
            db=db_session,
            model_id=created_model.model_id,
        )

        assert found_model is not None
        assert found_model.model_id == created_model.model_id
        assert found_model.model_name == "test_model"

    def test_select_model_by_project_id(self, db_session):
        """プロジェクトIDでモデルを取得できる"""
        project = cruds.add_project(db=db_session, project_name="test_project", commit=True)

        cruds.add_model(db=db_session, project_id=project.project_id, model_name="model1", commit=True)
        cruds.add_model(db=db_session, project_id=project.project_id, model_name="model2", commit=True)

        models = cruds.select_model_by_project_id(
            db=db_session,
            project_id=project.project_id,
        )

        assert len(models) == 2
        assert models[0].project_id == project.project_id
        assert models[1].project_id == project.project_id


class TestExperimentCRUD:
    """実験関連のCRUD操作テスト"""

    def test_add_experiment_success(self, db_session):
        """実験作成が成功する"""
        project = cruds.add_project(db=db_session, project_name="test_project", commit=True)
        model = cruds.add_model(
            db=db_session,
            project_id=project.project_id,
            model_name="test_model",
            commit=True,
        )

        experiment = cruds.add_experiment(
            db=db_session,
            model_id=model.model_id,
            model_version_id="v1.0.0",
            parameters={"learning_rate": 0.001, "batch_size": 32},
            training_dataset="s3://bucket/train.csv",
            validation_dataset="s3://bucket/val.csv",
            test_dataset="s3://bucket/test.csv",
            evaluations={"accuracy": 0.95},
            artifact_file_paths={"model": "s3://bucket/model.pkl"},
            commit=True,
        )

        assert experiment.experiment_id is not None
        assert experiment.model_id == model.model_id
        assert experiment.model_version_id == "v1.0.0"
        assert experiment.parameters["learning_rate"] == 0.001
        assert experiment.evaluations["accuracy"] == 0.95
        assert experiment.created_datetime is not None

    def test_select_experiment_by_id(self, db_session):
        """IDで実験を取得できる"""
        project = cruds.add_project(db=db_session, project_name="test_project", commit=True)
        model = cruds.add_model(db=db_session, project_id=project.project_id, model_name="test_model", commit=True)
        created_experiment = cruds.add_experiment(
            db=db_session,
            model_id=model.model_id,
            model_version_id="v1.0.0",
            commit=True,
        )

        found_experiment = cruds.select_experiment_by_id(
            db=db_session,
            experiment_id=created_experiment.experiment_id,
        )

        assert found_experiment is not None
        assert found_experiment.experiment_id == created_experiment.experiment_id

    def test_update_experiment_evaluation(self, db_session):
        """実験の評価結果を更新できる"""
        project = cruds.add_project(db=db_session, project_name="test_project", commit=True)
        model = cruds.add_model(db=db_session, project_id=project.project_id, model_name="test_model", commit=True)
        experiment = cruds.add_experiment(
            db=db_session,
            model_id=model.model_id,
            model_version_id="v1.0.0",
            evaluations={"accuracy": 0.90},
            commit=True,
        )

        updated_experiment = cruds.update_experiment_evaluation(
            db=db_session,
            experiment_id=experiment.experiment_id,
            evaluations={"f1_score": 0.88},
        )

        assert updated_experiment.evaluations["accuracy"] == 0.90  # 既存の値
        assert updated_experiment.evaluations["f1_score"] == 0.88  # 新しい値

    def test_update_experiment_artifact_file_paths(self, db_session):
        """実験のモデルファイルパスを更新できる"""
        project = cruds.add_project(db=db_session, project_name="test_project", commit=True)
        model = cruds.add_model(db=db_session, project_id=project.project_id, model_name="test_model", commit=True)
        experiment = cruds.add_experiment(
            db=db_session,
            model_id=model.model_id,
            model_version_id="v1.0.0",
            artifact_file_paths={"model": "s3://bucket/model_v1.pkl"},
            commit=True,
        )

        updated_experiment = cruds.update_experiment_artifact_file_paths(
            db=db_session,
            experiment_id=experiment.experiment_id,
            artifact_file_paths={"weights": "s3://bucket/weights.h5"},
        )

        assert updated_experiment.artifact_file_paths["model"] == "s3://bucket/model_v1.pkl"
        assert updated_experiment.artifact_file_paths["weights"] == "s3://bucket/weights.h5"
