"""推論ロジックのテスト"""
import base64
from pathlib import Path

import pytest
from PIL import Image
import io

from src.ml.predictor import ONNXPredictor
from src.configurations import AppConfig


@pytest.fixture
def sync_predictor():
    """同期推論用Predictor"""
    return ONNXPredictor(AppConfig.SYNC_MODEL_PATH)


@pytest.fixture
def test_image_base64():
    """テスト用画像（Base64）"""
    # 224x224のダミー画像を作成
    img = Image.new("RGB", (224, 224), color=(128, 128, 128))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()


def test_predictor_initialization(sync_predictor):
    """Predictorの初期化テスト"""
    assert sync_predictor.session is not None
    assert sync_predictor.input_name is not None
    assert sync_predictor.output_name is not None


def test_predict_from_base64(sync_predictor, test_image_base64):
    """Base64画像からの推論テスト"""
    result = sync_predictor.predict_from_base64(test_image_base64)

    # 結果は文字列
    assert isinstance(result, str)
    assert len(result) > 0


def test_preprocess(sync_predictor, test_image_base64):
    """前処理のテスト"""
    image_data = base64.b64decode(test_image_base64)
    preprocessed = sync_predictor.preprocess(image_data)

    # 形状確認
    assert preprocessed.shape == (1, 3, 224, 224)
