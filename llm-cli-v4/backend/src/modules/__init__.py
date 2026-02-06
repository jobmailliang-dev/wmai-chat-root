"""功能模块注册 - 依赖注入配置"""

from injector import Injector, Module, singleton
from injector import Binder

from .datasource import Connection, DatabaseManager
from .test import Test, TestService, TestDao


def _init_database():
    """初始化数据库"""
    conn = Connection("data/app.db")
    conn.init_schema()
    return conn


class DatabaseModule(Module):
    """数据库模块配置"""

    def configure(self, binder: Binder):
        # 连接 - 单例，使用工厂函数确保目录创建
        binder.bind(
            Connection,
            to=_init_database,
            scope=singleton
        )


class TestModule(Module):
    """Test 模块配置"""

    def configure(self, binder: Binder):
        # DAO - 单例
        binder.bind(
            TestDao,
            scope=singleton
        )
        # Service - 单例
        binder.bind(
            TestService,
            scope=singleton
        )


# 创建 Injector 实例
injector = Injector([
    DatabaseModule(),
    TestModule()
])

# 便捷函数
def get_injector() -> Injector:
    """获取 Injector 实例"""
    return injector


def get_test_service() -> TestService:
    """获取 TestService 实例"""
    return injector.get(TestService)


__all__ = [
    "injector",
    "get_injector",
    "get_test_service",
    "Test",
    "TestService",
    "TestDao",
    "Connection",
    "DatabaseManager"
]
