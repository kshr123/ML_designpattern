"""データモデル定義

FastAPIのリクエスト/レスポンスモデル
"""

from typing import Any, Dict, List

from pydantic import BaseModel


class PredictRequest(BaseModel):
    """推論リクエスト"""

    data: List[List[float]] = [[5.1, 3.5, 1.4, 0.2]]


class PredictionResponse(BaseModel):
    """推論レスポンス（各サービス）"""

    prediction: List[float]


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""

    health: str


class AllHealthResponse(BaseModel):
    """全サービスのヘルスチェックレスポンス"""

    setosa: Dict[str, str]
    versicolor: Dict[str, str]
    virginica: Dict[str, str]


class AllPredictionsResponse(BaseModel):
    """全サービスの推論結果"""

    setosa: Dict[str, Any]
    versicolor: Dict[str, Any]
    virginica: Dict[str, Any]


class LabelPredictionResponse(BaseModel):
    """ラベル選択結果"""

    prediction: Dict[str, Any]
