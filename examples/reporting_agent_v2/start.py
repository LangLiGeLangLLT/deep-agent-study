#!/usr/bin/env python3
"""
Reporting Agent 启动脚本
快速启动和配置 Reporting Agent
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        "deepagents",
        "langchain-openai", 
        "python-dotenv",
        "pandas"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        
        print("\n正在安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("依赖安装完成！")
        except subprocess.CalledProcessError:
            print("依赖安装失败，请手动安装:")
            for package in missing_packages:
                print(f"  pip install {package}")
            return False
    
    return True

def check_environment():
    """检查环境配置"""
    env_file = Path(".env")
    if not env_file.exists():
        print("未找到 .env 文件，正在创建...")
        try:
            # 复制示例配置
            example_file = Path(".env.example")
            if example_file.exists():
                import shutil
                shutil.copy2(example_file, env_file)
                print("已创建 .env 文件，请编辑其中的配置")
            else:
                # 创建基本的 .env 文件
                with open(env_file, 'w') as f:
                    f.write("""# Reporting Agent 环境配置
LLM_MODEL_ID=gpt-4
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
""")
                print("已创建基本的 .env 文件")
        except Exception as e:
            print(f"创建 .env 文件失败: {e}")
            return False
    
    # 检查 API 密钥
    api_key = os.getenv("LLM_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("警告: LLM_API_KEY 未正确设置")
        print("请编辑 .env 文件，设置您的 API 密钥")
        return False
    
    return True

def setup_database():
    """设置数据库"""
    data_dir = Path("data")
    if not data_dir.exists():
        print("创建数据目录...")
        data_dir.mkdir()
    
    # 检查数据库文件是否存在
    db_files = ["sales.db", "analytics.db", "financial.db", "inventory.db"]
    missing_dbs = []
    
    for db_file in db_files:
        db_path = data_dir / db_file
        if not db_path.exists():
            missing_dbs.append(db_file)
    
    if missing_dbs:
        print("检测到缺少数据库文件，正在创建示例数据...")
        try:
            # 运行数据设置脚本
            script_path = Path("data/setup_sample_data.py")
            if script_path.exists():
                subprocess.check_call([sys.executable, str(script_path)])
                print("示例数据创建完成！")
            else:
                print("未找到数据设置脚本，请手动创建数据库")
                return False
        except subprocess.CalledProcessError:
            print("创建示例数据失败")
            return False
    
    return True

def start_agent():
    """启动 Agent"""
    print("正在启动 Reporting Agent...")
    
    try:
        # 导入并运行 Agent
        from agent import reporting_agent
        
        print("Reporting Agent 已启动！")
        print("您可以开始提问，例如：")
        print("  - 查询最近30天的销售数据")
        print("  - 分析用户留存率")
        print("  - 生成财务报表")
        print("  - 查询库存情况")
        print("\n输入 'quit' 或 'exit' 退出")
        
        # 简单的交互循环
        while True:
            try:
                user_input = input("\n请输入您的问题: ").strip()
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("再见！")
                    break
                
                if not user_input:
                    continue
                
                # 调用 Agent
                result = reporting_agent.invoke({
                    "messages": [user_input]
                })
                
                # 显示结果
                for msg in result.get("messages", []):
                    if hasattr(msg, "content") and msg.content:
                        print(f"\n{msg.content}")
                        
            except KeyboardInterrupt:
                print("\n\n程序被用户中断")
                break
            except Exception as e:
                print(f"发生错误: {e}")
                
    except Exception as e:
        print(f"启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=== Reporting Agent 启动器 ===")
    print()
    
    # 检查依赖
    if not check_dependencies():
        print("依赖检查失败，请解决上述问题后重试")
        return False
    
    # 检查环境
    if not check_environment():
        print("环境配置检查失败，请解决上述问题后重试")
        return False
    
    # 设置数据库
    if not setup_database():
        print("数据库设置失败，请解决上述问题后重试")
        return False
    
    # 启动 Agent
    if start_agent():
        print("程序运行完成")
        return True
    else:
        print("程序运行失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)