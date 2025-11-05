"""
Health Check Router

ヘルスチェックエンドポイントを提供します。
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """
    ヘルスチェック

    サービスが正常に動作しているかを確認します。

    Returns:
        dict: ステータス情報
    """
    return {"status": "ok"}
