# 技術スタック

## プログラミング言語

- **Python**: 3.13以上（最新の安定版を使用）
- **型ヒント**: 可能な限り使用する（mypyでチェック）

## パッケージマネージャー

- **uv**: 高速・モダンなPythonパッケージマネージャー
  - 仮想環境管理
  - 依存関係管理
  - Pythonバージョン管理

### uvのインストール

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# または Homebrew
brew install uv
```

### uvの基本的な使い方

```bash
# Python 3.13のインストール
uv python install 3.13

# 仮想環境の作成
uv venv

# 仮想環境の有効化
source .venv/bin/activate  # macOS/Linux

# 依存関係のインストール
uv pip install -e ".[dev]"

# パッケージの追加
uv pip install <package>
```

## コア依存関係

標準的な依存関係（`pyproject.toml`より）:

### 必須
- `numpy>=2.0.0`
- `scikit-learn>=1.5.0`

### オプション（用途に応じて）
- **Deep Learning**: `torch>=2.3.0`, `tensorflow>=2.16.0`
- **Web Framework**: `fastapi>=0.111.0`, `uvicorn[standard]>=0.30.0`
- **Data Processing**: `pandas>=2.2.0`, `pillow>=10.3.0`
- **Utilities**: `pydantic>=2.7.0`, `python-dotenv>=1.0.0`

## 開発ツール

プロジェクトの`[project.optional-dependencies]`セクションで定義:

- **Testing**: `pytest>=8.2.0`, `pytest-cov>=5.0.0`
- **Formatting**: `black>=24.4.0`
- **Linting**: `ruff>=0.4.0`
- **Type Checking**: `mypy>=1.10.0`

## コンテナ

- **Docker**: コンテナ化
- **Docker Compose**: マルチコンテナアプリケーション

## プロジェクト管理

- **Git**: バージョン管理
- **GitHub**: リモートリポジトリ（MCP経由でアクセス可能）
- **Notion**: ドキュメント管理（MCP経由でアクセス可能）

## MCP (Model Context Protocol) サーバー

プロジェクトには以下のMCPサーバーが設定されています:

1. **GitHub MCP**: リポジトリ操作、Issue/PR管理
2. **Notion MCP**: Notionページ・データベース操作
3. **Serena MCP**: 高度なコード分析・編集（シンボリック検索、リファクタリング等）

## OS環境

- **システム**: macOS (Darwin)
- **Shellコマンド**: BSD系のコマンド（GNU Linuxとは一部異なる）
