# CIFAR-10 CNN 画像分類 仕様書

## 1. 要件定義

### 1.1 機能要件

- [ ] **データ読み込み**: torchvisionを使ってCIFAR-10データセットをダウンロード・読み込み
- [ ] **データ前処理**: 画像の正規化、テンソル変換
- [ ] **CNNモデル定義**: PyTorchでシンプルなCNNモデルを実装
- [ ] **学習パイプライン**: モデルの学習、検証、チェックポイント保存
- [ ] **評価**: テストデータでの精度評価
- [ ] **MLflow統合**: パラメータ、メトリクス、モデルの記録
- [ ] **ONNXエクスポート**: PyTorchモデルをONNX形式にエクスポート
- [ ] **ONNX検証**: ONNXモデルとPyTorchモデルの予測結果が一致することを確認

### 1.2 非機能要件

- **パフォーマンス**:
  - GPU利用可能時は自動的にGPUを使用
  - エポック実行時間: 数分程度（CPUの場合）
  - メモリ使用量: 学習時 < 2GB

- **スケーラビリティ**:
  - バッチサイズを調整可能
  - エポック数を設定可能

- **可用性**:
  - データダウンロード失敗時の適切なエラーハンドリング
  - チェックポイント保存による学習の再開可能性

- **保守性**:
  - モジュール化されたコード構成
  - 100%のテストカバレッジ
  - 型ヒントの使用

## 2. アーキテクチャ設計

### 2.1 システム構成

```
┌─────────────────────────────────────────────────────────┐
│              CIFAR-10学習パイプライン                    │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ データ読込   │   │ モデル学習   │   │ 結果記録     │
│ CIFAR-10     │   │ SimpleCNN    │   │ MLflow       │
│              │──▶│ CrossEntropy │──▶│ ONNX export  │
│ 60k samples  │   │ Adam         │   │              │
└──────────────┘   └──────────────┘   └──────────────┘
```

### 2.2 コンポーネント設計

#### データローダー (`data_loader.py`)
- **責務**: CIFAR-10データセットの読み込みと前処理
- **機能**:
  - torchvisionからのデータセットダウンロード
  - 画像の正規化（mean, std）
  - DataLoaderの作成

#### モデル (`model.py`)
- **責務**: CNNモデルの定義
- **構造**:
  - Conv2d層 × 2
  - MaxPool2d層 × 2
  - 全結合層 × 3
  - ReLU活性化関数

#### トレーナー (`trainer.py`)
- **責務**: モデルの学習と評価
- **機能**:
  - 学習ループ
  - 検証ループ
  - チェックポイント保存
  - メトリクス計算

#### ONNXエクスポーター (`onnx_exporter.py`)
- **責務**: PyTorchモデルをONNX形式に変換
- **機能**:
  - torch.onnx.exportを使った変換
  - ONNX Runtimeでの検証

#### MLflowマネージャー (`mlflow_manager.py`)
- **責務**: 実験の記録
- **機能**:
  - パラメータのログ
  - メトリクスのログ
  - モデルとアーティファクトのログ

### 2.3 技術スタック

- **言語**: Python 3.13
- **深層学習フレームワーク**: PyTorch 2.5+
- **データセット**: torchvision 0.20+
- **実験管理**: MLflow 2.10+
- **モデル変換**: onnx 1.17+, onnxruntime 1.20+
- **テスト**: pytest 8.2+, pytest-cov 5.0+
- **コード品質**: black 24.4+, ruff 0.4+, mypy 1.10+
- **パッケージ管理**: uv

## 3. データ仕様

### 3.1 CIFAR-10データセット

- **サイズ**: 60,000枚（学習50,000枚、テスト10,000枚）
- **画像サイズ**: 32×32ピクセル、RGB（3チャネル）
- **クラス数**: 10クラス
  - 0: airplane（飛行機）
  - 1: automobile（自動車）
  - 2: bird（鳥）
  - 3: cat（猫）
  - 4: deer（鹿）
  - 5: dog（犬）
  - 6: frog（カエル）
  - 7: horse（馬）
  - 8: ship（船）
  - 9: truck（トラック）

### 3.2 データ前処理

```python
transform = transforms.Compose([
    transforms.ToTensor(),  # [0, 255] → [0.0, 1.0]
    transforms.Normalize(
        mean=(0.4914, 0.4822, 0.4465),  # CIFAR-10の平均
        std=(0.2023, 0.1994, 0.2010),   # CIFAR-10の標準偏差
    )
])
```

### 3.3 データ形式

- **入力**: Tensor形状 `(batch_size, 3, 32, 32)`
- **出力**: Tensor形状 `(batch_size, 10)` - 各クラスのスコア（ロジット）

## 4. モデル仕様

### 4.1 SimpleCNNアーキテクチャ

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

### 4.2 学習パラメータ

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| `epochs` | 5 | エポック数（デフォルト） |
| `batch_size` | 32 | バッチサイズ |
| `learning_rate` | 0.001 | 学習率 |
| `optimizer` | Adam | 最適化アルゴリズム |
| `loss` | CrossEntropyLoss | 損失関数 |

### 4.3 評価指標

| メトリクス | 説明 |
|-----------|------|
| `train_loss` | 学習データでの損失 |
| `test_loss` | テストデータでの損失 |
| `test_accuracy` | テストデータでの精度（%） |

## 5. API仕様

### 5.1 主要関数

#### `load_cifar10_data()`
```python
def load_cifar10_data(
    batch_size: int = 32,
    data_dir: str = "./data"
) -> tuple[DataLoader, DataLoader]:
    """
    CIFAR-10データセットを読み込む。

    Args:
        batch_size: バッチサイズ
        data_dir: データ保存ディレクトリ

    Returns:
        (train_loader, test_loader): 学習用とテスト用のDataLoader
    """
```

#### `create_simple_cnn()`
```python
def create_simple_cnn() -> nn.Module:
    """
    SimpleCNNモデルを作成する。

    Returns:
        SimpleCNN: 初期化されたモデル
    """
```

#### `train_model()`
```python
def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    epochs: int = 5,
    learning_rate: float = 0.001,
    device: str = "cpu",
) -> dict[str, float]:
    """
    モデルを学習する。

    Args:
        model: 学習対象のモデル
        train_loader: 学習データローダー
        test_loader: テストデータローダー
        epochs: エポック数
        learning_rate: 学習率
        device: デバイス（"cpu" or "cuda"）

    Returns:
        metrics: 最終的なメトリクス（test_loss, test_accuracy）
    """
```

#### `export_to_onnx()`
```python
def export_to_onnx(
    model: nn.Module,
    onnx_path: str,
    input_shape: tuple[int, int, int, int] = (1, 3, 32, 32)
) -> None:
    """
    PyTorchモデルをONNX形式にエクスポートする。

    Args:
        model: エクスポート対象のモデル
        onnx_path: ONNX保存先パス
        input_shape: 入力テンソルの形状
    """
```

#### `validate_onnx_model()`
```python
def validate_onnx_model(
    pytorch_model: nn.Module,
    onnx_path: str,
    test_input: torch.Tensor,
) -> bool:
    """
    ONNXモデルとPyTorchモデルの予測が一致するか検証する。

    Args:
        pytorch_model: PyTorchモデル
        onnx_path: ONNXモデルのパス
        test_input: テスト用入力テンソル

    Returns:
        bool: 予測が一致すればTrue
    """
```

## 6. ファイル構成

```
06_cifar10_cnn/
├── SPECIFICATION.md              # この仕様書
├── README.md                     # プロジェクト説明
├── pyproject.toml                # プロジェクト設定
├── .python-version               # Python 3.13
├── src/
│   └── cifar10_cnn/
│       ├── __init__.py
│       ├── data_loader.py        # データ読み込み
│       ├── model.py              # CNNモデル定義
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
├── data/                         # CIFAR-10データ（gitignore）
├── mlruns/                       # MLflow実験記録（gitignore）
└── models/                       # 保存モデル（gitignore）
```

## 7. 成功基準

### 7.1 機能要件

- [ ] CIFAR-10データセットを正常にダウンロード・読み込みできる
- [ ] SimpleCNNモデルが正しく定義されている
- [ ] 学習が正常に実行され、損失が減少する
- [ ] テスト精度が30%以上（ランダム予測10%を上回る）
- [ ] MLflowにパラメータ、メトリクス、モデルが記録される
- [ ] ONNXモデルがエクスポートされる
- [ ] ONNXモデルとPyTorchモデルの予測が一致する

### 7.2 非機能要件

- [ ] 全テストケースがパス（100%成功）
- [ ] コードカバレッジ100%
- [ ] black、ruff、mypyがエラーなし
- [ ] GPU利用可能時は自動的にGPUで学習
- [ ] チェックポイント保存により学習再開可能

### 7.3 ドキュメント

- [ ] README.mdが完備されている
- [ ] 各関数にdocstringが記載されている
- [ ] セットアップ手順が明確

## 8. 制約事項

### 8.1 技術的制約

- **Python 3.13以上**: 最新の型ヒント機能を利用
- **PyTorch 2.5以上**: ONNX変換の互換性確保
- **メモリ**: 最低2GB以上のRAM推奨
- **ディスク**: データとモデル保存に500MB以上の空き容量

### 8.2 学習上の制約

- **エポック数**: デフォルト5エポック（短時間で完了するため）
- **モデル複雑度**: SimpleCNNのみ（VGG等の大規模モデルは対象外）
- **データ拡張**: 実装しない（基本的な正規化のみ）

### 8.3 スコープ外

- 複数モデルの比較実験
- ハイパーパラメータチューニング
- Dockerコンテナ化
- gRPCベースの推論サーバー
- データ拡張（Augmentation）
- 学習率スケジューリング

## 9. リスクと対策

### 9.1 リスク

| リスク | 影響 | 対策 |
|-------|------|------|
| データダウンロード失敗 | 学習不可 | リトライ機構、キャッシュ利用 |
| メモリ不足 | クラッシュ | バッチサイズ削減の推奨 |
| GPU利用不可 | 学習時間増大 | CPU自動フォールバック |
| ONNX変換失敗 | エクスポート不可 | PyTorchバージョン検証 |

### 9.2 対策の実装

- エラーハンドリングの徹底
- ログ出力の充実
- デバイス自動検出（CPU/GPU）
- テストでの事前検証

## 10. 参考資料

- [PyTorch公式ドキュメント](https://pytorch.org/docs/stable/index.html)
- [CIFAR-10データセット](https://www.cs.toronto.edu/~kriz/cifar.html)
- [torchvision datasets](https://pytorch.org/vision/stable/datasets.html)
- [ONNX公式ドキュメント](https://onnx.ai/)
- [MLflow公式ドキュメント](https://mlflow.org/docs/latest/index.html)

---

**作成日**: 2025-11-05
**作成者**: kshr123
**バージョン**: 1.0
