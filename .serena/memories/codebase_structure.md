# コードベース構造

## ルートディレクトリ構成

```
.
├── .claude/                    # Claude Code設定
│   ├── CLAUDE.md              # プロジェクトルールとベストプラクティス
│   └── settings.local.json    # ローカル設定（MCP有効化等）
├── .serena/                    # Serenaのメモリファイル（自動生成）
├── reference/                  # 参考リポジトリ（読み取り専用）
│   ├── chapter2_training/
│   ├── chapter3_release_patterns/
│   ├── chapter4_serving_patterns/
│   ├── chapter5_operations/
│   └── chapter6_operation_management/
├── my_implementations/         # 自分で実装するコード（書き込み可）
│   └── ch{N}__{pattern_name}/  # パターンごとのディレクトリ
├── templates/                  # テンプレートファイル
│   ├── SPECIFICATION.template.md
│   ├── pyproject.toml.template
│   ├── test_unit.template.py
│   ├── test_integration.template.py
│   └── test_e2e.template.py
├── notes/                      # 学習ノート・メモ（書き込み可）
├── progress/                   # 進捗管理（書き込み可）
│   └── learning_log.md
├── docs/                       # プロジェクトドキュメント
│   ├── DEVELOPMENT_WORKFLOW.md
│   └── MCP_SETUP.md
├── .mcp.json                   # MCP設定（gitignoreされている）
├── .mcp.json.example           # MCP設定の例
├── .gitignore                  # Git除外設定
├── README.md                   # プロジェクトの説明
├── QUICKSTART.md               # クイックスタートガイド
└── PROJECT_STATUS.md           # プロジェクト状況
```

---

## ディレクトリの役割

### `.claude/`
Claude Codeの設定とプロジェクトルールを管理。

- **CLAUDE.md**: 最重要ファイル。開発方法論、コーディング規約、MCPの設定方法など
- **settings.local.json**: MCP有効化設定、パーミッション設定

### `.serena/`
Serena MCPが生成するメモリファイル。プロジェクトに関する知識を保存。

**重要**: このディレクトリは自動生成され、手動で編集する必要はない。

### `reference/`
元の参考リポジトリ（`ml-system-in-actions`）。**読み取り専用**。

- 参考コードを分析し、設計を学ぶ
- コピペはせず、理解してから自分で実装する
- 各章（chapter）ごとにディレクトリが分かれている

**ルール**: このディレクトリ内のファイルは変更しない。

### `my_implementations/`
ゼロから実装するコードを配置する。**書き込み可**。

**命名規則**: `ch{N}__{pattern_name}/`
- 例: `ch4__synchronous_pattern/`, `ch4__async_pattern/`

**標準的なディレクトリ構成**:
```
ch{N}__{pattern_name}/
├── SPECIFICATION.md           # 仕様書
├── README.md                  # 実装の説明
├── pyproject.toml             # プロジェクト設定
├── .python-version            # Pythonバージョン指定
├── src/
│   └── {pattern_name}/
│       ├── __init__.py
│       ├── main.py            # エントリーポイント
│       └── ...                # その他のモジュール
└── tests/
    ├── __init__.py
    ├── test_unit.py           # ユニットテスト
    ├── test_integration.py    # 統合テスト
    └── test_e2e.py            # E2Eテスト（必要に応じて）
```

### `templates/`
新しいパターンを実装する際に使用するテンプレート。

- **SPECIFICATION.template.md**: 仕様書のテンプレート
- **pyproject.toml.template**: プロジェクト設定のテンプレート
- **test_unit.template.py**: ユニットテストのテンプレート
- **test_integration.template.py**: 統合テストのテンプレート
- **test_e2e.template.py**: E2Eテストのテンプレート

### `notes/`
学習ノート・メモを自由に作成。**書き込み可**。

**推奨命名規則**: `{pattern_name}_notes.md`
- 各パターンごとに学んだことをまとめる
- アーキテクチャ図や設計メモを保存

### `progress/`
進捗管理ファイルを配置。**書き込み可**。

- **learning_log.md**: 学習進捗ログ（常に最新に保つ）
  - 各パターンの学習開始・完了日時
  - 学んだこと、疑問点、改善点
  - 次回への持ち越し事項

### `docs/`
プロジェクト全体のドキュメント。

- **DEVELOPMENT_WORKFLOW.md**: 開発ワークフローの詳細（仕様駆動開発 + テスト駆動開発）
- **MCP_SETUP.md**: MCPサーバーの設定ガイド

---

## 参考リポジトリの構成

`reference/` 内の各章の構成:

### Chapter 2: Training（モデル学習）
モデルの学習に関するパターン。

### Chapter 3: Release Patterns（モデルリリース）
モデルをリリースする際のパターン。

### Chapter 4: Serving Patterns（推論サービス）
推論サービスの実装パターン。**最重要**。

主要なパターン:
- Synchronous Pattern: 同期推論
- Asynchronous Pattern: 非同期推論
- Batch Pattern: バッチ推論
- Web Single Pattern: Webシングルパターン
- など

### Chapter 5: Operations（運用）
運用に関するパターン。

### Chapter 6: Operation Management（運用管理）
高度な運用管理に関するパターン。

---

## ファイル命名規則

### Pythonファイル

- **モジュール**: `snake_case.py`
- **テストファイル**: `test_*.py`
- **パッケージ**: `__init__.py`

### ドキュメント

- **仕様書**: `SPECIFICATION.md`（大文字）
- **README**: `README.md`（大文字）
- **ノート**: `{pattern_name}_notes.md`（小文字）

### 設定ファイル

- **Python設定**: `pyproject.toml`
- **Docker設定**: `Dockerfile`, `docker-compose.yml`
- **環境変数**: `.env`, `.env.example`

---

## 自動生成ファイル（gitignoreされる）

以下のファイルは自動生成され、Gitにコミットされない:

- `__pycache__/` - Pythonのバイトコードキャッシュ
- `.venv/` - 仮想環境
- `uv.lock` - uvの依存関係ロックファイル
- `.pytest_cache/` - pytestのキャッシュ
- `.mypy_cache/` - mypyのキャッシュ
- `htmlcov/` - カバレッジレポート
- `.coverage` - カバレッジデータ
- `*.log` - ログファイル

---

## 機密情報の管理

以下のファイルは**絶対にGitにコミットしない**:

- `.env` - 環境変数（APIキー等）
- `*.pem`, `*.key` - 秘密鍵
- `credentials.json` - 認証情報
- `.mcp.json` - MCPトークン

`.gitignore`でこれらは除外設定済み。

---

## 開発時の注意点

### ディレクトリの読み取り/書き込み権限

| ディレクトリ | 読み取り | 書き込み | 用途 |
|--------------|----------|----------|------|
| `reference/` | ✅ | ❌ | 参考コードの参照のみ |
| `my_implementations/` | ✅ | ✅ | 自分のコードを実装 |
| `notes/` | ✅ | ✅ | 学習ノートを作成 |
| `progress/` | ✅ | ✅ | 進捗を記録 |
| `templates/` | ✅ | ❌ | テンプレートとして使用 |
| `.claude/` | ✅ | ⚠️ | 必要に応じて更新 |

### 新しいパターンを実装する際の流れ

1. `templates/` からテンプレートをコピー
2. `my_implementations/ch{N}__{pattern_name}/` に配置
3. 仕様書（SPECIFICATION.md）を作成
4. テストを書く（TDD）
5. 実装する
6. `progress/learning_log.md` に記録

詳細は `development_workflow.md` を参照。

---

## よく使うコマンド

### ディレクトリ構造の確認

```bash
# ルートディレクトリの構造を確認（2階層）
tree -L 2 -a

# 特定のディレクトリの詳細を確認
tree -L 3 my_implementations/
```

### ファイルの検索

```bash
# Pythonファイルを検索
find . -name "*.py" -type f

# テストファイルを検索
find . -name "test_*.py" -type f

# 特定のパターンを含むファイルを検索
grep -r "def test_" tests/
```

### プロジェクトの初期化

新しいパターンを実装する際:

```bash
cd my_implementations
mkdir -p ch{N}__{pattern_name}
cd ch{N}__{pattern_name}
cp ../../templates/pyproject.toml.template pyproject.toml
mkdir -p src/{pattern_name} tests
touch src/{pattern_name}/__init__.py tests/__init__.py
```

---

## まとめ

- **reference/**: 読むだけ、変更しない
- **my_implementations/**: 自分のコードを実装
- **templates/**: コピーして使う
- **notes/**: 学習ノートを自由に書く
- **progress/**: 進捗を記録
- **.claude/**: プロジェクトルールを確認（CLAUDE.md）
