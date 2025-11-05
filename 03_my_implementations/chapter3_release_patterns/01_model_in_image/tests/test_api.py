"""
FastAPI エンドポイントの統合テスト

このモジュールはFastAPIアプリケーションの各エンドポイントをテストします。
- ヘルスチェック
- メタデータ
- ラベル取得
- 推論（確率値）
- 推論（ラベル名）
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.model_in_image import app as app_module
from src.model_in_image.app import app
from src.model_in_image.prediction import Classifier


# テスト用の定数
TEST_MODEL_PATH = Path(__file__).parent.parent / "models" / "iris_svc.onnx"
TEST_LABEL_PATH = Path(__file__).parent.parent / "models" / "label.json"


@pytest.fixture
def client() -> TestClient:
    """テスト用のFastAPIクライアントを返すフィクスチャ"""
    # テスト用にclassifierを初期化
    app_module.classifier = Classifier(
        model_filepath=str(TEST_MODEL_PATH),
        label_filepath=str(TEST_LABEL_PATH),
    )
    return TestClient(app)


class TestHealthEndpoint:
    """ヘルスチェックエンドポイントのテスト"""

    def test_health_check(self, client: TestClient):
        """ヘルスチェックが正常に動作するかテスト"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"health": "ok"}

    def test_health_check_method_not_allowed(self, client: TestClient):
        """POST メソッドが許可されていないかテスト"""
        response = client.post("/health")
        assert response.status_code == 405  # Method Not Allowed


class TestMetadataEndpoint:
    """メタデータエンドポイントのテスト"""

    def test_metadata(self, client: TestClient):
        """メタデータが正しく返されるかテスト"""
        response = client.get("/metadata")
        assert response.status_code == 200

        data = response.json()
        assert "data_type" in data
        assert "data_structure" in data
        assert "data_sample" in data
        assert "prediction_type" in data
        assert "prediction_structure" in data
        assert "prediction_sample" in data

        # データ型の確認
        assert data["data_type"] == "float32"
        assert data["prediction_type"] == "float32"

        # データ構造の確認
        assert data["data_structure"] == "(1,4)"
        assert data["prediction_structure"] == "(1,3)"

        # サンプルデータの確認
        assert isinstance(data["data_sample"], list)
        assert isinstance(data["prediction_sample"], list)
        assert len(data["data_sample"][0]) == 4  # 4特徴量
        assert len(data["prediction_sample"]) == 3  # 3クラス


class TestLabelEndpoint:
    """ラベル取得エンドポイントのテスト"""

    def test_get_labels(self, client: TestClient):
        """ラベル一覧が正しく返されるかテスト"""
        response = client.get("/label")
        assert response.status_code == 200

        labels = response.json()
        assert isinstance(labels, dict)
        assert "0" in labels
        assert "1" in labels
        assert "2" in labels
        assert labels["0"] == "setosa"
        assert labels["1"] == "versicolor"
        assert labels["2"] == "virginica"


class TestPredictTestEndpoint:
    """テスト推論エンドポイントのテスト"""

    def test_predict_test(self, client: TestClient):
        """テスト推論（確率）が正常に動作するかテスト"""
        response = client.get("/predict/test")
        assert response.status_code == 200

        data = response.json()
        assert "prediction" in data
        assert isinstance(data["prediction"], list)
        assert len(data["prediction"]) == 3  # 3クラス分の確率

        # 確率値の範囲確認
        for prob in data["prediction"]:
            assert 0.0 <= prob <= 1.0

    def test_predict_test_label(self, client: TestClient):
        """テスト推論（ラベル）が正常に動作するかテスト"""
        response = client.get("/predict/test/label")
        assert response.status_code == 200

        data = response.json()
        assert "prediction" in data
        assert isinstance(data["prediction"], str)
        assert data["prediction"] in ["setosa", "versicolor", "virginica"]


class TestPredictEndpoint:
    """推論エンドポイントのテスト"""

    def test_predict_setosa(self, client: TestClient):
        """setosaの推論が正常に動作するかテスト"""
        payload = {"data": [[5.1, 3.5, 1.4, 0.2]]}
        response = client.post("/predict", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "prediction" in data
        assert isinstance(data["prediction"], list)
        assert len(data["prediction"]) == 3

        # setosa（クラス0）の確率が最も高いことを確認
        prediction = data["prediction"]
        assert prediction[0] > prediction[1]
        assert prediction[0] > prediction[2]

    def test_predict_versicolor(self, client: TestClient):
        """versicolorの推論が正常に動作するかテスト"""
        payload = {"data": [[5.9, 3.0, 4.2, 1.5]]}
        response = client.post("/predict", json=payload)
        assert response.status_code == 200

        data = response.json()
        prediction = data["prediction"]
        # versicolor（クラス1）の確率が最も高いことを確認
        assert prediction[1] > prediction[0]
        assert prediction[1] > prediction[2]

    def test_predict_virginica(self, client: TestClient):
        """virginicaの推論が正常に動作するかテスト"""
        payload = {"data": [[6.3, 2.9, 5.6, 1.8]]}
        response = client.post("/predict", json=payload)
        assert response.status_code == 200

        data = response.json()
        prediction = data["prediction"]
        # virginica（クラス2）の確率が最も高いことを確認
        assert prediction[2] > prediction[0]
        assert prediction[2] > prediction[1]

    def test_predict_label_setosa(self, client: TestClient):
        """setosaのラベル推論が正常に動作するかテスト"""
        payload = {"data": [[5.1, 3.5, 1.4, 0.2]]}
        response = client.post("/predict/label", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "prediction" in data
        assert data["prediction"] == "setosa"

    def test_predict_label_versicolor(self, client: TestClient):
        """versicolorのラベル推論が正常に動作するかテスト"""
        payload = {"data": [[5.9, 3.0, 4.2, 1.5]]}
        response = client.post("/predict/label", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["prediction"] == "versicolor"

    def test_predict_label_virginica(self, client: TestClient):
        """virginicaのラベル推論が正常に動作するかテスト"""
        payload = {"data": [[6.3, 2.9, 5.6, 1.8]]}
        response = client.post("/predict/label", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["prediction"] == "virginica"

    def test_predict_invalid_data_missing_field(self, client: TestClient):
        """dataフィールドがない場合にデフォルト値が使用されるかテスト"""
        payload = {}  # dataフィールドがない
        response = client.post("/predict", json=payload)
        # Dataモデルにデフォルト値があるため、200が返される
        assert response.status_code == 200
        # デフォルトのsetosaデータで推論が実行される
        data = response.json()
        assert "prediction" in data
        # setosaの確率が最も高いことを確認
        prediction = data["prediction"]
        assert prediction[0] > prediction[1]
        assert prediction[0] > prediction[2]

    def test_predict_invalid_data_wrong_type(self, client: TestClient):
        """データ型が間違っている場合にエラーが返されるかテスト"""
        payload = {"data": "invalid"}  # dataがstringになっている
        response = client.post("/predict", json=payload)
        assert response.status_code == 422

    def test_predict_invalid_data_wrong_shape(self, client: TestClient):
        """データの形状が間違っている場合にエラーが返されるかテスト"""
        payload = {"data": [[5.1, 3.5, 1.4]]}  # 特徴量が3つしかない
        response = client.post("/predict", json=payload)
        # 500エラーまたは400エラーが返される
        assert response.status_code in [400, 500]

    def test_predict_empty_data(self, client: TestClient):
        """空のデータでエラーが返されるかテスト"""
        payload = {"data": []}
        response = client.post("/predict", json=payload)
        assert response.status_code in [400, 422, 500]

    def test_predict_method_not_allowed(self, client: TestClient):
        """GET メソッドが許可されていないかテスト"""
        response = client.get("/predict")
        assert response.status_code == 405  # Method Not Allowed


class TestRootEndpoint:
    """ルートエンドポイントのテスト"""

    def test_root_redirect_or_docs(self, client: TestClient):
        """ルートパスがドキュメントまたはリダイレクトを返すかテスト"""
        response = client.get("/")
        # FastAPIのデフォルトでは、/はリダイレクトされるか404を返す
        # または、カスタムルートエンドポイントがある場合は200を返す
        assert response.status_code in [200, 404, 307]

    def test_docs_endpoint(self, client: TestClient):
        """APIドキュメントエンドポイントが存在するかテスト"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json(self, client: TestClient):
        """OpenAPI JSONが取得できるかテスト"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()
        assert "info" in response.json()
        assert "paths" in response.json()
