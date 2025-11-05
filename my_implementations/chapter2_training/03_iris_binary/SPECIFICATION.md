# Iris Binary Classification - 仕様書

## 1. 要件定義

### 1.1 機能要件

- [ ] Irisデータセットを3クラスから2クラス（二値分類）に変換できる
- [ ] 指定したクラス（setosa/versicolor/virginica）を「陽性（0）」、その他を「陰性（1）」として扱う
- [ ] StandardScalerで特徴量を正規化できる
- [ ] SVCモデルで二値分類を学習できる
- [ ] 学習済みモデルをONNX形式でエクスポートできる
- [ ] MLflowで実験を記録・管理できる
  - パラメータ（normalizer, model, target_iris）
  - メトリクス（accuracy, precision, recall）
  - モデルファイル（scikit-learn pickle, ONNX）
- [ ] 評価指標（accuracy, precision, recall）を計算できる

### 1.2 非機能要件

- **パフォーマンス**: 学習時間 < 10秒
- **再現性**: random_state固定により同じ結果を再現できる
- **拡張性**: 他のモデル（RF, Logistic Regressionなど）に容易に置き換え可能
- **保守性**: レイヤー分離により各コンポーネントが独立してテスト可能

## 2. アーキテクチャ設計

### 2.1 システム構成

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

### 2.2 コンポーネント設計

#### 1. Data Loader (`01_data_loader.py`)
- **責務**: データの読み込みと二値化
- **機能**:
  - Irisデータセットの読み込み
  - 指定クラスを陽性（0）、その他を陰性（1）に変換
  - train/testデータの分割

#### 2. Model Builder (`02_model.py`)
- **責務**: SVCパイプラインの定義
- **機能**:
  - StandardScaler + SVC のパイプライン構築
  - モデルパラメータの管理

#### 3. Trainer (`03_trainer.py`)
- **責務**: モデルの学習と評価
- **機能**:
  - モデルの学習（fit）
  - 評価指標の計算（accuracy, precision, recall）

#### 4. ONNX Exporter (`04_exporter.py`)
- **責務**: モデルのONNX変換
- **機能**:
  - scikit-learnモデルをONNX形式に変換
  - ONNXファイルの保存

#### 5. MLflow Manager (`05_mlflow_manager.py`)
- **責務**: MLflowでの実験管理
- **機能**:
  - パラメータのログ記録
  - メトリクスのログ記録
  - モデルの保存
  - Artifactの記録（ONNXファイル等）

### 2.3 技術スタック

- **Python**: 3.13
- **機械学習**:
  - scikit-learn: モデル学習
  - numpy: 数値計算
- **実験管理**:
  - MLflow: 実験追跡・モデル管理
- **モデル変換**:
  - ONNX: モデルエクスポート
  - skl2onnx: scikit-learn → ONNX変換
  - onnxruntime: ONNX推論
- **開発ツール**:
  - pytest: テストフレームワーク
  - black: コードフォーマッター
  - ruff: リンター
  - mypy: 型チェッカー

## 3. データフロー

### 3.1 学習フロー

```
1. データ読み込み
   load_iris() → 150サンプル × 4特徴量 × 3クラス

2. 二値化
   target_iris="setosa" の場合:
   [0, 0, 0, 1, 1, 1, 2, 2, 2] → [0, 0, 0, 1, 1, 1, 1, 1, 1]
   (setosa=0, others=1)

3. train/test分割
   train_test_split(test_size=0.3, random_state=42)

4. 正規化 + 学習
   StandardScaler().fit_transform(X_train)
   SVC(probability=True).fit(X_train_scaled, y_train)

5. 評価
   accuracy_score, precision_score, recall_score

6. ONNX変換
   convert_sklearn(model, initial_types=[...])

7. MLflow記録
   mlflow.log_param(), mlflow.log_metric(), mlflow.sklearn.log_model()
```

### 3.2 入力データ仕様

**Irisデータセット**:
- サンプル数: 150
- 特徴量: 4次元
  - sepal length (cm)
  - sepal width (cm)
  - petal length (cm)
  - petal width (cm)
- クラス: 3種類（元々）→ 2種類に変換
  - setosa (0)
  - versicolor (1)
  - virginica (2)

**二値化後**:
- クラス: 2種類
  - 陽性（0）: 指定クラス（例: setosa）
  - 陰性（1）: その他（例: versicolor + virginica）

### 3.3 出力データ仕様

**学習済みモデル**:
- scikit-learn pickle形式
- ONNX形式（.onnx）

**評価指標**:
- accuracy: 全体の正解率
- precision: 陽性予測のうち実際に陽性だった割合
- recall: 実際の陽性のうち正しく予測できた割合

**MLflow記録**:
- パラメータ:
  - normalize: "StandardScaler"
  - model: "svc"
  - target_iris: "setosa" | "versicolor" | "virginica"
- メトリクス:
  - accuracy: float
  - precision: float
  - recall: float
- Artifacts:
  - model/: scikit-learnモデル
  - iris_svc_{target_iris}.onnx: ONNXモデル

## 4. MLflow 統合仕様

### 4.1 実験管理

**Experiment**:
- 名前: "iris_binary_classification"
- ID: 環境変数 `MLFLOW_EXPERIMENT_ID` または 0

**Run**:
- 各学習実行ごとに新しいRunを作成
- Run IDは自動生成

### 4.2 記録内容

**Parameters**:
```python
mlflow.log_param("normalize", "StandardScaler")
mlflow.log_param("model", "svc")
mlflow.log_param("target_iris", args.target_iris)
```

**Metrics**:
```python
mlflow.log_metric("accuracy", accuracy)
mlflow.log_metric("precision", precision)
mlflow.log_metric("recall", recall)
```

**Models**:
```python
mlflow.sklearn.log_model(model, "model")
```

**Artifacts**:
```python
mlflow.log_artifact(onnx_path)  # ONNXファイル
```

### 4.3 MLflow UI

```bash
# サーバー起動
mlflow ui --port 5000

# ブラウザでアクセス
http://localhost:5000
```

**表示内容**:
- 実験一覧
- Run比較
- パラメータ・メトリクスの可視化
- モデルのダウンロード

## 5. API仕様

### 5.1 コマンドライン引数

```bash
python -m iris_binary.main --test_size 0.3 --target_iris setosa
```

**引数**:
- `--test_size`: テストデータの割合（デフォルト: 0.3）
- `--target_iris`: 陽性とするクラス（choices: ["setosa", "versicolor", "virginica"]）

### 5.2 環境変数

- `MLFLOW_TRACKING_URI`: MLflowのトラッキングURI（デフォルト: file://./mlruns）
- `MLFLOW_EXPERIMENT_ID`: 実験ID（デフォルト: 0）

## 6. エラーハンドリング

### 6.1 想定エラー

| エラー | 原因 | 対処 |
|-------|------|------|
| `ValueError` | 不正なtarget_iris | setosa/versicolor/virginicaのみ許可 |
| `FileNotFoundError` | ONNXファイル保存先が存在しない | ディレクトリを自動作成 |
| `MLflowException` | MLflow接続エラー | トラッキングURIの確認 |

### 6.2 ログ出力

- 学習開始/終了時にログ出力
- MLflow Run IDの表示
- 評価指標の表示

## 7. テスト仕様

### 7.1 ユニットテスト

**Data Loader** (`test_01_data_loader.py`):
- [ ] データ読み込みができる
- [ ] 二値化が正しく動作する（setosa → 0, others → 1）
- [ ] train/test分割が正しく動作する
- [ ] データ型がfloat32である

**Model Builder** (`test_02_model.py`):
- [ ] パイプラインが正しく構築される
- [ ] StandardScalerが含まれる
- [ ] SVCが含まれる

**Trainer** (`test_03_trainer.py`):
- [ ] モデルが学習できる
- [ ] 評価指標が計算できる
- [ ] 評価指標が0〜1の範囲である

**ONNX Exporter** (`test_04_exporter.py`):
- [ ] ONNXファイルが作成される
- [ ] ONNXファイルが読み込める
- [ ] ONNX推論が実行できる
- [ ] scikit-learnとONNXの予測結果が一致する

**MLflow Manager** (`test_05_mlflow_manager.py`):
- [ ] パラメータがログ記録される
- [ ] メトリクスがログ記録される
- [ ] モデルがログ記録される
- [ ] Artifactがログ記録される

### 7.2 統合テスト

**E2E Pipeline** (`test_06_integration.py`):
- [ ] データ読み込み → 学習 → 評価 → ONNX変換 → MLflow記録の全フローが動作する
- [ ] 3種類のtarget_iris（setosa, versicolor, virginica）で動作する
- [ ] MLflow UIで結果を確認できる

## 8. 成功基準

### 8.1 機能要件

- [ ] 全テストケースがパス（目標: 30個以上）
- [ ] コードカバレッジ > 90%
- [ ] 3種類のtarget_irisで正しく動作

### 8.2 性能要件

- [ ] 学習時間 < 10秒
- [ ] accuracy > 0.90（setosaの場合）
- [ ] ONNXとscikit-learnの予測が一致（差 < 1e-5）

### 8.3 品質要件

- [ ] black, ruff, mypyのチェックがパス
- [ ] READMEが完成している
- [ ] MLflow UIで実験結果が確認できる

## 9. 参考

- 元のコード: `reference/chapter2_training/iris_binary/`
- scikit-learn SVC: https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html
- MLflow: https://mlflow.org/docs/latest/tracking.html
- ONNX: https://onnx.ai/
- skl2onnx: https://onnx.ai/sklearn-onnx/

## 10. 今後の拡張案

- [ ] 他のモデル（Random Forest, Logistic Regression）の追加
- [ ] ハイパーパラメータチューニング（GridSearchCV）
- [ ] クロスバリデーション
- [ ] 混同行列（Confusion Matrix）の可視化
- [ ] ROC曲線・AUCの追加
- [ ] Docker化
- [ ] CI/CDパイプライン（GitHub Actions）
