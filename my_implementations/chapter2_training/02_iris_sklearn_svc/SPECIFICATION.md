# Iris SVM分類パイプライン 仕様書

Version: 1.0.0
Last Updated: 2025-11-04
Author: kshr123

---

## 目次

1. [要件定義](#1-要件定義)
2. [アーキテクチャ設計](#2-アーキテクチャ設計)
3. [API仕様](#3-api仕様)
4. [データモデル](#4-データモデル)
5. [成功基準](#5-成功基準)

---

## 1. 要件定義

### 1.1 機能要件

#### 必須機能
- [ ] Irisデータセットの読み込み
- [ ] train/testデータの分割（configurable test_size）
- [ ] データの前処理（StandardScaler）
- [ ] SVMモデル（SVC）の学習
- [ ] モデルの評価（accuracy, precision, recall）
- [ ] MLflowへのメトリクス・パラメータのログ
- [ ] MLflowへのモデルの保存
- [ ] ONNXフォーマットへのモデル変換
- [ ] ONNXモデルの保存

#### オプション機能
- [ ] ハイパーパラメータのチューニング
- [ ] クロスバリデーション
- [ ] 混同行列の可視化

### 1.2 非機能要件

- **再現性**: random seedを固定し、同じ結果を再現できること
- **拡張性**: 他のモデル（Random Forest等）に容易に置き換え可能
- **テスタビリティ**: 各関数が独立してテスト可能
- **保守性**: コードが明確で理解しやすい
- **実行時間**: 学習は数秒以内に完了すること

---

## 2. アーキテクチャ設計

### 2.1 システム構成

```
┌─────────────────────┐
│  CLI Interface      │
│  (train.py)         │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Training Pipeline  │
│  1. Data Loading    │
│  2. Preprocessing   │
│  3. Model Training  │
│  4. Evaluation      │
│  5. Model Export    │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐  ┌──────────┐
│ MLflow  │  │  ONNX    │
│ Tracking│  │  Model   │
└─────────┘  └──────────┘
```

### 2.2 コンポーネント設計

#### データローダー (`data_loader.py`)
- **責務**: Irisデータセットの読み込みとtrain/test分割
- **入力**: test_size (float), random_state (int)
- **出力**: x_train, x_test, y_train, y_test (numpy.ndarray)

#### モデル定義 (`model.py`)
- **責務**: scikit-learnパイプラインの定義
- **構成**: StandardScaler → SVC(probability=True)
- **出力**: Pipeline オブジェクト

#### トレーナー (`trainer.py`)
- **責務**: モデルの学習
- **入力**: pipeline, x_train, y_train
- **出力**: 学習済みpipeline

#### 評価器 (`evaluator.py`)
- **責務**: モデルの評価
- **入力**: trained_model, x_test, y_test
- **出力**: accuracy, precision, recall (float)

#### モデルエクスポーター (`exporter.py`)
- **責務**: ONNXフォーマットへの変換と保存
- **入力**: trained_model, output_path
- **出力**: ONNX model file

#### メインスクリプト (`train.py`)
- **責務**: 全体のオーケストレーション、MLflow連携
- **機能**:
  - コマンドライン引数の解析
  - 各コンポーネントの呼び出し
  - MLflowへのログ記録

### 2.3 技術スタック

- **Python**: 3.13
- **機械学習**: scikit-learn 1.5+
- **実験管理**: MLflow 2.18+
- **モデル変換**: skl2onnx 1.18+, onnx 1.17+
- **テスト**: pytest 8.4+
- **パッケージ管理**: uv

---

## 3. API仕様

### 3.1 CLI インターフェース

```bash
python src/iris_sklearn_svc/train.py [OPTIONS]
```

#### オプション

| オプション | 型 | デフォルト | 説明 |
|-----------|-----|-----------|------|
| `--test_size` | float | 0.3 | テストデータの割合（0.0-1.0） |
| `--random_state` | int | 42 | 乱数シード（再現性のため） |
| `--mlflow_experiment_name` | str | "iris_svc" | MLflow実験名 |

#### 使用例

```bash
# デフォルト設定で実行
python src/iris_sklearn_svc/train.py

# テストサイズを変更して実行
python src/iris_sklearn_svc/train.py --test_size 0.2

# 乱数シードを指定して実行
python src/iris_sklearn_svc/train.py --random_state 123
```

### 3.2 関数インターフェース

#### `get_data(test_size: float, random_state: int) -> Tuple`
```python
"""
Irisデータセットを読み込み、train/testに分割

Args:
    test_size (float): テストデータの割合（0.0-1.0）
    random_state (int): 乱数シード

Returns:
    Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        x_train, x_test, y_train, y_test
"""
```

#### `define_svc_pipeline() -> Pipeline`
```python
"""
StandardScaler + SVC のパイプラインを定義

Returns:
    Pipeline: scikit-learn Pipeline オブジェクト
"""
```

#### `train(model: Pipeline, x_train: np.ndarray, y_train: np.ndarray) -> Pipeline`
```python
"""
モデルを学習

Args:
    model (Pipeline): scikit-learn Pipeline
    x_train (np.ndarray): 訓練データ
    y_train (np.ndarray): 訓練ラベル

Returns:
    Pipeline: 学習済みモデル
"""
```

#### `evaluate(model: Pipeline, x_test: np.ndarray, y_test: np.ndarray) -> Tuple[float, float, float]`
```python
"""
モデルを評価

Args:
    model (Pipeline): 学習済みモデル
    x_test (np.ndarray): テストデータ
    y_test (np.ndarray): テストラベル

Returns:
    Tuple[float, float, float]: accuracy, precision, recall
"""
```

#### `save_onnx(model: Pipeline, filepath: str) -> None`
```python
"""
モデルをONNXフォーマットで保存

Args:
    model (Pipeline): 学習済みモデル
    filepath (str): 保存先パス
"""
```

---

## 4. データモデル

### 4.1 入力データ

#### Iris Dataset
- **ソース**: `sklearn.datasets.load_iris()`
- **特徴量数**: 4
  - sepal length (cm)
  - sepal width (cm)
  - petal length (cm)
  - petal width (cm)
- **クラス数**: 3
  - 0: Setosa
  - 1: Versicolor
  - 2: Virginica
- **サンプル数**: 150

#### データ型
```python
x_train: np.ndarray  # shape: (n_train_samples, 4), dtype: float32
x_test: np.ndarray   # shape: (n_test_samples, 4), dtype: float32
y_train: np.ndarray  # shape: (n_train_samples,), dtype: float32
y_test: np.ndarray   # shape: (n_test_samples,), dtype: float32
```

### 4.2 出力データ

#### MLflowログ

**パラメータ**:
```python
{
    "normalize": "StandardScaler",
    "model": "svc",
    "test_size": 0.3,
    "random_state": 42
}
```

**メトリクス**:
```python
{
    "accuracy": 0.95,   # float (0.0-1.0)
    "precision": 0.94,  # float (0.0-1.0)
    "recall": 0.95      # float (0.0-1.0)
}
```

**アーティファクト**:
- `model/`: scikit-learn model (pickle)
- `iris_svc_<experiment_id>.onnx`: ONNX model

#### ONNXモデル

```python
{
    "input_name": "float_input",
    "input_shape": [None, 4],  # バッチサイズ可変、特徴量4次元
    "input_type": FloatTensorType,
    "output_name": "output_label",
    "output_type": int64
}
```

---

## 5. 成功基準

### 5.1 機能的成功基準

- [ ] Irisデータセットが正常に読み込まれる
- [ ] train/testの分割が指定した割合で実行される
- [ ] StandardScalerが正常に動作する
- [ ] SVCモデルが正常に学習される
- [ ] 評価指標（accuracy, precision, recall）が計算される
- [ ] MLflowにパラメータがログされる
- [ ] MLflowにメトリクスがログされる
- [ ] MLflowにモデルが保存される
- [ ] ONNXモデルが正常に変換・保存される
- [ ] 保存されたONNXモデルが読み込み・推論可能

### 5.2 品質基準

- [ ] **全テストケースがパス**（ユニット・統合テスト）
- [ ] **コードカバレッジ > 80%**
- [ ] **学習時間 < 5秒**（CPU環境）
- [ ] **モデル精度 > 90%**（Irisは比較的簡単なデータセット）
- [ ] **型ヒントが適切に設定**されている
- [ ] **docstringが全関数に記載**されている
- [ ] **PEP 8準拠**（black, ruff通過）

### 5.3 再現性基準

- [ ] random_stateを固定した場合、同じ結果が得られる
- [ ] MLflowの実験が正しくトラッキングされる
- [ ] 保存されたモデルで同じ精度が再現される

---

## 6. テスト戦略

### 6.1 ユニットテスト

#### `tests/test_data_loader.py`
- [ ] データの読み込みが正常に行われる
- [ ] train/testの分割比率が正しい
- [ ] データ型がfloat32である
- [ ] データ形状が正しい（x: (N, 4), y: (N,)）

#### `tests/test_model.py`
- [ ] パイプラインが正しく定義される
- [ ] StandardScalerが含まれている
- [ ] SVCが含まれている
- [ ] probability=Trueが設定されている

#### `tests/test_trainer.py`
- [ ] モデルが学習される（fit呼び出し）
- [ ] 学習後に予測が可能

#### `tests/test_evaluator.py`
- [ ] 評価指標が計算される
- [ ] accuracy, precision, recallが0.0-1.0の範囲内
- [ ] 評価指標が合理的な値（> 0.5）

#### `tests/test_exporter.py`
- [ ] ONNXモデルが正常に保存される
- [ ] 保存されたONNXファイルが存在する
- [ ] ONNXモデルが読み込み可能
- [ ] ONNXモデルで推論が実行できる

### 6.2 統合テスト

#### `tests/test_integration.py`
- [ ] エンドツーエンドで学習パイプラインが実行される
- [ ] MLflowに正しくログされる
- [ ] ONNXモデルが正しく保存される
- [ ] 保存されたモデルで推論が実行できる

---

## 7. 実装計画

### フェーズ1: データ処理（Day 1）
1. `src/iris_sklearn_svc/data_loader.py` 実装
2. `tests/test_data_loader.py` 作成・実行

### フェーズ2: モデル定義（Day 1）
1. `src/iris_sklearn_svc/model.py` 実装
2. `tests/test_model.py` 作成・実行

### フェーズ3: 学習・評価（Day 1）
1. `src/iris_sklearn_svc/trainer.py` 実装
2. `src/iris_sklearn_svc/evaluator.py` 実装
3. `tests/test_trainer.py` 作成・実行
4. `tests/test_evaluator.py` 作成・実行

### フェーズ4: エクスポート（Day 1）
1. `src/iris_sklearn_svc/exporter.py` 実装
2. `tests/test_exporter.py` 作成・実行

### フェーズ5: 統合（Day 1）
1. `src/iris_sklearn_svc/train.py` 実装（CLIエントリポイント）
2. `tests/test_integration.py` 作成・実行
3. MLflow連携の確認

### フェーズ6: ドキュメント（Day 1）
1. README.md 作成
2. 使用例の追加
3. 学習ログの記録

---

## 8. 依存関係

### 必須ライブラリ
```toml
[project.dependencies]
scikit-learn = ">=1.5.0"
mlflow = ">=2.18.0"
onnx = ">=1.17.0"
skl2onnx = ">=1.18.0"
numpy = ">=1.26.0"
```

### 開発用ライブラリ
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.4.0",
    "pytest-cov>=6.0.0",
    "black>=24.0.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]
```

---

## 9. 参考資料

- [scikit-learn SVC](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [ONNX](https://onnx.ai/)
- [skl2onnx](https://onnx.ai/sklearn-onnx/)
- [参考実装](../../../reference/chapter2_training/iris_sklearn_svc/)

---

## 10. 変更履歴

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-04 | kshr123 | 初版作成 |
