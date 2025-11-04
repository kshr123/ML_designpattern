# 推奨コマンド集

## プロジェクト開始時

### 新しいパターンを実装する場合

```bash
# 1. ディレクトリを作成
mkdir -p my_implementations/ch{N}__{pattern_name}
cd my_implementations/ch{N}__{pattern_name}

# 2. pyproject.tomlをテンプレートからコピー
cp ../../templates/pyproject.toml.template pyproject.toml

# 3. Pythonバージョンを指定
echo "3.13" > .python-version

# 4. 仮想環境の作成
uv venv

# 5. 仮想環境の有効化
source .venv/bin/activate  # macOS/Linux

# 6. 開発ツールのインストール
uv pip install -e ".[dev]"

# 7. ディレクトリ構造を作成
mkdir -p tests src/{pattern_name}
touch src/{pattern_name}/__init__.py
touch tests/__init__.py
```

## 開発中のコマンド

### コードフォーマット

```bash
# Blackでフォーマット
black src/ tests/

# フォーマットのチェックのみ（変更しない）
black --check src/ tests/
```

### リント（静的解析）

```bash
# Ruffでリント
ruff check src/ tests/

# 自動修正可能な問題を修正
ruff check --fix src/ tests/
```

### 型チェック

```bash
# mypyで型チェック
mypy src/

# より詳細な出力
mypy --show-error-codes src/
```

### テスト実行

```bash
# すべてのテストを実行
pytest tests/ -v

# カバレッジ付きで実行
pytest tests/ -v --cov=src --cov-report=html

# 特定のテストファイルのみ実行
pytest tests/test_unit.py -v

# 特定のテスト関数のみ実行
pytest tests/test_unit.py::test_function_name -v

# 失敗したテストのみ再実行
pytest tests/ --lf
```

### すべてのチェックを一度に実行

```bash
# フォーマット → リント → 型チェック → テスト
black src/ tests/ && ruff check src/ tests/ && mypy src/ && pytest tests/ -v --cov=src
```

## タスク完了後のコマンド

### コード品質チェックリスト

実装が完了したら、以下のコマンドを順に実行する:

```bash
# 1. フォーマット
black src/ tests/

# 2. リント
ruff check src/ tests/

# 3. 型チェック
mypy src/

# 4. テスト（カバレッジ付き）
pytest tests/ -v --cov=src --cov-report=html --cov-report=term
```

すべてがパスすることを確認してから、次のステップに進む。

## Git操作（MCP経由でも可能）

### 基本操作

```bash
# 変更をステージング
git add .

# コミット
git commit -m "feat: implement {pattern_name}"

# プッシュ
git push origin main
```

### ブランチ操作

```bash
# 新しいブランチを作成して切り替え
git checkout -b feature/{pattern_name}

# ブランチをプッシュ
git push -u origin feature/{pattern_name}
```

## Docker操作（必要に応じて）

```bash
# イメージをビルド
docker build -t ml-pattern-{name} .

# コンテナを起動
docker run -p 8000:8000 ml-pattern-{name}

# Docker Composeで起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# 停止
docker-compose down
```

## プロジェクト管理

### 進捗記録

```bash
# 学習ログを編集
vim progress/learning_log.md

# ノートを作成
vim notes/{pattern_name}_notes.md
```

## uvコマンド

### 依存関係管理

```bash
# パッケージを追加
uv pip install <package>

# パッケージを削除
uv pip uninstall <package>

# 依存関係をロック
uv pip freeze > requirements.txt

# pyproject.tomlから依存関係をインストール
uv pip install -e ".[dev]"
```

### Python管理

```bash
# 利用可能なPythonバージョンを確認
uv python list

# 特定のバージョンをインストール
uv python install 3.13

# 現在のPythonバージョンを確認
uv python --version
```

## ディレクトリ操作（macOS）

```bash
# ディレクトリツリーを表示（2階層）
tree -L 2 -a

# ファイルを検索
find . -name "*.py" -type f

# パターンマッチでファイルを検索
fd "test_.*\.py"  # fd（高速なfindの代替）がインストールされている場合
```

## システム情報

```bash
# Pythonバージョン確認
python --version

# uvバージョン確認
uv --version

# Dockerバージョン確認
docker --version

# ディスク使用量確認
du -sh .
```

## トラブルシューティング

```bash
# 仮想環境を削除して再作成
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# キャッシュをクリア
rm -rf __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache
rm -rf .mypy_cache

# カバレッジレポートを削除
rm -rf htmlcov .coverage
```

## ショートカット（Makefile作成を推奨）

プロジェクトルートに`Makefile`を作成すると便利:

```makefile
.PHONY: format lint typecheck test check clean

format:
	black src/ tests/

lint:
	ruff check src/ tests/

typecheck:
	mypy src/

test:
	pytest tests/ -v --cov=src --cov-report=html

check: format lint typecheck test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage
```

使い方:
```bash
make format    # フォーマット
make lint      # リント
make typecheck # 型チェック
make test      # テスト
make check     # すべてのチェック
make clean     # キャッシュクリア
```
