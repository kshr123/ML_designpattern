"""前処理・後処理トランスフォーマーのテスト"""

import numpy as np
from PIL import Image

from src.ml.transformers import PytorchImagePreprocessTransformer, SoftmaxTransformer
from src.constants import CONSTANTS


class TestPytorchImagePreprocessTransformer:
    """PytorchImagePreprocessTransformer のテスト"""

    def test_init(self):
        """初期化パラメータの確認"""
        transformer = PytorchImagePreprocessTransformer()

        assert transformer.image_size == CONSTANTS.IMAGE_SIZE
        assert transformer.prediction_shape == CONSTANTS.PREDICTION_SHAPE
        assert transformer.mean_vec == CONSTANTS.IMAGENET_MEAN
        assert transformer.stddev_vec == CONSTANTS.IMAGENET_STDDEV

    def test_init_with_custom_params(self):
        """カスタムパラメータでの初期化"""
        custom_size = (128, 128)
        custom_shape = (1, 3, 128, 128)
        custom_mean = [0.5, 0.5, 0.5]
        custom_stddev = [0.5, 0.5, 0.5]

        transformer = PytorchImagePreprocessTransformer(
            image_size=custom_size,
            prediction_shape=custom_shape,
            mean_vec=custom_mean,
            stddev_vec=custom_stddev,
        )

        assert transformer.image_size == custom_size
        assert transformer.prediction_shape == custom_shape
        assert transformer.mean_vec == custom_mean
        assert transformer.stddev_vec == custom_stddev

    def test_transform_pil_image(self):
        """PIL Image の変換テスト"""
        # 赤色の画像を作成（RGB = 255, 0, 0）
        image = Image.new("RGB", (300, 300), color=(255, 0, 0))

        transformer = PytorchImagePreprocessTransformer()
        result = transformer.transform(image)

        # 出力形状の確認
        assert result.shape == CONSTANTS.PREDICTION_SHAPE
        assert result.dtype == np.float32

    def test_transform_numpy_array(self):
        """numpy配列の変換テスト"""
        # ランダムな画像データ (HWC形式、0-255の範囲)
        image_array = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)

        transformer = PytorchImagePreprocessTransformer()
        result = transformer.transform(image_array)

        # 出力形状の確認
        assert result.shape == CONSTANTS.PREDICTION_SHAPE
        assert result.dtype == np.float32

    def test_output_shape(self):
        """出力形状の確認 (1, 3, 224, 224)"""
        image = Image.new("RGB", (500, 500), color=(128, 128, 128))

        transformer = PytorchImagePreprocessTransformer()
        result = transformer.transform(image)

        # NCHW形式: (batch_size, channels, height, width)
        assert result.shape[0] == 1  # batch_size
        assert result.shape[1] == 3  # channels (RGB)
        assert result.shape[2] == 224  # height
        assert result.shape[3] == 224  # width

    def test_normalization(self):
        """正規化が正しく適用されているか確認"""
        # 白色の画像を作成（RGB = 255, 255, 255）
        image = Image.new("RGB", (224, 224), color=(255, 255, 255))

        transformer = PytorchImagePreprocessTransformer()
        result = transformer.transform(image)

        # 正規化の公式: (pixel / 255 - mean) / stddev
        # 白色 (255, 255, 255) の場合:
        # R channel: (1.0 - 0.485) / 0.229 ≈ 2.25
        # G channel: (1.0 - 0.456) / 0.224 ≈ 2.43
        # B channel: (1.0 - 0.406) / 0.225 ≈ 2.64

        # 正規化されているので、値の範囲は [-3, 3] 程度
        assert result.min() > -3.0
        assert result.max() < 3.0

    def test_channel_order_hwc_to_chw(self):
        """チャンネル順序変換 (HWC → CHW) の確認"""
        # R=255, G=0, B=0 の赤色画像
        image = Image.new("RGB", (224, 224), color=(255, 0, 0))

        transformer = PytorchImagePreprocessTransformer()
        result = transformer.transform(image)

        # CHW形式なので、result[0, 0, :, :] がRチャンネル
        # 赤色なので、Rチャンネルが最も大きい値を持つはず
        r_channel_mean = result[0, 0, :, :].mean()
        g_channel_mean = result[0, 1, :, :].mean()
        b_channel_mean = result[0, 2, :, :].mean()

        # Rチャンネルが他より大きいことを確認
        assert r_channel_mean > g_channel_mean
        assert r_channel_mean > b_channel_mean

    def test_sklearn_interface_fit(self):
        """scikit-learn Transformer インターフェース: fit メソッド"""
        image = Image.new("RGB", (224, 224), color=(128, 128, 128))

        transformer = PytorchImagePreprocessTransformer()
        result = transformer.fit(image)

        # fit は self を返す
        assert result is transformer

    def test_sklearn_interface_fit_transform(self):
        """scikit-learn Transformer インターフェース: fit_transform メソッド"""
        image = Image.new("RGB", (224, 224), color=(128, 128, 128))

        transformer = PytorchImagePreprocessTransformer()
        result = transformer.fit_transform(image)

        # fit_transform は変換結果を返す
        assert result.shape == CONSTANTS.PREDICTION_SHAPE
        assert result.dtype == np.float32

    def test_resize_smaller_image(self):
        """小さい画像のリサイズ (100x100 → 224x224)"""
        image = Image.new("RGB", (100, 100), color=(128, 128, 128))

        transformer = PytorchImagePreprocessTransformer()
        result = transformer.transform(image)

        # 224x224にリサイズされていることを確認
        assert result.shape[2] == 224
        assert result.shape[3] == 224

    def test_resize_larger_image(self):
        """大きい画像のリサイズ (500x500 → 224x224)"""
        image = Image.new("RGB", (500, 500), color=(128, 128, 128))

        transformer = PytorchImagePreprocessTransformer()
        result = transformer.transform(image)

        # 224x224にリサイズされていることを確認
        assert result.shape[2] == 224
        assert result.shape[3] == 224

    def test_resize_non_square_image(self):
        """正方形でない画像のリサイズ (300x200 → 224x224)"""
        image = Image.new("RGB", (300, 200), color=(128, 128, 128))

        transformer = PytorchImagePreprocessTransformer()
        result = transformer.transform(image)

        # 224x224にリサイズされていることを確認（アスペクト比は保持されない）
        assert result.shape[2] == 224
        assert result.shape[3] == 224


class TestSoftmaxTransformer:
    """SoftmaxTransformer のテスト"""

    def test_init(self):
        """初期化"""
        transformer = SoftmaxTransformer()
        assert transformer is not None

    def test_transform_numpy_array(self):
        """numpy配列のsoftmax変換"""
        # ロジット（生の出力）
        logits = np.array([[2.0, 1.0, 0.1]])

        transformer = SoftmaxTransformer()
        result = transformer.transform(logits)

        # 出力は確率分布
        assert result.shape == (1, 3)
        assert result.dtype == np.float32 or result.dtype == np.float64

    def test_transform_list(self):
        """Listのsoftmax変換"""
        # ロジット（生の出力）
        logits = [[2.0, 1.0, 0.1]]

        transformer = SoftmaxTransformer()
        result = transformer.transform(logits)

        # 出力は確率分布
        assert result.shape == (1, 3)

    def test_probabilities_sum_to_one(self):
        """確率の合計が1.0になることを確認"""
        logits = np.array([[3.0, 1.0, 0.5, 2.0, -1.0]])

        transformer = SoftmaxTransformer()
        result = transformer.transform(logits)

        # softmaxの性質: 確率の合計は1.0
        assert np.isclose(result.sum(), 1.0, atol=1e-6)

    def test_softmax_correct_calculation(self):
        """softmax計算が正しいか確認"""
        # シンプルなロジット
        logits = np.array([[1.0, 2.0, 3.0]])

        transformer = SoftmaxTransformer()
        result = transformer.transform(logits)

        # 手動でsoftmaxを計算
        exp_logits = np.exp(logits - np.max(logits))
        expected = exp_logits / exp_logits.sum()

        # 結果が一致することを確認
        assert np.allclose(result, expected, atol=1e-6)

    def test_softmax_preserves_order(self):
        """softmax変換後も順序関係が保たれることを確認"""
        # ロジット: 3.0 > 1.0 > 0.5
        logits = np.array([[3.0, 1.0, 0.5]])

        transformer = SoftmaxTransformer()
        result = transformer.transform(logits)

        # softmax変換後も: result[0, 0] > result[0, 1] > result[0, 2]
        assert result[0, 0] > result[0, 1]
        assert result[0, 1] > result[0, 2]

    def test_softmax_imagenet_1000_classes(self):
        """ImageNet 1000クラスのロジットを変換"""
        # 1000次元のロジット
        logits = np.random.randn(1, 1000)

        transformer = SoftmaxTransformer()
        result = transformer.transform(logits)

        # 形状確認
        assert result.shape == (1, 1000)

        # 確率の合計が1.0
        assert np.isclose(result.sum(), 1.0, atol=1e-6)

        # すべての値が [0, 1] の範囲内
        assert (result >= 0).all()
        assert (result <= 1).all()

    def test_sklearn_interface_fit(self):
        """scikit-learn Transformer インターフェース: fit メソッド"""
        logits = np.array([[1.0, 2.0, 3.0]])

        transformer = SoftmaxTransformer()
        result = transformer.fit(logits)

        # fit は self を返す
        assert result is transformer

    def test_sklearn_interface_fit_transform(self):
        """scikit-learn Transformer インターフェース: fit_transform メソッド"""
        logits = np.array([[1.0, 2.0, 3.0]])

        transformer = SoftmaxTransformer()
        result = transformer.fit_transform(logits)

        # fit_transform は変換結果を返す
        assert result.shape == (1, 3)
        assert np.isclose(result.sum(), 1.0, atol=1e-6)

    def test_numerical_stability(self):
        """数値安定性の確認（大きな値でもオーバーフローしない）"""
        # 非常に大きなロジット
        logits = np.array([[1000.0, 999.0, 998.0]])

        transformer = SoftmaxTransformer()
        result = transformer.transform(logits)

        # オーバーフローしていないことを確認
        assert not np.isnan(result).any()
        assert not np.isinf(result).any()

        # 確率の合計が1.0
        assert np.isclose(result.sum(), 1.0, atol=1e-6)
