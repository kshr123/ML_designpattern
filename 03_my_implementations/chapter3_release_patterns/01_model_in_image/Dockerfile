# Model-in-Image Pattern Dockerfile
# モデルファイルをイメージに組み込む

# ベースイメージ: Python 3.13 slim
FROM python:3.13-slim

# 作業ディレクトリを設定
WORKDIR /app

# 環境変数を設定
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    MODEL_FILEPATH=/app/models/iris_svc.onnx \
    LABEL_FILEPATH=/app/models/label.json

# システムパッケージの更新と必要なツールのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 依存関係ファイルをコピー
COPY pyproject.toml ./

# Pythonパッケージのインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn[standard] numpy scikit-learn onnxruntime pydantic python-dotenv

# アプリケーションコードをコピー
COPY src/ ./src/

# モデルファイルをコピー（重要: このパターンの核心）
COPY models/ ./models/

# 実行スクリプトをコピー
COPY run.sh ./
RUN chmod +x run.sh

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ポートを公開
EXPOSE 8000

# アプリケーションを実行
CMD ["./run.sh"]
