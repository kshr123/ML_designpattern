# 機械学習システムデザインパターン 学習プロジェクト

## 📁 プロジェクト構造

```
.
├── reference/              # 参考リポジトリ（クローン元）
│   └── ml-system-in-actions/
├── my_implementations/     # 自分で実装したコード
├── templates/              # テンプレートファイル
│   ├── SPECIFICATION.template.md
│   ├── pyproject.toml.template
│   └── test_*.template.py
├── docs/                   # ドキュメント
│   └── DEVELOPMENT_WORKFLOW.md
├── notes/                  # 学習ノート・メモ
└── progress/               # 進捗記録
    └── learning_log.md     # 学習進捗ログ
```

## 🎯 プロジェクトの目的

『AIエンジニアのための機械学習システムデザインパターン』の内容を学習し、
AI駆動開発でゼロから実装することで、実践的なスキルを習得する。

### 開発方法論

本プロジェクトでは実践に近い形で開発を進めます：

- **仕様駆動開発（SDD）**: まず仕様を明確化してから実装
- **テスト駆動開発（TDD）**: Red→Green→Refactorサイクル
- **段階的開発**: 小さなステップで確実に進める

詳細は [DEVELOPMENT_WORKFLOW.md](./docs/DEVELOPMENT_WORKFLOW.md) を参照してください。

## 📚 学習内容

1. **Chapter 2: Training** - モデル学習のパターン
2. **Chapter 3: Release** - モデルリリースのパターン
3. **Chapter 4: Serving** - 推論サービスのパターン
4. **Chapter 5: Operations** - 運用のパターン
5. **Chapter 6: Operation Management** - 運用管理のパターン

## 🔧 開発環境

- **Python**: 3.13以上（最新の安定版）
- **パッケージマネージャー**: uv
- **コンテナ**: Docker & Docker Compose

### セットアップ

#### uvのインストール

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# または Homebrew
brew install uv
```

#### Python 3.13のインストール

```bash
# uvでPython 3.13をインストール
uv python install 3.13
```

#### プロジェクトの初期化

```bash
# 新しいパターンを実装する場合
cd my_implementations/ch{N}__{pattern_name}

# pyproject.tomlをテンプレートからコピー
cp ../../templates/pyproject.toml.template pyproject.toml

# 仮想環境の作成
uv venv

# 仮想環境の有効化
source .venv/bin/activate  # macOS/Linux

# 依存関係のインストール
uv pip install -e ".[dev]"
```

## 🚀 使い方

### 新しいパターンを実装する

**詳細な手順は [DEVELOPMENT_WORKFLOW.md](./docs/DEVELOPMENT_WORKFLOW.md) を参照**

1. **理解**: 参考コードを読んで理解する
2. **仕様策定**: `SPECIFICATION.md` を作成
3. **テスト設計**: テストケースを作成（Red）
4. **実装**: テストを通す実装（Green）
5. **リファクタリング**: コードを改善（Refactor）
6. **検証**: 実際の動作確認
7. **振り返り**: 学習内容を記録

### テンプレートの活用

`templates/` フォルダに以下のテンプレートが用意されています：

- `SPECIFICATION.template.md` - 仕様書のテンプレート
- `pyproject.toml.template` - プロジェクト設定のテンプレート
- `test_unit.template.py` - ユニットテストのテンプレート
- `test_integration.template.py` - 統合テストのテンプレート
- `test_e2e.template.py` - E2Eテストのテンプレート

### 進捗を記録する
`progress/learning_log.md` に学習内容や気づきを記録

### 学習ノートを取る
`notes/` 配下に章ごとのノートやメモを作成

### 参考コードを確認する
`reference/` 配下の元のリポジトリを参照

## 📚 重要なドキュメント

- **[.claude/claude.md](./.claude/claude.md)** - プロジェクトルールとベストプラクティス（必読）
- **[progress/learning_log.md](./progress/learning_log.md)** - 学習進捗と詳細記録
- **[notes/](./notes/)** - 学習ガイド・技術ノート
  - [テストコード作成ガイド](./notes/test_writing_guide.md)
  - [uvパッケージマネージャーガイド](./notes/uv_package_manager_guide.md)
  - [Git & GitHub 初心者ガイド](./notes/git_github_beginner_guide.md)
  - [MCP設定完全ガイド](./notes/mcp_setup_guide.md)

## 📝 プロジェクト情報

- **開始日**: 2025-11-03
- **進捗状況**: [progress/learning_log.md](./progress/learning_log.md) を参照
- **完了パターン**: Model DB (Chapter 2)
