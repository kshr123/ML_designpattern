# Batch Pattern - ソースコード全体概要

## 📚 このディレクトリについて

このディレクトリには、**Batch Pattern（バッチ推論パターン）** の実装コードが含まれています。

Batch Patternは、**リアルタイム推論の代わりに定期的にまとめて処理**するデザインパターンです：

- **API Service**: データ登録と結果取得のみ（推論はしない）
- **Batch Job Service**: 60秒ごとに未推論データをまとめて処理
- **MySQL Database**: データと推論結果を永続化

## 🏗️ アーキテクチャ全体図

```
┌─────────────────────────────────────────────────────────────┐
│                        ユーザー                              │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Request
                         │ POST /predict (データ登録)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  API Service (このディレクトリのapi/)                        │
│  ┌──────────┐   ┌──────────┐                               │
│  │   app    │ → │    db    │                               │
│  │ FastAPI  │   │  CRUD    │                               │
│  │ ルーター │   │  操作    │                               │
│  └──────────┘   └────┬─────┘                               │
│                      │ INSERT (データ登録のみ、推論なし)    │
└──────────────────────┼─────────────────────────────────────┘
                       ↓
┌──────────────────────┼─────────────────────────────────────┐
│                      │                                      │
│              MySQL Database                                │
│    ┌─────────────────┴────────────────┐                   │
│    │ items テーブル                    │                   │
│    │ - id, data, created_at           │                   │
│    └─────────────┬────────────────────┘                   │
│    ┌─────────────┴────────────────────┐                   │
│    │ predictions テーブル               │                   │
│    │ - id, item_id, prediction        │                   │
│    └─────────────┬────────────────────┘                   │
└──────────────────┼─────────────────────────────────────────┘
                   │ SELECT (未推論データ取得)
                   ↓
┌─────────────────────────────────────────────────────────────┐
│  Batch Job Service (このディレクトリのtask/)                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │   job    │ → │    ml    │ → │    db    │               │
│  │60秒ループ│   │ ONNX推論 │   │  CRUD    │               │
│  │          │   │4並列処理 │   │  保存    │               │
│  └──────────┘   └──────────┘   └──────────┘               │
│                                      │ INSERT (推論結果)     │
└──────────────────────────────────────┼─────────────────────┘
                                       ↓
                                  結果をDBに保存
```

## 📁 ディレクトリ構成

```
src/
├── README.md                    # このファイル（全体概要）
│
├── api/                         # FastAPIアプリケーション
│   ├── app.py                  # FastAPIアプリ本体
│   └── routers.py              # APIエンドポイント定義
│
├── db/                          # データベース操作
│   ├── database.py             # DB接続設定
│   ├── models.py               # SQLAlchemyモデル定義
│   ├── schemas.py              # Pydanticスキーマ
│   └── cruds.py                # CRUD操作（作成・読取・更新・削除）
│
├── ml/                          # 機械学習ロジック
│   ├── predictor.py            # ONNX Runtime推論
│   └── data_loader.py          # データローダー
│
├── task/                        # バッチジョブ
│   └── job.py                  # メインバッチジョブ（60秒ループ）
│
├── configurations.py            # 環境変数の設定
└── constants.py                # 定数定義
```

## 🔄 データフロー（簡単な例）

### 例：Irisデータを推論する場合

```python
# ========================================
# フェーズ1: データ登録（即座に完了）
# ========================================

# 1. ユーザーがHTTPリクエストを送信
POST /predict
Body: {"data": [[5.1, 3.5, 1.4, 0.2]]}

# 2. api/routers.py でリクエストを受信
@router.post("/predict")
async def predict(data: Data, db: Session):
    # 推論は実行しない、DBに保存するだけ
    item_id = cruds.register_item(db, data.data)
    return {"id": item_id}  # 即座にID返却（< 50ms）

# 3. db/cruds.py でデータをDBに保存
def register_item(db: Session, data: List[List[float]]):
    item = models.Item(data=json.dumps(data))
    db.add(item)
    db.commit()
    return item.id

# ========================================
# フェーズ2: バッチ推論（60秒後）
# ========================================

# 4. task/job.py が60秒ごとに起動
def main():
    time.sleep(60)  # 待機

    # 4-1. 未推論データを取得
    items = cruds.select_without_prediction(db)

    # 4-2. ThreadPoolExecutor（4並列）で推論
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(predict_single_item, items)

    # 4-3. 推論結果をDBに保存
    for result in results:
        cruds.register_prediction(
            db,
            item_id=result["id"],
            prediction=result["prediction"]
        )

# 5. ml/predictor.py で推論実行
def predict(data: np.ndarray) -> np.ndarray:
    session = ort.InferenceSession("iris_svc.onnx")
    output = session.run(None, {"input": data})
    return output[0]  # 確率分布

# ========================================
# フェーズ3: 結果取得
# ========================================

# 6. ユーザーが結果を取得
GET /predict/id/1

# 7. api/routers.py でDBから結果を取得
@router.get("/predict/id/{id}")
async def get_prediction(id: int, db: Session):
    prediction = cruds.select_prediction_by_id(db, id)
    return {"id": id, "prediction": prediction}

# 推論完了前: {"id": 1, "prediction": null}
# 推論完了後: {"id": 1, "prediction": {"setosa": 0.97, ...}}
```

## 🚀 主要なクラスとその役割

### 1. FastAPI Application (`api/app.py`)
- **役割**: HTTPサーバーとして動作
- **やること**: データ登録と結果取得のエンドポイントを提供

### 2. APIRouter (`api/routers.py`)
- **役割**: エンドポイントの定義
- **やること**:
  - `POST /predict`: データ登録（推論はしない）
  - `GET /predict/id/{id}`: 推論結果取得

### 3. SQLAlchemyモデル (`db/models.py`)
- **役割**: データベーステーブルの定義
- **やること**:
  - `Item`: 入力データ
  - `Prediction`: 推論結果

### 4. CRUD操作 (`db/cruds.py`)
- **役割**: データベース操作
- **やること**:
  - `register_item()`: データ登録
  - `select_without_prediction()`: 未推論データ取得
  - `register_prediction()`: 推論結果保存

### 5. ONNXPredictor (`ml/predictor.py`)
- **役割**: ONNX Runtime推論
- **やること**: Irisデータ → 確率分布

### 6. BatchJob (`task/job.py`)
- **役割**: 定期バッチ推論
- **やること**:
  - 60秒待機
  - 未推論データ取得
  - ThreadPoolExecutorで4並列推論
  - 結果保存

## 🔑 重要な概念

### なぜ推論を分離するのか？

**同期推論（Web Single Pattern）の問題**:
```python
# ユーザーが推論完了まで待つ必要がある（遅い）
POST /predict → 推論実行（500ms） → レスポンス
```

**非同期推論（Batch Pattern）の利点**:
```python
# データ登録は即座に完了（速い）
POST /predict → DB保存（10ms） → レスポンス（ID返却）

# 推論はバックグラウンドで実行
60秒後 → バッチで推論 → DB保存
```

### ThreadPoolExecutorとは？

Pythonの標準ライブラリで、**並列処理**を簡単に実現できます：

```python
# 1つずつ処理（遅い）
for item in items:
    result = predict(item)  # 100ms × 100件 = 10秒

# 並列処理（速い）
with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(predict, items)  # 100ms × 100件 ÷ 4 = 2.5秒
```

### 依存関係の管理（depends_on）

docker-compose.ymlで、**サービスの起動順序を制御**します：

```yaml
job:
  depends_on:
    mysql:
      condition: service_healthy  # MySQLが健全になってから起動
```

## 🎯 バッチパターンが適している場合

**✅ 適している**:
- リアルタイム性が不要（数分〜数時間の遅延OK）
- 大量データを効率的に処理したい
- コスト削減のためにリソースを集中的に使いたい

**❌ 適していない**:
- リアルタイム推論が必要（< 1秒）
- ユーザーが即座に結果を必要とする
- データ到着時に即座に処理が必要

## 🛠️ 開発時の注意点

### データベースマイグレーション

テーブル定義を変更したら、マイグレーションが必要です：

```python
# db/models.py を変更
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    # 新しいカラムを追加
    user_id = Column(Integer)

# Alembicでマイグレーション（本実装では未使用）
# 現在は docker-compose down -v で再作成
```

### 環境変数

```yaml
environment:
  MYSQL_SERVER: mysql        # MySQLホスト名
  MYSQL_PORT: 3306          # MySQLポート
  BATCH_WAIT_TIME: 60       # バッチ実行間隔（秒）
  WORKER_THREADS: 4         # 並列スレッド数
```

## 🎯 まとめ

このBatch Patternの実装は、以下の3つの主要部分から構成されています：

1. **api/**: データ登録と結果取得（推論はしない）
2. **task/**: 定期的にバッチ推論を実行
3. **db/**: データベース操作（SQLAlchemy + MySQL）

全体として、**推論を非同期化することで、APIレスポンスが高速化し、リソースを効率的に使える**というメリットがあります。
