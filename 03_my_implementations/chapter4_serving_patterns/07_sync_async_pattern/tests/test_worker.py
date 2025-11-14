"""Workerのテスト"""
import base64
import io
import json
import time

import pytest
from PIL import Image
from fakeredis import FakeRedis

from src.worker.worker import process_job
from src.configurations import AppConfig


@pytest.fixture
def redis_client():
    """FakeRedisクライアント"""
    fake_redis = FakeRedis(decode_responses=True)
    yield fake_redis
    fake_redis.flushdb()


@pytest.fixture
def test_image_base64():
    """テスト用画像（Base64）"""
    img = Image.new("RGB", (224, 224), color=(128, 128, 128))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()


def test_process_job(redis_client, test_image_base64):
    """ジョブ処理のテスト"""
    # ジョブを登録
    job_id = "test-job-id-12345"
    job_data = {
        "image_data": test_image_base64,
        "status": "pending"
    }
    redis_client.setex(
        f"job:{job_id}",
        AppConfig.RESULT_TTL,
        json.dumps(job_data)
    )

    # ジョブ処理
    result = process_job(job_id, redis_client)

    # 結果確認
    assert isinstance(result, str)
    assert len(result) > 0

    # Redisに結果が保存されているか確認
    updated_job = redis_client.get(f"job:{job_id}")
    assert updated_job is not None
    updated_data = json.loads(updated_job)
    assert updated_data["status"] == "completed"
    assert updated_data["result"] == result


def test_process_job_not_found(redis_client):
    """存在しないジョブのテスト"""
    # 存在しないジョブIDを処理
    result = process_job("non-existent-job", redis_client)

    # Noneが返る
    assert result is None


def test_process_job_invalid_data(redis_client):
    """無効なデータのテスト"""
    # 無効なデータを登録
    job_id = "invalid-job"
    redis_client.setex(
        f"job:{job_id}",
        AppConfig.RESULT_TTL,
        json.dumps({"status": "pending", "image_data": "invalid-base64"})
    )

    # 処理時にエラーが起きても正常に処理される
    result = process_job(job_id, redis_client)

    # エラー時はNoneが返る
    assert result is None
