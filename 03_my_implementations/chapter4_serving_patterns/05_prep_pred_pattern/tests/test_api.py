"""API層テスト（FastAPIエンドポイント用）

TDDアプローチ:
1. Red Phase: このテストを実行して失敗することを確認
2. Green Phase: src/app/app.py と src/app/routers/ を実装
3. Refactor Phase: コードを改善
"""

import base64
import io
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image


# テスト対象のインポート（実装前なのでImportErrorになる）
from src.app.app import app


@pytest.fixture
def client():
    """TestClientのフィクスチャ"""
    return TestClient(app)


@pytest.fixture
def sample_image_base64():
    """テスト用Base64画像"""
    # 10x10の赤色画像を作成
    image = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


class TestHealthEndpoint:
    """ヘルスチェックエンドポイントのテスト"""

    def test_health_check_returns_200(self, client):
        """ヘルスチェックが200を返す"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self, client):
        """ヘルスチェックがhealthyステータスを返す"""
        response = client.get("/health")
        data = response.json()
        assert "health" in data
        assert data["health"] == "healthy"


class TestMetadataEndpoint:
    """メタデータエンドポイントのテスト"""

    def test_metadata_returns_200(self, client):
        """メタデータ取得が200を返す"""
        response = client.get("/metadata")
        assert response.status_code == 200

    def test_metadata_contains_data_type(self, client):
        """メタデータにdata_typeが含まれる"""
        response = client.get("/metadata")
        data = response.json()
        assert "data_type" in data

    def test_metadata_contains_data_structure(self, client):
        """メタデータにdata_structureが含まれる"""
        response = client.get("/metadata")
        data = response.json()
        assert "data_structure" in data

    def test_metadata_contains_data_sample(self, client):
        """メタデータにdata_sampleが含まれる"""
        response = client.get("/metadata")
        data = response.json()
        assert "data_sample" in data

    def test_metadata_contains_prediction_type(self, client):
        """メタデータにprediction_typeが含まれる"""
        response = client.get("/metadata")
        data = response.json()
        assert "prediction_type" in data


class TestLabelEndpoint:
    """ラベル取得エンドポイントのテスト"""

    def test_label_returns_200(self, client):
        """ラベル取得が200を返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.label = ["cat", "dog", "bird"]
            mock_get_classifier.return_value = mock_classifier

            response = client.get("/label")
            assert response.status_code == 200

    def test_label_returns_list(self, client):
        """ラベル取得がリストを返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.label = ["cat", "dog", "bird"]
            mock_get_classifier.return_value = mock_classifier

            response = client.get("/label")
            data = response.json()
            assert isinstance(data, list)

    def test_label_returns_imagenet_1000_classes(self, client):
        """ラベル取得がImageNet 1000クラスを返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.label = [f"class_{i}" for i in range(1000)]
            mock_get_classifier.return_value = mock_classifier

            response = client.get("/label")
            data = response.json()
            assert len(data) == 1000


class TestPredictTestEndpoint:
    """テスト画像推論エンドポイントのテスト"""

    def test_predict_test_returns_200(self, client):
        """テスト画像推論が200を返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.predict.return_value = [[0.1, 0.2, 0.7]]
            mock_get_classifier.return_value = mock_classifier

            response = client.get("/predict/test")
            assert response.status_code == 200

    def test_predict_test_returns_prediction_key(self, client):
        """テスト画像推論がpredictionキーを返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.predict.return_value = [[0.1, 0.2, 0.7]]
            mock_get_classifier.return_value = mock_classifier

            response = client.get("/predict/test")
            data = response.json()
            assert "prediction" in data

    def test_predict_test_returns_probability_array(self, client):
        """テスト画像推論が確率配列を返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.predict.return_value = [[0.1, 0.2, 0.7]]
            mock_get_classifier.return_value = mock_classifier

            response = client.get("/predict/test")
            data = response.json()
            assert isinstance(data["prediction"], list)
            assert isinstance(data["prediction"][0], list)


class TestPredictTestLabelEndpoint:
    """テスト画像ラベル推論エンドポイントのテスト"""

    def test_predict_test_label_returns_200(self, client):
        """テスト画像ラベル推論が200を返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.predict_label.return_value = "cat"
            mock_get_classifier.return_value = mock_classifier

            response = client.get("/predict/test/label")
            assert response.status_code == 200

    def test_predict_test_label_returns_prediction_key(self, client):
        """テスト画像ラベル推論がpredictionキーを返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.predict_label.return_value = "cat"
            mock_get_classifier.return_value = mock_classifier

            response = client.get("/predict/test/label")
            data = response.json()
            assert "prediction" in data

    def test_predict_test_label_returns_string(self, client):
        """テスト画像ラベル推論が文字列を返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.predict_label.return_value = "Siamese cat"
            mock_get_classifier.return_value = mock_classifier

            response = client.get("/predict/test/label")
            data = response.json()
            assert isinstance(data["prediction"], str)


class TestPredictEndpoint:
    """Base64画像推論エンドポイントのテスト"""

    def test_predict_returns_200(self, client, sample_image_base64):
        """Base64画像推論が200を返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.predict.return_value = [[0.1, 0.2, 0.7]]
            mock_get_classifier.return_value = mock_classifier

            response = client.post("/predict", json={"data": sample_image_base64})
            assert response.status_code == 200

    def test_predict_returns_prediction_key(self, client, sample_image_base64):
        """Base64画像推論がpredictionキーを返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.predict.return_value = [[0.1, 0.2, 0.7]]
            mock_get_classifier.return_value = mock_classifier

            response = client.post("/predict", json={"data": sample_image_base64})
            data = response.json()
            assert "prediction" in data

    def test_predict_accepts_base64_image(self, client, sample_image_base64):
        """Base64画像を受け付ける"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.predict.return_value = [[0.1, 0.2, 0.7]]
            mock_get_classifier.return_value = mock_classifier

            response = client.post("/predict", json={"data": sample_image_base64})
            assert response.status_code == 200

    def test_predict_requires_data_field(self, client):
        """dataフィールドが必須"""
        response = client.post("/predict", json={})
        # 422 Unprocessable Entity（バリデーションエラー）
        assert response.status_code == 422


class TestPredictLabelEndpoint:
    """Base64画像ラベル推論エンドポイントのテスト"""

    def test_predict_label_returns_200(self, client, sample_image_base64):
        """Base64画像ラベル推論が200を返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.predict_label.return_value = "cat"
            mock_get_classifier.return_value = mock_classifier

            response = client.post("/predict/label", json={"data": sample_image_base64})
            assert response.status_code == 200

    def test_predict_label_returns_prediction_key(self, client, sample_image_base64):
        """Base64画像ラベル推論がpredictionキーを返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.predict_label.return_value = "cat"
            mock_get_classifier.return_value = mock_classifier

            response = client.post("/predict/label", json={"data": sample_image_base64})
            data = response.json()
            assert "prediction" in data

    def test_predict_label_returns_string(self, client, sample_image_base64):
        """Base64画像ラベル推論が文字列を返す"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.predict_label.return_value = "Siamese cat"
            mock_get_classifier.return_value = mock_classifier

            response = client.post("/predict/label", json={"data": sample_image_base64})
            data = response.json()
            assert isinstance(data["prediction"], str)

    def test_predict_label_requires_data_field(self, client):
        """dataフィールドが必須"""
        response = client.post("/predict/label", json={})
        # 422 Unprocessable Entity（バリデーションエラー）
        assert response.status_code == 422


class TestAPIIntegration:
    """API統合テスト"""

    def test_all_endpoints_accessible(self, client):
        """全エンドポイントにアクセス可能"""
        with patch("src.app.routers.routers.get_classifier") as mock_get_classifier:
            mock_classifier = Mock()
            mock_classifier.label = ["cat"]
            mock_classifier.predict.return_value = [[0.1]]
            mock_classifier.predict_label.return_value = "cat"
            mock_get_classifier.return_value = mock_classifier

            # GET endpoints
            assert client.get("/health").status_code == 200
            assert client.get("/metadata").status_code == 200
            assert client.get("/label").status_code == 200
            assert client.get("/predict/test").status_code == 200
            assert client.get("/predict/test/label").status_code == 200
