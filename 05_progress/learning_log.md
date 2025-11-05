# 機械学習システムデザインパターン - 学習進捗記録

> **このファイルの目的**: どこまで完了して次にどこから始めるかを把握するため
> **詳細な実装内容**: 各パターンのREADME.mdを参照してください

---

## 📊 概要

| 項目 | 内容 |
|------|------|
| **開始日** | 2025-11-03 |
| **完了パターン数** | 3 / 26 パターン |
| **現在の章** | Chapter 2: Training |
| **最新の完了** | 03_iris_binary (2025-11-05) |
| **次の目標** | Chapter 4: Serving Patterns への移行検討 |

---

## 📖 章ごとの進捗状況

### Chapter 2: Training（学習）
- [x] **01_model_db** (完了: 2025-11-04)
  - 詳細: [03_my_implementations/chapter2_training/01_model_db/README.md](../03_my_implementations/chapter2_training/01_model_db/README.md)
- [x] **02_iris_sklearn_svc** (完了: 2025-11-04)
  - 詳細: [03_my_implementations/chapter2_training/02_iris_sklearn_svc/README.md](../03_my_implementations/chapter2_training/02_iris_sklearn_svc/README.md)
- [x] **03_iris_binary** (完了: 2025-11-05)
  - 詳細: [03_my_implementations/chapter2_training/03_iris_binary/README.md](../03_my_implementations/chapter2_training/03_iris_binary/README.md)
- [ ] cifar10
- [ ] iris_sklearn_outlier
- [ ] iris_sklearn_rf

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

### 推奨オプション

**Option A: Chapter 2 を完了させる**
- cifar10（CNN画像分類）
- iris_sklearn_rf（ランダムフォレスト）
- iris_sklearn_outlier（外れ値検出）

**Option B: Chapter 4 に進む（推奨）**
- ONNX + MLflow の知識を活かして推論パターンに進む
- synchronous_pattern から始める

---

## 📚 参考情報

- **プロジェクトルール**: [.claude/claude.md](../.claude/claude.md)
- **Chapter 2 進捗**: [03_my_implementations/chapter2_training/README.md](../03_my_implementations/chapter2_training/README.md)
- **全体進捗**: [README.md](../README.md)
