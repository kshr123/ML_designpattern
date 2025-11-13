"""CRUD操作モジュール

データベースのCreate, Read, Update, Delete操作を提供します。
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from src.db import models, schemas


def select_all_items(db: Session) -> List[models.Item]:
    """
    全アイテムを取得

    Args:
        db: データベースセッション

    Returns:
        全アイテムのリスト
    """
    return db.query(models.Item).all()


def select_without_prediction(db: Session) -> List[models.Item]:
    """
    推論結果がないアイテムを取得（未推論データ）

    Args:
        db: データベースセッション

    Returns:
        predictionがNULLのアイテムリスト
    """
    return db.query(models.Item).filter(models.Item.prediction == None).all()  # noqa: E711


def select_with_prediction(db: Session) -> List[models.Item]:
    """
    推論結果があるアイテムを取得（推論済みデータ）

    Args:
        db: データベースセッション

    Returns:
        predictionが存在するアイテムリスト
    """
    return db.query(models.Item).filter(models.Item.prediction != None).all()  # noqa: E711


def select_by_id(db: Session, id: int) -> Optional[models.Item]:
    """
    ID指定でアイテムを取得

    Args:
        db: データベースセッション
        id: アイテムID

    Returns:
        指定IDのアイテム（存在しない場合はNone）
    """
    return db.query(models.Item).filter(models.Item.id == id).first()


def register_item(db: Session, item: schemas.ItemBase, commit: bool = True) -> models.Item:
    """
    単一アイテムを登録

    Args:
        db: データベースセッション
        item: 登録するアイテム（ItemBaseスキーマ）
        commit: Trueの場合は即座にコミット

    Returns:
        登録されたアイテム
    """
    _item = models.Item(values=item.values)
    db.add(_item)

    if commit:
        db.commit()
        db.refresh(_item)

    return _item


def register_items(
    db: Session, items: List[schemas.ItemBase], commit: bool = True
) -> List[models.Item]:
    """
    複数アイテムを一括登録

    Args:
        db: データベースセッション
        items: 登録するアイテムのリスト
        commit: Trueの場合は即座にコミット

    Returns:
        登録されたアイテムのリスト
    """
    registered_items = []
    for item in items:
        _item = register_item(db=db, item=item, commit=False)
        registered_items.append(_item)

    if commit:
        db.commit()
        for _item in registered_items:
            db.refresh(_item)

    return registered_items


def register_predictions(
    db: Session, predictions: Dict[int, Dict[str, float]], commit: bool = True
) -> None:
    """
    推論結果を一括登録

    Args:
        db: データベースセッション
        predictions: {item_id: {class_id: probability}} 形式の推論結果
        commit: Trueの場合は即座にコミット

    使用例:
        predictions = {
            1: {"0": 0.971, "1": 0.016, "2": 0.013},
            2: {"0": 0.012, "1": 0.023, "2": 0.965},
        }
        register_predictions(db, predictions)
    """
    for item_id, prediction in predictions.items():
        item = select_by_id(db=db, id=item_id)
        if item:
            item.prediction = prediction
            if commit:
                db.commit()
                db.refresh(item)


def delete_item(db: Session, id: int, commit: bool = True) -> bool:
    """
    アイテムを削除

    Args:
        db: データベースセッション
        id: 削除するアイテムのID
        commit: Trueの場合は即座にコミット

    Returns:
        削除に成功した場合True、アイテムが存在しない場合False
    """
    item = select_by_id(db=db, id=id)
    if item:
        db.delete(item)
        if commit:
            db.commit()
        return True
    return False
