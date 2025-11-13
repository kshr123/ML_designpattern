# Asynchronous Pattern - Iris分類 仕様書

## 1. 概要

### 1.1 目的

非同期推論パターンを実装し、重い推論処理をバックグラウンドで実行することで、クライアントの待ち時間を最小化する。

### 1.2 解決する課題

- **同期推論の制約**: クライアントが推論完了まで待機する必要がある
- **リソース効率**: 複数の推論リクエストを効率的に処理したい
- **スケーラビリティ**: 大量のリクエストに対応したい
- **ユーザー体験**: レスポンスの遅延を改善したい

### 1.3 パターンの特徴

```
同期パターン:
  Client → [待機...] → Server(推論) → Response

非同期パターン:
  Client → job_id即座に返却
           ↓
  Background Worker → 推論実行
           ↓
  Client → job_idで結果取得
```

---

## 2. 要件定義

### 2.1 機能要件

#### 必須機能

- [x] **非同期推論API**: POST /predict でjob_idを即座に返却
- [x] **結果取得API**: GET /job/{job_id} で推論結果を取得
- [x] **ヘルスチェック**: GET /health でシステム状態確認
- [x] **メタデータ取得**: GET /metadata でモデル情報取得
- [x] **バックグラウンドワーカー**: Redisキューから推論ジョブを取得・実行

#### オプション機能

- [ ] **ジョブ一覧取得**: GET /jobs ですべてのジョブ状態を確認
- [ ] **ジョブキャンセル**: DELETE /job/{job_id} でジョブを中止
- [ ] **優先度キュー**: 重要なリクエストを優先処理

### 2.2 非機能要件

| 項目 | 要件 |
|------|------|
| **レスポンスタイム** | job_id返却 < 50ms（推論実行時間は除く） |
| **スループット** | > 100 req/s（キュー登録） |
| **可用性** | 99.5%以上 |
| **スケーラビリティ** | Workerを水平スケール可能 |
| **データ保持** | 結果をRedisに24時間保持 |

---

## 3. アーキテクチャ設計

### 3.1 システム構成

```
┌─────────────────────────────────────────────────────────────┐
│  Client                                                     │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│  Proxy (FastAPI) - Port 8000                                │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  POST /predict → job_id生成 → Redisに保存          │  │
│  │  GET /job/{job_id} → Redisから結果取得             │  │
│  └──────────────────────────────────────────────────────┘  │
└───────┬──────────────────────────────────────────┬──────────┘
        │                                          │
        ▼                                          │
┌────────────────┐                                 │
│  Redis         │◄────────────────────────────────┘
│  - Queue       │                                 ▼
│  - Job Store   │◄─────┐              ┌────────────────────┐
│  - Result Cache│      │              │ Backend Worker(s)  │
└────────────────┘      │              │                    │
                        │              │  ┌──────────────┐  │
                        │              │  │ Queue Poller │  │
                        │              │  └──────┬───────┘  │
                        │              │         │          │
                        │              │         ▼          │
                        │              │  ┌──────────────┐  │
                        │              │  │ gRPC Client  │  │
                        └──────────────┤  └──────┬───────┘  │
                                       └─────────┼──────────┘
                                                 │ gRPC
                                                 ▼
                                       ┌─────────────────────┐
                                       │ TensorFlow Serving  │
                                       │  - gRPC: 8500       │
                                       │  - REST: 8501       │
                                       │                     │
                                       │  ┌───────────────┐  │
                                       │  │ Iris Model    │  │
                                       │  │ SavedModel    │  │
                                       │  └───────────────┘  │
                                       └─────────────────────┘
```

### 3.2 コンポーネント設計

#### Proxy (FastAPI)

**役割:**
- クライアントからのリクエスト受付
- job_id生成
- Redisへのジョブ登録
- 結果の返却

**主要機能:**
```python
POST /predict
  → job_id = uuid4()[:6]
  → Redis: SET job:{job_id}:data {input_data}
  → Redis: LPUSH queue:predict job_id
  → return {"job_id": job_id}

GET /job/{job_id}
  → Redis: GET job:{job_id}:result
  → return {"job_id": job_id, "result": result}
```

#### Backend Worker

**役割:**
- Redisキューの監視
- 推論ジョブの実行
- 結果のRedis保存

**主要処理:**
```python
while True:
    job_id = Redis.RPOP("queue:predict")
    if job_id:
        data = Redis.GET(f"job:{job_id}:data")
        result = tensorflow_serving.predict(data)
        Redis.SET(f"job:{job_id}:result", result)
        Redis.EXPIRE(f"job:{job_id}:result", 86400)  # 24時間
    time.sleep(0.1)
```

#### Redis

**役割:**
- タスクキューの管理
- ジョブデータの一時保存
- 推論結果のキャッシュ

**キー設計:**
```
queue:predict              # List: 推論ジョブのキュー
job:{job_id}:data          # String: 入力データ (JSON)
job:{job_id}:result        # String: 推論結果 (JSON)
job:{job_id}:status        # String: ジョブ状態 (pending/processing/completed/failed)
```

#### TensorFlow Serving

**役割:**
- Irisモデルのホスティング
- gRPC推論API提供

**再利用:**
- Synchronous Patternで作成したSavedModelを使用

### 3.3 技術スタック

| コンポーネント | 技術 | バージョン |
|--------------|------|-----------|
| **Proxy** | FastAPI | 0.111+ |
| | Uvicorn | 0.30+ |
| | Pydantic | 2.7+ |
| **Worker** | Python | 3.11 |
| | gRPC | 1.60+ |
| | TensorFlow Serving API | 2.15+ |
| **Queue/Cache** | Redis | 7.0+ |
| **ML Serving** | TensorFlow Serving | 2.15+ |
| **Orchestration** | Docker Compose | 3.8+ |

---

## 4. API仕様

### 4.1 エンドポイント一覧

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | ヘルスチェック |
| GET | /metadata | モデルメタデータ取得 |
| POST | /predict | 非同期推論リクエスト |
| POST | /predict/test | テストデータで推論 |
| GET | /job/{job_id} | 推論結果取得 |

### 4.2 POST /predict

**リクエスト:**
```json
{
  "data": [[5.1, 3.5, 1.4, 0.2]]
}
```

**レスポンス（即座）:**
```json
{
  "job_id": "a1b2c3"
}
```

### 4.3 GET /job/{job_id}

**リクエスト:**
```
GET /job/a1b2c3
```

**レスポンス（処理中）:**
```json
{
  "job_id": "a1b2c3",
  "status": "processing"
}
```

**レスポンス（完了）:**
```json
{
  "job_id": "a1b2c3",
  "status": "completed",
  "result": {
    "prediction": 0,
    "class_name": "setosa",
    "probabilities": [0.97, 0.02, 0.01]
  }
}
```

**レスポンス（失敗）:**
```json
{
  "job_id": "a1b2c3",
  "status": "failed",
  "error": "Model inference timeout"
}
```

### 4.4 GET /health

**レスポンス:**
```json
{
  "status": "healthy",
  "components": {
    "redis": "ok",
    "tensorflow_serving": "ok"
  }
}
```

### 4.5 GET /metadata

**レスポンス:**
```json
{
  "model_spec": {
    "name": "iris",
    "version": "1"
  },
  "metadata": {
    "signature_def": {
      "serving_default": {
        "inputs": {
          "input": {
            "dtype": "DT_FLOAT",
            "tensor_shape": {"dim": [{"size": "-1"}, {"size": "4"}]}
          }
        },
        "outputs": {
          "output": {
            "dtype": "DT_FLOAT",
            "tensor_shape": {"dim": [{"size": "-1"}, {"size": "3"}]}
          }
        }
      }
    }
  }
}
```

---

## 5. データモデル

### 5.1 PredictRequest

```python
class PredictRequest(BaseModel):
    """推論リクエスト"""
    data: List[List[float]]

    class Config:
        json_schema_extra = {
            "example": {
                "data": [[5.1, 3.5, 1.4, 0.2]]
            }
        }
```

### 5.2 PredictResponse

```python
class PredictResponse(BaseModel):
    """推論レスポンス（job_id）"""
    job_id: str
```

### 5.3 JobResult

```python
class JobResult(BaseModel):
    """ジョブ結果"""
    job_id: str
    status: str  # pending, processing, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

---

## 6. データフロー

### 6.1 推論リクエストフロー

```
1. Client sends POST /predict
   ↓
2. Proxy generates job_id (uuid4()[:6])
   ↓
3. Proxy stores to Redis:
   - SET job:{job_id}:data {input_data}
   - SET job:{job_id}:status "pending"
   - LPUSH queue:predict job_id
   ↓
4. Proxy returns {"job_id": "a1b2c3"} immediately (< 50ms)
   ↓
5. Client receives job_id and can continue other tasks
```

### 6.2 バックグラウンド処理フロー

```
1. Worker polls Redis queue:
   job_id = RPOP queue:predict
   ↓
2. Worker retrieves data:
   data = GET job:{job_id}:data
   ↓
3. Worker updates status:
   SET job:{job_id}:status "processing"
   ↓
4. Worker calls TensorFlow Serving (gRPC):
   result = tf_serving.predict(data)
   ↓
5. Worker stores result:
   SET job:{job_id}:result {result}
   SET job:{job_id}:status "completed"
   EXPIRE job:{job_id}:result 86400
   ↓
6. Loop back to step 1
```

### 6.3 結果取得フロー

```
1. Client sends GET /job/{job_id}
   ↓
2. Proxy retrieves from Redis:
   status = GET job:{job_id}:status
   result = GET job:{job_id}:result
   ↓
3. Proxy returns:
   {"job_id": "a1b2c3", "status": "completed", "result": {...}}
```

---

## 7. エラーハンドリング

### 7.1 エラーケース

| エラー | HTTPステータス | 対応 |
|-------|--------------|------|
| **無効な入力データ** | 422 | バリデーションエラーを返す |
| **job_idが存在しない** | 404 | "Job not found" |
| **Redis接続エラー** | 503 | "Service temporarily unavailable" |
| **TF Serving接続エラー** | 503 | ジョブを再キュー |
| **推論タイムアウト** | 500 | statusを"failed"に更新 |

### 7.2 リトライポリシー

- **Workerの推論失敗**: 3回までリトライ、その後failed状態
- **Redis接続エラー**: 指数バックオフで再接続
- **TF Serving接続エラー**: ジョブをキューの先頭に戻す

---

## 8. パフォーマンス要件

### 8.1 レスポンスタイム

| API | 目標 | 最大許容 |
|-----|------|---------|
| POST /predict | < 20ms | 50ms |
| GET /job/{job_id} | < 10ms | 30ms |
| GET /health | < 5ms | 10ms |

### 8.2 スループット

- **Proxy**: > 100 req/s（キュー登録）
- **Worker**: 10-20 predictions/s（1 worker）
- **スケーリング**: Workerを増やせば線形にスケール

### 8.3 リソース使用量

| コンポーネント | CPU | Memory | Disk |
|--------------|-----|--------|------|
| Proxy | 0.5 core | 256MB | - |
| Worker | 1.0 core | 512MB | - |
| Redis | 0.2 core | 128MB | 1GB |
| TF Serving | 1.0 core | 1GB | 100MB |

---

## 9. セキュリティ

### 9.1 認証・認可

- **API Key**: （オプション）`X-API-Key` ヘッダーで認証
- **Rate Limiting**: IP単位で 100 req/min

### 9.2 入力検証

```python
# 入力データのバリデーション
- 4つの特徴量（sepal_length, sepal_width, petal_length, petal_width）
- すべて正の浮動小数点数
- 範囲チェック: 0.0 < value < 10.0
```

### 9.3 データ保護

- **Redis**: パスワード認証
- **TLS**: （本番環境）すべての通信をTLS化
- **機密データ**: 24時間後に自動削除（Redis EXPIRE）

---

## 10. モニタリング

### 10.1 メトリクス

```python
# Proxy metrics
- request_count: リクエスト数
- request_duration: レスポンスタイム
- error_rate: エラー率

# Worker metrics
- jobs_processed: 処理したジョブ数
- queue_length: キューの長さ
- processing_time: 平均処理時間

# Redis metrics
- memory_usage: メモリ使用量
- key_count: キー数
- expired_keys: 期限切れキー数
```

### 10.2 ログ

```python
# 構造化ログ（JSON）
{
  "timestamp": "2025-11-13T15:00:00Z",
  "level": "INFO",
  "component": "worker",
  "job_id": "a1b2c3",
  "action": "prediction_completed",
  "duration_ms": 125,
  "result": "setosa"
}
```

---

## 11. テスト計画

### 11.1 ユニットテスト

- [ ] Proxy APIエンドポイント
- [ ] Redis操作（キュー、データ取得・保存）
- [ ] Worker推論処理
- [ ] エラーハンドリング

### 11.2 統合テスト

- [ ] Proxy → Redis → Worker → TF Serving の完全フロー
- [ ] 複数ジョブの並行処理
- [ ] Redis障害時の挙動

### 11.3 E2Eテスト

- [ ] クライアント → POST /predict → GET /job/{job_id} → 結果確認
- [ ] 負荷テスト（100 req/s）

---

## 12. デプロイメント

### 12.1 Docker Compose構成

```yaml
services:
  proxy:
    build: ./proxy
    ports:
      - "8000:8000"
    depends_on:
      - redis

  worker:
    build: ./worker
    depends_on:
      - redis
      - tensorflow_serving
    deploy:
      replicas: 2  # 2つのワーカー

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  tensorflow_serving:
    image: tensorflow/serving:latest
    ports:
      - "8500:8500"
      - "8501:8501"
    volumes:
      - ../02_synchronous_pattern/saved_model/iris:/models/iris
```

### 12.2 環境変数

```bash
# Proxy
REDIS_HOST=redis
REDIS_PORT=6379
QUEUE_NAME=predict_queue

# Worker
REDIS_HOST=redis
TF_SERVING_HOST=tensorflow_serving
TF_SERVING_GRPC_PORT=8500
MODEL_NAME=iris
NUM_WORKERS=2
```

---

## 13. 成功基準

### 13.1 機能要件

- [x] POST /predict でjob_idを即座に返却（< 50ms）
- [x] GET /job/{job_id} で結果を取得できる
- [x] バックグラウンドで推論が実行される
- [x] 複数ジョブを並行処理できる
- [x] Redis経由でデータが正しく受け渡される

### 13.2 非機能要件

- [x] Proxy レスポンスタイム < 50ms
- [x] スループット > 100 req/s
- [x] Workerを複数起動してスケールできる
- [x] 推論精度 > 95%（Irisモデル）

### 13.3 テスト

- [x] 全ユニットテスト成功
- [x] 全統合テスト成功
- [x] E2Eテストで正常系・異常系を確認

---

## 14. Synchronous Pattern との比較

| 項目 | Synchronous | Asynchronous |
|------|------------|-------------|
| **レスポンス** | 推論結果を即座に返す | job_idを即座に返す |
| **待ち時間** | 推論完了まで待つ | 待たない |
| **アーキテクチャ** | Client ↔ Server | Client ↔ Proxy ↔ Worker |
| **コンポーネント数** | 1 (TF Serving) | 4 (Proxy, Worker, Redis, TF Serving) |
| **スケーリング** | TF Servingのみ | Worker を水平スケール |
| **複雑さ** | シンプル | 複雑（キュー管理必要） |
| **ユースケース** | リアルタイム推論 | バッチ処理、重い推論 |

---

**作成日**: 2025-11-13
**バージョン**: 1.0
**パターン**: Asynchronous Pattern (Chapter 4: Serving Patterns)
