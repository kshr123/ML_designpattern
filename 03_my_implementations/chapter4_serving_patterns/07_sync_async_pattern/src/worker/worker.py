"""Worker - 非同期推論処理

ProcessPoolExecutorを使用してResNet50による高精度推論を実行
"""
import json
import logging
from typing import Optional

from redis import Redis

from src.configurations import AppConfig
from src.ml.predictor import ONNXPredictor

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 非同期推論用Predictor（ResNet50 - 高精度だが重い）
async_predictor = ONNXPredictor(AppConfig.ASYNC_MODEL_PATH)


def process_job(job_id: str, redis_client: Redis) -> Optional[str]:
    """
    ジョブを処理

    Args:
        job_id: ジョブID
        redis_client: Redisクライアント

    Returns:
        推論結果（エラー時はNone）
    """
    try:
        # Redisからジョブデータを取得
        job_data_str = redis_client.get(f"job:{job_id}")

        if job_data_str is None:
            logger.warning(f"Job {job_id} not found")
            return None

        job_data = json.loads(job_data_str)
        image_data = job_data.get("image_data")

        if not image_data:
            logger.warning(f"Job {job_id} has no image_data")
            return None

        # 推論実行（ResNet50）
        logger.info(f"Processing job {job_id} with ResNet50...")
        result = async_predictor.predict_from_base64(image_data)
        logger.info(f"Job {job_id} completed: {result}")

        # 結果をRedisに保存
        job_data["status"] = "completed"
        job_data["result"] = result
        redis_client.setex(
            f"job:{job_id}",
            AppConfig.RESULT_TTL,
            json.dumps(job_data)
        )

        return result

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        return None


def run_worker(redis_client: Redis) -> None:
    """
    Workerのメインループ

    Args:
        redis_client: Redisクライアント
    """
    logger.info("Worker started")

    while True:
        try:
            # キューからジョブを取得（ブロッキング、タイムアウト1秒）
            job = redis_client.blpop(AppConfig.QUEUE_NAME, timeout=1)

            if job:
                _, job_id = job
                logger.info(f"Received job: {job_id}")
                process_job(job_id, redis_client)

        except KeyboardInterrupt:
            logger.info("Worker stopped")
            break
        except Exception as e:
            logger.error(f"Worker error: {e}")
            continue


if __name__ == "__main__":
    # Redisクライアント
    redis_client = Redis(
        host=AppConfig.REDIS_HOST,
        port=AppConfig.REDIS_PORT,
        decode_responses=True
    )

    # Workerを起動
    run_worker(redis_client)
