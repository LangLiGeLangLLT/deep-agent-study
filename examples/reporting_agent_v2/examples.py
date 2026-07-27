"""
Reporting Agent 使用示例
演示如何使用 Reporting Agent 进行各种数据分析
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from agent import reporting_agent

def test_sales_analysis():
    """测试销售数据分析"""
    print("=== 销售数据分析示例 ===")
    
    # 示例1: 查询最近30天的每日销售数据
    print("\n1. 查询最近30天的每日销售数据:")
    result = reporting_agent.invoke({
        "messages": [
            "请帮我查询最近30天的每日销售数据，并分析销售趋势"
        ]
    })
    
    # 示例2: 查询各地区的销售情况
    print("\n2. 分析各地区的销售业绩:")
    result = reporting_agent.invoke({
        "messages": [
            "分析一下华东、华南、华北三个地区的销售业绩对比"
        ]
    })
    
    # 示例3: 查询热销产品
    print("\n3. 查询最受欢迎的产品:")
    result = reporting_agent.invoke({
        "messages": [
            "列出销量最高的前10个产品"
        ]
    })

def test_user_analytics():
    """测试用户分析"""
    print("\n=== 用户分析示例 ===")
    
    # 示例1: 查询活跃用户
    print("\n1. 统计最近7天的日活跃用户数量:")
    result = reporting_agent.invoke({
        "messages": [
            "统计最近7天的日活跃用户数量"
        ]
    })
    
    # 示例2: 分析用户留存率
    print("\n2. 计算最近30天用户的留存率:")
    result = reporting_agent.invoke({
        "messages": [
            "计算最近30天用户的留存率情况"
        ]
    })
    
    # 示例3: 分析会话时长
    print("\n3. 分析用户会话时长:")
    result = reporting_agent.invoke({
        "messages": [
            "分析不同平台的用户平均会话时长"
        ]
    })

def test_financial_reports():
    """测试财务报表"""
    print("\n=== 财务报表示例 ===")
    
    # 示例1: 生成月度收入报表
    print("\n1. 生成2024年上半年的月度收入报表:")
    result = reporting_agent.invoke({
        "messages": [
            "生成2024年上半年的月度收入报表"
        ]
    })
    
    # 示例2: 分析部门支出
    print("\n2. 分析各部门支出情况:")
    result = reporting_agent.invoke({
        "messages": [
            "分析技术部和市场部上半年的支出对比"
        ]
    })
    
    # 示例3: 生成损益表
    print("\n3. 生成第二季度损益表:")
    result = reporting_agent.invoke({
        "messages": [
            "生成2024年第二季度的损益表"
        ]
    })

def test_inventory_management():
    """测试库存管理"""
    print("\n=== 库存管理示例 ===")
    
    # 示例1: 查询低库存商品
    print("\n1. 列出低库存商品:")
    result = reporting_agent.invoke({
        "messages": [
            "列出所有库存低于安全阈值的商品"
        ]
    })
    
    # 示例2: 仓库库存汇总
    print("\n2. 汇总各个仓库的库存情况:")
    result = reporting_agent.invoke({
        "messages": [
            "汇总各个仓库的库存情况"
        ]
    })
    
    # 示例3: 库存变动分析
    print("\n3. 分析最近30天的库存变动:")
    result = reporting_agent.invoke({
        "messages": [
            "分析最近30天的库存变动情况"
        ]
    })

def test_custom_reports():
    """测试自定义报表"""
    print("\n=== 自定义报表示例 ===")
    
    # 示例1: 客户分群分析
    print("\n1. 客户分群分析:")
    result = reporting_agent.invoke({
        "messages": [
            "分析客户的购买行为，进行客户分群"
        ]
    })
    
    # 示例2: 产品性能分析
    print("\n2. 产品性能分析:")
    result = reporting_agent.invoke({
        "messages": [
            "分析各产品的销售表现，找出最受欢迎的产品"
        ]
    })
    
    # 示例3: 销售业绩综合分析
    print("\n3. 销售业绩综合分析:")
    result = reporting_agent.invoke({
        "messages": [
            "综合分析销售业绩，包括收入、订单量、客单价等指标"
        ]
    })

def test_complex_queries():
    """测试复杂查询"""
    print("\n=== 复杂查询示例 ===")
    
    # 示例1: 跨维度分析
    print("\n1. 跨维度销售分析:")
    result = reporting_agent.invoke({
        "messages": [
            "分析不同产品类别在不同地区的销售表现，并找出增长最快的产品"
        ]
    })
    
    # 示例2: 时间序列分析
    print("\n2. 销售趋势时间序列分析:")
    result = reporting_agent.invoke({
        "messages": [
            "分析过去6个月的销售趋势，识别季节性模式和增长机会"
        ]
    })
    
    # 示例3: 异常检测
    print("\n3. 销售异常检测:")
    result = reporting_agent.invoke({
        "messages": [
            "检测销售数据中的异常值，识别可能的异常订单或数据错误"
        ]
    })

def run_all_examples():
    """运行所有示例"""
    print("开始运行 Reporting Agent 示例...")
    print("=" * 50)
    
    try:
        # 运行各个示例
        test_sales_analysis()
        test_user_analytics()
        test_financial_reports()
        test_inventory_management()
        test_custom_reports()
        test_complex_queries()
        
        print("\n" + "=" * 50)
        print("所有示例运行完成！")
        
    except Exception as e:
        print(f"运行示例时发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 检查环境变量
    if not os.getenv("LLM_API_KEY"):
        print("警告: LLM_API_KEY 环境变量未设置")
        print("请在 .env 文件中设置您的 API 密钥")
        return
    
    # 运行示例
    run_all_examples()