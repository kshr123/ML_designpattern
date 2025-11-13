"""Proxy FastAPI アプリケーション

非同期推論APIのエントリーポイント
"""

import uuid
from typing import Dict

from fastapi import FastAPI, HTTPException
from src.configurations import IrisConfig, RedisConfig
from src.models import (
    HealthResponse,
    JobResult,
    PredictRequest,
    PredictResponse,
    PredictionResult,
)
from src.utils.redis_client import RedisClient

# FastAPIアプリケーション
app = FastAPI(
    title="Asynchronous Pattern - Iris分類API",
    description="非同期推論パターンの実装（Redis + TensorFlow Serving）",
    version="1.0.0",
)

# Redisクライアント
redis_client = RedisClient(
    host=RedisConfig.host,
    port=RedisConfig.port,
    db=RedisConfig.db,
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """ヘルスチェック

    Returns:
        システムの状態
    """
    components = {}

    # Redis接続確認
    try:
        redis_ok = redis_client.ping()
        components["redis"] = "ok" if redis_ok else "error"
    except Exception:
        components["redis"] = "error"

    # Worker (ONNX) 稼働確認 - Redisのキュー長で代用
    try:
        queue_length = redis_client.queue_length(RedisConfig.queue_name)
        # キューが取得できればOK
        components["worker"] = "ok"
    except Exception:
        components["worker"] = "error"

    # 全体ステータス
    status = "healthy" if all(v == "ok" for v in components.values()) else "unhealthy"

    return HealthResponse(status=status, components=components)


@app.get("/metadata")
def metadata() -> Dict:
    """モデルメタデータ取得

    Returns:
        モデルメタデータ（ONNX）
    """
    return {
        "model_name": "iris_svc",
        "model_type": "ONNX",
        "input_shape": [4],  # 4つの特徴量
        "output_classes": 3,  # 3クラス
        "class_names": IrisConfig.class_names,
    }


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    """非同期推論リクエスト

    Args:
        request: 推論リクエスト（Iris特徴量）

    Returns:
        job_id（結果取得に使用）
    """
    # job_id生成（UUID4の最初の6文字）
    job_id = str(uuid.uuid4())[:6]

    # Redisにデータを保存してキューに登録
    try:
        redis_client.save_job_data(
            job_id=job_id,
            data=request.data,
            queue_name=RedisConfig.queue_name,
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis error: {e}")

    return PredictResponse(job_id=job_id)


@app.post("/predict/test", response_model=PredictResponse)
def predict_test() -> PredictResponse:
    """テストデータで推論リクエスト

    Returns:
        job_id
    """
    # テストデータを使用
    test_request = PredictRequest(data=IrisConfig.test_data)
    return predict(test_request)


@app.get("/job/{job_id}", response_model=JobResult)
def get_job_result(job_id: str) -> JobResult:
    """ジョブ結果取得

    Args:
        job_id: ジョブID

    Returns:
        ジョブの状態と結果

    Raises:
        HTTPException: ジョブが存在しない場合
    """
    # ジョブの存在確認
    if not redis_client.job_exists(job_id):
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    # ステータス取得
    status = redis_client.get_job_status(job_id)

    # 結果取得（完了している場合）
    result = None
    error = None

    if status == "completed":
        result_data = redis_client.get_job_result(job_id)
        if result_data:
            result = PredictionResult(**result_data)

    elif status == "failed":
        error_key = f"job:{job_id}:error"
        error = redis_client.get_data(error_key) or "Unknown error"

    return JobResult(job_id=job_id, status=status or "unknown", result=result, error=error)


@app.get("/")
def root() -> Dict[str, str]:
    """ルートエンドポイント

    Returns:
        API情報
    """
    return {
        "name": "Asynchronous Pattern API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "metadata": "GET /metadata",
            "predict": "POST /predict",
            "predict_test": "POST /predict/test",
            "job_result": "GET /job/{job_id}",
        },
    }
