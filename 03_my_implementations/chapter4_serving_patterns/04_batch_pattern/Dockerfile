# ========================================
# バッチパターン - Dockerfile
# ========================================
# APIサービスとバッチジョブの両方で使用
# コマンドで起動方法を切り替える

# ========================================
# Stage 1: ベースイメージ
# ========================================
FROM python:3.13-slim AS base

# 作業ディレクトリの設定
WORKDIR /app

# システムパッケージの更新と必要なツールのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uvのインストール
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# ========================================
# Stage 2: 依存関係のインストール
# ========================================
FROM base AS dependencies

# pyproject.tomlをコピー
COPY pyproject.toml ./

# 依存関係のインストール
RUN uv pip install --system -r pyproject.toml

# ========================================
# Stage 3: 最終イメージ
# ========================================
FROM dependencies AS final

# アプリケーションコードのコピー
COPY src/ ./src/
COPY models/ ./models/

# 環境変数の設定（デフォルト値）
ENV PYTHONUNBUFFERED=1 \
    PLATFORM=docker \
    MYSQL_SERVER=mysql \
    MYSQL_PORT=3306 \
    MYSQL_USER=user \
    MYSQL_PASSWORD=userpassword \
    MYSQL_DATABASE=sample_db \
    MODEL_FILEPATH=models/iris_svc.onnx \
    LABEL_FILEPATH=models/label.json \
    BATCH_WAIT_TIME=60 \
    WORKER_THREADS=4

# ポート公開（APIサービス用）
EXPOSE 8000

# デフォルトコマンド（APIサービス起動）
# バッチジョブの場合はdocker-compose.ymlでオーバーライド
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
