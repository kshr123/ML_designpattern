"""Pydanticモデル"""
from pydantic import BaseModel


class PredictRequest(BaseModel):
    """推論リクエスト"""
    image_data: str  # Base64エンコードされた画像


class PredictResponse(BaseModel):
    """推論レスポンス"""
    job_id: str
    result_sync: str  # MobileNet v2の結果


class JobResultResponse(BaseModel):
    """ジョブ結果レスポンス"""
    prediction: str  # ResNet50の結果（空文字列なら処理中）
