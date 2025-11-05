# Model-in-Image Pattern ハンズオン

**所要時間**: 約50分
**対象**: 機械学習モデルをKubernetesにデプロイしたい人

このチュートリアルでは、実際のIris分類モデルをDockerイメージに組み込み、Kubernetesにデプロイして本番環境を構築します。

---

## 📋 このチュートリアルで学ぶこと

- [ ] Model-in-Image Patternの仕組みを理解する
- [ ] 学習済みモデルをDockerイメージに組み込む
- [ ] FastAPIでモデルをサービス化する
- [ ] Kubernetesで本番環境を構築する
- [ ] ヘルスチェックとオートスケーリングを設定する
- [ ] 実際のAPIエンドポイントにアクセスする

---

## 🎯 Model-in-Image Patternとは

### パターンの概要

**学習済みモデルファイルをDockerイメージに直接組み込む方式**

```
┌─────────────────────────────────┐
│  Dockerイメージ                 │
│  ┌─────────────────────────┐   │
│  │  アプリケーションコード  │   │
│  │  (FastAPI)              │   │
│  ├─────────────────────────┤   │
│  │  モデルファイル          │   │
│  │  (iris_svc.onnx)        │   │
│  ├─────────────────────────┤   │
│  │  ラベルファイル          │   │
│  │  (label.json)           │   │
│  └─────────────────────────┘   │
└─────────────────────────────────┘
```

### メリット・デメリット

| メリット | デメリット |
|---------|-----------|
| ✅ デプロイが簡単（Pull & Run） | ❌ モデル更新時にイメージ再ビルドが必要 |
| ✅ 高速起動（ダウンロード不要） | ❌ イメージサイズが大きくなる |
| ✅ モデルとコードのバージョン一致 | ❌ 複数モデルの管理が煩雑 |
| ✅ オフライン環境でも動作 | |

### 他のパターンとの比較

- **Model-Load Pattern**: モデルを外部ストレージから起動時にロード
- **Build Pattern**: モデルをビルド時に学習して組み込む

---

## 🚀 Step 1: プロジェクト構造の理解

### 1.1 プロジェクトディレクトリに移動

```bash
cd /Users/kotaro/Desktop/dev/ML_designpattern/03_my_implementations/chapter3_release_patterns/01_model_in_image
```

### 1.2 ディレクトリ構造を確認

```bash
tree -L 2 -I '__pycache__|*.pyc|.venv|htmlcov'
```

**期待される構造**:
```
.
├── Dockerfile            # Dockerイメージのビルド手順
├── README.md
├── SPECIFICATION.md      # 仕様書
├── k8s/                  # Kubernetesマニフェスト
│   ├── deployment.yml    # Pod のデプロイ設定
│   ├── hpa.yml           # オートスケーリング設定
│   ├── namespace.yml     # 名前空間
│   └── service.yml       # 外部公開設定
├── models/               # モデルファイル
│   ├── iris_svc.onnx     # 学習済みONNXモデル（2.1KB）
│   └── label.json        # ラベルマッピング
├── pyproject.toml        # 依存関係
├── run.sh                # 起動スクリプト
├── src/
│   └── model_in_image/
│       ├── __init__.py
│       ├── app.py        # FastAPI アプリ
│       └── prediction.py # 推論ロジック
└── tests/                # テストコード
```

### 1.3 モデルファイルを確認

```bash
# モデルファイルのサイズ確認
ls -lh models/

# ラベルファイルの内容確認
cat models/label.json
```

**label.json の内容**:
```json
{
  "0": "setosa",
  "1": "versicolor",
  "2": "virginica"
}
```

### 1.4 Dockerfileを確認

```bash
cat Dockerfile
```

**重要なポイント**:
- `COPY models/ ./models/` - モデルファイルをイメージに組み込む
- `ENV PYTHONPATH=/app/src` - Python モジュールパス設定
- `HEALTHCHECK` - ヘルスチェック設定

---

## 🐳 Step 2: Dockerイメージのビルド

### 2.1 イメージをビルド

```bash
# イメージをビルド（3-5分かかります）
docker build -t model-in-image-pattern:v1.0 .
```

**ビルドプロセス**:
1. ベースイメージ（Python 3.13）を取得
2. 依存パッケージをインストール
3. アプリケーションコードをコピー
4. **モデルファイルをコピー（重要！）**
5. 起動スクリプトを設定

### 2.2 イメージを確認

```bash
# イメージ一覧
docker images | grep model-in-image-pattern
```

**期待される出力**:
```
model-in-image-pattern   v1.0   sha256:xxx   2 minutes ago   814MB
```

✅ **成功**: イメージサイズは約814MB

### 2.3 イメージの中身を確認

```bash
# イメージの詳細情報
docker inspect model-in-image-pattern:v1.0 | grep -A 10 "Env"
```

**確認ポイント**:
- `MODEL_FILEPATH=/app/models/iris_svc.onnx`
- `LABEL_FILEPATH=/app/models/label.json`
- `PYTHONPATH=/app/src`

---

## 🧪 Step 3: ローカルテスト

### 3.1 コンテナを起動

```bash
# コンテナを起動
docker run -d --name model-test -p 8000:8000 model-in-image-pattern:v1.0

# 起動を待つ（5秒）
sleep 5
```

### 3.2 ヘルスチェック

```bash
# ヘルスチェックエンドポイント
curl http://localhost:8000/health
```

**期待される出力**:
```json
{"health":"ok"}
```

### 3.3 メタデータ取得

```bash
# メタデータエンドポイント
curl http://localhost:8000/metadata | jq .
```

**期待される出力**:
```json
{
  "data_type": "float32",
  "data_structure": "(1,4)",
  "data_sample": [[5.1, 3.5, 1.4, 0.2]],
  "prediction_type": "float32",
  "prediction_structure": "(1,3)",
  "prediction_sample": [0.97093159, 0.01558308, 0.01348537]
}
```

### 3.4 ラベル一覧取得

```bash
# ラベルエンドポイント
curl http://localhost:8000/label | jq .
```

**期待される出力**:
```json
{
  "0": "setosa",
  "1": "versicolor",
  "2": "virginica"
}
```

### 3.5 推論テスト（Setosa）

```bash
# Setosa（品種0）の特徴量で推論
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": [[5.1, 3.5, 1.4, 0.2]]}' | jq .
```

**期待される出力**:
```json
{
  "prediction": [0.977, 0.016, 0.013]  # Setosaの確率が最も高い
}
```

### 3.6 ラベル付き推論

```bash
# ラベル名を返す
curl -X POST http://localhost:8000/predict/label \
  -H "Content-Type: application/json" \
  -d '{"data": [[5.1, 3.5, 1.4, 0.2]]}' | jq .
```

**期待される出力**:
```json
{
  "prediction": "setosa"
}
```

### 3.7 ログを確認

```bash
# コンテナのログ
docker logs model-test
```

### 3.8 クリーンアップ

```bash
# コンテナを停止・削除
docker stop model-test
docker rm model-test
```

✅ **成功**: ローカルで正常に動作することを確認

---

## ☸️ Step 4: Kubernetesにデプロイ

### 4.1 minikubeを起動

```bash
# Docker Desktopを起動
open -a Docker

# minikubeを起動
/opt/homebrew/bin/minikube start

# 状態確認
/opt/homebrew/bin/minikube status
```

### 4.2 イメージをminikubeにロード

```bash
# Dockerイメージをminikubeにロード（1-2分）
/opt/homebrew/bin/minikube image load model-in-image-pattern:v1.0
```

**重要**: minikubeは独自のDocker環境を持つため、イメージをロードする必要があります。

### 4.3 Namespaceを作成

```bash
# Namespaceを作成
/opt/homebrew/bin/kubectl apply -f k8s/namespace.yml

# 確認
/opt/homebrew/bin/kubectl get namespaces
```

**期待される出力**:
```
NAME              STATUS   AGE
model-in-image    Active   5s
...
```

### 4.4 Deploymentをデプロイ

```bash
# Deploymentを作成
/opt/homebrew/bin/kubectl apply -f k8s/deployment.yml

# Podの起動を確認（STATUS が Running になるまで待つ）
/opt/homebrew/bin/kubectl get pods -n model-in-image -w
```

**期待される出力**:
```
NAME                                       READY   STATUS    RESTARTS   AGE
model-in-image-deployment-xxx-yyy         1/1     Running   0          30s
model-in-image-deployment-xxx-zzz         1/1     Running   0          30s
```

✅ **成功**: 2つのPodが `Running` 状態

**Ctrl + C** で監視を終了

### 4.5 Deploymentを確認

```bash
# Deploymentの詳細
/opt/homebrew/bin/kubectl describe deployment model-in-image-deployment -n model-in-image
```

**確認ポイント**:
- `Replicas: 2 desired | 2 updated | 2 total | 2 available`
- `Events` に "Scaled up replica set" が表示される

### 4.6 Serviceを作成

```bash
# Serviceを作成
/opt/homebrew/bin/kubectl apply -f k8s/service.yml

# 確認
/opt/homebrew/bin/kubectl get services -n model-in-image
```

**期待される出力**:
```
NAME                    TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
model-in-image-service  NodePort   10.96.xxx.xxx   <none>        8000:30080/TCP   10s
```

---

## 🌐 Step 5: APIエンドポイントのテスト

### 5.1 ServiceのURLを取得

```bash
# ServiceのURLを取得
/opt/homebrew/bin/minikube service model-in-image-service -n model-in-image --url
```

**出力例**:
```
http://192.168.49.2:30080
```

このURLを環境変数に保存：

```bash
export API_URL=$(minikube service model-in-image-service -n model-in-image --url)
echo $API_URL
```

### 5.2 ヘルスチェック

```bash
curl $API_URL/health | jq .
```

### 5.3 推論テスト（3品種すべて）

```bash
# Setosa
curl -X POST $API_URL/predict/label \
  -H "Content-Type: application/json" \
  -d '{"data": [[5.1, 3.5, 1.4, 0.2]]}' | jq .

# Versicolor
curl -X POST $API_URL/predict/label \
  -H "Content-Type: application/json" \
  -d '{"data": [[5.9, 3.0, 4.2, 1.5]]}' | jq .

# Virginica
curl -X POST $API_URL/predict/label \
  -H "Content-Type: application/json" \
  -d '{"data": [[6.3, 2.9, 5.6, 1.8]]}' | jq .
```

**期待される出力**:
```json
{"prediction":"setosa"}
{"prediction":"versicolor"}
{"prediction":"virginica"}
```

✅ **成功**: 3品種すべて正しく分類できた

### 5.4 APIドキュメントをブラウザで確認

```bash
# SwaggerUIを開く
open ${API_URL}/docs
```

ブラウザでインタラクティブなAPIドキュメントが開きます。

---

## 📈 Step 6: スケーリングとモニタリング

### 6.1 手動スケールアウト

```bash
# レプリカ数を5に増やす
/opt/homebrew/bin/kubectl scale deployment model-in-image-deployment \
  --replicas=5 -n model-in-image

# Podを確認
/opt/homebrew/bin/kubectl get pods -n model-in-image
```

**期待される出力**:
```
NAME                                       READY   STATUS    RESTARTS   AGE
model-in-image-deployment-xxx-aaa         1/1     Running   0          10s
model-in-image-deployment-xxx-bbb         1/1     Running   0          10s
model-in-image-deployment-xxx-ccc         1/1     Running   0          2m
model-in-image-deployment-xxx-ddd         1/1     Running   0          2m
model-in-image-deployment-xxx-eee         1/1     Running   0          2m
```

### 6.2 負荷テスト

```bash
# 100回連続でリクエスト
for i in {1..100}; do
  curl -X POST $API_URL/predict/label \
    -H "Content-Type: application/json" \
    -d '{"data": [[5.1, 3.5, 1.4, 0.2]]}' \
    -s -o /dev/null -w "Request $i: %{http_code}\n"
done
```

**期待される出力**:
```
Request 1: 200
Request 2: 200
...
Request 100: 200
```

### 6.3 ログを確認

```bash
# 特定のPodのログ
POD_NAME=$(kubectl get pods -n model-in-image -o jsonpath='{.items[0].metadata.name}')
/opt/homebrew/bin/kubectl logs $POD_NAME -n model-in-image

# すべてのPodのログ
/opt/homebrew/bin/kubectl logs -l app=model-in-image -n model-in-image --tail=10
```

### 6.4 HPA（オートスケーリング）を設定（オプション）

```bash
# HPAを作成
/opt/homebrew/bin/kubectl apply -f k8s/hpa.yml

# HPA の状態を確認
/opt/homebrew/bin/kubectl get hpa -n model-in-image
```

**期待される出力**:
```
NAME                  REFERENCE                              TARGETS   MINPODS   MAXPODS   AGE
model-in-image-hpa    Deployment/model-in-image-deployment   5%/70%    2         10        10s
```

---

## 🔍 Step 7: デバッグとトラブルシューティング

### 7.1 Pod内部に入る

```bash
# Pod内でシェルを起動
POD_NAME=$(kubectl get pods -n model-in-image -o jsonpath='{.items[0].metadata.name}')
/opt/homebrew/bin/kubectl exec -it $POD_NAME -n model-in-image -- /bin/bash

# Pod内で確認
ls -la /app/models/
cat /app/models/label.json
python -c "import onnxruntime; print(onnxruntime.__version__)"
exit
```

### 7.2 Pod の詳細情報を確認

```bash
/opt/homebrew/bin/kubectl describe pod $POD_NAME -n model-in-image
```

**確認ポイント**:
- `Status`: Running
- `Containers.State.Running`
- `Events`: エラーがないか

### 7.3 Serviceのエンドポイントを確認

```bash
/opt/homebrew/bin/kubectl get endpoints model-in-image-service -n model-in-image
```

**期待される出力**:
```
NAME                    ENDPOINTS                         AGE
model-in-image-service  10.244.0.5:8000,10.244.0.6:8000   5m
```

✅ **成功**: Podの数だけエンドポイントが設定されている

---

## 🧹 Step 8: クリーンアップ

### 8.1 Kubernetesリソースを削除

```bash
# HPA（作成した場合）
/opt/homebrew/bin/kubectl delete -f k8s/hpa.yml

# Service
/opt/homebrew/bin/kubectl delete -f k8s/service.yml

# Deployment
/opt/homebrew/bin/kubectl delete -f k8s/deployment.yml

# Namespace（すべてのリソースが削除される）
/opt/homebrew/bin/kubectl delete -f k8s/namespace.yml

# 確認
/opt/homebrew/bin/kubectl get all -n model-in-image
```

**期待される出力**:
```
No resources found in model-in-image namespace.
```

### 8.2 minikubeを停止（オプション）

```bash
# 停止
/opt/homebrew/bin/minikube stop

# または削除
# /opt/homebrew/bin/minikube delete
```

---

## ✅ チェックリスト

このチュートリアルで学んだことを確認しましょう：

- [ ] Model-in-Image Patternの仕組みを理解した
- [ ] プロジェクト構造を確認した
- [ ] Dockerイメージをビルドした
- [ ] ローカルでテストした
- [ ] イメージをminikubeにロードした
- [ ] Namespaceを作成した
- [ ] Deploymentをデプロイした
- [ ] Serviceで外部公開した
- [ ] APIエンドポイントをテストした
- [ ] スケールアウトした
- [ ] 負荷テストを実施した
- [ ] ログを確認した
- [ ] クリーンアップした

---

## 🎓 学んだこと

### Model-in-Image Pattern の特徴

| 項目 | 説明 |
|------|------|
| **デプロイ** | イメージをPullするだけ |
| **起動速度** | 高速（モデルダウンロード不要） |
| **バージョン管理** | イメージタグでモデルとコードを一元管理 |
| **更新** | イメージ再ビルドが必要 |
| **適用シーン** | モデルサイズが小さい、更新頻度が低い |

### Kubernetes のメリット

- 自動スケーリング（HPA）
- 自動復旧（Podが落ちても再起動）
- ローリングアップデート（無停止更新）
- 負荷分散（Serviceが自動で振り分け）

---

## 🚀 次のステップ

### さらに学ぶ

1. **他のデプロイパターン**
   - Model-Load Pattern（外部ストレージからロード）
   - Build Pattern（ビルド時に学習）

2. **本番環境へ**
   - AWS EKS / GCP GKE / Azure AKS
   - Ingress Controller でHTTPS対応
   - セキュリティポリシー

3. **モニタリング**
   - Prometheus + Grafana
   - ELK Stack（ログ集約）
   - Jaeger（分散トレーシング）

4. **CI/CD**
   - GitHub Actions で自動ビルド・デプロイ
   - ArgoCD で GitOps

---

## 📚 参考資料

- [SPECIFICATION.md](../03_my_implementations/chapter3_release_patterns/01_model_in_image/SPECIFICATION.md) - このプロジェクトの仕様書
- [04_notes/09_docker_kubernetes_basics.md](../04_notes/09_docker_kubernetes_basics.md) - Docker & Kubernetes 入門ガイド
- [06_notes/onnx_inference_patterns.md](../04_notes/06_onnx_inference_patterns.md) - ONNX推論パターン

---

**お疲れ様でした！これで機械学習モデルのKubernetesデプロイができるようになりました！🎉**
