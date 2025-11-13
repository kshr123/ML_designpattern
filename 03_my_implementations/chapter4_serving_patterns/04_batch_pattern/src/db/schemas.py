"""Pydanticスキーマ定義モジュール

APIリクエスト/レスポンスのデータ検証用スキーマを定義します。
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from src.constants import CONSTANTS


class ItemBase(BaseModel):
    """アイテムの基本スキーマ"""

    values: List[float] = Field(
        ...,
        description="入力特徴量（Iris: 4次元）",
        min_length=CONSTANTS.IRIS_FEATURE_DIM,
        max_length=CONSTANTS.IRIS_FEATURE_DIM,
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"values": [5.1, 3.5, 1.4, 0.2]},
                {"values": [6.3, 3.3, 6.0, 2.5]},
            ]
        }
    }


class Item(ItemBase):
    """アイテムの完全スキーマ（DBレコード）"""

    id: int = Field(..., description="アイテムID")
    prediction: Optional[Dict[str, float]] = Field(None, description="推論結果（確率値）")
    created_datetime: datetime = Field(..., description="作成日時")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "values": [5.1, 3.5, 1.4, 0.2],
                    "prediction": {"0": 0.971, "1": 0.016, "2": 0.013},
                    "created_datetime": "2025-11-13T10:00:00",
                },
                {
                    "id": 2,
                    "values": [6.3, 3.3, 6.0, 2.5],
                    "prediction": None,
                    "created_datetime": "2025-11-13T10:00:01",
                },
            ]
        },
    }


class ItemList(BaseModel):
    """複数アイテムの一括登録用スキーマ"""

    items: List[ItemBase] = Field(..., description="登録するアイテムのリスト")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [
                        {"values": [5.1, 3.5, 1.4, 0.2]},
                        {"values": [6.3, 3.3, 6.0, 2.5]},
                    ]
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンススキーマ"""

    status: str = Field(..., description="ステータス")

    model_config = {"json_schema_extra": {"examples": [{"status": "ok"}]}}


class ModelMetadata(BaseModel):
    """モデルメタデータスキーマ"""

    model_name: str = Field(..., description="モデル名")
    model_type: str = Field(..., description="モデルタイプ")
    input_dim: int = Field(..., description="入力次元数")
    output_dim: int = Field(..., description="出力次元数（クラス数）")
    labels: Dict[str, str] = Field(..., description="ラベルマッピング")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "model_name": "iris_svc",
                    "model_type": "ONNX",
                    "input_dim": 4,
                    "output_dim": 3,
                    "labels": {"0": "setosa", "1": "versicolor", "2": "virginica"},
                }
            ]
        }
    }
