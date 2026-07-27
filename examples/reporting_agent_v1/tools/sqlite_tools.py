"""
SQLite 专用工具

提供 SQLite 数据库特定的查询和分析功能。
"""

import pandas as pd
import os
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class SQLiteTools:
    """SQLite 专用工具集"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """初始化 SQLite 数据库引擎"""
        try:
            if not os.path.exists(self.database_path):
                raise ValueError(f"SQLite 数据库文件不存在: {self.database_path}")
            
            database_url = f"sqlite:///{self.database_path}"
            self.engine = create_engine(database_url)
        except Exception as e:
            raise ValueError(f"无法创建 SQLite 数据库引擎: {e}")
    
    @tool
    def execute_sqlite_query(self, sql: str, description: str = "") -> str:
        """
        执行 SQLite 特定查询
        
        Args:
            sql: SQLite 查询语句
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
                
                return f"SQLite 查询结果:\n{df.to_string(index=False)}"
                
        except SQLAlchemyError as e:
            return f"SQLite 错误: {str(e)}"
        except Exception as e:
            return f"执行错误: {str(e)}"
    
    @tool
    def get_sqlite_tables(self) -> str:
        """
        获取 SQLite 数据库中的所有表
        
        Returns:
            表名列表
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
                tables = [row[0] for row in result.fetchall()]
                
                if not tables:
                    return "SQLite 数据库中没有表"
                
                return "SQLite 数据库中的表:\n" + "\n".join([f"{i+1}. {table}" for i, table in enumerate(tables)])
                
        except Exception as e:
            return f"获取 SQLite 表列表时出错: {str(e)}"
    
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
                result = connection.execute(text(f"PRAGMA index_list({table_name})"))
                indexes = result.fetchall()
                
                if not indexes:
                    return f"表 {table_name} 没有索引"
                
                # 格式化索引信息
                lines = [f"表 {table_name} 的索引:"]
                lines.append("索引名\t\t唯一\t\t根页")
                lines.append("-" * 40)
                
                for index in indexes:
                    lines.append(f"{index[1]}\t\t{index[2]}\t\t{index[3]}")
                
                return "\n".join(lines)
                
        except Exception as e:
            return f"获取表索引时出错: {str(e)}"
    
    @tool
    def get_table_info(self, table_name: str) -> str:
        """
        获取表的详细信息
        
        Args:
            table_name: 表名
            
        Returns:
            表信息
        """
        try:
            with self.engine.connect() as connection:
                # 获取表结构
                schema_result = connection.execute(text(f"PRAGMA table_info({table_name})"))
                schema = schema_result.fetchall()
                
                # 获取索引信息
                index_result = connection.execute(text(f"PRAGMA index_list({table_name})"))
                indexes = index_result.fetchall()
                
                # 获取行数
                count_result = connection.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                row_count = count_result.fetchone()[0]
                
                # 格式化表信息
                lines = [f"表 {table_name} 详细信息:"]
                lines.append("=" * 40)
                lines.append(f"总行数: {row_count}")
                lines.append(f"字段数: {len(schema)}")
                lines.append(f"索引数: {len(indexes)}")
                lines.append("")
                
                # 字段信息
                lines.append("字段信息:")
                lines.append("ID\t\t字段名\t\t类型\t\t是否为空\t\t默认值")
                lines.append("-" * 80)
                
                for field in schema:
                    lines.append(f"{field[0]}\t\t{field[1]}\t\t{field[2]}\t\t{field[3]}\t\t{field[4] or 'NULL'}")
                
                # 索引信息
                if indexes:
                    lines.append("")
                    lines.append("索引信息:")
                    lines.append("索引名\t\t唯一\t\t根页")
                    lines.append("-" * 40)
                    
                    for index in indexes:
                        lines.append(f"{index[1]}\t\t{index[2]}\t\t{index[3]}")
                
                return "\n".join(lines)
                
        except Exception as e:
            return f"获取表信息时出错: {str(e)}"
    
    @tool
    def get_database_info(self) -> str:
        """
        获取数据库的总体信息
        
        Returns:
            数据库信息
        """
        try:
            with self.engine.connect() as connection:
                # 获取所有表
                tables_result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
                tables = [row[0] for row in tables_result.fetchall()]
                
                # 获取数据库版本
                version_result = connection.execute(text("SELECT sqlite_version()"))
                version = version_result.fetchone()[0]
                
                # 获取数据库大小
                db_size = os.path.getsize(self.database_path)
                
                # 计算总行数
                total_rows = 0
                table_stats = []
                
                for table in tables:
                    count_result = connection.execute(text(f"SELECT COUNT(*) as count FROM {table}"))
                    row_count = count_result.fetchone()[0]
                    total_rows += row_count
                    table_stats.append(f"{table}: {row_count} 行")
                
                # 格式化数据库信息
                lines = ["SQLite 数据库信息:"]
                lines.append("=" * 40)
                lines.append(f"数据库文件: {self.database_path}")
                lines.append(f"SQLite 版本: {version}")
                lines.append(f"数据库大小: {db_size} 字节")
                lines.append(f"表数量: {len(tables)}")
                lines.append(f"总行数: {total_rows}")
                lines.append("")
                
                # 表统计
                lines.append("表统计:")
                for stat in table_stats:
                    lines.append(f"  {stat}")
                
                return "\n".join(lines)
                
        except Exception as e:
            return f"获取数据库信息时出错: {str(e)}"
    
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
                schema_result = connection.execute(text(f"PRAGMA table_info({table_name})"))
                schema = schema_result.fetchall()
                
                # 获取行数
                count_result = connection.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                row_count = count_result.fetchone()[0]
                
                # 获取索引信息
                index_result = connection.execute(text(f"PRAGMA index_list({table_name})"))
                indexes = index_result.fetchall()
                
                # 获取索引详细信息
                index_details = []
                for index in indexes:
                    index_detail_result = connection.execute(text(f"PRAGMA index_info({index[1]})"))
                    index_details.append(index_detail_result.fetchall())
                
                # 格式化分析结果
                lines = [f"表 {table_name} 分析报告:"]
                lines.append("=" * 50)
                lines.append(f"总行数: {row_count}")
                lines.append(f"字段数: {len(schema)}")
                lines.append(f"索引数: {len(indexes)}")
                lines.append("")
                
                # 字段分析
                lines.append("字段分析:")
                lines.append("ID\t\t字段名\t\t类型\t\t是否为空\t\t默认值")
                lines.append("-" * 80)
                
                for field in schema:
                    lines.append(f"{field[0]}\t\t{field[1]}\t\t{field[2]}\t\t{field[3]}\t\t{field[4] or 'NULL'}")
                
                # 索引分析
                if indexes:
                    lines.append("")
                    lines.append("索引分析:")
                    for i, index in enumerate(indexes):
                        lines.append(f"索引 {index[1]}:")
                        lines.append(f"  唯一: {index[2]}")
                        lines.append(f"  根页: {index[3]}")
                        
                        if i < len(index_details):
                            lines.append("  索引字段:")
                            for detail in index_details[i]:
                                lines.append(f"    {detail[2]} (列 {detail[1]})")
                        lines.append("")
                
                # 性能建议
                lines.append("性能建议:")
                if row_count > 10000 and not indexes:
                    lines.append("  - 考虑为常用查询字段添加索引")
                if len(schema) > 10:
                    lines.append("  - 表字段较多，考虑是否需要拆分")
                if row_count > 100000:
                    lines.append("  - 大表查询可能较慢，考虑分页或优化查询")
                
                return "\n".join(lines)
                
        except Exception as e:
            return f"分析表时出错: {str(e)}"