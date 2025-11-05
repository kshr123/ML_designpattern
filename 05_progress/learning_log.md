# 機械学習システムデザインパターン - 学習進捗記録

> **このファイルの目的**: どこまで完了して次にどこから始めるかを把握するため
> **詳細な実装内容**: 各パターンのREADME.mdを参照してください

---

## 📊 概要

| 項目 | 内容 |
|------|------|
| **開始日** | 2025-11-03 |
| **完了パターン数** | 6 / 26 パターン |
| **現在の章** | Chapter 2: Training（全パターン完了!） |
| **最新の完了** | 06_cifar10_cnn (2025-11-05) |
| **次の目標** | Chapter 3: Release Patterns へ進む |

---

## 📖 章ごとの進捗状況

### Chapter 2: Training（学習）
- [x] **01_model_db** (完了: 2025-11-04)
  - 詳細: [03_my_implementations/chapter2_training/01_model_db/README.md](../03_my_implementations/chapter2_training/01_model_db/README.md)
- [x] **02_iris_sklearn_svc** (完了: 2025-11-04)
  - 詳細: [03_my_implementations/chapter2_training/02_iris_sklearn_svc/README.md](../03_my_implementations/chapter2_training/02_iris_sklearn_svc/README.md)
- [x] **03_iris_binary** (完了: 2025-11-05)
  - 詳細: [03_my_implementations/chapter2_training/03_iris_binary/README.md](../03_my_implementations/chapter2_training/03_iris_binary/README.md)
- [x] **04_iris_sklearn_rf** (完了: 2025-11-05)
  - 詳細: [03_my_implementations/chapter2_training/04_iris_sklearn_rf/README.md](../03_my_implementations/chapter2_training/04_iris_sklearn_rf/README.md)
- [x] **05_iris_sklearn_outlier** (完了: 2025-11-05)
  - 詳細: [03_my_implementations/chapter2_training/05_iris_sklearn_outlier/README.md](../03_my_implementations/chapter2_training/05_iris_sklearn_outlier/README.md)
- [x] **06_cifar10_cnn** (完了: 2025-11-05)
  - 詳細: [03_my_implementations/chapter2_training/06_cifar10_cnn/README.md](../03_my_implementations/chapter2_training/06_cifar10_cnn/README.md)

### Chapter 3: Release Patterns（リリースパターン）
- [ ] model_in_image_pattern
- [ ] model_load_pattern

### Chapter 4: Serving Patterns（推論パターン）
- [ ] asynchronous_pattern
- [ ] batch_pattern
- [ ] data_cache_pattern
- [ ] edge_ai_pattern
- [ ] horizontal_microservice_pattern
- [ ] prediction_cache_pattern
- [ ] prep_pred_pattern
- [ ] sync_async_pattern
- [ ] synchronous_pattern
- [ ] web_single_pattern

### Chapter 5: Operations（運用）
- [ ] prediction_log_pattern
- [ ] prediction_monitoring_pattern

### Chapter 6: Operation Management（運用管理）
- [ ] circuit_breaker_pattern
- [ ] condition_based_pattern
- [ ] load_test_pattern
- [ ] online_ab_pattern
- [ ] paramater_based_pattern
- [ ] shadow_ab_pattern

---

## 🎯 次のステップ

### Chapter 2 完了！🎉

Chapter 2（Training）の全6パターンが完了しました。学んだことの概要：

- **01_model_db**: モデル管理データベース（FastAPI + SQLAlchemy）
- **02_iris_sklearn_svc**: SVM + CI/CD（GitHub Actions）
- **03_iris_binary**: 二値分類 + MLflow
- **04_iris_sklearn_rf**: ランダムフォレスト + ONNX
- **05_iris_sklearn_outlier**: 外れ値検出（教師なし学習）
- **06_cifar10_cnn**: CNN画像分類（PyTorch + MLflow + ONNX）

### 次の章の選択肢

**Option A: Chapter 3 - Release Patterns（推奨）**
- モデルのリリース方法を学ぶ
- model_in_image_pattern（Dockerへのモデル組み込み）
- model_load_pattern（実行時のモデル読み込み）

**Option B: Chapter 4 - Serving Patterns**
- 推論サービスの実装パターンを学ぶ
- synchronous_pattern から始める
- ONNX + MLflow の知識を活かせる

---

## 📚 参考情報

- **プロジェクトルール**: [.claude/claude.md](../.claude/claude.md)
- **Chapter 2 進捗**: [03_my_implementations/chapter2_training/README.md](../03_my_implementations/chapter2_training/README.md)
- **全体進捗**: [README.md](../README.md)
