"""Redis クライアント

キュー操作とデータストアの管理を行う
"""

import json
from typing import Any, Optional

import redis


class RedisClient:
    """Redisクライアント"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """初期化

        Args:
            host: Redisホスト
            port: Redisポート
            db: データベース番号
        """
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def ping(self) -> bool:
        """接続確認

        Returns:
            接続成功ならTrue
        """
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False

    # ========================================
    # キュー操作
    # ========================================

    def enqueue(self, queue_name: str, job_id: str) -> None:
        """ジョブをキューに追加（左プッシュ）

        Args:
            queue_name: キュー名
            job_id: ジョブID
        """
        self.client.lpush(queue_name, job_id)

    def dequeue(self, queue_name: str) -> Optional[str]:
        """キューからジョブを取得（右ポップ）

        Args:
            queue_name: キュー名

        Returns:
            ジョブID（キューが空ならNone）
        """
        job_id = self.client.rpop(queue_name)
        return job_id if job_id else None

    def dequeue_blocking(self, queue_name: str, timeout: int = 1) -> Optional[str]:
        """キューからジョブを取得（ブロッキング）

        ジョブが来るまでブロック（待機）する。
        CPUを無駄に使わず、レイテンシも低い。

        Args:
            queue_name: キュー名
            timeout: タイムアウト（秒）

        Returns:
            ジョブID（タイムアウトならNone）
        """
        result = self.client.brpop(queue_name, timeout=timeout)
        if result:
            # brpopは (queue_name, job_id) のタプルを返す
            _, job_id = result
            return job_id
        return None

    def queue_length(self, queue_name: str) -> int:
        """キューの長さを取得

        Args:
            queue_name: キュー名

        Returns:
            キュー内のジョブ数
        """
        return self.client.llen(queue_name)

    # ========================================
    # データストア操作
    # ========================================

    def set_data(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        """データを保存

        Args:
            key: キー
            value: 値（JSON変換可能なオブジェクト）
            expire: 有効期限（秒）
        """
        json_value = json.dumps(value)
        self.client.set(key, json_value)
        if expire:
            self.client.expire(key, expire)

    def get_data(self, key: str) -> Optional[Any]:
        """データを取得

        Args:
            key: キー

        Returns:
            値（JSON変換された元のオブジェクト）、存在しないならNone
        """
        value = self.client.get(key)
        if value is None:
            return None
        return json.loads(value)

    def delete_data(self, key: str) -> None:
        """データを削除

        Args:
            key: キー
        """
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        """キーの存在確認

        Args:
            key: キー

        Returns:
            存在すればTrue
        """
        return bool(self.client.exists(key))

    # ========================================
    # ジョブ管理用ヘルパー
    # ========================================

    def save_job_data(
        self, job_id: str, data: Any, queue_name: str, expire: int = 86400
    ) -> None:
        """ジョブデータを保存してキューに追加

        Args:
            job_id: ジョブID
            data: 入力データ
            queue_name: キュー名
            expire: データ有効期限（秒、デフォルト24時間）
        """
        # データを保存
        data_key = f"job:{job_id}:data"
        self.set_data(data_key, data, expire=expire)

        # ステータスを pending に設定
        status_key = f"job:{job_id}:status"
        self.set_data(status_key, "pending", expire=expire)

        # キューに追加
        self.enqueue(queue_name, job_id)

    def save_job_result(self, job_id: str, result: Any, expire: int = 86400) -> None:
        """ジョブ結果を保存

        Args:
            job_id: ジョブID
            result: 推論結果
            expire: 結果有効期限（秒、デフォルト24時間）
        """
        result_key = f"job:{job_id}:result"
        self.set_data(result_key, result, expire=expire)

        # ステータスを completed に更新
        status_key = f"job:{job_id}:status"
        self.set_data(status_key, "completed", expire=expire)

    def get_job_data(self, job_id: str) -> Optional[Any]:
        """ジョブデータを取得

        Args:
            job_id: ジョブID

        Returns:
            入力データ
        """
        data_key = f"job:{job_id}:data"
        return self.get_data(data_key)

    def get_job_result(self, job_id: str) -> Optional[Any]:
        """ジョブ結果を取得

        Args:
            job_id: ジョブID

        Returns:
            推論結果
        """
        result_key = f"job:{job_id}:result"
        return self.get_data(result_key)

    def get_job_status(self, job_id: str) -> Optional[str]:
        """ジョブステータスを取得

        Args:
            job_id: ジョブID

        Returns:
            ステータス（pending, processing, completed, failed）
        """
        status_key = f"job:{job_id}:status"
        return self.get_data(status_key)

    def set_job_status(
        self, job_id: str, status: str, expire: int = 86400
    ) -> None:
        """ジョブステータスを設定

        Args:
            job_id: ジョブID
            status: ステータス
            expire: 有効期限（秒）
        """
        status_key = f"job:{job_id}:status"
        self.set_data(status_key, status, expire=expire)

    def set_job_error(self, job_id: str, error: str, expire: int = 86400) -> None:
        """ジョブエラーを記録

        Args:
            job_id: ジョブID
            error: エラーメッセージ
            expire: 有効期限（秒）
        """
        error_key = f"job:{job_id}:error"
        self.set_data(error_key, error, expire=expire)
        self.set_job_status(job_id, "failed", expire=expire)

    def job_exists(self, job_id: str) -> bool:
        """ジョブの存在確認

        Args:
            job_id: ジョブID

        Returns:
            存在すればTrue
        """
        status_key = f"job:{job_id}:status"
        return self.exists(status_key)
