# 機械学習システムデザインパターン 学習プロジェクト

## 📁 プロジェクト構造

**フロー順に連番を付けて整理**

```
.
├── 01_reference/           # 参考リポジトリ（クローン元）
│   └── ml-system-in-actions/
├── 02_templates/           # テンプレートファイル
│   ├── SPECIFICATION.template.md
│   ├── pyproject.toml.template
│   └── test_*.template.py
├── 03_my_implementations/  # 自分で実装したコード
├── 04_notes/               # 学習ノート・メモ
├── 05_progress/            # 進捗記録
│   └── learning_log.md     # 学習進捗ログ
└── 06_docs/                # ドキュメント
    └── DEVELOPMENT_WORKFLOW.md
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
cd 03_my_implementations/chapter{N}__{category}/{NN}_{pattern_name}

# pyproject.tomlをテンプレートからコピー
cp ../../../02_templates/pyproject.toml.template pyproject.toml

# 仮想環境の作成
uv venv

# 仮想環境の有効化
source .venv/bin/activate  # macOS/Linux

# 依存関係のインストール
uv pip install -e ".[dev]"
```

## 🚀 使い方

### 新しいパターンを実装する

**詳細な手順は [DEVELOPMENT_WORKFLOW.md](./06_docs/DEVELOPMENT_WORKFLOW.md) を参照**

1. **理解**: 参考コードを読んで理解する
2. **仕様策定**: `SPECIFICATION.md` を作成
3. **テスト設計**: テストケースを作成（Red）
4. **実装**: テストを通す実装（Green）
5. **リファクタリング**: コードを改善（Refactor）
6. **検証**: 実際の動作確認
7. **振り返り**: 学習内容を記録

### テンプレートの活用

`02_templates/` フォルダに以下のテンプレートが用意されています：

- `SPECIFICATION.template.md` - 仕様書のテンプレート
- `pyproject.toml.template` - プロジェクト設定のテンプレート
- `test_unit.template.py` - ユニットテストのテンプレート
- `test_integration.template.py` - 統合テストのテンプレート
- `test_e2e.template.py` - E2Eテストのテンプレート

### 進捗を記録する
`05_progress/learning_log.md` に学習内容や気づきを記録

### 学習ノートを取る
`04_notes/` 配下に章ごとのノートやメモを作成

### 参考コードを確認する
`01_reference/` 配下の元のリポジトリを参照

## 📚 重要なドキュメント

- **[.claude/claude.md](./.claude/claude.md)** - プロジェクトルールとベストプラクティス（必読）
- **[05_progress/learning_log.md](./05_progress/learning_log.md)** - 学習進捗と詳細記録
- **[04_notes/](./04_notes/)** - 学習ガイド・技術ノート
  - [テストコード作成ガイド](./04_notes/test_writing_guide.md)
  - [uvパッケージマネージャーガイド](./04_notes/uv_package_manager_guide.md)
  - [Git & GitHub 初心者ガイド](./04_notes/git_github_beginner_guide.md)
  - [MCP設定完全ガイド](./04_notes/mcp_setup_guide.md)

## 📝 プロジェクト情報

- **開始日**: 2025-11-03
- **進捗状況**: [05_progress/learning_log.md](./05_progress/learning_log.md) を参照
- **完了パターン数**: 11 / 26 パターン（Chapter 2 完了、Chapter 3 完了、Chapter 4 進行中）
- **完了パターン**:
  - Model DB (Chapter 2) - 2025-11-04
  - Iris SVM Classifier + CI/CD (Chapter 2) - 2025-11-04
  - Iris Binary Classification + MLflow (Chapter 2) - 2025-11-05
  - Iris Random Forest + ONNX (Chapter 2) - 2025-11-05
  - Iris Outlier Detection (Chapter 2) - 2025-11-05
  - CIFAR-10 CNN + PyTorch + MLflow (Chapter 2) - 2025-11-05
  - Model-in-Image Pattern (Chapter 3) - 2025-11-06
  - Model-Load Pattern (Chapter 3) - 2025-11-13
  - Web Single Pattern (Chapter 4) - 2025-11-13
  - Synchronous Pattern (Chapter 4) - 2025-11-13
  - Asynchronous Pattern (Chapter 4) - 2025-11-13
