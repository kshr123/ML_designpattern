"""FastAPI アプリケーション - Model-Load Pattern"""
from logging import getLogger

from fastapi import FastAPI

from src.configurations import APIConfigurations
from src.ml.prediction import Data, classifier

logger = getLogger(__name__)

# FastAPIアプリケーション
app = FastAPI(
    title=APIConfigurations.title,
    description=APIConfigurations.description,
    version=APIConfigurations.version,
)


@app.get("/health")
async def health() -> dict:
    """
    ヘルスチェックエンドポイント

    Returns:
        ヘルスステータス
    """
    return {"health": "ok"}


@app.get("/metadata")
async def metadata() -> dict:
    """
    モデルのメタデータ取得エンドポイント

    Returns:
        モデルの入出力形式
    """
    return {
        "data_type": "float32",
        "data_shape": "(1, 4)",
        "data_sample": [[5.1, 3.5, 1.4, 0.2]],
        "prediction_type": "float32",
        "prediction_shape": "(1, 3)",
        "prediction_sample": [0.97, 0.02, 0.01],
    }


@app.get("/label")
async def label() -> dict:
    """
    ラベル一覧取得エンドポイント

    Returns:
        ラベル一覧
    """
    return classifier.label


@app.post("/predict")
async def predict(data: Data) -> dict:
    """
    推論エンドポイント（確率値）

    Args:
        data: 入力データ

    Returns:
        各クラスの確率値
    """
    prediction = classifier.predict(data.data)
    return {"prediction": prediction.tolist()}


@app.post("/predict/label")
async def predict_label(data: Data) -> dict:
    """
    推論エンドポイント（ラベル名）

    Args:
        data: 入力データ

    Returns:
        予測されたクラスのラベル名
    """
    prediction = classifier.predict_label(data.data)
    return {"prediction": prediction}
