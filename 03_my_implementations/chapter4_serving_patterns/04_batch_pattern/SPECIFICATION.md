# Batch Pattern（バッチ推論パターン）仕様書

## 1. 概要

### 1.1 パターンの目的

バッチ推論パターンは、**データ登録と推論処理を時間的に分離**し、一定間隔で未推論データをまとめて処理する設計パターンです。

### 1.2 解決する課題

- **リアルタイム性不要**: 推論結果が数分～数時間後でよい場合
- **リソース効率**: GPUやCPUリソースを効率的に利用したい
- **バッチ処理の最適化**: 複数データをまとめて処理することで高速化
- **システム負荷の分散**: ピークタイムを避けて処理実行

### 1.3 適用場面

- **夜間バッチ処理**: 1日1回、夜間にまとめて推論
- **定期レポート生成**: 1時間ごとに集計して推論
- **大量データ処理**: 数千～数万件のデータを効率的に処理
- **非リアルタイム分析**: 商品レコメンド、異常検知など

### 1.4 他パターンとの比較

| パターン | レスポンス | 適用場面 | 複雑さ |
|---------|-----------|---------|--------|
| **Synchronous** | 即座 | リアルタイム推論 | 低 |
| **Asynchronous** | 数秒～数分 | 長時間処理 | 中 |
| **Batch** | 数分～数時間 | 定期処理 | 中 |

---

## 2. 要件定義

### 2.1 機能要件

#### FR-1: データ登録機能
- [ ] クライアントがデータを登録できる（単一データ）
- [ ] クライアントが複数データを一括登録できる
- [ ] 登録時はデータのみ保存（推論は未実行）

#### FR-2: バッチ推論機能
- [ ] 定期的に未推論データを取得
- [ ] 複数データを並列で推論処理
- [ ] 推論結果をデータベースに保存
- [ ] 実行間隔: 60秒

#### FR-3: 結果取得機能
- [ ] 全データを取得できる
- [ ] 未推論データのみ取得できる
- [ ] 推論済みデータのみ取得できる
- [ ] ID指定でデータ取得できる

#### FR-4: モデル推論機能
- [ ] Irisデータセット（4特徴量）の3クラス分類
- [ ] ONNX形式のモデルを使用
- [ ] 確率値を返す（各クラスの確率）

### 2.2 非機能要件

#### NFR-1: パフォーマンス
- **推論スループット**: 100件/分以上
- **並列処理**: 4スレッドで並列実行
- **バッチサイズ**: 制限なし（全未推論データ）

#### NFR-2: 可用性
- **データベース**: MySQL 8.0（Apple Silicon対応、安定版）
- **障害時**: トランザクションロールバック

#### NFR-3: スケーラビリティ
- **水平スケール**: ジョブコンテナを複数起動可能
- **データ量**: 数万件まで対応

#### NFR-4: 保守性
- **ログ出力**: 処理開始・終了、エラーログ
- **環境変数**: 設定は環境変数で管理
- **コンテナ化**: Docker Composeで簡単起動

---

## 3. アーキテクチャ設計

### 3.1 システム構成

```
┌──────────────┐
│   Client     │
└──────┬───────┘
       │ HTTP (POST /data, GET /data/*)
       ↓
┌──────────────────────────┐
│   API Container          │
│   (FastAPI)              │
│   - データ登録           │
│   - 結果取得             │
│   Port: 8000             │
└──────┬───────────────────┘
       │ SQLAlchemy ORM
       ↓
┌──────────────────────────┐
│   MySQL Container        │
│   (MySQL 5.7)            │
│   - items テーブル       │
│   Port: 3306             │
└──────┬───────────────────┘
       │ SELECT WHERE prediction IS NULL
       ↓
┌──────────────────────────┐
│   Job Container          │
│   (Batch Job)            │
│   - 60秒ごとに起動       │
│   - 並列推論（4スレッド）│
│   - 結果をDBに保存       │
└──────────────────────────┘
```

### 3.2 コンポーネント設計

#### 3.2.1 データベース層（`src/db/`）

| ファイル | 責務 |
|---------|------|
| `models.py` | SQLAlchemyモデル定義（Itemテーブル） |
| `database.py` | データベース接続・セッション管理 |
| `cruds.py` | CRUD操作（登録、取得、更新） |
| `schemas.py` | Pydanticスキーマ（バリデーション） |

#### 3.2.2 API層（`src/api/`）

| ファイル | 責務 |
|---------|------|
| `routers.py` | FastAPIエンドポイント定義 |
| `app.py` | FastAPIアプリケーション初期化 |

#### 3.2.3 バッチジョブ層（`src/task/`）

| ファイル | 責務 |
|---------|------|
| `job.py` | バッチジョブのメインロジック |
| `worker.py` | 推論ワーカー（並列処理） |

#### 3.2.4 推論層（`src/ml/`）

| ファイル | 責務 |
|---------|------|
| `prediction.py` | ONNX推論クラス |

#### 3.2.5 設定層（`src/`）

| ファイル | 責務 |
|---------|------|
| `configurations.py` | 環境変数読み込み・設定管理 |
| `constants.py` | 定数定義 |

### 3.3 技術スタック

| レイヤー | 技術 | バージョン |
|---------|------|-----------|
| **言語** | Python | 3.13 |
| **データベース** | MySQL | 5.7 |
| **ORM** | SQLAlchemy | 2.0+ |
| **API** | FastAPI | 0.104+ |
| **推論** | ONNX Runtime | 1.16+ |
| **並列処理** | ThreadPoolExecutor | 標準ライブラリ |
| **コンテナ** | Docker Compose | 3.8 |
| **バリデーション** | Pydantic | 2.0+ |
| **DB接続** | PyMySQL | 1.1+ |

---

## 4. データベース設計

### 4.1 テーブル定義

#### items テーブル

| カラム名 | 型 | 制約 | 説明 |
|---------|---|------|------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | アイテムID |
| `values` | JSON | NOT NULL | 入力特徴量（4次元配列） |
| `prediction` | JSON | NULL | 推論結果（確率値） |
| `created_datetime` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 作成日時 |

**インデックス**:
- PRIMARY KEY: `id`
- INDEX: `prediction`（NULL判定用）

### 4.2 データ例

**登録直後**（推論前）:
```json
{
  "id": 1,
  "values": [5.1, 3.5, 1.4, 0.2],
  "prediction": null,
  "created_datetime": "2025-11-13 10:00:00"
}
```

**推論後**:
```json
{
  "id": 1,
  "values": [5.1, 3.5, 1.4, 0.2],
  "prediction": {
    "0": 0.971,
    "1": 0.016,
    "2": 0.013
  },
  "created_datetime": "2025-11-13 10:00:00"
}
```

### 4.3 SQL操作

**未推論データ取得**:
```sql
SELECT * FROM items WHERE prediction IS NULL;
```

**推論結果更新**:
```sql
UPDATE items SET prediction = '{"0": 0.971, "1": 0.016, "2": 0.013}' WHERE id = 1;
```

---

## 5. API仕様

### 5.1 エンドポイント一覧

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|--------------|----------|
| POST | `/data` | 単一データ登録 | `ItemBase` | `Item` |
| POST | `/data/list` | 複数データ一括登録 | `List[ItemBase]` | `List[Item]` |
| GET | `/data/all` | 全データ取得 | - | `List[Item]` |
| GET | `/data/unpredicted` | 未推論データ取得 | - | `List[Item]` |
| GET | `/data/predicted` | 推論済みデータ取得 | - | `List[Item]` |
| GET | `/data/{id}` | ID指定データ取得 | - | `Item` |
| GET | `/health` | ヘルスチェック | - | `{"status": "ok"}` |
| GET | `/metadata` | モデルメタデータ | - | `ModelMetadata` |

### 5.2 リクエスト/レスポンス形式

#### POST /data

**リクエスト**:
```json
{
  "values": [5.1, 3.5, 1.4, 0.2]
}
```

**レスポンス**:
```json
{
  "id": 1,
  "values": [5.1, 3.5, 1.4, 0.2],
  "prediction": null,
  "created_datetime": "2025-11-13T10:00:00"
}
```

#### POST /data/list

**リクエスト**:
```json
{
  "items": [
    {"values": [5.1, 3.5, 1.4, 0.2]},
    {"values": [6.3, 3.3, 6.0, 2.5]}
  ]
}
```

**レスポンス**:
```json
[
  {
    "id": 1,
    "values": [5.1, 3.5, 1.4, 0.2],
    "prediction": null,
    "created_datetime": "2025-11-13T10:00:00"
  },
  {
    "id": 2,
    "values": [6.3, 3.3, 6.0, 2.5],
    "prediction": null,
    "created_datetime": "2025-11-13T10:00:01"
  }
]
```

#### GET /data/predicted

**レスポンス**:
```json
[
  {
    "id": 1,
    "values": [5.1, 3.5, 1.4, 0.2],
    "prediction": {
      "0": 0.971,
      "1": 0.016,
      "2": 0.013
    },
    "created_datetime": "2025-11-13T10:00:00"
  }
]
```

### 5.3 エラーレスポンス

**400 Bad Request** - 無効なデータ:
```json
{
  "detail": "Invalid data format"
}
```

**404 Not Found** - データが存在しない:
```json
{
  "detail": "Item not found"
}
```

**500 Internal Server Error** - サーバーエラー:
```json
{
  "detail": "Internal server error"
}
```

---

## 6. バッチジョブ仕様

### 6.1 実行フロー

```
1. 起動時に60秒待機
   ↓
2. データベースから未推論データ取得
   ↓
3. ThreadPoolExecutor（4スレッド）で並列推論
   ↓
4. 推論結果をDictに格納
   ↓
5. データベースに一括更新（トランザクション）
   ↓
6. ログ出力（処理件数、実行時間）
   ↓
7. 終了（コンテナは1回実行で終了）
```

### 6.2 並列処理設計

**ThreadPoolExecutor**:
```python
with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(predict, data)
```

- **スレッド数**: 4（CPU効率を考慮）
- **処理単位**: アイテムごと（1アイテム = 1推論）
- **エラーハンドリング**: 各スレッドで例外キャッチ

### 6.3 トランザクション管理

```python
with get_context_db() as db:
    # 1. 未推論データ取得
    data = cruds.select_without_prediction(db=db)

    # 2. 推論処理
    predictions = {}
    for item in data:
        predictions[item.id] = predict(item.values)

    # 3. 一括更新（トランザクション）
    cruds.register_predictions(db=db, predictions=predictions, commit=True)
```

### 6.4 ログ出力

**開始ログ**:
```
INFO: waiting for batch to start (60 seconds)
```

**処理ログ**:
```
INFO: starting batch
INFO: found 10 unpredicted items
INFO: starting inference with 4 threads
```

**完了ログ**:
```
INFO: batch completed successfully
INFO: processed 10 items in 2.5 seconds
```

---

## 7. 推論仕様

### 7.1 モデル形式

- **フォーマット**: ONNX (Open Neural Network Exchange)
- **モデルファイル**: `iris_svc.onnx`
- **ラベルファイル**: `label.json`

### 7.2 入出力形式

**入力**:
- **形状**: `(1, 4)` - バッチサイズ1、特徴量4次元
- **型**: `float32`
- **例**: `[[5.1, 3.5, 1.4, 0.2]]`

**出力**:
- **形状**: `(3,)` - 3クラスの確率
- **型**: `float64`
- **例**: `[0.971, 0.016, 0.013]`

### 7.3 ラベルマッピング

```json
{
  "0": "setosa",
  "1": "versicolor",
  "2": "virginica"
}
```

---

## 8. Docker Compose設計

### 8.1 コンテナ構成

```yaml
services:
  mysql:
    image: mysql:5.7
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: sample_db
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    volumes:
      - mysql_data:/var/lib/mysql

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    depends_on:
      - mysql
    environment:
      MYSQL_SERVER: mysql
      MYSQL_USER: user
      MYSQL_PASSWORD: password
      MYSQL_DATABASE: sample_db
      MODEL_FILEPATH: /app/models/iris_svc.onnx
      LABEL_FILEPATH: /app/models/label.json

  job:
    build:
      context: .
      dockerfile: Dockerfile.job
    depends_on:
      - mysql
    environment:
      MYSQL_SERVER: mysql
      MYSQL_USER: user
      MYSQL_PASSWORD: password
      MYSQL_DATABASE: sample_db
      MODEL_FILEPATH: /app/models/iris_svc.onnx
      LABEL_FILEPATH: /app/models/label.json

volumes:
  mysql_data:
```

### 8.2 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `MYSQL_SERVER` | MySQLホスト名 | `localhost` |
| `MYSQL_USER` | MySQLユーザー名 | `root` |
| `MYSQL_PASSWORD` | MySQLパスワード | `password` |
| `MYSQL_DATABASE` | データベース名 | `sample_db` |
| `MYSQL_PORT` | MySQLポート | `3306` |
| `MODEL_FILEPATH` | ONNXモデルパス | `/app/models/iris_svc.onnx` |
| `LABEL_FILEPATH` | ラベルファイルパス | `/app/models/label.json` |

### 8.3 ボリューム

- `mysql_data`: MySQLデータ永続化

---

## 9. 成功基準

### 9.1 機能面

- [ ] **データ登録**: 単一・複数データが正常に登録できる
- [ ] **バッチ推論**: 60秒後に未推論データが推論される
- [ ] **並列処理**: 4スレッドで並列推論が動作する
- [ ] **結果更新**: 推論結果がデータベースに正しく保存される
- [ ] **結果取得**: APIで推論済みデータが取得できる

### 9.2 非機能面

- [ ] **パフォーマンス**: 100件/分以上の推論スループット
- [ ] **可用性**: MySQLが停止してもコンテナが再起動できる
- [ ] **保守性**: ログが適切に出力される
- [ ] **スケーラビリティ**: ジョブコンテナを複数起動できる

### 9.3 テスト

- [ ] **ユニットテスト**: 全モジュールのテスト合格
- [ ] **統合テスト**: API + DB連携のテスト合格
- [ ] **E2Eテスト**: データ登録→バッチ実行→結果取得の一連の流れ

### 9.4 ドキュメント

- [ ] **README.md**: セットアップ手順、実行方法、学習内容
- [ ] **SPECIFICATION.md**: 本仕様書（本ファイル）
- [ ] **コメント**: 重要なロジックにコメント記載

---

## 10. 実装スケジュール

### Phase 1: 理解（完了）
- [x] 参考コード分析
- [x] アーキテクチャ理解

### Phase 2: 仕様策定（現在）
- [x] SPECIFICATION.md作成

### Phase 3: セットアップ
- [ ] ディレクトリ構造作成
- [ ] pyproject.toml設定
- [ ] .python-version設定

### Phase 4: データベース層実装（TDD）
- [ ] models.py
- [ ] database.py
- [ ] cruds.py
- [ ] schemas.py

### Phase 5: API層実装（TDD）
- [ ] routers.py
- [ ] app.py

### Phase 6: 推論層実装（TDD）
- [ ] prediction.py

### Phase 7: バッチジョブ実装（TDD）
- [ ] job.py

### Phase 8: Docker化
- [ ] Dockerfile.api
- [ ] Dockerfile.job
- [ ] docker-compose.yml

### Phase 9: テスト・検証
- [ ] ユニットテスト
- [ ] 統合テスト
- [ ] E2Eテスト

### Phase 10: ドキュメント
- [ ] README.md更新
- [ ] 学習内容まとめ

---

## 11. 参考資料

- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [SQLAlchemy公式ドキュメント](https://docs.sqlalchemy.org/)
- [ONNX Runtime](https://onnxruntime.ai/)
- [MySQL 5.7リファレンス](https://dev.mysql.com/doc/refman/5.7/en/)
- [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html)

---

**作成日**: 2025-11-13
**バージョン**: 1.0
**パターン**: Chapter 4 - Batch Pattern（バッチ推論パターン）
