# Iris SVM Classification with scikit-learn

## 概要

このプロジェクトはIrisデータセットを使ったSVM（サポートベクターマシン）分類の実装です。
機械学習システムデザインパターンの学習の一環として、TDD（テスト駆動開発）で実装しています。

## ディレクトリ構造

```
iris_sklearn_svc/
├── src/
│   └── iris_sklearn_svc/
│       ├── __init__.py
│       ├── data_loader.py      # データ読み込み
│       ├── model.py             # パイプライン定義
│       ├── trainer.py           # 学習ロジック（予定）
│       ├── evaluator.py         # 評価ロジック（予定）
│       ├── exporter.py          # ONNX変換（予定）
│       └── train.py             # メインスクリプト（予定）
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py     # data_loaderのテスト
│   └── test_model.py            # modelのテスト
├── test_results/                # TDD Red/Greenの記録
│   ├── data_loader_red.txt     # data_loader失敗時
│   ├── data_loader_green.txt   # data_loader成功時
│   ├── model_red.txt            # model失敗時
│   └── model_green.txt          # model成功時
├── htmlcov/                     # カバレッジレポート（Git管理外）
├── SPECIFICATION.md             # 詳細仕様書
├── pyproject.toml               # プロジェクト設定
└── README.md                    # このファイル
```

## 技術スタック

- **Python**: 3.13
- **機械学習**: scikit-learn 1.5+
- **実験管理**: MLflow 2.18+（予定）
- **モデル変換**: skl2onnx 1.18+, onnx 1.17+（予定）
- **テスト**: pytest 8.4+, pytest-cov 7.0+
- **パッケージ管理**: uv

## セットアップ

### 1. 仮想環境の作成

```bash
uv venv
source .venv/bin/activate  # macOS/Linux
```

### 2. 依存関係のインストール

```bash
# プロジェクトをeditable modeでインストール
uv pip install -e .

# 開発ツールのインストール
uv pip install pytest pytest-cov black ruff mypy
```

## 実装済みコンポーネント

### ✅ data_loader.py

Irisデータセットを読み込み、train/testに分割する機能。

```python
from iris_sklearn_svc.data_loader import get_data

x_train, x_test, y_train, y_test = get_data(test_size=0.3, random_state=42)
```

**テスト結果**:
- 7テストケース全て成功
- コードカバレッジ: 100%
- 詳細: `test_results/data_loader_green.txt`

### ✅ model.py

scikit-learn パイプライン（StandardScaler + SVC）を構築する機能。

```python
from iris_sklearn_svc.model import build_pipeline

pipeline = build_pipeline()
# Pipeline: StandardScaler -> SVC(kernel='rbf', probability=True, random_state=42)
```

**テスト結果**:
- 8テストケース全て成功
- コードカバレッジ: 100%
- 詳細: `test_results/model_green.txt`

## テストの実行

### 全テストの実行

```bash
pytest tests/ -v
```

### カバレッジレポート付き実行

```bash
pytest tests/ -v --cov=src --cov-report=html
```

HTMLレポートは `htmlcov/index.html` で確認できます。

### 個別モジュールのテスト

```bash
# data_loaderのみ
pytest tests/test_data_loader.py -v

# modelのみ
pytest tests/test_model.py -v
```

## TDD（テスト駆動開発）の記録

このプロジェクトはTDDで開発されており、各モジュールのRed→Green進捗が `test_results/` ディレクトリに記録されています。

### Red Phase（失敗フェーズ）
実装前にテストを書き、期待通りに失敗することを確認：
- `test_results/data_loader_red.txt`
- `test_results/model_red.txt`

### Green Phase（成功フェーズ）
実装後に全テストが通ることを確認：
- `test_results/data_loader_green.txt`
- `test_results/model_green.txt`

各ファイルにはヘッダー、pytest出力、分析セクションが含まれており、学習記録として機能します。

## 今後の実装予定

- [ ] `trainer.py` - モデル学習機能
- [ ] `evaluator.py` - モデル評価機能（accuracy, precision, recall）
- [ ] `exporter.py` - ONNXフォーマット変換
- [ ] `train.py` - メインスクリプト（MLflow連携）
- [ ] 統合テスト
- [ ] E2Eテスト

## 学んだこと

### TDDのメリット
1. **テストファースト**: 要件を先に明確化できる
2. **リファクタリング安心**: テストがあるので大胆に改善できる
3. **ドキュメントとしても機能**: テストが使用例になる
4. **Red→Greenの記録**: 学習プロセスを可視化できる

### scikit-learn Pipeline
- 前処理（StandardScaler）とモデル（SVC）を統一的に扱える
- fit/predictが一度の呼び出しで完結
- 再現性の確保（random_state）が重要

## 参考

- [SPECIFICATION.md](./SPECIFICATION.md) - 詳細な仕様書
- [元の実装](../../../reference/chapter2_training/iris_sklearn_svc/) - 参考コード（読み取り専用）
- [プロジェクトルール](../../../.claude/claude.md) - 開発プロセス

---

開発者: kshr123
最終更新: 2025-11-04
