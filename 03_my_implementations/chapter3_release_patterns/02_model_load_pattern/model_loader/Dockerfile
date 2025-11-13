FROM python:3.13-slim

ENV PROJECT_DIR=/workdir
WORKDIR ${PROJECT_DIR}

# 依存関係のインストール
COPY model_loader/requirements.txt ${PROJECT_DIR}/
RUN pip install --no-cache-dir -r requirements.txt

# モデルローダースクリプトのコピー
COPY model_loader/main.py ${PROJECT_DIR}/main.py

# エントリーポイント
# Kubernetesから環境変数（GCS_BUCKET, GCS_MODEL_BLOB, MODEL_FILEPATH）を受け取る
# 環境変数をコマンドライン引数として渡すためのスクリプトを使用
COPY model_loader/entrypoint.sh ${PROJECT_DIR}/
RUN chmod +x ${PROJECT_DIR}/entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
