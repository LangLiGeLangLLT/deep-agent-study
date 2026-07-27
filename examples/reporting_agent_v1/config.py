"""
Reporting Agent 配置管理

提供数据库连接配置和 Agent 行为配置。
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Reporting Agent 配置类"""
    
    # 数据库配置
    database_url: str = "sqlite:///default.db"
    mysql_enabled: bool = False
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_username: str = "root"
    mysql_password: str = ""
    mysql_database: str = "test"
    
    postgres_enabled: bool = False
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_username: str = "postgres"
    postgres_password: str = ""
    postgres_database: str = "test"
    
    sqlite_enabled: bool = True
    sqlite_path: str = "data.db"
    
    # Agent 行为配置
    max_iterations: int = 10
    max_rows: int = 1000
    enable_query_analysis: bool = True
    enable_auto_optimization: bool = True
    
    # 安全配置
    enable_sql_validation: bool = True
    allowed_sql_types: list = None
    
    def __post_init__(self):
        """初始化默认值"""
        if self.allowed_sql_types is None:
            self.allowed_sql_types = ['SELECT', 'SHOW', 'DESCRIBE', 'DESC']
    
    @classmethod
    def from_env(cls) -> 'Config':
        """从环境变量加载配置"""
        import os
        
        return cls(
            database_url=os.getenv('DATABASE_URL', 'sqlite:///default.db'),
            mysql_enabled=os.getenv('MYSQL_ENABLED', 'false').lower() == 'true',
            mysql_host=os.getenv('MYSQL_HOST', 'localhost'),
            mysql_port=int(os.getenv('MYSQL_PORT', '3306')),
            mysql_username=os.getenv('MYSQL_USERNAME', 'root'),
            mysql_password=os.getenv('MYSQL_PASSWORD', ''),
            mysql_database=os.getenv('MYSQL_DATABASE', 'test'),
            
            postgres_enabled=os.getenv('POSTGRES_ENABLED', 'false').lower() == 'true',
            postgres_host=os.getenv('POSTGRES_HOST', 'localhost'),
            postgres_port=int(os.getenv('POSTGRES_PORT', '5432')),
            postgres_username=os.getenv('POSTGRES_USERNAME', 'postgres'),
            postgres_password=os.getenv('POSTGRES_PASSWORD', ''),
            postgres_database=os.getenv('POSTGRES_DATABASE', 'test'),
            
            sqlite_enabled=os.getenv('SQLITE_ENABLED', 'true').lower() == 'true',
            sqlite_path=os.getenv('SQLITE_PATH', 'data.db'),
            
            max_iterations=int(os.getenv('MAX_ITERATIONS', '10')),
            max_rows=int(os.getenv('MAX_ROWS', '1000')),
            enable_query_analysis=os.getenv('ENABLE_QUERY_ANALYSIS', 'true').lower() == 'true',
            enable_auto_optimization=os.getenv('ENABLE_AUTO_OPTIMIZATION', 'true').lower() == 'true',
            enable_sql_validation=os.getenv('ENABLE_SQL_VALIDATION', 'true').lower() == 'true',
        )
    
    def get_database_config(self, db_type: str) -> dict:
        """获取特定数据库的配置"""
        if db_type == 'mysql':
            return {
                'host': self.mysql_host,
                'port': self.mysql_port,
                'username': self.mysql_username,
                'password': self.mysql_password,
                'database': self.mysql_database
            }
        elif db_type == 'postgres':
            return {
                'host': self.postgres_host,
                'port': self.postgres_port,
                'username': self.postgres_username,
                'password': self.postgres_password,
                'database': self.postgres_database
            }
        elif db_type == 'sqlite':
            return {
                'database_path': self.sqlite_path
            }
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")