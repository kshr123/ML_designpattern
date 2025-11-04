# Model DB 仕様書

Version: 1.0.0
Last Updated: 2025-11-04
Author: kshr123

---

## 目次

1. [要件定義](#1-要件定義)
2. [アーキテクチャ設計](#2-アーキテクチャ設計)
3. [API仕様](#3-api仕様)
4. [データモデル](#4-データモデル)
5. [成功基準](#5-成功基準)
6. [制約事項](#6-制約事項)

---

## 1. 要件定義

### 1.1 背景と目的

**背景**
- 機械学習プロジェクトでは、複数のモデルや実験を管理する必要がある
- モデルのバージョン、パラメータ、評価結果を追跡・比較したい
- 再現性を担保するため、学習データやモデルファイルのパスを記録する必要がある

**目的**
- 機械学習モデルのライフサイクル全体を管理するデータベースシステムを構築する
- REST APIを通じてプロジェクト、モデル、実験情報を登録・取得できるようにする
- MLOpsの基盤として、モデルの追跡と管理を容易にする

### 1.2 機能要件

#### 必須機能

##### プロジェクト管理
- [ ] **FR-001**: プロジェクト登録
  - 詳細: プロジェクト名と説明を登録できる
  - 入力: `project_name`, `description` (optional)
  - 出力: 登録されたプロジェクト情報 (`project_id`, `created_datetime`)

- [ ] **FR-002**: プロジェクト取得
  - 詳細: 全プロジェクト、またはIDや名前で特定プロジェクトを取得
  - 入力: `project_id` または `project_name` (optional)
  - 出力: プロジェクト情報のリスト or 単一プロジェクト

##### モデル管理
- [ ] **FR-003**: モデル登録
  - 詳細: プロジェクト配下にモデルを登録できる
  - 入力: `project_id`, `model_name`, `description` (optional)
  - 出力: 登録されたモデル情報 (`model_id`, `created_datetime`)

- [ ] **FR-004**: モデル取得
  - 詳細: 全モデル、またはID、プロジェクトID、名前でモデルを取得
  - 入力: `model_id`, `project_id`, `model_name`, `project_name` (optional)
  - 出力: モデル情報のリスト or 単一モデル

##### 実験管理
- [ ] **FR-005**: 実験登録
  - 詳細: モデルの実験記録を登録できる
  - 入力: `model_id`, `model_version_id`, `parameters`, `training_dataset`, `validation_dataset`, `test_dataset`, `evaluations`, `artifact_file_paths` (all optional except model_id and model_version_id)
  - 出力: 登録された実験情報 (`experiment_id`, `created_datetime`)

- [ ] **FR-006**: 実験取得
  - 詳細: 全実験、またはID、モデルID、プロジェクトIDで実験を取得
  - 入力: `experiment_id`, `model_version_id`, `model_id`, `project_id` (optional)
  - 出力: 実験情報のリスト or 単一実験

- [ ] **FR-007**: 実験結果更新
  - 詳細: 既存実験の評価結果やモデルファイルパスを更新できる
  - 入力: `experiment_id`, `evaluations` または `artifact_file_paths`
  - 出力: 更新された実験情報

#### オプション機能
- [ ] **FR-OPT-001**: プロジェクト・モデル・実験の削除機能
- [ ] **FR-OPT-002**: 実験の比較機能
- [ ] **FR-OPT-003**: ページネーション機能

### 1.3 非機能要件

#### パフォーマンス
- **レスポンスタイム**: 平均 < 200ms、99パーセンタイル < 1000ms
- **スループット**: > 50 req/sec (十分な性能)
- **データベースクエリ**: インデックスを活用した高速検索

#### スケーラビリティ
- **同時接続数**: > 50接続
- **水平スケーリング**: Docker Composeによる複数コンテナ起動可能
- **データ量**: 1万件以上のプロジェクト・モデル・実験を管理可能

#### 可用性
- **稼働率**: 99%以上（開発環境）
- **データ永続化**: PostgreSQLによる永続化
- **復旧**: Docker Composeによる簡単な再起動

#### セキュリティ
- **認証**: 本バージョンでは未実装（将来的にAPIキー認証を検討）
- **入力検証**: Pydanticによる厳格なバリデーション
- **SQLインジェクション対策**: SQLAlchemy ORMによる防御

#### 保守性
- **ログ**: uvicornの標準ログ出力
- **テストカバレッジ**: > 80%
- **コード品質**: 型ヒント、docstring、PEP 8準拠

---

## 2. アーキテクチャ設計

### 2.1 システム構成

```
┌─────────────────┐
│     Client      │
│  (REST Client)  │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────────────┐
│    FastAPI Server       │
│  (Port 8000)            │
│  ┌───────────────────┐  │
│  │  API Routers      │  │
│  │  - /projects      │  │
│  │  - /models        │  │
│  │  - /experiments   │  │
│  │  - /health        │  │
│  └─────────┬─────────┘  │
│            │             │
│  ┌─────────▼─────────┐  │
│  │   CRUD Layer      │  │
│  │  (Database Ops)   │  │
│  └─────────┬─────────┘  │
│            │             │
│  ┌─────────▼─────────┐  │
│  │  SQLAlchemy ORM   │  │
│  └─────────┬─────────┘  │
└────────────┼─────────────┘
             │
             ↓
┌─────────────────────────┐
│    PostgreSQL 13        │
│  (Port 5432)            │
│  ┌───────────────────┐  │
│  │  projects table   │  │
│  │  models table     │  │
│  │  experiments table│  │
│  └───────────────────┘  │
└─────────────────────────┘
```

### 2.2 コンポーネント設計

#### API Layer (`src/api/`)
- **役割**: HTTPリクエストの受付とレスポンス
- **責務**:
  - ルーティング（FastAPI Router）
  - リクエストバリデーション（Pydantic）
  - レスポンスフォーマット
  - エラーハンドリング

#### CRUD Layer (`src/db/cruds.py`)
- **役割**: データベース操作の実装
- **責務**:
  - Create: プロジェクト、モデル、実験の登録
  - Read: データの取得・検索
  - Update: 実験結果の更新
  - Delete: （将来実装）

#### Model Layer (`src/db/models.py`)
- **役割**: データベーステーブル定義（SQLAlchemy ORM）
- **責務**:
  - テーブル構造の定義
  - カラム定義（型、制約、コメント）
  - リレーション定義（外部キー）

#### Schema Layer (`src/db/schemas.py`)
- **役割**: リクエスト・レスポンスのデータ構造定義（Pydantic）
- **責務**:
  - データバリデーション
  - JSONシリアライズ/デシリアライズ
  - API仕様の明確化

#### Database Layer (`src/db/database.py`)
- **役割**: データベース接続管理
- **責務**:
  - SQLAlchemy Engineの作成
  - セッション管理
  - 接続プーリング

### 2.3 技術スタック

| レイヤー | 技術 | バージョン | 理由 |
|---------|------|-----------|------|
| Language | Python | 3.13+ | 最新の安定版、型ヒント強化 |
| Web Framework | FastAPI | 0.111+ | 高速、型安全、自動API文書生成 |
| ORM | SQLAlchemy | 1.4+ | 強力なORM、マイグレーション対応 |
| Database | PostgreSQL | 13+ | リレーショナルDB、JSON型対応 |
| Validation | Pydantic | 2.0+ | 型安全なバリデーション |
| ASGI Server | Uvicorn | 0.30+ | 非同期対応、高速 |
| Process Manager | Gunicorn | 21.0+ | 本番環境用のワーカー管理 |
| Testing | pytest | 8.2+ | 標準的なテストツール |
| Container | Docker | latest | 環境の統一、ポータビリティ |

### 2.4 データフロー

#### プロジェクト登録フロー
```
1. Client sends POST /projects
   ↓
2. FastAPI validates request (Pydantic Schema)
   ↓
3. CRUD checks if project_name exists
   ↓
4. If not exists, generate UUID for project_id
   ↓
5. SQLAlchemy inserts to projects table
   ↓
6. PostgreSQL commits transaction
   ↓
7. FastAPI returns created project (JSON)
```

#### 実験取得フロー
```
1. Client sends GET /experiments/project-id/{project_id}
   ↓
2. FastAPI routes to experiments endpoint
   ↓
3. CRUD joins experiments and models tables
   ↓
4. SQLAlchemy executes SELECT query
   ↓
5. PostgreSQL returns matching records
   ↓
6. Pydantic serializes to JSON
   ↓
7. FastAPI returns response
```

---

## 3. API仕様

### 3.1 エンドポイント一覧

#### プロジェクト関連
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /projects/all | 全プロジェクト取得 | None |
| GET | /projects/id/{project_id} | プロジェクトをIDで取得 | None |
| GET | /projects/name/{project_name} | プロジェクトを名前で取得 | None |
| POST | /projects | プロジェクト作成 | None |

#### モデル関連
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /models/all | 全モデル取得 | None |
| GET | /models/id/{model_id} | モデルをIDで取得 | None |
| GET | /models/project-id/{project_id} | プロジェクトIDでモデル取得 | None |
| GET | /models/name/{model_name} | モデルを名前で取得 | None |
| GET | /models/project-name/{project_name} | プロジェクト名でモデル取得 | None |
| POST | /models | モデル作成 | None |

#### 実験関連
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /experiments/all | 全実験取得 | None |
| GET | /experiments/id/{experiment_id} | 実験をIDで取得 | None |
| GET | /experiments/model-version-id/{model_version_id} | モデルバージョンIDで実験取得 | None |
| GET | /experiments/model-id/{model_id} | モデルIDで実験取得 | None |
| GET | /experiments/project-id/{project_id} | プロジェクトIDで実験取得 | None |
| POST | /experiments | 実験作成 | None |
| POST | /experiments/evaluations/{experiment_id} | 評価結果更新 | None |
| POST | /experiments/artifact-file-paths/{experiment_id} | モデルファイルパス更新 | None |

#### ヘルスチェック
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /health | ヘルスチェック | None |

### 3.2 詳細仕様

#### POST /projects

**説明**: 新しいプロジェクトを作成する（既存の場合は既存のプロジェクトを返す）

**リクエスト**

```json
{
  "project_name": "image_classification",
  "description": "画像分類プロジェクト"
}
```

**レスポンス (200 OK)**

```json
{
  "project_id": "a1b2c3",
  "project_name": "image_classification",
  "description": "画像分類プロジェクト",
  "created_datetime": "2025-11-04T12:00:00+09:00"
}
```

#### POST /experiments

**説明**: 新しい実験記録を作成する

**リクエスト**

```json
{
  "model_id": "d4e5f6",
  "model_version_id": "v1.0.0",
  "parameters": {
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100
  },
  "training_dataset": "s3://bucket/train.csv",
  "validation_dataset": "s3://bucket/val.csv",
  "test_dataset": "s3://bucket/test.csv",
  "evaluations": {
    "accuracy": 0.95,
    "f1_score": 0.93
  },
  "artifact_file_paths": {
    "model": "s3://bucket/models/model.pkl",
    "weights": "s3://bucket/models/weights.h5"
  }
}
```

**レスポンス (200 OK)**

```json
{
  "experiment_id": "g7h8i9",
  "model_id": "d4e5f6",
  "model_version_id": "v1.0.0",
  "parameters": {...},
  "training_dataset": "s3://bucket/train.csv",
  "validation_dataset": "s3://bucket/val.csv",
  "test_dataset": "s3://bucket/test.csv",
  "evaluations": {...},
  "artifact_file_paths": {...},
  "created_datetime": "2025-11-04T12:30:00+09:00"
}
```

#### POST /experiments/evaluations/{experiment_id}

**説明**: 実験の評価結果を更新する（既存の評価に追加/更新）

**リクエスト**

```json
{
  "evaluations": {
    "precision": 0.94,
    "recall": 0.92
  }
}
```

**レスポンス (200 OK)**

```json
{
  "experiment_id": "g7h8i9",
  "evaluations": {
    "accuracy": 0.95,
    "f1_score": 0.93,
    "precision": 0.94,
    "recall": 0.92
  },
  ...
}
```

#### GET /health

**説明**: サービスの健全性を確認

**レスポンス (200 OK)**

```json
{
  "status": "ok"
}
```

---

## 4. データモデル

### 4.1 データベーススキーマ

#### projects テーブル

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|-----|------|
| project_id | String(255) | PRIMARY KEY | プロジェクト一意識別子（UUID6桁） |
| project_name | String(255) | NOT NULL, UNIQUE | プロジェクト名 |
| description | Text | NULLABLE | プロジェクトの説明 |
| created_datetime | DateTime(timezone=True) | NOT NULL, DEFAULT=now() | 作成日時 |

#### models テーブル

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|-----|------|
| model_id | String(255) | PRIMARY KEY | モデル一意識別子（UUID6桁） |
| project_id | String(255) | FOREIGN KEY(projects.project_id), NOT NULL | プロジェクトID |
| model_name | String(255) | NOT NULL | モデル名 |
| description | Text | NULLABLE | モデルの説明 |
| created_datetime | DateTime(timezone=True) | NOT NULL, DEFAULT=now() | 作成日時 |

**制約**:
- プロジェクト内でmodel_nameは一意（ビジネスロジックで制御）

#### experiments テーブル

| カラム名 | 型 | 制約 | 説明 |
|---------|-----|-----|------|
| experiment_id | String(255) | PRIMARY KEY | 実験一意識別子（UUID6桁） |
| model_id | String(255) | FOREIGN KEY(models.model_id), NOT NULL | モデルID |
| model_version_id | String(255) | NOT NULL | モデルバージョンID |
| parameters | JSON | NULLABLE | 学習パラメータ |
| training_dataset | Text | NULLABLE | 学習データセットパス |
| validation_dataset | Text | NULLABLE | 検証データセットパス |
| test_dataset | Text | NULLABLE | テストデータセットパス |
| evaluations | JSON | NULLABLE | 評価結果 |
| artifact_file_paths | JSON | NULLABLE | モデルファイルパス |
| created_datetime | DateTime(timezone=True) | NOT NULL, DEFAULT=now() | 作成日時 |

### 4.2 Pydantic スキーマ

#### ProjectCreate
```python
class ProjectCreate(BaseModel):
    project_name: str
    description: Optional[str] = None
```

#### Project
```python
class Project(BaseModel):
    project_id: str
    project_name: str
    description: Optional[str]
    created_datetime: datetime

    class Config:
        orm_mode = True
```

#### ModelCreate
```python
class ModelCreate(BaseModel):
    project_id: str
    model_name: str
    description: Optional[str] = None
```

#### Model
```python
class Model(BaseModel):
    model_id: str
    project_id: str
    model_name: str
    description: Optional[str]
    created_datetime: datetime

    class Config:
        orm_mode = True
```

#### ExperimentCreate
```python
class ExperimentCreate(BaseModel):
    model_id: str
    model_version_id: str
    parameters: Optional[Dict[str, Any]] = None
    training_dataset: Optional[str] = None
    validation_dataset: Optional[str] = None
    test_dataset: Optional[str] = None
    evaluations: Optional[Dict[str, Any]] = None
    artifact_file_paths: Optional[Dict[str, Any]] = None
```

#### Experiment
```python
class Experiment(BaseModel):
    experiment_id: str
    model_id: str
    model_version_id: str
    parameters: Optional[Dict[str, Any]]
    training_dataset: Optional[str]
    validation_dataset: Optional[str]
    test_dataset: Optional[str]
    evaluations: Optional[Dict[str, Any]]
    artifact_file_paths: Optional[Dict[str, Any]]
    created_datetime: datetime

    class Config:
        orm_mode = True
```

### 4.3 ER図

```
┌─────────────────┐
│   projects      │
├─────────────────┤
│ project_id (PK) │
│ project_name    │
│ description     │
│ created_datetime│
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐
│   models        │
├─────────────────┤
│ model_id (PK)   │
│ project_id (FK) │
│ model_name      │
│ description     │
│ created_datetime│
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────────┐
│   experiments       │
├─────────────────────┤
│ experiment_id (PK)  │
│ model_id (FK)       │
│ model_version_id    │
│ parameters (JSON)   │
│ training_dataset    │
│ validation_dataset  │
│ test_dataset        │
│ evaluations (JSON)  │
│ artifact_file_paths │
│ created_datetime    │
└─────────────────────┘
```

---

## 5. 成功基準

### 5.1 機能面

- [ ] 全てのプロジェクト操作API（作成、取得）が正常動作する
- [ ] 全てのモデル操作API（作成、取得）が正常動作する
- [ ] 全ての実験操作API（作成、取得、更新）が正常動作する
- [ ] 外部キー制約が正しく機能する（存在しないproject_idでモデル作成できない等）
- [ ] 同じproject_name/model_nameの重複登録が適切に処理される
- [ ] ヘルスチェックエンドポイントが動作する
- [ ] Swagger UI (http://localhost:8000/docs) でAPIドキュメントが閲覧できる

### 5.2 品質面

- [ ] ユニットテストカバレッジ > 80%
  - CRUD関数の全テスト
  - スキーマバリデーションのテスト
- [ ] 統合テストが全て通過
  - エンドポイントのE2Eテスト
  - データベース操作のテスト
- [ ] 型チェック（mypy）がエラーなく通る

### 5.3 パフォーマンス面

- [ ] 単一レコード取得 < 100ms
- [ ] 全レコード取得（100件） < 500ms
- [ ] レコード作成 < 200ms
- [ ] 同時10接続でエラーなく動作

### 5.4 運用面

- [ ] Docker Composeで環境を簡単に起動できる
- [ ] ログが標準出力に適切に出力される
- [ ] README.mdにセットアップ手順が記載されている
- [ ] SPECIFICATION.mdが最新の状態に保たれている

---

## 6. 制約事項

### 6.1 技術的制約

- Python 3.13以上が必要
- PostgreSQL 13以上が必要
- Docker、Docker Composeが必要
- メモリ: 最低1GB推奨（PostgreSQL + FastAPI）
- ストレージ: 最低500MB（Dockerイメージ + データベース）

### 6.2 機能的制約

- **認証・認可**: 本バージョンでは未実装（全てのエンドポイントがパブリック）
- **削除機能**: 本バージョンでは未実装
- **トランザクション**: 複数テーブルにまたがる複雑なトランザクションは未対応
- **ページネーション**: 大量データ取得時のページングは未実装
- **検索機能**: 部分一致検索やフィルタリングは限定的

### 6.3 スコープ外

以下は本バージョンでは実装しない：
- [ ] 認証・認可機能（APIキー、OAuth2等）
- [ ] 削除機能（論理削除、物理削除）
- [ ] ページネーション・ソート機能
- [ ] 実験の比較・可視化機能
- [ ] モデルファイルの実体管理（S3等との連携）
- [ ] 監査ログ・変更履歴
- [ ] マイグレーション管理（Alembic等）
- [ ] パフォーマンスモニタリング（Prometheus等）

将来のバージョンで検討する機能：
- [ ] GraphQL API対応
- [ ] WebSocket対応（リアルタイム更新）
- [ ] 機械学習パイプラインとの統合（MLflow等）
- [ ] レコメンデーション機能（ベストモデル提案）

---

## 変更履歴

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-04 | kshr123 | 初版作成 |

---

## 参考資料

- [参考リポジトリ](../../../reference/chapter2_training/model_db/)
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [SQLAlchemy公式ドキュメント](https://docs.sqlalchemy.org/)
- [Pydantic公式ドキュメント](https://docs.pydantic.dev/)
- [PostgreSQL公式ドキュメント](https://www.postgresql.org/docs/)
