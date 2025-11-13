"""Backend Worker

Redisキューを監視して推論ジョブを実行する
"""

import time
from logging import INFO, Formatter, StreamHandler, getLogger

from src.backend.onnx_client import ONNXClient
from src.configurations import CacheConfig, RedisConfig, WorkerConfig
from src.utils.redis_client import RedisClient

# ロガー設定
log_format = Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")
logger = getLogger("worker")
stdout_handler = StreamHandler()
stdout_handler.setFormatter(log_format)
logger.addHandler(stdout_handler)
logger.setLevel(INFO)


class PredictionWorker:
    """推論ワーカー"""

    def __init__(self):
        """初期化"""
        # Redisクライアント
        self.redis_client = RedisClient(
            host=RedisConfig.host,
            port=RedisConfig.port,
            db=RedisConfig.db,
        )

        # ONNX Runtime クライアント
        self.onnx_client = ONNXClient()

        # 設定
        self.queue_name = RedisConfig.queue_name
        self.brpop_timeout = WorkerConfig.brpop_timeout
        self.max_retries = WorkerConfig.max_retries
        self.prediction_timeout = WorkerConfig.prediction_timeout

        logger.info(f"Worker initialized (queue: {self.queue_name})")

    def process_job(self, job_id: str) -> bool:
        """ジョブを処理

        Args:
            job_id: ジョブID

        Returns:
            成功したらTrue
        """
        logger.info(f"Processing job: {job_id}")

        # ステータスを processing に更新
        self.redis_client.set_job_status(job_id, "processing")

        # データ取得
        data = self.redis_client.get_job_data(job_id)
        if data is None:
            logger.error(f"Job {job_id}: Data not found")
            self.redis_client.set_job_error(job_id, "Data not found")
            return False

        # 推論実行
        try:
            results = self.onnx_client.predict(data, timeout=self.prediction_timeout)

            if results is None:
                logger.error(f"Job {job_id}: Prediction failed")
                self.redis_client.set_job_error(job_id, "Prediction failed")
                return False

            # 結果を保存（複数サンプルの場合は最初のサンプルのみ）
            result = results[0] if len(results) > 0 else None

            if result:
                logger.info(
                    f"Job {job_id}: Completed - {result['class_name']} "
                    f"(prob: {max(result['probabilities']):.3f})"
                )
                self.redis_client.save_job_result(
                    job_id=job_id, result=result, expire=CacheConfig.job_ttl
                )
                return True
            else:
                logger.error(f"Job {job_id}: No results returned")
                self.redis_client.set_job_error(job_id, "No results returned")
                return False

        except Exception as e:
            logger.error(f"Job {job_id}: Exception - {e}")
            self.redis_client.set_job_error(job_id, str(e))
            return False

    def run(self) -> None:
        """ワーカーメインループ（BRPOPブロッキング方式）"""
        logger.info("Worker started (blocking mode)")

        while True:
            try:
                # キューからジョブを取得（ブロッキング）
                # ジョブが来るまで待機（タイムアウト設定秒）
                job_id = self.redis_client.dequeue_blocking(
                    self.queue_name, timeout=self.brpop_timeout
                )

                if job_id:
                    # ジョブを処理
                    success = self.process_job(job_id)

                    if not success:
                        # 失敗した場合はリトライ（後で実装可能）
                        logger.warning(f"Job {job_id}: Failed")

                # time.sleep不要！BRPOPが自動的に待機する

            except KeyboardInterrupt:
                logger.info("Worker stopping...")
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                # エラー時のみ少し待つ
                time.sleep(1)

        # クリーンアップ
        self.onnx_client.close()
        logger.info("Worker stopped")


def main():
    """エントリーポイント"""
    worker = PredictionWorker()
    worker.run()


if __name__ == "__main__":
    main()
