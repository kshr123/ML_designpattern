# Model-Load Pattern 仕様書

## 1. 要件定義

### 1.1 機能要件

- [ ] **FR-1**: InitContainerでGCSまたはローカルストレージからモデルファイルをダウンロードできる
- [ ] **FR-2**: ダウンロードしたモデルファイルを共有ボリューム（emptyDir）に保存できる
- [ ] **FR-3**: メインコンテナが起動時に共有ボリュームからモデルを読み込める
- [ ] **FR-4**: FastAPIでREST APIを提供できる
- [ ] **FR-5**: `/health` エンドポイントでヘルスチェックができる
- [ ] **FR-6**: `/metadata` エンドポイントでモデルの入出力形式を取得できる
- [ ] **FR-7**: `/label` エンドポイントでラベル一覧を取得できる
- [ ] **FR-8**: `/predict` エンドポイントで推論（確率値）ができる
- [ ] **FR-9**: `/predict/label` エンドポイントで推論（ラベル名）ができる
- [ ] **FR-10**: 環境変数でモデルファイルパスを変更できる
- [ ] **FR-11**: 環境変数でGCSバケット名・ブロブパスを変更できる

### 1.2 非機能要件

- **パフォーマンス**:
  - 推論レスポンスタイム < 100ms
  - InitContainerのダウンロード時間 < 30秒（モデルサイズに依存）
- **スケーラビリティ**:
  - Horizontal Pod Autoscalerで自動スケーリング
  - 最小3レプリカ、最大10レプリカ
- **可用性**:
  - ヘルスチェックで異常Pod検知
  - ローリングアップデート対応
- **セキュリティ**:
  - 機密情報（GCS認証）は環境変数またはSecretで管理
  - モデルファイルへのアクセス制御
- **保守性**:
  - モデル更新時はDockerイメージ再ビルド不要
  - 環境変数変更のみでモデル切り替え可能

---

## 2. アーキテクチャ設計

### 2.1 システム構成

```
┌─────────────────────────────────────────┐
│             Kubernetes Pod              │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │     InitContainer (model-loader) │  │
│  │  - GCSからモデルダウンロード     │  │
│  │  - /workdir に保存               │  │
│  └──────────────┬───────────────────┘  │
│                 ↓                       │
│  ┌──────────────────────────────────┐  │
│  │         emptyDir Volume          │  │
│  │      /workdir (共有ストレージ)   │  │
│  └──────────────┬───────────────────┘  │
│                 ↓                       │
│  ┌──────────────────────────────────┐  │
│  │   Main Container (API Server)    │  │
│  │  - FastAPI + ONNX Runtime        │  │
│  │  - /workdir からモデル読み込み   │  │
│  │  - 推論サービス提供              │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

### 2.2 コンポーネント設計

#### InitContainer (model-loader)

- **役割**: モデルファイルのダウンロードと配置
- **責務**:
  - GCSまたはローカルストレージからモデルをダウンロード
  - 共有ボリューム（/workdir）にモデルを保存
  - ダウンロード完了後、メインコンテナに制御を渡す
- **入力**:
  - `--gcs_bucket`: GCSバケット名
  - `--gcs_model_blob`: GCSブロブパス
  - `--model_filepath`: ローカル保存先パス
- **出力**: モデルファイル（/workdir/model.onnx）

#### Main Container (API Server)

- **役割**: REST APIによる推論サービス提供
- **責務**:
  - FastAPIサーバの起動
  - モデルの読み込み（/workdirから）
  - 推論リクエストの処理
  - ヘルスチェック応答
- **入力**: 推論リクエスト（JSON）
- **出力**: 推論結果（JSON）

#### emptyDir Volume

- **役割**: InitContainerとメインコンテナ間でファイル共有
- **特性**:
  - Pod削除時にデータも削除される（一時ストレージ）
  - 同一Pod内のコンテナ間でファイル共有可能
  - メモリまたはディスクにマウント可能

### 2.3 技術スタック

- **言語**: Python 3.13
- **Webフレームワーク**: FastAPI
- **機械学習**: ONNX Runtime
- **パッケージマネージャー**: uv
- **コンテナ**: Docker
- **オーケストレーション**: Kubernetes (minikube)
- **ストレージ**:
  - 本番: Google Cloud Storage (GCS)
  - ローカル: ローカルファイルシステム（学習用）
- **共有ボリューム**: emptyDir

---

## 3. API仕様

### 3.1 エンドポイント

| Method | Path            | Description                  |
| ------ | --------------- | ---------------------------- |
| GET    | /health         | ヘルスチェック               |
| GET    | /metadata       | モデルの入出力形式取得       |
| GET    | /label          | ラベル一覧取得               |
| POST   | /predict        | 推論実行（確率値）           |
| POST   | /predict/label  | 推論実行（ラベル名）         |

### 3.2 リクエスト/レスポンス形式

#### GET /health

**レスポンス**:
```json
{
  "health": "ok"
}
```

#### GET /metadata

**レスポンス**:
```json
{
  "data_type": "float32",
  "data_shape": "(1, 4)",
  "data_sample": [[5.1, 3.5, 1.4, 0.2]],
  "prediction_type": "float32",
  "prediction_shape": "(1, 3)",
  "prediction_sample": [0.97, 0.02, 0.01]
}
```

#### GET /label

**レスポンス**:
```json
{
  "0": "setosa",
  "1": "versicolor",
  "2": "virginica"
}
```

#### POST /predict

**リクエスト**:
```json
{
  "data": [[5.1, 3.5, 1.4, 0.2]]
}
```

**レスポンス**:
```json
{
  "prediction": [0.97, 0.02, 0.01]
}
```

#### POST /predict/label

**リクエスト**:
```json
{
  "data": [[5.1, 3.5, 1.4, 0.2]]
}
```

**レスポンス**:
```json
{
  "prediction": "setosa"
}
```

### 3.3 エラーレスポンス

```json
{
  "detail": "エラーメッセージ"
}
```

ステータスコード:
- `400 Bad Request`: 不正なリクエスト
- `500 Internal Server Error`: サーバエラー

---

## 4. データモデル

### 4.1 入力データ

**スキーマ**:
```python
{
  "data": List[List[float]]  # Shape: (batch_size, 4)
}
```

**例**:
```python
{
  "data": [
    [5.1, 3.5, 1.4, 0.2],  # Iris Setosa
    [6.7, 3.0, 5.2, 2.3]   # Iris Virginica
  ]
}
```

### 4.2 出力データ

**確率値（/predict）**:
```python
{
  "prediction": List[float]  # Shape: (3,) - 各クラスの確率
}
```

**ラベル名（/predict/label）**:
```python
{
  "prediction": str  # "setosa", "versicolor", "virginica"
}
```

---

## 5. 環境変数

### 5.1 メインコンテナ

| 環境変数 | デフォルト | 説明 |
|---------|-----------|------|
| `MODEL_FILEPATH` | `/workdir/model.onnx` | モデルファイルパス |
| `LABEL_FILEPATH` | `/workdir/label.json` | ラベルファイルパス |

### 5.2 InitContainer

| 環境変数 | デフォルト | 説明 |
|---------|-----------|------|
| `GCS_BUCKET` | - | GCSバケット名 |
| `GCS_MODEL_BLOB` | - | GCSブロブパス |
| `MODEL_FILEPATH` | `/workdir/model.onnx` | ダウンロード先パス |

---

## 6. ファイル構成

```
02_model_load_pattern/
├── SPECIFICATION.md          # この仕様書
├── README.md                 # 実装説明
├── pyproject.toml            # 依存関係（uv管理）
├── Dockerfile                # メインコンテナ
├── model_loader/             # InitContainerコード
│   ├── Dockerfile
│   ├── __init__.py
│   └── main.py              # モデルダウンロードロジック
├── src/                      # メインコンテナコード
│   ├── __init__.py
│   ├── main.py              # FastAPIアプリ
│   ├── configurations.py    # 設定
│   ├── constants.py         # 定数
│   └── ml/
│       ├── __init__.py
│       └── prediction.py    # 推論ロジック
├── k8s/                      # Kubernetesマニフェスト
│   ├── namespace.yml
│   ├── deployment.yml       # InitContainer + Main Container
│   ├── service.yml
│   └── hpa.yml              # オートスケーリング
├── models/                   # ローカル開発用モデル
│   ├── iris_svc.onnx
│   └── label.json
└── tests/                    # テストコード
    ├── test_unit.py
    └── test_integration.py
```

---

## 7. 成功基準

- [ ] **SC-1**: InitContainerがモデルを正常にダウンロードできる
- [ ] **SC-2**: メインコンテナが共有ボリュームからモデルを読み込める
- [ ] **SC-3**: 全APIエンドポイントが正常に応答する
- [ ] **SC-4**: 推論精度が参考実装と同等である
- [ ] **SC-5**: 全テストケースがパスする（カバレッジ > 80%）
- [ ] **SC-6**: Kubernetesにデプロイして動作確認できる
- [ ] **SC-7**: 環境変数変更でモデルを切り替えられる
- [ ] **SC-8**: HPAでオートスケーリングが動作する
- [ ] **SC-9**: エラーハンドリングが適切である
- [ ] **SC-10**: ログが適切に出力される

---

## 8. Model-in-Image Patternとの比較

| 観点 | Model-in-Image | Model-Load (このパターン) |
|------|----------------|--------------------------|
| **モデル配置** | Dockerイメージに組み込み | 起動時に外部からロード |
| **モデル更新** | イメージ再ビルド必要 | 環境変数変更のみ |
| **イメージサイズ** | 大きい（モデル含む） | 小さい（モデル除く） |
| **起動時間** | 速い | 少し遅い（ダウンロード） |
| **柔軟性** | 低い | 高い |
| **適用シーン** | 小さいモデル、低更新頻度 | 大きいモデル、高更新頻度 |
| **複雑さ** | シンプル | やや複雑（InitContainer） |

---

## 9. 実装の制約事項

### 9.1 ローカル開発

- GCSの代わりにローカルファイルシステムを使用
- InitContainerはローカルモデルをコピーするだけ
- 環境変数 `USE_LOCAL_MODEL=true` で切り替え

### 9.2 本番環境

- GCSを使用してモデルを管理
- IAM認証を設定
- モデルバージョン管理を実施

---

**最終更新**: 2025-11-13
