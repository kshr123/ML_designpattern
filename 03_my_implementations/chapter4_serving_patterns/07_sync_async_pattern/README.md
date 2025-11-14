# Sync-Async Pattern（時間差推論パターン）

## 📚 概要

**速いモデルで即座にレスポンス + 遅い高精度モデルを裏で実行**

- **Proxy**: FastAPI + MobileNet v2（同期推論） → 即レスポンス
- **Worker**: ProcessPoolExecutor + ResNet50（非同期推論） → 裏で処理
- **Queue**: Redis（ジョブ管理 + 結果ストア）

## 🎯 このパターンの価値

**問題**:
```
速いモデル（MobileNet v2）: 50ms、精度80%
遅いモデル（ResNet50）: 500ms、精度90%

ユーザーは待ちたくない！でも高精度も欲しい！
```

**解決策**:
```
1. 速いモデルで即座に返す → UX向上 ✅
2. 遅いモデルは裏で処理 → 品質向上 ✅
3. 後から高精度結果を取得可能 → 柔軟性 ✅
```

---

## 🆕 このパターンで学ぶ新技術

### 1. ProcessPoolExecutor ⭐

**何？**: プロセスベースの並列実行（真の並列！）

**これまで**: ThreadPoolExecutor（スレッドベース、GILで制限）
**今回**: ProcessPoolExecutor（**プロセスベース、GILなし**）

**違い**:
```python
# ThreadPoolExecutor: GILの制約あり
Thread 1: 計算中 ████
Thread 2: 待機中 ----  ← 同時に動けない
Thread 3: 待機中 ----

# ProcessPoolExecutor: 真の並列実行
Process 1: 計算中 ████  ← 全部同時に動く！
Process 2: 計算中 ████
Process 3: 計算中 ████
```

**使い方**:
```python
from concurrent.futures import ProcessPoolExecutor

def heavy_task(data):
    return model.predict(data)  # CPU集約的

# 4プロセスで並列実行
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(heavy_task, data_list))
```

**詳細**: [04_notes/12_process_vs_thread.md](../../../04_notes/12_process_vs_thread.md)

---

### 2. FastAPI BackgroundTasks ⭐

**何？**: レスポンスを返した後も処理を続ける

**例**:
```python
from fastapi import BackgroundTasks

@app.post("/predict")
def predict(image: Image, background_tasks: BackgroundTasks):
    # 1. 速いモデル（即座に実行）
    result_fast = mobilenet.predict(image)  # 50ms

    # 2. 遅いモデル（裏で実行）
    background_tasks.add_task(
        save_to_queue,
        image,
        job_id
    )

    # 3. すぐ返す！
    return {"result": result_fast, "job_id": job_id}

# ユーザー: 50msで結果もらえる 😊
# 裏: 重いモデルがゆっくり処理
```

**メリット**:
- ✅ ユーザーを待たせない
- ✅ 重い処理は裏で継続
- ✅ FastAPI標準機能

---

## 🏗️ アーキテクチャ

```
ユーザー
   ↓ POST /predict
Proxy (FastAPI)
   ├→ MobileNet v2（同期）→ 即座に結果返却 ⚡
   └→ BackgroundTasks → Redisキューに登録
        ↓
      Backend Worker (ProcessPoolExecutor)
        └→ ResNet50（非同期）→ 結果をRedisに保存 🐢

GET /job/{job_id}
   ↓
Proxy → Redisから遅い推論の結果を取得
```

### 技術スタック

| コンポーネント | 技術 | 役割 |
|------------|------|------|
| **Proxy** | FastAPI + ONNX Runtime + BackgroundTasks | 同期推論、ジョブ登録 |
| **Worker** | ProcessPoolExecutor + ONNX Runtime | 非同期推論（並列） |
| **Models** | MobileNet v2（速い）、ResNet50（遅くて高精度） | 推論 |
| **Queue** | Redis | ジョブ管理 + 結果ストア |

---

## 📊 他のパターンとの比較

| パターン | 並列化技術 | タスクの種類 |
|---------|----------|------------|
| **Batch** | ThreadPoolExecutor | DB読み込み（I/O待ち） |
| **Asynchronous** | asyncio.gather | HTTPリクエスト（I/O待ち） |
| **Horizontal Microservice** | asyncio.gather | HTTPリクエスト（I/O待ち） |
| **Sync-Async** | **ProcessPoolExecutor** ⭐ | **推論処理（CPU集約）** |

---

## 🚀 クイックスタート

### 1. ユニットテスト

```bash
# 仮想環境セットアップ
echo "3.13" > .python-version
uv venv
source .venv/bin/activate

# 依存関係インストール
uv pip install -r requirements.txt
uv pip install pytest pytest-cov fakeredis

# モデルダウンロード
curl -L -o models/mobilenet_v2.onnx \
  https://github.com/onnx/models/raw/main/validated/vision/classification/mobilenet/model/mobilenetv2-12.onnx

curl -L -o models/resnet50.onnx \
  https://github.com/onnx/models/raw/main/validated/vision/classification/resnet/model/resnet50-v2-7.onnx

# テスト実行
pytest tests/ -v

# 結果: ✅ 11/11 passed
```

### 2. Docker Compose で E2E テスト

```bash
# Dockerで起動
docker compose up -d --build

# ヘルスチェック
curl http://localhost:8000/health

# E2Eテスト実行
./test_e2e.sh

# 停止
docker compose down
```

---

## 🔌 API仕様

### 1. ヘルスチェック

**エンドポイント**: `GET /health`

**レスポンス**:
```json
{
  "status": "healthy"
}
```

### 2. 推論リクエスト（同期 + 非同期ジョブ登録）

**エンドポイント**: `POST /predict`

**リクエスト**:
```json
{
  "image_data": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**レスポンス**:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "result_sync": "tabby cat"
}
```

- `job_id`: 非同期ジョブのUUID
- `result_sync`: MobileNet v2 による同期推論結果（即座）

### 3. 非同期ジョブ結果取得

**エンドポイント**: `GET /job/{job_id}`

**レスポンス**（完了時）:
```json
{
  "prediction": "Persian cat"
}
```

**レスポンス**（処理中）:
```json
{
  "prediction": ""
}
```

- `prediction`: ResNet50 による非同期推論結果（空文字列なら処理中）

---

## 🎓 学習ポイント

### 1. なぜProcessPoolExecutor？

```
速いモデル: 50ms
遅いモデル: 500ms

→ 遅いモデルは裏で処理
→ 重い推論 = CPU集約的
→ ProcessPoolExecutor が最適！
```

### 2. なぜBackgroundTasks？

```
同期推論: すぐ返す必要がある
非同期推論: 裏で処理してOK

→ BackgroundTasks で即座にレスポンス
→ UX向上！
```

### 3. ThreadPoolExecutor との違い

| | ThreadPool | ProcessPool |
|---|-----------|-------------|
| **並列性** | GILで制限 | 真の並列 ⭐ |
| **CPU使用率** | 低い | 高い |
| **推論速度** | 遅い | 速い |

---

## 💡 実装のポイント

### Proxy側（src/proxy/app.py）

```python
from fastapi import FastAPI, BackgroundTasks
from src.ml.predictor import ONNXPredictor

# 同期推論用（MobileNet v2）
sync_predictor = ONNXPredictor("models/mobilenet_v2.onnx")

@app.post("/predict")
async def predict(request: PredictRequest, background_tasks: BackgroundTasks):
    # 1. ジョブID生成
    job_id = str(uuid.uuid4())

    # 2. 同期推論（MobileNet v2 - 即座に実行）
    result_sync = sync_predictor.predict_from_base64(request.image_data)

    # 3. 非同期ジョブをキューに登録（BackgroundTasks）
    background_tasks.add_task(enqueue_job, job_id, request.image_data)

    # 4. 即座に返す！
    return PredictResponse(
        job_id=job_id,
        result_sync=result_sync  # MobileNet v2の結果
    )

def enqueue_job(job_id: str, image_data: str):
    """ジョブをRedisキューに登録"""
    job_data = {"image_data": image_data, "status": "pending"}
    redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
    redis_client.rpush("queue:jobs", job_id)
```

### Worker側（src/worker/worker.py）

```python
from src.ml.predictor import ONNXPredictor

# 非同期推論用（ResNet50）
async_predictor = ONNXPredictor("models/resnet50.onnx")

def process_job(job_id: str, redis_client: Redis):
    """ジョブを処理"""
    # 1. Redisからジョブデータを取得
    job_data = json.loads(redis_client.get(f"job:{job_id}"))
    image_data = job_data["image_data"]

    # 2. 推論実行（ResNet50 - 高精度だが重い）
    result = async_predictor.predict_from_base64(image_data)

    # 3. 結果をRedisに保存
    job_data["status"] = "completed"
    job_data["result"] = result
    redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))

    return result

def run_worker(redis_client: Redis):
    """Workerのメインループ"""
    while True:
        # キューからジョブを取得（ブロッキング）
        job = redis_client.blpop("queue:jobs", timeout=1)
        if job:
            _, job_id = job
            process_job(job_id, redis_client)
```

---

## ✅ テスト結果

### TDD サイクル完了

```
1. ✅ Predictor:  Red → Green (3/3 tests)
2. ✅ Proxy API:  Red → Green (5/5 tests)
3. ✅ Worker:     Red → Green (3/3 tests)
4. ✅ 統合:       All Green (11/11 tests)
```

### テスト詳細

| コンポーネント | テスト数 | 成功 | 内容 |
|------------|---------|------|------|
| **Predictor** | 3 | ✅ 3 | ONNX推論、前処理、Base64サポート |
| **Proxy API** | 5 | ✅ 5 | 同期推論、ジョブ登録、結果取得 |
| **Worker** | 3 | ✅ 3 | 非同期推論、エラーハンドリング |
| **合計** | **11** | **✅ 11** | **実行時間: 2.76秒** |

### テスト環境

- **FakeRedis**: 外部依存なしでテスト実行
- **Monkeypatch**: Proxy の Redis クライアントを置き換え
- **TestClient**: FastAPI のテストクライアント

詳細: `tests/test_results/all_tests_green.txt`

---

## 📁 ディレクトリ構成

```
07_sync_async_pattern/
├── SPECIFICATION.md          # 詳細仕様
├── README.md                 # このファイル
├── docker-compose.yml        # 3サービス構成（Proxy, Worker, Redis）
├── Dockerfile.proxy          # Proxyイメージ
├── Dockerfile.worker         # Workerイメージ
├── requirements.txt          # Python依存関係
├── test_e2e.sh               # E2Eテストスクリプト ⭐
├── models/                   # ONNXモデル
│   ├── mobilenet_v2.onnx     # 同期推論用（14MB）
│   └── resnet50.onnx         # 非同期推論用（98MB）
├── src/
│   ├── configurations.py     # 環境変数管理
│   ├── models.py             # Pydanticモデル
│   ├── proxy/                # Proxyサービス
│   │   └── app.py            # FastAPI + BackgroundTasks
│   ├── worker/               # Workerサービス
│   │   └── worker.py         # Redis Queue処理
│   └── ml/                   # 推論ロジック
│       ├── predictor.py      # ONNX Runtime推論
│       └── labels.py         # ImageNetラベル
└── tests/                    # テストコード
    ├── test_predictor.py     # Predictorテスト（3 tests）
    ├── test_proxy.py         # Proxy APIテスト（5 tests）
    ├── test_worker.py        # Workerテスト（3 tests）
    └── test_results/         # テスト結果（コメント付き）
        ├── proxy_red.txt     # Proxy Red Phase
        ├── proxy_green.txt   # Proxy Green Phase
        ├── worker_red.txt    # Worker Red Phase
        ├── worker_green.txt  # Worker Green Phase
        └── all_tests_green.txt  # 統合テスト結果
```

---

## 📖 詳細ドキュメント

- **仕様書**: [SPECIFICATION.md](./SPECIFICATION.md) - 要件定義、API仕様、データモデル
- **プロセス vs スレッド**: [04_notes/12_process_vs_thread.md](../../../04_notes/12_process_vs_thread.md)
- **並行 vs 並列**: [04_notes/11_concurrency_vs_parallelism.md](../../../04_notes/11_concurrency_vs_parallelism.md)
- **ONNX推論**: [04_notes/06_onnx_inference_patterns.md](../../../04_notes/06_onnx_inference_patterns.md)

---

**実装日**: 2025-11-14
**パターン**: Sync-Async Pattern (Chapter 4)
