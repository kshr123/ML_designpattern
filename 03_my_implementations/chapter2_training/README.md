# Chapter 2: Training（学習）

機械学習システムにおける**モデルの学習プロセス**に関するデザインパターンを実装します。

---

## 🎯 この章で学ぶこと

Chapter 2では、機械学習モデルの学習フェーズに焦点を当て、以下のスキルを習得します：

### 学習するテーマ

1. **モデル管理の基礎**
   - モデルのライフサイクル管理
   - プロジェクト・モデル・実験の階層構造
   - メタデータとパラメータの記録

2. **様々な学習アルゴリズム**
   - SVM（Support Vector Machine）
   - ランダムフォレスト（アンサンブル学習）
   - 異常検知（教師なし学習）
   - CNN（深層学習）

3. **実験管理とトラッキング**
   - MLflowによる実験記録
   - パラメータとメトリクスの管理
   - モデルのバージョン管理

4. **モデルの相互運用性**
   - ONNX形式へのエクスポート
   - 異なるフレームワーク間でのモデル共有

---

## 📖 他の章との違い

機械学習システムの各章が扱う範囲：

| 章 | 焦点 | 主なトピック |
|---|------|-------------|
| **Chapter 2: Training** | **モデルの学習** | データ準備、アルゴリズム選択、ハイパーパラメータ調整、実験管理 |
| Chapter 3: Release | モデルのデプロイ準備 | モデルのパッケージング、バージョニング、リリース戦略 |
| Chapter 4: Serving | モデルの推論サービス | API設計、同期/非同期推論、スケーリング、キャッシング |
| Chapter 5: Operations | システム運用 | ログ記録、モニタリング、アラート、性能追跡 |
| Chapter 6: Operation Management | 高度な運用管理 | A/Bテスト、Circuit Breaker、カナリアリリース |

**Chapter 2の位置づけ**:
- MLシステムの**最初のステップ** - モデルを作成する
- Chapter 3以降の基盤となる - 良いモデルを作らなければ、良いシステムは作れない
- 実験と改善のサイクル - 複数のモデルを試して最適なものを見つける

---

## 📚 実装パターン一覧

| # | パターン名 | 内容 | 難易度 | 状態 |
|---|-----------|------|--------|------|
| 01 | **model_db** | モデル管理データベース（FastAPI + SQLAlchemy） | ⭐⭐⭐ | ✅ 完了 |
| 02 | **iris_sklearn_svc** | SVM分類 + CI/CD（GitHub Actions） | ⭐⭐ | ✅ 完了 |
| 03 | **iris_binary** | 二値分類 + MLflow実験管理 | ⭐⭐ | ✅ 完了 |
| 04 | **iris_sklearn_rf** | ランダムフォレスト + ONNX | ⭐ | ✅ 完了 |
| 05 | **iris_sklearn_outlier** | 外れ値検出（教師なし学習） | ⭐⭐ | ✅ 完了 |
| 06 | **cifar10_cnn** | CNN画像分類（PyTorch + MLflow + ONNX） | ⭐⭐⭐ | ✅ 完了 |

### 進捗状況

- **完了**: 6/6 パターン（100%達成！）
- **Chapter 2完了**: 全パターンの実装が完了しました

---

## 🎓 学習の推奨順序

```
01_model_db
  ↓ モデル管理の全体像を理解

02_iris_sklearn_svc
  ↓ scikit-learn + CI/CD + ONNXの基本

03_iris_binary
  ↓ MLflow実験管理の実践

04_iris_sklearn_rf
  ↓ アンサンブル学習 + パイプライン

05_iris_sklearn_outlier
  ↓ 教師なし学習・異常検知

06_cifar10
  ↓ 深層学習・GPU学習
```

---

## 📂 ディレクトリ構成

```
chapter2_training/
├── README.md                    # このファイル（概要）
├── 01_model_db/                 # ✅ モデル管理DB
│   ├── SPECIFICATION.md         # 詳細仕様
│   ├── README.md                # 実装ドキュメント
│   └── ...
├── 02_iris_sklearn_svc/         # ✅ SVM + CI/CD
│   ├── SPECIFICATION.md
│   ├── README.md
│   └── ...
├── 03_iris_binary/              # ✅ 二値分類 + MLflow
│   ├── SPECIFICATION.md
│   ├── README.md
│   └── ...
├── 04_iris_sklearn_rf/          # ✅ ランダムフォレスト + ONNX
│   ├── SPECIFICATION.md
│   ├── README.md
│   └── ...
├── 05_iris_sklearn_outlier/     # ✅ 外れ値検出
│   ├── SPECIFICATION.md
│   ├── README.md
│   └── ...
└── 06_cifar10_cnn/              # ✅ CNN画像分類
    ├── SPECIFICATION.md
    ├── README.md
    └── ...
```

**詳細はパターン別のREADME.mdを参照してください。**

---

## 🔗 関連ドキュメント

- **プロジェクトルール**: [.claude/claude.md](../../.claude/claude.md)
- **学習進捗**: [05_progress/learning_log.md](../../05_progress/learning_log.md)
- **開発ワークフロー**: [06_docs/DEVELOPMENT_WORKFLOW.md](../../06_docs/DEVELOPMENT_WORKFLOW.md)
- **全体概要**: [README.md](../../README.md)

---

**各パターンの詳細な実装内容、技術スタック、学んだことは、各ディレクトリのREADME.mdを参照してください。**
