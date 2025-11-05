"""
FastAPIアプリケーションのメインモジュール

このモジュールはFastAPIアプリケーションを作成し、
推論APIエンドポイントを提供します。
"""

import os
from contextlib import asynccontextmanager
from logging import getLogger
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from model_in_image.prediction import Classifier, Data

logger = getLogger(__name__)


# 環境変数からモデルとラベルのパスを取得
# デフォルトは開発環境用のパス
DEFAULT_MODEL_PATH = str(Path(__file__).parent.parent.parent / "models" / "iris_svc.onnx")
DEFAULT_LABEL_PATH = str(Path(__file__).parent.parent.parent / "models" / "label.json")

MODEL_FILEPATH = os.getenv("MODEL_FILEPATH", DEFAULT_MODEL_PATH)
LABEL_FILEPATH = os.getenv("LABEL_FILEPATH", DEFAULT_LABEL_PATH)


# Classifierのグローバルインスタンス（起動時に初期化）
classifier: Classifier = None  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションのライフサイクル管理

    起動時にモデルを読み込み、シャットダウン時にクリーンアップします。
    """
    global classifier
    # Startup
    try:
        logger.info("アプリケーションを起動しています...")
        logger.info(f"モデルパス: {MODEL_FILEPATH}")
        logger.info(f"ラベルパス: {LABEL_FILEPATH}")

        classifier = Classifier(
            model_filepath=MODEL_FILEPATH,
            label_filepath=LABEL_FILEPATH,
        )
        logger.info("モデルとラベルの読み込みが完了しました")
    except Exception as e:
        logger.error(f"起動時にエラーが発生しました: {e}")
        raise

    yield

    # Shutdown
    logger.info("アプリケーションをシャットダウンしています...")


# FastAPIアプリケーションの作成
app = FastAPI(
    title="Model-in-Image Pattern API",
    description="モデルファイルをDockerイメージに組み込んだ推論API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> Dict[str, str]:
    """
    ヘルスチェックエンドポイント

    Returns:
        ヘルスステータス
    """
    return {"health": "ok"}


@app.get("/metadata")
def metadata() -> Dict:
    """
    メタデータエンドポイント

    データ構造とサンプルデータの情報を返します。

    Returns:
        メタデータ情報
    """
    return {
        "data_type": "float32",
        "data_structure": "(1,4)",
        "data_sample": Data().data,
        "prediction_type": "float32",
        "prediction_structure": "(1,3)",
        "prediction_sample": [0.97093159, 0.01558308, 0.01348537],
    }


@app.get("/label")
def label() -> Dict[str, str]:
    """
    ラベル一覧エンドポイント

    Returns:
        クラスインデックスとラベル名のマッピング
    """
    if classifier is None:
        raise HTTPException(status_code=500, detail="Classifierが初期化されていません")
    return classifier.label


@app.get("/predict/test")
def predict_test() -> Dict[str, List[float]]:
    """
    テスト推論エンドポイント（確率値）

    デフォルトのテストデータで推論を実行します。

    Returns:
        予測確率値
    """
    if classifier is None:
        raise HTTPException(status_code=500, detail="Classifierが初期化されていません")

    try:
        prediction = classifier.predict(data=Data().data)
        return {"prediction": prediction.tolist()}
    except Exception as e:
        logger.error(f"テスト推論でエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predict/test/label")
def predict_test_label() -> Dict[str, str]:
    """
    テスト推論エンドポイント（ラベル名）

    デフォルトのテストデータで推論を実行し、ラベル名を返します。

    Returns:
        予測ラベル名
    """
    if classifier is None:
        raise HTTPException(status_code=500, detail="Classifierが初期化されていません")

    try:
        prediction = classifier.predict_label(data=Data().data)
        return {"prediction": prediction}
    except Exception as e:
        logger.error(f"テスト推論（ラベル）でエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict")
def predict(data: Data) -> Dict[str, List[float]]:
    """
    推論エンドポイント（確率値）

    与えられたデータで推論を実行し、確率値を返します。

    Args:
        data: 入力データ

    Returns:
        予測確率値

    Raises:
        HTTPException: 推論に失敗した場合
    """
    if classifier is None:
        raise HTTPException(status_code=500, detail="Classifierが初期化されていません")

    try:
        prediction = classifier.predict(data=data.data)
        return {"prediction": prediction.tolist()}
    except ValueError as e:
        logger.error(f"入力データが不正です: {e}")
        raise HTTPException(status_code=400, detail=f"入力データが不正です: {str(e)}")
    except Exception as e:
        logger.error(f"推論でエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/label")
def predict_label(data: Data) -> Dict[str, str]:
    """
    推論エンドポイント（ラベル名）

    与えられたデータで推論を実行し、ラベル名を返します。

    Args:
        data: 入力データ

    Returns:
        予測ラベル名

    Raises:
        HTTPException: 推論に失敗した場合
    """
    if classifier is None:
        raise HTTPException(status_code=500, detail="Classifierが初期化されていません")

    try:
        prediction = classifier.predict_label(data=data.data)
        return {"prediction": prediction}
    except ValueError as e:
        logger.error(f"入力データが不正です: {e}")
        raise HTTPException(status_code=400, detail=f"入力データが不正です: {str(e)}")
    except KeyError as e:
        logger.error(f"ラベルが見つかりません: {e}")
        raise HTTPException(status_code=500, detail=f"ラベルが見つかりません: {str(e)}")
    except Exception as e:
        logger.error(f"推論（ラベル）でエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail=str(e))
