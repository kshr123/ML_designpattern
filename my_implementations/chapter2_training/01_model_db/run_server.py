"""
Development Server

開発用サーバーを起動します。
"""

import uvicorn
from src.db.initialize import init_db

if __name__ == "__main__":
    # データベースを初期化
    print("Initializing database...")
    init_db()

    # サーバーを起動
    print("\nStarting FastAPI server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server\n")

    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # コード変更時に自動リロード
    )
