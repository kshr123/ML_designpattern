"""
APIルーターモジュール

全てのエンドポイントを定義します。
"""

import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from src.ml.prediction import Data, classifier

router = APIRouter()


@router.get("/health")
def health() -> Dict[str, str]:
    """
    ヘルスチェックエンドポイント

    Returns:
        {"health": "ok"}
    """
    return {"health": "ok"}


@router.get("/metadata")
def metadata() -> Dict[str, Any]:
    """
    メタデータエンドポイント

    入力データの型・構造・サンプルを返します。

    Returns:
        データ型、構造、サンプルを含む辞書
    """
    return {
        "data_type": "float32",
        "data_structure": "(1,4)",
        "data_sample": Data().data,
        "prediction_type": "float32",
        "prediction_structure": "(1,3)",
        "prediction_sample": [0.97093159, 0.01558308, 0.01348537],
    }


@router.get("/label")
def label() -> Dict[str, str]:
    """
    ラベルエンドポイント

    分類ラベルの一覧を返します。

    Returns:
        {
            "0": "setosa",
            "1": "versicolor",
            "2": "virginica"
        }
    """
    return classifier.label


@router.get("/predict/test")
def predict_test() -> Dict[str, List[float]]:
    """
    テスト推論エンドポイント（確率値）

    サンプルデータで推論を実行し、確率値を返します。

    Returns:
        {"prediction": [setosa確率, versicolor確率, virginica確率]}
    """
    job_id = str(uuid.uuid4())
    prediction = classifier.predict(data=Data().data)
    prediction_list = list(prediction)
    return {"prediction": prediction_list}


@router.get("/predict/test/label")
def predict_test_label() -> Dict[str, str]:
    """
    テスト推論エンドポイント（ラベル名）

    サンプルデータで推論を実行し、ラベル名を返します。

    Returns:
        {"prediction": "setosa" | "versicolor" | "virginica"}
    """
    job_id = str(uuid.uuid4())
    prediction = classifier.predict_label(data=Data().data)
    return {"prediction": prediction}


@router.post("/predict")
def predict(data: Data) -> Dict[str, List[float]]:
    """
    推論エンドポイント（確率値）

    POSTリクエストで送信されたデータで推論を実行し、確率値を返します。

    Args:
        data: 入力データ {"data": [[sepal_length, sepal_width, petal_length, petal_width]]}

    Returns:
        {"prediction": [setosa確率, versicolor確率, virginica確率]}
    """
    job_id = str(uuid.uuid4())
    try:
        prediction = classifier.predict(data.data)
        prediction_list = list(prediction)
        return {"prediction": prediction_list}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")


@router.post("/predict/label")
def predict_label(data: Data) -> Dict[str, str]:
    """
    推論エンドポイント（ラベル名）

    POSTリクエストで送信されたデータで推論を実行し、ラベル名を返します。

    Args:
        data: 入力データ {"data": [[sepal_length, sepal_width, petal_length, petal_width]]}

    Returns:
        {"prediction": "setosa" | "versicolor" | "virginica"}
    """
    job_id = str(uuid.uuid4())
    try:
        prediction = classifier.predict_label(data.data)
        return {"prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")
