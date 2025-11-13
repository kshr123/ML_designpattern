# Web Single Pattern - Iris分類API

## 📋 概要

Web Single PatternはシングルDockerコンテナでWeb APIとして推論器を公開するパターンです。gunicorn + uvicorn + FastAPIの構成により、本番環境で堅牢かつ高性能なAPIサービスを提供します。

このプロジェクトでは、ONNX形式のIris分類モデルを使用して、7つのRESTful APIエンドポイントを提供します。

## 🏗️ アーキテクチャ

### システム構成

```
┌─────────────────────────────────────────────────────┐
│                   クライアント                       │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────┐
│           Gunicorn Master Process                   │
│  - ポート8000リッスン                                │
│  - ワーカー管理・負荷分散                            │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────┼───────────┬───────────┐
         ▼           ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
    │ Worker │  │ Worker │  │ Worker │  │ Worker │
    │   1    │  │   2    │  │   3    │  │   4    │
    │(Uvicorn)│ │(Uvicorn)│ │(Uvicorn)│ │(Uvicorn)│
    └────┬───┘  └────┬───┘  └────┬───┘  └────┬───┘
         │           │           │           │
         └───────────┴───────────┴───────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  FastAPI App    │
            │  (src.main:app) │
            └────────┬────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │ Router │  │ Model  │  │ Config │
    └────┬───┘  └────┬───┘  └────────┘
         │           │
         │           ▼
         │    ┌─────────────┐
         │    │ ONNX Runtime│
         │    │  (推論)     │
         │    └─────────────┘
         │
         ▼
    ┌────────────────┐
    │ 7 Endpoints    │
    └────────────────┘
```

### コンポーネント

| コンポーネント | 役割 | ファイル |
|--------------|------|---------|
| **Gunicorn** | プロセス管理・負荷分散 | run.sh |
| **Uvicorn** | ASGIサーバー・非同期実行 | run.sh |
| **FastAPI** | Webフレームワーク | src/main.py |
| **Router** | APIエンドポイント定義 | src/api/routers/prediction.py |
| **Classifier** | ONNX推論ロジック | src/ml/prediction.py |
| **Configurations** | 環境変数管理 | src/configurations/constants.py |

## 🛠️ 技術スタック

### ランタイム
- **Python**: 3.13
- **Docker**: コンテナ化
- **Gunicorn**: 23.0.0+ (WSGIサーバー・プロセス管理)
- **Uvicorn**: 0.30.0+ (ASGIサーバー・非同期処理)

### フレームワーク・ライブラリ
- **FastAPI**: 0.111.0+ (Webフレームワーク)
- **Pydantic**: 2.0.0+ (データバリデーション)
- **ONNX Runtime**: 1.19.0+ (推論エンジン)
- **NumPy**: 2.0.0+ (数値計算)

### 開発ツール
- **pytest**: 9.0.1 (テストフレームワーク)
- **pytest-cov**: カバレッジ測定
- **httpx**: FastAPI統合テスト
- **uv**: パッケージマネージャー

## 📡 API仕様

### エンドポイント一覧

| Method | Path | 説明 | レスポンス例 |
|--------|------|------|-------------|
| GET | `/health` | ヘルスチェック | `{"health": "ok"}` |
| GET | `/metadata` | データ型・構造情報 | メタデータオブジェクト |
| GET | `/label` | ラベル一覧 | `{"0": "setosa", ...}` |
| GET | `/predict/test` | テスト推論（確率値） | `{"prediction": [0.97, ...]}` |
| GET | `/predict/test/label` | テスト推論（ラベル名） | `{"prediction": "setosa"}` |
| POST | `/predict` | 推論（確率値） | `{"prediction": [0.97, ...]}` |
| POST | `/predict/label` | 推論（ラベル名） | `{"prediction": "setosa"}` |

### データ形式

**入力（POST /predict）:**
```json
{
  "data": [[sepal_length, sepal_width, petal_length, petal_width]]
}
```

**例:**
```json
{
  "data": [[5.1, 3.5, 1.4, 0.2]]
}
```

**出力（確率値）:**
```json
{
  "prediction": [setosa確率, versicolor確率, virginica確率]
}
```

**出力（ラベル名）:**
```json
{
  "prediction": "setosa" | "versicolor" | "virginica"
}
```

詳細な仕様は [SPECIFICATION.md](./SPECIFICATION.md) を参照してください。

## 🚀 セットアップ

### 前提条件

- Python 3.13以上
- Docker
- uv（Pythonパッケージマネージャー）

### 1. ローカル開発環境

#### 依存関係のインストール

```bash
# プロジェクトディレクトリに移動
cd 03_my_implementations/chapter4_serving_patterns/01_web_single_pattern

# 仮想環境を作成
uv venv

# 仮想環境を有効化
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

# 依存関係をインストール
uv pip install fastapi uvicorn gunicorn onnxruntime numpy pydantic pytest pytest-cov httpx
```

#### 開発サーバーの起動（Uvicorn単体）

```bash
# ローカル開発用（シングルプロセス）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 本番モード（Gunicorn + Uvicorn）

```bash
# 本番モード（マルチプロセス）
bash run.sh
```

### 2. Docker環境

#### Dockerイメージのビルド

```bash
docker build -t web-single-pattern:latest .
```

#### コンテナの起動

```bash
docker run -d \
  --name web-single-pattern \
  -p 8000:8000 \
  web-single-pattern:latest
```

#### コンテナの停止・削除

```bash
docker stop web-single-pattern
docker rm web-single-pattern
```

## 🧪 テスト

### テスト実行

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ付きで実行
pytest tests/ -v --cov=src --cov-report=html

# 特定のテストファイルのみ実行
pytest tests/test_api.py -v
```

### テスト結果

- **総テスト数**: 41
- **成功率**: 100% (41/41)
- **コードカバレッジ**: 98%
- **実行時間**: 0.60秒

詳細は [tests/test_results/README.md](./tests/test_results/README.md) を参照してください。

## 📝 使い方

### 1. ヘルスチェック

```bash
curl http://localhost:8000/health
```

**レスポンス:**
```json
{"health": "ok"}
```

### 2. メタデータ取得

```bash
curl http://localhost:8000/metadata
```

**レスポンス:**
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

### 3. ラベル一覧

```bash
curl http://localhost:8000/label
```

**レスポンス:**
```json
{
  "0": "setosa",
  "1": "versicolor",
  "2": "virginica"
}
```

### 4. テスト推論（確率値）

```bash
curl http://localhost:8000/predict/test
```

**レスポンス:**
```json
{
  "prediction": [0.9709315896034241, 0.015583082102239132, 0.013485366478562355]
}
```

### 5. テスト推論（ラベル名）

```bash
curl http://localhost:8000/predict/test/label
```

**レスポンス:**
```json
{"prediction": "setosa"}
```

### 6. 推論（確率値）

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"data": [[5.1, 3.5, 1.4, 0.2]]}'
```

**レスポンス:**
```json
{
  "prediction": [0.9709315896034241, 0.015583082102239132, 0.013485366478562355]
}
```

### 7. 推論（ラベル名）

```bash
curl -X POST http://localhost:8000/predict/label \
  -H "Content-Type: application/json" \
  -d '{"data": [[6.3, 3.3, 6.0, 2.5]]}'
```

**レスポンス:**
```json
{"prediction": "virginica"}
```

## 🎓 学んだこと

### 1. **Gunicorn + Uvicornの組み合わせ**

**なぜ組み合わせるのか？**
- **Gunicorn**: プロセス管理、負荷分散、グレースフルシャットダウン
- **Uvicorn**: ASGI対応、非同期処理、高速実行

**メリット:**
- ✅ マルチプロセスでCPUコアを最大活用
- ✅ 1つのワーカーが死んでも他が継続（高可用性）
- ✅ FastAPIの非同期機能を活用
- ✅ ダウンタイムなしでリロード可能

**設定（run.sh）:**
```bash
WORKERS=4  # 4つのプロセス
gunicorn src.main:app \
  -w ${WORKERS} \
  -k uvicorn.workers.UvicornWorker  # Uvicornワーカークラス
```

### 2. **TDD（Test-Driven Development）の実践**

**Red → Green → Refactorサイクル:**
1. **Red**: テストを先に書く（失敗することを確認）
2. **Green**: 実装してテストをパス
3. **Refactor**: コードを改善（エラーハンドリング追加など）

**成果:**
- 41のテストケースで全機能をカバー
- コードカバレッジ98%達成
- エラーハンドリングの漏れを防止

### 3. **エラーハンドリングの重要性**

**不正な入力データへの対応:**
```python
@router.post("/predict")
def predict(data: Data) -> Dict[str, List[float]]:
    try:
        prediction = classifier.predict(data.data)
        return {"prediction": list(prediction)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")
```

**学び:**
- ONNX Runtimeは不正なデータ構造で例外を投げる
- try-exceptで適切にハンドリングし、HTTPException(400)を返す
- ユーザーフレンドリーなエラーメッセージを提供

### 4. **グローバルインスタンスの効率化**

**モデルの読み込みを1回だけ実行:**
```python
# src/ml/prediction.py:99-103
classifier = Classifier(
    model_filepath=ModelConfigurations.model_filepath,
    label_filepath=ModelConfigurations.label_filepath,
)
```

**メリット:**
- アプリケーション起動時に1度だけモデルを読み込む
- 各リクエストでモデルを再読み込みしない（高速化）
- メモリ効率が良い

### 5. **環境変数による設定管理**

**12 Factor Appの原則に従う:**
```python
# src/configurations/constants.py
class ModelConfigurations:
    model_filepath = os.getenv("MODEL_FILEPATH", "models/iris_svc.onnx")
    label_filepath = os.getenv("LABEL_FILEPATH", "models/label.json")
```

**メリット:**
- 環境ごとに設定を切り替え可能
- コードを変更せずにDockerで環境変数を上書き
- デフォルト値でローカル開発が容易

### 6. **FastAPIの自動ドキュメント生成**

FastAPIは自動的にSwagger UIとReDocを生成します：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**メリット:**
- API仕様が自動的にドキュメント化
- 実際にブラウザからAPIをテスト可能
- OpenAPI 3.0仕様に準拠

### 7. **Dockerマルチステージビルドの検討**

**現在の実装:**
- シングルステージ（1つのFROM）

**改善案（マルチステージビルド）:**
```dockerfile
# ビルドステージ
FROM python:3.13 AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 実行ステージ
FROM python:3.13-slim
COPY --from=builder /root/.local /root/.local
COPY ./src /app/src
COPY ./models /app/models
...
```

**メリット:**
- イメージサイズを削減（不要なビルドツールを含まない）
- セキュリティ向上（攻撃面の削減）

## 🔧 改善案

### 1. **ロギングの強化**
- 構造化ログ（JSON形式）
- リクエストID追跡
- パフォーマンスメトリクス

### 2. **メトリクス収集**
- Prometheusメトリクス公開
- レスポンスタイム測定
- エラー率モニタリング

### 3. **レート制限**
- FastAPI Limiterで過負荷防止
- ユーザーごとのクォータ管理

### 4. **キャッシュ**
- 同じ入力データの推論結果をキャッシュ
- Redis等の外部キャッシュ利用

### 5. **バッチ推論対応**
- 複数データの同時推論
- スループット向上

## 📚 参考

- **仕様書**: [SPECIFICATION.md](./SPECIFICATION.md)
- **参考コード**: [01_reference/chapter4_serving_patterns/web_single_pattern/](../../../01_reference/chapter4_serving_patterns/web_single_pattern/)
- **FastAPI公式**: https://fastapi.tiangolo.com/
- **Gunicorn公式**: https://gunicorn.org/
- **Uvicorn公式**: https://www.uvicorn.org/
- **ONNX Runtime**: https://onnxruntime.ai/

## 📄 ライセンス

このプロジェクトは学習目的で作成されたものです。

---

**実装日**: 2025-11-13
**開発者**: kshr123
**パターン**: Web Single Pattern (Chapter 4: Serving Patterns)
