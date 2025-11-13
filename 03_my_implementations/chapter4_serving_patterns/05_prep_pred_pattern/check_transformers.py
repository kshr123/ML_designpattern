"""transformers.py の入出力確認スクリプト"""

import numpy as np
from PIL import Image

from src.ml.transformers import PytorchImagePreprocessTransformer, SoftmaxTransformer

print("=" * 80)
print("PytorchImagePreprocessTransformer の入出力確認")
print("=" * 80)

# 1. 赤色の画像を作成（300×300ピクセル）
print("\n【入力】")
print("画像サイズ: 300×300 ピクセル")
print("色: 赤色 (RGB = 255, 0, 0)")
red_image = Image.new("RGB", (300, 300), color=(255, 0, 0))
print(f"PIL Image mode: {red_image.mode}")
print(f"PIL Image size: {red_image.size}")

# 2. 前処理
preprocessor = PytorchImagePreprocessTransformer()
preprocessed = preprocessor.transform(red_image)

print("\n【前処理パラメータ】")
print(f"image_size: {preprocessor.image_size}")
print(f"prediction_shape: {preprocessor.prediction_shape}")
print(f"mean_vec: {preprocessor.mean_vec}")
print(f"stddev_vec: {preprocessor.stddev_vec}")

print("\n【出力】")
print(f"形状: {preprocessed.shape}")
print(f"dtype: {preprocessed.dtype}")
print(f"最小値: {preprocessed.min():.4f}")
print(f"最大値: {preprocessed.max():.4f}")
print(f"\n各チャンネルの平均値:")
print(f"  R channel (index 0): {preprocessed[0, 0, :, :].mean():.4f}")
print(f"  G channel (index 1): {preprocessed[0, 1, :, :].mean():.4f}")
print(f"  B channel (index 2): {preprocessed[0, 2, :, :].mean():.4f}")

print("\n【解説】")
print("赤色画像なので、Rチャンネルの値が最も大きくなります。")
print("正規化の計算: (pixel / 255 - mean) / stddev")
print(f"  R: (1.0 - 0.485) / 0.229 = {(1.0 - 0.485) / 0.229:.4f}")
print(f"  G: (0.0 - 0.456) / 0.224 = {(0.0 - 0.456) / 0.224:.4f}")
print(f"  B: (0.0 - 0.406) / 0.225 = {(0.0 - 0.406) / 0.225:.4f}")

print("\n" + "=" * 80)
print("SoftmaxTransformer の入出力確認")
print("=" * 80)

# 3. ロジット（生の出力）を作成
print("\n【入力】ロジット（ImageNet 1000クラスのシミュレーション）")
# ランダムなロジット（1000次元）
np.random.seed(42)
logits = np.random.randn(1, 1000).astype(np.float32)

print(f"形状: {logits.shape}")
print(f"dtype: {logits.dtype}")
print(f"最小値: {logits.min():.4f}")
print(f"最大値: {logits.max():.4f}")
print(f"平均値: {logits.mean():.4f}")

# 最大値のインデックスを確認
max_index = np.argmax(logits)
print(f"\n最大ロジットのクラス: {max_index}")
print(f"最大ロジットの値: {logits[0, max_index]:.4f}")

# 4. Softmax変換
softmax_transformer = SoftmaxTransformer()
probabilities = softmax_transformer.transform(logits)

print("\n【出力】確率分布")
print(f"形状: {probabilities.shape}")
print(f"dtype: {probabilities.dtype}")
print(f"最小値: {probabilities.min():.6f}")
print(f"最大値: {probabilities.max():.6f}")
print(f"合計: {probabilities.sum():.10f}")

# 最大確率のインデックスを確認
max_prob_index = np.argmax(probabilities)
print(f"\n最大確率のクラス: {max_prob_index}")
print(f"最大確率の値: {probabilities[0, max_prob_index]:.6f}")

# Top-5を表示
top5_indices = np.argsort(probabilities[0])[::-1][:5]
print("\nTop-5 クラス:")
for i, idx in enumerate(top5_indices, 1):
    print(f"  {i}. クラス {idx}: {probabilities[0, idx]:.6f} ({probabilities[0, idx] * 100:.4f}%)")

print("\n【解説】")
print("Softmax変換により、ロジットが確率分布に変換されました。")
print("- すべての確率は [0, 1] の範囲内")
print("- 確率の合計は 1.0")
print("- ロジットの順序関係は保持される")

print("\n" + "=" * 80)
