#!/bin/bash
set -eu

# 環境変数のデフォルト値
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-1}

# FastAPIアプリケーションの起動
uvicorn src.main:app \
    --host ${HOST} \
    --port ${PORT} \
    --workers ${WORKERS}
