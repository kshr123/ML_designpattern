#!/bin/bash
# FastAPI アプリケーション起動スクリプト

set -e

echo "=========================================="
echo "Model-in-Image Pattern API Server"
echo "=========================================="
echo ""
echo "モデルファイルパス: ${MODEL_FILEPATH}"
echo "ラベルファイルパス: ${LABEL_FILEPATH}"
echo ""
echo "アプリケーションを起動します..."
echo ""

# Uvicorn で FastAPI アプリケーションを起動
exec uvicorn model_in_image.app:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info
