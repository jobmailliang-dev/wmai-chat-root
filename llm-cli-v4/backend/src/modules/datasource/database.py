"""数据库初始化模块"""

from .connection import Connection


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = "data/app.db"):
        self._connection = Connection(db_path)
        self._initialized = False

    @property
    def conn(self) -> Connection:
        return self._connection

    def init_database(self):
        """初始化数据库表（仅执行一次）"""
        if self._initialized:
            return
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._initialized = True
