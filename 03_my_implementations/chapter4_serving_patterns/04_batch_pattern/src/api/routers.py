"""FastAPI ルーター定義モジュール

APIエンドポイントを定義します。
"""

from logging import getLogger
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db import cruds, schemas
from src.db.database import get_db
from src.ml.prediction import classifier

logger = getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=schemas.HealthResponse)
def root():
    """
    ルートエンドポイント

    Returns:
        ステータスメッセージ
    """
    return {"status": "Batch Pattern API is running"}


@router.get("/health", response_model=schemas.HealthResponse)
def health_check():
    """
    ヘルスチェックエンドポイント

    Returns:
        ヘルスステータス
    """
    return {"status": "ok"}


@router.get("/metadata", response_model=schemas.ModelMetadata)
def get_metadata():
    """
    モデルメタデータ取得エンドポイント

    Returns:
        モデルのメタデータ
    """
    metadata = classifier.get_metadata()
    return metadata


@router.post("/data", response_model=schemas.Item)
def register_data(item: schemas.ItemBase, db: Session = Depends(get_db)):
    """
    単一データ登録エンドポイント

    Args:
        item: 登録するデータ
        db: データベースセッション

    Returns:
        登録されたアイテム
    """
    logger.info(f"Registering item: {item.values}")
    registered_item = cruds.register_item(db=db, item=item)
    logger.info(f"Item registered with ID: {registered_item.id}")
    return registered_item


@router.post("/data/list", response_model=List[schemas.Item])
def register_data_list(item_list: schemas.ItemList, db: Session = Depends(get_db)):
    """
    複数データ一括登録エンドポイント

    Args:
        item_list: 登録するデータのリスト
        db: データベースセッション

    Returns:
        登録されたアイテムのリスト
    """
    logger.info(f"Registering {len(item_list.items)} items")
    registered_items = cruds.register_items(db=db, items=item_list.items)
    logger.info(f"{len(registered_items)} items registered")
    return registered_items


@router.get("/data/all", response_model=List[schemas.Item])
def get_all_data(db: Session = Depends(get_db)):
    """
    全データ取得エンドポイント

    Args:
        db: データベースセッション

    Returns:
        全アイテムのリスト
    """
    logger.info("Fetching all items")
    items = cruds.select_all_items(db=db)
    logger.info(f"Found {len(items)} items")
    return items


@router.get("/data/unpredicted", response_model=List[schemas.Item])
def get_unpredicted_data(db: Session = Depends(get_db)):
    """
    未推論データ取得エンドポイント

    Args:
        db: データベースセッション

    Returns:
        predictionがNULLのアイテムリスト
    """
    logger.info("Fetching unpredicted items")
    items = cruds.select_without_prediction(db=db)
    logger.info(f"Found {len(items)} unpredicted items")
    return items


@router.get("/data/predicted", response_model=List[schemas.Item])
def get_predicted_data(db: Session = Depends(get_db)):
    """
    推論済みデータ取得エンドポイント

    Args:
        db: データベースセッション

    Returns:
        predictionが存在するアイテムリスト
    """
    logger.info("Fetching predicted items")
    items = cruds.select_with_prediction(db=db)
    logger.info(f"Found {len(items)} predicted items")
    return items


@router.get("/data/{item_id}", response_model=schemas.Item)
def get_data_by_id(item_id: int, db: Session = Depends(get_db)):
    """
    ID指定データ取得エンドポイント

    Args:
        item_id: アイテムID
        db: データベースセッション

    Returns:
        指定IDのアイテム

    Raises:
        HTTPException: アイテムが存在しない場合
    """
    logger.info(f"Fetching item with ID: {item_id}")
    item = cruds.select_by_id(db=db, id=item_id)

    if item is None:
        logger.warning(f"Item with ID {item_id} not found")
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    logger.info(f"Item found: {item.id}")
    return item
