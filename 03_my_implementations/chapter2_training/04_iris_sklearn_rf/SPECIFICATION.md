# Iris Random Forest Classification - 仕様書

## 1. 要件定義

### 1.1 機能要件

- [x] Irisデータセットの読み込みと前処理
- [x] ランダムフォレスト分類器による3クラス分類
- [x] StandardScalerによる特徴量の標準化
- [x] MLflowによる実験トラッキング
  - パラメータの記録（n_estimators, max_depth, random_state等）
  - メトリクスの記録（accuracy, f1-score等）
  - モデルのartifact保存
- [x] ONNX形式でのモデルエクスポート
- [x] 学習済みモデルの評価

### 1.2 非機能要件

- **パフォーマンス**: 学習時間 < 10秒（Irisデータセット）
- **再現性**: random_seedの固定により再現可能
- **可読性**: scikit-learn Pipelineパターンによる明確なワークフロー
- **移植性**: ONNX形式による他フレームワークとの相互運用性
- **テスタビリティ**: 各コンポーネントが独立してテスト可能

## 2. アーキテクチャ設計

### 2.1 システム構成

```
┌─────────────────────────────────────────────────────┐
│                  Training Pipeline                   │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐                                    │
│  │ Data Loader  │ → Irisデータセットの読み込み       │
│  └──────┬───────┘                                    │
│         ↓                                            │
│  ┌──────────────┐                                    │
│  │   Pipeline   │                                    │
│  │ ┌──────────┐ │                                    │
│  │ │Scaler    │ │ → 特徴量の標準化                   │
│  │ └────┬─────┘ │                                    │
│  │      ↓       │                                    │
│  │ ┌──────────┐ │                                    │
│  │ │RandomFor.│ │ → 分類器                           │
│  │ └──────────┘ │                                    │
│  └──────┬───────┘                                    │
│         ↓                                            │
│  ┌──────────────┐                                    │
│  │   Evaluator  │ → モデル評価                       │
│  └──────┬───────┘                                    │
│         ↓                                            │
│  ┌──────────────┐     ┌──────────────┐              │
│  │ MLflow Logger│ ──→ │ ONNX Exporter│              │
│  └──────────────┘     └──────────────┘              │
│                                                       │
└─────────────────────────────────────────────────────┘
```

### 2.2 コンポーネント設計

#### 2.2.1 DataLoader (`data_loader.py`)
**責務**: データセットの読み込みと分割
- `load_iris_data()`: Irisデータセットを読み込み
- `split_data()`: データを訓練/テストセットに分割

#### 2.2.2 ModelBuilder (`model.py`)
**責務**: モデルパイプラインの定義
- `create_rf_pipeline()`: StandardScaler + RandomForestClassifierのPipelineを構築
- パラメータ: n_estimators, max_depth, random_state等

#### 2.2.3 Trainer (`trainer.py`)
**責務**: モデルの学習と評価
- `train_model()`: パイプラインの学習
- `evaluate_model()`: モデルの評価（accuracy, f1-score等）

#### 2.2.4 MLflowLogger (`mlflow_logger.py`)
**責務**: MLflowへのログ記録
- `log_params()`: ハイパーパラメータのログ
- `log_metrics()`: 評価メトリクスのログ
- `log_model()`: モデルのartifact保存

#### 2.2.5 ONNXExporter (`onnx_exporter.py`)
**責務**: モデルのONNX形式への変換
- `export_to_onnx()`: scikit-learnモデルをONNXに変換
- `validate_onnx()`: ONNX推論の動作確認

### 2.3 技術スタック

- **Python**: 3.13
- **機械学習**: scikit-learn 1.5.0+
- **実験管理**: MLflow 2.10.0+
- **モデル変換**: skl2onnx 1.16.0+, onnxruntime 1.17.0+
- **数値計算**: numpy 2.0.0+
- **テスト**: pytest 8.2.0+, pytest-cov 5.0.0+
- **コード品質**: black, ruff, mypy

## 3. データ仕様

### 3.1 入力データ

**Iris Dataset**
- **特徴量**: 4次元
  - sepal_length (cm)
  - sepal_width (cm)
  - petal_length (cm)
  - petal_width (cm)
- **ラベル**: 3クラス
  - 0: Setosa
  - 1: Versicolor
  - 2: Virginica
- **サンプル数**: 150

### 3.2 データ分割

- **訓練データ**: 80% (120サンプル)
- **テストデータ**: 20% (30サンプル)
- **分割方法**: stratified split（クラス比率を維持）

### 3.3 前処理

```python
# StandardScaler による標準化
# 各特徴量を平均0、分散1に変換
X_scaled = (X - mean) / std
```

## 4. モデル仕様

### 4.1 RandomForestClassifier パラメータ

| パラメータ | デフォルト値 | 説明 |
|-----------|-------------|------|
| n_estimators | 100 | 決定木の数 |
| max_depth | None | 木の最大深さ（Noneは無制限） |
| min_samples_split | 2 | 内部ノード分割に必要な最小サンプル数 |
| min_samples_leaf | 1 | 葉ノードに必要な最小サンプル数 |
| random_state | 42 | 乱数シード（再現性） |

### 4.2 Pipeline構成

```python
Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(
        n_estimators=100,
        max_depth=None,
        random_state=42
    ))
])
```

## 5. MLflow仕様

### 5.1 記録するパラメータ

- `n_estimators`: 決定木の数
- `max_depth`: 木の最大深さ
- `min_samples_split`: 分割に必要な最小サンプル数
- `min_samples_leaf`: 葉に必要な最小サンプル数
- `random_state`: 乱数シード

### 5.2 記録するメトリクス

- `accuracy`: 正解率
- `f1_score_macro`: マクロ平均F1スコア
- `f1_score_weighted`: 重み付きF1スコア
- `precision_macro`: マクロ平均適合率
- `recall_macro`: マクロ平均再現率

### 5.3 Artifacts

- `model/`: scikit-learn Pipelineモデル
- `model.onnx`: ONNX形式のモデル
- `confusion_matrix.png`: 混同行列（オプション）

## 6. ONNX仕様

### 6.1 変換仕様

- **入力型**: FloatTensorType([None, 4])
  - None: バッチサイズ（可変）
  - 4: 特徴量次元
- **出力型**: Int64（クラスラベル）とFloat（確率）

### 6.2 検証項目

- scikit-learnモデルとONNXモデルの予測一致性
- 推論速度の計測

## 7. テスト仕様

### 7.1 ユニットテスト

#### test_data_loader.py
- `test_load_iris_data()`: データ読み込みのテスト
  - データ形状の確認（150サンプル、4特徴量）
  - ラベル数の確認（3クラス）
- `test_split_data()`: データ分割のテスト
  - 訓練/テスト比率の確認
  - stratified splitの確認

#### test_model.py
- `test_create_rf_pipeline()`: パイプライン構築のテスト
  - パイプラインのステップ確認
  - パラメータの確認
- `test_pipeline_fit()`: パイプラインの学習テスト
  - 学習が正常に完了すること
  - 学習後のattributeが存在すること

#### test_trainer.py
- `test_train_model()`: 学習処理のテスト
- `test_evaluate_model()`: 評価処理のテスト
  - メトリクスの範囲確認（0〜1）

#### test_onnx_exporter.py
- `test_export_to_onnx()`: ONNX変換のテスト
  - ONNXファイルが生成されること
  - ファイルサイズが0より大きいこと
- `test_onnx_prediction()`: ONNX推論のテスト
  - scikit-learnとONNXの予測一致性

### 7.2 統合テスト

#### test_integration.py
- `test_full_training_pipeline()`: 全体フローのテスト
  - データ読み込み → 学習 → 評価 → MLflowログ → ONNX変換
  - エンドツーエンドで正常に動作すること

### 7.3 E2Eテスト（オプション）

#### test_e2e.py
- MLflow UIからの実験確認
- ONNX推論の実行確認

## 8. ディレクトリ構成

```
04_iris_sklearn_rf/
├── src/
│   └── iris_sklearn_rf/
│       ├── __init__.py
│       ├── data_loader.py      # データ読み込み
│       ├── model.py            # モデル定義
│       ├── trainer.py          # 学習・評価
│       ├── mlflow_logger.py    # MLflowログ
│       ├── onnx_exporter.py    # ONNX変換
│       └── train.py            # メインスクリプト
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_model.py
│   ├── test_trainer.py
│   ├── test_onnx_exporter.py
│   └── test_integration.py
├── test_results/               # テスト結果の記録
│   ├── data_loader_red.txt
│   ├── data_loader_green.txt
│   └── ...
├── mlruns/                     # MLflow実験データ
├── SPECIFICATION.md            # 本仕様書
├── README.md                   # ドキュメント
└── pyproject.toml             # プロジェクト設定
```

## 9. 成功基準

### 9.1 機能要件

- [x] 全テストケースがパス（カバレッジ 80%以上）
- [x] モデルの正解率が 90%以上（Irisデータセット）
- [x] MLflowに実験が正しく記録される
- [x] ONNX変換が成功し、推論結果が一致する

### 9.2 非機能要件

- [x] コードがPEP 8に準拠（black, ruff）
- [x] 型ヒントが適切に付与されている（mypy）
- [x] ドキュメントが充実している
- [x] 再現性が確保されている（random_state固定）

### 9.3 学習目標

- [x] ランダムフォレストの仕組みを理解
- [x] scikit-learn Pipelineの使い方を習得
- [x] MLflowによる実験管理を実践
- [x] ONNXによるモデル変換を理解

## 10. 実装スケジュール

### Phase 1: データ処理（TDD Red → Green）
1. `test_data_loader.py` 作成（Red）
2. `data_loader.py` 実装（Green）

### Phase 2: モデル構築（TDD Red → Green）
1. `test_model.py` 作成（Red）
2. `model.py` 実装（Green）

### Phase 3: 学習・評価（TDD Red → Green）
1. `test_trainer.py` 作成（Red）
2. `trainer.py` 実装（Green）

### Phase 4: MLflow連携（TDD Red → Green）
1. `test_mlflow_logger.py` 作成（Red）
2. `mlflow_logger.py` 実装（Green）

### Phase 5: ONNX変換（TDD Red → Green）
1. `test_onnx_exporter.py` 作成（Red）
2. `onnx_exporter.py` 実装（Green）

### Phase 6: 統合とリファクタリング
1. 統合テスト作成・実行
2. コードリファクタリング
3. ドキュメント整備

## 参考

- [scikit-learn RandomForestClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [skl2onnx Documentation](https://onnx.ai/sklearn-onnx/)
- [参考実装](../../../01_reference/ml-system-in-actions/chapter2_training/iris_sklearn_rf/)
