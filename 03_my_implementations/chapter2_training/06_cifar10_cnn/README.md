# cifar10_cnn

CIFAR-10データセットを用いたCNN画像分類（PyTorch + MLflow + ONNX）

## 📋 概要

このプロジェクトは、PyTorchを使ったCNN（畳み込みニューラルネットワーク）による画像分類パターンの実装です。
CIFAR-10データセット（10クラスの32×32カラー画像）を使用し、SimpleCNNモデルで分類します。

### 特徴

- **深層学習（CNN）**: PyTorchでのCNN実装
- **自動データダウンロード**: torchvisionによる自動ダウンロード
- **MLflow統合**: 実験のパラメータ、メトリクス、モデルを自動記録
- **ONNX対応**: 異なるフレームワークでモデルを利用可能
- **100%テストカバレッジ**: TDD（Red-Green-Refactor）サイクルによる開発

## 🎯 学習目標

このパターンを通して学べること：

1. **PyTorchでのCNN実装**
   - 畳み込み層の構成
   - プーリング層の役割
   - 全結合層との接続

2. **画像データの前処理**
   - 正規化（Normalize）
   - データローダーの作成

3. **学習パイプライン**
   - 学習ループの実装
   - テストデータでの評価
   - デバイス管理（CPU/GPU）

4. **実験管理**
   - MLflowによるハイパーパラメータ追跡
   - メトリクスの記録と比較

5. **モデルの相互運用性**
   - ONNX形式へのエクスポート
   - 推論結果の検証

## 🏗️ アーキテクチャ

### SimpleCNNモデル構成

```
入力: (batch, 3, 32, 32)
  ↓
Conv2d(3 → 6, kernel=5)      # (batch, 6, 28, 28)
  ↓
ReLU
  ↓
MaxPool2d(2, 2)              # (batch, 6, 14, 14)
  ↓
Conv2d(6 → 16, kernel=5)     # (batch, 16, 10, 10)
  ↓
ReLU
  ↓
MaxPool2d(2, 2)              # (batch, 16, 5, 5)
  ↓
Flatten                      # (batch, 400)
  ↓
Linear(400 → 120)
  ↓
ReLU
  ↓
Linear(120 → 84)
  ↓
ReLU
  ↓
Linear(84 → 10)
  ↓
出力: (batch, 10)
```

## 📂 プロジェクト構成

```
06_cifar10_cnn/
├── SPECIFICATION.md              # 詳細な仕様書
├── README.md                     # このファイル
├── pyproject.toml                # プロジェクト設定
├── src/
│   └── cifar10_cnn/
│       ├── __init__.py
│       ├── data_loader.py        # CIFAR-10データ読み込み
│       ├── model.py              # SimpleCNN定義
│       ├── trainer.py            # 学習・評価
│       ├── onnx_exporter.py      # ONNXエクスポート
│       ├── mlflow_manager.py     # MLflow統合
│       └── train.py              # メインスクリプト
├── tests/
│   ├── test_data_loader.py       # データローダーテスト
│   ├── test_model.py             # モデルテスト
│   ├── test_trainer.py           # 学習・評価テスト
│   ├── test_onnx_exporter.py     # ONNXテスト
│   └── test_mlflow_manager.py    # MLflowテスト
├── data/                         # CIFAR-10データ（自動ダウンロード）
├── models/                       # 保存モデル
└── mlruns/                       # MLflow実験記録
```

## 🚀 セットアップ

### 前提条件

- Python 3.13以上
- uv（パッケージマネージャー）

### インストール

```bash
# 1. ディレクトリに移動
cd 06_cifar10_cnn

# 2. 仮想環境の作成
uv venv

# 3. 仮想環境の有効化
source .venv/bin/activate  # macOS/Linux

# 4. 依存関係のインストール
uv pip install -e ".[dev]"

# 5. onnxscriptのインストール（必須）
uv pip install onnxscript
```

## 💻 使い方

### 学習パイプラインの実行

```bash
# 仮想環境を有効化
source .venv/bin/activate

# メインスクリプトの実行
python -m cifar10_cnn.train
```

### 実行結果例

```
================================================================================
CIFAR-10 CNN 学習パイプライン
================================================================================

使用デバイス: cpu

[1/5] データを読み込み中...
  ✓ 学習データ: 50000 サンプル
  ✓ テストデータ: 10000 サンプル

[2/5] モデルを作成中...
  ✓ モデル: SimpleCNN
  ✓ パラメータ数: 62,006

[3/5] モデルを学習中...
  エポック数: 5
  バッチサイズ: 32
  学習率: 0.001

Epoch [1/5], Loss: 1.5496
Epoch [2/5], Loss: 1.2592
Epoch [3/5], Loss: 1.1401
Epoch [4/5], Loss: 1.0584
Epoch [5/5], Loss: 0.9950

  ✓ テスト損失: 1.0755
  ✓ テスト精度: 62.58%

[4/5] ONNXモデルをエクスポート中...
  ✓ ONNXモデル作成: models/cifar10_cnn.onnx
  ✓ ONNX検証: 成功

[5/5] MLflowに記録中...
  ✓ パラメータとメトリクスを記録
  ✓ モデルとONNXを記録

================================================================================
✅ 学習パイプライン完了
================================================================================

📊 結果サマリー:
  - テスト精度: 62.58%
  - テスト損失: 1.0755
  - ONNXモデル: models/cifar10_cnn.onnx
  - MLflow実験: cifar10_cnn
```

### テストの実行

```bash
# 全テストの実行
pytest tests/ -v

# カバレッジ付きテスト
pytest tests/ -v --cov=src/cifar10_cnn --cov-report=html

# カバレッジレポートを開く
open htmlcov/index.html
```

### コード品質チェック

```bash
# フォーマット
black src/ tests/

# リント
ruff check src/ tests/ --fix

# 型チェック（外部ライブラリのエラーは許容）
mypy src/
```

## 🧪 テスト結果

### テストサマリー

- **総テスト数**: 48
- **成功**: 48 (100%)
- **失敗**: 0
- **カバレッジ**: 100%

### テスト内訳

| モジュール | テスト数 | カバレッジ |
|-----------|---------|-----------|
| data_loader | 12 | 100% |
| model | 10 | 100% |
| trainer | 9 | 100% |
| onnx_exporter | 8 | 100% |
| mlflow_manager | 9 | 100% |

## 📊 技術スタック

| カテゴリ | ツール |
|---------|--------|
| **言語** | Python 3.13 |
| **深層学習** | PyTorch 2.5+, torchvision 0.20+ |
| **実験管理** | MLflow 2.10+ |
| **ONNX** | onnx 1.17+, onnxruntime 1.20+, onnxscript 0.5+ |
| **テスト** | pytest 8.2+, pytest-cov 5.0+ |
| **コード品質** | black 24.4+, ruff 0.4+, mypy 1.10+ |
| **パッケージ管理** | uv |

## 🔑 主要なハイパーパラメータ

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| `epochs` | 5 | エポック数 |
| `batch_size` | 32 | バッチサイズ |
| `learning_rate` | 0.001 | 学習率 |
| `optimizer` | Adam | 最適化アルゴリズム |
| `loss` | CrossEntropyLoss | 損失関数 |

## 📈 評価指標

| メトリクス | 値 | 説明 |
|-----------|-----|------|
| test_accuracy | ~62.5% | テストデータでの精度 |
| test_loss | ~1.08 | テストデータでの損失 |
| parameters | 62,006 | モデルパラメータ数 |

## 🎓 学んだこと

### 1. CNNの基礎

- **畳み込み層**: 画像の特徴抽出
- **プーリング層**: 特徴マップのダウンサンプリング
- **活性化関数**: ReLUによる非線形性の導入

### 2. PyTorchの実装パターン

- `nn.Module`の継承
- `forward`メソッドの定義
- `DataLoader`によるバッチ処理

### 3. 学習ループの実装

- 勾配のゼロ化 (`optimizer.zero_grad()`)
- 順伝播 (`model(input)`)
- 損失計算 (`criterion(output, target)`)
- 逆伝播 (`loss.backward()`)
- パラメータ更新 (`optimizer.step()`)

### 4. TDDサイクルの実践

1. **Red**: テストを先に書き、失敗することを確認
2. **Green**: テストを通す最小限の実装
3. **Refactor**: コード品質を改善

### 5. MLflowによる実験管理

- パラメータとメトリクスの自動記録
- モデルのバージョン管理
- 実験の再現性確保

### 6. ONNXによる相互運用性

- PyTorchモデルをONNX形式に変換
- 異なるフレームワーク間でモデルを共有
- 推論結果の一致を検証

## 🔗 関連ドキュメント

- [SPECIFICATION.md](./SPECIFICATION.md) - 詳細な仕様書
- [参考実装](../../01_reference/chapter2_training/cifar10/) - 元のコード
- [PyTorch公式ドキュメント](https://pytorch.org/docs/stable/index.html)
- [CIFAR-10データセット](https://www.cs.toronto.edu/~kriz/cifar.html)
- [MLflow](https://mlflow.org/docs/latest/index.html)
- [ONNX](https://onnx.ai/)

## ⚠️ 注意事項

- **初回実行**: データセットのダウンロードに時間がかかります（約170MB）
- **学習時間**: CPUの場合、5エポックで数分かかります
- **GPU利用**: CUDA対応GPUがあれば自動的に利用されます
- **メモリ**: 最低2GB以上のRAM推奨

## 🚧 今後の拡張

- [ ] より深いモデル（VGG11, VGG16）の実装
- [ ] データ拡張（Augmentation）の追加
- [ ] 学習率スケジューリング
- [ ] より多くのエポックでの学習
- [ ] GPU利用時のベンチマーク
- [ ] 推論APIの実装

---

**開発者**: kshr123
**開発日**: 2025-11-05
**プロジェクト**: [ML_designpattern](https://github.com/kshr123/ML_designpattern)
