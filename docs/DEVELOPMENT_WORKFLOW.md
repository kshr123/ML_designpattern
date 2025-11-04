# 開発ワークフロー - 仕様駆動 + テスト駆動開発

このドキュメントでは、機械学習システムデザインパターンを実装する際の実践的な開発ワークフローを説明します。

---

## 📋 目次

1. [概要](#概要)
2. [開発環境のセットアップ](#開発環境のセットアップ)
3. [開発サイクル](#開発サイクル)
4. [具体的な実装手順](#具体的な実装手順)
5. [品質保証](#品質保証)
6. [トラブルシューティング](#トラブルシューティング)

---

## 概要

### 開発アプローチ

本プロジェクトでは以下のアプローチを採用します：

1. **仕様駆動開発（Specification-Driven Development）**
   - まず仕様を明確化
   - 実装前に「何を作るか」を定義
   - チームやレビュアーと合意形成

2. **テスト駆動開発（Test-Driven Development）**
   - Red: 失敗するテストを書く
   - Green: テストを通す最小限の実装
   - Refactor: コードを改善

3. **段階的開発**
   - 小さなステップで進める
   - 各ステップで動作確認
   - 早期のフィードバック

### 開発フロー図

```
┌──────────────────────────────────────────────────────────────┐
│                     開発サイクル                              │
└──────────────────────────────────────────────────────────────┘
        │
        ↓
┌──────────────────┐
│ 1. 理解フェーズ  │ - 参考コード分析
│                  │ - 要件の理解
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 2. 仕様策定      │ - SPECIFICATION.md作成
│                  │ - 要件、API、データモデル定義
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 3. テスト設計    │ - テストケース作成（Red）
│                  │ - ユニット・統合・E2Eテスト
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 4. 実装          │ - テストを通す実装（Green）
│                  │ - 段階的に機能追加
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 5. リファクタ    │ - コード改善（Refactor）
│                  │ - テストは通ったまま
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 6. 検証          │ - 実際の動作確認
│                  │ - パフォーマンステスト
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 7. 振り返り      │ - 学習内容記録
│                  │ - 改善点の洗い出し
└──────────────────┘
```

---

## 開発環境のセットアップ

### 前提条件

- Python 3.13以上
- uv（パッケージマネージャー）
- Docker & Docker Compose
- Git

### 初回セットアップ

```bash
# 1. プロジェクトディレクトリに移動
cd /path/to/ML_designpattern

# 2. uvのインストール（未インストールの場合）
brew install uv

# 3. Python 3.13のインストール
uv python install 3.13
```

---

## 開発サイクル

### フェーズ1: 理解（Understanding）

**目的**: 実装するパターンを深く理解する

**手順**:

```bash
# 1. 参考コードを確認
cd reference/chapter{N}_{pattern_name}

# 2. READMEとコードを読む
cat README.md
# コードを読んで理解する

# 3. メモを作成
cd ../../notes
touch {pattern_name}_understanding.md
```

**Claude Codeへの指示例**:
- "{pattern_name}の参考コードを分析して、アーキテクチャを説明して"
- "このパターンが解決する課題とユースケースを教えて"
- "参考実装の設計判断について説明して"

**成果物**:
- `notes/{pattern_name}_understanding.md` - 理解したことのメモ

---

### フェーズ2: 仕様策定（Specification）

**目的**: 実装する内容を明確に定義する

**手順**:

```bash
# 1. プロジェクトディレクトリを作成
mkdir -p my_implementations/ch{N}__{pattern_name}
cd my_implementations/ch{N}__{pattern_name}

# 2. 環境セットアップ
cp ../../templates/pyproject.toml.template pyproject.toml
echo "3.13" > .python-version
uv venv
source .venv/bin/activate

# 3. 開発ツールのインストール
uv pip install pytest pytest-cov black ruff mypy

# 4. ディレクトリ構造作成
mkdir -p src/{pattern_name} tests
touch src/{pattern_name}/__init__.py tests/__init__.py

# 5. 仕様書のテンプレートをコピー
cp ../../templates/SPECIFICATION.template.md SPECIFICATION.md
```

**Claude Codeへの指示例**:
- "{pattern_name}のSPECIFICATION.mdを作成して"
- "要件定義から始めて、機能要件と非機能要件を明確にして"
- "API仕様を詳細に定義して"

**成果物**:
- `SPECIFICATION.md` - 完成した仕様書
- プロジェクト構造

**レビューポイント**:
- [ ] 要件が明確に定義されている
- [ ] アーキテクチャが図示されている
- [ ] API仕様が詳細に記載されている
- [ ] 成功基準が定義されている

---

### フェーズ3: テスト設計（Test Design）

**目的**: 仕様に基づいてテストケースを作成する（TDD - Red）

**手順**:

```bash
# 1. テストテンプレートをコピー
cp ../../templates/test_unit.template.py tests/test_unit.py
cp ../../templates/test_integration.template.py tests/test_integration.py
cp ../../templates/test_e2e.template.py tests/test_e2e.py

# 2. テストケースを実装
# Claude Codeに依頼してテストを作成
```

**Claude Codeへの指示例**:
- "SPECIFICATION.mdに基づいてユニットテストを作成して"
- "APIエンドポイントの統合テストを作成して"
- "エラーケースのテストも含めて"

**テストの実行（失敗することを確認）**:

```bash
# ユニットテストのみ実行
pytest tests/test_unit.py -v

# 全テスト実行
pytest tests/ -v

# → 実装がないのでテストは失敗する（Red）
```

**成果物**:
- `tests/test_unit.py` - ユニットテスト
- `tests/test_integration.py` - 統合テスト
- `tests/test_e2e.py` - E2Eテスト

---

### フェーズ4: 実装（Implementation）

**目的**: テストを通す実装を段階的に行う（TDD - Green）

**手順**:

```bash
# 実装ファイルを作成
touch src/{pattern_name}/main.py
touch src/{pattern_name}/model.py
touch src/{pattern_name}/service.py
```

**実装の進め方**:

1. **最初のテストを通す**
   ```bash
   # Claude Codeに依頼
   # "最初のテストケースを通すための最小限の実装をして"

   # テスト実行
   pytest tests/test_unit.py::TestBasic::test_first -v
   ```

2. **次のテストを通す**
   ```bash
   # Claude Codeに依頼
   # "次のテストケースを通す実装を追加して"

   # テスト実行
   pytest tests/test_unit.py::TestBasic::test_second -v
   ```

3. **繰り返し**
   - 1つずつテストを通していく
   - 各ステップでテストを実行
   - 全てのテストがGreenになるまで

**実装の原則**:
- **最小限の実装**: テストを通すために必要な最小限のコードを書く
- **段階的**: 一度に全てを実装しない
- **動作確認**: 各ステップでテストを実行

**Claude Codeへの指示例**:
- "test_basic_functionalityを通す実装をして"
- "test_error_handlingを通すようにエラー処理を追加して"
- "test_integrationを通すようにコンポーネントを統合して"

**成果物**:
- 実装コード（src/配下）
- 全テストがパス（Green）

---

### フェーズ5: リファクタリング（Refactoring）

**目的**: テストが通った状態でコードを改善する（TDD - Refactor）

**手順**:

```bash
# 1. コードレビュー依頼
# Claude Codeに「実装をレビューして改善点を提案して」

# 2. リファクタリング実施
# 提案された改善を適用

# 3. テスト実行（Greenのまま）
pytest tests/ -v --cov=src --cov-report=html

# 4. カバレッジ確認
open htmlcov/index.html
```

**リファクタリングの観点**:
- [ ] コードの可読性
- [ ] 重複の削除（DRY原則）
- [ ] 適切な抽象化
- [ ] 命名の改善
- [ ] パフォーマンス最適化
- [ ] エラーハンドリング

**Claude Codeへの指示例**:
- "コードをレビューして、リファクタリングの提案をして"
- "重複コードを関数に抽出して"
- "この関数の責務を分割して"
- "型ヒントを追加して"

**コード品質チェック**:

```bash
# フォーマット
black src/ tests/

# リント
ruff check src/ tests/ --fix

# 型チェック
mypy src/

# 全テスト + カバレッジ
pytest tests/ -v --cov=src --cov-report=term --cov-report=html
```

**成果物**:
- リファクタリングされたコード
- テストカバレッジレポート

---

### フェーズ6: 検証（Verification）

**目的**: 実際の動作を確認し、非機能要件を検証する

**手順**:

```bash
# 1. アプリケーションを起動
python -m src.{pattern_name}.main

# 2. 別ターミナルで動作確認
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": {"field1": "test"}}'

# 3. ログ確認
tail -f logs/app.log

# 4. パフォーマンステスト
pytest tests/test_e2e.py::TestPerformanceE2E -v
```

**検証項目**:

| 項目 | 確認方法 | 基準 |
|------|---------|------|
| 機能要件 | E2Eテスト | 全テストパス |
| レスポンスタイム | パフォーマンステスト | < 100ms |
| エラーハンドリング | エラーケーステスト | 適切なエラーメッセージ |
| ログ | ログファイル確認 | 構造化ログ出力 |
| メトリクス | /metrics確認 | 必要なメトリクス収集 |

**Claude Codeへの指示例**:
- "アプリケーションを起動して動作確認して"
- "パフォーマンステストを実行して結果を分析して"
- "エラーケースを実際に試して、ログを確認して"

**成果物**:
- 動作確認結果
- パフォーマンステスト結果
- ログサンプル

---

### フェーズ7: 振り返り（Retrospective）

**目的**: 学習内容を記録し、改善点を見つける

**手順**:

```bash
# 1. README作成
touch README.md
# Claude Codeに「READMEを作成して」

# 2. 学習ログ更新
cd ../../progress
# learning_log.mdに記録
```

**記録する内容**:

1. **学んだこと**
   - パターンの理解
   - 技術的な発見
   - 設計判断の理由

2. **うまくいった点**
   - 効果的だったアプローチ
   - 良い設計判断

3. **改善点**
   - 困難だった点
   - より良い方法
   - 次回への教訓

4. **コードメトリクス**
   - テストカバレッジ
   - コード行数
   - パフォーマンス結果

**Claude Codeへの指示例**:
- "README.mdを作成して。セットアップ手順と実行方法を含めて"
- "このパターンの学習ポイントをまとめて"
- "実装の改善点を提案して"

**成果物**:
- `README.md` - 実装ドキュメント
- `progress/learning_log.md` 更新 - 学習記録

---

## 品質保証

### コード品質チェックリスト

実装完了前に以下を確認：

#### 機能面
- [ ] 全ての機能要件が実装されている
- [ ] 全てのテストケースがパスする
- [ ] エラーハンドリングが適切

#### コード品質
- [ ] PEP 8に準拠（black実行済み）
- [ ] リンターエラーなし（ruff実行済み）
- [ ] 型チェックエラーなし（mypy実行済み）
- [ ] テストカバレッジ > 80%

#### ドキュメント
- [ ] SPECIFICATION.mdが完成
- [ ] README.mdが完成
- [ ] コードにdocstringがある
- [ ] 複雑なロジックにコメントがある

#### 実践的品質
- [ ] ログが適切に出力される
- [ ] エラーメッセージが分かりやすい
- [ ] 環境変数で設定を変更できる
- [ ] リソースが適切にクリーンアップされる

### 自動品質チェック

```bash
# Makefileを作成して一括実行
cat > Makefile << 'EOF'
.PHONY: quality
quality: format lint typecheck test

.PHONY: format
format:
	black src/ tests/
	ruff check src/ tests/ --fix

.PHONY: lint
lint:
	ruff check src/ tests/

.PHONY: typecheck
typecheck:
	mypy src/

.PHONY: test
test:
	pytest tests/ -v --cov=src --cov-report=term --cov-report=html

.PHONY: test-fast
test-fast:
	pytest tests/ -v -m "not slow"
EOF

# 実行
make quality
```

---

## トラブルシューティング

### よくある問題と解決方法

#### テストが失敗する

```bash
# 1. 詳細なエラーメッセージを確認
pytest tests/ -v -s

# 2. 特定のテストのみ実行
pytest tests/test_unit.py::TestClass::test_method -v

# 3. デバッグモードで実行
pytest tests/ --pdb
```

#### 依存関係の問題

```bash
# 仮想環境を再作成
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

#### パフォーマンスが悪い

```bash
# プロファイリング実行
python -m cProfile -o profile.stats src/{pattern_name}/main.py

# 結果を確認
python -m pstats profile.stats
```

#### メモリリーク

```bash
# メモリプロファイリング
pip install memory_profiler
python -m memory_profiler src/{pattern_name}/main.py
```

---

## 次のステップ

1. `.claude/claude.md` を読んで開発プロセスを理解
2. `progress/learning_log.md` で学習目標を確認
3. 最初のパターンを選んで実装開始！

**推奨開始パターン**:
- Chapter 4: `synchronous_pattern` - シンプルで理解しやすい
- Chapter 2: `iris_sklearn_svc` - 基礎的なMLパイプライン

---

## 参考資料

- [プロジェクトREADME](../README.md)
- [Claude Codeルール](../.claude/claude.md)
- [仕様書テンプレート](../templates/SPECIFICATION.template.md)
- [テストテンプレート](../templates/test_*.template.py)
