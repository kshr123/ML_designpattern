# Webシングルパターン 仕様書

## 1. 要件定義

### 1.1 機能要件

このシステムは、Iris分類モデルをWeb APIとして公開し、HTTP経由で推論リクエストを受け付けます。

#### 必須機能
- [ ] **ヘルスチェックエンドポイント**：APIの稼働状況を確認できる
- [ ] **メタデータエンドポイント**：入力データの型・構造・サンプルを取得できる
- [ ] **ラベルエンドポイント**：分類ラベルの一覧を取得できる
- [ ] **テスト推論エンドポイント**：サンプルデータで推論をテストできる
- [ ] **推論エンドポイント（確率値）**：POST リクエストで推論結果（確率値）を取得できる
- [ ] **推論エンドポイント（ラベル名）**：POST リクエストで推論結果（ラベル名）を取得できる

#### オプション機能
- [ ] **ロギング**：全リクエストをログに記録
- [ ] **ジョブID発行**：各リクエストに一意のIDを付与
- [ ] **エラーハンドリング**：適切なHTTPステータスコードとエラーメッセージを返す

### 1.2 非機能要件

| 項目 | 要件 | 理由 |
|------|------|------|
| **パフォーマンス** | レスポンスタイム < 100ms | ユーザー体験の向上 |
| **スケーラビリティ** | gunicornワーカー数を調整可能 | 負荷に応じた調整 |
| **可用性** | ヘルスチェックエンドポイントを提供 | モニタリング・運用の容易さ |
| **セキュリティ** | 入力データのバリデーション | 不正なデータからの保護 |
| **保守性** | コードの可読性とテストカバレッジ100% | 長期的な保守性 |

---

## 2. アーキテクチャ設計

### 2.1 システム構成

```
┌───────────────────────────────────────────────────────┐
│               Docker Container                         │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │  gunicorn (WSGI Server)                      │    │
│  │  - プロセス管理                               │    │
│  │  - 複数ワーカーの起動と管理                   │    │
│  │                                                │    │
│  │  ┌─────────────────────────────────────────┐ │    │
│  │  │  uvicorn workers (4 workers)            │ │    │
│  │  │  - ASGIサーバー                          │ │    │
│  │  │                                           │ │    │
│  │  │  ┌───────────────────────────────────┐  │ │    │
│  │  │  │  FastAPI Application              │  │ │    │
│  │  │  │                                     │  │ │    │
│  │  │  │  ┌─────────────────────────────┐  │  │ │    │
│  │  │  │  │  API Routers                │  │  │ │    │
│  │  │  │  │  - /health                  │  │  │ │    │
│  │  │  │  │  - /metadata                │  │  │ │    │
│  │  │  │  │  - /label                   │  │  │ │    │
│  │  │  │  │  - /predict/test            │  │  │ │    │
│  │  │  │  │  - /predict/test/label      │  │  │ │    │
│  │  │  │  │  - /predict (POST)          │  │  │ │    │
│  │  │  │  │  - /predict/label (POST)    │  │  │ │    │
│  │  │  │  └─────────────────────────────┘  │  │ │    │
│  │  │  │                                     │  │ │    │
│  │  │  │  ┌─────────────────────────────┐  │  │ │    │
│  │  │  │  │  Classifier                 │  │  │ │    │
│  │  │  │  │  - ONNX Runtime             │  │  │ │    │
│  │  │  │  │  - predict()                │  │  │ │    │
│  │  │  │  │  - predict_label()          │  │  │ │    │
│  │  │  │  └─────────────────────────────┘  │  │ │    │
│  │  │  └───────────────────────────────────┘  │ │    │
│  │  └─────────────────────────────────────────┘ │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │  Models                                       │    │
│  │  - iris_svc.onnx (Irisモデル)                │    │
│  │  - label.json (ラベルマッピング)              │    │
│  └──────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────┘
                         ▲
                         │ HTTP Request (Port 8000)
                         │
                    ┌────┴─────┐
                    │  Client  │
                    └──────────┘
```

### 2.2 コンポーネント設計

| コンポーネント | 責務 | 実装 |
|--------------|------|------|
| **gunicorn** | プロセス管理、ワーカーのライフサイクル管理 | run.sh |
| **uvicorn** | ASGIサーバー、非同期処理 | gunicornのワーカー |
| **FastAPI** | ルーティング、リクエスト/レスポンス処理 | src/main.py |
| **APIRouter** | エンドポイント定義、ビジネスロジック呼び出し | src/api/routers/prediction.py |
| **Classifier** | ONNXモデルのロード、推論実行 | src/ml/prediction.py |
| **Configurations** | 環境変数管理、設定値の一元管理 | src/configurations/constants.py |

### 2.3 技術スタック

| カテゴリ | 技術 | バージョン | 用途 |
|---------|------|-----------|------|
| **言語** | Python | 3.13 | アプリケーション開発 |
| **Webフレームワーク** | FastAPI | 0.111.0+ | Web API構築 |
| **WSGIサーバー** | gunicorn | 23.0.0+ | プロセス管理 |
| **ASGIサーバー** | uvicorn | 0.30.0+ | 非同期処理 |
| **推論エンジン** | ONNX Runtime | 1.19.0+ | モデル推論 |
| **データ検証** | pydantic | 2.0.0+ | リクエストデータ検証 |
| **数値計算** | numpy | 2.0.0+ | 配列演算 |
| **コンテナ** | Docker | - | 環境構築・デプロイ |

---

## 3. API仕様

### 3.1 エンドポイント一覧

| Method | Path | 説明 | 認証 |
|--------|------|------|------|
| GET | `/health` | ヘルスチェック | 不要 |
| GET | `/metadata` | メタデータ取得 | 不要 |
| GET | `/label` | ラベル一覧取得 | 不要 |
| GET | `/predict/test` | テスト推論（確率値） | 不要 |
| GET | `/predict/test/label` | テスト推論（ラベル名） | 不要 |
| POST | `/predict` | 推論（確率値） | 不要 |
| POST | `/predict/label` | 推論（ラベル名） | 不要 |

### 3.2 詳細仕様

#### 1. `GET /health`

**説明**: APIの稼働状況を確認

**リクエスト**: なし

**レスポンス**:
```json
{
  "health": "ok"
}
```

**ステータスコード**:
- 200 OK: 正常稼働

---

#### 2. `GET /metadata`

**説明**: 入力データの型・構造・サンプルを取得

**リクエスト**: なし

**レスポンス**:
```json
{
  "data_type": "float32",
  "data_structure": "(1,4)",
  "data_sample": [[5.1, 3.5, 1.4, 0.2]],
  "prediction_type": "float32",
  "prediction_structure": "(1,3)",
  "prediction_sample": [0.9709, 0.0156, 0.0135]
}
```

**ステータスコード**:
- 200 OK: 正常取得

---

#### 3. `GET /label`

**説明**: 分類ラベルの一覧を取得

**リクエスト**: なし

**レスポンス**:
```json
{
  "0": "setosa",
  "1": "versicolor",
  "2": "virginica"
}
```

**ステータスコード**:
- 200 OK: 正常取得

---

#### 4. `GET /predict/test`

**説明**: サンプルデータで推論（確率値）

**リクエスト**: なし

**レスポンス**:
```json
{
  "prediction": [0.9709, 0.0156, 0.0135]
}
```

**ステータスコード**:
- 200 OK: 正常推論

---

#### 5. `GET /predict/test/label`

**説明**: サンプルデータで推論（ラベル名）

**リクエスト**: なし

**レスポンス**:
```json
{
  "prediction": "setosa"
}
```

**ステータスコード**:
- 200 OK: 正常推論

---

#### 6. `POST /predict`

**説明**: 推論（確率値）

**リクエスト**:
```json
{
  "data": [[5.1, 3.5, 1.4, 0.2]]
}
```

**レスポンス**:
```json
{
  "prediction": [0.9709, 0.0156, 0.0135]
}
```

**ステータスコード**:
- 200 OK: 正常推論
- 400 Bad Request: 不正な入力データ
- 422 Unprocessable Entity: データ検証エラー

---

#### 7. `POST /predict/label`

**説明**: 推論（ラベル名）

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

**ステータスコード**:
- 200 OK: 正常推論
- 400 Bad Request: 不正な入力データ
- 422 Unprocessable Entity: データ検証エラー

---

## 4. データモデル

### 4.1 入力データ（Data）

```python
class Data(BaseModel):
    data: List[List[float]] = [[5.1, 3.5, 1.4, 0.2]]
```

**フィールド**:
- `data`: Irisの特徴量（sepal length, sepal width, petal length, petal width）
  - 型: `List[List[float]]`
  - デフォルト: `[[5.1, 3.5, 1.4, 0.2]]`（Iris setosaのサンプル）
  - 制約: 各行は4要素の浮動小数点数

### 4.2 出力データ（Prediction）

**確率値**:
```python
{
    "prediction": List[float]  # [setosa確率, versicolor確率, virginica確率]
}
```

**ラベル名**:
```python
{
    "prediction": str  # "setosa" | "versicolor" | "virginica"
}
```

---

## 5. 環境変数

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|--------------|------|
| `MODEL_FILEPATH` | ONNXモデルファイルのパス | `/app/models/iris_svc.onnx` | ✅ |
| `LABEL_FILEPATH` | ラベルファイルのパス | `/app/models/label.json` | ✅ |
| `API_TITLE` | API名 | `Web Single Pattern` | ❌ |
| `API_DESCRIPTION` | API説明 | `Iris classification API` | ❌ |
| `API_VERSION` | APIバージョン | `0.1.0` | ❌ |
| `HOST` | バインドホスト | `0.0.0.0` | ❌ |
| `PORT` | バインドポート | `8000` | ❌ |
| `WORKERS` | gunicornワーカー数 | `4` | ❌ |

---

## 6. ディレクトリ構成

```
01_web_single_pattern/
├── SPECIFICATION.md          # この仕様書
├── README.md                 # プロジェクト説明
├── pyproject.toml            # Python依存関係
├── requirements.txt          # Python依存関係（gunicorn用）
├── Dockerfile                # Dockerイメージ定義
├── run.sh                    # gunicorn起動スクリプト
├── .python-version           # Pythonバージョン指定
│
├── models/                   # モデルファイル
│   ├── iris_svc.onnx         # Irisモデル（ONNX形式）
│   └── label.json            # ラベルマッピング
│
├── src/                      # アプリケーションコード
│   ├── __init__.py
│   ├── main.py               # FastAPIアプリケーション
│   │
│   ├── api/                  # APIレイヤー
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── prediction.py # エンドポイント定義
│   │
│   ├── ml/                   # 機械学習モジュール
│   │   ├── __init__.py
│   │   └── prediction.py     # 推論クラス
│   │
│   └── configurations/       # 設定管理
│       ├── __init__.py
│       └── constants.py      # 定数・環境変数
│
└── tests/                    # テストコード
    ├── __init__.py
    ├── test_api.py           # APIエンドポイントのテスト
    ├── test_prediction.py    # 推論ロジックのテスト
    ├── test_configuration.py # 設定のテスト
    └── test_results/         # テスト結果
        └── README.md         # pytest出力の読み方
```

---

## 7. 成功基準

以下の条件をすべて満たすことで、実装完了とします：

### 7.1 機能要件
- [ ] 全エンドポイント（7つ）が正常動作する
- [ ] 推論結果の精度が90%以上（テストデータ）
- [ ] エラーハンドリングが適切に実装されている

### 7.2 非機能要件
- [ ] レスポンスタイムが100ms未満
- [ ] 全テストケースがパス（100%カバレッジ）
- [ ] Dockerイメージが正常にビルドできる
- [ ] gunicorn + uvicornが正常に起動する

### 7.3 ドキュメント
- [ ] SPECIFICATION.md（この仕様書）
- [ ] README.md（実装ドキュメント）
- [ ] tests/test_results/README.md（テスト結果の読み方）
- [ ] コード内のdocstring（重要な関数・クラス）

### 7.4 コード品質
- [ ] PEP 8準拠
- [ ] 型ヒント使用
- [ ] 日本語コメント・docstring

---

## 8. 参考情報

- **参考コード**: `01_reference/chapter4_serving_patterns/web_single_pattern/`
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **gunicorn Documentation**: https://docs.gunicorn.org/
- **ONNX Runtime Documentation**: https://onnxruntime.ai/docs/

---

**作成日**: 2025-11-13
**バージョン**: 1.0.0
