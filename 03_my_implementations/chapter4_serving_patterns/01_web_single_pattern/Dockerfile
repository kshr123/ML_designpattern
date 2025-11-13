FROM python:3.13-slim

ENV PROJECT_DIR web_single_pattern
WORKDIR /${PROJECT_DIR}

# 依存関係のインストール
ADD ./requirements.txt /${PROJECT_DIR}/
RUN apt-get -y update && \
    apt-get -y install apt-utils gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードとモデルのコピー
COPY ./src/ /${PROJECT_DIR}/src/
COPY ./models/ /${PROJECT_DIR}/models/

# 環境変数の設定
ENV MODEL_FILEPATH=/${PROJECT_DIR}/models/iris_svc.onnx
ENV LABEL_FILEPATH=/${PROJECT_DIR}/models/label.json
ENV API_TITLE="Web Single Pattern"
ENV API_DESCRIPTION="Iris classification API using Web Single Pattern"
ENV API_VERSION="0.1.0"
ENV LOG_LEVEL=INFO

# 実行スクリプトのコピーと実行権限付与
COPY ./run.sh /${PROJECT_DIR}/run.sh
RUN chmod +x /${PROJECT_DIR}/run.sh

# ポート公開
EXPOSE 8000

# アプリケーション起動
CMD ["./run.sh"]
