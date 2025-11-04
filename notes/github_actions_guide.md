# GitHub Actions 完全ガイド

最終更新: 2025-11-04

## 📚 目次

1. [GitHub Actionsとは](#github-actionsとは)
2. [基本概念と用語](#基本概念と用語)
3. [ワークフローの構造](#ワークフローの構造)
4. [実際の使い方](#実際の使い方)
5. [トラブルシューティング](#トラブルシューティング)
6. [ベストプラクティス](#ベストプラクティス)
7. [実践例: iris_sklearn_svc](#実践例-iris_sklearn_svc)

---

## GitHub Actionsとは

**GitHub上でコードの自動処理を実行できるCI/CD（継続的インテグレーション/デリバリー）プラットフォーム**

### 簡単に言うと

```
コードをpushしたら、自動的にテストやビルドを実行してくれる仕組み
```

### できること

- ✅ コードをpushしたときに自動テスト
- ✅ Pull Request作成時にコード品質チェック
- ✅ 自動ビルドとデプロイ
- ✅ 定期実行（毎日、毎週など）
- ✅ 手動実行

### メリット

1. **品質保証**: 人間のミスを防ぐ
2. **時間節約**: 自動化で開発に集中できる
3. **統一性**: 全員が同じ環境でテスト
4. **透明性**: 実行結果が見える

---

## 基本概念と用語

### 1. ワークフロー (Workflow) 📋

**自動化の設計図全体**

- YAMLファイルで定義
- `.github/workflows/` ディレクトリに配置
- 1つのリポジトリに複数のワークフローを持てる

**例え**: 料理のレシピ本全体

```yaml
# .github/workflows/test.yml
name: Tests
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest tests/
```

### 2. イベント (Event) 🎯

**ワークフローを起動するきっかけ**

**よく使うイベント**:
```yaml
on: push                    # コードをpushしたとき
on: pull_request           # PRを作成したとき
on: schedule               # 定期実行（cron形式）
on: workflow_dispatch      # 手動実行
```

**例え**: 料理を始めるタイミング

### 3. ジョブ (Job) 🏗️

**1つのまとまった作業単位**

- 複数のジョブは**並列実行**される（デフォルト）
- 依存関係を設定することも可能

**例え**: 料理のコース（前菜、メイン、デザート）

```yaml
jobs:
  test:           # ジョブ1: テスト
    runs-on: ubuntu-latest
    steps: [...]

  build:          # ジョブ2: ビルド（testと並列）
    runs-on: ubuntu-latest
    steps: [...]

  deploy:         # ジョブ3: デプロイ（testに依存）
    needs: test
    runs-on: ubuntu-latest
    steps: [...]
```

### 4. ステップ (Step) 📝

**ジョブの中の1つ1つの作業**

- ステップは**順番に実行**される（上から下へ）
- 各ステップは成功しないと次に進まない

**例え**: レシピの手順

```yaml
steps:
  - name: コードをチェックアウト    # ステップ1
    uses: actions/checkout@v4

  - name: Pythonをセットアップ      # ステップ2
    uses: actions/setup-python@v5

  - name: テストを実行              # ステップ3
    run: pytest tests/
```

### 5. アクション (Action) 🔧

**再利用可能な部品**

2種類ある：

**a) 既存のアクション（uses）**:
```yaml
- uses: actions/checkout@v4           # コードをダウンロード
- uses: actions/setup-python@v5       # Pythonをインストール
- uses: actions/upload-artifact@v4    # ファイルを保存
```

**b) コマンド実行（run）**:
```yaml
- run: pytest tests/
- run: black src/
- run: |
    echo "複数行の"
    echo "コマンドも実行できる"
```

**例え**: 調理器具（包丁、フライパンなど）

### 6. ランナー (Runner) 🖥️

**実際に作業を実行するコンピューター**

GitHubが提供する3種類：

```yaml
runs-on: ubuntu-latest    # Linuxマシン（最も一般的）
runs-on: macos-latest     # macOSマシン
runs-on: windows-latest   # Windowsマシン
```

**例え**: 厨房（料理を作る場所）

---

## ワークフローの構造

### 基本構造

```yaml
name: ワークフロー名                    # ①名前（必須ではないが推奨）

on:                                    # ②イベント（いつ実行？）
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:                                  # ③ジョブ（何をする？）
  job-name:                            # ジョブ名
    runs-on: ubuntu-latest             # ④ランナー

    steps:                             # ⑤ステップ（具体的な作業）
      - name: ステップ1                 # ステップ名（オプション）
        uses: actions/checkout@v4      # アクション

      - name: ステップ2
        run: echo "Hello World"        # コマンド
```

### 詳細な構造

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
    paths:                             # パスフィルター
      - 'src/**'
      - 'tests/**'
  pull_request:
    branches: [ main ]
  schedule:                            # 定期実行
    - cron: '0 0 * * *'                # 毎日午前0時
  workflow_dispatch:                   # 手動実行

jobs:
  test:
    runs-on: ubuntu-latest

    # デフォルト設定
    defaults:
      run:
        working-directory: ./my-project
        shell: bash

    # 環境変数
    env:
      NODE_ENV: test
      API_KEY: ${{ secrets.API_KEY }}

    # マトリックス戦略（複数環境でテスト）
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
        os: [ubuntu-latest, macos-latest]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/

      - name: Upload results
        if: always()                   # 常に実行
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: test-results/
```

---

## 実際の使い方

### 画面の見方

#### 1. Actionsタブを開く

```
GitHubリポジトリ → 上部メニューの「Actions」をクリック
```

#### 2. Actionsページの構成

```
┌────────────────────────────────────────────────────────┐
│ GitHub Actions                                         │
├─────────────────┬──────────────────────────────────────┤
│ 左: ワークフロー │ 右: 実行履歴                         │
│ 一覧            │                                      │
│                 │                                      │
│ All workflows   │ 🔄 Tests #42                         │
│                 │    Fix bug in data loader            │
│ Tests           │    main • abc123 • 2 min ago         │
│ Code Quality    │                                      │
│ Deploy          │ ✅ Tests #41                         │
│                 │    Add new feature                   │
│                 │    main • def456 • 1 hour ago        │
└─────────────────┴──────────────────────────────────────┘
```

#### 3. 実行状態のアイコン

- 🔄 **黄色の回転** = 実行中（In progress）
- ✅ **緑のチェック** = 成功（Success）
- ❌ **赤いバツ** = 失敗（Failure）
- ⚪ **灰色の丸** = キャンセル（Cancelled）

#### 4. ワークフローの詳細を見る

```
「Tests」をクリック
↓
┌────────────────────────────────────────────────────────┐
│ Tests #42                                              │
│ Fix bug in data loader                                 │
├────────────────────────────────────────────────────────┤
│ Jobs (3)                  │ ログエリア                 │
│                           │                            │
│ ✅ test (ubuntu, 3.11)    │ > Set up job              │
│ ✅ test (ubuntu, 3.12)    │ > Run actions/checkout    │
│ 🔄 test (ubuntu, 3.13)    │ > Set up Python 3.13      │
│                           │ > Install dependencies    │
│                           │ > Run tests               │
│                           │   52 passed in 2.16s ✅   │
└────────────────────────────────────────────────────────┘
```

#### 5. 個別ジョブの詳細

```
左側のジョブをクリック
↓
┌────────────────────────────────────────────────────────┐
│ test (ubuntu-latest, 3.13)                             │
├────────────────────────────────────────────────────────┤
│ ▼ Set up job                           0s              │
│ ▼ Run actions/checkout@v4              1s              │
│ ▼ Set up Python 3.13                   5s              │
│ ▼ Install dependencies                15s              │
│ ▶ Run tests                            2s  ← クリック！│
│   ============================= test session starts    │
│   collected 52 items                                   │
│   tests/test_data_loader.py::test... PASSED           │
│   ...                                                  │
│   ============================== 52 passed in 2.16s    │
│ ▼ Upload coverage                      3s              │
│ ▼ Complete job                         0s              │
└────────────────────────────────────────────────────────┘
```

### コミットページでの確認

コミット詳細ページでもワークフローの結果が表示される：

```
Commit: Fix bug in data loader
abc123

✅ All checks have passed
   ✅ Tests / test (ubuntu-latest, 3.13)
   ✅ Code Quality / lint
   ✅ Coverage Report / coverage

[View details →]
```

---

## トラブルシューティング

### よくあるエラーと解決方法

#### 1. ワークフローが実行されない

**症状**: Actionsページに何も表示されない

**原因と解決**:
```yaml
# ❌ 間違い: サブディレクトリに配置
my_project/.github/workflows/test.yml

# ✅ 正しい: リポジトリルートに配置
.github/workflows/test.yml
```

**確認方法**:
```bash
# ワークフローファイルの場所を確認
ls -la .github/workflows/

# YAMLの構文チェック
python -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))"
```

#### 2. 依存関係のインストールエラー

**症状**: `No solution found when resolving dependencies`

**原因**: Pythonバージョンとパッケージの互換性

**解決**:
```yaml
# pyproject.tomlの要件を確認
requires-python = ">=3.13"

# ワークフローのPythonバージョンを一致させる
strategy:
  matrix:
    python-version: ["3.13"]  # 3.11, 3.12を削除

# プレリリース版を防ぐ
- uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}
    allow-prereleases: false
```

#### 3. working-directory が機能しない

**症状**: `No such file or directory`

**原因**: パスが間違っている、またはチェックアウトされていない

**解決**:
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: my_implementations/chapter2_training/iris_sklearn_svc

    steps:
      # 必須: 最初にチェックアウト
      - uses: actions/checkout@v4

      # working-directoryが適用される
      - run: ls -la  # このディレクトリの内容が表示される
```

#### 4. パスフィルターが効かない

**症状**: 関係ないファイルの変更でもワークフローが実行される

**解決**:
```yaml
on:
  push:
    paths:
      - 'my_implementations/chapter2_training/iris_sklearn_svc/**'
      - '.github/workflows/test.yml'  # ワークフロー自身も含める
    paths-ignore:  # 除外パス
      - '**.md'
      - 'docs/**'
```

#### 5. シークレットが使えない

**症状**: `${{ secrets.MY_TOKEN }}` が空

**解決**:
1. リポジトリ設定 → Secrets and variables → Actions
2. 「New repository secret」をクリック
3. 名前と値を設定（例: `CODECOV_TOKEN`）

```yaml
# 使い方
- name: Upload to Codecov
  env:
    CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
  run: codecov
```

---

## ベストプラクティス

### 1. ワークフローの分割

```
❌ 1つの巨大なワークフロー
.github/workflows/
└── all.yml  (テスト + リント + ビルド + デプロイ)

✅ 複数の小さなワークフロー
.github/workflows/
├── test.yml      # テスト
├── lint.yml      # コード品質
├── build.yml     # ビルド
└── deploy.yml    # デプロイ
```

**理由**:
- 失敗箇所が明確
- 再実行が速い
- 並列実行で全体が速くなる

### 2. マトリックス戦略の活用

```yaml
# 複数環境でテスト
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ["3.11", "3.12", "3.13"]
    # 3 × 3 = 9ジョブが並列実行される
```

**ただし**: 必要最小限に
- コストを考慮（無料枠: 2000分/月）
- 実行時間を考慮

### 3. キャッシュの活用

```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

**効果**: 依存関係のインストール時間を大幅短縮

### 4. 条件付き実行

```yaml
# PRの場合のみ実行
- name: Comment on PR
  if: github.event_name == 'pull_request'
  run: echo "PR detected"

# 失敗しても続行
- name: Upload logs
  if: failure()
  uses: actions/upload-artifact@v4

# 常に実行
- name: Cleanup
  if: always()
  run: rm -rf temp/
```

### 5. セキュリティ

```yaml
# ❌ 危険: シークレットをログに出力
- run: echo ${{ secrets.API_KEY }}

# ✅ 安全: 環境変数として使用
- name: Use secret
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: |
    # API_KEY を使用（ログには表示されない）
    curl -H "Authorization: Bearer $API_KEY" ...
```

### 6. タイムアウト設定

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 30  # 30分でタイムアウト

    steps:
      - name: Run tests
        timeout-minutes: 10  # このステップは10分でタイムアウト
        run: pytest tests/
```

### 7. 並行実行の制御

```yaml
# 同じブランチで複数のワークフローが走らないようにする
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # 古い実行をキャンセル
```

---

## 実践例: iris_sklearn_svc

このプロジェクトで実装した3つのワークフロー：

### 1. Tests ワークフロー

**ファイル**: `.github/workflows/test.yml`

**目的**: コードの動作確認

```yaml
name: Tests - iris_sklearn_svc

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'my_implementations/chapter2_training/iris_sklearn_svc/**'
      - '.github/workflows/test.yml'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'my_implementations/chapter2_training/iris_sklearn_svc/**'
      - '.github/workflows/test.yml'

jobs:
  test:
    runs-on: ${{ matrix.os }}
    defaults:
      run:
        working-directory: my_implementations/chapter2_training/iris_sklearn_svc

    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          allow-prereleases: false

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH

      - name: Create virtual environment
        run: uv venv

      - name: Install dependencies
        run: |
          source .venv/bin/activate
          uv pip install -e ".[dev]"

      - name: Run unit tests
        run: |
          source .venv/bin/activate
          pytest tests/ -v --cov=src/iris_sklearn_svc --cov-report=xml --cov-report=term

      - name: Upload coverage reports to Codecov
        if: matrix.os == 'ubuntu-latest'
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
          token: ${{ secrets.CODECOV_TOKEN }}
```

**ポイント**:
- ✅ パスフィルターで必要なときだけ実行
- ✅ working-directory でサブプロジェクトに対応
- ✅ マトリックスで Ubuntu と macOS をテスト
- ✅ uv で高速なパッケージ管理
- ✅ Codecov にカバレッジをアップロード

### 2. Code Quality ワークフロー

**ファイル**: `.github/workflows/lint.yml`

**目的**: コード品質チェック

```yaml
name: Code Quality - iris_sklearn_svc

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'my_implementations/chapter2_training/iris_sklearn_svc/**'
      - '.github/workflows/lint.yml'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'my_implementations/chapter2_training/iris_sklearn_svc/**'
      - '.github/workflows/lint.yml'

jobs:
  lint:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: my_implementations/chapter2_training/iris_sklearn_svc

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH

      - name: Create virtual environment
        run: uv venv

      - name: Install dependencies
        run: |
          source .venv/bin/activate
          uv pip install -e ".[dev]"

      - name: Run black (code formatting check)
        run: |
          source .venv/bin/activate
          black --check src/ tests/

      - name: Run ruff (linting)
        run: |
          source .venv/bin/activate
          ruff check src/ tests/

      - name: Run mypy (type checking)
        run: |
          source .venv/bin/activate
          mypy src/
```

**ポイント**:
- ✅ black でフォーマットチェック
- ✅ ruff でリンティング
- ✅ mypy で型チェック
- ✅ 3つのツールを順番に実行

### 3. Coverage Report ワークフロー

**ファイル**: `.github/workflows/coverage.yml`

**目的**: カバレッジレポート生成

```yaml
name: Coverage Report - iris_sklearn_svc

on:
  push:
    branches: [ main ]
    paths:
      - 'my_implementations/chapter2_training/iris_sklearn_svc/**'
      - '.github/workflows/coverage.yml'
  pull_request:
    branches: [ main ]
    paths:
      - 'my_implementations/chapter2_training/iris_sklearn_svc/**'
      - '.github/workflows/coverage.yml'

jobs:
  coverage:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: my_implementations/chapter2_training/iris_sklearn_svc

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH

      - name: Create virtual environment
        run: uv venv

      - name: Install dependencies
        run: |
          source .venv/bin/activate
          uv pip install -e ".[dev]"

      - name: Run tests with coverage
        run: |
          source .venv/bin/activate
          pytest tests/ -v --cov=src/iris_sklearn_svc --cov-report=html --cov-report=term --cov-report=xml

      - name: Upload coverage report as artifact
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: my_implementations/chapter2_training/iris_sklearn_svc/htmlcov/

      - name: Comment coverage on PR
        if: github.event_name == 'pull_request'
        uses: py-cov-action/python-coverage-comment-action@v3
        with:
          GITHUB_TOKEN: ${{ github.token }}
          MINIMUM_GREEN: 80
          MINIMUM_ORANGE: 60
```

**ポイント**:
- ✅ HTMLレポートを生成
- ✅ アーティファクトとして保存（ダウンロード可能）
- ✅ PRに自動でカバレッジをコメント

---

## 学習のポイント

### 段階的に理解する

1. **まず基本を**: 1つのジョブ、1つのステップから
2. **徐々に拡張**: マトリックス、複数ジョブ
3. **実践で学ぶ**: 実際に動かしてエラーを解決

### 理解を深める質問

- ❓ なぜこのステップは失敗したのか？
- ❓ このジョブは並列実行できるか？
- ❓ このワークフローは必要最小限か？

### デバッグ方法

```yaml
# ログ出力を追加
- name: Debug
  run: |
    echo "Working directory: $(pwd)"
    echo "Files: $(ls -la)"
    echo "Python version: $(python --version)"
    echo "Environment: ${{ toJSON(env) }}"
```

---

## 参考リンク

### 公式ドキュメント
- [GitHub Actions Documentation](https://docs.github.com/ja/actions)
- [Workflow syntax](https://docs.github.com/ja/actions/using-workflows/workflow-syntax-for-github-actions)
- [Events that trigger workflows](https://docs.github.com/ja/actions/using-workflows/events-that-trigger-workflows)

### よく使うアクション
- [actions/checkout](https://github.com/actions/checkout) - リポジトリをチェックアウト
- [actions/setup-python](https://github.com/actions/setup-python) - Python環境セットアップ
- [actions/cache](https://github.com/actions/cache) - 依存関係のキャッシュ
- [actions/upload-artifact](https://github.com/actions/upload-artifact) - ファイルの保存
- [codecov/codecov-action](https://github.com/codecov/codecov-action) - カバレッジアップロード

### Marketplace
- [GitHub Marketplace - Actions](https://github.com/marketplace?type=actions)

---

## まとめ

### GitHub Actionsの本質

```
コードの品質を自動的に保証する仕組み
= 開発者の時間を節約し、バグを減らす
```

### 重要なポイント

1. **ワークフローはリポジトリルートに配置** (`.github/workflows/`)
2. **YAML構文に注意** （インデントが重要）
3. **パスフィルターで効率化** （必要なときだけ実行）
4. **エラーログを読む習慣** （問題解決力が上がる）
5. **小さく始めて徐々に拡張** （一度に全部やろうとしない）

### 次のステップ

- [ ] 他のプロジェクトにもワークフローを追加
- [ ] カスタムアクションを作成
- [ ] より高度な自動化を実装
- [ ] セルフホストランナーを検討

---

**作成日**: 2025-11-04
**最終更新**: 2025-11-04
**プロジェクト**: ML_designpattern/iris_sklearn_svc
