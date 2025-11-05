# Iris Classification with Random Forest

## 概要

このプロジェクトは、Irisデータセットを使用したランダムフォレスト分類器の実装です。
MLflowによる実験管理とONNX形式でのモデルエクスポートを含みます。

## 主な機能

- ランダムフォレスト分類器による3クラス分類（Setosa, Versicolor, Virginica）
- StandardScalerによる特徴量の標準化
- MLflowによる実験トラッキング（パラメータ、メトリクス、モデル）
- ONNX形式でのモデルエクスポート
- 包括的なテストスイート

## セットアップ

### 前提条件

- Python 3.13以上
- uv（パッケージマネージャー）

### インストール

```bash
# 仮想環境の作成
uv venv

# 仮想環境の有効化
source .venv/bin/activate  # macOS/Linux

# 依存関係のインストール
uv pip install -e ".[dev]"
```

## 使い方

```bash
# モデルの学習
python src/iris_sklearn_rf/train.py

# MLflow UIの起動
mlflow ui
```

## テスト

```bash
# 全テストの実行
pytest tests/ -v

# カバレッジ付きでテスト実行
pytest tests/ -v --cov=src --cov-report=html
```

## プロジェクト構造

```
04_iris_sklearn_rf/
├── src/
│   └── iris_sklearn_rf/
│       ├── __init__.py
│       ├── train.py          # メインの学習スクリプト
│       ├── data_loader.py    # データ読み込み
│       ├── model.py          # モデル定義
│       └── utils.py          # ユーティリティ関数
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_model.py
│   └── test_train.py
├── SPECIFICATION.md          # 仕様書
├── README.md                 # このファイル
└── pyproject.toml           # プロジェクト設定
```

## 学習内容

このパターンを通して以下を学習します：

- ランダムフォレストのハイパーパラメータチューニング
- scikit-learnのPipelineパターン
- MLflowによる実験管理のベストプラクティス
- ONNXによるモデルの相互運用性

## 参考

- [仕様書](./SPECIFICATION.md)
- [参考コード](../../../01_reference/ml-system-in-actions/chapter2_training/iris_sklearn_rf/)
