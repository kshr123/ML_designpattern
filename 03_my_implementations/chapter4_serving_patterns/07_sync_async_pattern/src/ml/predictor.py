"""ONNX Runtime推論クライアント"""
import base64
import io
from typing import List

import numpy as np
import onnxruntime as ort
from PIL import Image

from src.ml.labels import get_label


class ONNXPredictor:
    """ONNX Runtime推論クライアント"""

    def __init__(self, model_path: str):
        """
        初期化

        Args:
            model_path: ONNXモデルのパス
        """
        self.model_path = model_path
        self.session = ort.InferenceSession(model_path)

        # 入出力名を取得
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def preprocess(self, image_data: bytes) -> np.ndarray:
        """
        画像の前処理

        Args:
            image_data: 画像バイトデータ

        Returns:
            前処理済みNumPy配列 (1, 3, 224, 224)
        """
        # PILで画像を開く
        image = Image.open(io.BytesIO(image_data))

        # RGBに変換
        image = image.convert("RGB")

        # リサイズ
        image = image.resize((224, 224))

        # NumPy配列に変換
        img_array = np.array(image).astype(np.float32)

        # 正規化（ImageNet標準）
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32) * 255
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32) * 255
        img_array = (img_array - mean) / std

        # チャンネル順序変更: (H, W, C) → (C, H, W)
        img_array = img_array.transpose(2, 0, 1)

        # バッチ次元追加: (C, H, W) → (1, C, H, W)
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def predict(self, image_data: bytes) -> str:
        """
        推論実行

        Args:
            image_data: 画像バイトデータ

        Returns:
            予測ラベル名
        """
        # 前処理
        input_data = self.preprocess(image_data)

        # 推論
        outputs = self.session.run([self.output_name], {self.input_name: input_data})

        # 最も確率が高いクラスを取得
        class_id = int(np.argmax(outputs[0]))

        # ラベル名を返す
        return get_label(class_id)

    def predict_from_base64(self, base64_data: str) -> str:
        """
        Base64エンコードされた画像から推論

        Args:
            base64_data: Base64エンコードされた画像

        Returns:
            予測ラベル名
        """
        image_data = base64.b64decode(base64_data)
        return self.predict(image_data)
