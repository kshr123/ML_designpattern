#!/bin/bash
# ================================================================================
# onnx_runtime_server_entrypoint.sh - ONNX Runtime Server起動スクリプト
# ================================================================================
#
# 【このスクリプトの目的】
#   - ONNX Runtime Serverを指定されたモデル（ResNet50）で起動
#   - HTTP（REST API）とgRPCの両方のエンドポイントを公開
#   - PrepサービスからのgRPC推論リクエストを受け付ける
#
# 【ONNX Runtime Serverとは】
#   - MicrosoftのONNXモデル推論用の高速サーバー
#   - CPU/GPU最適化された推論エンジン
#   - gRPCとHTTPの両方をサポート
#   - 本番環境で広く使われている（低レイテンシ、高スループット）
#
# 【起動の流れ】
#   1. 環境変数から設定を読み込み（デフォルト値あり）
#   2. onnxruntime_server コマンドで推論サーバー起動
#   3. 指定されたモデルをロードして待機
#
# ================================================================================

# エラー時に即座に終了、未定義変数使用時にエラー
set -eu

# ================================================================================
# 環境変数の設定（${変数名:-デフォルト値}）
# ================================================================================
# docker-compose.yml で設定された環境変数を使用、なければデフォルト値

# HTTPポート（REST API用）
# ポート8001でHTTP REST APIを公開
# 用途: デバッグ、モニタリング、HTTP経由での推論（オプション）
HTTP_PORT=${HTTP_PORT:-8001}

# gRPCポート
# ポート50051でgRPCエンドポイントを公開
# 用途: Prepサービスからの高速推論リクエスト（メイン）
GRPC_PORT=${GRPC_PORT:-50051}

# ログレベル
# debug: 詳細なログ（開発・デバッグ用）
# 他の選択肢: info, warning, error
LOGLEVEL=${LOGLEVEL:-"debug"}

# HTTPスレッド数
# HTTP REST APIリクエストを処理する並列スレッド数
# 4スレッド: 中規模トラフィック想定
NUM_HTTP_THREADS=${NUM_HTTP_THREADS:-4}

# モデルファイルのパス
# ResNet50（ONNX形式）のフルパス
# Dockerfile.predで環境変数 MODEL_PATH が設定されている
MODEL_PATH=${MODEL_PATH:-"/prep_pred_pattern/models/resnet50.onnx"}

# ================================================================================
# ONNX Runtime Server起動
# ================================================================================
#
# 【コマンド】./onnxruntime_server
#   - ONNX Runtime Serverの実行ファイル（/onnxruntime/server/ディレクトリ内）
#
# 【パラメータ解説】
#   --http_port: HTTPエンドポイントのポート番号
#   --grpc_port: gRPCエンドポイントのポート番号
#   --num_http_threads: HTTPリクエスト処理スレッド数
#   --model_path: ロードするONNXモデルのパス
#
# 【起動後の動作】
#   1. ResNet50モデル（約100MB）をメモリにロード
#   2. HTTP（8001）とgRPC（50051）でリクエストを待機
#   3. PrepサービスからgRPC経由で推論リクエストを受信
#   4. ResNet50で推論を実行し、ロジット（1000次元ベクトル）を返却
#
# 【gRPCエンドポイント】
#   - プロトコル: Protocol Buffers
#   - 入力: TensorProto（float32, shape: [1, 3, 224, 224]）
#   - 出力: TensorProto（float32, shape: [1, 1000]）← ロジット
#
# 【HTTPエンドポイント（オプション）】
#   - URL: http://localhost:8001/v1/models/resnet50:predict
#   - リクエスト: JSON（TensorProtoのJSON表現）
#   - レスポンス: JSON（推論結果）
#
./onnxruntime_server \
    --http_port=${HTTP_PORT} \
    --grpc_port=${GRPC_PORT} \
    --num_http_threads=${NUM_HTTP_THREADS} \
    --model_path=${MODEL_PATH}
