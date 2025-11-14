# プロセス vs スレッド 完全ガイド

## 📚 概要

**対象**: プロセスとスレッドの違いを理解したい人、ThreadPoolExecutorとProcessPoolExecutorの使い分けを知りたい人

### 📝 この記事で学べること
- プロセスとスレッドの違い
- ThreadPoolExecutor vs ProcessPoolExecutor
- GIL（Global Interpreter Lock）の制約
- 適切な使い分け方法

### 🎯 こんな時に読む
- 「プロセスとスレッドって何が違うの？」
- 「ThreadPoolExecutorとProcessPoolExecutorどちらを使うべき？」
- 「GILって何？」
- 「並列処理で速くならないのはなぜ？」

### ⏱️ 読了時間
約25分

---

## 🎯 プロセス vs スレッド

### プロセス = 別々のアプリ

```
Google Chrome（プロセス1）
VS Code（プロセス2）
Slack（プロセス3）

→ 完全に独立
→ メモリも別々
→ 1つがクラッシュしても他は無事
```

### スレッド = 1つのアプリの中の作業

```
Google Chrome（1つのプロセス）
  ├ タブ1（スレッド1）
  ├ タブ2（スレッド2）
  └ タブ3（スレッド3）

→ メモリ共有
→ 1つがクラッシュすると全部死ぬ
```

---

## 📊 比較表

| | プロセス | スレッド |
|---|---------|---------|
| **起動時間** | 遅い（100ms） | 速い（1ms） |
| **メモリ** | 大きい（独立） | 小さい（共有） |
| **通信速度** | 遅い（IPC必要） | 速い（メモリ共有） |
| **安全性** | 高い（独立） | 低い（共有） |
| **並列性（Python）** | **真の並列** ⭐ | **並列にならない** ❌ |

---

## 🔒 GIL（Global Interpreter Lock）とは？

### Pythonの制約

**GIL = 同時に1つのスレッドしかPythonコードを実行できない**

```python
# スレッドを4つ起動しても...
CPU Core 1: [Thread 1] ████ ← 実行中
CPU Core 2: [Thread 2] ---- ← 待機中（GILロック）
CPU Core 3: [Thread 3] ---- ← 待機中（GILロック）
CPU Core 4: [Thread 4] ---- ← 待機中（GILロック）

# 同時に動けるのは1つだけ！
```

### なぜGILがあるのか？

1. **メモリ管理を簡単にする**
   - 複数スレッドが同時にメモリを変更すると危険
   - GILで保護することで安全性を確保

2. **Cライブラリとの互換性**
   - 多くのCライブラリはスレッドセーフではない
   - GILがあることで安全に使える

---

## 🐍 ThreadPoolExecutor

### 基本的な使い方

```python
import time
from concurrent.futures import ThreadPoolExecutor

def io_task(n):
    """I/O待ちのタスク"""
    time.sleep(1)  # ファイル読み込み、HTTP通信などをシミュレート
    return n * 2

# 4つのタスクを4スレッドで実行
with ThreadPoolExecutor(max_workers=4) as executor:
    start = time.time()
    results = list(executor.map(io_task, range(4)))
    print(f"時間: {time.time() - start:.2f}秒")

# 実行結果:
# 時間: 1.00秒 ← 1秒 × 4 = 4秒かかるはずが1秒！
```

**なぜ速い？**
```
Thread 1: [開始]--待機--[完了]
Thread 2: [開始]--待機--[完了]  ← 待機中はGIL解放
Thread 3: [開始]--待機--[完了]  ← 他のスレッドが動ける
Thread 4: [開始]--待機--[完了]

I/O待ち中はGILが解放される！
```

### CPU集約的なタスクでは？

```python
def cpu_task(n):
    """CPU集約的なタスク"""
    total = 0
    for i in range(n):
        total += i * i
    return total

# 4つのタスクを4スレッドで実行
with ThreadPoolExecutor(max_workers=4) as executor:
    start = time.time()
    results = list(executor.map(cpu_task, [10_000_000] * 4))
    print(f"時間: {time.time() - start:.2f}秒")

# 実行結果:
# 時間: 4.5秒 ← 速くならない！
```

**なぜ速くならない？**
```
時間軸 →
Thread 1: ████--████--████  ← GILを取得
Thread 2: --████--████--██  ← GILを待つ
Thread 3: ----████--████--  ← GILを待つ
Thread 4: ██----████----██  ← GILを待つ

GILの奪い合いでオーバーヘッド
実質的にシングルスレッドと同じ
```

---

## 🚀 ProcessPoolExecutor

### 基本的な使い方

```python
import time
from concurrent.futures import ProcessPoolExecutor

def cpu_task(n):
    """CPU集約的なタスク"""
    total = 0
    for i in range(n):
        total += i * i
    return total

# 4つのタスクを4プロセスで実行
with ProcessPoolExecutor(max_workers=4) as executor:
    start = time.time()
    results = list(executor.map(cpu_task, [10_000_000] * 4))
    print(f"時間: {time.time() - start:.2f}秒")

# 実行結果:
# 時間: 1.2秒 ← ほぼ4倍速！
```

**なぜ速い？**
```
CPU Core 1: [Process 1] ████████████ ← 独立したPythonインタープリタ
CPU Core 2: [Process 2] ████████████ ← 独立したPythonインタープリタ
CPU Core 3: [Process 3] ████████████ ← 独立したPythonインタープリタ
CPU Core 4: [Process 4] ████████████ ← 独立したPythonインタープリタ

各プロセスが独自のGILを持つ → 真の並列実行！
```

### 注意点

#### 1. プロセス起動のオーバーヘッド

```python
# ❌ 軽いタスクには向かない
with ProcessPoolExecutor() as executor:
    results = executor.map(lambda x: x * 2, range(100))
    # プロセス起動コスト（100ms）> タスク実行時間（1ms）

# ✅ 重いタスクには最適
with ProcessPoolExecutor() as executor:
    results = executor.map(heavy_inference, images)
    # プロセス起動コスト（100ms）< タスク実行時間（5秒）
```

#### 2. プロセス間通信のコスト

```python
# ❌ 大きなデータの受け渡しは遅い
import numpy as np

large_array = np.zeros((1000, 1000, 1000))  # 8GB

def process_data(data):
    return data * 2

with ProcessPoolExecutor() as executor:
    # データをプロセス間でコピー → 遅い！
    result = executor.submit(process_data, large_array)
```

**解決策**: 共有メモリやRedisを使う
```python
# ✅ RedisにデータIDだけ渡す
def process_data(data_id):
    data = redis.get(data_id)  # Redisから取得
    result = data * 2
    redis.set(result_id, result)
    return result_id

with ProcessPoolExecutor() as executor:
    result = executor.submit(process_data, "data_123")
```

---

## 📋 使い分けガイド

### タスクの種類で選ぶ

| タスクの種類 | 推奨 | 理由 |
|------------|------|-----|
| **I/O待ち**<br>（HTTP、ファイル、DB） | **ThreadPoolExecutor** | ✅ GILはI/O待ち中に解放される<br>✅ プロセス起動のオーバーヘッド不要<br>✅ メモリ効率が良い |
| **CPU集約**<br>（計算、画像処理、推論） | **ProcessPoolExecutor** | ✅ GILの制約を回避<br>✅ 真の並列実行が可能<br>✅ マルチコアCPUを最大限活用 |

### 実装パターン別

| パターン | 使用技術 | タスクの種類 |
|---------|---------|------------|
| **Batch Pattern** | ThreadPoolExecutor | DB読み込み + 推論（I/O待ちが多い） |
| **Sync-Async Pattern** | **ProcessPoolExecutor** | 推論処理（CPU集約的） |

---

## 💡 実践例

### 例1：画像処理（CPU集約的）

```python
from concurrent.futures import ProcessPoolExecutor
from PIL import Image

def resize_image(image_path):
    """CPU集約的な画像処理"""
    img = Image.open(image_path)
    img = img.resize((800, 600))
    img.save(f"resized_{image_path}")
    return image_path

# 100枚の画像を処理
images = [f"image_{i}.jpg" for i in range(100)]

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(resize_image, images))

# 4コアCPUで約4倍速！
```

### 例2：APIリクエスト（I/O待ち）

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def fetch_url(url):
    """I/O待ちが多い"""
    response = requests.get(url)
    return response.text

# 100個のURLから取得
urls = [f"https://api.example.com/data/{i}" for i in range(100)]

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch_url, urls))

# 10スレッドで並行実行
```

### 例3：機械学習推論（CPU集約的）

```python
from concurrent.futures import ProcessPoolExecutor
import onnxruntime as ort

def predict_batch(images):
    """CPU集約的な推論"""
    session = ort.InferenceSession("model.onnx")
    results = []
    for image in images:
        output = session.run(None, {"input": image})
        results.append(output)
    return results

# データを分割
batches = split_into_batches(all_images, batch_size=100)

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(predict_batch, batches))

# 4プロセスで並列推論！
```

---

## 🎯 まとめ

### プロセス vs スレッド

| 特徴 | プロセス | スレッド |
|-----|---------|---------|
| **独立性** | 完全に独立 | メモリ共有 |
| **起動速度** | 遅い | 速い |
| **メモリ** | 多い | 少ない |
| **並列性（Python）** | **真の並列** ⭐ | GILで制限 |

### ThreadPoolExecutor vs ProcessPoolExecutor

| | ThreadPoolExecutor | ProcessPoolExecutor |
|---|-------------------|---------------------|
| **適用場面** | I/O待ち | CPU集約 |
| **速度向上** | I/O待ち時のみ | 常に向上 |
| **オーバーヘッド** | 小さい | 大きい |
| **メモリ** | 共有（効率的） | 独立（非効率） |

### 選択フローチャート

```
タスクを分類
    ↓
CPU計算が多い？
    YES → ProcessPoolExecutor
    NO  → I/O待ちが多い？
            YES → ThreadPoolExecutor
            NO  → 並列化不要
```

---

## 📖 参考リンク

- [concurrent.futures公式ドキュメント](https://docs.python.org/ja/3/library/concurrent.futures.html)
- [GILについて](https://wiki.python.org/moin/GlobalInterpreterLock)
- [並行実行 vs 並列実行ガイド](./11_concurrency_vs_parallelism.md)

---

**作成日**: 2025-11-14
**関連パターン**: Sync-Async Pattern (Chapter 4)
