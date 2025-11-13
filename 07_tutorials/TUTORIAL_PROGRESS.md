# Model-in-Image Pattern ハンズオン - 進捗記録

## 📅 実施日
開始: 2025-11-13

## 🎉 チュートリアル完了！

**完了日**: 2025-11-13

このチュートリアルを通じて、Model-in-Image PatternをKubernetesにデプロイする実践的なスキルを習得しました。

---

## ✅ 完了したステップ

### Step 1: プロジェクト構造の理解 ✅
- [x] 1.1 プロジェクトディレクトリに移動
- [x] 1.2 ディレクトリ構造を確認
- [x] 1.3 モデルファイルを確認
- [x] 1.4 Dockerfileを確認

**学んだこと**:
- Model-in-Image Patternの仕組み（モデルファイルをイメージに組み込む）
- プロジェクトの構造（k8s/, models/, src/）
- モデルファイルのサイズ（約2.1KB）

---

### Step 2: Dockerイメージのビルド ✅
- [x] 2.1 イメージをビルド
- [x] 2.2 イメージを確認

**学んだこと**:
- `-t` オプション（tag）でイメージに名前とバージョンを付ける
- イメージサイズ: 約814MB（Python 3.13 + FastAPI + ONNX Runtime + モデル）
- `docker build -t model-in-image-pattern:v1.0 .`

---

### Step 3: ローカルテスト ✅
- [x] 3.1 コンテナを起動
- [x] 3.2 ヘルスチェック
- [x] 3.3 メタデータ取得
- [x] 3.4 ラベル一覧取得
- [x] 3.5 推論テスト（Setosa）
- [x] 3.6 ラベル付き推論
- [x] 3.7 ログを確認
- [x] 3.8 クリーンアップ

**学んだこと**:
- `-d` オプション（detached mode）でバックグラウンド実行
- `--name` でコンテナ名を指定（イメージとコンテナは別物）
- `-p 8000:8000` でポートマッピング（ホスト:コンテナ）
- `docker ps` でコンテナの起動状態を確認
- `docker logs` でログを確認
- APIエンドポイント:
  - `/health` - ヘルスチェック
  - `/metadata` - モデルの入出力形式
  - `/label` - ラベル一覧
  - `/predict` - 推論（確率値）
  - `/predict/label` - 推論（ラベル名）

**現在の状態**:
- Dockerイメージ: `model-in-image-pattern:v1.0` ビルド済み
- コンテナ: `model-test` 起動中（localhost:8000）

---

### Step 4: Kubernetesにデプロイ ✅
- [x] 4.1 minikubeを起動
- [x] 4.2 イメージをminikubeにロード
- [x] 4.3 Namespaceを作成
- [x] 4.4 Deploymentをデプロイ
- [x] 4.5 Podが起動するまで待つ
- [x] 4.6 Serviceを作成

**学んだこと**:
- Dockerとminikubeは別の環境（イメージのロードが必要）
- Namespaceでリソースを整理（クリーンアップが簡単）
- kubectl の `-n` オプション（namespace指定は必須）
- minikube service --url（minikube専用のURL取得方法）

---

### Step 5: APIエンドポイントのテスト ✅
- [x] 5.1 ServiceのURLを取得
- [x] 5.2 ヘルスチェック
- [x] 5.3 推論テスト（3品種すべて）

**学んだこと**:
- Setosa、Versicolor、Virginica の3品種すべてを正しく分類
- Kubernetesにデプロイしたモデルが正常に動作

---

### Step 6: スケーリングとモニタリング ✅
- [x] 6.1 手動スケールアウト（2個→5個）
- [x] 6.2 負荷テスト（100回リクエスト）
- [x] 6.3 ログ確認（負荷分散を確認）

**学んだこと**:
- kubectl scale で簡単にPod数を変更
- Serviceが自動的に負荷を分散（複数のPodに振り分け）
- for ループでの負荷テスト方法
- kubectl logs --prefix=true で各Podのログを確認

---

### Step 8: クリーンアップ ✅
- [x] Kubernetesリソースを削除（Namespace削除）
- [x] Dockerイメージを削除
- [x] minikubeを停止

---

## 🎯 チュートリアルの目標 ✅ 達成

このチュートリアルを通じて以下を習得しました：
- [x] Model-in-Image Patternの仕組みを理解する
- [x] 学習済みモデルをDockerイメージに組み込む
- [x] FastAPIでモデルをサービス化する
- [x] Kubernetesで本番環境を構築する
- [x] ヘルスチェックとスケーリングを実践する
- [x] 実際のAPIエンドポイントにアクセスする
- [x] 負荷分散を確認する

---

## 💡 重要な概念（復習用）

### Dockerの基本概念
- **イメージ vs コンテナ**: イメージ=設計図、コンテナ=実行中のインスタンス
- **`-t` (tag)**: イメージに名前とバージョンを付ける
- **`-d` (detached)**: バックグラウンドで実行
- **`--name`**: コンテナ名を指定
- **`-p ホスト:コンテナ`**: ポートマッピング（外部からアクセスできるようにする）

### Model-in-Image Pattern
- **メリット**: デプロイが簡単、高速起動、バージョン一致、オフライン対応
- **デメリット**: モデル更新時に再ビルド、イメージサイズ増大、複数モデル管理が煩雑
- **適用シーン**: モデルサイズが小さい、更新頻度が低い

---

## 🔗 参考ドキュメント

- [07_tutorials/03_model_in_image_hands_on.md](./03_model_in_image_hands_on.md) - チュートリアル本文
- [04_notes/09_docker_kubernetes_basics.md](../04_notes/09_docker_kubernetes_basics.md) - Docker & Kubernetes 基礎
- [03_my_implementations/chapter3_release_patterns/01_model_in_image/README.md](../03_my_implementations/chapter3_release_patterns/01_model_in_image/README.md) - 実装詳細

---

**次回の再開手順**:
1. このファイルを開いて「次はここから」を確認
2. コンテナの状態を確認: `docker ps`
3. Step 3.7 から続行
