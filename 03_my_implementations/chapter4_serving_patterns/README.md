# Chapter 4: Serving Patterns（推論サービスパターン）

## 🎯 この章で学ぶこと

機械学習モデルを本番システムで稼働させるための**推論サービスアーキテクチャ**を学びます。

- Web APIとしての推論器の公開方法
- 同期・非同期推論パターン
- キャッシュ戦略によるパフォーマンス最適化
- マイクロサービスアーキテクチャ
- エッジAIとバッチ推論

## 📖 他の章との違い

| 章 | 焦点 | 主なトピック |
|---|------|-------------|
| Chapter 2 | **モデル学習** | データ準備、学習、評価 |
| Chapter 3 | **モデルリリース** | Docker化、Kubernetes、モデル配信 |
| **Chapter 4** | **推論サービス** | API設計、性能最適化、アーキテクチャパターン |
| Chapter 5 | **運用** | モニタリング、ログ管理、オブザーバビリティ |

**Chapter 4の特徴：**
- ✅ **実際のサービス設計**: 本番環境で使える推論APIの実装
- ✅ **性能とスケーラビリティ**: レスポンスタイム、スループット、可用性を重視
- ✅ **多様なパターン**: ユースケースに応じた10種類の推論パターン

## 📚 実装パターン一覧

| # | パターン名 | 内容 | 難易度 | 状態 |
|---|-----------|------|--------|------|
| 01 | **Web Single Pattern** | シングルコンテナでWeb API公開 | ⭐ | ✅ 完了 (2025-11-13) |
| 02 | **Synchronous Pattern** | TensorFlow Serving + gRPC/REST | ⭐⭐ | ✅ 完了 (2025-11-13) |
| 03 | **Asynchronous Pattern** | 非同期推論パターン (Redis + ONNX) | ⭐⭐ | ✅ 完了 (2025-11-13) |
| 04 | **Batch Pattern** | バッチ推論パターン (MySQL + ThreadPoolExecutor) | ⭐⭐ | ✅ 完了 (2025-11-13) |
| 05 | Prep-Pred Pattern | 前処理・推論分離パターン | ⭐⭐ | ⏳ 未着手 |
| 06 | Sync-Async Pattern | 同期・非同期ハイブリッド | ⭐⭐⭐ | ⏳ 未着手 |
| 07 | Data Cache Pattern | データキャッシュパターン | ⭐⭐ | ⏳ 未着手 |
| 08 | Prediction Cache Pattern | 推論結果キャッシュパターン | ⭐⭐ | ⏳ 未着手 |
| 09 | Horizontal Microservice Pattern | 水平分割マイクロサービス | ⭐⭐⭐ | ⏳ 未着手 |
| 10 | Edge AI Pattern | エッジAIパターン | ⭐⭐⭐ | ⏳ 未着手 |

## 🎓 学習の推奨順序

```
01_web_single_pattern
    ↓ (基礎)
02_synchronous_pattern
    ↓
03_asynchronous_pattern ──┐
    ↓                     │
04_batch_pattern          │ (パターンの組み合わせ)
    ↓                     │
05_prep_pred_pattern ─────┘
    ↓
06_sync_async_pattern
    ↓
07_data_cache_pattern ────┐
    ↓                     │ (最適化)
08_prediction_cache_pattern┘
    ↓
09_horizontal_microservice_pattern
    ↓ (高度)
10_edge_ai_pattern
```

**推奨の理由：**
1. **Web Single Pattern** - 最も基本的なパターン、FastAPI + gunicorn + uvicornの構成を理解
2. **Synchronous/Asynchronous** - 同期・非同期の違いを理解
3. **Batch/Prep-Pred** - 処理の分離と効率化を学ぶ
4. **Sync-Async Hybrid** - パターンの組み合わせ
5. **Cache Patterns** - パフォーマンス最適化手法
6. **Microservice/Edge AI** - 高度なアーキテクチャ

## 📊 完了状況

- **完了**: 4/10パターン (40%)
- **進行中**: 0/10パターン
- **未着手**: 6/10パターン

### 完了パターン

#### 01_web_single_pattern ✅
- **完了日**: 2025-11-13
- **技術スタック**: Python 3.13, FastAPI, Gunicorn, Uvicorn, ONNX Runtime
- **成果**:
  - TDDで41テスト作成・全パス（カバレッジ98%）
  - Dockerイメージ作成
  - 7つのAPIエンドポイント実装
  - gunicorn + uvicornのマルチプロセス構成を理解
- **詳細**: [01_web_single_pattern/README.md](./01_web_single_pattern/README.md)

#### 02_synchronous_pattern ✅
- **完了日**: 2025-11-13
- **技術スタック**: Python 3.11, TensorFlow 2.15.0, TensorFlow Serving, gRPC, Protocol Buffers
- **成果**:
  - TensorFlow SavedModel形式でモデル作成（精度96.67%）
  - TensorFlow Servingでデプロイ
  - gRPCとRESTの両方のクライアント実装
  - Python 3.12/3.13互換性問題を解決
  - Apple Silicon制限事項をドキュメント化
- **詳細**: [02_synchronous_pattern/README.md](./02_synchronous_pattern/README.md)

#### 03_asynchronous_pattern ✅
- **完了日**: 2025-11-13
- **技術スタック**: Python 3.13, FastAPI, Redis 7, ONNX Runtime, Docker Compose
- **成果**:
  - Proxy + Worker + Redisの3層アーキテクチャ実装
  - TensorFlow ServingからONNX Runtimeへ移行（Apple Silicon対応）
  - BRPOPブロッキング方式でCPU効率化（ポーリング vs BRPOP）
  - 非同期処理の証明テストスクリプト作成
  - ジョブステータス管理（pending → processing → completed）
  - Docker Composeでマルチコンテナ構成
- **詳細**: [03_asynchronous_pattern/README.md](./03_asynchronous_pattern/README.md)

#### 04_batch_pattern ✅
- **完了日**: 2025-11-13
- **技術スタック**: Python 3.13, FastAPI, MySQL 8.0, ONNX Runtime, SQLAlchemy 2.0, Docker Compose
- **成果**:
  - データ登録と推論処理の時間的分離アーキテクチャ
  - ThreadPoolExecutorによる並列バッチ推論（4 workers）
  - TDDで41テスト作成・全パス（カバレッジ82%）
  - 仕様駆動開発の実践（SQLite→MySQL修正の教訓）
  - MySQL 8.0認証対応（cryptographyパッケージ）
  - SQLAlchemy 2.0への移行
  - Docker Composeで4サービス構成（mysql、mysql_test、api、job）
  - バッチジョブの自動再起動設定（restart: unless-stopped）
- **詳細**: [04_batch_pattern/README.md](./04_batch_pattern/README.md)

## 🔗 関連ドキュメント

### 参考リポジトリ
- [chapter4_serving_patterns](../../01_reference/chapter4_serving_patterns/)

### 技術ガイド
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [Gunicorn公式ドキュメント](https://gunicorn.org/)
- [Uvicorn公式ドキュメント](https://www.uvicorn.org/)
- [ONNX Runtime](https://onnxruntime.ai/)

### プロジェクト全体
- [プロジェクトルートREADME](../../README.md)
- [学習ログ](../../05_progress/learning_log.md)

---

**詳細は各パターンのREADME.mdを参照してください。**
