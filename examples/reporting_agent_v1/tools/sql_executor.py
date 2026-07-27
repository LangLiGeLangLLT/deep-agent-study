"""
通用 SQL 执行器

支持多种数据库的 SQL 查询执行和结果处理。
"""

import re
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from langchain_core.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class SQLExecutor:
    """通用 SQL 执行器"""
    
    def __init__(self, database_url: str, max_rows: int = 1000):
        self.database_url = database_url
        self.max_rows = max_rows
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """初始化数据库引擎"""
        try:
            self.engine = create_engine(self.database_url)
        except Exception as e:
            raise ValueError(f"无法创建数据库引擎: {e}")
    
    def _validate_sql(self, sql: str) -> bool:
        """验证 SQL 查询的安全性"""
        # 基本的安全检查
        dangerous_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 
            'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE'
        ]
        
        sql_upper = sql.upper().strip()
        
        # 检查危险关键词
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False
        
        # 检查是否包含分号（防止多语句攻击）
        if ';' in sql:
            return False
            
        return True
    
    def _parse_query_type(self, sql: str) -> str:
        """解析查询类型"""
        sql_upper = sql.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return 'select'
        elif sql_upper.startswith('SHOW'):
            return 'show'
        elif sql_upper.startswith('DESCRIBE') or sql_upper.startswith('DESC'):
            return 'describe'
        else:
            return 'unknown'
    
    def _format_results(self, results: Union[pd.DataFrame, List[Dict]], query_type: str) -> str:
        """格式化查询结果"""
        if isinstance(results, pd.DataFrame):
            if results.empty:
                return "查询结果为空"
            
            # 限制行数
            if len(results) > self.max_rows:
                results = results.head(self.max_rows)
                return f"查询结果（显示前 {self.max_rows} 行，共 {len(results)} 行）:\n{results.to_string(index=False)}"
            
            return results.to_string(index=False)
        
        elif isinstance(results, list):
            if not results:
                return "查询结果为空"
            
            # 格式化字典列表
            formatted_lines = []
            for i, row in enumerate(results[:self.max_rows], 1):
                formatted_lines.append(f"{i}. {row}")
            
            if len(results) > self.max_rows:
                formatted_lines.append(f"... 还有 {len(results) - self.max_rows} 行")
            
            return "\n".join(formatted_lines)
        
        else:
            return str(results)
    
    @tool
    def execute_query(self, sql: str, description: str = "") -> str:
        """
        执行 SQL 查询
        
        Args:
            sql: 要执行的 SQL 查询语句
            description: 查询描述（可选）
            
        Returns:
            查询结果字符串
        """
        if not self._validate_sql(sql):
            return "错误：SQL 查询包含不安全的内容，无法执行"
        
        try:
            query_type = self._parse_query_type(sql)
            
            with self.engine.connect() as connection:
                result = connection.execute(text(sql))
                
                if query_type == 'select':
                    # 获取 SELECT 查询结果
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())
                    return self._format_results(df, query_type)
                else:
                    # 获取其他类型查询的结果
                    rows_affected = result.rowcount
                    return f"查询执行成功，影响了 {rows_affected} 行"
                    
        except SQLAlchemyError as e:
            return f"数据库错误: {str(e)}"
        except Exception as e:
            return f"执行错误: {str(e)}"
    
    @tool
    def get_tables(self) -> str:
        """
        获取数据库中的所有表名
        
        Returns:
            表名列表
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SHOW TABLES"))
                tables = [row[0] for row in result.fetchall()]
                
                if not tables:
                    return "数据库中没有表"
                
                return "数据库中的表:\n" + "\n".join([f"{i+1}. {table}" for i, table in enumerate(tables)])
                
        except Exception as e:
            return f"获取表列表时出错: {str(e)}"
    
    @tool
    def get_table_schema(self, table_name: str) -> str:
        """
        获取表的 schema 信息
        
        Args:
            table_name: 表名
            
        Returns:
            表的 schema 信息
        """
        if not self._validate_sql(table_name):
            return "错误：表名包含不安全的内容"
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(f"DESCRIBE {table_name}"))
                schema = result.fetchall()
                
                if not schema:
                    return f"表 {table_name} 不存在或为空"
                
                # 格式化 schema 信息
                schema_lines = [f"表 {table_name} 的结构:"]
                schema_lines.append("字段名\t\t数据类型\t\t是否为空\t\t键\t\t默认值\t\t额外")
                schema_lines.append("-" * 80)
                
                for row in schema:
                    schema_lines.append("\t".join(str(cell) for cell in row))
                
                return "\n".join(schema_lines)
                
        except Exception as e:
            return f"获取表 schema 时出错: {str(e)}"
    
    @tool
    def analyze_query(self, sql: str) -> str:
        """
        分析 SQL 查询
        
        Args:
            sql: 要分析的 SQL 查询
            
        Returns:
            查询分析结果
        """
        if not sql.strip():
            return "错误：SQL 语句为空"
        
        query_type = self._parse_query_type(sql)
        
        analysis = {
            "query_type": query_type,
            "is_select": query_type == 'select',
            "is_safe": self._validate_sql(sql),
            "estimated_complexity": self._estimate_complexity(sql)
        }
        
        return f"SQL 查询分析:\n- 类型: {analysis['query_type']}\n- 安全性: {'安全' if analysis['is_safe'] else '不安全'}\n- 复杂度: {analysis['estimated_complexity']}"
    
    def _estimate_complexity(self, sql: str) -> str:
        """估算查询复杂度"""
        sql_upper = sql.upper()
        
        # 简单的复杂度估算
        if 'JOIN' in sql_upper:
            return "中等"
        elif 'GROUP BY' in sql_upper or 'HAVING' in sql_upper:
            return "中等"
        elif 'SUBQUERY' in sql_upper or 'UNION' in sql_upper:
            return "高"
        else:
            return "低"