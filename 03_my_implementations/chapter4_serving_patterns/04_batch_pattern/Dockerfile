# ================================================================================
# Dockerfile - Batch Pattern（APIサービス & バッチジョブ）
# ================================================================================
#
# 【このDockerfileの目的】
#   - 1つのDockerfileで2つのサービスを構築（効率化）
#   - APIサービス: FastAPIでHTTP REST APIを提供
#   - バッチジョブ: 定期的にDB内の未推論データを推論
#
# 【なぜ1つのDockerfileで2つのサービスを作るのか】
#   - 共通の依存関係（FastAPI, SQLAlchemy, ONNX Runtime等）
#   - 共通のコードベース（src/配下を共有）
#   - イメージサイズの削減（同じイメージを再利用）
#   - メンテナンス性の向上（依存関係の管理が1箇所で済む）
#
# 【起動方法の切り替え】
#   - APIサービス: Dockerfileのデフォルトコマンド（uvicorn）
#   - バッチジョブ: docker-compose.ymlでcommandをオーバーライド
#
# 【マルチステージビルドの構成】
#   Stage 1 (base): Python + uv のインストール
#   Stage 2 (dependencies): Pythonパッケージのインストール
#   Stage 3 (final): アプリケーションコードの配置と実行
#
# ================================================================================

# ================================================================================
# Stage 1: ベースイメージ - Python + uvのセットアップ
# ================================================================================
#
# 【目的】
#   - Python 3.13のスリムイメージをベースに
#   - uv（高速パッケージマネージャー）をインストール
#
# 【なぜuvを使うのか】
#   - pipより10-100倍高速
#   - 依存関係の解決が正確
#   - pyproject.tomlから直接インストール可能
#
FROM python:3.13-slim AS base

# 作業ディレクトリの設定
# すべてのコマンドはこのディレクトリで実行される
WORKDIR /app

# システムパッケージの更新と必要なツールのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # curl: uvのインストールスクリプトをダウンロードするために必要
    curl \
    # キャッシュクリーンアップ（イメージサイズ削減）
    && rm -rf /var/lib/apt/lists/*

# uvのインストール
# astral.shの公式スクリプトを使用
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# uvのパスを追加（インストール場所: /root/.local/bin/uv）
ENV PATH="/root/.local/bin:${PATH}"

# ================================================================================
# Stage 2: 依存関係のインストール
# ================================================================================
#
# 【目的】
#   - pyproject.tomlに記載された依存関係をインストール
#   - アプリケーションコードは含めない（Dockerキャッシュ活用）
#
# 【なぜアプリコードを含めないか】
#   - 依存関係は頻繁に変わらない → キャッシュが効く
#   - アプリコードは頻繁に変わる → 変更のたびに依存インストールは無駄
#   - この分離により、コード変更時のビルドが高速化
#
FROM base AS dependencies

# pyproject.tomlのみをコピー
# 依存関係の定義ファイル（FastAPI, SQLAlchemy, ONNX Runtime等）
COPY pyproject.toml ./

# 依存関係のインストール
# --system: システムのPythonに直接インストール（仮想環境を作らない）
# -r pyproject.toml: pyproject.tomlから依存関係を読み込み
RUN uv pip install --system -r pyproject.toml

# ================================================================================
# Stage 3: 最終イメージ - アプリケーションの配置
# ================================================================================
#
# 【目的】
#   - アプリケーションコードとモデルファイルを配置
#   - 環境変数を設定
#   - 起動コマンドを定義
#
FROM dependencies AS final

# アプリケーションコードのコピー
# src/: すべてのPythonソースコード
#   - src/api/: FastAPI関連（APIサービス用）
#   - src/task/: バッチジョブ関連
#   - src/ml/: 推論ロジック
#   - src/db/: データベース操作（SQLAlchemy）
COPY src/ ./src/

# モデルファイルのコピー
# models/: ONNXモデルとラベル定義
#   - iris_svc.onnx: Iris分類モデル（約1KB）
#   - label.json: クラスラベル ["setosa", "versicolor", "virginica"]
COPY models/ ./models/

# ================================================================================
# 環境変数の設定（デフォルト値）
# ================================================================================
# docker-compose.ymlで上書き可能
# 各サービスの設定を柔軟に変更できる

# Python関連
ENV PYTHONUNBUFFERED=1

# 実行環境識別（docker, local等）
ENV PLATFORM=docker

# MySQL接続設定
# MYSQL_SERVER: Dockerコンテナではサービス名（mysql）で名前解決
ENV MYSQL_SERVER=mysql \
    MYSQL_PORT=3306 \
    MYSQL_USER=user \
    MYSQL_PASSWORD=userpassword \
    MYSQL_DATABASE=sample_db

# モデルファイルパス
ENV MODEL_FILEPATH=models/iris_svc.onnx \
    LABEL_FILEPATH=models/label.json

# バッチジョブ設定
# BATCH_WAIT_TIME: バッチ処理の実行間隔（秒）
# WORKER_THREADS: ThreadPoolExecutorの並列スレッド数
ENV BATCH_WAIT_TIME=60 \
    WORKER_THREADS=4

# ================================================================================
# ポート公開
# ================================================================================
# APIサービス用のポート
# バッチジョブはポートを使わないが、同じイメージなのでEXPOSE
EXPOSE 8000

# ================================================================================
# デフォルトコマンド
# ================================================================================
#
# 【APIサービスの起動】
#   - uvicorn: ASGIサーバー（FastAPI用）
#   - src.api.app:app: src/api/app.py の app オブジェクト
#   - --host 0.0.0.0: すべてのネットワークインターフェースでリッスン
#   - --port 8000: ポート8000で起動
#
# 【バッチジョブの起動】
#   - docker-compose.ymlでcommandをオーバーライド
#   - command: python -m src.task.job
#   - これによりバッチジョブが起動される
#
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
