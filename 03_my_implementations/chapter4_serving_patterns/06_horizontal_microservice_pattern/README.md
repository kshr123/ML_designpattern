# Horizontal Microservice Pattern

## 📚 概要

**複数の専門化されたサービスを水平に配置し、Proxyが並列リクエストを送信して結果を集約するパターン**

- **Proxy**: 3つのサービスに`asyncio.gather`で並列リクエスト
- **Service Setosa/Versicolor/Virginica**: 各クラスのバイナリ分類器（ONNX Runtime）

## 🏗️ アーキテクチャ

```
ユーザー
   ↓ POST /predict
Proxy (Port 9100)
   ├→ Service Setosa (Port 9101)      ┐
   ├→ Service Versicolor (Port 9102)  ├→ asyncio.gather（並列実行）
   └→ Service Virginica (Port 9103)   ┘
   ↓ 結果集約
{"setosa": {...}, "versicolor": {...}, "virginica": {...}}
```

## 🚀 クイックスタート

```bash
# 起動
docker compose up -d

# ヘルスチェック
curl http://localhost:9100/health/all

# 推論（全サービス）
curl -X POST http://localhost:9100/predict/post/test

# 推論（最良ラベル選択）
curl -X POST http://localhost:9100/predict/label \
  -H "Content-Type: application/json" \
  -d '{"data": [[5.1, 3.5, 1.4, 0.2]]}'

# 停止
docker compose down
```

## 📖 詳細ドキュメント

- **仕様書**: [SPECIFICATION.md](./SPECIFICATION.md) - 要件定義、API仕様、データモデル
- **テスト結果**: [TEST_RESULTS.md](./TEST_RESULTS.md) - 動作確認証跡（4つのテストケース）
- **ソースコード概要**: [src/README.md](./src/README.md) - アーキテクチャ、データフロー

## 📁 ファイル構成

```
06_horizontal_microservice_pattern/
├── SPECIFICATION.md          # 要件定義（詳細）
├── TEST_RESULTS.md           # 動作確認証跡
├── docker-compose.yml        # 4サービス構成
├── Dockerfile.proxy          # Proxyイメージ
├── Dockerfile.service        # 各サービスイメージ
├── models/                   # ONNXモデル（3種）
└── src/
    ├── proxy/                # Proxyサービス（並列実行）
    ├── services/             # 各専門サービス
    ├── ml/predictor.py       # ONNX Runtime推論
    ├── configurations.py     # 環境変数管理
    └── models.py             # Pydanticモデル
```

## 🎯 重要な実装ポイント

### 1. 並列実行（asyncio.gather）
```python
# src/proxy/routers.py
async with httpx.AsyncClient() as client:
    tasks = [send_request(name, url) for name, url in services.items()]
    responses = await asyncio.gather(*tasks)  # ← 並列実行！
```

### 2. 最良ラベル選択
```python
# 各サービスの確率を比較して最も高いものを選択
for service_name, result in responses:
    proba = result["prediction"][0]
    if proba > best_proba:
        best_proba = proba
        best_label = service_name
```

## 🔗 関連パターン

| パターン | 実行方式 | 適用場面 |
|---------|---------|---------|
| **Horizontal Microservice** | 並列（asyncio.gather） | 複数モデルの結果を集約 |
| Asynchronous Pattern | 非同期（Redis Queue） | 準リアルタイム推論 |
| Batch Pattern | 定期実行（60秒ごと） | 大量データの定期処理 |

---

**実装日**: 2025-11-14
**動作確認**: ✅ 全テスト成功（TEST_RESULTS.md参照）
