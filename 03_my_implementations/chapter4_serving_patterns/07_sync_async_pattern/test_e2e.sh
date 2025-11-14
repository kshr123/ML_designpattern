#!/bin/bash

# E2Eテストスクリプト
# Sync-Async Patternの動作確認

set -e

echo "=========================================="
echo "Sync-Async Pattern E2E Test"
echo "=========================================="
echo ""

# ベースURL
BASE_URL="http://localhost:8000"

# テスト用画像（224x224のダミー画像をBase64エンコード）
# ここでは簡易的に小さいPNG画像を使用
TEST_IMAGE="iVBORw0KGgoAAAANSUhEUgAAAOAAAADgCAIAAACVT/22AAACaklEQVR4nO3SMQEAIAzAMED5pOOAlx6Jgh7dM7Og6vwOgBeDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXNoKQZlDSDkmZQ0gxKmkFJMyhpBiXtAi/3A0Ab3DaFAAAAAElFTkSuQmCC"

echo "1. ヘルスチェック"
echo "------------------------------------------"
curl -s "$BASE_URL/health" | jq '.'
echo ""
echo ""

echo "2. 同期推論 + 非同期ジョブ登録"
echo "------------------------------------------"
RESPONSE=$(curl -s -X POST "$BASE_URL/predict" \
  -H "Content-Type: application/json" \
  -d "{\"image_data\": \"$TEST_IMAGE\"}")

echo "$RESPONSE" | jq '.'
echo ""

# job_idを抽出
JOB_ID=$(echo "$RESPONSE" | jq -r '.job_id')
SYNC_RESULT=$(echo "$RESPONSE" | jq -r '.result_sync')

echo "📊 同期推論結果: $SYNC_RESULT"
echo "🆔 ジョブID: $JOB_ID"
echo ""
echo ""

echo "3. 非同期ジョブ結果取得（処理中）"
echo "------------------------------------------"
echo "⏳ 即座に取得（まだ処理中のはず）..."
curl -s "$BASE_URL/job/$JOB_ID" | jq '.'
echo ""
echo ""

echo "4. Worker処理待機"
echo "------------------------------------------"
echo "⏰ Workerの処理を待機中（5秒）..."
sleep 5
echo ""

echo "5. 非同期ジョブ結果取得（完了）"
echo "------------------------------------------"
ASYNC_RESULT=$(curl -s "$BASE_URL/job/$JOB_ID" | jq -r '.prediction')
echo "📊 非同期推論結果: $ASYNC_RESULT"
echo ""
echo ""

echo "=========================================="
echo "✅ E2Eテスト完了"
echo "=========================================="
echo ""
echo "結果サマリー:"
echo "  - 同期推論（MobileNet v2）: $SYNC_RESULT"
echo "  - 非同期推論（ResNet50）:   $ASYNC_RESULT"
echo ""
echo "ℹ️  同期推論は即座に結果を返し、"
echo "   非同期推論はバックグラウンドで処理されました。"
echo ""
