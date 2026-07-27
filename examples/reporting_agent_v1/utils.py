"""
Reporting Agent 工具函数

提供通用的工具函数和辅助方法。
"""

import re
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

def validate_sql(sql: str) -> Tuple[bool, str]:
    """
    验证 SQL 查询的安全性
    
    Args:
        sql: SQL 查询语句
        
    Returns:
        (是否安全, 错误信息)
    """
    if not sql or not sql.strip():
        return False, "SQL 语句为空"
    
    sql_upper = sql.upper().strip()
    
    # 危险关键词检查
    dangerous_keywords = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 
        'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE',
        'GRANT', 'REVOKE', 'BEGIN', 'COMMIT', 'ROLLBACK'
    ]
    
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False, f"包含危险关键词: {keyword}"
    
    # 多语句检查
    if ';' in sql:
        # 允许在注释中的分号
        if not re.search(r'/\*.*?\*/', sql, re.DOTALL):
            return False, "包含多个 SQL 语句"
    
    # 检查是否包含注释（可选的安全措施）
    if '--' in sql or '/*' in sql:
        # 允许注释，但需要确保注释不会影响查询逻辑
        pass
    
    return True, "SQL 查询安全"

def parse_query_type(sql: str) -> str:
    """
    解析 SQL 查询类型
    
    Args:
        sql: SQL 查询语句
        
    Returns:
        查询类型
    """
    if not sql or not sql.strip():
        return "unknown"
    
    sql_upper = sql.upper().strip()
    
    if sql_upper.startswith('SELECT'):
        return 'select'
    elif sql_upper.startswith('SHOW'):
        return 'show'
    elif sql_upper.startswith('DESCRIBE') or sql_upper.startswith('DESC'):
        return 'describe'
    elif sql_upper.startswith('EXPLAIN'):
        return 'explain'
    else:
        return 'unknown'

def format_results(results: pd.DataFrame, max_rows: int = 1000) -> str:
    """
    格式化查询结果
    
    Args:
        results: 查询结果 DataFrame
        max_rows: 最大显示行数
        
    Returns:
        格式化后的结果字符串
    """
    if results.empty:
        return "查询结果为空"
    
    # 限制行数
    if len(results) > max_rows:
        results = results.head(max_rows)
        return f"查询结果（显示前 {max_rows} 行，共 {len(results)} 行）:\n{results.to_string(index=False)}"
    
    return results.to_string(index=False)

def generate_insights(results: pd.DataFrame, query_type: str) -> str:
    """
    生成数据洞察
    
    Args:
        results: 查询结果
        query_type: 查询类型
        
    Returns:
        数据洞察字符串
    """
    if results.empty:
        return "没有足够的数据生成洞察"
    
    insights = []
    
    # 基本统计信息
    if len(results) > 0:
        insights.append(f"数据集包含 {len(results)} 行记录")
        
        if len(results.columns) > 0:
            insights.append(f"涉及 {len(results.columns)} 个字段")
    
    # 数值字段分析
    numeric_columns = results.select_dtypes(include=['number']).columns
    if len(numeric_columns) > 0:
        insights.append("数值字段分析:")
        for col in numeric_columns:
            if len(results[col]) > 0:
                non_null_count = results[col].count()
                null_count = results[col].isnull().sum()
                insights.append(f"  - {col}: {non_null_count} 个非空值, {null_count} 个空值")
    
    # 文本字段分析
    text_columns = results.select_dtypes(include=['object']).columns
    if len(text_columns) > 0:
        insights.append("文本字段分析:")
        for col in text_columns:
            unique_count = results[col].nunique()
            insights.append(f"  - {col}: {unique_count} 个唯一值")
    
    return "\n".join(insights)

def create_sample_database() -> str:
    """
    创建示例数据库和表
    
    Returns:
        数据库文件路径
    """
    import sqlite3
    import os
    
    # 创建数据目录
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # 数据库文件路径
    db_path = os.path.join(data_dir, "sample.db")
    
    # 创建数据库连接
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建示例表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT,
        salary REAL,
        hire_date TEXT,
        status TEXT
    )
    ''')
    
    # 插入示例数据
    cursor.execute('''
    INSERT OR IGNORE INTO employees (id, name, department, salary, hire_date, status) 
    VALUES 
        (1, '张三', '技术部', 8000, '2023-01-15', '在职'),
        (2, '李四', '销售部', 6000, '2023-02-20', '在职'),
        (3, '王五', '技术部', 9000, '2022-12-10', '在职'),
        (4, '赵六', '人事部', 5000, '2023-03-05', '离职'),
        (5, '钱七', '技术部', 7500, '2023-04-12', '在职'),
        (6, '孙八', '销售部', 6500, '2023-01-25', '在职'),
        (7, '周九', '财务部', 7000, '2023-02-28', '在职'),
        (8, '吴十', '技术部', 8500, '2022-11-15', '在职')
    ''')
    
    # 创建第二个示例表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        manager TEXT,
        budget REAL,
        location TEXT
    )
    ''')
    
    # 插入部门数据
    cursor.execute('''
    INSERT OR IGNORE INTO departments (id, name, manager, budget, location) 
    VALUES 
        (1, '技术部', '张三', 500000, '北京'),
        (2, '销售部', '李四', 300000, '上海'),
        (3, '人事部', '赵六', 200000, '北京'),
        (4, '财务部', '周九', 250000, '深圳')
    ''')
    
    # 提交更改并关闭连接
    conn.commit()
    conn.close()
    
    return db_path

def get_database_info(db_path: str) -> Dict[str, Any]:
    """
    获取数据库信息
    
    Args:
        db_path: 数据库文件路径
        
    Returns:
        数据库信息字典
    """
    import sqlite3
    
    if not os.path.exists(db_path):
        return {"error": "数据库文件不存在"}
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取表信息
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    # 获取每个表的统计信息
    table_stats = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        table_stats[table] = count
    
    # 获取数据库大小
    db_size = os.path.getsize(db_path)
    
    conn.close()
    
    return {
        "database_path": db_path,
        "database_size": db_size,
        "tables": tables,
        "table_stats": table_stats,
        "total_tables": len(tables),
        "total_rows": sum(table_stats.values())
    }