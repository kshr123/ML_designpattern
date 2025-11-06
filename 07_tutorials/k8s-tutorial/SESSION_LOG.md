# Kubernetesチュートリアル - セッション記録

## 📅 実施日
2025-11-07

## 🎯 学習内容

### 完了したステップ

#### Step 1: Minikubeの起動確認
- `minikube status` でクラスタの状態確認
- すでに起動済みであることを確認

#### Step 2: kubectl基本コマンド
- `kubectl get nodes` - ノード一覧の表示
- `kubectl get pods` - Pod一覧の表示
- `kubectl get services` - Service一覧の表示

#### Step 3: Deployment作成とService公開
- **nginx-deployment.yaml** を作成
  - `replicas: 3` で3つのPodを起動
  - `nginx:alpine` イメージを使用
  - ラベル `app: nginx` を設定
- **nginx-service.yaml** を作成
  - `type: NodePort` で外部アクセス可能に
  - `selector: app: nginx` でPodを選択
  - `nodePort: 30080` で公開
- `kubectl apply` でマニフェストを適用
- ブラウザでNginxのウェルカムページを確認 ✅

#### Step 4: スケーリング
- **スケールアウト**: `kubectl scale --replicas=5`
  - Pod数を3→5に増加
  - Serviceが自動的に5つのエンドポイントを検出
- **スケールイン**: `kubectl scale --replicas=2`
  - Pod数を5→2に減少
  - 不要なPodが自動的に終了

#### Step 5: ローリングアップデート
- `kubectl set image` でイメージを更新
  - `nginx:alpine` → `nginx:1.27` に変更
- `kubectl rollout status` で進行状況を確認
- **ダウンタイムなし**で全Podを更新 ✅
- 新しいPodを段階的に起動、古いPodを段階的に終了

---

## 🧠 重要な概念の理解

### 1. DeploymentとServiceの関係

| リソース | 役割 | 例え |
|---------|------|------|
| **Deployment** | Podを作成・管理する | 工場（製品を作る） |
| **Service** | Podへのアクセスを提供する | 受付・案内所（製品に案内する） |

**連携の仕組み**:
```
Deployment → Podにラベルを付ける（app=nginx）
             ↓
Service    → ラベルでPodを探す（app=nginx）
             ↓
             トラフィックを振り分け（ロードバランシング）
```

**重要**: DeploymentとServiceは独立しており、**ラベル**でつながっている（疎結合）

### 2. Selectorの仕組み

- **何を見ているか**: Pod の `metadata.labels`
- **何のために**: 動的に変わるPodを「属性」で柔軟に選択するため
- **具体例**:
  ```yaml
  # Deployment: Podにラベルを付ける
  template:
    metadata:
      labels:
        app: nginx

  # Service: ラベルでPodを探す
  selector:
    app: nginx
  ```

### 3. Podの名前

- **自動生成される**: `<deployment-name>-<replicaset-hash>-<random-hash>`
- **例**: `nginx-deployment-54695b766-2fll8`
- **変わる可能性がある**: 再起動やアップデート時
- **だからラベルを使う**: 名前ではなくラベルで管理

### 4. Minikubeとは

- **定義**: ローカルPC上でKubernetesクラスタを動かすツール
- **目的**: 学習・開発・テスト
- **特徴**:
  - 無料
  - 1台のPC内で完結
  - 本番環境と同じAPIを使える
- **本番環境との違い**:
  - Minikube: 1ノード（Master + Worker統合）
  - 本番: 複数ノード（高可用性・スケーラビリティ）

---

## 📝 作成したファイル

### 1. nginx-deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
```

### 2. nginx-service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
      nodePort: 30080
```

---

## ✅ 習得したkubectlコマンド

| コマンド | 用途 |
|---------|------|
| `kubectl get nodes` | ノード一覧の表示 |
| `kubectl get pods` | Pod一覧の表示 |
| `kubectl get pods --show-labels` | Podとラベルを表示 |
| `kubectl get services` | Service一覧の表示 |
| `kubectl get deployments` | Deployment一覧の表示 |
| `kubectl apply -f <file>` | マニフェストを適用 |
| `kubectl describe <resource> <name>` | リソースの詳細情報を表示 |
| `kubectl scale deployment <name> --replicas=<N>` | Pod数をN個にスケール |
| `kubectl set image deployment/<name> <container>=<image>` | イメージを更新 |
| `kubectl rollout status deployment/<name>` | ローリングアップデートの進行状況 |
| `kubectl rollout history deployment/<name>` | デプロイ履歴を表示 |
| `kubectl rollout undo deployment/<name>` | 前のバージョンにロールバック |
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
   - コストをかけずにKubernetesを学べる

2. **ラベルの重要性**
   - 名前ではなく属性で管理
   - 動的な環境に適した設計

3. **Kubernetesの自動管理**
   - Podの再起動
   - スケーリング
   - ローリングアップデート
   - すべて自動化されている

---

## 🔜 次のステップ（未実施）

- [ ] ロールバック（`kubectl rollout undo`）
- [ ] ConfigMapとSecret（設定と機密情報の管理）
- [ ] Volume（永続化ストレージ）
- [ ] Namespace（リソースの論理分割）
- [ ] Ingress（HTTPルーティング）
- [ ] リソースのクリーンアップ

---

## 💡 感想・気づき

- Kubernetesの基本概念（Deployment、Service、Pod、ラベル）を理解できた
- kubectl の基本コマンドに慣れた
- ローリングアップデートの実際の動作を体験できた
- DeploymentとServiceの関係性が明確になった
- Minikubeの役割と位置づけを理解できた
- 疎結合な設計の重要性を実感した

---

## 🔗 関連ドキュメント

- [nginx-deployment.yaml](./nginx-deployment.yaml)
- [nginx-service.yaml](./nginx-service.yaml)
- [07_tutorials/02_minikube_kubernetes.md](../02_minikube_kubernetes.md)
