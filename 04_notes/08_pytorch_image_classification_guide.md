# PyTorch画像分類 完全ガイド - 初心者向け

> **このガイドの対象者**: PyTorchを初めて使う方、深層学習で画像分類に挑戦したい方

**実例プロジェクト**: [06_cifar10_cnn](../03_my_implementations/chapter2_training/06_cifar10_cnn/)

---

## 📋 目次

1. [PyTorchとは？](#1-pytorchとは)
2. [画像分類の基礎](#2-画像分類の基礎)
3. [CNN（畳み込みニューラルネットワーク）の仕組み](#3-cnn畳み込みニューラルネットワークの仕組み)
4. [PyTorchの基本概念](#4-pytorchの基本概念)
5. [実践: CIFAR-10画像分類](#5-実践-cifar-10画像分類)
6. [よくある質問とトラブルシューティング](#6-よくある質問とトラブルシューティング)
7. [次のステップ](#7-次のステップ)

---

## 1. PyTorchとは？

### 1.1 PyTorchの特徴

**PyTorch**は、Metaが開発したオープンソースの深層学習フレームワークです。

| 特徴 | 説明 |
|------|------|
| **Pythonライク** | Pythonの文法で直感的に書ける |
| **動的計算グラフ** | 柔軟なモデル構築が可能 |
| **豊富なライブラリ** | 画像（torchvision）、自然言語（torchtext）など |
| **研究から本番まで** | プロトタイピングから本番デプロイまで対応 |
| **大規模コミュニティ** | 豊富なドキュメントとサンプル |

### 1.2 他のフレームワークとの比較

| フレームワーク | 特徴 | 適用場面 |
|--------------|------|---------|
| **PyTorch** | 柔軟性高い、研究向き | 研究、カスタムモデル開発 |
| **TensorFlow/Keras** | 本番デプロイに強い | 大規模本番環境 |
| **scikit-learn** | 古典的機械学習 | 表形式データ、軽量モデル |

### 1.3 インストール

```bash
# CPU版（開発・学習用）
pip install torch torchvision

# GPU版（CUDA 11.8の場合）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# または uv を使用（推奨）
uv pip install torch torchvision
```

**確認**:
```python
import torch
print(torch.__version__)  # 例: 2.5.0
print(torch.cuda.is_available())  # GPUが使えるか確認
```

---

## 2. 画像分類の基礎

### 2.1 画像分類とは？

**画像分類**: 画像を見て、それが何のカテゴリに属するかを判定するタスク

**例**:
```
入力画像: 🐱 → 出力: "猫" (10クラス中の1つ)
入力画像: 🚗 → 出力: "車" (10クラス中の1つ)
```

### 2.2 CIFAR-10データセット

CIFAR-10は画像分類の学習に最適な標準データセットです。

| 項目 | 内容 |
|------|------|
| **画像サイズ** | 32×32ピクセル（小さい！） |
| **チャンネル数** | 3（RGB: Red, Green, Blue） |
| **クラス数** | 10（飛行機、車、鳥、猫、鹿、犬、カエル、馬、船、トラック） |
| **学習データ** | 50,000枚 |
| **テストデータ** | 10,000枚 |

**データの形状**:
```python
# 1枚の画像: (3, 32, 32) = (チャンネル, 高さ, 幅)
# バッチ処理: (32, 3, 32, 32) = (バッチサイズ, チャンネル, 高さ, 幅)
```

### 2.3 画像データの前処理

画像をニューラルネットワークに入力する前に行う処理：

```python
from torchvision import transforms

transform = transforms.Compose([
    transforms.ToTensor(),        # PIL Image → Tensor ([0, 255] → [0.0, 1.0])
    transforms.Normalize(
        mean=(0.4914, 0.4822, 0.4465),  # CIFAR-10の平均
        std=(0.2023, 0.1994, 0.2010),   # CIFAR-10の標準偏差
    ),
])
```

**正規化の効果**:
- 学習が安定する（勾配消失・爆発を防ぐ）
- 収束が早くなる

---

## 3. CNN（畳み込みニューラルネットワーク）の仕組み

### 3.1 なぜCNNが画像に強いのか？

**従来の全結合ネットワークの問題**:
```python
# 32×32×3 = 3,072ピクセルを全て全結合層につなぐ
# → パラメータ数が爆発的に増える
# → 空間的な情報（隣接ピクセルの関係）が失われる
```

**CNNの利点**:
- **局所的な特徴を抽出**: 畳み込み層が小さなフィルタで特徴を検出
- **パラメータ共有**: 同じフィルタを画像全体に適用 → パラメータ削減
- **階層的な特徴学習**: 浅い層でエッジ、深い層で複雑な形状を学習

### 3.2 CNNの基本構成要素

#### 3.2.1 畳み込み層（Convolutional Layer）

```python
nn.Conv2d(in_channels=3, out_channels=6, kernel_size=5)
```

**役割**: フィルタ（カーネル）で画像をスキャンして特徴を抽出

```
入力: (batch, 3, 32, 32)   # RGBの32×32画像
  ↓ 畳み込み (kernel=5×5)
出力: (batch, 6, 28, 28)   # 6種類の特徴マップ
```

**パラメータ数**:
```
= (kernel_size × kernel_size × in_channels + 1) × out_channels
= (5 × 5 × 3 + 1) × 6 = 456
```

#### 3.2.2 活性化関数（ReLU）

```python
F.relu(x)  # max(0, x)
```

**役割**: 非線形性を導入（線形変換だけでは表現力が低い）

```
入力: [-2, -1, 0, 1, 2]
  ↓ ReLU
出力: [0, 0, 0, 1, 2]  # 負の値を0にする
```

#### 3.2.3 プーリング層（Pooling Layer）

```python
nn.MaxPool2d(kernel_size=2, stride=2)
```

**役割**:
- 特徴マップのサイズを縮小（計算量削減）
- 位置の変化に対する頑健性を向上

```
入力: (batch, 6, 28, 28)
  ↓ MaxPooling (2×2)
出力: (batch, 6, 14, 14)  # サイズが半分に
```

**MaxPoolingの動作**:
```
入力（2×2領域）:
  [1, 3]
  [2, 4]
  ↓ 最大値を取る
出力: 4
```

#### 3.2.4 全結合層（Fully Connected Layer）

```python
nn.Linear(in_features=400, out_features=120)
```

**役割**: 抽出された特徴を組み合わせて最終的な分類を行う

```
入力: (batch, 400)  # 畳み込み層からの特徴ベクトル
  ↓ 全結合
出力: (batch, 120)  # 中間表現
  ↓ さらに全結合
出力: (batch, 10)   # 10クラスの確率
```

### 3.3 SimpleCNNアーキテクチャの全体像

```
入力: (batch, 3, 32, 32)
  ↓
[畳み込み1] Conv2d(3→6, kernel=5)    → (batch, 6, 28, 28)
  ↓
[活性化] ReLU                        → (batch, 6, 28, 28)
  ↓
[プーリング1] MaxPool2d(2×2)         → (batch, 6, 14, 14)
  ↓
[畳み込み2] Conv2d(6→16, kernel=5)   → (batch, 16, 10, 10)
  ↓
[活性化] ReLU                        → (batch, 16, 10, 10)
  ↓
[プーリング2] MaxPool2d(2×2)         → (batch, 16, 5, 5)
  ↓
[平坦化] Flatten                     → (batch, 400)
  ↓
[全結合1] Linear(400→120)            → (batch, 120)
  ↓
[活性化] ReLU                        → (batch, 120)
  ↓
[全結合2] Linear(120→84)             → (batch, 84)
  ↓
[活性化] ReLU                        → (batch, 84)
  ↓
[全結合3] Linear(84→10)              → (batch, 10)
  ↓
出力: 10クラスのスコア
```

**パラメータ数**: 合計 62,006

---

## 4. PyTorchの基本概念

### 4.1 Tensor（テンソル）

**Tensor**は多次元配列で、PyTorchの基本データ構造です。

```python
import torch

# スカラー（0次元）
scalar = torch.tensor(5)
print(scalar.shape)  # torch.Size([])

# ベクトル（1次元）
vector = torch.tensor([1, 2, 3])
print(vector.shape)  # torch.Size([3])

# 行列（2次元）
matrix = torch.tensor([[1, 2], [3, 4]])
print(matrix.shape)  # torch.Size([2, 2])

# 画像バッチ（4次元）
images = torch.randn(32, 3, 32, 32)  # (バッチ, チャンネル, 高さ, 幅)
print(images.shape)  # torch.Size([32, 3, 32, 32])
```

### 4.2 nn.Module（モデルの基底クラス）

すべてのニューラルネットワークは`nn.Module`を継承します。

```python
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        # レイヤーを定義
        self.conv1 = nn.Conv2d(3, 6, kernel_size=5)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)

    def forward(self, x):
        # 順伝播の処理を定義
        x = self.pool(F.relu(self.conv1(x)))
        # ... (以下続く)
        return x
```

**重要メソッド**:
- `__init__()`: レイヤーを定義
- `forward()`: 順伝播の処理を定義
- `parameters()`: 学習可能なパラメータを返す
- `train()` / `eval()`: 訓練モード / 評価モードに切り替え

### 4.3 DataLoader（データ読み込み）

**DataLoader**はバッチ処理を自動化します。

```python
from torch.utils.data import DataLoader

# データセットを作成
train_dataset = datasets.CIFAR10(
    root='./data',
    train=True,
    download=True,
    transform=transform
)

# DataLoaderでラップ
train_loader = DataLoader(
    train_dataset,
    batch_size=32,      # 1回に32枚処理
    shuffle=True,       # データをシャッフル
    num_workers=0,      # マルチプロセス数
)

# イテレーションで使用
for images, labels in train_loader:
    print(images.shape)  # torch.Size([32, 3, 32, 32])
    print(labels.shape)  # torch.Size([32])
    break
```

### 4.4 損失関数（Loss Function）

**損失関数**は、予測と正解の「ズレ」を数値化します。

```python
# 多クラス分類では CrossEntropyLoss を使う
criterion = nn.CrossEntropyLoss()

# 例
outputs = model(images)     # (batch, 10) 各クラスのスコア
labels = torch.tensor([3])  # 正解ラベル（クラス3）

loss = criterion(outputs, labels)
print(loss.item())  # 例: 2.3026
```

**よく使う損失関数**:
| 損失関数 | 用途 |
|---------|------|
| `CrossEntropyLoss` | 多クラス分類 |
| `BCELoss` | 二値分類 |
| `MSELoss` | 回帰 |

### 4.5 最適化アルゴリズム（Optimizer）

**オプティマイザ**は、損失を最小化するようにパラメータを更新します。

```python
# Adam（適応的学習率を持つ高性能オプティマイザ）
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
```

**主なオプティマイザ**:
| オプティマイザ | 特徴 |
|--------------|------|
| `SGD` | シンプル、学習率調整が必要 |
| `Adam` | 適応的学習率、多くの場合で高性能 |
| `AdamW` | Adamの改良版、重み減衰が正しい |

### 4.6 デバイス管理（CPU/GPU）

```python
# デバイスを自動選択
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# モデルとデータをデバイスに移動
model = model.to(device)
images = images.to(device)
labels = labels.to(device)
```

---

## 5. 実践: CIFAR-10画像分類

### 5.1 プロジェクト構成

```
06_cifar10_cnn/
├── src/cifar10_cnn/
│   ├── data_loader.py      # データ読み込み
│   ├── model.py            # SimpleCNN定義
│   ├── trainer.py          # 学習・評価
│   ├── onnx_exporter.py    # ONNXエクスポート
│   ├── mlflow_manager.py   # MLflow統合
│   └── train.py            # メインスクリプト
├── tests/                  # テストコード
├── models/                 # 保存モデル
└── mlruns/                 # MLflow記録
```

### 5.2 ステップ1: データ読み込み

**ファイル**: `src/cifar10_cnn/data_loader.py`

```python
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

def get_transforms():
    """CIFAR-10用の前処理を定義"""
    return transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(
            mean=(0.4914, 0.4822, 0.4465),
            std=(0.2023, 0.1994, 0.2010),
        ),
    ])

def load_cifar10_data(batch_size=32, data_dir="./data"):
    """CIFAR-10データセットを読み込み"""
    transform = get_transforms()

    # 学習データ
    train_dataset = datasets.CIFAR10(
        root=data_dir,
        train=True,
        download=True,  # 初回は自動ダウンロード
        transform=transform,
    )

    # テストデータ
    test_dataset = datasets.CIFAR10(
        root=data_dir,
        train=False,
        download=True,
        transform=transform,
    )

    # DataLoaderを作成
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    return train_loader, test_loader
```

**使い方**:
```python
train_loader, test_loader = load_cifar10_data(batch_size=32)

# 確認
print(f"学習バッチ数: {len(train_loader)}")  # 1563 = 50000 / 32
print(f"テストバッチ数: {len(test_loader)}")  # 313 = 10000 / 32
```

### 5.3 ステップ2: モデル定義

**ファイル**: `src/cifar10_cnn/model.py`

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SimpleCNN(nn.Module):
    """CIFAR-10用のシンプルなCNNモデル"""

    def __init__(self):
        super(SimpleCNN, self).__init__()

        # 畳み込み層1: 3チャンネル → 6チャンネル
        self.conv1 = nn.Conv2d(3, 6, kernel_size=5)

        # プーリング層（共通）
        self.pool = nn.MaxPool2d(2, 2)

        # 畳み込み層2: 6チャンネル → 16チャンネル
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)

        # 全結合層
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)  # 10クラス出力

    def forward(self, x):
        """順伝播の定義"""
        # 畳み込み1 + ReLU + プーリング
        x = self.pool(F.relu(self.conv1(x)))

        # 畳み込み2 + ReLU + プーリング
        x = self.pool(F.relu(self.conv2(x)))

        # 平坦化（4次元 → 2次元）
        x = x.view(-1, 16 * 5 * 5)

        # 全結合1 + ReLU
        x = F.relu(self.fc1(x))

        # 全結合2 + ReLU
        x = F.relu(self.fc2(x))

        # 全結合3（出力層、活性化なし）
        x = self.fc3(x)

        return x

def create_simple_cnn():
    """SimpleCNNモデルを作成"""
    return SimpleCNN()
```

**使い方**:
```python
model = create_simple_cnn()
print(model)

# パラメータ数を確認
total_params = sum(p.numel() for p in model.parameters())
print(f"総パラメータ数: {total_params:,}")  # 62,006
```

### 5.4 ステップ3: 学習ループ

**ファイル**: `src/cifar10_cnn/trainer.py`

```python
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict

def train_model(
    model,
    train_loader,
    test_loader,
    epochs=5,
    learning_rate=0.001,
    device="cpu",
):
    """モデルを学習"""
    # デバイスに移動
    model = model.to(device)

    # 損失関数とオプティマイザを定義
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # エポックループ
    for epoch in range(epochs):
        model.train()  # 訓練モードに設定
        running_loss = 0.0

        # バッチループ
        for images, labels in train_loader:
            # デバイスに移動
            images = images.to(device)
            labels = labels.to(device)

            # 1. 勾配をゼロ化
            optimizer.zero_grad()

            # 2. 順伝播
            outputs = model(images)

            # 3. 損失計算
            loss = criterion(outputs, labels)

            # 4. 逆伝播
            loss.backward()

            # 5. パラメータ更新
            optimizer.step()

            running_loss += loss.item()

        # エポック終了時の平均損失
        avg_loss = running_loss / len(train_loader)
        print(f"Epoch [{epoch + 1}/{epochs}], Loss: {avg_loss:.4f}")

    # テストデータで評価
    metrics = evaluate_model(model, test_loader, device)

    return {
        "test_loss": metrics["loss"],
        "test_accuracy": metrics["accuracy"],
    }

def evaluate_model(model, test_loader, device="cpu"):
    """モデルを評価"""
    model.eval()  # 評価モードに設定
    criterion = nn.CrossEntropyLoss()

    total_loss = 0.0
    correct = 0
    total = 0

    # 勾配計算を無効化
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            # 順伝播
            outputs = model(images)

            # 損失計算
            loss = criterion(outputs, labels)
            total_loss += loss.item()

            # 精度計算
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    return {
        "loss": total_loss / len(test_loader),
        "accuracy": 100.0 * correct / total,
    }
```

### 5.5 ステップ4: 学習実行

**ファイル**: `src/cifar10_cnn/train.py`

```python
import torch
from cifar10_cnn.data_loader import load_cifar10_data
from cifar10_cnn.model import create_simple_cnn
from cifar10_cnn.trainer import train_model

def main():
    """メインパイプライン"""
    # ハイパーパラメータ
    batch_size = 32
    epochs = 5
    learning_rate = 0.001

    # デバイス設定
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用デバイス: {device}")

    # データ読み込み
    train_loader, test_loader = load_cifar10_data(batch_size=batch_size)

    # モデル作成
    model = create_simple_cnn()

    # 学習
    metrics = train_model(
        model,
        train_loader,
        test_loader,
        epochs=epochs,
        learning_rate=learning_rate,
        device=device,
    )

    # 結果表示
    print(f"\nテスト精度: {metrics['test_accuracy']:.2f}%")
    print(f"テスト損失: {metrics['test_loss']:.4f}")

if __name__ == "__main__":
    main()
```

### 5.6 実行方法

```bash
# 1. ディレクトリに移動
cd 03_my_implementations/chapter2_training/06_cifar10_cnn

# 2. 仮想環境を有効化
source .venv/bin/activate

# 3. 学習実行
python -m cifar10_cnn.train
```

**実行結果例**:
```
使用デバイス: cpu

Epoch [1/5], Loss: 1.5496
Epoch [2/5], Loss: 1.2592
Epoch [3/5], Loss: 1.1401
Epoch [4/5], Loss: 1.0584
Epoch [5/5], Loss: 0.9950

テスト精度: 62.58%
テスト損失: 1.0755
```

### 5.7 ステップ5: モデル保存と読み込み

```python
# モデル保存（パラメータのみ）
torch.save(model.state_dict(), "models/cifar10_cnn.pth")

# モデル読み込み
model = create_simple_cnn()
model.load_state_dict(torch.load("models/cifar10_cnn.pth"))
model.eval()  # 評価モードに設定

# モデル全体を保存（アーキテクチャ含む）
torch.save(model, "models/cifar10_cnn_full.pth")

# モデル全体を読み込み
model = torch.load("models/cifar10_cnn_full.pth")
```

---

## 6. よくある質問とトラブルシューティング

### Q1: バッチサイズはどう決める？

**A**: メモリ制約と学習安定性のバランス

| バッチサイズ | メリット | デメリット |
|-------------|---------|-----------|
| **小（8-16）** | メモリ節約、汎化性能高い | 学習が不安定、遅い |
| **中（32-64）** | バランスが良い | - |
| **大（128-256）** | 学習が安定、速い | メモリ消費大、汎化性能低下 |

**推奨**: まずは32から始めて、メモリに余裕があれば64に増やす

### Q2: 学習率はどう決める？

**A**: Adamの場合は`0.001`（1e-3）が標準

```python
# 学習率が大きすぎる → 損失が発散
optimizer = optim.Adam(model.parameters(), lr=0.1)  # ❌

# 学習率が小さすぎる → 学習が遅い
optimizer = optim.Adam(model.parameters(), lr=0.00001)  # ❌

# ちょうど良い
optimizer = optim.Adam(model.parameters(), lr=0.001)  # ✅
```

**学習率スケジューリング**（高度）:
```python
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

for epoch in range(epochs):
    train(...)
    scheduler.step()  # 10エポックごとに学習率を0.1倍
```

### Q3: エポック数はどう決める？

**A**: 過学習（オーバーフィッティング）を避ける

```python
# 学習損失とテスト損失を記録
train_losses = []
test_losses = []

for epoch in range(epochs):
    train_loss = train(...)
    test_loss = evaluate(...)

    train_losses.append(train_loss)
    test_losses.append(test_loss)

    # テスト損失が増加し始めたら過学習のサイン
    if len(test_losses) > 2 and test_losses[-1] > test_losses[-2]:
        print("過学習の兆候あり。学習を早期終了します。")
        break
```

**推奨**:
- 最初は5-10エポックで様子見
- 損失が下がり続けるなら20-50エポックまで増やす

### Q4: GPUを使うには？

```python
# 自動デバイス選択
device = "cuda" if torch.cuda.is_available() else "cpu"

# モデルとデータをGPUに移動
model = model.to(device)

for images, labels in train_loader:
    images = images.to(device)
    labels = labels.to(device)
    # ...
```

**GPU確認**:
```bash
# CUDAが利用可能か確認
python -c "import torch; print(torch.cuda.is_available())"

# GPU名を確認
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

### Q5: メモリ不足エラーが出る場合

**エラー**:
```
RuntimeError: CUDA out of memory
```

**対策**:
1. **バッチサイズを減らす**: 32 → 16 → 8
2. **勾配を蓄積**: 小さなバッチを複数回で大きなバッチをシミュレート
   ```python
   accumulation_steps = 4

   for i, (images, labels) in enumerate(train_loader):
       outputs = model(images)
       loss = criterion(outputs, labels) / accumulation_steps
       loss.backward()

       if (i + 1) % accumulation_steps == 0:
           optimizer.step()
           optimizer.zero_grad()
   ```
3. **モデルを小さくする**: チャンネル数を減らす

### Q6: 精度が上がらない場合

**チェックリスト**:

1. **データの正規化を確認**
   ```python
   # 正規化なし → 精度低い
   # 正規化あり → 精度向上
   ```

2. **学習率を調整**
   ```python
   # 0.001 で精度が上がらない → 0.0001 に減らす
   optimizer = optim.Adam(model.parameters(), lr=0.0001)
   ```

3. **モデルを深くする**
   ```python
   # 畳み込み層を追加
   self.conv3 = nn.Conv2d(16, 32, kernel_size=3)
   ```

4. **データ拡張を追加**
   ```python
   transform = transforms.Compose([
       transforms.RandomHorizontalFlip(),  # 左右反転
       transforms.RandomCrop(32, padding=4),  # ランダムクロップ
       transforms.ToTensor(),
       transforms.Normalize(...),
   ])
   ```

### Q7: 損失が`nan`になる場合

**原因**:
- 学習率が大きすぎる
- 勾配爆発

**対策**:
```python
# 1. 学習率を下げる
optimizer = optim.Adam(model.parameters(), lr=0.0001)

# 2. 勾配クリッピング
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

---

## 7. 次のステップ

### 7.1 このガイドで学んだこと

- ✅ PyTorchの基本概念（Tensor, nn.Module, DataLoader）
- ✅ CNNの仕組み（畳み込み層、プーリング層、全結合層）
- ✅ 画像分類の実装（データ読み込み→モデル定義→学習→評価）
- ✅ ハイパーパラメータの調整方法
- ✅ よくあるエラーとその対処法

### 7.2 さらに学ぶためのリソース

#### 📚 公式ドキュメント
- [PyTorch公式チュートリアル](https://pytorch.org/tutorials/)
- [torchvision公式ドキュメント](https://pytorch.org/vision/stable/index.html)

#### 🎓 おすすめコース
- [PyTorch公式: 60分でわかるPyTorch](https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html)
- [fast.ai - Practical Deep Learning](https://course.fast.ai/)

#### 📖 おすすめ書籍
- 『深層学習』（Goodfellow, Bengio, Courville）
- 『PyTorchではじめるディープラーニング実装入門』

### 7.3 次に挑戦すること

#### レベル1: モデルの改善
1. **データ拡張を追加**
   ```python
   transforms.RandomHorizontalFlip(),
   transforms.RandomCrop(32, padding=4),
   transforms.ColorJitter(brightness=0.2, contrast=0.2),
   ```

2. **より深いモデルを試す**
   - VGG11, VGG16
   - ResNet（残差接続）

3. **学習率スケジューリング**
   ```python
   scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
   ```

#### レベル2: 別のデータセットに挑戦
1. **MNIST**: 手書き数字認識（簡単）
2. **Fashion-MNIST**: 衣類画像分類（中級）
3. **ImageNet**: 大規模画像分類（高度）

#### レベル3: 転移学習
```python
import torchvision.models as models

# 事前学習済みモデルを使用
model = models.resnet18(pretrained=True)

# 最終層だけ置き換え
model.fc = nn.Linear(512, 10)  # CIFAR-10用に調整
```

#### レベル4: 本番デプロイ
1. **ONNX形式にエクスポート**
   - 本プロジェクト（06_cifar10_cnn）の`onnx_exporter.py`を参照

2. **FastAPIでWebサービス化**
   - Chapter 4（Serving Patterns）で学習

3. **Docker化**
   - Chapter 3（Release Patterns）で学習

### 7.4 実践プロジェクトのアイデア

1. **動物分類アプリ**
   - 自分で撮影した動物の画像を分類
   - Kaggleの[Dogs vs. Cats](https://www.kaggle.com/c/dogs-vs-cats)データセットを使用

2. **物体検出**
   - YOLO, Faster R-CNNで物体を検出
   - [COCO Dataset](https://cocodataset.org/)を使用

3. **画像生成**
   - GAN（敵対的生成ネットワーク）で画像生成
   - Stable Diffusionの仕組みを学ぶ

4. **医療画像解析**
   - X線画像から病気を検出
   - [ChestX-ray14](https://nihcc.app.box.com/v/ChestXray-NIHCC)データセット

---

## 📝 まとめ

このガイドでは、PyTorchを使った画像分類の基礎から実践までを学びました。

**重要ポイント**:
1. **PyTorch**: 柔軟で直感的な深層学習フレームワーク
2. **CNN**: 畳み込み層で画像の特徴を抽出、階層的に学習
3. **学習ループ**: 勾配ゼロ化 → 順伝播 → 損失計算 → 逆伝播 → パラメータ更新
4. **実践**: データ読み込み → モデル定義 → 学習 → 評価 → 保存

**次のステップ**: このガイドを基に、自分のデータセットやプロジェクトに挑戦しましょう！

---

**参考プロジェクト**: [06_cifar10_cnn](../03_my_implementations/chapter2_training/06_cifar10_cnn/)

**質問・フィードバック**: GitHubのIssueでお気軽にどうぞ！

**最終更新**: 2025-11-05
