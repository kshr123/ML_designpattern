"""バッチジョブのユニットテスト

バッチ推論処理のテストを実施します。
"""

import pytest
from sqlalchemy.orm import Session

from src.db import cruds, schemas
from src.task.job import predict_single_item, run_batch_inference


class TestBatchInference:
    """バッチ推論のテスト"""

    def test_predict_single_item(self, test_db: Session, sample_item_data: dict):
        """単一アイテムの推論をテスト"""
        # データを登録
        item = schemas.ItemBase(**sample_item_data)
        registered_item = cruds.register_item(db=test_db, item=item)

        # 推論実行
        result = predict_single_item(registered_item)

        assert result["id"] == registered_item.id
        assert result["prediction"] is not None
        assert isinstance(result["prediction"], dict)
        assert len(result["prediction"]) == 3  # 3クラス

        # 確率値の確認
        for class_id, prob in result["prediction"].items():
            assert class_id in ["0", "1", "2"]
            assert 0.0 <= prob <= 1.0

    def test_run_batch_inference_empty(self, test_db: Session):
        """空データでのバッチ推論をテスト"""
        predictions = run_batch_inference(data=[], max_workers=2)

        assert len(predictions) == 0

    def test_run_batch_inference_single(self, test_db: Session, sample_item_data: dict):
        """単一データでのバッチ推論をテスト"""
        # データを登録
        item = schemas.ItemBase(**sample_item_data)
        registered_item = cruds.register_item(db=test_db, item=item)

        # 未推論データ取得
        data = cruds.select_without_prediction(db=test_db)

        # バッチ推論実行
        predictions = run_batch_inference(data=data, max_workers=2)

        assert len(predictions) == 1
        assert registered_item.id in predictions
        assert isinstance(predictions[registered_item.id], dict)

    def test_run_batch_inference_multiple(self, test_db: Session, sample_items_data: list):
        """複数データでのバッチ推論をテスト"""
        # データを登録
        items = [schemas.ItemBase(**data) for data in sample_items_data]
        registered_items = cruds.register_items(db=test_db, items=items)

        # 未推論データ取得
        data = cruds.select_without_prediction(db=test_db)

        # バッチ推論実行
        predictions = run_batch_inference(data=data, max_workers=2)

        assert len(predictions) == len(sample_items_data)

        for registered_item in registered_items:
            assert registered_item.id in predictions
            assert isinstance(predictions[registered_item.id], dict)
            assert len(predictions[registered_item.id]) == 3

    def test_batch_inference_with_database_update(
        self, test_db: Session, sample_items_data: list
    ):
        """バッチ推論とデータベース更新の統合テスト"""
        # 1. データを登録
        items = [schemas.ItemBase(**data) for data in sample_items_data]
        registered_items = cruds.register_items(db=test_db, items=items)

        # 2. 未推論データ取得
        unpredicted_data = cruds.select_without_prediction(db=test_db)
        assert len(unpredicted_data) == len(sample_items_data)

        # 3. バッチ推論実行
        predictions = run_batch_inference(data=unpredicted_data, max_workers=2)
        assert len(predictions) == len(sample_items_data)

        # 4. 推論結果をデータベースに保存
        cruds.register_predictions(db=test_db, predictions=predictions, commit=True)

        # 5. 推論済みデータ取得
        predicted_data = cruds.select_with_prediction(db=test_db)
        assert len(predicted_data) == len(sample_items_data)

        for item in predicted_data:
            assert item.prediction is not None
            assert isinstance(item.prediction, dict)
            assert len(item.prediction) == 3

        # 6. 未推論データが0件であることを確認
        unpredicted_data_after = cruds.select_without_prediction(db=test_db)
        assert len(unpredicted_data_after) == 0

    def test_parallel_processing(self, test_db: Session):
        """並列処理（ThreadPoolExecutor）をテスト"""
        # 多めのデータを登録
        data_list = [
            {"values": [5.1, 3.5, 1.4, 0.2]},
            {"values": [6.3, 3.3, 6.0, 2.5]},
            {"values": [5.9, 3.0, 5.1, 1.8]},
            {"values": [5.8, 2.7, 5.1, 1.9]},
            {"values": [6.7, 3.1, 4.4, 1.4]},
        ]

        items = [schemas.ItemBase(**data) for data in data_list]
        cruds.register_items(db=test_db, items=items)

        # 未推論データ取得
        data = cruds.select_without_prediction(db=test_db)

        # 並列処理（4ワーカー）
        predictions = run_batch_inference(data=data, max_workers=4)

        # 全データが推論されていることを確認
        assert len(predictions) == len(data_list)


class TestBatchJobIntegration:
    """バッチジョブの統合テスト"""

    def test_complete_batch_cycle(self, test_db: Session, sample_items_data: list):
        """
        完全なバッチサイクルをテスト

        1. データ登録
        2. 未推論データ確認
        3. バッチ推論実行
        4. 推論結果保存
        5. 推論済みデータ確認
        """
        # 1. データ登録
        items = [schemas.ItemBase(**data) for data in sample_items_data]
        registered_items = cruds.register_items(db=test_db, items=items)

        # 2. 未推論データ確認
        unpredicted = cruds.select_without_prediction(db=test_db)
        assert len(unpredicted) == len(sample_items_data)

        # 3. バッチ推論実行
        predictions = run_batch_inference(data=unpredicted, max_workers=2)
        assert len(predictions) == len(sample_items_data)

        # 4. 推論結果保存
        cruds.register_predictions(db=test_db, predictions=predictions)

        # 5. 推論済みデータ確認
        predicted = cruds.select_with_prediction(db=test_db)
        assert len(predicted) == len(sample_items_data)

        unpredicted_after = cruds.select_without_prediction(db=test_db)
        assert len(unpredicted_after) == 0
