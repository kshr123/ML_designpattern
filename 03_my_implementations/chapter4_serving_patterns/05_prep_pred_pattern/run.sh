#!/bin/bash
# ================================================================================
# run.sh - Prep Service（FastAPI）起動スクリプト
# ================================================================================
#
# 【このスクリプトの目的】
#   - gunicorn（本番環境向けWSGIサーバー）でFastAPIアプリを起動
#   - 複数ワーカープロセスで並列処理
#   - 本番運用に適した設定（リクエスト制限、グレースフルシャットダウン等）
#
# 【なぜgunicornを使うのか】
#   - FastAPI単体（uvicorn）よりも本番環境に適している
#   - 複数ワーカーで並列処理 → スループット向上
#   - プロセス管理機能（再起動、グレースフルシャットダウン）
#   - メモリリークの軽減（定期的なワーカー再起動）
#
# 【起動の流れ】
#   1. 環境変数から設定値を読み込み（デフォルト値あり）
#   2. gunicorn起動
#   3. gunicorn → uvicorn worker → FastAPIアプリ（src.app.app:app）
#
# 【ワーカーについて】
#   - ワーカー数（WORKERS）: 並列処理できるリクエスト数
#   - 推奨: CPUコア数 × 2 + 1
#   - この設定: 4ワーカー（中規模トラフィック想定）
#
# ================================================================================

# エラー時に即座に終了、未定義変数使用時にエラー
set -eu

# ================================================================================
# 環境変数の設定（${変数名:-デフォルト値}）
# ================================================================================
# 既に環境変数が設定されていればその値を使い、なければデフォルト値を使用

# バインドするホストアドレス
# 0.0.0.0 = すべてのネットワークインターフェースでリッスン
HOST=${HOST:-"0.0.0.0"}

# バインドするポート番号
# Dockerコンテナ内でのポート（外部からは docker-compose.yml の8002で公開）
PORT=${PORT:-8000}

# ワーカープロセス数
# 並列処理できるリクエスト数に影響
# 推奨: CPUコア数 × 2 + 1、ここでは4に設定
WORKERS=${WORKERS:-4}

# Uvicornワーカークラス
# gunicornとFastAPI（ASGI）を接続するためのワーカー
# UvicornWorker: 非同期処理をサポート
UVICORN_WORKER=${UVICORN_WORKER:-"uvicorn.workers.UvicornWorker"}

# ログレベル
# info: 通常の情報レベル（本番環境推奨）
# 他の選択肢: debug, warning, error
LOGLEVEL=${LOGLEVEL:-"info"}

# バックログサイズ
# 同時接続待ちキューの最大数
# 2048: 高トラフィック時でも接続を受け付けられる
BACKLOG=${BACKLOG:-2048}

# 最大リクエスト数（ワーカーあたり）
# 1ワーカーがこの数のリクエストを処理したら自動再起動
# 目的: メモリリークの防止
# 65536 = 約6.5万リクエスト処理後に再起動
LIMIT_MAX_REQUESTS=${LIMIT_MAX_REQUESTS:-65536}

# 最大リクエスト数のジッター（ランダム性）
# ワーカーの再起動タイミングをずらす（同時再起動を避ける）
# 実際の再起動タイミング: (MAX_REQUESTS - MAX_REQUESTS_JITTER) 〜 MAX_REQUESTS
MAX_REQUESTS_JITTER=${MAX_REQUESTS_JITTER:-2048}

# グレースフルタイムアウト
# SIGTERM受信後、ワーカーが処理中のリクエストを完了させる猶予時間（秒）
# 10秒: 長時間推論を待つ余裕を持たせる
GRACEFUL_TIMEOUT=${GRACEFUL_TIMEOUT:-10}

# アプリケーションのパス
# src.app.app:app → src/app/app.py の app オブジェクト
APP_NAME=${APP_NAME:-"src.app.app:app"}

# ================================================================================
# gunicorn起動
# ================================================================================
#
# 【パラメータ解説】
#   -b (--bind): バインドアドレス（HOST:PORT）
#   -w (--workers): ワーカープロセス数
#   -k (--worker-class): ワーカークラス（uvicorn.workers.UvicornWorker）
#   --log-level: ログレベル
#   --backlog: 接続待ちキューのサイズ
#   --max-requests: ワーカー再起動の閾値
#   --max-requests-jitter: 再起動タイミングのランダム性
#   --graceful-timeout: シャットダウン時の猶予時間
#   --reload: コード変更時に自動リロード（開発用、本番では通常オフ）
#
# 【起動後の動作】
#   1. gunicornが4つのワーカープロセスを起動
#   2. 各ワーカーがFastAPIアプリをロード
#   3. 0.0.0.0:8000でHTTPリクエストを待機
#   4. リクエストが来たら空いているワーカーが処理
#
gunicorn ${APP_NAME} \
    -b ${HOST}:${PORT} \
    -w ${WORKERS} \
    -k ${UVICORN_WORKER} \
    --log-level ${LOGLEVEL} \
    --backlog ${BACKLOG} \
    --max-requests ${LIMIT_MAX_REQUESTS} \
    --max-requests-jitter ${MAX_REQUESTS_JITTER} \
    --graceful-timeout ${GRACEFUL_TIMEOUT} \
    --reload
