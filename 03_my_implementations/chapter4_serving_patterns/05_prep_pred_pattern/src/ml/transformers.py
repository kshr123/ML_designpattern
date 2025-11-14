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
        # ========================================
        # ステップ0: 入力形式の統一
        # ========================================
        # PIL Image に変換（numpy配列の場合）
        # - numpy配列の場合: shape (H, W, C) の uint8配列
        # - PIL Imageの場合: そのまま使用
        if isinstance(X, np.ndarray):
            # numpy配列 → PIL Image
            # 例: (224, 224, 3) uint8配列 → PIL Image
            image = Image.fromarray(X)
        else:
            image = X

        # ========================================
        # ステップ1: リサイズ
        # ========================================
        # 任意のサイズ → 224×224 にリサイズ
        # - self.image_size = (224, 224)
        # - Image.BILINEAR: 双線形補間（品質と速度のバランス）
        # - 例: (500, 400) → (224, 224)
        image = image.resize(self.image_size, Image.BILINEAR)

        # ========================================
        # ステップ2: numpy配列に変換
        # ========================================
        # PIL Image → numpy配列 (HWC形式)
        # - shape: (224, 224, 3)
        # - dtype: float32（計算精度のため）
        # - 値の範囲: [0, 255]（まだ正規化していない）
        image_array = np.array(image, dtype=np.float32)

        # ========================================
        # ステップ3: ピクセル値の正規化
        # ========================================
        # [0, 255] → [0, 1] に正規化
        # - 255で割ることで、0〜1の範囲にスケーリング
        # - 例: RGB(128, 64, 255) → (0.502, 0.251, 1.0)
        image_array = image_array / 255.0

        # ========================================
        # ステップ4: ImageNet正規化
        # ========================================
        # ImageNetデータセットの統計で標準化
        # - mean: [0.485, 0.456, 0.406] (RGB各チャンネル)
        # - stddev: [0.229, 0.224, 0.225] (RGB各チャンネル)
        #
        # 計算式: (pixel - mean) / stddev
        # - この変換により、各チャンネルの平均が0、標準偏差が1になる
        # - ResNet50はImageNetで学習されているため、同じ正規化が必要
        mean = np.array(self.mean_vec, dtype=np.float32)
        stddev = np.array(self.stddev_vec, dtype=np.float32)
        image_array = (image_array - mean) / stddev

        # ========================================
        # ステップ5: チャンネル順序変換
        # ========================================
        # HWC → CHW に変換
        # - (height, width, channels) → (channels, height, width)
        # - (224, 224, 3) → (3, 224, 224)
        #
        # 理由:
        # - PyTorchやONNXはCHW形式を使用
        # - PILやOpenCVはHWC形式を使用
        # - transpose()で軸の順序を入れ替える
        #   - 元の軸: (0, 1, 2) = (H, W, C)
        #   - 新しい軸: (2, 0, 1) = (C, H, W)
        image_array = np.transpose(image_array, (2, 0, 1))

        # ========================================
        # ステップ6: バッチ次元の追加
        # ========================================
        # CHW → NCHW に変換
        # - (channels, height, width) → (1, channels, height, width)
        # - (3, 224, 224) → (1, 3, 224, 224)
        #
        # 理由:
        # - ディープラーニングモデルはバッチ処理を前提とする
        # - N: バッチサイズ（ここでは1枚の画像なのでN=1）
        # - expand_dims(axis=0)で先頭に次元を追加
        image_array = np.expand_dims(image_array, axis=0)

        # ========================================
        # 最終確認と返却
        # ========================================
        # 最終形状: (1, 3, 224, 224) float32
        # - 1: バッチサイズ
        # - 3: RGBチャンネル
        # - 224×224: 画像サイズ
        # - float32: データ型（ONNXモデルの入力型に合わせる）
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
            X: ロジット（生の出力） shape: (1, num_classes) or (num_classes,)

        Returns:
            確率分布 shape: (1, num_classes)
        """
        # ========================================
        # ステップ1: 入力形式の統一
        # ========================================
        # リストの場合はnumpy配列に変換
        # - 例: [2.3, 5.1, 1.2, ...] → np.array([2.3, 5.1, 1.2, ...])
        if isinstance(X, list):
            X = np.array(X, dtype=np.float32)

        # ========================================
        # ステップ2: 1次元配列に変換
        # ========================================
        # 入力が (1, 1000) または (1000,) の場合に対応
        # - (1, 1000) → (1000,) に変換
        # - (1000,) → そのまま
        x = X[0] if len(X.shape) == 2 else X

        # ========================================
        # ステップ3: Softmax計算（数値安定性を考慮）
        # ========================================
        # 通常のSoftmax: softmax(x_i) = exp(x_i) / Σexp(x_j)
        #
        # 問題点:
        # - exp()は大きな値で overflow を起こす可能性がある
        # - 例: exp(1000) = ∞ （オーバーフロー）
        #
        # 解決策: 最大値を引いてから計算
        # softmax(x) = exp(x - max(x)) / sum(exp(x - max(x)))
        #
        # 数学的に等価だが、数値的に安定:
        # - exp(x - max(x)) は最大でも exp(0) = 1
        # - アンダーフローのリスクのみ（オーバーフローなし）

        # 最大値を取得
        # 例: x = [2.3, 5.1, 1.2, 3.4, ...] → x_max = 5.1
        x_max = np.max(x)

        # 最大値を引いてから exp() を計算
        # 例: exp([2.3-5.1, 5.1-5.1, 1.2-5.1, ...])
        #   = exp([-2.8, 0.0, -3.9, ...])
        #   = [0.061, 1.0, 0.020, ...]
        exp_x = np.exp(x - x_max)

        # 合計で割って確率分布にする
        # - 合計 = 1.0 になる
        # - 各要素は 0 〜 1 の範囲
        # 例: [0.061, 1.0, 0.020, ...] / 1.081 = [0.056, 0.925, 0.019, ...]
        softmax = exp_x / np.sum(exp_x)

        # ========================================
        # ステップ4: 形状を整形して返却
        # ========================================
        # (1000,) → (1, 1000) に変換
        # - バッチ次元を追加（モデル出力と形式を揃える）
        # - 例: [0.001, 0.82, 0.003, ...] → [[0.001, 0.82, 0.003, ...]]
        return np.array([softmax], dtype=np.float32)
