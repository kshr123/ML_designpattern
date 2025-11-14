# Horizontal Microservice Pattern - 仕様書

## 📚 概要

**Horizontal Microservice Pattern（水平マイクロサービスパターン）** は、複数の専門化された推論サービスを水平に配置し、Proxyが並列にリクエストを送信して結果を集約するデザインパターンです。

### パターンの目的

- **専門化**: 各サービスが特定のクラス（タスク）に特化
- **並列処理**: 複数のサービスに同時にリクエストを送信して高速化
- **スケーラビリティ**: 各サービスを独立してスケール可能
- **疎結合**: サービス間の依存関係を最小化

---

## 🏗️ システムアーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                        ユーザー                              │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP POST /predict
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Proxy Service (FastAPI) - Port 9000                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  asyncio.gather で並列リクエスト                      │  │
│  │  ├─→ POST http://service_setosa:8000/predict        │  │
│  │  ├─→ POST http://service_versicolor:8001/predict    │  │
│  │  └─→ POST http://service_virginica:8002/predict     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                  │                  │
         ↓                  ↓                  ↓
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Service Setosa  │ │Service Versicolor│ │Service Virginica│
│   Port: 8000    │ │   Port: 8001     │ │   Port: 8002    │
│                 │ │                  │ │                 │
│  ONNX Model:    │ │  ONNX Model:     │ │  ONNX Model:    │
│  iris_svc_0     │ │  iris_svc_0      │ │  iris_svc_0     │
│  _setosa.onnx   │ │  _versicolor.onnx│ │  _virginica.onnx│
│                 │ │                  │ │                 │
│  Binary分類:    │ │  Binary分類:     │ │  Binary分類:    │
│  setosaか？     │ │  versicolorか？  │ │  virginicaか？  │
│  → [P, 1-P]     │ │  → [P, 1-P]      │ │  → [P, 1-P]     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                  │                  │
         └──────────────────┴──────────────────┘
                            ↓
                    結果を集約して返却
```

### データフロー

```
1. ユーザー → Proxy (POST /predict)
   Body: {"data": [[5.1, 3.5, 1.4, 0.2]]}

2. Proxy → 3つのサービスに並列リクエスト (asyncio.gather)
   - httpx.AsyncClient で非同期HTTP通信
   - 各サービスに同じデータを送信

3. 各サービス → ONNX Runtime で推論
   - Setosa: [0.98, 0.02] (98% setosaである確率)
   - Versicolor: [0.01, 0.99] (1% versicolorである確率)
   - Virginica: [0.01, 0.99] (1% virginicaである確率)

4. Proxy → 結果を集約
   - /predict: 全サービスの結果を返す
   - /predict/label: 最も高い確率のクラスを選択
```

---

## 📋 機能要件

### FR-1: Proxyサービス

#### FR-1.1: ヘルスチェック
- **エンドポイント**: `GET /health`
- **レスポンス**: `{"health": "ok"}`
- **目的**: Proxyサービスの稼働確認

#### FR-1.2: 全サービスヘルスチェック
- **エンドポイント**: `GET /health/all`
- **動作**: 3つのサービス全てに `/health` リクエストを送信
- **レスポンス**:
  ```json
  {
    "setosa": {"health": "ok"},
    "versicolor": {"health": "ok"},
    "virginica": {"health": "ok"}
  }
  ```

#### FR-1.3: メタデータ取得
- **エンドポイント**: `GET /metadata`
- **レスポンス**: 入力データと出力データのスキーマ情報

#### FR-1.4: 推論リクエスト（全サービス）
- **エンドポイント**: `POST /predict`
- **入力**: `{"data": [[...]]}`
- **出力**: 全サービスの推論結果
  ```json
  {
    "setosa": {"prediction": [0.98, 0.02]},
    "versicolor": {"prediction": [0.01, 0.99]},
    "virginica": {"prediction": [0.01, 0.99]}
  }
  ```

#### FR-1.5: 推論リクエスト（ラベル選択）
- **エンドポイント**: `POST /predict/label`
- **入力**: `{"data": [[...]]}`
- **出力**: 最も高い確率のクラス
  ```json
  {
    "prediction": {
      "proba": 0.98,
      "label": "setosa"
    }
  }
  ```

### FR-2: 各専門サービス（Setosa/Versicolor/Virginica）

#### FR-2.1: ヘルスチェック
- **エンドポイント**: `GET /health`
- **レスポンス**: `{"health": "ok"}`

#### FR-2.2: メタデータ取得
- **エンドポイント**: `GET /metadata`
- **レスポンス**: 入力データと出力データのスキーマ情報

#### FR-2.3: 推論リクエスト
- **エンドポイント**: `POST /predict`
- **入力**: `{"data": [[5.1, 3.5, 1.4, 0.2]]}`
- **出力**: バイナリ分類の確率
  ```json
  {
    "prediction": [0.98, 0.02]
  }
  ```
  - `[0]`: そのクラスである確率
  - `[1]`: そのクラスでない確率

#### FR-2.4: テストデータで推論
- **エンドポイント**: `GET /predict/test`
- **動作**: 固定のテストデータで推論実行

---

## 🎯 非機能要件

### NFR-1: パフォーマンス
- **並列処理**: 3つのサービスへのリクエストは並列実行（asyncio.gather）
- **レスポンスタイム**: 並列実行により、単一サービスと同等の速度（約50-100ms）
- **スループット**: 各サービスを独立してスケール可能

### NFR-2: 可用性
- **ヘルスチェック**: 各サービスの稼働状態を確認可能
- **障害分離**: 1つのサービスが停止しても他は動作継続

### NFR-3: スケーラビリティ
- **水平スケーリング**: 各サービスを独立してレプリカ増減可能
- **負荷分散**: Docker Composeのreplicas設定でスケールアウト

### NFR-4: 保守性
- **疎結合**: 各サービスは独立して開発・デプロイ可能
- **モジュール性**: サービスの追加・削除が容易

---

## 🗂️ データモデル

### リクエストモデル

```python
class PredictRequest(BaseModel):
    """推論リクエスト"""
    data: List[List[float]]  # Iris特徴量（4次元）

    # 例
    # {
    #   "data": [
    #     [5.1, 3.5, 1.4, 0.2]  # 萼片長, 萼片幅, 花弁長, 花弁幅
    #   ]
    # }
```

### レスポンスモデル（各サービス）

```python
class PredictionResponse(BaseModel):
    """推論レスポンス（各サービス）"""
    prediction: List[float]  # [そのクラスである確率, そのクラスでない確率]

    # 例（Setosaサービス）
    # {
    #   "prediction": [0.98, 0.02]  # 98% setosaである
    # }
```

### レスポンスモデル（Proxy - 全サービス）

```python
class AllPredictionsResponse(BaseModel):
    """全サービスの推論結果"""
    setosa: PredictionResponse
    versicolor: PredictionResponse
    virginica: PredictionResponse
```

### レスポンスモデル（Proxy - ラベル選択）

```python
class LabelPredictionResponse(BaseModel):
    """ラベル選択結果"""
    prediction: Dict[str, Any]
    # {
    #   "prediction": {
    #     "proba": 0.98,
    #     "label": "setosa"
    #   }
    # }
```

---

## 🔧 技術スタック

### Backend
- **Python**: 3.13
- **FastAPI**: 非同期Webフレームワーク
- **uvicorn**: ASGIサーバー
- **httpx**: 非同期HTTPクライアント
- **asyncio**: 並列実行

### 機械学習
- **ONNX Runtime**: 推論エンジン
- **NumPy**: 数値計算

### インフラ
- **Docker**: コンテナ化
- **Docker Compose**: マルチコンテナオーケストレーション

---

## 📝 API仕様

### Proxy Service (Port 9000)

| メソッド | エンドポイント | 説明 | レスポンス |
|---------|---------------|------|----------|
| GET | `/health` | ヘルスチェック | `{"health": "ok"}` |
| GET | `/health/all` | 全サービスヘルスチェック | 各サービスの状態 |
| GET | `/metadata` | メタデータ取得 | スキーマ情報 |
| POST | `/predict` | 全サービスで推論 | 全サービスの結果 |
| POST | `/predict/label` | 最良ラベル選択 | 最も確率が高いクラス |
| GET | `/predict/get/test` | テストデータで推論(GET) | 全サービスの結果 |
| POST | `/predict/post/test` | テストデータで推論(POST) | 全サービスの結果 |

### Service (Port 8000/8001/8002)

| メソッド | エンドポイント | 説明 | レスポンス |
|---------|---------------|------|----------|
| GET | `/health` | ヘルスチェック | `{"health": "ok"}` |
| GET | `/metadata` | メタデータ取得 | スキーマ情報 |
| POST | `/predict` | 推論実行 | バイナリ分類確率 |
| GET | `/predict/test` | テストデータで推論 | バイナリ分類確率 |

---

## 🎯 成功基準

### 機能面
- [ ] Proxyが3つのサービスに並列リクエストを送信できる
- [ ] asyncio.gatherで並列実行される
- [ ] 各サービスがONNXモデルで推論を実行できる
- [ ] `/predict/label`が最も確率の高いクラスを正しく選択する
- [ ] ヘルスチェックが全サービスで動作する

### 品質面
- [ ] テストカバレッジ80%以上
- [ ] 型チェック（mypy）がパスする
- [ ] リンター（ruff）がパスする
- [ ] フォーマッター（black）適用済み

### 動作面
- [ ] Docker Composeで全サービスが起動する
- [ ] curlでリクエストを送信して正しい結果が返る
- [ ] 並列リクエストが順次実行より高速

---

## 🔄 開発フロー

### Phase 1: 基礎実装
1. `src/configurations.py`: 環境変数と設定
2. `src/models.py`: Pydanticモデル定義
3. `src/ml/predictor.py`: ONNX Runtime推論ロジック

### Phase 2: サービス実装
4. `src/services/app.py`: 各専門サービスのFastAPIアプリ
5. `src/services/routers.py`: 各専門サービスのエンドポイント

### Phase 3: Proxy実装
6. `src/proxy/app.py`: ProxyのFastAPIアプリ
7. `src/proxy/routers.py`: Proxyのエンドポイント（並列実行）

### Phase 4: Docker化
8. `Dockerfile.proxy`: Proxyのイメージ
9. `Dockerfile.service`: 各サービスのイメージ
10. `docker-compose.yml`: マルチコンテナ構成

### Phase 5: テスト・検証
11. 単体テスト（pytest）
12. 統合テスト（docker-compose up）
13. パフォーマンステスト（並列 vs 順次）

---

## 📦 ディレクトリ構成

```
06_horizontal_microservice_pattern/
├── SPECIFICATION.md         # この仕様書
├── README.md                # 実装完了後に作成
├── docker-compose.yml       # マルチコンテナ構成
├── Dockerfile.proxy         # Proxyイメージ
├── Dockerfile.service       # サービスイメージ
├── pyproject.toml           # 依存関係定義
├── .python-version          # Python 3.13
├── models/                  # ONNXモデル
│   ├── iris_svc_0_setosa.onnx
│   ├── iris_svc_0_versicolor.onnx
│   ├── iris_svc_0_virginica.onnx
│   └── label.json
├── src/
│   ├── configurations.py    # 環境変数・設定
│   ├── models.py            # Pydanticモデル
│   ├── proxy/               # Proxyサービス
│   │   ├── app.py
│   │   └── routers.py
│   ├── services/            # 各専門サービス
│   │   ├── app.py
│   │   └── routers.py
│   ├── ml/                  # 機械学習ロジック
│   │   └── predictor.py
│   └── utils/               # ユーティリティ
└── tests/                   # テストコード
    ├── proxy/
    ├── services/
    └── ml/
```

---

## 🚀 実装計画

### Step 1: 設定とモデル定義（TDD）
- [ ] `src/configurations.py` 実装
- [ ] `src/models.py` 実装
- [ ] テスト作成 & Green

### Step 2: 推論ロジック（TDD）
- [ ] `src/ml/predictor.py` 実装
- [ ] テスト作成 & Green

### Step 3: 各サービス（TDD）
- [ ] `src/services/app.py` 実装
- [ ] `src/services/routers.py` 実装
- [ ] テスト作成 & Green

### Step 4: Proxy（TDD）
- [ ] `src/proxy/app.py` 実装
- [ ] `src/proxy/routers.py` 実装（asyncio.gather）
- [ ] テスト作成 & Green

### Step 5: Docker化
- [ ] `Dockerfile.proxy` 作成
- [ ] `Dockerfile.service` 作成
- [ ] `docker-compose.yml` 作成

### Step 6: 統合テスト
- [ ] docker-compose up で起動
- [ ] curlでリクエスト送信
- [ ] 並列実行の動作確認

### Step 7: ドキュメント
- [ ] README.md 作成
- [ ] 学習記録更新

---

## 📝 備考

### Batch Pattern vs Horizontal Microservice Pattern

| 項目 | Batch Pattern | Horizontal Microservice |
|------|--------------|------------------------|
| **実行タイミング** | 定期的（60秒ごと） | リクエストごと |
| **並列化** | ThreadPoolExecutor | asyncio.gather |
| **サービス構成** | API + Job | Proxy + 複数サービス |
| **適用場面** | 大量データの定期処理 | リアルタイム推論 |

### Asynchronous Pattern vs Horizontal Microservice Pattern

| 項目 | Asynchronous Pattern | Horizontal Microservice |
|------|---------------------|------------------------|
| **キュー** | Redis | なし（直接HTTP通信） |
| **Worker** | キュー監視 | HTTPエンドポイント |
| **並列化** | Worker複製 | サービス複製 |
| **適用場面** | 準リアルタイム推論 | 即座のレスポンス |

---

**作成日**: 2025-11-14
**作成者**: Claude Code (TDD)
