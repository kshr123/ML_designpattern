# model_in_image_pattern 仕様書

## 1. 要件定義

### 1.1 機能要件

- [ ] **F1: モデルファイルのイメージ組み込み**
  - ONNXモデルファイルをDockerイメージに含める
  - ラベルファイル（JSON）をイメージに含める
  - イメージビルド時にモデルが固定される

- [ ] **F2: 推論APIの提供**
  - FastAPIを使用したREST API
  - 確率値を返す推論エンドポイント
  - ラベル名を返す推論エンドポイント

- [ ] **F3: ヘルスチェックとメタデータAPI**
  - `/health`: サーバーの健全性確認
  - `/metadata`: データ構造とサンプル情報
  - `/label`: ラベル一覧の取得

- [ ] **F4: Kubernetesデプロイ**
  - Deploymentでレプリカ管理
  - Serviceで内部アクセス
  - HPA（Horizontal Pod Autoscaler）で自動スケーリング

### 1.2 非機能要件

- **パフォーマンス**
  - 推論レスポンスタイム: < 100ms（単一リクエスト）
  - スループット: > 100 req/sec（4レプリカ時）

- **スケーラビリティ**
  - 最小レプリカ: 3
  - 最大レプリカ: 10
  - CPU使用率50%でスケール

- **可用性**
  - ローリングアップデート対応
  - ヘルスチェックによる自動復旧

- **リソース効率**
  - CPU制限: 500m/pod
  - メモリ制限: 300Mi/pod

## 2. アーキテクチャ設計

### 2.1 システム構成

```
┌─────────────────────────────────────────────────────────────┐
│  Kubernetes Cluster                                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Namespace: model-in-image                             │ │
│  │                                                        │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  Deployment (4 replicas)                         │ │ │
│  │  │                                                  │ │ │
│  │  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐ │ │ │
│  │  │  │ Pod 1  │  │ Pod 2  │  │ Pod 3  │  │ Pod 4  │ │ │ │
│  │  │  │        │  │        │  │        │  │        │ │ │ │
│  │  │  │ Docker │  │ Docker │  │ Docker │  │ Docker │ │ │ │
│  │  │  │ Image  │  │ Image  │  │ Image  │  │ Image  │ │ │ │
│  │  │  │ + Model│  │ + Model│  │ + Model│  │ + Model│ │ │ │
│  │  │  └────────┘  └────────┘  └────────┘  └────────┘ │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │                         │                              │ │
│  │  ┌──────────────────────▼────────────────────────┐   │ │
│  │  │  Service (ClusterIP) - Port 8000              │   │ │
│  │  └───────────────────────────────────────────────┘   │ │
│  │                                                        │ │
│  │  ┌────────────────────────────────────────────────┐  │ │
│  │  │  HPA (3-10 replicas, CPU 50%)                  │  │ │
│  │  └────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Dockerイメージ構成

```
Docker Image
├── /model_in_image_pattern/
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.py              # FastAPIアプリケーション
│   │   │   └── routers/
│   │   │       └── routers.py      # APIエンドポイント
│   │   ├── ml/
│   │   │   └── prediction.py       # 推論ロジック（ONNXRuntime）
│   │   ├── configurations.py       # 設定管理
│   │   └── constants.py            # 定数
│   ├── models/                     # ★モデルファイル（イメージに含む）
│   │   ├── iris_svc.onnx          # ONNXモデル
│   │   └── label.json              # ラベル定義
│   └── run.sh                      # 起動スクリプト
```

### 2.3 コンポーネント設計

| コンポーネント | 責務 | 技術スタック |
|--------------|------|------------|
| **FastAPI** | REST APIサーバー | FastAPI 0.111+ |
| **ONNXRuntime** | モデル推論実行 | onnxruntime 1.18+ |
| **Classifier** | モデル読み込み・推論管理 | Python クラス |
| **Kubernetes Deployment** | レプリカ管理・ローリングアップデート | K8s apps/v1 |
| **Kubernetes Service** | 内部ロードバランシング | K8s ClusterIP |
| **HPA** | 自動スケーリング | K8s autoscaling/v2 |

### 2.4 データフロー

```
1. イメージビルド時
   学習済みモデル → Docker Build → イメージ（モデル含む）

2. デプロイ時
   イメージ → Kubernetes Pull → Pod起動 → モデル読み込み

3. 推論時
   クライアント → Service → Pod → FastAPI → Classifier → ONNXRuntime → 推論結果
```

### 2.5 技術スタック

- **Python**: 3.13
- **Web Framework**: FastAPI 0.111+, Uvicorn 0.30+
- **ML Runtime**: ONNXRuntime 1.18+
- **Container**: Docker
- **Orchestration**: Kubernetes (minikube)
- **Tools**: kubectl, uv

## 3. API仕様

### 3.1 エンドポイント一覧

| Method | Path | Description | Request | Response |
|--------|------|-------------|---------|----------|
| GET | `/health` | ヘルスチェック | - | `{"health": "ok"}` |
| GET | `/metadata` | データ構造情報 | - | メタデータJSON |
| GET | `/label` | ラベル一覧 | - | `{"0": "setosa", ...}` |
| GET | `/predict/test` | テスト推論（確率） | - | `{"prediction": [0.97, ...]}` |
| GET | `/predict/test/label` | テスト推論（ラベル） | - | `{"prediction": "setosa"}` |
| POST | `/predict` | 推論（確率） | Data JSON | `{"prediction": [0.97, ...]}` |
| POST | `/predict/label` | 推論（ラベル） | Data JSON | `{"prediction": "setosa"}` |

### 3.2 データモデル

#### 入力データ（Data）

```json
{
  "data": [
    [5.1, 3.5, 1.4, 0.2]
  ]
}
```

**スキーマ**:
- `data`: `List[List[float]]` - 特徴量の2次元配列
- 形状: `(N, 4)` - Nは推論サンプル数、4はIrisの特徴量数

#### 出力データ（確率）

```json
{
  "prediction": [0.97093159, 0.01558308, 0.01348537]
}
```

**スキーマ**:
- `prediction`: `List[float]` - 各クラスの確率
- 形状: `(3,)` - 3はクラス数

#### 出力データ（ラベル）

```json
{
  "prediction": "setosa"
}
```

**スキーマ**:
- `prediction`: `str` - 予測されたクラスのラベル名

#### ラベル定義（label.json）

```json
{
  "0": "setosa",
  "1": "versicolor",
  "2": "virginica"
}
```

### 3.3 エラーレスポンス

| Status Code | Description | Response Example |
|-------------|-------------|------------------|
| 400 | 不正なリクエスト | `{"detail": "Invalid data format"}` |
| 422 | バリデーションエラー | `{"detail": [{"loc": ["body", "data"], "msg": "field required"}]}` |
| 500 | サーバーエラー | `{"detail": "Internal server error"}` |

## 4. Kubernetes仕様

### 4.1 Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: model-in-image
```

### 4.2 Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-in-image
  namespace: model-in-image
spec:
  replicas: 4
  selector:
    matchLabels:
      app: model-in-image
  template:
    spec:
      containers:
        - name: model-in-image
          image: <your-docker-repo>/model-in-image:0.1.0
          ports:
            - containerPort: 8000
          resources:
            limits:
              cpu: 500m
              memory: "300Mi"
            requests:
              cpu: 500m
              memory: "300Mi"
```

### 4.3 Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: model-in-image
  namespace: model-in-image
spec:
  type: ClusterIP
  ports:
    - port: 8000
      protocol: TCP
  selector:
    app: model-in-image
```

### 4.4 HorizontalPodAutoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-in-image
  namespace: model-in-image
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-in-image
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50
```

## 5. モデル仕様

### 5.1 学習済みモデル

- **モデルファイル**: `models/iris_svc.onnx`
- **フォーマット**: ONNX
- **アルゴリズム**: SVM（Support Vector Machine）
- **データセット**: Iris
- **特徴量**: 4次元（sepal length, sepal width, petal length, petal width）
- **クラス数**: 3（setosa, versicolor, virginica）

### 5.2 ラベルファイル

- **ファイル**: `models/label.json`
- **フォーマット**: JSON
- **内容**: クラスインデックスとラベル名のマッピング

## 6. 環境変数

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `MODEL_FILEPATH` | モデルファイルのパス | `/model_in_image_pattern/models/iris_svc.onnx` | ✅ |
| `LABEL_FILEPATH` | ラベルファイルのパス | `/model_in_image_pattern/models/label.json` | ✅ |
| `LOG_LEVEL` | ログレベル | `DEBUG` | ❌ |
| `LOG_FORMAT` | ログフォーマット | `TEXT` | ❌ |

## 7. ビルドとデプロイ

### 7.1 ビルド手順

```bash
# 1. 学習済みモデルを準備（Chapter 2で作成したモデルを使用）
cp ../../../03_my_implementations/chapter2_training/02_iris_sklearn_svc/models/iris_svc.onnx models/
cp ../../../03_my_implementations/chapter2_training/02_iris_sklearn_svc/models/label.json models/

# 2. Dockerイメージのビルド
docker build -t model-in-image:0.1.0 -f Dockerfile .

# 3. ローカルテスト
docker run -p 8000:8000 model-in-image:0.1.0
```

### 7.2 デプロイ手順

```bash
# 1. minikubeのDockerデーモンを使用（ローカル開発時）
eval $(minikube docker-env)

# 2. イメージをminikubeにロード
minikube image load model-in-image:0.1.0

# 3. Kubernetesにデプロイ
kubectl apply -f manifests/namespace.yml
kubectl apply -f manifests/deployment.yml

# 4. デプロイ確認
kubectl -n model-in-image get pods,deploy,svc,hpa

# 5. ポートフォワードでアクセス
kubectl -n model-in-image port-forward svc/model-in-image 8000:8000
```

### 7.3 削除手順

```bash
kubectl delete namespace model-in-image
```

## 8. テスト戦略

### 8.1 ユニットテスト

- `test_prediction.py`: Classifierクラスのテスト
  - モデル読み込み
  - ラベル読み込み
  - 推論ロジック

### 8.2 統合テスト

- `test_api.py`: FastAPI エンドポイントのテスト
  - 各エンドポイントのレスポンス検証
  - データバリデーション
  - エラーハンドリング

### 8.3 E2Eテスト

- `test_e2e.py`: Kubernetes環境でのテスト
  - デプロイ成功確認
  - Service経由のアクセス
  - 複数Podへのロードバランシング

### 8.4 負荷テスト

- `locust`等を使用した負荷テスト
- スループット測定
  - 目標: > 100 req/sec
- レスポンスタイム測定
  - 目標: < 100ms (p99)

## 9. 成功基準

### 9.1 機能要件

- [ ] モデルとラベルがDockerイメージに正しく組み込まれている
- [ ] 全APIエンドポイントが正常に動作する
- [ ] 推論結果が正確である（参照実装と一致）

### 9.2 非機能要件

- [ ] 推論レスポンスタイム < 100ms
- [ ] 全ユニットテストが成功（カバレッジ > 80%）
- [ ] 全統合テストが成功
- [ ] Kubernetesへのデプロイが成功
- [ ] HPAが正常に動作（負荷時にスケール）

### 9.3 ドキュメント

- [ ] README.mdが完成（セットアップ手順、実行方法）
- [ ] コードに日本語のdocstringとコメントが付いている
- [ ] アーキテクチャ図が含まれている

## 10. 制約事項

### 10.1 技術的制約

- モデルファイルはイメージに固定される（動的変更不可）
- モデル更新時はイメージの再ビルドとデプロイが必要
- イメージサイズがモデルサイズに依存

### 10.2 運用上の制約

- ローカル開発はminikubeを使用
- 本番環境ではDocker Hubまたはプライベートレジストリが必要
- Kubernetesのメトリクスサーバーが必要（HPA使用時）

## 11. model_in_image vs model_load の比較

| 項目 | model_in_image | model_load |
|------|---------------|------------|
| **モデル配置** | イメージ内 | 外部ストレージ |
| **デプロイ速度** | 速い | 遅い（ロード時間） |
| **柔軟性** | 低い（再ビルド必要） | 高い（動的ロード） |
| **イメージサイズ** | 大きい | 小さい |
| **ユースケース** | モデル更新頻度が低い | モデル頻繁更新 |

## 12. 参考

- **元の実装**: `01_reference/chapter3_release_patterns/model_in_image_pattern/`
- **関連パターン**: Chapter 2 - iris_sklearn_svc（モデル学習）
- **Kubernetes公式ドキュメント**: https://kubernetes.io/docs/
- **FastAPI公式ドキュメント**: https://fastapi.tiangolo.com/
