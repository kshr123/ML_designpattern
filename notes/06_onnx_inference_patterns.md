# ONNX推論パターン完全ガイド

このガイドでは、ONNXモデルを使った推論の様々なパターンと実装方法を説明します。

## 📋 目次

1. [ONNX基礎](#onnx基礎)
2. [推論パターン一覧](#推論パターン一覧)
3. [パターン1: 同期推論パターン](#パターン1-同期推論パターン)
4. [パターン2: バッチ推論パターン](#パターン2-バッチ推論パターン)
5. [パターン3: 非同期推論パターン](#パターン3-非同期推論パターン)
6. [パターン4: ストリーミング推論パターン](#パターン4-ストリーミング推論パターン)
7. [パターン5: REST APIパターン](#パターン5-rest-apiパターン)
8. [パターン6: gRPCパターン](#パターン6-grpcパターン)
9. [パターン7: サーバーレスパターン](#パターン7-サーバーレスパターン)
10. [パターン選択ガイド](#パターン選択ガイド)
11. [実装順序の推奨](#実装順序の推奨)
12. [ベストプラクティス](#ベストプラクティス)
13. [トラブルシューティング](#トラブルシューティング)

---

## ONNX基礎

### ONNXとは？

**ONNX (Open Neural Network Exchange)** は、機械学習モデルの相互運用可能なフォーマットです。

#### なぜONNXを使うのか？

| 観点 | メリット |
|------|---------|
| **移植性** | 訓練フレームワーク（PyTorch, TensorFlow, scikit-learn）と推論環境を分離 |
| **パフォーマンス** | ONNX Runtimeは高度に最適化されており、元のフレームワークより高速な場合が多い |
| **デプロイ柔軟性** | C++, Java, JavaScript等、様々な言語で推論可能 |
| **モデル最適化** | グラフ最適化、量子化、プルーニングなどの最適化技術を適用可能 |

### ONNX Runtimeとは？

**ONNX Runtime** は、ONNXモデルを実行するための高性能推論エンジンです。

#### 主な特徴

- **クロスプラットフォーム**: Windows, Linux, macOS, モバイル、Webブラウザ
- **ハードウェアアクセラレーション**: CPU, GPU (CUDA), NPU, TPUに対応
- **複数言語対応**: Python, C++, C#, Java, JavaScript
- **本番環境対応**: Microsoftが開発・保守しており、多くの本番システムで使用

### 基本的な使い方

```python
import onnxruntime as ort
import numpy as np

# 1. モデルのロード
session = ort.InferenceSession('model.onnx')

# 2. 入力・出力の情報取得
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

print(f"入力名: {input_name}")
print(f"入力形状: {session.get_inputs()[0].shape}")
print(f"入力型: {session.get_inputs()[0].type}")

# 3. 推論実行
input_data = np.array([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32)
outputs = session.run(None, {input_name: input_data})

# 4. 結果取得
prediction = outputs[0]
print(f"予測結果: {prediction}")
```

---

## 推論パターン一覧

| パターン | 用途 | 複雑度 | パフォーマンス | 実装コスト |
|---------|------|--------|--------------|-----------|
| **1. 同期推論** | バッチ処理、単純なAPI | ⭐ | ⭐⭐ | 低 |
| **2. バッチ推論** | 大量データ処理 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 低 |
| **3. 非同期推論** | 並行リクエスト処理 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 中 |
| **4. ストリーミング推論** | リアルタイム処理 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 高 |
| **5. REST API** | Webアプリ、マイクロサービス | ⭐⭐ | ⭐⭐⭐ | 低 |
| **6. gRPC** | 高性能マイクロサービス | ⭐⭐⭐ | ⭐⭐⭐⭐ | 中 |
| **7. サーバーレス** | イベント駆動、自動スケール | ⭐⭐⭐⭐ | ⭐⭐⭐ | 高 |

---

## パターン1: 同期推論パターン

### 概要

最もシンプルな推論パターン。リクエストごとに1つのデータを処理し、結果を返すまで待機します。

**iris_sklearn_svcプロジェクトで実装済み**のパターンです。

### 適用場面

- バッチ処理スクリプト
- 低トラフィックなAPI
- 開発・テスト環境
- シンプルなCLIツール

### メリット・デメリット

| メリット | デメリット |
|---------|-----------|
| ✅ 実装が簡単 | ❌ スループットが低い |
| ✅ デバッグしやすい | ❌ リソース効率が悪い |
| ✅ エラーハンドリングが直感的 | ❌ 高トラフィックに不向き |

### 実装例

#### 基本的な実装

```python
import onnxruntime as ort
import numpy as np
from typing import Dict, Any

class ONNXPredictor:
    """同期推論を行うシンプルな予測器"""

    def __init__(self, model_path: str):
        """
        Args:
            model_path: ONNXモデルファイルのパス
        """
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def predict(self, data: np.ndarray) -> np.ndarray:
        """
        推論を実行

        Args:
            data: 入力データ (例: shape=(1, 4) for iris)

        Returns:
            予測結果
        """
        # 型を確認・変換
        if data.dtype != np.float32:
            data = data.astype(np.float32)

        # 推論実行
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: data}
        )

        return outputs[0]

    def predict_with_proba(self, data: np.ndarray) -> Dict[str, Any]:
        """
        予測とその確率を返す

        Args:
            data: 入力データ

        Returns:
            予測結果と確率の辞書
        """
        outputs = self.session.run(None, {self.input_name: data.astype(np.float32)})

        return {
            "prediction": outputs[0],
            "probabilities": outputs[1] if len(outputs) > 1 else None
        }

# 使用例
if __name__ == "__main__":
    # 予測器の初期化
    predictor = ONNXPredictor("iris_model.onnx")

    # 単一データの予測
    sample = np.array([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32)
    result = predictor.predict(sample)
    print(f"予測結果: {result[0]}")

    # 確率付き予測
    result_with_proba = predictor.predict_with_proba(sample)
    print(f"予測: {result_with_proba['prediction'][0]}")
    if result_with_proba['probabilities'] is not None:
        print(f"確率: {result_with_proba['probabilities'][0]}")
```

#### エラーハンドリング付き実装

```python
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustONNXPredictor:
    """エラーハンドリングとログを備えた同期予測器"""

    def __init__(self, model_path: str):
        # モデルファイルの存在確認
        if not Path(model_path).exists():
            raise FileNotFoundError(f"モデルファイルが見つかりません: {model_path}")

        try:
            self.session = ort.InferenceSession(model_path)
            self.input_name = self.session.get_inputs()[0].name
            self.input_shape = self.session.get_inputs()[0].shape
            logger.info(f"モデルロード成功: {model_path}")
            logger.info(f"入力形状: {self.input_shape}")
        except Exception as e:
            logger.error(f"モデルのロードに失敗: {e}")
            raise

    def predict(self, data: np.ndarray) -> np.ndarray:
        try:
            # 入力検証
            self._validate_input(data)

            # 型変換
            if data.dtype != np.float32:
                data = data.astype(np.float32)

            # 推論実行
            logger.debug(f"推論開始: shape={data.shape}")
            outputs = self.session.run(None, {self.input_name: data})
            logger.debug(f"推論完了")

            return outputs[0]

        except ValueError as e:
            logger.error(f"入力検証エラー: {e}")
            raise
        except Exception as e:
            logger.error(f"推論エラー: {e}")
            raise

    def _validate_input(self, data: np.ndarray) -> None:
        """入力データの検証"""
        expected_features = self.input_shape[-1]

        if data.ndim != 2:
            raise ValueError(f"入力は2次元配列である必要があります。実際: {data.ndim}次元")

        if data.shape[1] != expected_features:
            raise ValueError(
                f"特徴量数が不正です。期待: {expected_features}, 実際: {data.shape[1]}"
            )

        # 欠損値チェック
        if np.isnan(data).any():
            raise ValueError("入力に欠損値(NaN)が含まれています")

        # 無限大チェック
        if np.isinf(data).any():
            raise ValueError("入力に無限大(inf)が含まれています")
```

### iris_sklearn_svcでの実装

このプロジェクトでは、統合テストで同期推論パターンを使用しています：

```python
# tests/test_integration.py から抜粋

def test_onnx_inference_matches_sklearn_prediction(
    self, trained_pipeline_and_test_data, onnx_model_path
):
    """ONNXとscikit-learnの予測が一致することを確認"""
    trained_model, x_test, _ = trained_pipeline_and_test_data

    # scikit-learnでの予測
    sklearn_predictions = trained_model.predict(x_test)

    # ONNX Runtimeでの予測（同期推論）
    session = ort.InferenceSession(onnx_model_path)
    input_name = session.get_inputs()[0].name
    x_test_float32 = x_test.astype(np.float32)
    onnx_outputs = session.run(None, {input_name: x_test_float32})
    onnx_predictions = onnx_outputs[0]

    # 予測結果の一致を確認
    assert np.array_equal(sklearn_predictions, onnx_predictions)
```

---

## パターン2: バッチ推論パターン

### 概要

複数のデータをまとめて処理することで、スループットを大幅に向上させます。

### 適用場面

- 大量の画像/テキストの一括処理
- 定期的なバッチジョブ
- オフライン推論
- データパイプライン

### メリット・デメリット

| メリット | デメリット |
|---------|-----------|
| ✅ スループットが非常に高い | ❌ リアルタイム性が低い |
| ✅ GPU活用時に特に効果的 | ❌ メモリ使用量が大きい |
| ✅ リソース効率が良い | ❌ バッチサイズの調整が必要 |

### 実装例

#### 基本的なバッチ推論

```python
import onnxruntime as ort
import numpy as np
from typing import List, Iterator
import logging

logger = logging.getLogger(__name__)

class BatchPredictor:
    """バッチ推論を行う予測器"""

    def __init__(self, model_path: str, batch_size: int = 32):
        """
        Args:
            model_path: ONNXモデルのパス
            batch_size: バッチサイズ（デフォルト: 32）
        """
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.batch_size = batch_size
        logger.info(f"BatchPredictor初期化: batch_size={batch_size}")

    def predict_batch(self, data_list: List[np.ndarray]) -> np.ndarray:
        """
        データリストをバッチ処理

        Args:
            data_list: 入力データのリスト

        Returns:
            全ての予測結果を結合した配列
        """
        all_predictions = []

        # バッチに分割して処理
        for batch in self._create_batches(data_list):
            batch_data = np.array(batch, dtype=np.float32)
            outputs = self.session.run(None, {self.input_name: batch_data})
            all_predictions.append(outputs[0])

        # 結果を結合
        return np.concatenate(all_predictions, axis=0)

    def _create_batches(self, data_list: List[np.ndarray]) -> Iterator[List[np.ndarray]]:
        """データリストをバッチに分割"""
        for i in range(0, len(data_list), self.batch_size):
            yield data_list[i:i + self.batch_size]

# 使用例
if __name__ == "__main__":
    predictor = BatchPredictor("iris_model.onnx", batch_size=32)

    # 100個のサンプルを生成
    samples = [np.array([5.1, 3.5, 1.4, 0.2]) for _ in range(100)]

    # バッチ推論実行
    predictions = predictor.predict_batch(samples)
    print(f"処理完了: {len(predictions)}件")
```

#### 動的バッチサイズ調整付き実装

```python
import time
from typing import Optional

class AdaptiveBatchPredictor:
    """動的にバッチサイズを調整する予測器"""

    def __init__(
        self,
        model_path: str,
        initial_batch_size: int = 32,
        max_batch_size: int = 128,
        min_batch_size: int = 8
    ):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.batch_size = initial_batch_size
        self.max_batch_size = max_batch_size
        self.min_batch_size = min_batch_size

        # パフォーマンストラッキング
        self.avg_latency = None

    def predict_batch(self, data_list: List[np.ndarray]) -> np.ndarray:
        """動的バッチサイズでデータを処理"""
        all_predictions = []

        for batch in self._create_batches(data_list):
            start_time = time.time()

            # バッチ推論
            batch_data = np.array(batch, dtype=np.float32)
            outputs = self.session.run(None, {self.input_name: batch_data})
            all_predictions.append(outputs[0])

            # レイテンシを記録
            latency = time.time() - start_time
            self._update_batch_size(latency, len(batch))

        return np.concatenate(all_predictions, axis=0)

    def _update_batch_size(self, latency: float, batch_size: int) -> None:
        """レイテンシに基づいてバッチサイズを調整"""
        # 移動平均を計算
        if self.avg_latency is None:
            self.avg_latency = latency
        else:
            self.avg_latency = 0.9 * self.avg_latency + 0.1 * latency

        # バッチサイズ調整ロジック
        per_sample_latency = latency / batch_size

        # レイテンシが低い = バッチサイズを増やす余地あり
        if per_sample_latency < 0.001 and self.batch_size < self.max_batch_size:
            self.batch_size = min(self.batch_size * 2, self.max_batch_size)
            logger.info(f"バッチサイズ増加: {self.batch_size}")

        # レイテンシが高い = バッチサイズを減らす
        elif per_sample_latency > 0.01 and self.batch_size > self.min_batch_size:
            self.batch_size = max(self.batch_size // 2, self.min_batch_size)
            logger.info(f"バッチサイズ減少: {self.batch_size}")

    def _create_batches(self, data_list: List[np.ndarray]) -> Iterator[List[np.ndarray]]:
        """現在のバッチサイズでデータを分割"""
        for i in range(0, len(data_list), self.batch_size):
            yield data_list[i:i + self.batch_size]
```

#### プログレスバー付き実装

```python
from tqdm import tqdm

class BatchPredictorWithProgress:
    """プログレスバー付きバッチ予測器"""

    def __init__(self, model_path: str, batch_size: int = 32):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.batch_size = batch_size

    def predict_batch(
        self,
        data_list: List[np.ndarray],
        show_progress: bool = True
    ) -> np.ndarray:
        """プログレスバー付きでバッチ処理"""
        all_predictions = []
        batches = list(self._create_batches(data_list))

        # プログレスバーのイテレータ
        iterator = tqdm(batches, desc="推論中") if show_progress else batches

        for batch in iterator:
            batch_data = np.array(batch, dtype=np.float32)
            outputs = self.session.run(None, {self.input_name: batch_data})
            all_predictions.append(outputs[0])

        return np.concatenate(all_predictions, axis=0)

    def _create_batches(self, data_list: List[np.ndarray]) -> Iterator[List[np.ndarray]]:
        for i in range(0, len(data_list), self.batch_size):
            yield data_list[i:i + self.batch_size]

# 使用例
if __name__ == "__main__":
    predictor = BatchPredictorWithProgress("iris_model.onnx", batch_size=32)

    # 1000個のサンプルを処理
    samples = [np.array([5.1, 3.5, 1.4, 0.2]) for _ in range(1000)]
    predictions = predictor.predict_batch(samples)
    # 出力: 推論中: 100%|██████████| 32/32 [00:01<00:00, 20.12it/s]
```

---

## パターン3: 非同期推論パターン

### 概要

I/O待機時間を有効活用し、複数のリクエストを並行処理します。

### 適用場面

- 中〜高トラフィックなWebAPI
- 非同期フレームワーク（FastAPI, aiohttp）との統合
- マイクロサービスアーキテクチャ
- 複数のモデルを並行呼び出し

### メリット・デメリット

| メリット | デメリット |
|---------|-----------|
| ✅ 高いスループット | ❌ 実装が複雑 |
| ✅ リソース効率が良い | ❌ デバッグが難しい |
| ✅ レスポンスタイムが短い | ❌ 並行制御が必要 |

### 実装例

#### asyncioベースの基本実装

```python
import asyncio
import onnxruntime as ort
import numpy as np
from typing import List
from concurrent.futures import ThreadPoolExecutor

class AsyncONNXPredictor:
    """非同期推論を行う予測器"""

    def __init__(self, model_path: str, max_workers: int = 4):
        """
        Args:
            model_path: ONNXモデルのパス
            max_workers: 並行実行する最大ワーカー数
        """
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        logger.info(f"AsyncPredictor初期化: max_workers={max_workers}")

    async def predict_async(self, data: np.ndarray) -> np.ndarray:
        """
        非同期で推論を実行

        Args:
            data: 入力データ

        Returns:
            予測結果
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._predict_sync,
            data
        )
        return result

    def _predict_sync(self, data: np.ndarray) -> np.ndarray:
        """同期的な推論処理（Executorで実行される）"""
        if data.dtype != np.float32:
            data = data.astype(np.float32)

        outputs = self.session.run(None, {self.input_name: data})
        return outputs[0]

    async def predict_many_async(self, data_list: List[np.ndarray]) -> List[np.ndarray]:
        """
        複数のデータを非同期並行処理

        Args:
            data_list: 入力データのリスト

        Returns:
            予測結果のリスト
        """
        tasks = [self.predict_async(data) for data in data_list]
        results = await asyncio.gather(*tasks)
        return results

    def __del__(self):
        """クリーンアップ"""
        self.executor.shutdown(wait=True)

# 使用例
async def main():
    predictor = AsyncONNXPredictor("iris_model.onnx", max_workers=4)

    # 単一データの非同期推論
    sample = np.array([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32)
    result = await predictor.predict_async(sample)
    print(f"予測結果: {result[0]}")

    # 複数データの並行処理
    samples = [np.array([[5.1, 3.5, 1.4, 0.2]]) for _ in range(10)]
    results = await predictor.predict_many_async(samples)
    print(f"処理完了: {len(results)}件")

if __name__ == "__main__":
    asyncio.run(main())
```

#### FastAPI統合例

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="Iris ONNX Async API")

# グローバルな予測器インスタンス
predictor: AsyncONNXPredictor = None

class PredictRequest(BaseModel):
    """予測リクエスト"""
    features: List[float]

    class Config:
        json_schema_extra = {
            "example": {
                "features": [5.1, 3.5, 1.4, 0.2]
            }
        }

class PredictResponse(BaseModel):
    """予測レスポンス"""
    prediction: int
    class_name: str

class BatchPredictRequest(BaseModel):
    """バッチ予測リクエスト"""
    samples: List[List[float]]

class BatchPredictResponse(BaseModel):
    """バッチ予測レスポンス"""
    predictions: List[int]
    count: int

@app.on_event("startup")
async def startup_event():
    """アプリ起動時に予測器を初期化"""
    global predictor
    predictor = AsyncONNXPredictor("iris_model.onnx", max_workers=4)
    logger.info("予測器を初期化しました")

@app.on_event("shutdown")
async def shutdown_event():
    """アプリ終了時にクリーンアップ"""
    global predictor
    if predictor:
        predictor.executor.shutdown(wait=True)
    logger.info("予測器をシャットダウンしました")

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    単一サンプルの予測

    - **features**: Irisの4つの特徴量 [sepal_length, sepal_width, petal_length, petal_width]
    """
    try:
        # 入力検証
        if len(request.features) != 4:
            raise HTTPException(
                status_code=400,
                detail="特徴量は4つ必要です（sepal_length, sepal_width, petal_length, petal_width）"
            )

        # 推論実行
        data = np.array([request.features], dtype=np.float32)
        result = await predictor.predict_async(data)

        # クラス名マッピング
        class_names = ["setosa", "versicolor", "virginica"]
        prediction = int(result[0])

        return PredictResponse(
            prediction=prediction,
            class_name=class_names[prediction]
        )

    except Exception as e:
        logger.error(f"予測エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/batch", response_model=BatchPredictResponse)
async def predict_batch(request: BatchPredictRequest):
    """
    バッチ予測（非同期並行処理）

    - **samples**: 予測したいサンプルのリスト
    """
    try:
        # 入力検証
        for i, sample in enumerate(request.samples):
            if len(sample) != 4:
                raise HTTPException(
                    status_code=400,
                    detail=f"サンプル{i}の特徴量数が不正です"
                )

        # データ準備
        data_list = [
            np.array([sample], dtype=np.float32)
            for sample in request.samples
        ]

        # 非同期並行推論
        results = await predictor.predict_many_async(data_list)
        predictions = [int(result[0]) for result in results]

        return BatchPredictResponse(
            predictions=predictions,
            count=len(predictions)
        )

    except Exception as e:
        logger.error(f"バッチ予測エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "model_loaded": predictor is not None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

使用例：

```bash
# サーバー起動
python async_api.py

# 単一予測
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'

# バッチ予測
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "samples": [
      [5.1, 3.5, 1.4, 0.2],
      [6.2, 2.9, 4.3, 1.3],
      [7.3, 2.9, 6.3, 1.8]
    ]
  }'
```

---

## パターン4: ストリーミング推論パターン

### 概要

継続的に流れてくるデータをリアルタイムで処理します。

### 適用場面

- リアルタイム映像分析
- センサーデータの異常検知
- 音声認識・リアルタイム翻訳
- IoTデバイスからのデータストリーム
- ログ監視・異常検知

### メリット・デメリット

| メリット | デメリット |
|---------|-----------|
| ✅ リアルタイム処理 | ❌ 実装が複雑 |
| ✅ 低レイテンシ | ❌ 状態管理が必要 |
| ✅ スケーラブル | ❌ エラーリカバリが難しい |

### 実装例

#### Queue + Threading実装

```python
import queue
import threading
import time
from typing import Callable, Optional

class StreamingPredictor:
    """ストリーミング推論を行う予測器"""

    def __init__(
        self,
        model_path: str,
        callback: Callable[[np.ndarray, np.ndarray], None],
        max_queue_size: int = 100
    ):
        """
        Args:
            model_path: ONNXモデルのパス
            callback: 推論結果を処理するコールバック関数 (data, result) -> None
            max_queue_size: キューの最大サイズ
        """
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.callback = callback

        # データキュー
        self.input_queue = queue.Queue(maxsize=max_queue_size)

        # ワーカースレッド
        self.worker_thread = None
        self.is_running = False

        logger.info(f"StreamingPredictor初期化: max_queue_size={max_queue_size}")

    def start(self):
        """ストリーミング処理を開始"""
        if self.is_running:
            logger.warning("既に実行中です")
            return

        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_stream, daemon=True)
        self.worker_thread.start()
        logger.info("ストリーミング処理を開始しました")

    def stop(self):
        """ストリーミング処理を停止"""
        if not self.is_running:
            return

        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("ストリーミング処理を停止しました")

    def push_data(self, data: np.ndarray, timeout: float = 1.0) -> bool:
        """
        推論キューにデータを追加

        Args:
            data: 入力データ
            timeout: タイムアウト時間（秒）

        Returns:
            追加に成功したかどうか
        """
        try:
            self.input_queue.put(data, timeout=timeout)
            return True
        except queue.Full:
            logger.warning("キューが満杯です。データをスキップします。")
            return False

    def _process_stream(self):
        """ワーカースレッドで実行される処理ループ"""
        logger.info("ストリーム処理ループを開始")

        while self.is_running:
            try:
                # キューからデータを取得（タイムアウト付き）
                data = self.input_queue.get(timeout=0.1)

                # 推論実行
                if data.dtype != np.float32:
                    data = data.astype(np.float32)

                outputs = self.session.run(None, {self.input_name: data})
                result = outputs[0]

                # コールバック実行
                try:
                    self.callback(data, result)
                except Exception as e:
                    logger.error(f"コールバックエラー: {e}")

                # キューのタスク完了を通知
                self.input_queue.task_done()

            except queue.Empty:
                # タイムアウト - ループを続ける
                continue
            except Exception as e:
                logger.error(f"ストリーム処理エラー: {e}")

        logger.info("ストリーム処理ループを終了")

# 使用例
def result_callback(data: np.ndarray, result: np.ndarray):
    """推論結果を処理するコールバック"""
    print(f"入力: {data[0]} -> 予測: {result[0]}")

if __name__ == "__main__":
    # 予測器の初期化
    predictor = StreamingPredictor(
        "iris_model.onnx",
        callback=result_callback,
        max_queue_size=100
    )

    # ストリーミング開始
    predictor.start()

    try:
        # データを継続的に送信（シミュレーション）
        for i in range(20):
            sample = np.array([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32)
            success = predictor.push_data(sample)
            if success:
                print(f"データ{i}を送信")
            time.sleep(0.5)  # 0.5秒ごとにデータ送信

        # 全てのデータが処理されるまで待機
        predictor.input_queue.join()

    finally:
        # 停止
        predictor.stop()
```

#### asyncio + aiokafka統合例

```python
import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json
import numpy as np

class KafkaStreamingPredictor:
    """Kafkaストリームと統合した推論器"""

    def __init__(
        self,
        model_path: str,
        kafka_servers: List[str],
        input_topic: str,
        output_topic: str
    ):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name

        self.kafka_servers = kafka_servers
        self.input_topic = input_topic
        self.output_topic = output_topic

        self.consumer = None
        self.producer = None

    async def start(self):
        """Kafkaコンシューマー・プロデューサーを起動"""
        # コンシューマー初期化
        self.consumer = AIOKafkaConsumer(
            self.input_topic,
            bootstrap_servers=self.kafka_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        await self.consumer.start()

        # プロデューサー初期化
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()

        logger.info(f"Kafka接続完了: {self.input_topic} -> {self.output_topic}")

    async def stop(self):
        """クリーンアップ"""
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()

    async def process_stream(self):
        """Kafkaストリームを処理"""
        try:
            async for message in self.consumer:
                # メッセージから特徴量を抽出
                data_dict = message.value
                features = data_dict.get("features")

                if not features or len(features) != 4:
                    logger.warning(f"不正なデータをスキップ: {data_dict}")
                    continue

                # 推論実行
                data = np.array([features], dtype=np.float32)
                outputs = self.session.run(None, {self.input_name: data})
                prediction = int(outputs[0][0])

                # 結果をKafkaに送信
                result = {
                    "input_features": features,
                    "prediction": prediction,
                    "timestamp": time.time()
                }
                await self.producer.send(self.output_topic, value=result)

                logger.debug(f"予測完了: {features} -> {prediction}")

        except Exception as e:
            logger.error(f"ストリーム処理エラー: {e}")
            raise

# 使用例
async def main():
    predictor = KafkaStreamingPredictor(
        model_path="iris_model.onnx",
        kafka_servers=["localhost:9092"],
        input_topic="iris-input",
        output_topic="iris-predictions"
    )

    try:
        await predictor.start()
        await predictor.process_stream()
    finally:
        await predictor.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## パターン5: REST APIパターン

### 概要

HTTPベースのRESTful APIとして推論サービスを提供します。

### 適用場面

- Webアプリケーションとの統合
- マイクロサービスアーキテクチャ
- 社内APIサービス
- プロトタイプ・MVP開発

### メリット・デメリット

| メリット | デメリット |
|---------|-----------|
| ✅ 実装が簡単 | ❌ gRPCより低速 |
| ✅ デバッグが容易 | ❌ バイナリデータの扱いが非効率 |
| ✅ 広く使われている | ❌ スキーマ定義が緩い |
| ✅ curlで簡単にテスト可能 | |

### 実装例

#### FastAPI完全実装

```python
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import onnxruntime as ort
import numpy as np
import logging
import time

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリ初期化
app = FastAPI(
    title="Iris Classification API",
    description="ONNX Runtime を使用したIris分類API",
    version="1.0.0"
)

# グローバル変数
_predictor: Optional['IrisPredictor'] = None

class IrisPredictor:
    """ONNX推論クラス"""

    CLASS_NAMES = ["setosa", "versicolor", "virginica"]

    def __init__(self, model_path: str):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        logger.info(f"モデルロード完了: {model_path}")

    def predict(self, data: np.ndarray) -> dict:
        """推論実行"""
        if data.dtype != np.float32:
            data = data.astype(np.float32)

        outputs = self.session.run(None, {self.input_name: data})
        prediction = int(outputs[0][0])

        # 確率情報があれば含める
        probabilities = outputs[1][0].tolist() if len(outputs) > 1 else None

        return {
            "prediction": prediction,
            "class_name": self.CLASS_NAMES[prediction],
            "probabilities": probabilities
        }

# リクエスト/レスポンスモデル
class PredictRequest(BaseModel):
    """予測リクエスト"""
    sepal_length: float = Field(..., ge=0, le=10, description="がく片の長さ (cm)")
    sepal_width: float = Field(..., ge=0, le=10, description="がく片の幅 (cm)")
    petal_length: float = Field(..., ge=0, le=10, description="花びらの長さ (cm)")
    petal_width: float = Field(..., ge=0, le=10, description="花びらの幅 (cm)")

    class Config:
        json_schema_extra = {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2
            }
        }

class PredictResponse(BaseModel):
    """予測レスポンス"""
    prediction: int = Field(..., description="予測されたクラスID (0-2)")
    class_name: str = Field(..., description="予測されたクラス名")
    probabilities: Optional[List[float]] = Field(None, description="各クラスの確率")
    inference_time_ms: float = Field(..., description="推論時間 (ミリ秒)")

class BatchPredictRequest(BaseModel):
    """バッチ予測リクエスト"""
    samples: List[PredictRequest] = Field(..., min_length=1, max_length=100)

class BatchPredictResponse(BaseModel):
    """バッチ予測レスポンス"""
    results: List[PredictResponse]
    total_count: int
    total_inference_time_ms: float

class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""
    status: str
    model_loaded: bool
    timestamp: float

# 依存性注入
def get_predictor() -> IrisPredictor:
    """予測器インスタンスを取得"""
    if _predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="モデルが初期化されていません"
        )
    return _predictor

# ライフサイクルイベント
@app.on_event("startup")
async def startup_event():
    """起動時にモデルをロード"""
    global _predictor
    try:
        _predictor = IrisPredictor("models/iris_model.onnx")
        logger.info("APIサーバー起動完了")
    except Exception as e:
        logger.error(f"モデルロードエラー: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """終了時のクリーンアップ"""
    logger.info("APIサーバーシャットダウン")

# エンドポイント
@app.get("/", tags=["General"])
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Iris Classification API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    ヘルスチェック

    モデルのロード状態とAPIの稼働状況を確認します。
    """
    return HealthResponse(
        status="healthy" if _predictor else "unhealthy",
        model_loaded=_predictor is not None,
        timestamp=time.time()
    )

@app.post(
    "/predict",
    response_model=PredictResponse,
    tags=["Prediction"],
    status_code=status.HTTP_200_OK
)
async def predict(
    request: PredictRequest,
    predictor: IrisPredictor = Depends(get_predictor)
):
    """
    単一サンプルの予測

    Irisの4つの特徴量から品種を予測します。

    - **sepal_length**: がく片の長さ (cm)
    - **sepal_width**: がく片の幅 (cm)
    - **petal_length**: 花びらの長さ (cm)
    - **petal_width**: 花びらの幅 (cm)
    """
    try:
        start_time = time.time()

        # データ準備
        data = np.array([[
            request.sepal_length,
            request.sepal_width,
            request.petal_length,
            request.petal_width
        ]], dtype=np.float32)

        # 推論実行
        result = predictor.predict(data)

        # レスポンス時間計算
        inference_time_ms = (time.time() - start_time) * 1000

        return PredictResponse(
            prediction=result["prediction"],
            class_name=result["class_name"],
            probabilities=result["probabilities"],
            inference_time_ms=inference_time_ms
        )

    except Exception as e:
        logger.error(f"予測エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"予測処理に失敗しました: {str(e)}"
        )

@app.post(
    "/predict/batch",
    response_model=BatchPredictResponse,
    tags=["Prediction"]
)
async def predict_batch(
    request: BatchPredictRequest,
    predictor: IrisPredictor = Depends(get_predictor)
):
    """
    バッチ予測

    複数のサンプルをまとめて予測します（最大100件）。
    """
    try:
        start_time = time.time()
        results = []

        for sample in request.samples:
            sample_start = time.time()

            data = np.array([[
                sample.sepal_length,
                sample.sepal_width,
                sample.petal_length,
                sample.petal_width
            ]], dtype=np.float32)

            result = predictor.predict(data)
            sample_time_ms = (time.time() - sample_start) * 1000

            results.append(PredictResponse(
                prediction=result["prediction"],
                class_name=result["class_name"],
                probabilities=result["probabilities"],
                inference_time_ms=sample_time_ms
            ))

        total_time_ms = (time.time() - start_time) * 1000

        return BatchPredictResponse(
            results=results,
            total_count=len(results),
            total_inference_time_ms=total_time_ms
        )

    except Exception as e:
        logger.error(f"バッチ予測エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"バッチ予測処理に失敗しました: {str(e)}"
        )

# エラーハンドラー
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
```

#### Docker化

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# 依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコピー
COPY . .

# モデルディレクトリ作成
RUN mkdir -p models

# ポート公開
EXPOSE 8000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 起動コマンド
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  iris-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models:ro
    environment:
      - LOG_LEVEL=info
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

#### クライアントサンプル

```python
import requests
import json

class IrisAPIClient:
    """Iris API クライアント"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def predict(self, sepal_length: float, sepal_width: float,
                petal_length: float, petal_width: float) -> dict:
        """単一予測"""
        url = f"{self.base_url}/predict"
        data = {
            "sepal_length": sepal_length,
            "sepal_width": sepal_width,
            "petal_length": petal_length,
            "petal_width": petal_width
        }

        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def predict_batch(self, samples: list) -> dict:
        """バッチ予測"""
        url = f"{self.base_url}/predict/batch"
        data = {"samples": samples}

        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        """ヘルスチェック"""
        url = f"{self.base_url}/health"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

# 使用例
if __name__ == "__main__":
    client = IrisAPIClient()

    # ヘルスチェック
    health = client.health_check()
    print(f"Health: {health}")

    # 単一予測
    result = client.predict(5.1, 3.5, 1.4, 0.2)
    print(f"Prediction: {result['class_name']}")

    # バッチ予測
    samples = [
        {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
        {"sepal_length": 6.2, "sepal_width": 2.9, "petal_length": 4.3, "petal_width": 1.3},
    ]
    batch_result = client.predict_batch(samples)
    print(f"Batch predictions: {batch_result['total_count']} samples")
```

---

## パターン6: gRPCパターン

### 概要

Protocol Buffersを使った高性能RPCフレームワークでサービスを提供します。

### 適用場面

- マイクロサービス間通信
- 高スループットが必要なシステム
- 多言語環境（クライアントが複数言語）
- ストリーミングが必要な場合

### メリット・デメリット

| メリット | デメリット |
|---------|-----------|
| ✅ RESTより高速 | ❌ 学習コストが高い |
| ✅ 型安全 | ❌ デバッグが難しい |
| ✅ ストリーミング対応 | ❌ ブラウザから直接呼べない |
| ✅ 多言語対応 | ❌ セットアップが複雑 |

### 実装例

#### Protocol Buffers定義

```protobuf
// iris_service.proto
syntax = "proto3";

package iris;

// Iris分類サービス
service IrisClassifier {
  // 単一予測
  rpc Predict(PredictRequest) returns (PredictResponse);

  // バッチ予測
  rpc PredictBatch(BatchPredictRequest) returns (BatchPredictResponse);

  // サーバーサイドストリーミング
  rpc PredictStream(stream PredictRequest) returns (stream PredictResponse);
}

// リクエストメッセージ
message PredictRequest {
  float sepal_length = 1;
  float sepal_width = 2;
  float petal_length = 3;
  float petal_width = 4;
}

// レスポンスメッセージ
message PredictResponse {
  int32 prediction = 1;
  string class_name = 2;
  repeated float probabilities = 3;
  float inference_time_ms = 4;
}

// バッチリクエスト
message BatchPredictRequest {
  repeated PredictRequest samples = 1;
}

// バッチレスポンス
message BatchPredictResponse {
  repeated PredictResponse results = 1;
  int32 total_count = 2;
  float total_inference_time_ms = 3;
}
```

#### gRPCサーバー実装

```python
import grpc
from concurrent import futures
import time
import numpy as np
import onnxruntime as ort
import logging

# 生成されたコードをインポート
import iris_service_pb2
import iris_service_pb2_grpc

logger = logging.getLogger(__name__)

class IrisClassifierServicer(iris_service_pb2_grpc.IrisClassifierServicer):
    """Iris分類gRPCサービス"""

    CLASS_NAMES = ["setosa", "versicolor", "virginica"]

    def __init__(self, model_path: str):
        """
        Args:
            model_path: ONNXモデルのパス
        """
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        logger.info(f"gRPCサービス初期化: {model_path}")

    def Predict(self, request, context):
        """単一予測"""
        try:
            start_time = time.time()

            # データ準備
            data = np.array([[
                request.sepal_length,
                request.sepal_width,
                request.petal_length,
                request.petal_width
            ]], dtype=np.float32)

            # 推論
            outputs = self.session.run(None, {self.input_name: data})
            prediction = int(outputs[0][0])
            probabilities = outputs[1][0].tolist() if len(outputs) > 1 else []

            # レスポンス時間
            inference_time_ms = (time.time() - start_time) * 1000

            return iris_service_pb2.PredictResponse(
                prediction=prediction,
                class_name=self.CLASS_NAMES[prediction],
                probabilities=probabilities,
                inference_time_ms=inference_time_ms
            )

        except Exception as e:
            logger.error(f"予測エラー: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return iris_service_pb2.PredictResponse()

    def PredictBatch(self, request, context):
        """バッチ予測"""
        try:
            start_time = time.time()
            results = []

            for sample in request.samples:
                sample_response = self.Predict(sample, context)
                results.append(sample_response)

            total_time_ms = (time.time() - start_time) * 1000

            return iris_service_pb2.BatchPredictResponse(
                results=results,
                total_count=len(results),
                total_inference_time_ms=total_time_ms
            )

        except Exception as e:
            logger.error(f"バッチ予測エラー: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return iris_service_pb2.BatchPredictResponse()

    def PredictStream(self, request_iterator, context):
        """ストリーミング予測"""
        try:
            for request in request_iterator:
                yield self.Predict(request, context)

        except Exception as e:
            logger.error(f"ストリーム予測エラー: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

def serve(model_path: str, port: int = 50051, max_workers: int = 10):
    """gRPCサーバーを起動"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))

    iris_service_pb2_grpc.add_IrisClassifierServicer_to_server(
        IrisClassifierServicer(model_path), server
    )

    server.add_insecure_port(f'[::]:{port}')
    server.start()

    logger.info(f"gRPCサーバー起動: port={port}, max_workers={max_workers}")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("サーバーを停止します...")
        server.stop(grace=5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve("iris_model.onnx", port=50051)
```

#### gRPCクライアント実装

```python
import grpc
import iris_service_pb2
import iris_service_pb2_grpc

class IrisGRPCClient:
    """Iris gRPCクライアント"""

    def __init__(self, host: str = "localhost", port: int = 50051):
        """
        Args:
            host: サーバーホスト
            port: サーバーポート
        """
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = iris_service_pb2_grpc.IrisClassifierStub(self.channel)

    def predict(self, sepal_length: float, sepal_width: float,
                petal_length: float, petal_width: float) -> dict:
        """単一予測"""
        request = iris_service_pb2.PredictRequest(
            sepal_length=sepal_length,
            sepal_width=sepal_width,
            petal_length=petal_length,
            petal_width=petal_width
        )

        response = self.stub.Predict(request)

        return {
            "prediction": response.prediction,
            "class_name": response.class_name,
            "probabilities": list(response.probabilities),
            "inference_time_ms": response.inference_time_ms
        }

    def predict_batch(self, samples: list) -> dict:
        """バッチ予測"""
        requests = [
            iris_service_pb2.PredictRequest(**sample)
            for sample in samples
        ]

        batch_request = iris_service_pb2.BatchPredictRequest(samples=requests)
        response = self.stub.PredictBatch(batch_request)

        return {
            "results": [
                {
                    "prediction": r.prediction,
                    "class_name": r.class_name,
                    "probabilities": list(r.probabilities)
                }
                for r in response.results
            ],
            "total_count": response.total_count,
            "total_inference_time_ms": response.total_inference_time_ms
        }

    def predict_stream(self, samples: list):
        """ストリーミング予測"""
        def request_generator():
            for sample in samples:
                yield iris_service_pb2.PredictRequest(**sample)

        responses = self.stub.PredictStream(request_generator())

        for response in responses:
            yield {
                "prediction": response.prediction,
                "class_name": response.class_name,
                "probabilities": list(response.probabilities),
                "inference_time_ms": response.inference_time_ms
            }

    def close(self):
        """接続をクローズ"""
        self.channel.close()

# 使用例
if __name__ == "__main__":
    client = IrisGRPCClient()

    # 単一予測
    result = client.predict(5.1, 3.5, 1.4, 0.2)
    print(f"予測: {result['class_name']}")

    # バッチ予測
    samples = [
        {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
        {"sepal_length": 6.2, "sepal_width": 2.9, "petal_length": 4.3, "petal_width": 1.3},
    ]
    batch_result = client.predict_batch(samples)
    print(f"バッチ予測完了: {batch_result['total_count']}件")

    # ストリーミング
    print("ストリーミング予測:")
    for result in client.predict_stream(samples):
        print(f"  - {result['class_name']}")

    client.close()
```

---

## パターン7: サーバーレスパターン

### 概要

AWS Lambda、Azure Functions、Google Cloud Functionsなどのサーバーレス環境でモデルをデプロイします。

### 適用場面

- イベント駆動型の推論
- トラフィックが不定期・急増する場合
- インフラ管理を最小化したい場合
- コスト最適化（使った分だけ課金）

### メリット・デメリット

| メリット | デメリット |
|---------|-----------|
| ✅ 自動スケーリング | ❌ コールドスタート遅延 |
| ✅ インフラ管理不要 | ❌ 実行時間制限（15分等） |
| ✅ 従量課金 | ❌ メモリ制限 |
| ✅ 高可用性 | ❌ デバッグが難しい |

### 実装例

#### AWS Lambda実装

```python
# lambda_handler.py
import json
import boto3
import numpy as np
import onnxruntime as ort
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# グローバル変数（コンテナ再利用時に保持される）
_session = None

def load_model():
    """S3からモデルをロードし、セッションを初期化"""
    global _session

    if _session is not None:
        logger.info("既存のセッションを再利用")
        return _session

    logger.info("モデルをロード中...")

    # S3からモデルをダウンロード
    s3 = boto3.client('s3')
    bucket = os.environ['MODEL_BUCKET']
    key = os.environ['MODEL_KEY']
    local_path = '/tmp/model.onnx'

    s3.download_file(bucket, key, local_path)
    logger.info(f"モデルダウンロード完了: {local_path}")

    # ONNX Runtimeセッション初期化
    _session = ort.InferenceSession(local_path)
    logger.info("セッション初期化完了")

    return _session

def lambda_handler(event, context):
    """
    Lambda関数のエントリーポイント

    Args:
        event: API Gatewayからのイベント
        context: Lambda実行コンテキスト

    Returns:
        API Gatewayレスポンス
    """
    try:
        # モデルロード（初回またはコールドスタート時）
        session = load_model()
        input_name = session.get_inputs()[0].name

        # リクエストボディをパース
        body = json.loads(event['body'])

        # 入力検証
        features = body.get('features')
        if not features or len(features) != 4:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': '特徴量は4つ必要です'
                })
            }

        # 推論実行
        data = np.array([features], dtype=np.float32)
        outputs = session.run(None, {input_name: data})
        prediction = int(outputs[0][0])
        probabilities = outputs[1][0].tolist() if len(outputs) > 1 else None

        # クラス名マッピング
        class_names = ["setosa", "versicolor", "virginica"]

        # レスポンス
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'prediction': prediction,
                'class_name': class_names[prediction],
                'probabilities': probabilities
            })
        }

    except Exception as e:
        logger.error(f"エラー: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
```

#### Dockerfileレイヤー（Lambda用）

```dockerfile
# Dockerfile
FROM public.ecr.aws/lambda/python:3.13

# ONNX Runtimeインストール
RUN pip install --no-cache-dir \
    onnxruntime==1.23.0 \
    boto3 \
    numpy

# Lambda関数コードをコピー
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}

# ハンドラー指定
CMD ["lambda_handler.lambda_handler"]
```

#### SAMテンプレート（Infrastructure as Code）

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Iris ONNX Inference Lambda

Globals:
  Function:
    Timeout: 30
    MemorySize: 1024

Resources:
  # Lambda関数
  IrisPredictionFunction:
    Type: AWS::Serverless::Function
    Properties:
      PackageType: Image
      ImageUri: !Sub '${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/iris-lambda:latest'
      Environment:
        Variables:
          MODEL_BUCKET: !Ref ModelBucket
          MODEL_KEY: iris_model.onnx
      Events:
        PredictAPI:
          Type: Api
          Properties:
            Path: /predict
            Method: post
      Policies:
        - S3ReadPolicy:
            BucketName: !Ref ModelBucket

  # S3バケット（モデル保存用）
  ModelBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: iris-model-bucket
      VersioningConfiguration:
        Status: Enabled

Outputs:
  PredictionApi:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/predict/"

  FunctionArn:
    Description: "Lambda Function ARN"
    Value: !GetAtt IrisPredictionFunction.Arn
```

#### デプロイ手順

```bash
# 1. Dockerイメージをビルド
docker build -t iris-lambda .

# 2. ECRにプッシュ
aws ecr create-repository --repository-name iris-lambda
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag iris-lambda:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/iris-lambda:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/iris-lambda:latest

# 3. モデルをS3にアップロード
aws s3 cp iris_model.onnx s3://iris-model-bucket/iris_model.onnx

# 4. SAMでデプロイ
sam build
sam deploy --guided

# 5. テスト
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/Prod/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

---

## パターン選択ガイド

### フローチャート

```
推論パターンを選ぶ
  |
  ├─ リアルタイム性が最重要？
  |    ├─ Yes → ストリーミング推論パターン (4)
  |    └─ No → 次へ
  |
  ├─ 大量データを一括処理？
  |    ├─ Yes → バッチ推論パターン (2)
  |    └─ No → 次へ
  |
  ├─ Webから呼び出す？
  |    ├─ Yes → REST APIパターン (5)
  |    └─ No → 次へ
  |
  ├─ 高性能マイクロサービス？
  |    ├─ Yes → gRPCパターン (6)
  |    └─ No → 次へ
  |
  ├─ トラフィックが不定期？
  |    ├─ Yes → サーバーレスパターン (7)
  |    └─ No → 次へ
  |
  ├─ 並行リクエスト処理？
  |    ├─ Yes → 非同期推論パターン (3)
  |    └─ No → 同期推論パターン (1)
```

### シナリオ別推奨パターン

| シナリオ | 推奨パターン | 理由 |
|---------|------------|------|
| **社内ツール（CLI）** | 1. 同期推論 | シンプル、デバッグ容易 |
| **Webアプリ** | 5. REST API | 実装簡単、広く使われている |
| **データ分析パイプライン** | 2. バッチ推論 | 高スループット、効率的 |
| **リアルタイム異常検知** | 4. ストリーミング | 低レイテンシ、継続処理 |
| **高トラフィックAPI** | 3. 非同期推論 | 並行処理、効率的 |
| **マイクロサービス** | 6. gRPC | 高性能、型安全 |
| **不定期バッチ処理** | 7. サーバーレス | 自動スケール、コスト最適 |

---

## 実装順序の推奨

学習・実装の順序として以下を推奨します：

### ステップ1: 基礎を固める
1. **同期推論パターン** (1) ← **iris_sklearn_svcで実装済み**
   - ONNXの基本を理解
   - 最もシンプルで理解しやすい
   - 次のステップの土台

### ステップ2: パフォーマンス向上
2. **バッチ推論パターン** (2)
   - 同期推論を拡張
   - スループット向上の基本を学ぶ

### ステップ3: API化
3. **REST APIパターン** (5)
   - 実用的なサービス化
   - FastAPIの学習
   - デプロイ・運用の基礎

### ステップ4: 並行処理
4. **非同期推論パターン** (3)
   - asyncioの理解
   - パフォーマンスチューニング
   - REST APIに組み込める

### ステップ5: 高度なパターン（必要に応じて）
5. **ストリーミング推論** (4) - リアルタイム処理が必要な場合
6. **gRPCパターン** (6) - マイクロサービスが必要な場合
7. **サーバーレスパターン** (7) - クラウドデプロイが必要な場合

---

## ベストプラクティス

### 1. モデルロードの最適化

#### ❌ 悪い例：毎回ロード
```python
def predict(data):
    session = ort.InferenceSession('model.onnx')  # 毎回ロード（遅い）
    return session.run(None, {input_name: data})
```

#### ✅ 良い例：初期化時に1度だけロード
```python
class Predictor:
    def __init__(self, model_path):
        self.session = ort.InferenceSession(model_path)  # 1度だけ
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, data):
        return self.session.run(None, {self.input_name: data})
```

### 2. 入力検証

```python
def validate_input(data: np.ndarray, expected_shape: tuple) -> None:
    """入力データを検証"""
    # 次元チェック
    if data.ndim != len(expected_shape):
        raise ValueError(f"期待される次元: {len(expected_shape)}, 実際: {data.ndim}")

    # 形状チェック（動的次元を除く）
    for i, (expected, actual) in enumerate(zip(expected_shape, data.shape)):
        if expected != -1 and expected != actual:
            raise ValueError(f"次元{i}: 期待={expected}, 実際={actual}")

    # 欠損値チェック
    if np.isnan(data).any():
        raise ValueError("入力にNaNが含まれています")

    # 無限大チェック
    if np.isinf(data).any():
        raise ValueError("入力にinfが含まれています")
```

### 3. エラーハンドリング

```python
import functools
import logging

def handle_prediction_errors(func):
    """予測エラーをハンドリングするデコレータ"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logging.error(f"入力エラー: {e}")
            raise
        except ort.capi.onnxruntime_pybind11_state.RuntimeException as e:
            logging.error(f"ONNXランタイムエラー: {e}")
            raise
        except Exception as e:
            logging.error(f"予期しないエラー: {e}", exc_info=True)
            raise
    return wrapper

class Predictor:
    @handle_prediction_errors
    def predict(self, data):
        # 推論処理
        pass
```

### 4. ログとモニタリング

```python
import time
import logging

class InstrumentedPredictor:
    """ログとメトリクスを記録する予測器"""

    def __init__(self, model_path):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.logger = logging.getLogger(__name__)

        # メトリクス
        self.total_predictions = 0
        self.total_time = 0.0

    def predict(self, data):
        start_time = time.time()

        try:
            result = self.session.run(None, {self.input_name: data})

            # メトリクス更新
            elapsed = time.time() - start_time
            self.total_predictions += 1
            self.total_time += elapsed

            # ログ
            self.logger.info(
                f"予測完了 | "
                f"時間: {elapsed*1000:.2f}ms | "
                f"入力形状: {data.shape}"
            )

            return result

        except Exception as e:
            self.logger.error(f"予測失敗: {e}")
            raise

    def get_metrics(self):
        """メトリクスを取得"""
        if self.total_predictions == 0:
            return {"avg_time_ms": 0, "total_predictions": 0}

        return {
            "avg_time_ms": (self.total_time / self.total_predictions) * 1000,
            "total_predictions": self.total_predictions
        }
```

### 5. バージョン管理

```python
import json
from pathlib import Path

class VersionedPredictor:
    """モデルバージョン情報を管理する予測器"""

    def __init__(self, model_path: str, metadata_path: str = None):
        self.model_path = model_path
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name

        # メタデータ読み込み
        if metadata_path:
            with open(metadata_path) as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

    def get_version_info(self):
        """バージョン情報を返す"""
        return {
            "model_path": self.model_path,
            "model_version": self.metadata.get("version", "unknown"),
            "model_date": self.metadata.get("created_at", "unknown"),
            "framework": self.metadata.get("framework", "unknown"),
            "accuracy": self.metadata.get("accuracy", "unknown")
        }

    def predict(self, data):
        return self.session.run(None, {self.input_name: data})
```

メタデータファイル例（`model_metadata.json`）:
```json
{
  "version": "1.0.0",
  "created_at": "2025-01-15T10:30:00Z",
  "framework": "scikit-learn 1.6.0",
  "accuracy": 0.97,
  "dataset": "iris",
  "features": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
  "classes": ["setosa", "versicolor", "virginica"]
}
```

---

## トラブルシューティング

### 問題1: "No such file or directory" エラー

**症状**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'model.onnx'
```

**原因**: モデルファイルのパスが間違っている

**解決策**:
```python
from pathlib import Path

# 絶対パスを使用
model_path = Path(__file__).parent / "models" / "iris_model.onnx"
if not model_path.exists():
    raise FileNotFoundError(f"モデルが見つかりません: {model_path}")

session = ort.InferenceSession(str(model_path))
```

### 問題2: 入力形状のミスマッチ

**症状**:
```
RuntimeException: [ONNXRuntimeError] : 2 : INVALID_ARGUMENT :
Invalid rank for input: X. Got: 1 Expected: 2
```

**原因**: 入力データの次元が期待と異なる

**解決策**:
```python
# 1次元配列の場合、2次元に変換
if data.ndim == 1:
    data = data.reshape(1, -1)

# または
data = np.array([[5.1, 3.5, 1.4, 0.2]])  # 最初から2次元にする
```

### 問題3: 型の不一致

**症状**:
```
RuntimeException: [ONNXRuntimeError] : 2 : INVALID_ARGUMENT :
Unexpected input data type. Actual: (tensor(double)) , expected: (tensor(float))
```

**原因**: データ型が float64 だが、モデルは float32 を期待

**解決策**:
```python
# float32に変換
data = data.astype(np.float32)

# または作成時に型を指定
data = np.array([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32)
```

### 問題4: メモリエラー

**症状**:
```
MemoryError: Unable to allocate array
```

**原因**: バッチサイズが大きすぎる

**解決策**:
```python
# バッチサイズを小さくする
BATCH_SIZE = 32  # 64から32に削減

# またはメモリ監視を追加
import psutil

def get_memory_usage():
    """現在のメモリ使用量（MB）"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

# バッチ処理前にチェック
mem_before = get_memory_usage()
result = predictor.predict_batch(large_batch)
mem_after = get_memory_usage()
print(f"メモリ使用量: {mem_after - mem_before:.2f}MB")
```

### 問題5: 推論が遅い

**原因と解決策**:

| 原因 | 解決策 |
|------|--------|
| 毎回モデルをロード | 初期化時に1度だけロード（グローバル変数またはクラス変数） |
| CPU実行 | GPU版ONNX Runtimeを使用 |
| 小さいバッチサイズ | バッチサイズを大きくする |
| データ型変換のオーバーヘッド | 事前に適切な型に変換 |

```python
# GPU使用
import onnxruntime as ort

providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
session = ort.InferenceSession('model.onnx', providers=providers)

# 使用中のプロバイダーを確認
print(session.get_providers())
```

---

## まとめ

### 重要ポイント

1. **パターン選択は要件次第**
   - まずは同期推論で基礎を固める
   - 要件に応じて適切なパターンを選ぶ

2. **パフォーマンスの鍵**
   - モデルは1度だけロード
   - 適切なバッチサイズ
   - 型変換のオーバーヘッドを最小化

3. **本番環境での注意点**
   - 入力検証は必須
   - エラーハンドリングを丁寧に
   - ログとモニタリングを忘れずに

4. **スケーラビリティ**
   - トラフィックに応じてパターンを選ぶ
   - 非同期処理やバッチ処理を活用
   - 必要に応じてサーバーレス化

### 次のステップ

- [ ] iris_sklearn_svcの同期推論パターンを復習
- [ ] バッチ推論パターンを実装
- [ ] FastAPIでREST API化
- [ ] 非同期推論を試す
- [ ] 興味に応じて高度なパターンに挑戦

---

**最終更新**: 2025-01-15
**関連ドキュメント**: `github_actions_guide.md`, `project_overview.md`
