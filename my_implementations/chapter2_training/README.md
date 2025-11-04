# Chapter 2: Training（学習）パターン

このディレクトリには、機械学習モデルの学習に関するデザインパターンの実装が含まれています。

---

## 📚 Chapter 2 の概要

### 目的
機械学習モデルの学習プロセスにおける以下を学ぶ：
- モデルの学習方法
- データの前処理
- モデルの保存・管理
- 学習履歴の記録

### 学習する6つのパターン

| パターン | 目的 | 難易度 | 状態 |
|---------|------|--------|------|
| **model_db** | モデル管理データベース | ⭐⭐⭐ | ✅ 完了 |
| **iris_sklearn_svc** | Support Vector Classifier | ⭐ | ⏸️ 未着手 |
| **iris_sklearn_rf** | Random Forest | ⭐ | ⏸️ 未着手 |
| **iris_binary** | 二値分類 | ⭐ | ⏸️ 未着手 |
| **iris_sklearn_outlier** | 外れ値検出 | ⭐⭐ | ⏸️ 未着手 |
| **cifar10** | 画像分類（CNN） | ⭐⭐⭐ | ⏸️ 未着手 |

---

## 📁 ディレクトリ構造

```
chapter2_training/
├── README.md                    # このファイル
├── model_db/                    # ✅ 完了
│   ├── SPECIFICATION.md
│   ├── README.md
│   ├── pyproject.toml
│   ├── run_server.py
│   ├── src/
│   └── tests/
│
├── iris_sklearn_svc/           # ⏸️ 今後実装
│   └── ...
│
├── iris_sklearn_rf/            # ⏸️ 今後実装
│   └── ...
│
└── (その他のパターン)
```

---

## 🎯 実装済みパターン

### ✅ model_db - モデル管理データベース

**完了日**: 2025-11-04

#### 概要
機械学習モデルのライフサイクル（プロジェクト → モデル → 実験）を管理するデータベースシステム。

#### 技術スタック
- **フレームワーク**: FastAPI
- **ORM**: SQLAlchemy
- **データベース**: PostgreSQL / SQLite
- **バリデーション**: Pydantic
- **テスト**: pytest

#### 主な機能
- プロジェクト管理（作成、取得、更新、削除）
- モデル管理（プロジェクトに紐づく）
- 実験管理（パラメータ、評価指標の記録）
- 16個のRESTful APIエンドポイント

#### アーキテクチャ
5レイヤー構成：
1. **API Layer** - FastAPIエンドポイント
2. **Schema Layer** - Pydanticモデル
3. **CRUD Layer** - データベース操作
4. **Model Layer** - SQLAlchemyモデル
5. **Database Layer** - 接続管理

#### テスト
- 31個のテストケース（カバレッジ92%）
- ユニットテスト: 15個
- 統合テスト: 16個

#### 学んだこと
- レイヤー分離アーキテクチャの利点
- Pydanticのバリデーション・シリアライゼーション・ドキュメント生成
- TDD（テスト駆動開発）の実践
- SQLAlchemyのORM操作
- JSON型カラムの扱い方

#### ディレクトリ
```
model_db/
├── SPECIFICATION.md          # 詳細な仕様書
├── README.md                 # 実装ドキュメント
├── pyproject.toml            # 依存関係
├── run_server.py             # サーバー起動
├── src/
│   ├── api/                  # FastAPI
│   ├── db/                   # SQLAlchemy + CRUD
│   └── configurations.py     # 設定
└── tests/
    ├── test_cruds.py         # ユニットテスト
    └── test_api.py           # 統合テスト
```

#### 参考
- [詳細な実装ドキュメント](./model_db/README.md)
- [仕様書](./model_db/SPECIFICATION.md)
- [学習記録](../../progress/learning_log.md#2025-11-04---model-db)

---

## 📋 今後実装するパターン

### ⏸️ iris_sklearn_svc - Support Vector Classifier

#### 概要
Irisデータセットを使ったSupport Vector Classifierの実装。

#### 学習ポイント
- sklearn の基本的な使い方
- データの前処理（標準化）
- モデルの学習と評価
- モデルの保存（pickle）

#### 推奨実装順序
2番目（model_db の次）

#### 参考コード
`reference/chapter2_training/iris_sklearn_svc/`

---

### ⏸️ iris_sklearn_rf - Random Forest

#### 概要
Irisデータセットを使ったRandom Forestの実装。

#### 学習ポイント
- アンサンブル学習
- ハイパーパラメータチューニング
- 特徴量の重要度分析

#### 推奨実装順序
3番目

#### 参考コード
`reference/chapter2_training/iris_sklearn_rf/`

---

### ⏸️ iris_binary - 二値分類

#### 概要
Irisデータセットを二値分類問題として扱う実装。

#### 学習ポイント
- 多クラス分類から二値分類への変換
- 不均衡データの扱い
- 評価指標（Precision、Recall、F1-score）

#### 推奨実装順序
4番目

#### 参考コード
`reference/chapter2_training/iris_binary/`

---

### ⏸️ iris_sklearn_outlier - 外れ値検出

#### 概要
Irisデータセットを使った外れ値検出の実装。

#### 学習ポイント
- 外れ値検出アルゴリズム（Isolation Forest、One-Class SVM）
- 異常検知の評価方法
- 教師なし学習

#### 推奨実装順序
5番目

#### 参考コード
`reference/chapter2_training/iris_sklearn_outlier/`

---

### ⏸️ cifar10 - 画像分類（CNN）

#### 概要
CIFAR-10データセットを使った畳み込みニューラルネットワーク（CNN）の実装。

#### 学習ポイント
- 深層学習フレームワーク（PyTorch/TensorFlow）
- CNNアーキテクチャ
- 画像の前処理（データ拡張）
- GPUトレーニング
- チェックポイント管理

#### 推奨実装順序
6番目（最後、最も複雑）

#### 参考コード
`reference/chapter2_training/cifar10/`

---

## 🚀 新しいパターンを実装する手順

### ステップ1: ディレクトリ作成

```bash
# プロジェクトルートから
cd my_implementations/chapter2_training

# 新しいパターンのディレクトリを作成
mkdir iris_sklearn_svc
cd iris_sklearn_svc

# Pythonバージョン指定
echo "3.13" > .python-version

# テンプレートをコピー
cp ../../../templates/pyproject.toml.template pyproject.toml
cp ../../../templates/SPECIFICATION.template.md SPECIFICATION.md
```

### ステップ2: 環境構築

```bash
# 仮想環境作成
uv venv
source .venv/bin/activate

# 開発ツールインストール
uv pip install pytest pytest-cov black ruff mypy

# パターン固有の依存関係を追加
# 例: scikit-learn, pandas, numpy
uv pip install scikit-learn pandas numpy matplotlib
```

### ステップ3: ディレクトリ構造作成

```bash
# 基本的な構造
mkdir -p src/iris_svc tests data notebooks
touch src/iris_svc/__init__.py
touch tests/__init__.py

# プロジェクト構造例
# src/iris_svc/
#   ├── __init__.py
#   ├── data_loader.py      # データ読み込み
#   ├── preprocessor.py     # 前処理
#   ├── trainer.py          # 学習
#   └── evaluator.py        # 評価
```

### ステップ4: 参考コードを分析

```bash
# 参考コードを確認
cd ../../../../reference/chapter2_training/iris_sklearn_svc
cat README.md

# アーキテクチャを理解
# - どのファイルが何をしているか
# - データの流れ
# - 依存関係
```

### ステップ5: 仕様書作成（SDD）

```
Claude Codeに指示:
「iris_sklearn_svcパターンのSPECIFICATION.mdを作成して。
参考コードを分析して、要件定義、アーキテクチャ、成功基準を明確にして」
```

### ステップ6: テスト作成（TDD - Red）

```bash
# テストファイルを作成
# tests/test_data_loader.py
# tests/test_preprocessor.py
# tests/test_trainer.py
# tests/test_evaluator.py

# テスト実行（失敗する）
pytest tests/ -v
```

### ステップ7: 実装（TDD - Green）

```
Claude Codeに指示:
「テストを通すための実装を段階的に進めて」

1. data_loader を実装
2. preprocessor を実装
3. trainer を実装
4. evaluator を実装
5. 各ステップでテストを実行
```

### ステップ8: 動作確認

```bash
# 学習を実行
python src/iris_svc/train.py

# 結果を確認
python src/iris_svc/evaluate.py
```

### ステップ9: ドキュメント作成

```bash
# README.mdを作成
# - 実装の概要
# - セットアップ手順
# - 実行方法
# - 結果
# - 学んだこと
```

### ステップ10: 学習記録

```bash
# progress/learning_log.md に追加
# - 実装日
# - 学んだこと
# - 疑問点
# - 改善点
```

---

## 📝 開発ルール（Chapter 2 固有）

### ファイル命名規則

```
パターン名/
├── SPECIFICATION.md          # 必須: 仕様書
├── README.md                 # 必須: 実装ドキュメント
├── pyproject.toml            # 必須: 依存関係
├── .python-version           # 推奨: Pythonバージョン
├── .gitignore                # 必須: 除外ファイル
│
├── src/                      # ソースコード
│   └── パターン名/
│       ├── __init__.py
│       ├── data_loader.py    # データ読み込み
│       ├── preprocessor.py   # 前処理
│       ├── trainer.py        # 学習
│       ├── evaluator.py      # 評価
│       └── predictor.py      # 推論
│
├── tests/                    # テスト
│   ├── test_data_loader.py
│   ├── test_preprocessor.py
│   ├── test_trainer.py
│   └── test_evaluator.py
│
├── data/                     # データ（.gitignoreに追加）
│   ├── raw/                  # 生データ
│   ├── processed/            # 前処理済み
│   └── .gitkeep
│
├── models/                   # 学習済みモデル（.gitignoreに追加）
│   └── .gitkeep
│
├── notebooks/                # Jupyter Notebook（オプション）
│   └── exploration.ipynb
│
└── results/                  # 結果（.gitignoreに追加）
    ├── metrics.json
    └── plots/
```

### .gitignore に追加すべきもの

```gitignore
# データ（大きすぎる）
data/raw/
data/processed/

# 学習済みモデル（大きすぎる）
models/*.pkl
models/*.pth
models/*.h5

# 結果
results/

# Jupyter Notebook
.ipynb_checkpoints/
```

### データの扱い

```python
# ❌ Bad: データをGitにコミット
git add data/iris.csv  # 小さくてもNG

# ✅ Good: データダウンロードスクリプトを作成
# src/iris_svc/download_data.py
def download_iris_data():
    """Irisデータセットをダウンロード"""
    from sklearn.datasets import load_iris
    iris = load_iris()
    # data/raw/ に保存
```

---

## 🎓 学習の進め方

### 推奨順序

```
1. model_db (完了)
   ↓ データベース操作、API設計を学ぶ

2. iris_sklearn_svc
   ↓ sklearn の基礎を学ぶ

3. iris_sklearn_rf
   ↓ アンサンブル学習を学ぶ

4. iris_binary
   ↓ 二値分類と評価指標を学ぶ

5. iris_sklearn_outlier
   ↓ 異常検知を学ぶ

6. cifar10
   ↓ 深層学習を学ぶ
```

### 各パターンの学習時間目安

| パターン | 学習時間 | 実装時間 |
|---------|---------|---------|
| model_db | 4-6時間 | ✅ 完了 |
| iris_sklearn_svc | 2-3時間 | 未着手 |
| iris_sklearn_rf | 2-3時間 | 未着手 |
| iris_binary | 2-3時間 | 未着手 |
| iris_sklearn_outlier | 3-4時間 | 未着手 |
| cifar10 | 6-8時間 | 未着手 |

---

## 💡 よくある質問

### Q1: 参考コードをそのままコピーしていい？

**A**: いいえ。このプロジェクトの目的は「学習」です。

```
❌ Bad: コピペ
cp -r ../../../../reference/chapter2_training/iris_sklearn_svc/* .

✅ Good: 理解してから実装
1. 参考コードを読んで理解
2. 仕様書を作成
3. テストを作成
4. ゼロから実装
```

### Q2: どれくらい忠実に再現すればいい？

**A**: アーキテクチャの本質を理解していれば、実装は自由にアレンジOK。

```
重要なのは:
✅ パターンの目的を理解している
✅ アーキテクチャの考え方を学んでいる
✅ ベストプラクティスを適用している

実装の詳細:
🆗 ファイル名が違う
🆗 クラス名が違う
🆗 より良い方法を使っている
```

### Q3: テストは必須？

**A**: はい。TDDを実践することで理解が深まります。

```
テストのメリット:
✅ 仕様を明確にできる
✅ リファクタリングが安全
✅ バグを早期発見
✅ ドキュメントになる
```

### Q4: 全パターン実装する必要がある？

**A**: いいえ。興味のあるパターンから始めてOK。

```
最低限:
✅ model_db (完了)
✅ 1つの機械学習パターン（iris_*）

推奨:
✅ model_db (完了)
✅ iris_sklearn_svc
✅ cifar10
```

---

## 📊 進捗管理

### 進捗の記録先

```
progress/learning_log.md
- 各パターンの学習内容
- 学んだこと
- 疑問点
- 改善点
```

### チェックリスト

各パターン実装時：

- [ ] 参考コードを分析・理解
- [ ] SPECIFICATION.md 作成
- [ ] ディレクトリ構造作成
- [ ] pyproject.toml 設定
- [ ] テスト作成（TDD）
- [ ] 実装
- [ ] 全テスト通過
- [ ] 動作確認
- [ ] README.md 作成
- [ ] 学習記録に追加
- [ ] Gitコミット

---

## 🔗 関連ドキュメント

| ドキュメント | 内容 |
|------------|------|
| [開発ワークフロー](../../../docs/DEVELOPMENT_WORKFLOW.md) | 7フェーズの開発プロセス |
| [Claude Rules](../../../.claude/claude.md) | プロジェクト全体のルール |
| [学習記録](../../../progress/learning_log.md) | 詳細な進捗記録 |
| [テストガイド](../../../notes/test_writing_guide.md) | テストの書き方 |
| [uvガイド](../../../notes/uv_package_manager_guide.md) | 依存関係管理 |

---

**次のパターンに挑戦しましょう！🚀**
