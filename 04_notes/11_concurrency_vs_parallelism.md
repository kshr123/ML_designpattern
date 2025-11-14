# 並行実行 vs 並列実行 完全ガイド

## 📚 概要

**対象**: 非同期処理・並列処理を理解したい人、asyncio.gatherの仕組みを知りたい人

### 📝 この記事で学べること
- 並行実行（Concurrency）と並列実行（Parallelism）の違い
- asyncio.gatherの仕組みと使い方
- multiprocessingとの違い
- 適切な技術選択の方法

### 🎯 こんな時に読む
- 「並行と並列って何が違うの？」
- 「asyncio.gatherはなぜ速い？」
- 「multiprocessingとasyncioどちらを使うべき？」
- 「Horizontal Microservice Patternの仕組みを理解したい」

### ⏱️ 読了時間
約40分

---

## 🎯 核心の違い

### 並列実行（Parallelism）
**複数のタスクが物理的に同時に実行される**

```
CPU Core 1: ████████████ (Task A)
CPU Core 2: ████████████ (Task B)  ← 同時刻に両方実行
CPU Core 3: ████████████ (Task C)

必要なもの: マルチコア CPU、マルチスレッド/マルチプロセス
```

### 並行実行/非同期実行（Concurrency）
**複数のタスクが論理的に同時進行しているように見える**

```
Single Core: ██A██B██A██C██B██A██C  ← 高速に切り替え

タスクAの実行 → 待ち時間（I/O）→ タスクBに切り替え
              → タスクBも待ち → タスクCに切り替え
              → タスクAの続き...

必要なもの: シングルコアでもOK
```

---

## 🌟 具体例で理解する

### 例：コーヒーショップ

#### 並列実行（Parallelism）
```
バリスタ1: [エスプレッソ抽出] ← 同時に作業
バリスタ2: [ミルク泡立て]     ← 同時に作業
バリスタ3: [ドリップコーヒー] ← 同時に作業

3人が「物理的に同時」に作業
```

**特徴**:
- 3人のバリスタが必要（リソース消費大）
- 本当に同時に作業している
- 作業が終わる時間 = max(各作業時間)

#### 並行実行（Concurrency）
```
バリスタ1人:
1. エスプレッソマシン起動 → 抽出待ち（30秒）
2. 待っている間にミルク泡立て開始 → 待ち（20秒）
3. 待っている間にドリップコーヒー準備
4. エスプレッソ完成 → 仕上げ
5. ミルク完成 → 仕上げ

1人が「待ち時間を活用」して複数タスクを進行
```

**特徴**:
- 1人のバリスタでOK（リソース効率的）
- 待ち時間を有効活用
- 作業が終わる時間 ≈ max(各作業時間) + 切り替えコスト

---

## 🐍 Pythonでの実装

### 1. 並行実行（asyncio）← asyncio.gatherはこれ！

```python
import asyncio
import time

async def task_a():
    print("Task A: 開始")
    await asyncio.sleep(2)  # I/O待ち（ネットワーク通信など）
    print("Task A: 完了")
    return "A"

async def task_b():
    print("Task B: 開始")
    await asyncio.sleep(2)  # I/O待ち
    print("Task B: 完了")
    return "B"

async def main():
    start = time.time()

    # 並行実行
    results = await asyncio.gather(task_a(), task_b())

    print(f"時間: {time.time() - start:.2f}秒")
    print(f"結果: {results}")

# 実行結果:
# Task A: 開始
# Task B: 開始
# Task A: 完了
# Task B: 完了
# 時間: 2.00秒  ← 2秒 + 2秒 = 2秒（並行実行）
# 結果: ['A', 'B']
```

**重要**: これは**シングルスレッド**で動いています！

```
イベントループ（1つのスレッド）:
[Task A開始] → await(I/O待ち) → [Task B開始] → await(I/O待ち)
→ [Task A完了] → [Task B完了]

CPUは1つのコアしか使っていない
```

### 2. 並列実行（multiprocessing）

```python
import multiprocessing
import time

def cpu_task(name):
    """CPU集約的なタスク"""
    print(f"Task {name}: 開始")
    total = 0
    for i in range(100_000_000):  # CPU計算
        total += i
    print(f"Task {name}: 完了")
    return name

if __name__ == "__main__":
    start = time.time()

    # 並列実行（マルチプロセス）
    with multiprocessing.Pool(processes=2) as pool:
        results = pool.map(cpu_task, ["A", "B"])

    print(f"時間: {time.time() - start:.2f}秒")
    print(f"結果: {results}")

# 実行結果（2コアCPUの場合）:
# Task A: 開始
# Task B: 開始
# Task A: 完了
# Task B: 完了
# 時間: 3.00秒  ← 3秒 + 3秒 = 3秒（並列実行）
# 結果: ['A', 'B']

# シングルスレッドで逐次実行なら: 6秒かかる
```

**重要**: これは**マルチプロセス**で、物理的に2つのCPUコアを使っています！

---

## 📐 図解：並行 vs 並列

### 並行実行（Concurrency）- asyncio
```
時間軸 →
Thread 1: [A1]--wait--[A2]--wait--[A3]
           ↓          ↓          ↓
           [B1]--wait--[B2]--wait--[B3]
                  ↓          ↓
                  [C1]--wait--[C2]

1つのスレッドが高速に切り替わる
waitの間に他のタスクを実行
```

### 並列実行（Parallelism）- multiprocessing
```
時間軸 →
Thread 1: [A1][A2][A3][A4][A5]
Thread 2: [B1][B2][B3][B4][B5]  ← 同時実行
Thread 3: [C1][C2][C3][C4][C5]  ← 同時実行

複数のスレッド/プロセスが同時に実行
```

---

## 🔄 逐次実行 vs 並行実行の違い

### ❌ 逐次実行（asyncio.gatherを使わない場合）

```python
async with httpx.AsyncClient() as client:
    result1 = await client.post("http://service_setosa:8000/predict", ...)
    result2 = await client.post("http://service_versicolor:8000/predict", ...)
    result3 = await client.post("http://service_virginica:8000/predict", ...)
```

**実行時間**：
```
Service Setosa:     100ms
Service Versicolor: 100ms
Service Virginica:  100ms
─────────────────────────
合計: 300ms ⏱️
```

### ✅ 並行実行（asyncio.gatherを使う場合）

```python
async with httpx.AsyncClient() as client:
    tasks = [
        client.post("http://service_setosa:8000/predict", ...),
        client.post("http://service_versicolor:8000/predict", ...),
        client.post("http://service_virginica:8000/predict", ...)
    ]
    results = await asyncio.gather(*tasks)  # 並行実行！
```

**実行時間**：
```
Service Setosa:     ████████████ 100ms
Service Versicolor: ████████████ 100ms (同時実行)
Service Virginica:  ████████████ 100ms (同時実行)
─────────────────────────────────
合計: 100ms ⚡ (約3倍速い！)
```

---

## 🎯 asyncio.gatherは並行？並列？

**答え: 並行実行（Concurrency）**です！

```python
# Horizontal Microservice Patternの例
async def main():
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post("http://service1:8000/predict", ...),
            client.post("http://service2:8000/predict", ...),
            client.post("http://service3:8000/predict", ...)
        ]
        results = await asyncio.gather(*tasks)
```

**動作の仕組み**:
```
1. Task 1: HTTPリクエスト送信 → ネットワーク待ち
2. Task 2: HTTPリクエスト送信 → ネットワーク待ち  ← 待ってる間に実行
3. Task 3: HTTPリクエスト送信 → ネットワーク待ち  ← 待ってる間に実行
4. Task 1: レスポンス受信
5. Task 2: レスポンス受信
6. Task 3: レスポンス受信

全てシングルスレッドで動作！
```

---

## 🎯 なぜasyncio.gatherを使うのか？

### 1. **I/O待機時間の有効活用**

```python
# HTTPリクエストは「待ち時間」が長い

[リクエスト送信] ← 0.1ms
[ネットワーク通信] ← 10ms
[サーバー処理] ← 50ms    ← この間、CPUは遊んでいる！
[レスポンス受信] ← 10ms
```

**asyncio.gather**を使うと、この待ち時間に他のリクエストを処理できます。

### 2. **スケーラビリティ**

```python
# サービスが増えても、レスポンス時間は変わらない！

3サービス: 100ms
5サービス: 100ms  ← 並行実行だから
10サービス: 100ms
```

逐次実行だと：
```python
3サービス: 300ms
5サービス: 500ms
10サービス: 1000ms  ← 遅すぎる！
```

### 3. **リソース効率**

```python
# 1つのProxyコンテナで複数サービスを呼び出せる

CPU使用率: 5% ← ほとんどI/O待ち
メモリ: 50MB
スループット: 高い ✅
```

---

## 📊 使い分け

| タスクの種類 | 最適な方法 | 理由 |
|------------|----------|-----|
| **I/O待ち**<br>（HTTP、ファイル、DB） | **asyncio** | 待ち時間が長い→並行実行で効率化 |
| **CPU集約**<br>（画像処理、計算） | **multiprocessing** | CPU使用率が高い→並列実行が必要 |
| **両方混在** | **asyncio + ProcessPoolExecutor** | 組み合わせて使う |

---

## 💡 実世界の例

### 例1：レコメンデーションシステム
```python
# 複数のレコメンドモデルを並行実行
results = await asyncio.gather(
    collaborative_filtering_service(),  # 100ms
    content_based_service(),            # 120ms
    deep_learning_service()             # 150ms
)
# 合計: 150ms（最も遅いモデルの時間）
# 逐次実行なら: 370ms
```

### 例2：マルチモーダルAI
```python
# 画像・テキスト・音声を同時処理
results = await asyncio.gather(
    image_analysis_service(image),    # 200ms
    text_sentiment_service(text),     # 100ms
    speech_recognition_service(audio) # 300ms
)
# 合計: 300ms
# 逐次実行なら: 600ms
```

---

## 🏗️ Horizontal Microservice Patternでの実装

### レイヤー別整理

| レイヤー | 実行方式 | 実装技術 | 説明 |
|---------|---------|---------|------|
| **インフラ** | **並列実行** | Docker Compose | 4つのコンテナが物理的に並列動作 |
| **Proxy** | **並行実行** | asyncio.gather | HTTPリクエストをI/O待ち活用で並行処理 |
| **各サービス** | 同期実行 | 通常のdef | ONNX推論は同期的に実行 |

### システム全体では「並列実行」している

**コンテナレベル（インフラ）では並列**:
```yaml
# docker-compose.yml
services:
  proxy:           # プロセス1
  service_setosa:  # プロセス2  ← 物理的に別プロセス
  service_versicolor: # プロセス3  ← 物理的に別プロセス
  service_virginica:  # プロセス4  ← 物理的に別プロセス
```

**実行の様子**：
```
CPU Core 1: [Proxy]             ← コンテナ1
CPU Core 2: [Service Setosa]    ← コンテナ2（並列実行）
CPU Core 3: [Service Versicolor]← コンテナ3（並列実行）
CPU Core 4: [Service Virginica] ← コンテナ4（並列実行）
```

**Pythonコードレベルでは並行**:
```python
# Proxyの中（シングルスレッド）
async with httpx.AsyncClient() as client:
    # HTTPリクエストを3つ送信
    task1 = client.post("service_setosa:8000", ...)    # I/O待ち
    task2 = client.post("service_versicolor:8000", ...) # I/O待ち
    task3 = client.post("service_virginica:8000", ...)  # I/O待ち

    # 並行実行（シングルスレッドで待ち時間を活用）
    results = await asyncio.gather(task1, task2, task3)
```

---

## 📚 asyncio.gatherの特徴

### メリット ✅
- **並行実行**で大幅な速度向上
- **エラーハンドリング**が容易（`return_exceptions=True`オプション）
- **コードが簡潔**

### 注意点 ⚠️
```python
# すべてのタスクが完了するまで待つ
# 1つでも遅いサービスがあると、全体が遅くなる

results = await asyncio.gather(
    fast_service(),   # 10ms
    slow_service(),   # 5000ms ← これが終わるまで待つ
    fast_service2()   # 20ms
)
# 合計: 5000ms
```

**対策**：タイムアウトを設定
```python
async with asyncio.timeout(1.0):  # 1秒でタイムアウト
    results = await asyncio.gather(*tasks)
```

---

## 🎯 なぜこの設計なのか？

### 1. Proxyで並行実行（asyncio）を使う理由
```python
# HTTPリクエスト = I/O待ちが支配的
# → asyncioが最適

await asyncio.gather(
    client.post(...),  # ネットワーク待ち 50ms
    client.post(...),  # ネットワーク待ち 50ms
    client.post(...)   # ネットワーク待ち 50ms
)
# 合計: 50ms（並行実行）
# 逐次実行なら: 150ms
```

### 2. 各サービスで並列実行（multiprocessing）を使わない理由

```python
# 各サービスは既に独立したコンテナ
# → わざわざmultiprocessingする必要がない！

# もしmultiprocessingを使うと:
# Container 1 (Service Setosa)
#   → Process 1
#   → Process 2  ← 不要なオーバーヘッド
#   → Process 3
```

### 3. 各サービスの推論を同期実行にする理由

```python
# ONNX Runtimeの推論は：
# - CPU/GPU計算が中心
# - 1リクエストあたり数十ms
# → 並行・並列化する必要性が低い

def predict(data):
    return self.session.run(...)  # 50ms で完了
```

---

## 💡 もし両方使うとしたら？

実際のプロダクションでは、こういうケースがあります：

```python
# 例：各サービス内でバッチ推論する場合

# src/services/routers.py
import asyncio
from concurrent.futures import ProcessPoolExecutor

# 並列実行プール（CPU集約的なタスク用）
executor = ProcessPoolExecutor(max_workers=4)

@router.post("/predict/batch")
async def predict_batch(requests: List[PredictRequest]):
    """大量の推論リクエストを処理"""

    # CPU集約的なタスクをmultiprocessingで並列実行
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(executor, predictor.predict, req.data)
        for req in requests
    ]

    # asyncioで並行実行を調整
    results = await asyncio.gather(*tasks)

    return results

# これなら両方使っている！
```

---

## 🎯 まとめ

| 概念 | 英語 | 実行方法 | CPUコア | 適用場面 |
|-----|------|---------|---------|---------|
| **並行実行** | Concurrency | asyncio | 1つ | I/O待ち |
| **並列実行** | Parallelism | multiprocessing | 複数 | CPU計算 |

**asyncio.gatherの正体**:
- ✅ 並行実行（Concurrency）
- ❌ 並列実行（Parallelism）ではない
- **I/O待ち時間を活用**して複数タスクを進行
- シングルスレッドで動作

**Horizontal Microservice Patternでは**:
- HTTPリクエスト = I/O待ちが主体
- → asyncio.gather（並行実行）が最適
- 「並列」と言っても通じるが、正確には「並行」

この違いを理解すると、適切な技術選択ができるようになります！🚀

---

## 📖 参考リンク

- [asyncio公式ドキュメント](https://docs.python.org/ja/3/library/asyncio.html)
- [multiprocessing公式ドキュメント](https://docs.python.org/ja/3/library/multiprocessing.html)
- [ONNX推論パターン完全ガイド](./06_onnx_inference_patterns.md)

---

**作成日**: 2025-11-14
**関連パターン**: Horizontal Microservice Pattern (Chapter 4)
