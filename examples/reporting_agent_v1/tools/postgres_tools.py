"""
PostgreSQL 专用工具

提供 PostgreSQL 数据库特定的查询和分析功能。
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class PostgreSQLTools:
    """PostgreSQL 专用工具集"""
    
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """初始化 PostgreSQL 数据库引擎"""
        try:
            database_url = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            self.engine = create_engine(database_url)
        except Exception as e:
            raise ValueError(f"无法创建 PostgreSQL 数据库引擎: {e}")
    
    @tool
    def execute_postgres_query(self, sql: str, description: str = "") -> str:
        """
        执行 PostgreSQL 特定查询
        
        Args:
            sql: PostgreSQL 查询语句
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
                
                return f"PostgreSQL 查询结果:\n{df.to_string(index=False)}"
                
        except SQLAlchemyError as e:
            return f"PostgreSQL 错误: {str(e)}"
        except Exception as e:
            return f"执行错误: {str(e)}"
    
    @tool
    def get_postgres_tables(self) -> str:
        """
        获取 PostgreSQL 数据库中的所有表
        
        Returns:
            表名列表
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' "
                    "ORDER BY table_name"
                ))
                tables = [row[0] for row in result.fetchall()]
                
                if not tables:
                    return "PostgreSQL 数据库中没有表"
                
                return "PostgreSQL 数据库中的表:\n" + "\n".join([f"{i+1}. {table}" for i, table in enumerate(tables)])
                
        except Exception as e:
            return f"获取 PostgreSQL 表列表时出错: {str(e)}"
    
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
                result = connection.execute(text(
                    f"SELECT indexname, indexdef FROM pg_indexes "
                    f"WHERE tablename = '{table_name}' "
                    "ORDER BY indexname"
                ))
                indexes = result.fetchall()
                
                if not indexes:
                    return f"表 {table_name} 没有索引"
                
                # 格式化索引信息
                lines = [f"表 {table_name} 的索引:"]
                lines.append("索引名\t\t索引定义")
                lines.append("-" * 80)
                
                for index in indexes:
                    lines.append(f"{index[0]}\t\t{index[1]}")
                
                return "\n".join(lines)
                
        except Exception as e:
            return f"获取表索引时出错: {str(e)}"
    
    @tool
    def get_table_constraints(self, table_name: str) -> str:
        """
        获取表的约束信息
        
        Args:
            table_name: 表名
            
        Returns:
            约束信息
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(
                    f"SELECT constraint_name, constraint_type, column_name "
                    f"FROM information_schema.key_column_usage "
                    f"WHERE table_name = '{table_name}' "
                    "ORDER BY constraint_name, ordinal_position"
                ))
                constraints = result.fetchall()
                
                if not constraints:
                    return f"表 {table_name} 没有约束"
                
                # 格式化约束信息
                lines = [f"表 {table_name} 的约束:"]
                lines.append("约束名\t\t类型\t\t字段")
                lines.append("-" * 50)
                
                for constraint in constraints:
                    lines.append(f"{constraint[0]}\t\t{constraint[1]}\t\t{constraint[2]}")
                
                return "\n".join(lines)
                
        except Exception as e:
            return f"获取表约束时出错: {str(e)}"
    
    @tool
    def get_table_statistics(self, table_name: str) -> str:
        """
        获取表的统计信息
        
        Args:
            table_name: 表名
            
        Returns:
            统计信息
        """
        try:
            with self.engine.connect() as connection:
                # 获取表的行数
                count_result = connection.execute(text(f"SELECT reltuples::bigint as estimated_rows FROM pg_class WHERE relname = '{table_name}'"))
                estimated_rows = count_result.fetchone()[0]
                
                # 获取表的大小
                size_result = connection.execute(text(
                    f"SELECT pg_size_pretty(pg_total_relation_size('{table_name}')) as total_size, "
                    f"pg_size_pretty(pg_relation_size('{table_name}')) as table_size, "
                    f"pg_size_pretty(pg_indexes_size('{table_name}')) as indexes_size "
                    f"FROM pg_class WHERE relname = '{table_name}'"
                ))
                size_info = size_result.fetchone()
                
                # 格式化统计信息
                lines = [f"表 {table_name} 统计信息:"]
                lines.append("=" * 40)
                lines.append(f"估计行数: {estimated_rows}")
                lines.append(f"总大小: {size_info[0]}")
                lines.append(f"表大小: {size_info[1]}")
                lines.append(f"索引大小: {size_info[2]}")
                
                return "\n".join(lines)
                
        except Exception as e:
            return f"获取表统计信息时出错: {str(e)}"
    
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
                schema_result = connection.execute(text(
                    f"SELECT column_name, data_type, is_nullable, column_default "
                    f"FROM information_schema.columns "
                    f"WHERE table_name = '{table_name}' "
                    "ORDER BY ordinal_position"
                ))
                schema = schema_result.fetchall()
                
                # 获取行数
                count_result = connection.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                row_count = count_result.fetchone()[0]
                
                # 获取索引信息
                index_result = connection.execute(text(
                    f"SELECT indexname, indexdef FROM pg_indexes "
                    f"WHERE tablename = '{table_name}' "
                    "ORDER BY indexname"
                ))
                indexes = index_result.fetchall()
                
                # 获取约束信息
                constraint_result = connection.execute(text(
                    f"SELECT constraint_name, constraint_type, column_name "
                    f"FROM information_schema.key_column_usage "
                    f"WHERE table_name = '{table_name}' "
                    "ORDER BY constraint_name, ordinal_position"
                ))
                constraints = constraint_result.fetchall()
                
                # 格式化分析结果
                lines = [f"表 {table_name} 分析报告:"]
                lines.append("=" * 50)
                lines.append(f"总行数: {row_count}")
                lines.append(f"字段数: {len(schema)}")
                lines.append(f"索引数: {len(indexes)}")
                lines.append(f"约束数: {len(constraints)}")
                lines.append("")
                
                # 字段分析
                lines.append("字段分析:")
                lines.append("字段名\t\t类型\t\t是否为空\t\t默认值")
                lines.append("-" * 80)
                
                for field in schema:
                    lines.append(f"{field[0]}\t\t{field[1]}\t\t{field[2]}\t\t{field[3] or 'NULL'}")
                
                # 索引分析
                if indexes:
                    lines.append("")
                    lines.append("索引分析:")
                    lines.append("索引名\t\t索引定义")
                    lines.append("-" * 80)
                    
                    for index in indexes:
                        lines.append(f"{index[0]}\t\t{index[1]}")
                
                # 约束分析
                if constraints:
                    lines.append("")
                    lines.append("约束分析:")
                    lines.append("约束名\t\t类型\t\t字段")
                    lines.append("-" * 50)
                    
                    for constraint in constraints:
                        lines.append(f"{constraint[0]}\t\t{constraint[1]}\t\t{constraint[2]}")
                
                return "\n".join(lines)
                
        except Exception as e:
            return f"分析表时出错: {str(e)}"