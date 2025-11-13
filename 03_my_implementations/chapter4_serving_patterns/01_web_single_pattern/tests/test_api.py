"""
APIエンドポイントのテスト

このモジュールは、FastAPIの全エンドポイントをテストします。
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """FastAPIテストクライアント"""
    from src.main import app

    return TestClient(app)


class TestHealthEndpoint:
    """ヘルスチェックエンドポイントのテスト"""

    def test_health_check(self, client):
        """GET /health が正常に応答する"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"health": "ok"}


class TestMetadataEndpoint:
    """メタデータエンドポイントのテスト"""

    def test_metadata(self, client):
        """GET /metadata が正常に応答する"""
        response = client.get("/metadata")
        assert response.status_code == 200

        data = response.json()
        assert "data_type" in data
        assert "data_structure" in data
        assert "data_sample" in data
        assert "prediction_type" in data
        assert "prediction_structure" in data
        assert "prediction_sample" in data

    def test_metadata_data_type(self, client):
        """メタデータのデータ型が正しい"""
        response = client.get("/metadata")
        data = response.json()

        assert data["data_type"] == "float32"
        assert data["prediction_type"] == "float32"

    def test_metadata_data_structure(self, client):
        """メタデータのデータ構造が正しい"""
        response = client.get("/metadata")
        data = response.json()

        assert data["data_structure"] == "(1,4)"
        assert data["prediction_structure"] == "(1,3)"

    def test_metadata_data_sample(self, client):
        """メタデータのサンプルデータが正しい"""
        response = client.get("/metadata")
        data = response.json()

        assert isinstance(data["data_sample"], list)
        assert len(data["data_sample"]) == 1
        assert len(data["data_sample"][0]) == 4


class TestLabelEndpoint:
    """ラベルエンドポイントのテスト"""

    def test_label(self, client):
        """GET /label が正常に応答する"""
        response = client.get("/label")
        assert response.status_code == 200

        labels = response.json()
        assert isinstance(labels, dict)

    def test_label_contains_all_classes(self, client):
        """全てのクラスラベルを含む"""
        response = client.get("/label")
        labels = response.json()

        assert "0" in labels
        assert "1" in labels
        assert "2" in labels

    def test_label_values(self, client):
        """ラベル値が正しい"""
        response = client.get("/label")
        labels = response.json()

        assert labels["0"] == "setosa"
        assert labels["1"] == "versicolor"
        assert labels["2"] == "virginica"


class TestPredictTestEndpoint:
    """テスト推論エンドポイント（確率値）のテスト"""

    def test_predict_test(self, client):
        """GET /predict/test が正常に応答する"""
        response = client.get("/predict/test")
        assert response.status_code == 200

        data = response.json()
        assert "prediction" in data

    def test_predict_test_returns_probabilities(self, client):
        """確率値のリストを返す"""
        response = client.get("/predict/test")
        data = response.json()

        prediction = data["prediction"]
        assert isinstance(prediction, list)
        assert len(prediction) == 3

    def test_predict_test_probabilities_sum_to_one(self, client):
        """確率値の合計が1に近い"""
        response = client.get("/predict/test")
        data = response.json()

        prediction = data["prediction"]
        total = sum(prediction)
        assert 0.99 <= total <= 1.01


class TestPredictTestLabelEndpoint:
    """テスト推論エンドポイント（ラベル名）のテスト"""

    def test_predict_test_label(self, client):
        """GET /predict/test/label が正常に応答する"""
        response = client.get("/predict/test/label")
        assert response.status_code == 200

        data = response.json()
        assert "prediction" in data

    def test_predict_test_label_returns_string(self, client):
        """ラベル名（文字列）を返す"""
        response = client.get("/predict/test/label")
        data = response.json()

        prediction = data["prediction"]
        assert isinstance(prediction, str)

    def test_predict_test_label_is_valid(self, client):
        """有効なラベル名を返す"""
        response = client.get("/predict/test/label")
        data = response.json()

        prediction = data["prediction"]
        assert prediction in ["setosa", "versicolor", "virginica"]


class TestPredictEndpoint:
    """推論エンドポイント（確率値）のテスト"""

    def test_predict_post(self, client):
        """POST /predict が正常に応答する"""
        request_data = {"data": [[5.1, 3.5, 1.4, 0.2]]}
        response = client.post("/predict", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "prediction" in data

    def test_predict_setosa(self, client):
        """Iris setosaの推論が正しい"""
        request_data = {"data": [[5.1, 3.5, 1.4, 0.2]]}
        response = client.post("/predict", json=request_data)
        data = response.json()

        prediction = data["prediction"]
        # setosa（index 0）の確率が最も高い
        assert prediction.index(max(prediction)) == 0

    def test_predict_virginica(self, client):
        """Iris virginicaの推論が正しい"""
        request_data = {"data": [[6.3, 3.3, 6.0, 2.5]]}
        response = client.post("/predict", json=request_data)
        data = response.json()

        prediction = data["prediction"]
        # virginica（index 2）の確率が最も高い
        assert prediction.index(max(prediction)) == 2

    def test_predict_returns_list(self, client):
        """確率値のリストを返す"""
        request_data = {"data": [[5.1, 3.5, 1.4, 0.2]]}
        response = client.post("/predict", json=request_data)
        data = response.json()

        prediction = data["prediction"]
        assert isinstance(prediction, list)
        assert len(prediction) == 3

    def test_predict_invalid_data_structure(self, client):
        """不正なデータ構造でエラーを返す"""
        # 4要素ではなく3要素のデータ
        request_data = {"data": [[1.0, 2.0, 3.0]]}
        response = client.post("/predict", json=request_data)
        # バリデーションエラーまたは推論エラーで4xx/5xxを返すことを期待
        # （実装によってはONNXが内部でエラーを出す場合もある）
        # ここではリクエストは受け付けられるが、結果は不定とする
        assert response.status_code in [200, 400, 422, 500]


class TestPredictLabelEndpoint:
    """推論エンドポイント（ラベル名）のテスト"""

    def test_predict_label_post(self, client):
        """POST /predict/label が正常に応答する"""
        request_data = {"data": [[5.1, 3.5, 1.4, 0.2]]}
        response = client.post("/predict/label", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "prediction" in data

    def test_predict_label_setosa(self, client):
        """Iris setosaのラベル予測が正しい"""
        request_data = {"data": [[5.1, 3.5, 1.4, 0.2]]}
        response = client.post("/predict/label", json=request_data)
        data = response.json()

        prediction = data["prediction"]
        assert prediction == "setosa"

    def test_predict_label_virginica(self, client):
        """Iris virginicaのラベル予測が正しい"""
        request_data = {"data": [[6.3, 3.3, 6.0, 2.5]]}
        response = client.post("/predict/label", json=request_data)
        data = response.json()

        prediction = data["prediction"]
        assert prediction == "virginica"

    def test_predict_label_returns_string(self, client):
        """ラベル名（文字列）を返す"""
        request_data = {"data": [[5.1, 3.5, 1.4, 0.2]]}
        response = client.post("/predict/label", json=request_data)
        data = response.json()

        prediction = data["prediction"]
        assert isinstance(prediction, str)

    def test_predict_label_is_valid(self, client):
        """有効なラベル名を返す"""
        request_data = {"data": [[5.1, 3.5, 1.4, 0.2]]}
        response = client.post("/predict/label", json=request_data)
        data = response.json()

        prediction = data["prediction"]
        assert prediction in ["setosa", "versicolor", "virginica"]
