# Horizontal Microservice Pattern - ソースコード概要

## 📚 このディレクトリについて

**Horizontal Microservice Pattern（水平マイクロサービスパターン）** の実装コードです。

複数の専門サービスを水平に配置し、Proxyが`asyncio.gather`で並列リクエストを送信して結果を集約します。

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────────────────┐
│                    ユーザー                          │
└────────────────────┬────────────────────────────────┘
                     │ POST /predict
                     ↓
┌─────────────────────────────────────────────────────┐
│  Proxy Service (proxy/)                             │
│  ┌────────────────────────────────────────────┐    │
│  │  asyncio.gather で並列リクエスト            │    │
│  │  ├→ POST http://service_setosa:8000         │    │
│  │  ├→ POST http://service_versicolor:8000     │    │
│  │  └→ POST http://service_virginica:8000      │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
         │              │              │
         ↓              ↓              ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│Service      │ │Service      │ │Service      │
│Setosa       │ │Versicolor   │ │Virginica    │
│             │ │             │ │             │
│ONNX Model   │ │ONNX Model   │ │ONNX Model   │
│setosa.onnx  │ │versicolor   │ │virginica    │
│             │ │  .onnx      │ │  .onnx      │
│             │ │             │ │             │
│Binary分類:  │ │Binary分類:  │ │Binary分類:  │
│setosa?      │ │versicolor?  │ │virginica?   │
│→ [0.98,0.02]│ │→ [0.00,1.00]│ │→ [0.01,0.99]│
└─────────────┘ └─────────────┘ └─────────────┘
         │              │              │
         └──────────────┴──────────────┘
                        ↓
                 結果を集約して返却
```

## 📁 ディレクトリ構成

```
src/
├── README.md              # このファイル
│
├── proxy/                 # Proxyサービス
│   ├── app.py            # FastAPIアプリ
│   └── routers.py        # 並列実行ロジック（asyncio.gather）
│
├── services/              # 各専門サービス
│   ├── app.py            # FastAPIアプリ
│   └── routers.py        # 推論エンドポイント
│
├── ml/                    # 機械学習ロジック
│   └── predictor.py      # ONNX Runtime推論クライアント
│
├── configurations.py      # 環境変数・設定管理
└── models.py             # Pydanticモデル定義
```

## 🔄 データフロー

```python
# フェーズ1: リクエスト受付（即座）
POST /predict
Body: {"data": [[5.1, 3.5, 1.4, 0.2]]}
  ↓
proxy/routers.py: predict()
  ↓ job_id生成

# フェーズ2: 並列実行（asyncio.gather）
async with httpx.AsyncClient() as client:
    tasks = [
        send_request("setosa", "http://service_setosa:8000"),
        send_request("versicolor", "http://service_versicolor:8000"),
        send_request("virginica", "http://service_virginica:8000"),
    ]
    responses = await asyncio.gather(*tasks)  # 並列実行！

# フェーズ3: 各サービスで推論
services/routers.py: predict()
  ↓
ml/predictor.py: predict()
  ↓
ONNX Runtime推論（各サービス独立）

# フェーズ4: 結果集約
{
  "setosa": {"prediction": [0.98, 0.02]},      # 98% setosaである
  "versicolor": {"prediction": [0.00, 1.00]},  # 0% versicolorである
  "virginica": {"prediction": [0.01, 0.99]}    # 1% virginicaである
}
  ↓ 最良ラベル選択（/predict/labelの場合）
{
  "prediction": {
    "proba": 0.98,
    "label": "setosa"
  }
}
```

## 🚀 主要なクラスとその役割

### 1. Proxy (`proxy/routers.py`)
- **役割**: 3つのサービスに並列リクエストを送信
- **やること**:
  - `POST /predict`: 全サービスに並列リクエスト、結果集約
  - `POST /predict/label`: 最も高い確率のクラスを選択
  - `GET /health/all`: 全サービスのヘルスチェック

### 2. Service Router (`services/routers.py`)
- **役割**: 各専門サービスのエンドポイント
- **やること**:
  - `POST /predict`: ONNX Runtimeで推論実行
  - `GET /health`: ヘルスチェック

### 3. ONNXPredictor (`ml/predictor.py`)
- **役割**: ONNX Runtime推論クライアント
- **やること**:
  - モデル初期化（各サービスが異なるモデルを使用）
  - バイナリ分類（そのクラスか否か）

### 4. ProxyConfig / ServiceConfig (`configurations.py`)
- **役割**: 環境変数管理
- **やること**:
  - ProxyConfig: 各サービスのURL取得
  - ServiceConfig: モードに応じたモデルパス取得

## 🔑 重要な技術ポイント

### 1. asyncio.gather による並列実行

**なぜ並列実行するのか？**
```python
# 逐次実行（遅い）
result1 = await client.post(url1)  # 50ms
result2 = await client.post(url2)  # 50ms
result3 = await client.post(url3)  # 50ms
# 合計: 150ms

# 並列実行（速い）
tasks = [client.post(url1), client.post(url2), client.post(url3)]
results = await asyncio.gather(*tasks)
# 合計: 50ms（最も遅いサービスの時間）
```

### 2. httpx.AsyncClient

**FastAPIの非同期処理**:
- `httpx`は`requests`の非同期版
- `async with`でコネクションプール管理
- 複数リクエストを効率的に処理

### 3. 専門化されたサービス

**各サービスは独立**:
- Setosa Service: `iris_svc_0_setosa.onnx` を使用
- Versicolor Service: `iris_svc_0_versicolor.onnx` を使用
- Virginica Service: `iris_svc_0_virginica.onnx` を使用

**メリット**:
- 各サービスを独立してスケール可能
- 1つのサービスが停止しても他は動作継続
- モデル更新時に特定サービスのみ再デプロイ

### 4. 最良ラベル選択アルゴリズム

```python
best_label = None
best_proba = -1.0

for service_name, result in responses:
    proba = result["prediction"][0]  # そのクラスである確率
    if proba > best_proba:
        best_proba = proba
        best_label = service_name

# 例:
# setosa: 0.98 ← 最大！
# versicolor: 0.00
# virginica: 0.01
# → "setosa" を選択
```

## 🎯 他パターンとの比較

### Batch Pattern vs Horizontal Microservice Pattern

| 項目 | Batch Pattern | Horizontal Microservice |
|------|--------------|------------------------|
| **実行タイミング** | 定期的（60秒ごと） | リクエストごと（即座） |
| **並列化** | ThreadPoolExecutor | asyncio.gather |
| **サービス構成** | API + Job | Proxy + 複数サービス |
| **適用場面** | 大量データの定期処理 | 即座のレスポンス |

### Asynchronous Pattern vs Horizontal Microservice Pattern

| 項目 | Asynchronous Pattern | Horizontal Microservice |
|------|---------------------|------------------------|
| **キュー** | Redis BRPOP | なし（直接HTTP通信） |
| **実行方式** | Worker監視 | 並列HTTPリクエスト |
| **ブロック** | しない（job_id返却） | しない（並列で高速） |
| **適用場面** | 重い推論（数秒） | 軽量推論（数十ms） |

## 🎯 まとめ

このHorizontal Microservice Patternの実装は、以下の特徴があります：

1. **proxy/**: 並列リクエスト送信と結果集約
2. **services/**: 各専門サービス（独立したバイナリ分類器）
3. **ml/**: ONNX Runtime推論

全体として、**複数のマイクロサービスを並列実行することで、高速かつスケーラブルな推論システムを構築できる**というメリットがあります。
