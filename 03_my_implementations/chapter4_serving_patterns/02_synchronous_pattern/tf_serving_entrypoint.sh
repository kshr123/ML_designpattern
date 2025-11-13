#!/bin/bash

# TensorFlow Serving起動スクリプト
# gRPCとRESTの両方のエンドポイントを公開します

set -e

# 環境変数のデフォルト値
MODEL_NAME=${MODEL_NAME:-iris}
MODEL_BASE_PATH=${MODEL_BASE_PATH:-/models/iris}

echo "========================================="
echo "TensorFlow Serving Starting..."
echo "========================================="
echo "Model Name: ${MODEL_NAME}"
echo "Model Base Path: ${MODEL_BASE_PATH}"
echo "gRPC Port: 8500"
echo "REST Port: 8501"
echo "========================================="

# モデルディレクトリの確認
if [ ! -d "${MODEL_BASE_PATH}" ]; then
    echo "ERROR: Model directory not found: ${MODEL_BASE_PATH}"
    exit 1
fi

# モデルバージョンの確認
MODEL_VERSION_DIR="${MODEL_BASE_PATH}/1"
if [ ! -d "${MODEL_VERSION_DIR}" ]; then
    echo "ERROR: Model version directory not found: ${MODEL_VERSION_DIR}"
    exit 1
fi

echo "Model directory structure:"
ls -lh "${MODEL_BASE_PATH}"
echo ""
ls -lh "${MODEL_VERSION_DIR}"
echo "========================================="

# TensorFlow Servingを起動
# --rest_api_port=8501: REST APIポート
# --model_name: モデル名
# --model_base_path: モデルのベースパス
tensorflow_model_server \
    --rest_api_port=8501 \
    --model_name="${MODEL_NAME}" \
    --model_base_path="${MODEL_BASE_PATH}"
