# minikube & Kubernetes チュートリアル

**所要時間**: 約40分
**対象**: Kubernetesを初めて使う人

このチュートリアルでは、実際にminikubeでKubernetesクラスタを動かしながら学びます。

---

## 📋 このチュートリアルで学ぶこと

- [ ] minikubeを起動・停止する
- [ ] Podをデプロイする
- [ ] Deploymentでレプリカを管理する
- [ ] Serviceで外部に公開する
- [ ] スケールアウト/インする
- [ ] ローリングアップデートする
- [ ] kubectl コマンドを使いこなす

---

## 🚀 Step 1: minikubeのセットアップ

### 1.1 Docker Desktopを起動

```bash
# Docker Desktopを起動（GUIまたはコマンド）
open -a Docker

# Dockerが起動しているか確認
docker ps
```

### 1.2 minikubeを起動

```bash
# minikubeを起動
/opt/homebrew/bin/minikube start

# または短縮形（エイリアスを設定している場合）
# minikube start
```

**期待される出力**:
```
😄  Darwin 14.6.0 上の minikube v1.37.0
✨  docker ドライバーを使用中
...
🏄  完了しました！kubectl がデフォルトで「minikube」クラスタと「default」ネームスペースを使用するよう設定されました
```

### 1.3 minikubeの状態を確認

```bash
# 状態確認
/opt/homebrew/bin/minikube status
```

**期待される出力**:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

✅ **成功**: すべて "Running" または "Configured" になっている

### 1.4 kubectlの確認

```bash
# kubectlのバージョン確認
/opt/homebrew/bin/kubectl version --client

# クラスタ情報を確認
/opt/homebrew/bin/kubectl cluster-info
```

**期待される出力**:
```
Kubernetes control plane is running at https://127.0.0.1:xxxxx
...
```

---

## 📦 Step 2: 最初のPodをデプロイ

### 2.1 Nginxポッドを作成

```bash
# Nginxポッドを作成
/opt/homebrew/bin/kubectl run my-nginx --image=nginx:alpine --port=80
```

**出力**:
```
pod/my-nginx created
```

### 2.2 Podの状態を確認

```bash
# Pod一覧を表示
/opt/homebrew/bin/kubectl get pods

# 詳細情報を表示
/opt/homebrew/bin/kubectl get pods -o wide
```

**期待される出力**:
```
NAME       READY   STATUS    RESTARTS   AGE
my-nginx   1/1     Running   0          10s
```

**STATUS の意味**:
- `Pending`: スケジュール待ち
- `ContainerCreating`: コンテナ作成中
- `Running`: 実行中 ✅
- `Error`: エラー発生
- `CrashLoopBackOff`: 起動→クラッシュを繰り返している

### 2.3 Podの詳細を確認

```bash
# Pod の詳細情報
/opt/homebrew/bin/kubectl describe pod my-nginx
```

**確認ポイント**:
- `Status`: Running
- `IP`: Pod内部IP
- `Events`: 作成時のイベントログ

### 2.4 Podのログを確認

```bash
# ログを表示
/opt/homebrew/bin/kubectl logs my-nginx

# リアルタイムログ
/opt/homebrew/bin/kubectl logs -f my-nginx
```

**Ctrl + C** で終了

### 2.5 Podにアクセスしてみる

```bash
# Port Forwardを使ってローカルからアクセス
/opt/homebrew/bin/kubectl port-forward pod/my-nginx 8080:80
```

別のターミナルを開いて：

```bash
# アクセステスト
curl http://localhost:8080
```

✅ **成功**: Nginxのデフォルトページが返ってくる

**Ctrl + C** でPort Forwardを終了

### 2.6 Podを削除

```bash
# Podを削除
/opt/homebrew/bin/kubectl delete pod my-nginx

# 削除を確認
/opt/homebrew/bin/kubectl get pods
```

---

## 🔄 Step 3: Deploymentでレプリカを管理

### 3.1 作業ディレクトリを作成

```bash
mkdir -p ~/k8s-tutorial && cd ~/k8s-tutorial
```

### 3.2 Deploymentマニフェストを作成

```bash
cat > nginx-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3  # 3つのPodを作成
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
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
EOF
```

**マニフェストの説明**:
- `replicas: 3`: 3つの同じPodを作成
- `selector`: どのPodを管理するか
- `template`: Podの設計図
- `resources`: リソース制限

### 3.3 Deploymentを適用

```bash
# マニフェストを適用
/opt/homebrew/bin/kubectl apply -f nginx-deployment.yaml
```

**出力**:
```
deployment.apps/nginx-deployment created
```

### 3.4 Deploymentを確認

```bash
# Deployment一覧
/opt/homebrew/bin/kubectl get deployments

# Pod一覧（3つ作成されているはず）
/opt/homebrew/bin/kubectl get pods

# ReplicaSet一覧
/opt/homebrew/bin/kubectl get rs
```

**期待される出力**:
```
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   3/3     3            3           10s

NAME                              READY   STATUS    RESTARTS   AGE
nginx-deployment-xxx-yyy          1/1     Running   0          10s
nginx-deployment-xxx-zzz          1/1     Running   0          10s
nginx-deployment-xxx-www          1/1     Running   0          10s
```

✅ **成功**: 3つのPodすべてが `Running` 状態

### 3.5 Podを手動で削除してみる

```bash
# 1つのPodを削除
/opt/homebrew/bin/kubectl delete pod <pod-name>

# すぐにPodを確認
/opt/homebrew/bin/kubectl get pods
```

**重要**: Deploymentが自動的に新しいPodを作成して、3つを維持します！

---

## 🌐 Step 4: Serviceで外部に公開

### 4.1 Serviceマニフェストを作成

```bash
cat > nginx-service.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: NodePort
  selector:
    app: nginx  # app=nginx のラベルを持つPodに転送
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080  # 外部アクセス用ポート
EOF
```

**Serviceの説明**:
- `type: NodePort`: ノードのポートで公開
- `selector`: どのPodに転送するか
- `port`: Service内部のポート
- `targetPort`: Pod側のポート
- `nodePort`: 外部アクセス用（30000-32767の範囲）

### 4.2 Serviceを適用

```bash
/opt/homebrew/bin/kubectl apply -f nginx-service.yaml
```

### 4.3 Serviceを確認

```bash
# Service一覧
/opt/homebrew/bin/kubectl get services

# 詳細情報
/opt/homebrew/bin/kubectl describe service nginx-service
```

**出力例**:
```
NAME            TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
nginx-service   NodePort   10.96.xxx.xxx   <none>        80:30080/TCP   10s
```

### 4.4 Serviceにアクセス

```bash
# minikube service コマンドでアクセス
/opt/homebrew/bin/minikube service nginx-service --url
```

**出力例**:
```
http://192.168.49.2:30080
```

このURLをブラウザで開くか、curlでアクセス：

```bash
curl $(minikube service nginx-service --url)
```

✅ **成功**: Nginxのデフォルトページが表示される

---

## 📈 Step 5: スケールアウト/イン

### 5.1 レプリカ数を増やす（スケールアウト）

```bash
# 5つに増やす
/opt/homebrew/bin/kubectl scale deployment nginx-deployment --replicas=5

# 確認
/opt/homebrew/bin/kubectl get pods
```

**出力**:
```
NAME                              READY   STATUS    RESTARTS   AGE
nginx-deployment-xxx-aaa          1/1     Running   0          10s
nginx-deployment-xxx-bbb          1/1     Running   0          10s
nginx-deployment-xxx-ccc          1/1     Running   0          30s
nginx-deployment-xxx-ddd          1/1     Running   0          30s
nginx-deployment-xxx-eee          1/1     Running   0          30s
```

### 5.2 レプリカ数を減らす（スケールイン）

```bash
# 2つに減らす
/opt/homebrew/bin/kubectl scale deployment nginx-deployment --replicas=2

# 確認
/opt/homebrew/bin/kubectl get pods
```

**重要**: Kubernetesが自動的に余分なPodを削除します

### 5.3 マニフェストで変更

```bash
# マニフェストを編集
sed -i '' 's/replicas: 3/replicas: 4/' nginx-deployment.yaml

# 適用
/opt/homebrew/bin/kubectl apply -f nginx-deployment.yaml

# 確認
/opt/homebrew/bin/kubectl get pods
```

---

## 🔄 Step 6: ローリングアップデート

### 6.1 イメージバージョンを更新

```bash
# Nginxのバージョンを更新
/opt/homebrew/bin/kubectl set image deployment/nginx-deployment nginx=nginx:1.25-alpine

# ローリングアップデートの状態を監視
/opt/homebrew/bin/kubectl rollout status deployment/nginx-deployment
```

**出力**:
```
Waiting for deployment "nginx-deployment" rollout to finish: 1 out of 4 new replicas have been updated...
Waiting for deployment "nginx-deployment" rollout to finish: 2 out of 4 new replicas have been updated...
...
deployment "nginx-deployment" successfully rolled out
```

**重要**: 1つずつ順番に更新されるので、サービスは停止しません！

### 6.2 ロールアウト履歴を確認

```bash
# 履歴を表示
/opt/homebrew/bin/kubectl rollout history deployment/nginx-deployment
```

**出力例**:
```
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

### 6.3 ロールバック（元に戻す）

```bash
# 前のバージョンに戻す
/opt/homebrew/bin/kubectl rollout undo deployment/nginx-deployment

# 状態を確認
/opt/homebrew/bin/kubectl rollout status deployment/nginx-deployment

# Podのイメージを確認
/opt/homebrew/bin/kubectl get pods -o jsonpath='{.items[0].spec.containers[0].image}'
```

✅ **成功**: `nginx:alpine` に戻っている

---

## 🧹 Step 7: クリーンアップ

### 7.1 リソースを削除

```bash
# Serviceを削除
/opt/homebrew/bin/kubectl delete service nginx-service

# Deploymentを削除（Podも自動削除される）
/opt/homebrew/bin/kubectl delete deployment nginx-deployment

# すべてのリソースを確認
/opt/homebrew/bin/kubectl get all
```

**期待される出力**:
```
NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
service/kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   30m
```

### 7.2 作業ディレクトリを削除

```bash
cd ~ && rm -rf ~/k8s-tutorial
```

### 7.3 minikubeを停止（オプション）

```bash
# minikubeを停止
/opt/homebrew/bin/minikube stop

# または完全に削除
# /opt/homebrew/bin/minikube delete
```

---

## 🔧 よくあるトラブルと解決方法

### ❌ 問題 1: minikube start が失敗する

**原因**: Docker Desktopが起動していない

**解決策**:
```bash
# Docker Desktopを起動
open -a Docker

# 起動を待ってから再実行
/opt/homebrew/bin/minikube start
```

---

### ❌ 問題 2: Pod が `ImagePullBackOff`

**原因**: イメージ名が間違っているか、ネットワークエラー

**解決策**:
```bash
# Podの詳細を確認
/opt/homebrew/bin/kubectl describe pod <pod-name>

# Eventsセクションでエラーを確認
# イメージ名を修正してマニフェストを再適用
```

---

### ❌ 問題 3: Service にアクセスできない

**原因**: Serviceのselectorが間違っている

**解決策**:
```bash
# Serviceの詳細を確認
/opt/homebrew/bin/kubectl describe service <service-name>

# Endpoints が設定されているか確認
/opt/homebrew/bin/kubectl get endpoints <service-name>

# Endpointsが空の場合、selectorとPodのlabelが一致していない
/opt/homebrew/bin/kubectl get pods --show-labels
```

---

### ❌ 問題 4: kubectl コマンドが見つからない

**原因**: パスが通っていない

**解決策**:
```bash
# 完全パスで実行
/opt/homebrew/bin/kubectl get pods

# またはエイリアスを設定
echo 'alias kubectl="/opt/homebrew/bin/kubectl"' >> ~/.zshrc
source ~/.zshrc
```

---

## 📊 kubectl コマンドチートシート

### リソース確認

```bash
# すべてのリソース
kubectl get all

# 特定のリソース
kubectl get pods
kubectl get deployments
kubectl get services
kubectl get nodes

# 詳細情報
kubectl describe <resource> <name>

# YAML形式で表示
kubectl get <resource> <name> -o yaml
```

### リソース作成・更新・削除

```bash
# マニフェストから作成/更新
kubectl apply -f <file.yaml>

# 作成のみ
kubectl create -f <file.yaml>

# 削除
kubectl delete -f <file.yaml>
kubectl delete <resource> <name>
```

### デバッグ

```bash
# ログを確認
kubectl logs <pod>
kubectl logs -f <pod>  # リアルタイム

# コンテナ内でコマンド実行
kubectl exec -it <pod> -- /bin/sh

# Port Forward
kubectl port-forward <pod> <local-port>:<pod-port>
```

### スケーリング

```bash
# レプリカ数を変更
kubectl scale deployment <name> --replicas=<count>

# オートスケール（HPA）
kubectl autoscale deployment <name> --min=2 --max=10 --cpu-percent=80
```

### ロールアウト

```bash
# ローリングアップデート
kubectl set image deployment/<name> <container>=<new-image>

# 状態確認
kubectl rollout status deployment/<name>

# 履歴
kubectl rollout history deployment/<name>

# ロールバック
kubectl rollout undo deployment/<name>
```

---

## ✅ チェックリスト

このチュートリアルで学んだことを確認しましょう：

- [ ] minikubeを起動した
- [ ] Podをデプロイした
- [ ] Podのログを確認した
- [ ] Deploymentを作成した
- [ ] レプリカが自動復旧することを確認した
- [ ] Serviceで外部公開した
- [ ] スケールアウト/インした
- [ ] ローリングアップデートした
- [ ] ロールバックした
- [ ] クリーンアップした

---

## 🎯 次のステップ

Kubernetesの基礎を学んだので、次は実際の機械学習モデルをデプロイしましょう！

👉 [03_model_in_image_hands_on.md](./03_model_in_image_hands_on.md)

---

## 📚 参考資料

- [Kubernetes 公式チュートリアル](https://kubernetes.io/ja/docs/tutorials/)
- [kubectl チートシート](https://kubernetes.io/ja/docs/reference/kubectl/cheatsheet/)
- [minikube 公式ドキュメント](https://minikube.sigs.k8s.io/docs/)
- [04_notes/09_docker_kubernetes_basics.md](../../../04_notes/09_docker_kubernetes_basics.md)

---

**お疲れ様でした！🎉**
