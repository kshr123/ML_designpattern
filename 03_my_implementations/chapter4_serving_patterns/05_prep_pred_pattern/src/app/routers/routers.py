"""APIルーター

各エンドポイントの実装。

エンドポイント:
- GET /health: ヘルスチェック
- GET /metadata: メタデータ取得
- GET /label: ImageNetラベル一覧
- GET /predict/test: テスト画像で推論（確率）
- GET /predict/test/label: テスト画像で推論（ラベル）
- POST /predict: Base64画像で推論（確率）
- POST /predict/label: Base64画像で推論（ラベル）
"""

import base64
import io
from logging import getLogger
from typing import Any, Dict, List

from fastapi import APIRouter
from PIL import Image
from pydantic import BaseModel
from src.ml.prediction import Data, get_classifier

logger = getLogger(__name__)
router = APIRouter()


class InputData(BaseModel):
    """POST リクエスト用の入力データモデル（dataフィールド必須）"""

    data: str  # Base64エンコードされた画像データ（必須）


@router.get("/health")
def health() -> Dict[str, str]:
    """ヘルスチェック

    Returns:
        ステータス情報
    """
    return {"health": "healthy"}


@router.get("/metadata")
def metadata() -> Dict[str, Any]:
    """メタデータ取得

    APIの入出力形式を返す。

    Returns:
        メタデータ情報
    """
    return {
        "data_type": "str",
        "data_structure": "(1,1)",
        "data_sample": "base64 encoded image file",
        "prediction_type": "float32",
        "prediction_structure": "(1,1000)",
        "prediction_sample": "[0.07093159, 0.01558308, 0.01348537, ...]",
    }


@router.get("/label")
def label() -> List[str]:
    """ImageNetラベル一覧取得

    Returns:
        ImageNet 1000クラスのラベルリスト
    """
    classifier = get_classifier()
    return classifier.label


@router.get("/predict/test")
def predict_test() -> Dict[str, List[List[float]]]:
    """テスト画像で推論（確率）

    内部のデフォルト画像を使用して推論を実行。

    Returns:
        確率分布（1000クラス）
    """
    classifier = get_classifier()
    prediction = classifier.predict(data=Data().data)
    return {"prediction": prediction}


@router.get("/predict/test/label")
def predict_test_label() -> Dict[str, str]:
    """テスト画像で推論（ラベル）

    内部のデフォルト画像を使用して推論を実行し、ラベル名を返す。

    Returns:
        ラベル名
    """
    classifier = get_classifier()
    prediction = classifier.predict_label(data=Data().data)
    return {"prediction": prediction}


@router.post("/predict")
def predict(data: InputData) -> Dict[str, List[List[float]]]:
    """Base64画像で推論（確率）

    Base64エンコードされた画像を受け取り、推論を実行。

    Args:
        data: Base64エンコードされた画像データ

    Returns:
        確率分布（1000クラス）
    """
    # ========================================
    # ステップ1: Base64デコード
    # ========================================
    # Base64文字列 → バイナリデータに変換
    # - HTTPリクエストではバイナリを直接送れないため、Base64でエンコードする
    # - 例: "iVBORw0KGgoAAAANS..." → b'\x89PNG\r\n...'
    image_bytes = base64.b64decode(data.data)

    # ========================================
    # ステップ2: バイト列をメモリ上のファイルに変換
    # ========================================
    # バイナリデータ → BytesIOオブジェクト
    # - BytesIO: メモリ上のファイルのように扱えるオブジェクト
    # - ディスクに保存せずに画像を読み込める
    io_bytes = io.BytesIO(image_bytes)

    # ========================================
    # ステップ3: PIL Imageに変換
    # ========================================
    # BytesIO → PIL Image
    # - Image.open()で画像形式（JPEG, PNG, etc.）を自動判定
    # - メモリ上で画像を開く（ファイル保存不要）
    image_data = Image.open(io_bytes)

    # ========================================
    # ステップ4: 推論実行
    # ========================================
    # Classifierインスタンスを取得（シングルトン）
    # - 初回のみ初期化、以降は再利用
    classifier = get_classifier()

    # 推論実行: PIL Image → 確率分布
    # - 前処理 → gRPC通信 → 後処理
    # - 戻り値: [[0.001, 0.82, 0.003, ...]] (1000クラスの確率)
    prediction = classifier.predict(data=image_data)

    return {"prediction": prediction}


@router.post("/predict/label")
def predict_label(data: InputData) -> Dict[str, str]:
    """Base64画像で推論（ラベル）

    Base64エンコードされた画像を受け取り、推論を実行してラベル名を返す。

    Args:
        data: Base64エンコードされた画像データ

    Returns:
        ラベル名
    """
    # ========================================
    # ステップ1: Base64デコード
    # ========================================
    # Base64文字列 → バイナリデータに変換
    # - クライアント側でBase64エンコードされた画像データを受信
    # - 例: "iVBORw0KGgoAAAANS..." → b'\x89PNG\r\n...'
    image_bytes = base64.b64decode(data.data)

    # ========================================
    # ステップ2: バイト列をメモリ上のファイルに変換
    # ========================================
    # バイナリデータ → BytesIOオブジェクト
    # - ディスクに一時ファイルを作らずに処理できる
    # - メモリ効率が良い
    io_bytes = io.BytesIO(image_bytes)

    # ========================================
    # ステップ3: PIL Imageに変換
    # ========================================
    # BytesIO → PIL Image
    # - 画像形式（JPEG, PNG, GIF, etc.）を自動判定
    # - RGB形式で読み込まれる
    image_data = Image.open(io_bytes)

    # ========================================
    # ステップ4: 推論実行
    # ========================================
    # Classifierインスタンスを取得（シングルトン）
    classifier = get_classifier()

    # 推論実行: PIL Image → ラベル名
    # - 前処理 → gRPC通信 → 後処理 → argmax → ラベル取得
    # - 戻り値: "tabby cat" のようなラベル名
    prediction = classifier.predict_label(data=image_data)

    return {"prediction": prediction}
