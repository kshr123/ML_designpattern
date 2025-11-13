#!/bin/bash
set -eu

# 環境変数をコマンドライン引数として渡してmodel_loaderを実行
python main.py \
    --gcs_bucket="${GCS_BUCKET}" \
    --gcs_model_blob="${GCS_MODEL_BLOB}" \
    --model_filepath="${MODEL_FILEPATH}"
