# 機械学習システムデザインパターン - 学習進捗記録

## 📊 概要

| 項目 | 内容 |
|------|------|
| **開始日** | 2025-11-03 |
| **完了パターン数** | 1 / 26 パターン |
| **現在の章** | Chapter 2: Training |
| **最新の完了** | Model DB (2025-11-04) |
| **次の目標** | Iris分類パターン（iris_sklearn_svc） |

---

## 📑 目次

### 🎯 [学習目標](#学習目標)
### 📚 [参考リポジトリ](#参考リポジトリ)
### 📖 [章ごとの学習状況](#章ごとの学習状況)
  - [Chapter 2: Training](#chapter-2-training学習)
  - [Chapter 3: Release Patterns](#chapter-3-release-patternsリリースパターン)
  - [Chapter 4: Serving Patterns](#chapter-4-serving-patterns推論パターン)
  - [Chapter 5: Operations](#chapter-5-operations運用)
  - [Chapter 6: Operation Management](#chapter-6-operation-management運用管理)

### 📝 [学習メモ](#学習メモ)
  - [2025-11-03 - プロジェクトセットアップ](#2025-11-03---プロジェクトセットアップ完了)
  - [2025-11-04 - Model DB実装](#2025-11-04---model-dbモデル管理データベース)

### 💡 [気づき・応用アイデア](#気づき応用アイデア)

---

## 🎯 学習目標

- 機械学習システムのデザインパターンを理解する
- 各パターンを実際に実装して動作を確認する
- 実プロジェクトに応用できるスキルを身につける

---

## 📚 参考リポジトリ

- [ml-system-in-actions](./reference/README.md)
- 書籍: 『AIエンジニアのための機械学習システムデザインパターン』

---

## 📖 章ごとの学習状況

### Chapter 2: Training（学習）
- [ ] cifar10
- [ ] iris_binary
- [ ] iris_sklearn_outlier
- [ ] iris_sklearn_rf
- [ ] iris_sklearn_svc
- [x] model_db (完了: 2025-11-04)

### Chapter 3: Release Patterns（リリースパターン）
- [ ] model_in_image_pattern
- [ ] model_load_pattern

### Chapter 4: Serving Patterns（推論パターン）
- [ ] asynchronous_pattern
- [ ] batch_pattern
- [ ] data_cache_pattern
- [ ] edge_ai_pattern
- [ ] horizontal_microservice_pattern
- [ ] prediction_cache_pattern
- [ ] prep_pred_pattern
- [ ] sync_async_pattern
- [ ] synchronous_pattern
- [ ] web_single_pattern

### Chapter 5: Operations（運用）
- [ ] prediction_log_pattern
- [ ] prediction_monitoring_pattern

### Chapter 6: Operation Management（運用管理）
- [ ] circuit_breaker_pattern
- [ ] condition_based_pattern
- [ ] load_test_pattern
- [ ] online_ab_pattern
- [ ] paramater_based_pattern
- [ ] shadow_ab_pattern

---

## 📝 学習メモ

### 2025-11-03 - プロジェクトセットアップ完了

#### ✅ 完了した作業

**1. 環境構築**
- 参考リポジトリ（ml-system-in-actions）をクローン
- プロジェクト構造の整理（reference/, templates/, docs/, my_implementations/, notes/, progress/）
- Python 3.13 + uvの環境設定
- .gitignoreの作成

**2. 開発方法論の確立**
- 仕様駆動開発（SDD）の導入
- テスト駆動開発（TDD）の導入
- 7フェーズの開発フローを定義
  1. 理解 → 2. 仕様策定 → 3. テスト設計 → 4. 実装 → 5. リファクタリング → 6. 検証 → 7. 振り返り

**3. テンプレート作成**
- `templates/SPECIFICATION.template.md` - 仕様書テンプレート
- `templates/pyproject.toml.template` - プロジェクト設定
- `templates/test_unit.template.py` - ユニットテストテンプレート
- `templates/test_integration.template.py` - 統合テストテンプレート
- `templates/test_e2e.template.py` - E2Eテストテンプレート
- `templates/mcp_settings.json.template` - MCP設定テンプレート

**4. ドキュメント作成**
- `docs/DEVELOPMENT_WORKFLOW.md` - 詳細な開発ワークフロー
- `docs/MCP_SETUP.md` - MCP設定ガイド
- `docs/GITHUB_MCP_QUICKSTART.md` - GitHubクイックスタート
- `docs/MCP_STATUS.md` - MCP設定状況
- `.claude/claude.md` - プロジェクトルールとベストプラクティス

**5. MCP設定**
- ✅ GitHub MCP Server設定完了
- GitHub Personal Access Token取得・設定
- `~/.claude/settings.json` 更新完了

#### 📋 プロジェクト構造

```
ML_designpattern/
├── reference/              # 参考リポジトリ（読み取り専用）
├── my_implementations/     # 実装コード（これから作成）
├── templates/              # テンプレートファイル
├── docs/                   # ドキュメント
├── notes/                  # 学習メモ
├── progress/               # 進捗管理（このファイル）
├── .claude/               # Claude Code設定
├── .gitignore
└── README.md
```

#### 🎯 次回のタスク

**優先度：最高（MCP設定完了が先）**
1. **Claude Codeを再起動してMCP設定を完了**
   - GitHub MCP接続確認（/mcpコマンド）
   - Context7 MCP追加
   - Serena MCP追加
   - Notion MCP追加
   - 詳細: [docs/MCP_RESTART_GUIDE.md](../docs/MCP_RESTART_GUIDE.md)

**優先度：高（MCP設定後）**
2. **Chapter 4: synchronous_pattern の実装開始**
   - 参考コードの理解フェーズから開始
   - `reference/chapter4_serving_patterns/synchronous_pattern/` を分析
   - 理解した内容を `notes/synchronous_pattern_understanding.md` に記録

**手順**:
```bash
# 1. 参考コードを確認
cd reference/chapter4_serving_patterns/synchronous_pattern
cat README.md

# 2. プロジェクトディレクトリ作成
cd ../../my_implementations
mkdir -p ch4__synchronous_pattern
cd ch4__synchronous_pattern

# 3. テンプレートコピー
cp ../../templates/pyproject.toml.template pyproject.toml
echo "3.13" > .python-version

# 4. 環境セットアップ
uv venv
source .venv/bin/activate
uv pip install pytest pytest-cov black ruff mypy

# 5. ディレクトリ構造作成
mkdir -p src/synchronous_pattern tests
touch src/synchronous_pattern/__init__.py tests/__init__.py

# 6. 仕様書作成
cp ../../templates/SPECIFICATION.template.md SPECIFICATION.md
```

**Claude Codeへの指示例**:
- "synchronous_patternの参考コードを分析して、アーキテクチャと要件を説明して"
- "SPECIFICATION.mdを作成して。同期推論パターンの仕様を定義して"

#### 📚 重要なドキュメント

- [開発ワークフロー](../docs/DEVELOPMENT_WORKFLOW.md) - 実装手順の詳細
- [Claude Rules](../.claude/claude.md) - 開発ルールとベストプラクティス
- [MCP Status](../docs/MCP_STATUS.md) - MCP設定状況

#### 🔧 開発環境

- Python: 3.13
- パッケージマネージャー: uv
- MCP: GitHub（設定済み）
- 開発手法: 仕様駆動開発（SDD） + テスト駆動開発（TDD）

#### 💡 重要な気づき

- 仕様を先に書くことで実装の方向性が明確になる
- テストを先に書くことで品質が担保される
- テンプレートを用意することで一貫性のある実装ができる
- MCPを使うことでGitHub操作が効率化される

---

### 2025-11-04 - Model DB（モデル管理データベース）

#### 学んだこと

**1. レイヤー分離アーキテクチャ**
- API Layer, CRUD Layer, Model Layer, Schema Layerの明確な分離
- 各レイヤーが単一の責務を持つことの重要性（Single Responsibility Principle）
- レイヤー分離により、テスト容易性・保守性・拡張性が向上

**2. Pydanticの3つの役割**
- バリデーション：リクエストデータの自動検証
- シリアライゼーション：DBオブジェクト↔JSONの相互変換
- ドキュメント生成：Swagger UIの自動生成

**3. テスト駆動開発（TDD）の実践**
- Red（失敗するテスト）→ Green（テストを通す）→ Refactor（改善）
- テストを先に書くことで仕様が明確化
- 31個のテストケースで92%のカバレッジを達成

**4. SQLAlchemyとPydanticの使い分け**
- SQLAlchemy（models.py）：データベース構造の定義
- Pydantic（schemas.py）：API入出力の定義
- 同じ名前のクラスでも役割が異なる

**5. SQLiteのJSON型の扱い**
- JSON型カラムの更新は新しいdictオブジェクトを作成する必要がある
- `data.evaluations["key"] = value` ではなく、`updated = dict(data.evaluations); updated.update(...); data.evaluations = updated`

#### 実装のポイント

**アーキテクチャ**
- FastAPI + SQLAlchemy + PostgreSQL
- Project → Model → Experiment の3階層構造
- 16個のRESTエンドポイント

**開発プロセス**
1. 仕様策定（SPECIFICATION.md）
2. テスト設計（31個のテストケース）
3. 実装（レイヤーごとに段階的）
4. テスト実行（全て通過）

**テスト構成**
- ユニットテスト：CRUD層の関数テスト（15個）
- 統合テスト：APIエンドポイントのE2Eテスト（16個）
- fixtureでインメモリSQLiteを使用（StaticPool）

**工夫した点**
- 同名プロジェクト/モデルの重複チェック
- JSON型カラムの更新時の新規dict作成
- テスト用データベースの分離（dependency override）

#### 疑問点・課題

**解決済み**
- ✅ レイヤー分離の理由 → 責務分離、テスト容易性、保守性向上
- ✅ Pydanticの役割 → バリデーション、シリアライゼーション、ドキュメント生成
- ✅ SQLiteのJSON型更新 → 新しいdictオブジェクトを作成

**今後の課題**
- [ ] PostgreSQLでの本番環境動作確認
- [ ] Docker Composeによる環境構築
- [ ] エラーハンドリングの強化（404, 500等）
- [ ] ページネーション機能の追加
- [ ] 認証・認可機能の実装
- [ ] ロギングとモニタリングの追加

#### 成果物

- `my_implementations/chapter2_training/model_db/`
  - SPECIFICATION.md（詳細な仕様書）
  - README.md（実装ドキュメント）
  - src/（全5レイヤーの実装）
  - tests/（31個のテストケース）

#### メトリクス

- **実装期間**: 1日
- **コード行数**: 約235行（テスト除く）
- **テストケース**: 31個
- **カバレッジ**: 92%
- **エンドポイント数**: 16個

#### 追加学習：テストコードの書き方

**学習内容**:
- テストコードの基本概念（3Aパターン：Arrange-Act-Assert）
- テストの種類（ユニットテスト、統合テスト、E2Eテスト）
- pytestの使い方（fixture、assert、コマンド）
- ベストプラクティス（1テスト1アサーション、独立性、エッジケース）
- 実践的な例題と練習問題

**作成したドキュメント**:
- `notes/test_writing_guide.md` - テストコード作成の完全ガイド

**理解したこと**:
- テストは「コードの仕様書」であり「保険」である
- テストを先に書くことで設計が明確になる（TDD）
- 良いテストの条件：具体的、独立、高速、わかりやすい

#### 実装環境の構築と動作確認

**実装内容**:
- `src/configurations.py` - 環境変数ベースの設定管理
- `src/db/initialize.py` - データベース初期化スクリプト
- `run_server.py` - 開発用サーバー起動スクリプト
- SQLiteを開発環境のデフォルトDBに設定（本番はPostgreSQL）

**動作確認結果**:
```bash
# サーバー起動成功
python run_server.py
# → http://localhost:8000 で起動
# → Swagger UI: http://localhost:8000/docs

# API動作確認（全て成功）
✅ プロジェクト作成: POST /projects
✅ プロジェクト取得: GET /projects/all
✅ モデル作成: POST /models
✅ モデル取得: GET /models/project-id/{project_id}
✅ 実験作成: POST /experiments
✅ 評価更新: POST /experiments/evaluations/{experiment_id}
✅ 実験取得: GET /experiments/model-id/{model_id}
```

**確認できたこと**:
- JSON型カラムが正常に動作（parameters, evaluations）
- 日本語データが正しく保存・取得できる
- 外部キー制約が正常に機能
- 自動ID生成が正常に動作
- データがSQLiteファイル（model_db.sqlite）に永続化

**発見した注意点**:
- エンドポイントのパス区切りはハイフン（`project-id`）を使用
- 評価更新は `PATCH` ではなく `POST` メソッド
- エンドポイントパスは仕様書と実装で一致することを確認済み

---

## 💡 気づき・応用アイデア


