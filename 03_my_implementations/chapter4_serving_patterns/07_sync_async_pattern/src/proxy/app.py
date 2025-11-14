"""Proxy APIサーバー

同期推論（MobileNet v2）と非同期推論（ResNet50）を提供
"""
import json
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from redis import Redis

from src.configurations import AppConfig
from src.ml.predictor import ONNXPredictor
from src.models import PredictRequest, PredictResponse, JobResultResponse


# FastAPIアプリ
app = FastAPI(title="Sync-Async Pattern Proxy")

# 同期推論用Predictor（MobileNet v2 - 軽量モデル）
sync_predictor = ONNXPredictor(AppConfig.SYNC_MODEL_PATH)

# Redisクライアント
redis_client = Redis(
    host=AppConfig.REDIS_HOST,
    port=AppConfig.REDIS_PORT,
    decode_responses=True
)


def enqueue_job(job_id: str, image_data: str) -> None:
    """
    ジョブをRedisキューに登録

    Args:
        job_id: ジョブID
        image_data: Base64エンコードされた画像データ
    """
    job_data = {
        "image_data": image_data,
        "status": "pending"
    }

    # Redisに保存
    redis_client.setex(
        f"job:{job_id}",
        AppConfig.RESULT_TTL,
        json.dumps(job_data)
    )

    # キューに追加
    redis_client.rpush(AppConfig.QUEUE_NAME, job_id)


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest, background_tasks: BackgroundTasks):
    """
    画像分類推論

    - 同期: MobileNet v2による高速推論（即座に結果を返す）
    - 非同期: ResNet50による高精度推論（バックグラウンドで実行）

    Args:
        request: 推論リクエスト（Base64画像）
        background_tasks: FastAPIバックグラウンドタスク

    Returns:
        job_id: 非同期ジョブID
        result_sync: 同期推論結果（MobileNet v2）
    """
    # ジョブIDを生成
    job_id = str(uuid.uuid4())

    # 同期推論（MobileNet v2 - 軽量で高速）
    result_sync = sync_predictor.predict_from_base64(request.image_data)

    # 非同期ジョブをキューに追加（ResNet50 - 高精度だが重い）
    background_tasks.add_task(enqueue_job, job_id, request.image_data)

    return PredictResponse(
        job_id=job_id,
        result_sync=result_sync
    )


@app.get("/job/{job_id}", response_model=JobResultResponse)
async def get_job_result(job_id: str):
    """
    非同期ジョブの結果を取得

    Args:
        job_id: ジョブID

    Returns:
        prediction: 推論結果（空文字列なら処理中）

    Raises:
        HTTPException: ジョブが見つからない場合
    """
    # Redisから結果を取得
    job_data_str = redis_client.get(f"job:{job_id}")

    if job_data_str is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = json.loads(job_data_str)

    # 処理中なら空文字列を返す
    if job_data["status"] == "pending":
        return JobResultResponse(prediction="")

    # 完了していたら結果を返す
    return JobResultResponse(prediction=job_data.get("result", ""))
