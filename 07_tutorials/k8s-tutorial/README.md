# Kubernetes実践チュートリアル

## 📅 実施情報

- **実施日**: 2025-11-07
- **所要時間**: 約90分
- **対象**: Kubernetesを初めて使う人
- **環境**: minikube + kubectl on macOS

---

## 🎯 学習目標

このチュートリアルでは、Kubernetesの基本的なリソース（Pod、Deployment、Service）を実際に動かしながら学びます。

### 習得した知識

1. **Kubernetesの基本概念**
   - Pod、Deployment、Serviceの役割
   - ラベルとセレクタの仕組み
   - 宣言的な設定管理（マニフェストファイル）

2. **kubectl基本操作**
   - リソースの作成、確認、更新、削除
   - スケーリング（Pod数の増減）
   - ローリングアップデート

3. **実践的なスキル**
   - マニフェストファイルの作成
   - Deploymentでアプリケーションをデプロイ
   - Serviceで外部公開
   - 無停止でのアップデート

---

## 📁 ファイル構成

```
k8s-tutorial/
├── README.md                     # このファイル
├── SESSION_LOG.md                # 詳細な学習記録
├── nginx-deployment.yaml         # Deploymentマニフェスト
└── nginx-service.yaml            # Serviceマニフェスト
```

---

## 📖 実施した内容

### Step 1: Minikube起動確認
- `minikube status` でクラスタの状態確認

### Step 2: kubectl基本コマンド
- `kubectl get nodes` - ノード一覧
- `kubectl get pods` - Pod一覧
- `kubectl get services` - Service一覧

### Step 3: Deployment作成とService公開
- **nginx-deployment.yaml** を作成
  - `replicas: 3` で3つのPodを起動
  - `nginx:alpine` イメージを使用
- **nginx-service.yaml** を作成
  - `type: NodePort` で外部アクセス可能に
  - `nodePort: 30080` で公開
- ブラウザでNginxのウェルカムページを確認 ✅

### Step 4: スケーリング
- Pod数を3→5→2に動的に変更
- Serviceが自動的にエンドポイントを更新

### Step 5: ローリングアップデート
- `nginx:alpine` → `nginx:1.27` に更新
- **ダウンタイムなし**で全Podを更新 ✅

---

## 🧠 重要な概念

### 1. DeploymentとServiceの関係

```
┌─────────────────────────────────┐
│  Deployment (nginx-deployment)  │  ← Pod管理者
│  replicas: 3                    │
│  template.labels: app=nginx     │
└─────────────────────────────────┘
    ↓ Podを作成・監視
    ↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Pod 1    │  │ Pod 2    │  │ Pod 3    │
│ app=nginx│  │ app=nginx│  │ app=nginx│
└──────────┘  └──────────┘  └──────────┘
    ↑ ラベルで検索
    ↓
┌─────────────────────────────────┐
│  Service (nginx-service)        │  ← アクセスポイント
│  selector: app=nginx            │
│  port: 30080                    │
└─────────────────────────────────┘
```

**重要**: DeploymentとServiceは独立しており、**ラベル**でつながっている（疎結合）

### 2. Selectorの仕組み

- **何を見ているか**: Pod の `metadata.labels`
- **何のために**: 動的に変わるPodを「属性」で柔軟に選択するため

### 3. Minikubeとは

- **定義**: ローカルPC上でKubernetesクラスタを動かすツール
- **目的**: 学習・開発・テスト
- **本番環境との違い**: Minikube（1ノード）vs 本番（複数ノード）

---

## 📊 習得したkubectlコマンド

| コマンド | 用途 |
|---------|------|
| `kubectl get nodes` | ノード一覧の表示 |
| `kubectl get pods` | Pod一覧の表示 |
| `kubectl get pods --show-labels` | Podとラベルを表示 |
| `kubectl get services` | Service一覧の表示 |
| `kubectl apply -f <file>` | マニフェストを適用 |
| `kubectl describe <resource> <name>` | リソースの詳細情報を表示 |
| `kubectl scale deployment <name> --replicas=<N>` | Pod数をN個にスケール |
| `kubectl set image deployment/<name> <container>=<image>` | イメージを更新 |
| `kubectl rollout status deployment/<name>` | ローリングアップデートの進行状況 |
| `minikube service <name> --url` | ServiceのURLを取得 |

---

## 🎓 学んだこと

### 技術的な学び

1. **Kubernetesの宣言的管理**
   - YAMLで「あるべき状態」を定義
   - Kubernetesが自動的にその状態を維持

2. **スケーラビリティ**
   - `kubectl scale` でPod数を動的に変更
   - Serviceが自動的にエンドポイントを更新

3. **無停止デプロイ（ローリングアップデート）**
   - 新しいPodを段階的に起動
   - 古いPodを段階的に終了
   - サービスは常に稼働

4. **疎結合な設計**
   - DeploymentとServiceは独立
   - ラベルで柔軟に連携

### 概念的な学び

1. **Minikubeの位置づけ**
   - 学習・開発のためのローカル環境
   - 本番環境と同じAPIを使える

2. **ラベルの重要性**
   - 名前ではなく属性で管理
   - 動的な環境に適した設計

---

## 🔜 次のステップ

このチュートリアルを完了したら、次は：

1. **未実施の内容を試す**
   - ロールバック（`kubectl rollout undo`）
   - リソースのクリーンアップ

2. **Model-in-Image Patternハンズオン**
   - 実際の機械学習モデルをKubernetesにデプロイ
   - [03_model_in_image_hands_on.md](../03_model_in_image_hands_on.md)

3. **さらに学ぶ**
   - ConfigMapとSecret
   - Volume（永続化ストレージ）
   - Namespace（リソースの論理分割）
   - Ingress（HTTPルーティング）

---

## 📚 関連ドキュメント

- [SESSION_LOG.md](./SESSION_LOG.md) - 詳細な実施記録
- [nginx-deployment.yaml](./nginx-deployment.yaml) - Deploymentマニフェスト
- [nginx-service.yaml](./nginx-service.yaml) - Serviceマニフェスト
- [02_minikube_kubernetes.md](../02_minikube_kubernetes.md) - チュートリアルガイド
- [04_notes/09_docker_kubernetes_basics.md](../../04_notes/09_docker_kubernetes_basics.md) - Docker & Kubernetes入門ガイド

---

**お疲れさまでした！🎉**

Kubernetesの基本を実践的に学ぶことができました。次はより実践的なパターンに挑戦しましょう。
