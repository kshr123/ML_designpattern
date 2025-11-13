FROM python:3.13-slim

ENV PROJECT_DIR=/workdir
WORKDIR ${PROJECT_DIR}

# 依存関係のインストール
COPY requirements.txt ${PROJECT_DIR}/
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY src/ ${PROJECT_DIR}/src/

# ラベルファイルのコピー（emptyDirと競合しないよう別ディレクトリに配置）
RUN mkdir -p ${PROJECT_DIR}/config
COPY models/label.json ${PROJECT_DIR}/config/label.json

# 環境変数の設定
ENV MODEL_FILEPATH=${PROJECT_DIR}/models/iris_svc.onnx
ENV LABEL_FILEPATH=${PROJECT_DIR}/config/label.json

# 起動スクリプトのコピー
COPY run.sh ${PROJECT_DIR}/
RUN chmod +x ${PROJECT_DIR}/run.sh

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# FastAPIアプリケーションの起動
CMD ["./run.sh"]
