"""データモデル

APIリクエスト・レスポンスのスキーマ定義
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """推論リクエスト"""

    data: List[List[float]] = Field(
        ...,
        description="Iris特徴量のリスト（各要素は4次元の配列）",
        min_length=1,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    [5.1, 3.5, 1.4, 0.2],  # setosa
                    [6.3, 3.3, 6.0, 2.5],  # virginica
                ]
            }
        }


class PredictResponse(BaseModel):
    """推論レスポンス（job_id）"""

    job_id: str = Field(..., description="ジョブID（結果取得に使用）")

    class Config:
        json_schema_extra = {"example": {"job_id": "a1b2c3"}}


class PredictionResult(BaseModel):
    """推論結果の詳細"""

    prediction: int = Field(..., description="予測クラス（0, 1, 2）")
    class_name: str = Field(..., description="クラス名（setosa, versicolor, virginica）")
    probabilities: List[float] = Field(..., description="各クラスの確率値")

    class Config:
        json_schema_extra = {
            "example": {
                "prediction": 0,
                "class_name": "setosa",
                "probabilities": [0.97, 0.02, 0.01],
            }
        }


class JobResult(BaseModel):
    """ジョブ結果"""

    job_id: str = Field(..., description="ジョブID")
    status: str = Field(
        ..., description="ジョブステータス（pending, processing, completed, failed）"
    )
    result: Optional[PredictionResult] = Field(None, description="推論結果（完了時のみ）")
    error: Optional[str] = Field(None, description="エラーメッセージ（失敗時のみ）")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "a1b2c3",
                "status": "completed",
                "result": {
                    "prediction": 0,
                    "class_name": "setosa",
                    "probabilities": [0.97, 0.02, 0.01],
                },
                "error": None,
            }
        }


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""

    status: str = Field(..., description="全体ステータス（healthy, unhealthy）")
    components: Dict[str, str] = Field(..., description="各コンポーネントの状態")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "components": {"redis": "ok", "tensorflow_serving": "ok"},
            }
        }
