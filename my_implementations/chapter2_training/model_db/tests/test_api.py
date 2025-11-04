"""
API層の統合テスト

このテストでは、FastAPIのエンドポイントをテストします。
TDD - Redフェーズ：まず失敗するテストを書きます。
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.db.database import Base, get_db
from src.api.app import app


# テスト用インメモリデータベース
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_client():
    """テスト用クライアントを作成"""
    # StaticPoolを使用してインメモリDBで複数スレッドから同じ接続を使えるようにする
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # テーブル作成
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # 依存性を上書き
    app.dependency_overrides[get_db] = override_get_db

    # TestClientを作成してテストを実行
    client = TestClient(app)
    yield client

    # クリーンアップ
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


class TestHealthEndpoint:
    """ヘルスチェックエンドポイントのテスト"""

    def test_health_check(self, test_client):
        """ヘルスチェックが正常に動作する"""
        response = test_client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestProjectEndpoints:
    """プロジェクト関連のエンドポイントテスト"""

    def test_create_project(self, test_client):
        """プロジェクト作成APIが正常に動作する"""
        response = test_client.post(
            "/projects",
            json={"project_name": "test_project", "description": "Test description"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["project_name"] == "test_project"
        assert data["description"] == "Test description"
        assert "project_id" in data
        assert "created_datetime" in data

    def test_create_project_minimal(self, test_client):
        """説明なしでプロジェクト作成できる"""
        response = test_client.post(
            "/projects",
            json={"project_name": "minimal_project"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["project_name"] == "minimal_project"
        assert data["description"] is None

    def test_get_all_projects(self, test_client):
        """全プロジェクト取得APIが正常に動作する"""
        # プロジェクトを2つ作成
        test_client.post("/projects", json={"project_name": "project1"})
        test_client.post("/projects", json={"project_name": "project2"})

        response = test_client.get("/projects/all")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["project_name"] == "project1"
        assert data[1]["project_name"] == "project2"

    def test_get_project_by_id(self, test_client):
        """IDでプロジェクト取得APIが正常に動作する"""
        create_response = test_client.post(
            "/projects",
            json={"project_name": "test_project"},
        )
        project_id = create_response.json()["project_id"]

        response = test_client.get(f"/projects/id/{project_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == project_id
        assert data["project_name"] == "test_project"

    def test_get_project_by_name(self, test_client):
        """名前でプロジェクト取得APIが正常に動作する"""
        test_client.post("/projects", json={"project_name": "unique_project"})

        response = test_client.get("/projects/name/unique_project")

        assert response.status_code == 200
        data = response.json()
        assert data["project_name"] == "unique_project"


class TestModelEndpoints:
    """モデル関連のエンドポイントテスト"""

    def test_create_model(self, test_client):
        """モデル作成APIが正常に動作する"""
        # まずプロジェクトを作成
        project_response = test_client.post(
            "/projects",
            json={"project_name": "test_project"},
        )
        project_id = project_response.json()["project_id"]

        # モデルを作成
        response = test_client.post(
            "/models",
            json={
                "project_id": project_id,
                "model_name": "test_model",
                "description": "Model description",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["model_name"] == "test_model"
        assert data["project_id"] == project_id
        assert data["description"] == "Model description"
        assert "model_id" in data
        assert "created_datetime" in data

    def test_get_all_models(self, test_client):
        """全モデル取得APIが正常に動作する"""
        project_response = test_client.post("/projects", json={"project_name": "test_project"})
        project_id = project_response.json()["project_id"]

        test_client.post("/models", json={"project_id": project_id, "model_name": "model1"})
        test_client.post("/models", json={"project_id": project_id, "model_name": "model2"})

        response = test_client.get("/models/all")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_model_by_id(self, test_client):
        """IDでモデル取得APIが正常に動作する"""
        project_response = test_client.post("/projects", json={"project_name": "test_project"})
        project_id = project_response.json()["project_id"]

        create_response = test_client.post(
            "/models",
            json={"project_id": project_id, "model_name": "test_model"},
        )
        model_id = create_response.json()["model_id"]

        response = test_client.get(f"/models/id/{model_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["model_id"] == model_id
        assert data["model_name"] == "test_model"

    def test_get_models_by_project_id(self, test_client):
        """プロジェクトIDでモデル取得APIが正常に動作する"""
        project_response = test_client.post("/projects", json={"project_name": "test_project"})
        project_id = project_response.json()["project_id"]

        test_client.post("/models", json={"project_id": project_id, "model_name": "model1"})
        test_client.post("/models", json={"project_id": project_id, "model_name": "model2"})

        response = test_client.get(f"/models/project-id/{project_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(m["project_id"] == project_id for m in data)


class TestExperimentEndpoints:
    """実験関連のエンドポイントテスト"""

    def test_create_experiment(self, test_client):
        """実験作成APIが正常に動作する"""
        # プロジェクトとモデルを作成
        project_response = test_client.post("/projects", json={"project_name": "test_project"})
        project_id = project_response.json()["project_id"]

        model_response = test_client.post(
            "/models",
            json={"project_id": project_id, "model_name": "test_model"},
        )
        model_id = model_response.json()["model_id"]

        # 実験を作成
        response = test_client.post(
            "/experiments",
            json={
                "model_id": model_id,
                "model_version_id": "v1.0.0",
                "parameters": {"learning_rate": 0.001, "batch_size": 32},
                "training_dataset": "s3://bucket/train.csv",
                "validation_dataset": "s3://bucket/val.csv",
                "test_dataset": "s3://bucket/test.csv",
                "evaluations": {"accuracy": 0.95},
                "artifact_file_paths": {"model": "s3://bucket/model.pkl"},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["model_id"] == model_id
        assert data["model_version_id"] == "v1.0.0"
        assert data["parameters"]["learning_rate"] == 0.001
        assert data["evaluations"]["accuracy"] == 0.95
        assert "experiment_id" in data
        assert "created_datetime" in data

    def test_create_experiment_minimal(self, test_client):
        """最小限の情報で実験作成できる"""
        project_response = test_client.post("/projects", json={"project_name": "test_project"})
        project_id = project_response.json()["project_id"]

        model_response = test_client.post(
            "/models",
            json={"project_id": project_id, "model_name": "test_model"},
        )
        model_id = model_response.json()["model_id"]

        response = test_client.post(
            "/experiments",
            json={"model_id": model_id, "model_version_id": "v1.0.0"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["model_id"] == model_id
        assert data["model_version_id"] == "v1.0.0"
        assert data["parameters"] is None
        assert data["evaluations"] is None

    def test_get_all_experiments(self, test_client):
        """全実験取得APIが正常に動作する"""
        project_response = test_client.post("/projects", json={"project_name": "test_project"})
        project_id = project_response.json()["project_id"]

        model_response = test_client.post(
            "/models",
            json={"project_id": project_id, "model_name": "test_model"},
        )
        model_id = model_response.json()["model_id"]

        test_client.post("/experiments", json={"model_id": model_id, "model_version_id": "v1.0.0"})
        test_client.post("/experiments", json={"model_id": model_id, "model_version_id": "v1.0.1"})

        response = test_client.get("/experiments/all")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_experiment_by_id(self, test_client):
        """IDで実験取得APIが正常に動作する"""
        project_response = test_client.post("/projects", json={"project_name": "test_project"})
        project_id = project_response.json()["project_id"]

        model_response = test_client.post(
            "/models",
            json={"project_id": project_id, "model_name": "test_model"},
        )
        model_id = model_response.json()["model_id"]

        create_response = test_client.post(
            "/experiments",
            json={"model_id": model_id, "model_version_id": "v1.0.0"},
        )
        experiment_id = create_response.json()["experiment_id"]

        response = test_client.get(f"/experiments/id/{experiment_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["experiment_id"] == experiment_id

    def test_update_experiment_evaluations(self, test_client):
        """実験の評価結果更新APIが正常に動作する"""
        project_response = test_client.post("/projects", json={"project_name": "test_project"})
        project_id = project_response.json()["project_id"]

        model_response = test_client.post(
            "/models",
            json={"project_id": project_id, "model_name": "test_model"},
        )
        model_id = model_response.json()["model_id"]

        create_response = test_client.post(
            "/experiments",
            json={
                "model_id": model_id,
                "model_version_id": "v1.0.0",
                "evaluations": {"accuracy": 0.90},
            },
        )
        experiment_id = create_response.json()["experiment_id"]

        # 評価結果を更新
        response = test_client.post(
            f"/experiments/evaluations/{experiment_id}",
            json={"evaluations": {"f1_score": 0.88}},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["evaluations"]["accuracy"] == 0.90
        assert data["evaluations"]["f1_score"] == 0.88

    def test_update_experiment_artifact_file_paths(self, test_client):
        """実験のモデルファイルパス更新APIが正常に動作する"""
        project_response = test_client.post("/projects", json={"project_name": "test_project"})
        project_id = project_response.json()["project_id"]

        model_response = test_client.post(
            "/models",
            json={"project_id": project_id, "model_name": "test_model"},
        )
        model_id = model_response.json()["model_id"]

        create_response = test_client.post(
            "/experiments",
            json={
                "model_id": model_id,
                "model_version_id": "v1.0.0",
                "artifact_file_paths": {"model": "s3://bucket/model.pkl"},
            },
        )
        experiment_id = create_response.json()["experiment_id"]

        # ファイルパスを更新
        response = test_client.post(
            f"/experiments/artifact-file-paths/{experiment_id}",
            json={"artifact_file_paths": {"weights": "s3://bucket/weights.h5"}},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["artifact_file_paths"]["model"] == "s3://bucket/model.pkl"
        assert data["artifact_file_paths"]["weights"] == "s3://bucket/weights.h5"
