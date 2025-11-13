"""バッチジョブモジュール

定期的に未推論データを取得し、並列で推論を実行し、結果をデータベースに保存します。
"""

import time
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
from typing import Dict, List

from src.configurations import BatchConfigurations
from src.db import cruds, models
from src.db.database import get_context_db
from src.ml.prediction import classifier

logger = getLogger(__name__)


def predict_single_item(item: models.Item) -> Dict[str, any]:
    """
    単一アイテムの推論を実行

    Args:
        item: 推論対象アイテム

    Returns:
        {"id": item_id, "prediction": {class_id: probability}}
    """
    try:
        logger.info(f"Predicting item ID: {item.id}")

        # 推論実行
        prediction_dict = classifier.predict_dict([item.values])

        logger.info(f"Item ID {item.id}: prediction={prediction_dict}")

        return {"id": item.id, "prediction": prediction_dict}

    except Exception as e:
        logger.error(f"Error predicting item ID {item.id}: {e}")
        return {"id": item.id, "prediction": None, "error": str(e)}


def run_batch_inference(data: List[models.Item], max_workers: int = 4) -> Dict[int, Dict[str, float]]:
    """
    バッチ推論を並列実行

    Args:
        data: 推論対象データのリスト
        max_workers: 並列処理のワーカー数

    Returns:
        {item_id: {class_id: probability}} 形式の推論結果
    """
    predictions = {}

    if not data:
        logger.info("No data to predict")
        return predictions

    logger.info(f"Starting batch inference for {len(data)} items with {max_workers} workers")

    # ThreadPoolExecutorで並列推論
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(predict_single_item, data)

        for result in results:
            if result["prediction"] is not None:
                predictions[result["id"]] = result["prediction"]
            else:
                logger.warning(f"Item ID {result['id']}: prediction failed")

    logger.info(f"Batch inference completed. {len(predictions)} predictions generated")

    return predictions


def main():
    """
    バッチジョブのメイン処理

    1. 指定時間待機（60秒）
    2. 未推論データ取得
    3. 並列推論実行
    4. 結果をデータベースに保存
    """
    logger.info("=" * 80)
    logger.info("Batch job started")
    logger.info("=" * 80)

    # 待機時間
    wait_time = BatchConfigurations.wait_time
    worker_threads = BatchConfigurations.worker_threads

    logger.info(f"Waiting for {wait_time} seconds before starting batch inference...")
    time.sleep(wait_time)

    logger.info("Starting batch inference...")

    # データベースから未推論データ取得
    with get_context_db() as db:
        # 未推論データ取得
        data = cruds.select_without_prediction(db=db)

        if not data:
            logger.info("No unpredicted data found. Batch job completed.")
            return

        logger.info(f"Found {len(data)} unpredicted items")

        # 並列推論実行
        start_time = time.time()
        predictions = run_batch_inference(data=data, max_workers=worker_threads)
        elapsed_time = time.time() - start_time

        logger.info(f"Batch inference took {elapsed_time:.2f} seconds")

        # 推論結果をデータベースに保存
        if predictions:
            logger.info(f"Registering {len(predictions)} predictions to database...")
            cruds.register_predictions(db=db, predictions=predictions, commit=True)
            logger.info("Predictions registered successfully")
        else:
            logger.warning("No predictions to register")

    logger.info("=" * 80)
    logger.info("Batch job completed successfully")
    logger.info("=" * 80)


if __name__ == "__main__":
    # ロギング設定
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # バッチジョブ実行
    main()
