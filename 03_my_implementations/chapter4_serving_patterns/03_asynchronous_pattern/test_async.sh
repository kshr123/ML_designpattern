#!/bin/bash

echo "======================================"
echo "非同期処理の確認テスト"
echo "======================================"
echo ""

echo "【1】リクエスト送信（即座にjob_idが返るはず）"
echo "開始時刻: $(date +%H:%M:%S)"
RESPONSE=$(curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"data":[[5.1, 3.5, 1.4, 0.2]]}')
echo "レスポンス: $RESPONSE"
echo "終了時刻: $(date +%H:%M:%S)"
echo "👉 約0.1秒以内に返るはず（3秒待たない＝非同期の証拠）"
echo ""

# job_idを抽出
JOB_ID=$(echo $RESPONSE | sed 's/.*"job_id":"\([^"]*\)".*/\1/')
echo "Job ID: $JOB_ID"
echo ""

echo "【2】直後のステータス確認（pendingまたはprocessingのはず）"
STATUS=$(curl -s http://localhost:8000/job/$JOB_ID)
echo "ステータス: $STATUS"
echo "👉 completedではないはず（まだ処理中）"
echo ""

echo "【3】1秒後のステータス確認（まだprocessingのはず）"
sleep 1
STATUS=$(curl -s http://localhost:8000/job/$JOB_ID)
echo "ステータス: $STATUS"
echo "👉 まだ完了していないはず（3秒の処理中）"
echo ""

echo "【4】さらに2.5秒後のステータス確認（completedのはず）"
sleep 2.5
STATUS=$(curl -s http://localhost:8000/job/$JOB_ID)
echo "ステータス: $STATUS"
echo "👉 完了しているはず"
echo ""

echo "======================================"
echo "✅ 非同期処理の証明："
echo "   - リクエストは即座に返る（3秒待たない）"
echo "   - 処理はバックグラウンドで実行"
echo "   - ステータスをポーリングして確認できる"
echo "======================================"
