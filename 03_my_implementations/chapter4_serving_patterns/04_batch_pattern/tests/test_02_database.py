"""データベース層のユニットテスト

CRUD操作のテストを実施します。
"""

import pytest
from sqlalchemy.orm import Session

from src.db import cruds, models, schemas


class TestCRUDOperations:
    """CRUD操作のテスト"""

    def test_register_item(self, test_db: Session, sample_item_data: dict):
        """単一アイテム登録をテスト"""
        item = schemas.ItemBase(**sample_item_data)
        registered_item = cruds.register_item(db=test_db, item=item)

        assert registered_item.id is not None
        assert registered_item.values == sample_item_data["values"]
        assert registered_item.prediction is None
        assert registered_item.created_datetime is not None

    def test_register_items(self, test_db: Session, sample_items_data: list):
        """複数アイテム一括登録をテスト"""
        items = [schemas.ItemBase(**data) for data in sample_items_data]
        registered_items = cruds.register_items(db=test_db, items=items)

        assert len(registered_items) == len(sample_items_data)

        for i, registered_item in enumerate(registered_items):
            assert registered_item.id is not None
            assert registered_item.values == sample_items_data[i]["values"]
            assert registered_item.prediction is None

    def test_select_all_items(self, test_db: Session, sample_items_data: list):
        """全アイテム取得をテスト"""
        # データを登録
        items = [schemas.ItemBase(**data) for data in sample_items_data]
        cruds.register_items(db=test_db, items=items)

        # 全アイテム取得
        all_items = cruds.select_all_items(db=test_db)

        assert len(all_items) == len(sample_items_data)

    def test_select_by_id(self, test_db: Session, sample_item_data: dict):
        """ID指定アイテム取得をテスト"""
        item = schemas.ItemBase(**sample_item_data)
        registered_item = cruds.register_item(db=test_db, item=item)

        # ID指定で取得
        fetched_item = cruds.select_by_id(db=test_db, id=registered_item.id)

        assert fetched_item is not None
        assert fetched_item.id == registered_item.id
        assert fetched_item.values == sample_item_data["values"]

    def test_select_by_id_not_found(self, test_db: Session):
        """存在しないIDでの取得をテスト"""
        fetched_item = cruds.select_by_id(db=test_db, id=9999)

        assert fetched_item is None

    def test_select_without_prediction(self, test_db: Session, sample_items_data: list):
        """未推論アイテム取得をテスト"""
        # データを登録（推論結果なし）
        items = [schemas.ItemBase(**data) for data in sample_items_data]
        cruds.register_items(db=test_db, items=items)

        # 未推論アイテム取得
        unpredicted_items = cruds.select_without_prediction(db=test_db)

        assert len(unpredicted_items) == len(sample_items_data)

        for item in unpredicted_items:
            assert item.prediction is None

    def test_select_with_prediction(
        self, test_db: Session, sample_items_data: list, sample_prediction: dict
    ):
        """推論済みアイテム取得をテスト"""
        # データを登録
        items = [schemas.ItemBase(**data) for data in sample_items_data]
        registered_items = cruds.register_items(db=test_db, items=items)

        # 1つ目のアイテムに推論結果を登録
        predictions = {registered_items[0].id: sample_prediction}
        cruds.register_predictions(db=test_db, predictions=predictions)

        # 推論済みアイテム取得
        predicted_items = cruds.select_with_prediction(db=test_db)

        assert len(predicted_items) == 1
        assert predicted_items[0].id == registered_items[0].id
        assert predicted_items[0].prediction == sample_prediction

    def test_register_predictions(
        self, test_db: Session, sample_items_data: list, sample_prediction: dict
    ):
        """推論結果登録をテスト"""
        # データを登録
        items = [schemas.ItemBase(**data) for data in sample_items_data]
        registered_items = cruds.register_items(db=test_db, items=items)

        # 推論結果を登録
        predictions = {
            registered_items[0].id: sample_prediction,
            registered_items[1].id: {"0": 0.012, "1": 0.023, "2": 0.965},
        }
        cruds.register_predictions(db=test_db, predictions=predictions)

        # 推論済みアイテム取得
        predicted_items = cruds.select_with_prediction(db=test_db)

        assert len(predicted_items) == 2
        assert predicted_items[0].prediction is not None
        assert predicted_items[1].prediction is not None

    def test_delete_item(self, test_db: Session, sample_item_data: dict):
        """アイテム削除をテスト"""
        item = schemas.ItemBase(**sample_item_data)
        registered_item = cruds.register_item(db=test_db, item=item)

        # 削除
        result = cruds.delete_item(db=test_db, id=registered_item.id)

        assert result is True

        # 削除されたことを確認
        fetched_item = cruds.select_by_id(db=test_db, id=registered_item.id)
        assert fetched_item is None

    def test_delete_item_not_found(self, test_db: Session):
        """存在しないアイテムの削除をテスト"""
        result = cruds.delete_item(db=test_db, id=9999)

        assert result is False


class TestPydanticSchemas:
    """Pydanticスキーマのテスト"""

    def test_item_base_valid(self, sample_item_data: dict):
        """ItemBaseの正常なバリデーションをテスト"""
        item = schemas.ItemBase(**sample_item_data)

        assert item.values == sample_item_data["values"]

    def test_item_base_invalid_length(self):
        """ItemBaseの無効な長さをテスト"""
        with pytest.raises(ValueError):
            schemas.ItemBase(values=[1.0, 2.0, 3.0])  # 3次元（4次元必須）

    def test_item_list_valid(self, sample_items_data: list):
        """ItemListの正常なバリデーションをテスト"""
        items = [schemas.ItemBase(**data) for data in sample_items_data]
        item_list = schemas.ItemList(items=items)

        assert len(item_list.items) == len(sample_items_data)
