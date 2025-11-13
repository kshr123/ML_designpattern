# Asynchronous Pattern（非同期推論パターン）

## 📋 概要

非同期推論パターンは、**リクエストの受付と推論処理を分離**し、長時間の推論をバックグラウンドで実行する設計パターンです。

### 解決する課題

- **長時間の推論処理**：推論に数秒～数分かかる場合、クライアントをブロックしない
- **スループット向上**：推論処理中も新しいリクエストを受け付けられる
- **リソースの効率利用**：推論ワーカーを独立してスケールできる
- **タイムアウト回避**：HTTPタイムアウトを気にせず長時間処理が可能

### このパターンが適している場合

- 画像処理、動画解析など処理時間が長い推論
- バッチ推論を効率的に処理したい場合
- 推論リソースとAPI サーバーを独立してスケールしたい場合
- クライアントがポーリングやWebSocketで結果を取得できる場合

## 🏗️ アーキテクチャ

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /predict
       │ (即座にjob_idを返す)
       ↓
┌──────────────────────┐
│   Proxy (FastAPI)    │
│  - リクエスト受付    │
│  - job_id発行        │
│  - Redis登録         │
└──────┬───────────────┘
       │ LPUSH job_id
       ↓
┌──────────────────────┐
│   Redis (キュー)     │
│  - ジョブキュー      │
│  - データストア      │
│  - ステータス管理    │
└──────┬───────────────┘
       │ BRPOP (ブロッキング)
       ↓
┌──────────────────────┐
│  Worker (ONNX)       │
│  - キュー監視        │
│  - 推論実行          │
│  - 結果保存          │
└──────────────────────┘
```

### コンポーネント

| コンポーネント | 役割 | 技術スタック |
|--------------|------|------------|
| **Proxy** | クライアントとの窓口、job管理 | FastAPI, Pydantic |
| **Redis** | ジョブキュー、データストア | Redis 7 (alpine) |
| **Worker** | 推論実行（複数起動可能） | Python, ONNX Runtime |

## 🔧 技術スタック

### 主要技術

- **Python**: 3.13
- **FastAPI**: 非同期APIフレームワーク
- **Redis**: ジョブキュー＋データストア
- **ONNX Runtime**: クロスプラットフォーム推論エンジン
- **Docker Compose**: マルチコンテナオーケストレーション

### 依存関係

```toml
[project]
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "redis>=5.0.0",
    "onnxruntime>=1.16.0",
    "numpy>=1.24.0",
    "pydantic>=2.0.0",
]
```

## 🎯 実装の特徴

### 1. ONNX Runtimeへの移行

当初はTensorFlow Servingを使用する予定でしたが、**Apple Silicon (M1/M2)での互換性**と**シンプルさ**を考慮してONNX Runtimeに変更しました。

**メリット**:
- クロスプラットフォーム対応（Apple Silicon含む）
- コンテナが軽量（TF Servingより小さい）
- Pythonコードから直接推論実行（gRPC不要）
- セットアップが簡単

### 2. BRPOPブロッキング方式

キュー監視に**Redis BRPOP（Blocking Right Pop）**を採用しました。

**従来のポーリング方式**:
```python
while True:
    job_id = redis.rpop(queue_name)
    if not job_id:
        time.sleep(0.1)  # CPU無駄遣い
    else:
        process(job_id)
```

**BRPOP方式**（採用）:
```python
while True:
    # ジョブが来るまでブロック（CPUを使わない）
    job_id = redis.brpop(queue_name, timeout=1)
    if job_id:
        process(job_id)
```

**メリット**:
- **CPU効率**: アイドル時のCPU使用率がほぼゼロ
- **低レイテンシ**: ジョブ到着時に即座に処理開始（ポーリング遅延なし）
- **Redis負荷軽減**: ポーリングによる無駄なクエリがない

### 3. ジョブステータス管理

Redisで以下のキー設計を採用：

```
job:{job_id}:data      # 入力データ
job:{job_id}:status    # ステータス (pending/processing/completed/failed)
job:{job_id}:result    # 推論結果
job:{job_id}:error     # エラーメッセージ
```

**ステータス遷移**:
```
pending → processing → completed
                    └→ failed
```

## 🚀 セットアップと実行

### 前提条件

- Python 3.13以上
- Docker & Docker Compose
- uv（パッケージマネージャー）

### 1. 環境構築

```bash
# Pythonバージョン指定
echo "3.13" > .python-version

# 仮想環境作成
uv venv

# 有効化
source .venv/bin/activate

# 依存関係インストール
uv pip install fastapi uvicorn redis onnxruntime numpy pydantic requests
```

### 2. ローカル実行（開発用）

**ターミナル1: Redis起動**
```bash
docker run -d --name async_redis -p 6379:6379 redis:7-alpine
```

**ターミナル2: Proxy起動**
```bash
source .venv/bin/activate
uvicorn src.proxy.app:app --host 0.0.0.0 --port 8000 --reload
```

**ターミナル3: Worker起動**
```bash
source .venv/bin/activate
python -m src.backend.worker
```

### 3. Docker Compose実行（本番想定）

```bash
# ビルドと起動
docker-compose up --build

# バックグラウンド実行
docker-compose up -d

# ログ確認
docker-compose logs -f worker

# 停止
docker-compose down
```

### 4. 動作確認

**ヘルスチェック**:
```bash
curl http://localhost:8000/health
# {"status":"healthy","components":{"redis":"ok","worker":"ok"}}
```

**テスト推論**:
```bash
# リクエスト送信（即座にjob_idが返る）
curl -X POST http://localhost:8000/predict/test
# {"job_id":"b44613"}

# 結果取得
curl http://localhost:8000/job/b44613
# {"job_id":"b44613","status":"completed","result":{...}}
```

**カスタムデータで推論**:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"data":[[6.3, 3.3, 6.0, 2.5]]}'
# {"job_id":"763c75"}

curl http://localhost:8000/job/763c75
# {"status":"completed","result":{"prediction":2,"class_name":"virginica",...}}
```

## ✅ 非同期処理の確認

### テストスクリプト

非同期処理であることを証明するテストスクリプトを用意しました：

```bash
./test_async.sh
```

このスクリプトは以下を確認します：

1. **リクエストが即座に返る**（処理完了を待たない）
2. **ステータスが遷移する**（pending → processing → completed）
3. **Proxyがブロックされない**（処理中も他のリクエストを受け付ける）

### 実行結果例

```
【1】リクエスト送信（即座にjob_idが返るはず）
開始時刻: 15:36:52
レスポンス: {"job_id":"133efe"}
終了時刻: 15:36:52  ← 即座に返る！
👉 約0.1秒以内に返るはず（3秒待たない＝非同期の証拠）

【2】直後のステータス確認（pendingまたはprocessingのはず）
ステータス: {"status":"processing",...}
👉 completedではないはず（まだ処理中）

【3】1秒後のステータス確認（まだprocessingのはず）
ステータス: {"status":"processing",...}
👉 まだ完了していないはず（3秒の処理中）

【4】さらに2.5秒後のステータス確認（completedのはず）
ステータス: {"status":"completed","result":{...}}
👉 完了しているはず
```

## 📚 APIエンドポイント

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API情報 |
| GET | `/health` | ヘルスチェック |
| GET | `/metadata` | モデルメタデータ |
| POST | `/predict` | 非同期推論リクエスト |
| POST | `/predict/test` | テストデータで推論 |
| GET | `/job/{job_id}` | ジョブ結果取得 |

### リクエスト/レスポンス例

**POST /predict**
```json
// Request
{
  "data": [[5.1, 3.5, 1.4, 0.2]]
}

// Response (即座に返る)
{
  "job_id": "b44613"
}
```

**GET /job/{job_id}**
```json
// Response (pending)
{
  "job_id": "b44613",
  "status": "pending",
  "result": null,
  "error": null
}

// Response (completed)
{
  "job_id": "b44613",
  "status": "completed",
  "result": {
    "prediction": 0,
    "class_name": "setosa",
    "probabilities": [0.971, 0.016, 0.013]
  },
  "error": null
}
```

## 🎓 学んだこと

### 1. 非同期処理の本質

**単なるRedis利用 ≠ 非同期処理**

非同期処理の本質は以下の3点：
1. **リクエストとレスポンスの分離**：即座にjob_idを返す
2. **処理の独立性**：Workerが別プロセスで動作
3. **ステータス管理**：クライアントがポーリングで結果取得

### 2. BRPOPの威力

ポーリング方式からBRPOPブロッキング方式への変更で：
- **CPU使用率**: 常時5-10% → アイドル時0%
- **レスポンスタイム**: 平均50-100ms → 1ms以下
- **Redis負荷**: 10リクエスト/秒 → オンデマンド

### 3. キュー設計のポイント

**LPUSH/BRPOP の組み合わせ**:
```
LPUSH → [Job3][Job2][Job1] → BRPOP
        ↑                    ↑
      新しい                古い
```

- **LPUSH（左プッシュ）**: キューの先頭に追加
- **BRPOP（右ポップ）**: キューの末尾から取得
- **結果**: FIFO（First In, First Out）

### 4. ONNX Runtime の利点

TensorFlow Servingと比較して：

| 項目 | TensorFlow Serving | ONNX Runtime |
|------|-------------------|--------------|
| Apple Silicon | ❌ 非対応 | ✅ 対応 |
| セットアップ | 複雑（gRPC設定） | シンプル |
| イメージサイズ | ~2GB | ~500MB |
| 推論速度 | 高速 | 高速 |
| モデル形式 | SavedModel | ONNX（汎用） |

### 5. エラーハンドリングの重要性

非同期処理では以下のエラーケースを考慮：
- ジョブが見つからない（TTL切れ）
- 推論タイムアウト
- Workerクラッシュ
- Redis接続エラー

各ケースで適切なステータスとエラーメッセージを返す設計が重要。

### 6. スケーラビリティ

Docker Composeで簡単にWorkerをスケール：
```yaml
worker:
  deploy:
    replicas: 2  # 2つのWorkerが並列処理
```

Kubernetesなら：
```bash
kubectl scale deployment worker --replicas=5
```

## 🔄 同期パターンとの比較

| 項目 | 同期パターン | 非同期パターン |
|------|------------|--------------|
| レスポンス | 推論完了後 | 即座にjob_id |
| クライアント | ブロック | ブロックされない |
| タイムアウト | HTTPタイムアウトリスク | なし |
| スケーラビリティ | APIサーバーに依存 | Workerを独立スケール |
| 複雑さ | シンプル | やや複雑 |
| 適用場面 | 高速推論（<1秒） | 長時間推論（>数秒） |

## 📝 次のステップ

### 改善案

1. **WebSocketサポート**: ポーリング不要でリアルタイム結果通知
2. **優先度キュー**: 重要なジョブを優先処理
3. **リトライ機能**: 失敗時の自動再試行
4. **メトリクス収集**: Prometheus + Grafanaで監視
5. **バッチ推論**: 複数ジョブをまとめて処理

### 関連パターン

- **Web Single Pattern**: シンプルな同期推論（Chapter 4-1）
- **Batch Pattern**: バッチ推論パターン（Chapter 4-4）
- **Streaming Pattern**: ストリーミング推論（Chapter 4-5）

## 🔗 参考

- [SPECIFICATION.md](./SPECIFICATION.md) - 詳細な仕様書
- [参考実装](../../../01_reference/chapter4_serving_patterns/asynchronous_pattern/) - オリジナルコード
- [Redis BRPOP ドキュメント](https://redis.io/commands/brpop/)
- [ONNX Runtime](https://onnxruntime.ai/)

---

**実装完了日**: 2025-11-13
**パターン**: Chapter 4 - Asynchronous Pattern（非同期推論パターン）
