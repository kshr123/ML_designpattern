# iris_sklearn_outlier 仕様書

## 1. 要件定義

### 1.1 機能要件

- [ ] Irisデータセットを正常データとして読み込む
- [ ] One-Class SVMで外れ値検出モデルを学習する
- [ ] 学習データに対する外れ値率を算出する
- [ ] MLflowで実験を記録する（パラメータ、メトリクス、モデル）
- [ ] 学習済みモデルをONNX形式でエクスポートする
- [ ] ONNXモデルとscikit-learnモデルの予測結果が一致することを検証する

### 1.2 非機能要件

- **パフォーマンス**: 学習時間 < 10秒（Irisデータセット150サンプル）
- **再現性**: random_state固定で毎回同じ結果
- **テストカバレッジ**: 80%以上
- **コード品質**: black, ruff, mypyによる品質チェックをパス
- **ドキュメント**: 全てのdocstringを日本語で記載

## 2. アーキテクチャ設計

### 2.1 システム構成

```
┌─────────────────────────────────────────────────────────┐
│                  外れ値検出学習パイプライン                │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ データ読込   │   │ モデル学習   │   │ 結果記録     │
│ load_iris()  │   │ One-Class    │   │ MLflow       │
│              │──▶│ SVM          │──▶│ ONNX export  │
│ 150 samples  │   │ StandardScaler│   │              │
└──────────────┘   └──────────────┘   └──────────────┘
```

### 2.2 コンポーネント設計

#### データローダー (`data_loader.py`)
- **責務**: Irisデータの読み込み
- **入力**: なし
- **出力**: 特徴量行列 (150, 4) - float32

#### モデル定義 (`model.py`)
- **責務**: One-Class SVM パイプラインの作成
- **構成**:
  1. StandardScaler: 特徴量の正規化（平均0、分散1）
  2. OneClassSVM: 外れ値検出
     - `nu`: 外れ値の上限割合（デフォルト: 0.1 = 10%）
     - `gamma`: RBFカーネルのパラメータ（デフォルト: "auto"）
     - `kernel`: カーネル関数（デフォルト: "rbf"）

#### トレーナー (`trainer.py`)
- **責務**: モデルの学習と評価
- **学習**: `fit(X)` - 教師なし学習
- **評価**: 外れ値率の算出
  - 予測値: +1（正常）、-1（外れ値）
  - outlier_rate = (外れ値数) / (全データ数)

#### ONNXエクスポーター (`onnx_exporter.py`)
- **責務**: ONNX形式へのエクスポートと検証
- **エクスポート**: skl2onnxでモデル変換
- **検証**: sklearn予測 vs ONNX予測の一致確認

#### メインスクリプト (`train.py`)
- **責務**: 完全な学習パイプラインの実行
- **MLflow統合**: 実験のトラッキング

### 2.3 技術スタック

- **Python**: 3.13
- **機械学習**: scikit-learn 1.5+
- **実験管理**: MLflow 2.17+
- **ONNX**: onnx 1.17+, onnxruntime 1.20+, skl2onnx 1.18+
- **開発ツール**: pytest, black, ruff, mypy
- **パッケージ管理**: uv

## 3. データ仕様

### 3.1 入力データ

**Irisデータセット**:
- **形状**: (150, 4)
- **型**: float32
- **特徴量**:
  1. sepal length (cm) - がく片の長さ
  2. sepal width (cm) - がく片の幅
  3. petal length (cm) - 花弁の長さ
  4. petal width (cm) - 花弁の幅
- **用途**: 全データを正常データとして学習

### 3.2 モデル出力

**予測値**:
- **型**: int (1 または -1)
- **意味**:
  - `+1`: 正常データ
  - `-1`: 外れ値（異常データ）

**決定関数値**:
- **型**: float
- **意味**: 決定境界からの距離（負の値ほど外れ値の可能性が高い）

## 4. モデル仕様

### 4.1 One-Class SVM

**パラメータ**:
```python
OneClassSVM(
    nu=0.1,           # 外れ値の上限割合（0 < nu <= 1）
    gamma="auto",     # RBFカーネルパラメータ（1/n_features）
    kernel="rbf"      # カーネル関数
)
```

**特徴**:
- 正常データのみで学習
- 正常データの境界を学習し、境界外を外れ値として検出
- `nu`パラメータで外れ値の許容割合を制御

### 4.2 パイプライン構成

```python
Pipeline([
    ("scaler", StandardScaler()),      # 正規化
    ("ocs", OneClassSVM(nu=0.1))       # 外れ値検出
])
```

## 5. MLflow 実験管理

### 5.1 記録するパラメータ

| パラメータ名 | 型 | 説明 |
|------------|-----|------|
| normalize | str | 正規化手法（StandardScaler） |
| model | str | モデル名（one_class_svm） |
| nu | float | 外れ値上限割合 |
| gamma | str/float | カーネルパラメータ |
| kernel | str | カーネル関数 |

### 5.2 記録するメトリクス

| メトリクス名 | 型 | 説明 | 期待値 |
|------------|-----|------|--------|
| outlier_rate | float | 外れ値と判定された割合 | ~0.1（nuに依存） |
| n_support_vectors | int | サポートベクター数 | - |

### 5.3 記録する成果物

- **MLflowモデル**: `model/` - scikit-learn形式
- **ONNXモデル**: `iris_ocs_0.onnx` - ONNX形式

## 6. ONNX エクスポート仕様

### 6.1 入力仕様

```python
FloatTensorType([None, 4])
# None: バッチサイズ（可変）
# 4: 特徴量数（Iris）
```

### 6.2 出力仕様

- **label**: 予測クラス（+1 or -1）
- **score**: 決定関数値（float）

### 6.3 検証

- sklearn予測結果とONNX予測結果が全サンプルで一致することを確認

## 7. テスト戦略

### 7.1 ユニットテスト

**test_data_loader.py**:
- [ ] Irisデータの読み込みテスト
- [ ] データ形状の検証
- [ ] データ型の検証

**test_model.py**:
- [ ] パイプライン作成テスト
- [ ] パイプライン構成の検証
- [ ] パラメータ設定の検証
- [ ] カスタムパラメータのテスト

**test_trainer.py**:
- [ ] モデル学習テスト
- [ ] 外れ値率の算出テスト
- [ ] 外れ値率が妥当な範囲にあることの確認
- [ ] 予測値が+1または-1であることの検証

**test_onnx_exporter.py**:
- [ ] ONNXエクスポートテスト
- [ ] ONNXファイル作成の確認
- [ ] ONNX予測とscikit-learn予測の一致確認

### 7.2 統合テスト

**test_integration.py**:
- [ ] エンドツーエンドの学習パイプライン実行
- [ ] MLflowへの記録確認
- [ ] ONNXモデルのエクスポート確認

## 8. ディレクトリ構造

```
05_iris_sklearn_outlier/
├── SPECIFICATION.md           # この仕様書
├── README.md                  # 実装ドキュメント
├── pyproject.toml             # プロジェクト設定
├── src/
│   └── iris_sklearn_outlier/
│       ├── __init__.py
│       ├── data_loader.py     # データ読み込み
│       ├── model.py           # モデル定義
│       ├── trainer.py         # 学習・評価
│       ├── onnx_exporter.py   # ONNXエクスポート
│       └── train.py           # メインスクリプト
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_model.py
│   ├── test_trainer.py
│   ├── test_onnx_exporter.py
│   └── test_integration.py
├── test_results/              # テスト結果（Red/Green）
├── mlruns/                    # MLflow実験記録
└── .venv/                     # 仮想環境
```

## 9. 成功基準

- [ ] 全ユニットテストがパス（pytest）
- [ ] 統合テストがパス
- [ ] テストカバレッジ ≥ 80%
- [ ] コード品質チェックがパス（black, ruff, mypy）
- [ ] 外れ値率が妥当な範囲（0.05 ~ 0.15程度）
- [ ] ONNXモデルとscikit-learnモデルの予測が一致
- [ ] MLflowに実験が正しく記録される
- [ ] 学習時間 < 10秒
- [ ] ドキュメントが日本語で完備されている

## 10. 参考

- **元の実装**: `01_reference/chapter2_training/iris_sklearn_outlier/`
- **scikit-learn OneClassSVM**: https://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html
- **MLflow**: https://mlflow.org/docs/latest/index.html
- **ONNX**: https://onnx.ai/
