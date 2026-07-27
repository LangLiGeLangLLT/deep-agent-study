"""
MySQL 专用工具

提供 MySQL 数据库特定的查询和分析功能。
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class MySQLTools:
    """MySQL 专用工具集"""
    
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """初始化 MySQL 数据库引擎"""
        try:
            database_url = f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            self.engine = create_engine(database_url)
        except Exception as e:
            raise ValueError(f"无法创建 MySQL 数据库引擎: {e}")
    
    @tool
    def execute_mysql_query(self, sql: str, description: str = "") -> str:
        """
        执行 MySQL 特定查询
        
        Args:
            sql: MySQL 查询语句
            description: 查询描述（可选）
            
        Returns:
            查询结果
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(sql))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                
                if df.empty:
                    return "查询结果为空"
                
                return f"MySQL 查询结果:\n{df.to_string(index=False)}"
                
        except SQLAlchemyError as e:
            return f"MySQL 错误: {str(e)}"
        except Exception as e:
            return f"执行错误: {str(e)}"
    
    @tool
    def get_mysql_tables(self) -> str:
        """
        获取 MySQL 数据库中的所有表
        
        Returns:
            表名列表
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SHOW TABLES"))
                tables = [row[0] for row in result.fetchall()]
                
                if not tables:
                    return "MySQL 数据库中没有表"
                
                return "MySQL 数据库中的表:\n" + "\n".join([f"{i+1}. {table}" for i, table in enumerate(tables)])
                
        except Exception as e:
            return f"获取 MySQL 表列表时出错: {str(e)}"
    
    @tool
    def get_table_indexes(self, table_name: str) -> str:
        """
        获取表的索引信息
        
        Args:
            table_name: 表名
            
        Returns:
            索引信息
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(f"SHOW INDEX FROM {table_name}"))
                indexes = result.fetchall()
                
                if not indexes:
                    return f"表 {table_name} 没有索引"
                
                # 格式化索引信息
                lines = [f"表 {table_name} 的索引:"]
                lines.append("索引名\t\t字段\t\t唯一\t\t类型")
                lines.append("-" * 60)
                
                for index in indexes:
                    lines.append(f"{index[2]}\t\t{index[4]}\t\t{index[1]}\t\t{index[10] or 'BTREE'}")
                
                return "\n".join(lines)
                
        except Exception as e:
            return f"获取表索引时出错: {str(e)}"
    
    @tool
    def get_table_status(self, table_name: str) -> str:
        """
        获取表的状态信息
        
        Args:
            table_name: 表名
            
        Returns:
            表状态信息
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(f"SHOW TABLE STATUS LIKE '{table_name}'"))
                status = result.fetchone()
                
                if not status:
                    return f"表 {table_name} 不存在"
                
                # 格式化状态信息
                lines = [f"表 {table_name} 状态信息:"]
                lines.append(f"引擎: {status[1]}")
                lines.append(f"版本: {status[2]}")
                lines.append(f"行数: {status[4]}")
                lines.append(f"数据大小: {status[6]} KB")
                lines.append(f"索引大小: {status[8]} KB")
                lines.append(f"总大小: {status[10]} KB")
                
                return "\n".join(lines)
                
        except Exception as e:
            return f"获取表状态时出错: {str(e)}"
    
    @tool
    def analyze_table(self, table_name: str) -> str:
        """
        分析表的结构和性能
        
        Args:
            table_name: 表名
            
        Returns:
            表分析结果
        """
        try:
            with self.engine.connect() as connection:
                # 获取表结构
                schema_result = connection.execute(text(f"DESCRIBE {table_name}"))
                schema = schema_result.fetchall()
                
                # 获取行数
                count_result = connection.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                row_count = count_result.fetchone()[0]
                
                # 获取索引信息
                index_result = connection.execute(text(f"SHOW INDEX FROM {table_name}"))
                indexes = index_result.fetchall()
                
                # 格式化分析结果
                lines = [f"表 {table_name} 分析报告:"]
                lines.append("=" * 50)
                lines.append(f"总行数: {row_count}")
                lines.append(f"字段数: {len(schema)}")
                lines.append(f"索引数: {len(indexes)}")
                lines.append("")
                
                # 字段分析
                lines.append("字段分析:")
                lines.append("字段名\t\t类型\t\t是否为空\t\t键")
                lines.append("-" * 60)
                
                for field in schema:
                    lines.append(f"{field[0]}\t\t{field[1]}\t\t{field[2]}\t\t{field[3]}")
                
                # 索引分析
                if indexes:
                    lines.append("")
                    lines.append("索引分析:")
                    lines.append("索引名\t\t字段\t\t唯一")
                    lines.append("-" * 40)
                    
                    for index in indexes:
                        lines.append(f"{index[2]}\t\t{index[4]}\t\t{index[1]}")
                
                return "\n".join(lines)
                
        except Exception as e:
            return f"分析表时出错: {str(e)}"