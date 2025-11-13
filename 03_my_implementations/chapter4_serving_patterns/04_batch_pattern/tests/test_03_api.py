"""API層のユニットテスト

FastAPIエンドポイントのテストを実施します。
"""

import pytest
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """APIエンドポイントのテスト"""

    def test_root(self, client: TestClient):
        """ルートエンドポイントをテスト"""
        response = client.get("/")

        assert response.status_code == 200
        assert response.json()["status"] == "Batch Pattern API is running"

    def test_health_check(self, client: TestClient):
        """ヘルスチェックエンドポイントをテスト"""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_get_metadata(self, client: TestClient):
        """メタデータ取得エンドポイントをテスト"""
        response = client.get("/metadata")

        assert response.status_code == 200

        data = response.json()
        assert data["model_name"] == "iris_svc"
        assert data["model_type"] == "ONNX"
        assert data["input_dim"] == 4
        assert data["output_dim"] == 3
        assert "labels" in data


class TestDataRegistration:
    """データ登録エンドポイントのテスト"""

    def test_register_single_data(self, client: TestClient, sample_item_data: dict):
        """単一データ登録をテスト"""
        response = client.post("/data", json=sample_item_data)

        assert response.status_code == 200

        data = response.json()
        assert data["id"] is not None
        assert data["values"] == sample_item_data["values"]
        assert data["prediction"] is None

    def test_register_multiple_data(self, client: TestClient, sample_items_data: list):
        """複数データ一括登録をテスト"""
        payload = {"items": sample_items_data}
        response = client.post("/data/list", json=payload)

        assert response.status_code == 200

        data = response.json()
        assert len(data) == len(sample_items_data)

        for i, item in enumerate(data):
            assert item["id"] is not None
            assert item["values"] == sample_items_data[i]["values"]
            assert item["prediction"] is None

    def test_register_invalid_data(self, client: TestClient):
        """無効なデータ登録をテスト"""
        invalid_data = {"values": [1.0, 2.0, 3.0]}  # 3次元（4次元必須）
        response = client.post("/data", json=invalid_data)

        assert response.status_code == 422  # Validation Error


class TestDataRetrieval:
    """データ取得エンドポイントのテスト"""

    def test_get_all_data(self, client: TestClient, sample_items_data: list):
        """全データ取得をテスト"""
        # データを登録
        payload = {"items": sample_items_data}
        client.post("/data/list", json=payload)

        # 全データ取得
        response = client.get("/data/all")

        assert response.status_code == 200

        data = response.json()
        assert len(data) == len(sample_items_data)

    def test_get_unpredicted_data(self, client: TestClient, sample_items_data: list):
        """未推論データ取得をテスト"""
        # データを登録
        payload = {"items": sample_items_data}
        client.post("/data/list", json=payload)

        # 未推論データ取得
        response = client.get("/data/unpredicted")

        assert response.status_code == 200

        data = response.json()
        assert len(data) == len(sample_items_data)

        for item in data:
            assert item["prediction"] is None

    def test_get_predicted_data_empty(self, client: TestClient, sample_items_data: list):
        """推論済みデータ取得（空）をテスト"""
        # データを登録（推論なし）
        payload = {"items": sample_items_data}
        client.post("/data/list", json=payload)

        # 推論済みデータ取得
        response = client.get("/data/predicted")

        assert response.status_code == 200

        data = response.json()
        assert len(data) == 0  # 推論済みデータはない

    def test_get_data_by_id(self, client: TestClient, sample_item_data: dict):
        """ID指定データ取得をテスト"""
        # データを登録
        register_response = client.post("/data", json=sample_item_data)
        registered_item = register_response.json()

        # ID指定で取得
        response = client.get(f"/data/{registered_item['id']}")

        assert response.status_code == 200

        data = response.json()
        assert data["id"] == registered_item["id"]
        assert data["values"] == sample_item_data["values"]

    def test_get_data_by_id_not_found(self, client: TestClient):
        """存在しないID指定データ取得をテスト"""
        response = client.get("/data/9999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestDataFlow:
    """データフロー統合テスト"""

    def test_complete_data_flow(self, client: TestClient):
        """
        完全なデータフロー（登録→取得→確認）をテスト
        """
        # 1. データ登録
        data = {"values": [5.1, 3.5, 1.4, 0.2]}
        register_response = client.post("/data", json=data)
        assert register_response.status_code == 200
        registered_item = register_response.json()

        # 2. 全データ取得
        all_response = client.get("/data/all")
        assert all_response.status_code == 200
        all_data = all_response.json()
        assert len(all_data) >= 1

        # 3. 未推論データ取得
        unpredicted_response = client.get("/data/unpredicted")
        assert unpredicted_response.status_code == 200
        unpredicted_data = unpredicted_response.json()
        assert len(unpredicted_data) >= 1
        assert registered_item["id"] in [item["id"] for item in unpredicted_data]

        # 4. ID指定取得
        id_response = client.get(f"/data/{registered_item['id']}")
        assert id_response.status_code == 200
        id_data = id_response.json()
        assert id_data["id"] == registered_item["id"]
        assert id_data["values"] == data["values"]
        assert id_data["prediction"] is None
