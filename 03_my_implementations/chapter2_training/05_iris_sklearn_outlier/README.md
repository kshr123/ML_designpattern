# iris_sklearn_outlier

Irisデータセットを用いた外れ値検出（One-Class SVM + MLflow + ONNX）

## 📋 概要

このプロジェクトは、教師なし学習（One-Class SVM）を使用した外れ値検出パターンの実装です。
Irisデータセット全体を「正常データ」として学習し、正常なデータの境界を学習します。

### 特徴

- **教師なし学習**: ラベルを使わず、データの分布のみから外れ値を検出
- **One-Class SVM**: RBFカーネルを使用した高度な外れ値検出
- **MLflow統合**: 実験のパラメータ、メトリクス、モデルを自動記録
- **ONNX対応**: 異なるフレームワークでモデルを利用可能
- **100%テストカバレッジ**: TDD（Red-Green-Refactor）サイクルによる開発

## 🎯 学習目標

このパターンを通して学べること：

1. **教師なし学習の実装**
   - 正常データのみでの学習
   - 異常スコアの算出
   - 外れ値率の評価

2. **One-Class SVMの理解**
   - `nu`パラメータによる外れ値制御
   - RBFカーネルの活用
   - サポートベクターの役割

3. **実験管理**
   - MLflowによるハイパーパラメータ追跡
   - メトリクスの記録と比較
   - モデルのバージョン管理

4. **モデルの相互運用性**
   - ONNX形式へのエクスポート
   - 推論結果の検証

## 🏗️ アーキテクチャ

### システム構成

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

### モデルパイプライン

```python
Pipeline([
    ("scaler", StandardScaler()),      # 正規化
    ("ocs", OneClassSVM(nu=0.1))       # 外れ値検出
])
```

## 📂 プロジェクト構成

```
05_iris_sklearn_outlier/
├── SPECIFICATION.md              # 詳細な仕様書
├── README.md                     # このファイル
├── pyproject.toml                # プロジェクト設定
├── src/
│   └── iris_sklearn_outlier/
│       ├── __init__.py
│       ├── data_loader.py        # Irisデータ読み込み
│       ├── model.py              # One-Class SVMパイプライン
│       ├── trainer.py            # 学習・評価
│       ├── onnx_exporter.py      # ONNXエクスポート
│       └── train.py              # メインスクリプト
├── tests/
│   ├── test_data_loader.py       # データ読み込みテスト
│   ├── test_model.py             # モデルテスト
│   ├── test_trainer.py           # 学習・評価テスト
│   └── test_onnx_exporter.py     # ONNXテスト
├── test_results/
│   ├── all_tests_red.txt         # TDD Red Phase
│   └── all_tests_green.txt       # TDD Green Phase
├── mlruns/                       # MLflow実験記録
└── htmlcov/                      # カバレッジレポート
```

## 🚀 セットアップ

### 前提条件

- Python 3.13以上
- uv（パッケージマネージャー）

### インストール

```bash
# 1. ディレクトリに移動
cd 05_iris_sklearn_outlier

# 2. 仮想環境の作成
uv venv

# 3. 仮想環境の有効化
source .venv/bin/activate  # macOS/Linux

# 4. 依存関係のインストール
uv pip install -e ".[dev]"
```

## 💻 使い方

### 学習パイプラインの実行

```bash
# 仮想環境を有効化
source .venv/bin/activate

# メインスクリプトの実行
python -m iris_sklearn_outlier.train
```

### 実行結果例

```
================================================================================
Iris外れ値検出 学習パイプライン
================================================================================

[1/5] データを読み込み中...
  ✓ データ形状: (150, 4)
  ✓ データ型: float32

[2/5] モデルを学習中...
  ✓ 学習完了
  ✓ サポートベクター数: 21

[3/5] モデルを評価中...
  ✓ 外れ値率: 0.0933 (14/150 サンプル)
  ✓ 正常データ: 136 サンプル

[4/5] MLflowに記録中...
  ✓ パラメータとメトリクスを記録

[5/5] ONNXモデルをエクスポート中...
  ✓ ONNXモデル作成: /tmp/iris_ocs_0.onnx
  ✓ ONNX検証: 成功
  ✓ ONNXモデルをMLflowに記録

================================================================================
✅ 学習パイプライン完了
================================================================================

📊 結果サマリー:
  - 外れ値率: 0.0933
  - サポートベクター数: 21
  - MLflow実験ID: 0
  - ONNXモデル: iris_ocs_0.onnx
```

### テストの実行

```bash
# 全テストの実行
pytest tests/ -v

# カバレッジ付きテスト
pytest tests/ -v --cov=src/iris_sklearn_outlier --cov-report=html

# カバレッジレポートを開く
open htmlcov/index.html
```

### コード品質チェック

```bash
# フォーマット
black src/ tests/

# リント
ruff check src/ tests/

# 型チェック
mypy src/
```

## 🧪 テスト結果

### テストサマリー

- **総テスト数**: 35
- **成功**: 35 (100%)
- **失敗**: 0
- **カバレッジ**: 100%

### テスト内訳

| モジュール | テスト数 | カバレッジ |
|-----------|---------|-----------|
| data_loader | 6 | 100% |
| model | 10 | 100% |
| trainer | 10 | 100% |
| onnx_exporter | 9 | 100% |

## 📊 技術スタック

| カテゴリ | ツール |
|---------|--------|
| **言語** | Python 3.13 |
| **機械学習** | scikit-learn 1.5+ |
| **実験管理** | MLflow 2.10+ |
| **ONNX** | onnx 1.17+, onnxruntime 1.20+, skl2onnx 1.16+ |
| **テスト** | pytest 8.2+, pytest-cov 5.0+ |
| **コード品質** | black 24.4+, ruff 0.4+, mypy 1.10+ |
| **パッケージ管理** | uv |

## 🔑 主要なハイパーパラメータ

### One-Class SVM

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| `nu` | 0.1 | 外れ値の上限割合（0 < nu ≤ 1） |
| `gamma` | "auto" | RBFカーネルパラメータ（1/n_features） |
| `kernel` | "rbf" | カーネル関数 |

### パラメータの影響

- **nu**: 値を小さくすると外れ値が少なくなる（厳密な判定）
- **gamma**: 値を大きくすると決定境界が複雑になる（過学習リスク）
- **kernel**: "rbf"（非線形）、"linear"（線形）など

## 📈 評価指標

| メトリクス | 値 | 説明 |
|-----------|-----|------|
| outlier_rate | ~0.093 | 外れ値と判定された割合 |
| n_support_vectors | 21 | サポートベクター数 |
| n_outliers | 14 | 外れ値サンプル数 |
| n_inliers | 136 | 正常サンプル数 |

## 🎓 学んだこと

### 1. 教師なし学習の特徴

- **ラベル不要**: 正常データのみで学習可能
- **分布学習**: データの正常な分布を学習
- **閾値設定**: `nu`パラメータで外れ値の割合を制御

### 2. One-Class SVMの仕組み

- **サポートベクター**: 決定境界を定義する重要なサンプル
- **決定関数**: 境界からの距離で異常度を評価
- **カーネルトリック**: 非線形な境界を学習可能

### 3. TDDサイクルの実践

1. **Red**: テストを先に書き、失敗することを確認
2. **Green**: テストを通す最小限の実装
3. **Refactor**: コード品質を改善

### 4. MLflowによる実験管理

- パラメータとメトリクスの自動記録
- モデルのバージョン管理
- 実験の再現性確保

### 5. ONNXによる相互運用性

- scikit-learnモデルをONNX形式に変換
- 異なるフレームワーク間でモデルを共有
- 推論結果の一致を検証

## 🔍 他のパターンとの違い

| パターン | 学習方法 | 主な用途 |
|---------|---------|---------|
| **02_iris_sklearn_svc** | 教師あり（SVM） | 分類（ラベル予測） |
| **03_iris_binary** | 教師あり（二値分類） | 2クラス分類 |
| **04_iris_sklearn_rf** | 教師あり（RF） | 多クラス分類 |
| **05_iris_sklearn_outlier** | **教師なし（One-Class SVM）** | **外れ値検出** |

## 🔗 関連ドキュメント

- [SPECIFICATION.md](./SPECIFICATION.md) - 詳細な仕様書
- [参考実装](../../01_reference/chapter2_training/iris_sklearn_outlier/) - 元のコード
- [scikit-learn OneClassSVM](https://scikit-learn.org/stable/modules/generated/sklearn.svm.OneClassSVM.html)
- [MLflow](https://mlflow.org/docs/latest/index.html)
- [ONNX](https://onnx.ai/)

## ⚠️ 注意事項

- **nu パラメータ**: 0.1 は約10%の外れ値を許容する設定
- **学習データ**: 全データを正常として学習（実際の異常データは含まない）
- **スケーリング**: StandardScalerで正規化が必須（SVMは特徴量のスケールに敏感）
- **カーネル選択**: データの分布に応じて適切なカーネルを選択

## 🚧 今後の拡張

- [ ] 異なる`nu`値での性能比較
- [ ] 他のカーネル（linear, poly, sigmoid）の評価
- [ ] 実際の異常データを含むデータセットでの評価
- [ ] Isolation Forestとの性能比較
- [ ] リアルタイム異常検知への応用

---

**開発者**: kshr123
**開発日**: 2025-11-05
**プロジェクト**: [ML_designpattern](https://github.com/kshr123/ML_designpattern)
