"""
Reporting Agent 使用示例

演示如何使用 Reporting Agent 进行数据查询和分析。
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reporting_agent import create_reporting_agent
from reporting_agent.utils import create_sample_database

def main():
    """主函数"""
    print("=== Reporting Agent 使用示例 ===\n")
    
    # 创建示例数据库
    print("1. 创建示例数据库...")
    db_path = create_sample_database()
    print(f"   示例数据库已创建: {db_path}")
    
    # 配置 Agent
    print("\n2. 配置 Reporting Agent...")
    from reporting_agent.config import Config
    
    config = Config(
        sqlite_enabled=True,
        sqlite_path=db_path,
        max_rows=10,
        enable_query_analysis=True
    )
    
    # 创建 Agent
    print("   创建 Reporting Agent...")
    agent = create_reporting_agent(config)
    
    # 显示可用工具
    print("\n3. 可用工具:")
    tools = agent.get_available_tools()
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool}")
    
    # 示例查询
    print("\n4. 执行示例查询...")
    
    queries = [
        "获取所有员工的信息",
        "显示技术部的所有员工",
        "统计每个部门的员工数量",
        "获取员工薪资的平均值",
        "显示数据库中的所有表",
        "分析 employees 表的结构"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- 示例 {i}: {query} ---")
        try:
            result = agent.process_query(query)
            if result['success']:
                print("✓ 查询成功:")
                print(result['result'])
            else:
                print("✗ 查询失败:")
                print(result['error'])
        except Exception as e:
            print(f"✗ 执行出错: {e}")
    
    print("\n=== 示例完成 ===")

if __name__ == "__main__":
    main()