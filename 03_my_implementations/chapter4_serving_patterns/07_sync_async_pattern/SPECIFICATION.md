# Sync-Async Pattern 仕様書

## 📋 概要

**Sync-Async Pattern（時間差推論パターン）**: 速いモデルで即座にレスポンスを返しつつ、遅くて高精度なモデルをバックグラウンドで実行するパターン

### パターンの目的

1. **UX向上**: ユーザーを待たせない（速いモデルで即レスポンス）
2. **品質向上**: 高精度な結果も提供（遅いモデルを裏で実行）
3. **柔軟性**: ユーザーが必要に応じて高精度結果を取得

---

## 🎯 要件定義

### 機能要件

#### 1. 同期推論（Sync）
- **速いモデル**: MobileNet v2（ONNX）
- **推論時間**: < 100ms
- **レスポンス**: 即座に返却

#### 2. 非同期推論（Async）
- **遅いモデル**: ResNet50（ONNX）
- **推論時間**: 500ms〜1秒
- **実行方式**: バックグラウンド処理

#### 3. ジョブ管理
- **ジョブID発行**: UUID（6文字）
- **キュー**: Redis List（LPUSH/RPOP）
- **結果保存**: Redis（TTL: 1時間）

### 非機能要件

#### 1. パフォーマンス
- **同期推論レスポンス**: < 200ms
- **Worker並列度**: 2プロセス
- **スループット**: 10 req/sec

#### 2. スケーラビリティ
- **Workerプロセス**: 環境変数で調整可能
- **Redis**: 水平スケール可能

#### 3. 可用性
- **Workerクラッシュ**: 自動再起動
- **Redis接続**: リトライ機能

---

## 🏗️ システムアーキテクチャ

### 全体構成

```
┌─────────────────────────────────────────────────┐
│              Docker Network                      │
│                                                  │
│  ┌──────────────┐                                │
│  │    Proxy     │                                │
│  │  (FastAPI)   │                                │
│  │  Port: 8000  │                                │
│  └──────┬───────┘                                │
│         │                                         │
│    ┌────┴─────┬───────────────┐                 │
│    │          │               │                  │
│    ▼          ▼               ▼                  │
│  ┌────┐   ┌──────┐      ┌─────────┐            │
│  │ONNX│   │Redis │      │ Worker  │            │
│  │    │   │Queue │      │(Process │            │
│  │Sync│   │      │      │ Pool)   │            │
│  └────┘   └──┬───┘      └────┬────┘            │
│              │               │                   │
│              └───────────────┘                   │
│                      │                            │
│                      ▼                            │
│                 ┌──────────┐                     │
│                 │  ONNX    │                     │
│                 │  Async   │                     │
│                 └──────────┘                     │
└─────────────────────────────────────────────────┘
```

### コンポーネント

#### 1. Proxy（FastAPI）
- **役割**: リクエスト受付、同期推論、ジョブ登録
- **エンドポイント**:
  - `GET /health`: ヘルスチェック
  - `GET /metadata`: メタデータ取得
  - `POST /predict`: 推論リクエスト
  - `GET /job/{job_id}`: 結果取得
- **技術**: FastAPI, BackgroundTasks, httpx, ONNX Runtime

#### 2. Worker（Backend）
- **役割**: キュー監視、非同期推論、結果保存
- **並列度**: 2プロセス（ProcessPoolExecutor）
- **技術**: ProcessPoolExecutor, ONNX Runtime, Redis

#### 3. Redis
- **役割**: キュー、結果ストア
- **データ構造**:
  - `queue:jobs`: List（ジョブID）
  - `image:{job_id}`: String（Base64画像）
  - `result:{job_id}`: String（予測結果、TTL: 3600秒）

---

## 📊 データフロー

### 1. 推論リクエスト

```
[ユーザー]
    ↓ POST /predict
    ↓ {"image_data": "base64..."}
    ↓
[Proxy]
    ├→ 1. job_id生成（UUID 6文字）
    ├→ 2. Base64デコード
    ├→ 3. 同期推論（MobileNet v2）── 50ms
    │   → 結果をレスポンスに含める
    ├→ 4. BackgroundTaskで非同期ジョブ登録
    │   ├→ image:{job_id}をRedisに保存
    │   └→ job_idをキューにLPUSH
    └→ 5. 即座にレスポンス返却
        {"job_id": "a1b2c3", "result_sync": "Persian cat"}

[Worker]
    ├→ 6. RPOPでキューからjob_id取得（ブロック待機）
    ├→ 7. image:{job_id}をRedisから取得
    ├→ 8. 非同期推論（ResNet50）── 500ms
    └→ 9. result:{job_id}に結果保存（TTL: 3600秒）

[ユーザー]
    ↓ GET /job/a1b2c3
    ↓
[Proxy]
    ├→ 10. result:{job_id}をRedisから取得
    └→ 11. レスポンス返却
         {"a1b2c3": {"prediction": "Siamese cat"}}
```

---

## 🔌 API仕様

### 1. ヘルスチェック

**エンドポイント**: `GET /health`

**レスポンス**:
```json
{
  "health": "ok"
}
```

---

### 2. メタデータ取得

**エンドポイント**: `GET /metadata`

**レスポンス**:
```json
{
  "data_type": "str",
  "data_structure": "(1,1)",
  "data_sample": "base64 encoded image file",
  "prediction_type": "str",
  "prediction_structure": "(1,1)",
  "prediction_sample": "Persian cat"
}
```

---

### 3. 推論リクエスト

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
  "job_id": "a1b2c3",
  "result_sync": "Persian cat"
}
```

**ステータスコード**:
- `200 OK`: 成功
- `400 Bad Request`: 不正なリクエスト
- `500 Internal Server Error`: サーバーエラー

---

### 4. テスト推論

**エンドポイント**: `GET /predict/test`

**レスポンス**:
```json
{
  "job_id": "x9y8z7",
  "result_sync": "Persian cat"
}
```

---

### 5. 結果取得

**エンドポイント**: `GET /job/{job_id}`

**レスポンス**（完了時）:
```json
{
  "a1b2c3": {
    "prediction": "Siamese cat"
  }
}
```

**レスポンス**（処理中）:
```json
{
  "a1b2c3": {
    "prediction": ""
  }
}
```

**ステータスコード**:
- `200 OK`: 成功（処理中でも200）
- `404 Not Found`: job_idが存在しない

---

## 🤖 モデル仕様

### 同期モデル（MobileNet v2）

- **モデル**: MobileNet v2（ONNX）
- **入力**: `(1, 3, 224, 224)` - RGB画像
- **出力**: `(1, 1000)` - ImageNet 1000クラス
- **前処理**:
  1. リサイズ: 224x224
  2. 正規化: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
  3. チャンネル順序: RGB → BGR（不要、MobileNet v2はRGB）
  4. 次元追加: (3, 224, 224) → (1, 3, 224, 224)

### 非同期モデル（ResNet50）

- **モデル**: ResNet50（ONNX）
- **入力**: `(1, 3, 224, 224)` - RGB画像
- **出力**: `(1, 1000)` - ImageNet 1000クラス
- **前処理**: MobileNet v2と同じ

---

## 🗄️ データストア仕様

### Redis

#### キー設計

| キー | 型 | 説明 | TTL |
|------|-----|------|-----|
| `queue:jobs` | List | ジョブIDのキュー | なし |
| `image:{job_id}` | String | Base64画像データ | 3600秒 |
| `result:{job_id}` | String | 予測結果（ラベル名） | 3600秒 |

#### コマンド

```bash
# ジョブ登録
LPUSH queue:jobs "a1b2c3"
SET image:a1b2c3 "iVBORw0..." EX 3600

# ジョブ取得
RPOP queue:jobs

# 結果保存
SET result:a1b2c3 "Siamese cat" EX 3600

# 結果取得
GET result:a1b2c3
```

---

## 🔧 環境変数

### Proxy

| 変数名 | デフォルト | 説明 |
|--------|-----------|------|
| `PORT` | `8000` | APIポート |
| `REDIS_HOST` | `redis` | Redisホスト |
| `REDIS_PORT` | `6379` | Redisポート |
| `SYNC_MODEL_PATH` | `/models/mobilenet_v2.onnx` | 同期モデルパス |
| `QUEUE_NAME` | `queue:jobs` | ジョブキュー名 |

### Worker

| 変数名 | デフォルト | 説明 |
|--------|-----------|------|
| `REDIS_HOST` | `redis` | Redisホスト |
| `REDIS_PORT` | `6379` | Redisポート |
| `ASYNC_MODEL_PATH` | `/models/resnet50.onnx` | 非同期モデルパス |
| `NUM_WORKERS` | `2` | Workerプロセス数 |
| `QUEUE_NAME` | `queue:jobs` | ジョブキュー名 |

---

## 🐳 Docker構成

### サービス構成

```yaml
services:
  proxy:
    - FastAPI + MobileNet v2
    - Port: 8000

  worker:
    - ProcessPoolExecutor + ResNet50
    - プロセス数: 2

  redis:
    - Version: 7
    - Port: 6379
```

---

## 🧪 テスト要件

### 1. ユニットテスト

- **Proxy**:
  - 同期推論のロジック
  - ジョブID生成
  - Redis操作

- **Worker**:
  - 非同期推論のロジック
  - キュー監視
  - エラーハンドリング

### 2. 統合テスト

- **エンドツーエンド**:
  1. POST /predict
  2. job_id取得
  3. GET /job/{job_id}でポーリング
  4. 結果確認

### 3. パフォーマンステスト

- **同期推論**: < 200ms
- **非同期推論**: 完了まで < 2秒

---

## 📈 監視・ログ

### メトリクス

- **Proxy**:
  - リクエスト数
  - レスポンスタイム（同期推論）
  - エラー率

- **Worker**:
  - 処理済みジョブ数
  - 推論時間（非同期）
  - キュー長

### ログ

```python
# Proxy
logger.info(f"POST /predict - job_id: {job_id}")
logger.info(f"Sync prediction: {result}")

# Worker
logger.info(f"Processing job: {job_id}")
logger.info(f"Async prediction: {result}")
```

---

## 🚀 デプロイ

### 起動手順

```bash
# 1. ディレクトリ移動
cd 07_sync_async_pattern

# 2. Docker Composeで起動
docker compose up -d

# 3. 動作確認
curl http://localhost:8000/health

# 4. テスト推論
curl http://localhost:8000/predict/test
```

### 停止手順

```bash
docker compose down
```

---

## 🎯 成功基準

- [ ] 同期推論が200ms以内で返る
- [ ] 非同期推論が裏で正常に動作
- [ ] 2プロセスのWorkerが並列実行
- [ ] Redisキューが正常に動作
- [ ] エラーハンドリングが適切
- [ ] ドキュメントが完備

---

## 📚 参考資料

- **技術メモ**: [TECH_NOTES.md](./TECH_NOTES.md)
- **プロセス vs スレッド**: [04_notes/12_process_vs_thread.md](../../../04_notes/12_process_vs_thread.md)
- **並行 vs 並列**: [04_notes/11_concurrency_vs_parallelism.md](../../../04_notes/11_concurrency_vs_parallelism.md)

---

**作成日**: 2025-11-14
**パターン**: Sync-Async Pattern (Chapter 4)
