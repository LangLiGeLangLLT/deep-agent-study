"""
Reporting Agent 主实现

基于 create_deep_agent 框架构建，支持智能 SQL 工具选择和执行。
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from deepagents import create_deep_agent
from .tools import SQLExecutor, MySQLTools, PostgreSQLTools, SQLiteTools
from .prompts import REPORTING_INSTRUCTIONS, WORKFLOW_INSTRUCTIONS
from .config import Config

class ReportingAgent:
    """报表生成 Agent"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.tools = self._initialize_tools()
        self.agent = self._create_agent()
        
    def _initialize_tools(self) -> List[Any]:
        """初始化所有可用的 SQL 工具"""
        tools = []
        
        # 通用 SQL 执行器
        tools.append(SQLExecutor(
            database_url=self.config.database_url,
            max_rows=self.config.max_rows
        ))
        
        # 数据库特定工具
        if self.config.mysql_enabled:
            tools.append(MySQLTools(
                host=self.config.mysql_host,
                port=self.config.mysql_port,
                username=self.config.mysql_username,
                password=self.config.mysql_password,
                database=self.config.mysql_database
            ))
            
        if self.config.postgres_enabled:
            tools.append(PostgreSQLTools(
                host=self.config.postgres_host,
                port=self.config.postgres_port,
                username=self.config.postgres_username,
                password=self.config.postgres_password,
                database=self.config.postgres_database
            ))
            
        if self.config.sqlite_enabled:
            tools.append(SQLiteTools(
                database_path=self.config.sqlite_path
            ))
            
        return tools
    
    def _create_agent(self):
        """创建基于 deepagents 的 Agent"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # 组合指令
        instructions = (
            WORKFLOW_INSTRUCTIONS + 
            "\n\n" + 
            "=" * 80 + 
            "\n\n" + 
            REPORTING_INSTRUCTIONS.format(
                date=current_date,
                available_tools=len(self.tools)
            )
        )
        
        # 创建 Agent
        agent = create_deep_agent(
            name="reporting-agent",
            description="智能报表生成 Agent，能够根据用户问题选择合适的 SQL 工具获取数据",
            system_prompt=instructions,
            tools=self.tools,
            max_iterations=self.config.max_iterations
        )
        
        return agent
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """处理用户查询"""
        try:
            result = self.agent.invoke(user_query)
            return {
                "success": True,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_tools(self) -> List[str]:
        """获取可用的工具列表"""
        return [tool.__class__.__name__ for tool in self.tools]

def create_reporting_agent(config: Optional[Config] = None) -> ReportingAgent:
    """创建 Reporting Agent 实例"""
    return ReportingAgent(config)