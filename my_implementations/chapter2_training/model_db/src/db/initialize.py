"""
Database Initialization

データベースのテーブルを作成します。
"""

from src.db.database import Base, engine
from src.db import models  # modelsをインポートしてBaseに登録


def init_db():
    """データベースを初期化してテーブルを作成"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
