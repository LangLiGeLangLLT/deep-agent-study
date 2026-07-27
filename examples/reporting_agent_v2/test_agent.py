"""
Reporting Agent 测试脚本
用于验证 Agent 的基本功能和工具调用
"""

import os
import sys
import unittest
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from agent import reporting_agent, get_db_connection

class TestReportingAgent(unittest.TestCase):
    """Reporting Agent 测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 确保数据库存在
        try:
            conn = get_db_connection("sales")
            conn.close()
        except:
            # 如果数据库不存在，跳过相关测试
            self.skipTest("数据库未初始化，请先运行 data/setup_sample_data.py")
    
    def test_sales_data_query(self):
        """测试销售数据查询"""
        print("\n测试销售数据查询...")
        
        # 测试每日销售数据查询
        result = reporting_agent.invoke({
            "messages": [
                "查询最近7天的每日销售数据"
            ]
        })
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertIn("messages", result)
        
        # 检查是否有工具调用
        tool_calls = []
        for msg in result.get("messages", []):
            if hasattr(msg, "content") and msg.content:
                if "query_sales_data" in msg.content:
                    tool_calls.append(msg.content)
        
        self.assertGreater(len(tool_calls), 0, "应该调用销售数据查询工具")
    
    def test_user_analytics_query(self):
        """测试用户分析查询"""
        print("\n测试用户分析查询...")
        
        result = reporting_agent.invoke({
            "messages": [
                "统计最近30天的活跃用户数量"
            ]
        })
        
        self.assertIsNotNone(result)
        self.assertIn("messages", result)
    
    def test_financial_reports_query(self):
        """测试财务报表查询"""
        print("\n测试财务报表查询...")
        
        result = reporting_agent.invoke({
            "messages": [
                "生成2024年上半月的收入报表"
            ]
        })
        
        self.assertIsNotNone(result)
        self.assertIn("messages", result)
    
    def test_inventory_data_query(self):
        """测试库存数据查询"""
        print("\n测试库存数据查询...")
        
        result = reporting_agent.invoke({
            "messages": [
                "查询各个仓库的库存汇总情况"
            ]
        })
        
        self.assertIsNotNone(result)
        self.assertIn("messages", result)
    
    def test_custom_reports_query(self):
        """测试自定义报表查询"""
        print("\n测试自定义报表查询...")
        
        result = reporting_agent.invoke({
            "messages": [
                "分析客户的购买行为，进行客户分群"
            ]
        })
        
        self.assertIsNotNone(result)
        self.assertIn("messages", result)
    
    def test_complex_query(self):
        """测试复杂查询"""
        print("\n测试复杂查询...")
        
        result = reporting_agent.invoke({
            "messages": [
                "分析不同产品类别在不同地区的销售表现"
            ]
        })
        
        self.assertIsNotNone(result)
        self.assertIn("messages", result)
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n测试错误处理...")
        
        # 测试无效的查询类型
        result = reporting_agent.invoke({
            "messages": [
                "查询一些不存在的数据类型"
            ]
        })
        
        self.assertIsNotNone(result)
        # 即使查询失败，也应该返回合理的响应
    
    def test_database_connections(self):
        """测试数据库连接"""
        print("\n测试数据库连接...")
        
        try:
            # 测试销售数据库连接
            conn = get_db_connection("sales")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            conn.close()
            
            self.assertGreater(count, 0, "产品表应该有数据")
            
            # 测试用户分析数据库连接
            conn = get_db_connection("analytics")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_activities")
            count = cursor.fetchone()[0]
            conn.close()
            
            self.assertGreater(count, 0, "用户活动表应该有数据")
            
        except Exception as e:
            self.fail(f"数据库连接测试失败: {e}")

def run_tests():
    """运行所有测试"""
    print("开始运行 Reporting Agent 测试...")
    print("=" * 50)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReportingAgent)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("所有测试通过！")
    else:
        print(f"测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
        
        # 输出失败详情
        for test, traceback in result.failures:
            print(f"\n失败: {test}")
            print(traceback)
        
        for test, traceback in result.errors:
            print(f"\n错误: {test}")
            print(traceback)

if __name__ == "__main__":
    # 检查环境变量
    if not os.getenv("LLM_API_KEY"):
        print("警告: LLM_API_KEY 环境变量未设置")
        print("请在 .env 文件中设置您的 API 密钥")
        sys.exit(1)
    
    # 运行测试
    run_tests()