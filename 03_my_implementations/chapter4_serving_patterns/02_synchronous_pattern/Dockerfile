# =======================================================
# TensorFlow Serving - Iris分類モデル
# =======================================================
FROM tensorflow/serving:latest

# 環境変数の設定
ENV MODEL_NAME=iris
ENV MODEL_BASE_PATH=/models/iris

# ローカルでビルドしたモデルをコピー
# 事前に `python build_model.py` を実行してモデルを作成しておくこと
COPY ./saved_model/iris /models/iris

# TensorFlow Serving起動スクリプトをコピー
COPY tf_serving_entrypoint.sh /usr/bin/tf_serving_entrypoint.sh
RUN chmod +x /usr/bin/tf_serving_entrypoint.sh

# ポート公開
# 8500: gRPC
# 8501: REST
EXPOSE 8500 8501

# TensorFlow Servingを起動
ENTRYPOINT ["/usr/bin/tf_serving_entrypoint.sh"]
