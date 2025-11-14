"""Proxy APIのテスト"""
import base64
import io
import json

import pytest
from PIL import Image
from fastapi.testclient import TestClient
from fakeredis import FakeRedis

from src.proxy.app import app
from src.configurations import AppConfig
import src.proxy.app as proxy_app


@pytest.fixture
def redis_client(monkeypatch):
    """FakeRedisクライアント"""
    fake_redis = FakeRedis(decode_responses=True)
    # アプリのredis_clientを置き換え
    monkeypatch.setattr(proxy_app, "redis_client", fake_redis)
    yield fake_redis
    # テスト後クリーンアップ
    fake_redis.flushdb()


@pytest.fixture
def client(redis_client):
    """FastAPIテストクライアント"""
    return TestClient(app)


@pytest.fixture
def test_image_base64():
    """テスト用画像（Base64）"""
    img = Image.new("RGB", (224, 224), color=(128, 128, 128))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()


def test_health_check(client):
    """ヘルスチェックエンドポイントのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_predict_endpoint(client, test_image_base64, redis_client):
    """推論エンドポイントのテスト"""
    # リクエスト
    response = client.post(
        "/predict",
        json={"image_data": test_image_base64}
    )

    # ステータスコード確認
    assert response.status_code == 200

    # レスポンス形式確認
    data = response.json()
    assert "job_id" in data
    assert "result_sync" in data

    # 同期結果は即座に返る
    assert isinstance(data["result_sync"], str)
    assert len(data["result_sync"]) > 0

    # job_idはUUID形式
    job_id = data["job_id"]
    assert len(job_id) == 36  # UUID形式

    # Redisにジョブが登録されているか確認
    job_data = redis_client.get(f"job:{job_id}")
    assert job_data is not None
    job_dict = json.loads(job_data)
    assert job_dict["image_data"] == test_image_base64
    assert job_dict["status"] == "pending"


def test_job_result_endpoint_pending(client, redis_client):
    """ジョブ結果取得（処理中）のテスト"""
    # テスト用ジョブを登録
    job_id = "test-job-id-12345"
    redis_client.setex(
        f"job:{job_id}",
        AppConfig.RESULT_TTL,
        json.dumps({"status": "pending", "image_data": "dummy"})
    )

    # 結果取得
    response = client.get(f"/job/{job_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["prediction"] == ""  # 処理中なら空文字列


def test_job_result_endpoint_completed(client, redis_client):
    """ジョブ結果取得（完了）のテスト"""
    # テスト用ジョブを登録（完了状態）
    job_id = "test-job-id-67890"
    redis_client.setex(
        f"job:{job_id}",
        AppConfig.RESULT_TTL,
        json.dumps({"status": "completed", "result": "tabby cat"})
    )

    # 結果取得
    response = client.get(f"/job/{job_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["prediction"] == "tabby cat"


def test_job_result_endpoint_not_found(client):
    """存在しないジョブIDのテスト"""
    response = client.get("/job/non-existent-job-id")
    assert response.status_code == 404
