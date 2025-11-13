"""前処理・後処理トランスフォーマー

画像の前処理とsoftmax変換を提供します。
"""

from typing import List, Tuple, Union

import numpy as np
from PIL import Image
from sklearn.base import BaseEstimator, TransformerMixin

from src.constants import CONSTANTS


class PytorchImagePreprocessTransformer(BaseEstimator, TransformerMixin):
    """PyTorch/ImageNet標準の画像前処理トランスフォーマー

    画像を ResNet50 の入力形式に変換します：
    - リサイズ (224×224)
    - チャンネル順序変換 (HWC → CHW)
    - 正規化 (ImageNet平均・標準偏差)
    - 形状変換 (1, 3, 224, 224)
    """

    def __init__(
        self,
        image_size: Tuple[int, int] = None,
        prediction_shape: Tuple[int, int, int, int] = None,
        mean_vec: List[float] = None,
        stddev_vec: List[float] = None,
    ):
        """初期化

        Args:
            image_size: リサイズサイズ (height, width)
            prediction_shape: 出力形状 (batch, channels, height, width)
            mean_vec: 正規化の平均値 (RGB)
            stddev_vec: 正規化の標準偏差 (RGB)
        """
        self.image_size = image_size if image_size is not None else CONSTANTS.IMAGE_SIZE
        self.prediction_shape = (
            prediction_shape if prediction_shape is not None else CONSTANTS.PREDICTION_SHAPE
        )
        self.mean_vec = mean_vec if mean_vec is not None else CONSTANTS.IMAGENET_MEAN
        self.stddev_vec = stddev_vec if stddev_vec is not None else CONSTANTS.IMAGENET_STDDEV

    def fit(self, X, y=None):
        """scikit-learn Transformer インターフェース: fit

        Args:
            X: 入力データ（使用しない）
            y: ターゲット（使用しない）

        Returns:
            self
        """
        return self

    def transform(self, X: Union[Image.Image, np.ndarray]) -> np.ndarray:
        """画像を前処理

        Args:
            X: PIL Image または numpy配列 (HWC形式)

        Returns:
            前処理済みnumpy配列 (1, 3, 224, 224)
        """
        # PIL Image に変換（numpy配列の場合）
        if isinstance(X, np.ndarray):
            # numpy配列 → PIL Image
            image = Image.fromarray(X)
        else:
            image = X

        # 1. リサイズ (224×224)
        image = image.resize(self.image_size, Image.BILINEAR)

        # 2. numpy配列に変換 (HWC形式)
        image_array = np.array(image, dtype=np.float32)

        # 3. ピクセル値を [0, 1] に正規化
        image_array = image_array / 255.0

        # 4. ImageNet正規化
        # (pixel - mean) / stddev
        mean = np.array(self.mean_vec, dtype=np.float32)
        stddev = np.array(self.stddev_vec, dtype=np.float32)
        image_array = (image_array - mean) / stddev

        # 5. チャンネル順序変換 (HWC → CHW)
        # (height, width, channels) → (channels, height, width)
        image_array = np.transpose(image_array, (2, 0, 1))

        # 6. バッチ次元を追加 (CHW → NCHW)
        # (channels, height, width) → (1, channels, height, width)
        image_array = np.expand_dims(image_array, axis=0)

        return image_array.astype(np.float32)


class SoftmaxTransformer(BaseEstimator, TransformerMixin):
    """Softmax変換トランスフォーマー

    ロジット（生の出力）を確率分布に変換します。
    """

    def __init__(self):
        """初期化"""
        pass

    def fit(self, X, y=None):
        """scikit-learn Transformer インターフェース: fit

        Args:
            X: 入力データ（使用しない）
            y: ターゲット（使用しない）

        Returns:
            self
        """
        return self

    def transform(self, X: Union[np.ndarray, List[float]]) -> np.ndarray:
        """Softmax変換

        Args:
            X: ロジット（生の出力） shape: (1, num_classes)

        Returns:
            確率分布 shape: (1, num_classes)
        """
        # リストの場合はnumpy配列に変換
        if isinstance(X, list):
            X = np.array(X, dtype=np.float32)

        # Softmax計算（数値安定性のためmax減算）
        # softmax(x) = exp(x - max(x)) / sum(exp(x - max(x)))
        x = X[0] if len(X.shape) == 2 else X
        x_max = np.max(x)
        exp_x = np.exp(x - x_max)
        softmax = exp_x / np.sum(exp_x)

        # 形状を (1, num_classes) に整形
        return np.array([softmax], dtype=np.float32)
