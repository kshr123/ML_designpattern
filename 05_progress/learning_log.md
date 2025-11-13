# 機械学習システムデザインパターン - 学習進捗記録

> **このファイルの目的**: どこまで完了して次にどこから始めるかを把握するため
> **詳細な実装内容**: 各パターンのREADME.mdを参照してください

---

## 📊 概要

| 項目 | 内容 |
|------|------|
| **開始日** | 2025-11-03 |
| **完了パターン数** | 8 / 26 パターン |
| **完了チュートリアル数** | 4 / 4 チュートリアル（すべて完了！） |
| **現在の章** | Chapter 3: Release Patterns（進行中） |
| **最新の完了** | Model-Load Pattern (2025-11-13) |
| **次の目標** | Chapter 4: Serving Patterns へ進む |

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
- [x] **02_model_load_pattern** (完了: 2025-11-13)
  - 詳細: [03_my_implementations/chapter3_release_patterns/02_model_load_pattern/README.md](../03_my_implementations/chapter3_release_patterns/02_model_load_pattern/README.md)

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
- [x] **02_minikube_kubernetes** (完了: 2025-11-07、クリーンアップ: 2025-11-12)
  - 詳細: [07_tutorials/k8s-tutorial/SESSION_LOG.md](../07_tutorials/k8s-tutorial/SESSION_LOG.md)
- [x] **番外編: Docker Compose** (完了: 2025-11-06)
  - docker-compose-demo/: FastAPI + Redis構成
  - docker-compose-advanced/: 環境変数管理
  - 詳細: [07_tutorials/docker_learning_notes.md](../07_tutorials/docker_learning_notes.md)
- [x] **03_model_in_image_hands_on** (完了: 2025-11-13)
  - 詳細: [07_tutorials/TUTORIAL_PROGRESS.md](../07_tutorials/TUTORIAL_PROGRESS.md)

---

## 🎯 次のステップ

### Docker/K8sチュートリアル完了！🎉

すべてのチュートリアルが完了しました（2025-11-12）。

---

### Chapter 3 継続！🚀

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

#### 完了した内容：02_model_load_pattern (2025-11-13)

- **学習内容**:
  - Model-Load Patternの実装（外部ストレージからモデルを動的にロード）
  - InitContainerとemptyDirを使ったデータ共有
  - GCSからのモデルダウンロード
  - Model-in-Image Patternとの違いを理解

- **技術スタック**:
  - Python 3.13、FastAPI、ONNX Runtime
  - Docker（InitContainer + Main Container）
  - Kubernetes（emptyDir、Liveness/Readiness Probe、HPA）
  - Google Cloud Storage (GCS)

- **学んだポイント**:
  - InitContainerの役割とemptyDirの特性
  - emptyDirマウント時のファイル上書き問題と解決方法
  - Liveness ProbeとReadiness Probeの違い
  - TDDサイクルの実践（28/28テスト成功、100%カバレッジ）

- **詳細**: [02_model_load_pattern/README.md](../03_my_implementations/chapter3_release_patterns/02_model_load_pattern/README.md)

---

## Chapter 4: Serving Patterns（推論サービスパターン）

### 完了した内容：01_web_single_pattern ✅ (2025-11-13)

- **学習内容**:
  - Web Single Patternの実装（シングルDockerコンテナでWeb API公開）
  - Gunicorn + Uvicornのマルチプロセス構成
  - FastAPIで7つのRESTful APIエンドポイント
  - ONNX Runtimeによる推論

- **技術スタック**:
  - Python 3.13、FastAPI、Gunicorn、Uvicorn
  - ONNX Runtime、Pydantic
  - Docker（本番環境向け）

- **学んだポイント**:
  - GunicornとUvicornの関係性と組み合わせ方
  - プロセス管理（Gunicorn）+ 非同期実行（Uvicorn）の利点
  - TDDサイクルの実践（41/41テスト成功、98%カバレッジ）
  - エラーハンドリングの重要性
  - グローバルインスタンスによるモデル読み込み効率化

- **詳細**: [01_web_single_pattern/README.md](../03_my_implementations/chapter4_serving_patterns/01_web_single_pattern/README.md)

### 次の目標（2025-11-13〜）

**Chapter 4: Serving Patterns を継続**

**推奨順序**:
1. ✅ `web_single_pattern` - シングルWebサーバー推論（完了）
2. `synchronous_pattern` - 同期推論
3. `asynchronous_pattern` - 非同期推論
4. その他のパターン（Batch、Cache、Microserviceなど）

---

## 📚 参考情報

- **プロジェクトルール**: [.claude/claude.md](../.claude/claude.md)
- **Chapter 2 進捗**: [03_my_implementations/chapter2_training/README.md](../03_my_implementations/chapter2_training/README.md)
- **全体進捗**: [README.md](../README.md)
