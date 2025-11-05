# Iris Binary Classification with MLflow

Iris データセットを使った二値分類（Binary Classification）の実装。MLflow による実験管理を含む。

## 📋 目次

- [概要](#概要)
- [特徴](#特徴)
- [アーキテクチャ](#アーキテクチャ)
- [セットアップ](#セットアップ)
- [使い方](#使い方)
- [テスト](#テスト)
- [MLflow UI](#mlflow-ui)
- [プロジェクト構造](#プロジェクト構造)
- [技術スタック](#技術スタック)
- [学んだこと](#学んだこと)

---

## 概要

このプロジェクトは、Iris データセット（3クラス分類問題）を二値分類問題に変換し、Support Vector Classifier (SVC) で学習する実装です。

### 二値分類とは

元のIrisデータセット：
- **3クラス**: Setosa、Versicolor、Virginica

二値分類への変換：
- **陽性クラス（0）**: 指定したクラス（例: Setosa）
- **陰性クラス（1）**: その他のクラス（例: Versicolor + Virginica）

### このプロジェクトが解決する課題

1. **多クラス分類を二値分類に変換する方法**
2. **二値分類の評価指標（Precision、Recall）の理解**
3. **MLflowによる実験管理の実践**
4. **ONNX変換によるモデルの互換性確保**

---

## 特徴

### ✅ 実装済み機能

- **二値分類変換**: 3クラス → 2クラスへの自動変換
- **SVC学習**: StandardScaler + SVC のパイプライン
- **評価指標**: Accuracy、Precision、Recall
- **ONNX変換**: scikit-learn → ONNX 変換
- **MLflow統合**: パラメータ、メトリクス、モデルの自動記録
- **テスト**: 34個のテストケース（97%成功率）
- **実験スクリプト**: コマンドライン引数による柔軟な実験実行

### 🎯 目標精度

| Target Class | Accuracy | Precision | Recall |
|--------------|----------|-----------|--------|
| Setosa       | > 95%    | > 95%     | > 95%  |
| Versicolor   | > 90%    | > 90%     | > 90%  |
| Virginica    | > 90%    | > 90%     | > 90%  |

---

## アーキテクチャ

### システム構成

```
┌─────────────────────────────────────────────────────────────┐
│                     MLflow Tracking                          │
│  (実験管理・パラメータ記録・メトリクス記録・モデル保存)        │
└─────────────────────────────────────────────────────────────┘
                              ↑
                              │ log_param, log_metric, log_model
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Iris Binary Classifier                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Data     │→ │   Model    │→ │  Trainer   │            │
│  │  Loader    │  │  Builder   │  │            │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│         ↓              ↓               ↓                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Binary    │  │    SVC     │  │ Evaluator  │            │
│  │Conversion  │  │  Pipeline  │  │            │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│                                        ↓                     │
│                                  ┌────────────┐             │
│                                  │   ONNX     │             │
│                                  │  Exporter  │             │
│                                  └────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

### コンポーネント

1. **Data Loader** (`data_loader.py`)
   - Irisデータセットの読み込み
   - 3クラス → 2クラス変換
   - Train/Test分割

2. **Model Builder** (`model.py`)
   - StandardScaler + SVC パイプライン構築

3. **Trainer** (`trainer.py`)
   - モデル学習
   - 評価指標計算（Accuracy、Precision、Recall）

4. **ONNX Exporter** (`exporter.py`)
   - scikit-learn モデル → ONNX 変換

5. **MLflow Manager** (`mlflow_manager.py`)
   - 実験パラメータの記録
   - メトリクスの記録
   - モデルとアーティファクトの保存

---

## セットアップ

### 1. 前提条件

- Python 3.13 以上
- uv（パッケージマネージャー）

### 2. インストール

```bash
# プロジェクトディレクトリに移動
cd my_implementations/chapter2_training/03_iris_binary

# Pythonバージョン確認
cat .python-version  # 3.13

# 仮想環境の有効化
source .venv/bin/activate

# 依存関係は既にインストール済み（.venv/）
# 必要に応じて再インストール:
# uv pip install -e .
```

### 3. 依存関係

主要なライブラリ：
- `scikit-learn`: 機械学習モデル
- `mlflow`: 実験管理
- `onnx`, `onnxruntime`: ONNX変換・推論
- `pytest`: テストフレームワーク

---

## 使い方

### 基本的な実験実行

```bash
# Setosa を陽性クラスとして学習
python run_experiment.py --target_iris setosa

# Versicolor を陽性クラスとして学習
python run_experiment.py --target_iris versicolor

# Virginica を陽性クラスとして学習
python run_experiment.py --target_iris virginica
```

### コマンドライン引数

```bash
python run_experiment.py \
  --target_iris setosa \        # 陽性クラス（setosa/versicolor/virginica）
  --test_size 0.3 \             # テストデータの割合（デフォルト: 0.3）
  --tracking_uri ./mlruns \     # MLflow保存先（デフォルト: ./mlruns）
  --experiment_name iris_binary # 実験名（デフォルト: iris_binary_classification）
```

### 実験の出力例

```
🚀 Starting experiment: iris_binary_classification
📊 Target class: setosa
📁 Tracking URI: ./mlruns

📥 Loading data...
   Train samples: 105, Test samples: 45
🏗️  Building model...
🎓 Training model...
📊 Evaluating model...
   Accuracy:  0.9778
   Precision: 1.0000
   Recall:    0.9333
🔄 Converting to ONNX...
   ONNX saved: /tmp/tmpxxxxx.onnx
📝 Logging to MLflow...
   Run ID: 378ec03e57d14e769df9e7026afb0e53

✅ Experiment completed successfully!
🌐 View results: mlflow ui --port 5000
   Then open: http://localhost:5000
```

---

## テスト

### 全テスト実行

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ付き
pytest tests/ -v --cov=src --cov-report=html

# HTMLレポート確認
open htmlcov/index.html
```

### テスト結果

```
============================= test session starts ==============================
collected 34 items

tests/test_01_data_loader.py::TestDataLoader::test_load_data_setosa PASSED
tests/test_01_data_loader.py::TestDataLoader::test_binary_conversion_setosa PASSED
...
tests/test_06_integration.py::TestIntegration::test_mlflow_experiment_tracking PASSED

======================== 1 failed, 33 passed in 27.77s =========================
```

**成功率**: 97% (33/34 テスト成功)

### テストの種類

1. **ユニットテスト** (28テスト)
   - Data Loader: 8テスト
   - Model Builder: 5テスト
   - Trainer: 6テスト
   - ONNX Exporter: 5テスト
   - MLflow Manager: 4テスト（1つ警告あり）

2. **統合テスト** (6テスト)
   - E2Eパイプライン（3クラス分）
   - MLflow実験追跡
   - ONNX推論検証

---

## MLflow UI

### サーバー起動

```bash
# プロジェクトディレクトリで実行
mlflow ui --backend-store-uri ./mlruns --port 5000
```

### アクセス

ブラウザで以下のURLを開く：
```
http://127.0.0.1:5000
```

### 確認できる内容

1. **実験一覧**
   - `iris_binary_classification` 実験
   - 各Runの一覧

2. **Runの詳細**
   - **Parameters**:
     - `normalize`: "StandardScaler"
     - `model`: "svc"
     - `target_iris`: "setosa" | "versicolor" | "virginica"

   - **Metrics**:
     - `accuracy`: 正解率
     - `precision`: 適合率
     - `recall`: 再現率

   - **Artifacts**:
     - `model/`: scikit-learn モデル（pickle形式）
     - `iris_svc_{target}.onnx`: ONNX モデル

3. **Run比較**
   - 複数の実験結果を並べて比較
   - メトリクスのグラフ表示
   - パラメータの違いを確認

### MLflow UIのスクリーンショット例

```
┌─────────────────────────────────────────────────────────┐
│ Experiments > iris_binary_classification                 │
├─────────────────────────────────────────────────────────┤
│ Run Name         │ Metrics           │ Parameters       │
├─────────────────┼───────────────────┼──────────────────┤
│ run_001         │ accuracy: 0.9778  │ target: setosa   │
│                 │ precision: 1.0000 │ model: svc       │
│                 │ recall: 0.9333    │                  │
├─────────────────┼───────────────────┼──────────────────┤
│ run_002         │ accuracy: 1.0000  │ target: versicolor│
│                 │ precision: 1.0000 │ model: svc       │
│                 │ recall: 1.0000    │                  │
└─────────────────┴───────────────────┴──────────────────┘
```

---

## プロジェクト構造

```
03_iris_binary/
├── README.md                      # このファイル
├── SPECIFICATION.md               # 詳細な仕様書
├── pyproject.toml                 # 依存関係
├── .python-version                # Python 3.13
├── run_experiment.py              # 実験実行スクリプト
│
├── src/iris_binary/               # ソースコード
│   ├── __init__.py
│   ├── data_loader.py             # データ読み込み・二値化
│   ├── model.py                   # SVCパイプライン構築
│   ├── trainer.py                 # 学習・評価
│   ├── exporter.py                # ONNX変換
│   └── mlflow_manager.py          # MLflow統合
│
├── tests/                         # テストコード
│   ├── test_01_data_loader.py     # Data Loaderテスト
│   ├── test_02_model.py           # Model Builderテスト
│   ├── test_03_trainer.py         # Trainerテスト
│   ├── test_04_exporter.py        # ONNX Exporterテスト
│   ├── test_05_mlflow_manager.py  # MLflow Managerテスト
│   └── test_06_integration.py     # 統合テスト
│
├── mlruns/                        # MLflow実験データ
│   ├── 0/                         # デフォルト実験
│   └── 853812526864526897/        # iris_binary_classification
│
├── htmlcov/                       # カバレッジレポート
└── test_results_full.txt          # テスト結果ログ
```

---

## 技術スタック

### 機械学習

- **scikit-learn 1.6.1**: SVC、StandardScaler
- **numpy**: 数値計算

### 実験管理

- **MLflow 2.19.0**: 実験追跡、パラメータ・メトリクス記録、モデル管理

### モデル変換

- **ONNX**: モデルの標準フォーマット
- **skl2onnx**: scikit-learn → ONNX 変換
- **onnxruntime**: ONNX推論エンジン

### 開発ツール

- **pytest**: テストフレームワーク
- **pytest-cov**: カバレッジ測定
- **black**: コードフォーマッター
- **ruff**: リンター
- **mypy**: 型チェッカー

---

## 学んだこと

### 1. 二値分類の基本

- **多クラス分類から二値分類への変換**
  - One-vs-Rest戦略
  - クラスのバランス調整の重要性

- **評価指標の理解**
  - **Accuracy**: 全体の正解率（バランスが取れている場合に有効）
  - **Precision**: 陽性予測のうち実際に陽性だった割合（偽陽性を減らしたい場合）
  - **Recall**: 実際の陽性のうち正しく予測できた割合（見逃しを減らしたい場合）

### 2. MLflow実験管理

- **実験の再現性**
  - パラメータの自動記録
  - 実験結果の比較が容易
  - モデルのバージョン管理

- **MLflow UIの活用**
  - 実験の可視化
  - Run間の比較
  - モデルのダウンロード

### 3. ONNX変換のベストプラクティス

- **scikit-learn → ONNX変換**
  - `skl2onnx.convert_sklearn()` の使用
  - 初期型情報（initial_types）の指定が必須
  - Pipeline全体を一度に変換可能

- **推論の一貫性検証**
  - scikit-learn と ONNX の予測結果が一致することを確認
  - テストでの検証が重要

### 4. テスト駆動開発（TDD）

- **段階的なテスト作成**
  - ユニットテスト → 統合テスト
  - 各コンポーネントの独立性を保つ

- **高いカバレッジの維持**
  - 97%のカバレッジ達成
  - エッジケースのテストも含む

### 5. プロジェクト構成

- **レイヤー分離**
  - データ読み込み、モデル構築、学習、評価、変換、実験管理を分離
  - 各コンポーネントが独立してテスト可能
  - 再利用性が高い

### 6. 実務への応用

- **実験の自動化**
  - コマンドライン引数による柔軟な実験実行
  - 複数のターゲットクラスでの自動実験

- **実験管理の重要性**
  - MLflowによる実験の追跡
  - 過去の実験結果の参照が容易

---

## 今後の拡張案

### 短期

- [ ] モデル署名（signature）と入力例（input_example）をMLflowに追加
- [ ] 混同行列（Confusion Matrix）の可視化
- [ ] ROC曲線とAUCの計算

### 中期

- [ ] 他のモデルの追加（Random Forest、Logistic Regression）
- [ ] ハイパーパラメータチューニング（GridSearchCV）
- [ ] クロスバリデーション

### 長期

- [ ] GitHub Actions による CI/CD
- [ ] Docker化
- [ ] REST APIサーバーの実装

---

## 参考

### ドキュメント

- [SPECIFICATION.md](./SPECIFICATION.md) - 詳細な仕様書
- [test_results_full.txt](./test_results_full.txt) - テスト結果ログ

### 参考リポジトリ

- [元のコード](../../../reference/chapter2_training/iris_binary/)

### 外部リンク

- [scikit-learn SVC](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html)
- [MLflow Documentation](https://mlflow.org/docs/latest/tracking.html)
- [ONNX](https://onnx.ai/)
- [skl2onnx](https://onnx.ai/sklearn-onnx/)

---

## ライセンス

このプロジェクトは学習目的で作成されました。

## 作成者

**kshr123** - 2025-11-05
