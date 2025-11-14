# app/ - FastAPI アプリケーション

## 📚 このディレクトリについて

このディレクトリには、**Prep Service（前処理サービス）** のHTTPサーバー実装が含まれています。

FastAPIフレームワークを使用して、ユーザーからのHTTPリクエストを受け付け、推論結果を返します。

## 📁 ファイル構成

```
app/
├── README.md           # このファイル
├── app.py             # FastAPIアプリケーション本体
└── routers/
    └── routers.py     # APIエンドポイント定義
```

## 🔄 リクエストの流れ

```
┌─────────────────────────────────────────────────────────────┐
│  1. ユーザーからHTTPリクエスト                               │
│     GET http://localhost:8002/predict/test/label            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  2. app.py - FastAPIアプリケーション                        │
│                                                              │
│     app = FastAPI()                                         │
│     app.include_router(routers.router)  # ルーターを登録    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  3. routers/routers.py - エンドポイント処理                 │
│                                                              │
│     @router.get("/predict/test/label")                      │
│     def predict_test_label():                               │
│         classifier = get_classifier()                       │
│         prediction = classifier.predict_label(image)        │
│         return {"prediction": prediction}                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
                   ml/prediction.py
              （推論ロジック + gRPC通信）
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  4. HTTPレスポンスを返す                                    │
│     {"prediction": "tabby cat"}                             │
└─────────────────────────────────────────────────────────────┘
```

## 📄 app.py - アプリケーション本体

### 役割
- FastAPIアプリケーションのインスタンスを作成
- CORSミドルウェアの設定
- ルーターの登録
- ヘルスチェックエンドポイントの提供

### コード例（簡略版）

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.routers import routers

# FastAPIアプリケーションを作成
app = FastAPI(
    title="Prep-Pred Pattern - Prep Service",
    description="前処理サービス",
    version="1.0.0",
)

# CORS設定（ブラウザからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのドメインを許可
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
)

# ルーターを登録（/predict/* などのエンドポイント）
app.include_router(routers.router)
```

### 起動方法

```bash
# 開発環境
uvicorn src.app.app:app --host 0.0.0.0 --port 8000

# 本番環境（Dockerコンテナ内）
gunicorn src.app.app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## 📄 routers/routers.py - エンドポイント定義

### 役割
- 各APIエンドポイントの実装
- リクエストのバリデーション
- 推論結果の返却

### 提供されるエンドポイント

| エンドポイント | メソッド | 説明 | 例 |
|---------------|---------|------|-----|
| `/health` | GET | ヘルスチェック | `{"health": "healthy"}` |
| `/metadata` | GET | APIメタデータ | 入出力形式の説明 |
| `/label` | GET | ImageNetラベル一覧 | 1000クラスのラベルリスト |
| `/predict/test` | GET | テスト画像で推論（確率） | 確率分布を返す |
| `/predict/test/label` | GET | テスト画像で推論（ラベル） | `{"prediction": "web site"}` |
| `/predict` | POST | Base64画像で推論（確率） | 確率分布を返す |
| `/predict/label` | POST | Base64画像で推論（ラベル） | ラベル名を返す |

### コード例1: ヘルスチェック

```python
@router.get("/health")
def health():
    """
    サービスが正常に動作しているかチェック

    Returns:
        {"health": "healthy"}
    """
    return {"health": "healthy"}
```

**使い方**:
```bash
curl http://localhost:8002/health
# {"health": "healthy"}
```

### コード例2: テスト画像で推論（ラベル）

```python
@router.get("/predict/test/label")
def predict_test_label():
    """
    デフォルトのテスト画像で推論を実行

    内部処理:
    1. Classifierインスタンスを取得
    2. デフォルト画像（10x10の赤色画像）を使用
    3. 推論 → ラベル名を取得
    4. JSONで返す

    Returns:
        {"prediction": "ラベル名"}
    """
    # Classifierインスタンスを取得（シングルトン）
    classifier = get_classifier()

    # デフォルト画像で推論実行
    # Data().data = Image.new("RGB", (10, 10), color=(255, 0, 0))
    prediction = classifier.predict_label(data=Data().data)

    return {"prediction": prediction}
```

**使い方**:
```bash
curl http://localhost:8002/predict/test/label
# {"prediction": "web site"}
```

### コード例3: Base64画像で推論（POST）

```python
class InputData(BaseModel):
    """POSTリクエスト用のデータモデル"""
    data: str  # Base64エンコードされた画像データ

@router.post("/predict/label")
def predict_label(data: InputData):
    """
    ユーザーがアップロードした画像で推論

    Args:
        data: Base64エンコードされた画像データ

    内部処理:
    1. Base64 → バイナリデータにデコード
    2. バイナリ → PIL Imageに変換
    3. 推論実行
    4. ラベル名を返す

    Returns:
        {"prediction": "ラベル名"}
    """
    # Base64デコード
    image_bytes = base64.b64decode(data.data)
    io_bytes = io.BytesIO(image_bytes)
    image_data = Image.open(io_bytes)

    # 推論実行
    classifier = get_classifier()
    prediction = classifier.predict_label(data=image_data)

    return {"prediction": prediction}
```

**使い方**:
```bash
# 画像をBase64エンコード
IMAGE_BASE64=$(base64 -i cat.jpg)

# POSTリクエスト送信
curl -X POST http://localhost:8002/predict/label \
  -H "Content-Type: application/json" \
  -d "{\"data\": \"$IMAGE_BASE64\"}"

# {"prediction": "tabby cat"}
```

## 🔑 重要なポイント

### 1. シングルトンパターン

Classifierインスタンスは1つだけ作成され、再利用されます：

```python
# ml/prediction.py
classifier = None  # グローバル変数

def get_classifier():
    """初回のみClassifierを作成、以降は再利用"""
    global classifier
    if classifier is None:
        classifier = Classifier(...)  # 初回のみ初期化
    return classifier
```

**メリット**:
- モデル読み込みは1回だけ（起動時）
- メモリ効率が良い
- レスポンスが速い

### 2. Pydanticによるバリデーション

```python
class InputData(BaseModel):
    data: str  # 必須フィールド、文字列型

# 自動的にバリデーションされる
@router.post("/predict/label")
def predict_label(data: InputData):
    # data.data は必ず str 型
    pass
```

**メリット**:
- 不正なリクエストを自動で拒否
- 型安全性が向上
- ドキュメント自動生成（Swagger UI）

### 3. 非同期処理

FastAPIは非同期処理に対応していますが、今回は同期関数を使用：

```python
# 同期版（今回）
@router.get("/predict/test/label")
def predict_test_label():
    return classifier.predict_label(...)

# 非同期版（I/O待ちが多い場合）
@router.get("/predict/test/label")
async def predict_test_label():
    return await classifier.predict_label_async(...)
```

## 🛠️ 開発時のヒント

### Swagger UIで動作確認

FastAPIは自動的にAPIドキュメントを生成します：

```bash
# サーバー起動後、ブラウザで開く
http://localhost:8002/docs
```

- すべてのエンドポイントが表示される
- ブラウザから直接テストできる
- リクエスト/レスポンスの形式が確認できる

### ログの確認

```python
from logging import getLogger

logger = getLogger(__name__)

@router.get("/predict/test/label")
def predict_test_label():
    logger.info("Received request for test prediction")
    result = classifier.predict_label(...)
    logger.info(f"Prediction result: {result}")
    return {"prediction": result}
```

### エラーハンドリング

```python
from fastapi import HTTPException

@router.post("/predict/label")
def predict_label(data: InputData):
    try:
        image_bytes = base64.b64decode(data.data)
        image_data = Image.open(io.BytesIO(image_bytes))
        prediction = classifier.predict_label(data=image_data)
        return {"prediction": prediction}
    except Exception as e:
        # エラーをHTTP 500で返す
        raise HTTPException(status_code=500, detail=str(e))
```

## 🎯 まとめ

`app/`ディレクトリは、Prep ServiceのHTTPインターフェースを提供します：

- **app.py**: FastAPIアプリケーションの設定と起動
- **routers/routers.py**: 各エンドポイントの実装

実際の推論ロジックは`ml/`ディレクトリで実装されており、このディレクトリはHTTPリクエストとMLロジックの橋渡しをする役割です。
