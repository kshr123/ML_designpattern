# 機械学習システムデザインパターン - 学習進捗記録

> **このファイルの目的**: どこまで完了して次にどこから始めるかを把握するため
> **詳細な実装内容**: 各パターンのREADME.mdを参照してください

---

## 📊 概要

| 項目 | 内容 |
|------|------|
| **開始日** | 2025-11-03 |
| **完了パターン数** | 7 / 26 パターン |
| **完了チュートリアル数** | 2 / 3 チュートリアル |
| **現在の章** | Chapter 3: Release Patterns（進行中） |
| **最新の完了** | Kubernetes基礎チュートリアル (2025-11-07) |
| **次の目標** | Chapter 3: 02_model_load_pattern の実装 |

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
- [x] **01_model_in_image** (完了: 2025-11-06)
  - 詳細: [03_my_implementations/chapter3_release_patterns/01_model_in_image/README.md](../03_my_implementations/chapter3_release_patterns/01_model_in_image/README.md)
- [ ] 02_model_load_pattern

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

## 🎓 チュートリアル進捗

### Docker & Kubernetes チュートリアル
- [x] **01_docker_basics** (完了: 2025-11-06)
  - 詳細: [07_tutorials/01_docker_basics.md](../07_tutorials/01_docker_basics.md)
- [x] **02_minikube_kubernetes** (完了: 2025-11-07)
  - 詳細: [07_tutorials/k8s-tutorial/SESSION_LOG.md](../07_tutorials/k8s-tutorial/SESSION_LOG.md)
- [ ] 03_model_in_image_hands_on（実装は完了済み、ハンズオン未実施）

---

## 🎯 次のステップ

### Chapter 3 開始！🚀

Chapter 3（Release Patterns）の最初のパターンが完了しました。

#### 完了した内容：01_model_in_image (2025-11-06)

- **学習内容**:
  - Model-in-Image Patternの実装（モデルファイルをDockerイメージに組み込み）
  - FastAPI + ONNX Runtime による推論API
  - Docker & Kubernetes の基礎
  - minikubeへの実デプロイと動作確認

- **技術スタック**:
  - Python 3.13、FastAPI、ONNX Runtime
  - Docker、Kubernetes (minikube)
  - HPA（Horizontal Pod Autoscaler）

- **詳細**: [01_model_in_image/README.md](../03_my_implementations/chapter3_release_patterns/01_model_in_image/README.md)

#### 作成したドキュメント・チュートリアル

- **学習ガイド**: [04_notes/09_docker_kubernetes_basics.md](../04_notes/09_docker_kubernetes_basics.md)
  - Docker & Kubernetesの基礎を初心者向けに解説（850行以上）

- **チュートリアルシリーズ**: [07_tutorials/](../07_tutorials/)
  - ✅ `01_docker_basics.md` - Dockerの基礎（30分）（完了: 2025-11-06）
  - ✅ `02_minikube_kubernetes.md` - minikube & Kubernetes（40分）（完了: 2025-11-07）
  - ⏸️ `03_model_in_image_hands_on.md` - Model-in-Image Patternハンズオン（50分）

#### 最新の学習内容（2025-11-07）

- **Kubernetesチュートリアル実施**:
  - Deployment、Service、Podの関係性を理解
  - kubectl基本コマンドの習得
  - スケーリング（2個→5個→2個）を実践
  - ローリングアップデート（nginx:alpine → nginx:1.27）を体験
  - DeploymentとServiceの疎結合な設計を理解
  - Minikubeの役割と位置づけを理解

- **詳細**: [07_tutorials/k8s-tutorial/SESSION_LOG.md](../07_tutorials/k8s-tutorial/SESSION_LOG.md)

### 次の目標

**Chapter 3: 02_model_load_pattern**
- モデルを外部ストレージから動的にロード
- S3/GCSなどのオブジェクトストレージとの連携
- Model-in-Image Patternとの違いを理解する

---

## 📚 参考情報

- **プロジェクトルール**: [.claude/claude.md](../.claude/claude.md)
- **Chapter 2 進捗**: [03_my_implementations/chapter2_training/README.md](../03_my_implementations/chapter2_training/README.md)
- **全体進捗**: [README.md](../README.md)
