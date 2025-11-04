# Model DB - モデル管理データベース

機械学習モデルのライフサイクル管理システム

## 概要

このプロジェクトは、機械学習プロジェクトにおけるモデル、実験、パラメータ、評価結果を管理するためのREST APIサービスです。
Project → Model → Experiment の3階層構造でデータを管理し、MLOpsの基盤として機能します。

## 実装状況

### ✅ 完了したフェーズ

1. **理解フェーズ** - 参考コードの分析完了
2. **仕様策定フェーズ** - SPECIFICATION.md作成完了
3. **テスト設計フェーズ** - 31個のテストケース作成完了
4. **実装フェーズ** - 全コンポーネント実装完了

### 📊 実装内容

| レイヤー | ファイル | 実装内容 | テスト |
|---------|---------|---------|--------|
| Database Layer | `src/db/database.py` | データベース接続管理 | ✅ |
| Model Layer | `src/db/models.py` | SQLAlchemyテーブル定義（3テーブル） | ✅ |
| Schema Layer | `src/db/schemas.py` | Pydanticスキーマ（9スキーマ） | ✅ |
| CRUD Layer | `src/db/cruds.py` | ビジネスロジック（20関数） | ✅ |
| API Layer | `src/api/app.py`, `src/api/routers/` | FastAPIエンドポイント（16エンドポイント） | ✅ |

### 📈 テスト結果

- **総テストケース数**: 31個
- **成功**: 31個 ✅
- **失敗**: 0個
- **コードカバレッジ**: 92%

#### テスト内訳
- **ユニットテスト** (`tests/test_cruds.py`): 15個
  - プロジェクトCRUD: 6個
  - モデルCRUD: 5個
  - 実験CRUD: 4個
- **統合テスト** (`tests/test_api.py`): 16個
  - ヘルスチェック: 1個
  - プロジェクトAPI: 5個
  - モデルAPI: 4個
  - 実験API: 6個

## アーキテクチャ

```
┌─────────────────┐
│  REST Client    │
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────────┐
│  FastAPI (API Layer)│
│  - /projects        │
│  - /models          │
│  - /experiments     │
└────────┬────────────┘
         │
┌────────▼────────────┐
│  CRUD Layer         │
│  (Business Logic)   │
└────────┬────────────┘
         │
┌────────▼────────────┐
│  SQLAlchemy (ORM)   │
│  - Project          │
│  - Model            │
│  - Experiment       │
└────────┬────────────┘
         │
┌────────▼────────────┐
│  PostgreSQL         │
└─────────────────────┘
```

## データモデル

### 3階層構造

```
Project (プロジェクト)
  └── Model (モデル)
        └── Experiment (実験)
```

- **Project**: 機械学習プロジェクトの情報
- **Model**: プロジェクト配下のモデル情報
- **Experiment**: モデルの学習実験記録（パラメータ、データセット、評価結果、モデルファイルパス）

## セットアップ

### 前提条件

- Python 3.13以上
- PostgreSQL 13以上（本番環境）
- Docker & Docker Compose（推奨）

### 開発環境

```bash
# 1. 仮想環境作成
uv venv
source .venv/bin/activate  # macOS/Linux

# 2. 依存関係インストール
uv pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dateutil

# 3. 開発ツールインストール
uv pip install pytest pytest-cov httpx black ruff mypy
```

### テスト実行

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ付きテスト
pytest tests/ --cov=src --cov-report=term

# 特定のテストファイルのみ
pytest tests/test_cruds.py -v
pytest tests/test_api.py -v
```

## API エンドポイント

### プロジェクト関連

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/all` | 全プロジェクト取得 |
| GET | `/projects/id/{project_id}` | プロジェクトをIDで取得 |
| GET | `/projects/name/{project_name}` | プロジェクトを名前で取得 |
| POST | `/projects` | プロジェクト作成 |

### モデル関連

| Method | Path | Description |
|--------|------|-------------|
| GET | `/models/all` | 全モデル取得 |
| GET | `/models/id/{model_id}` | モデルをIDで取得 |
| GET | `/models/project-id/{project_id}` | プロジェクトIDでモデル取得 |
| GET | `/models/name/{model_name}` | モデルを名前で取得 |
| POST | `/models` | モデル作成 |

### 実験関連

| Method | Path | Description |
|--------|------|-------------|
| GET | `/experiments/all` | 全実験取得 |
| GET | `/experiments/id/{experiment_id}` | 実験をIDで取得 |
| GET | `/experiments/model-id/{model_id}` | モデルIDで実験取得 |
| POST | `/experiments` | 実験作成 |
| POST | `/experiments/evaluations/{experiment_id}` | 評価結果更新 |
| POST | `/experiments/artifact-file-paths/{experiment_id}` | モデルファイルパス更新 |

### ヘルスチェック

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | ヘルスチェック |

## 使用例

### プロジェクト作成

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "image_classification",
    "description": "画像分類プロジェクト"
  }'
```

### モデル作成

```bash
curl -X POST http://localhost:8000/models \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "a1b2c3",
    "model_name": "resnet50",
    "description": "ResNet50ベースのモデル"
  }'
```

### 実験作成

```bash
curl -X POST http://localhost:8000/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "d4e5f6",
    "model_version_id": "v1.0.0",
    "parameters": {
      "learning_rate": 0.001,
      "batch_size": 32,
      "epochs": 100
    },
    "evaluations": {
      "accuracy": 0.95,
      "f1_score": 0.93
    }
  }'
```

## 技術スタック

- **Language**: Python 3.13
- **Web Framework**: FastAPI 0.121+
- **ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL 13+ (本番), SQLite (テスト)
- **Validation**: Pydantic 2.12+
- **ASGI Server**: Uvicorn 0.38+
- **Testing**: pytest 8.4+
- **Package Manager**: uv

## 開発手法

このプロジェクトは以下の開発手法を採用しています：

- **仕様駆動開発 (SDD)**: SPECIFICATION.mdで仕様を明確化
- **テスト駆動開発 (TDD)**: Red→Green→Refactorサイクル
- **レイヤー分離**: API, CRUD, Model, Schemaの明確な責務分離

## 学んだこと

### レイヤー分離の重要性

各レイヤーが明確な責務を持つことで：
- テストが容易
- 変更の影響範囲が限定的
- 再利用性が高い
- 保守性が向上

### Pydanticの役割

- リクエスト/レスポンスの自動バリデーション
- DBモデル↔API間のデータ変換
- Swagger UIの自動生成

### TDDのメリット

- テストを先に書くことで仕様が明確化
- リファクタリングが安心してできる
- バグの早期発見
- ドキュメントとしても機能

### SQLiteのJSON型の扱い

SQLiteのJSON型カラムを更新する際は、新しいdictオブジェクトを作成する必要がある：

```python
# ❌ これだと更新されない
data.evaluations["new_key"] = value

# ✅ 新しいdictを作成
updated = dict(data.evaluations)
updated.update({"new_key": value})
data.evaluations = updated
```

## 次のステップ

- [ ] Docker Composeによる本番環境セットアップ
- [ ] PostgreSQLへの接続確認
- [ ] エラーハンドリングの強化
- [ ] ページネーション機能の追加
- [ ] 認証・認可機能の追加

## 参考資料

- [SPECIFICATION.md](./SPECIFICATION.md) - 詳細な仕様書
- [参考リポジトリ](../../../reference/chapter2_training/model_db/)
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [SQLAlchemy公式ドキュメント](https://docs.sqlalchemy.org/)

---

**実装日**: 2025-11-04
**開発者**: kshr123
**バージョン**: 0.1.0
