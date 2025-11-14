"""各専門サービスのエンドポイント

バイナリ分類器として動作
"""

import uuid
from typing import Any, Dict

from fastapi import APIRouter

from src.configurations import AppConfig, ServiceConfig
from src.ml.predictor import ONNXPredictor
from src.models import PredictRequest, PredictionResponse

router = APIRouter()

# ONNX Predictorを初期化（起動時に1回のみ）
predictor = ONNXPredictor(model_path=ServiceConfig.get_model_path())


@router.get("/health")
def health() -> Dict[str, str]:
    """ヘルスチェック"""
    return {"health": "ok"}


@router.get("/metadata")
def metadata() -> Dict[str, Any]:
    """メタデータ取得"""
    return {
        "service": ServiceConfig.mode,
        "data_type": "float32",
        "data_structure": "(1,4)",
        "data_sample": AppConfig.test_data,
        "prediction_type": "float32",
        "prediction_structure": "(1,2)",
        "prediction_sample": [0.97, 0.03],
    }


@router.get("/predict/test")
def predict_test(id: str = None) -> PredictionResponse:
    """テストデータで推論

    Args:
        id: ジョブID（オプション、ログ用）
    """
    if id is None:
        id = str(uuid.uuid4())[:6]

    prediction = predictor.predict(data=AppConfig.test_data)
    return PredictionResponse(prediction=prediction)


@router.post("/predict")
def predict(request: PredictRequest, id: str = None) -> PredictionResponse:
    """推論実行

    Args:
        request: 推論リクエスト
        id: ジョブID（オプション、ログ用）
    """
    if id is None:
        id = str(uuid.uuid4())[:6]

    prediction = predictor.predict(data=request.data)
    return PredictionResponse(prediction=prediction)
