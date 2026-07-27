import os
import sqlite3
import pandas as pd
from typing import Dict, List, Any, Optional, Literal
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain.tools import tool
from pathlib import Path

load_dotenv()

# 初始化模型
model = ChatOpenAI(
    model=os.getenv("LLM_MODEL_ID"),
    model_name=os.getenv("LLM_MODEL_ID", "gpt-4"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    temperature=0,
)

# 数据库连接配置
DB_CONFIGS = {
    "sales": {
        "type": "sqlite",
        "path": "data/sales.db"
    },
    "analytics": {
        "type": "sqlite", 
        "path": "data/analytics.db"
    },
    "financial": {
        "type": "sqlite",
        "path": "data/financial.db"
    },
    "inventory": {
        "type": "sqlite",
        "path": "data/inventory.db"
    }
}

def get_db_connection(db_name: str):
    """获取数据库连接"""
    config = DB_CONFIGS.get(db_name)
    if not config:
        raise ValueError(f"Unknown database: {db_name}")
    
    if config["type"] == "sqlite":
        return sqlite3.connect(config["path"])
    else:
        raise ValueError(f"Unsupported database type: {config['type']}")

@tool
def query_sales_data(
    query_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    product_category: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    查询销售数据
    
    Args:
        query_type: 查询类型 - "daily_sales", "monthly_sales", "regional_sales", "product_sales", "top_products"
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        region: 地区筛选
        product_category: 产品类别筛选
        limit: 返回记录数限制
    
    Returns:
        查询结果字典，包含数据和元信息
    """
    try:
        conn = get_db_connection("sales")
        cursor = conn.cursor()
        
        # 根据查询类型构建不同的SQL查询
        if query_type == "daily_sales":
            sql = """
            SELECT DATE(order_date) as date, SUM(total_amount) as total_sales, 
                   COUNT(order_id) as order_count
            FROM sales_orders 
            WHERE order_date BETWEEN ? AND ?
            GROUP BY DATE(order_date)
            ORDER BY date DESC
            LIMIT ?
            """
            params = [start_date or "2024-01-01", end_date or "2024-12-31", limit]
            
        elif query_type == "monthly_sales":
            sql = """
            SELECT strftime('%Y-%m', order_date) as month, 
                   SUM(total_amount) as total_sales, 
                   COUNT(order_id) as order_count
            FROM sales_orders 
            WHERE order_date BETWEEN ? AND ?
            GROUP BY strftime('%Y-%m', order_date)
            ORDER BY month DESC
            LIMIT ?
            """
            params = [start_date or "2024-01-01", end_date or "2024-12-31", limit]
            
        elif query_type == "regional_sales":
            sql = """
            SELECT region, SUM(total_amount) as total_sales, 
                   COUNT(order_id) as order_count
            FROM sales_orders 
            WHERE order_date BETWEEN ? AND ?
            GROUP BY region
            ORDER BY total_sales DESC
            LIMIT ?
            """
            params = [start_date or "2024-01-01", end_date or "2024-12-31", limit]
            
        elif query_type == "product_sales":
            sql = """
            SELECT p.product_name, p.category, SUM(so.total_amount) as total_sales,
                   COUNT(so.order_id) as order_count
            FROM sales_orders so
            JOIN order_items oi ON so.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE so.order_date BETWEEN ? AND ?
            AND p.category = COALESCE(?, p.category)
            GROUP BY p.product_name, p.category
            ORDER BY total_sales DESC
            LIMIT ?
            """
            params = [start_date or "2024-01-01", end_date or "2024-12-31", product_category, limit]
            
        elif query_type == "top_products":
            sql = """
            SELECT p.product_name, p.category, SUM(oi.quantity) as total_quantity,
                   SUM(so.total_amount) as total_revenue
            FROM sales_orders so
            JOIN order_items oi ON so.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE so.order_date BETWEEN ? AND ?
            GROUP BY p.product_name, p.category
            ORDER BY total_revenue DESC
            LIMIT ?
            """
            params = [start_date or "2024-01-01", end_date or "2024-12-31", limit]
        else:
            raise ValueError(f"Unsupported query type: {query_type}")
        
        cursor.execute(sql, params)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        result = {
            "data": [dict(zip(columns, row)) for row in rows],
            "query_type": query_type,
            "total_records": len(rows),
            "parameters": {
                "start_date": start_date,
                "end_date": end_date,
                "region": region,
                "product_category": product_category,
                "limit": limit
            }
        }
        
        conn.close()
        return result
        
    except Exception as e:
        return {"error": f"Sales data query failed: {str(e)}"}

@tool
def query_user_analytics(
    metric: str,
    time_period: str = "30d",
    user_segment: Optional[str] = None,
    platform: Optional[str] = None
) -> Dict[str, Any]:
    """
    查询用户分析数据
    
    Args:
        metric: 指标类型 - "active_users", "user_retention", "session_duration", "conversion_rate"
        time_period: 时间周期 - "7d", "30d", "90d", "1y"
        user_segment: 用户群体筛选
        platform: 平台筛选
    
    Returns:
        查询结果字典
    """
    try:
        conn = get_db_connection("analytics")
        cursor = conn.cursor()
        
        # 根据指标类型构建查询
        if metric == "active_users":
            sql = """
            SELECT DATE(activity_date) as date, COUNT(DISTINCT user_id) as active_users
            FROM user_activities 
            WHERE activity_date >= date('now', ?)
            AND platform = COALESCE(?, platform)
            GROUP BY DATE(activity_date)
            ORDER BY date DESC
            """
            params = [f"-{time_period}", platform]
            
        elif metric == "user_retention":
            sql = """
            SELECT cohort_week, 
                   COUNT(DISTINCT user_id) as cohort_size,
                   COUNT(CASE WHEN retained = 1 THEN 1 END) as retained_users,
                   ROUND(COUNT(CASE WHEN retained = 1 THEN 1 END) * 100.0 / COUNT(DISTINCT user_id), 2) as retention_rate
            FROM user_retention
            WHERE cohort_week >= date('now', ?)
            AND user_segment = COALESCE(?, user_segment)
            GROUP BY cohort_week
            ORDER BY cohort_week DESC
            """
            params = [f"-{time_period}", user_segment]
            
        elif metric == "session_duration":
            sql = """
            SELECT platform, 
                   AVG(session_duration) as avg_duration,
                   COUNT(session_id) as session_count
            FROM user_sessions
            WHERE session_date >= date('now', ?)
            AND platform = COALESCE(?, platform)
            GROUP BY platform
            """
            params = [f"-{time_period}", platform]
            
        elif metric == "conversion_rate":
            sql = """
            DATE(created_at) as date,
            COUNT(CASE WHEN status = 'converted' THEN 1 END) * 100.0 / COUNT(*) as conversion_rate,
            COUNT(*) as total_leads
            FROM marketing_leads
            WHERE created_at >= date('now', ?)
            AND user_segment = COALESCE(?, user_segment)
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            """
            params = [f"-{time_period}", user_segment]
        else:
            raise ValueError(f"Unsupported metric: {metric}")
        
        cursor.execute(sql, params)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        result = {
            "data": [dict(zip(columns, row)) for row in rows],
            "metric": metric,
            "time_period": time_period,
            "total_records": len(rows),
            "parameters": {
                "user_segment": user_segment,
                "platform": platform
            }
        }
        
        conn.close()
        return result
        
    except Exception as e:
        return {"error": f"User analytics query failed: {str(e)}"}

@tool
def query_financial_reports(
    report_type: str,
    period: str = "monthly",
    fiscal_year: Optional[int] = None,
    department: Optional[str] = None
) -> Dict[str, Any]:
    """
    查询财务报表数据
    
    Args:
        report_type: 报表类型 - "revenue", "expenses", "profit_loss", "cash_flow"
        period: 报表周期 - "daily", "weekly", "monthly", "quarterly", "yearly"
        fiscal_year: 财务年份
        department: 部门筛选
    
    Returns:
        查询结果字典
    """
    try:
        conn = get_db_connection("financial")
        cursor = conn.cursor()
        
        # 根据报表类型构建查询
        if report_type == "revenue":
            sql = """
            SELECT strftime(?, transaction_date) as period,
                   SUM(amount) as total_revenue,
                   COUNT(transaction_id) as transaction_count
            FROM financial_transactions
            WHERE transaction_type = 'revenue'
            AND strftime('%Y', transaction_date) = COALESCE(?, strftime('%Y', transaction_date))
            GROUP BY strftime(?, transaction_date)
            ORDER BY period DESC
            """
            period_format = {"daily": "%Y-%m-%d", "weekly": "%Y-%W", "monthly": "%Y-%m", "quarterly": "%Y-Q", "yearly": "%Y"}[period]
            params = [period_format, str(fiscal_year or 2024), period_format]
            
        elif report_type == "expenses":
            sql = """
            SELECT strftime(?, transaction_date) as period,
                   category,
                   SUM(amount) as total_expenses,
                   COUNT(transaction_id) as transaction_count
            FROM financial_transactions
            WHERE transaction_type = 'expense'
            AND strftime('%Y', transaction_date) = COALESCE(?, strftime('%Y', transaction_date))
            AND department = COALESCE(?, department)
            GROUP BY strftime(?, transaction_date), category
            ORDER BY period DESC, total_expenses DESC
            """
            period_format = {"daily": "%Y-%m-%d", "weekly": "%Y-%W", "monthly": "%Y-%m", "quarterly": "%Y-Q", "yearly": "%Y"}[period]
            params = [period_format, str(fiscal_year or 2024), department, period_format]
            
        elif report_type == "profit_loss":
            sql = """
            SELECT strftime(?, transaction_date) as period,
                   SUM(CASE WHEN transaction_type = 'revenue' THEN amount ELSE 0 END) as revenue,
                   SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as expenses,
                   SUM(CASE WHEN transaction_type = 'revenue' THEN amount ELSE -amount END) as net_income
            FROM financial_transactions
            WHERE strftime('%Y', transaction_date) = COALESCE(?, strftime('%Y', transaction_date))
            GROUP BY strftime(?, transaction_date)
            ORDER BY period DESC
            """
            period_format = {"daily": "%Y-%m-%d", "weekly": "%Y-%W", "monthly": "%Y-%m", "quarterly": "%Y-Q", "yearly": "%Y"}[period]
            params = [period_format, str(fiscal_year or 2024), period_format]
            
        elif report_type == "cash_flow":
            sql = """
            SELECT strftime(?, transaction_date) as period,
                   transaction_type,
                   SUM(amount) as cash_flow_amount,
                   COUNT(transaction_id) as transaction_count
            FROM financial_transactions
            WHERE strftime('%Y', transaction_date) = COALESCE(?, strftime('%Y', transaction_date))
            GROUP BY strftime(?, transaction_date), transaction_type
            ORDER BY period DESC, transaction_type
            """
            period_format = {"daily": "%Y-%m-%d", "weekly": "%Y-%W", "monthly": "%Y-%m", "quarterly": "%Y-Q", "yearly": "%Y"}[period]
            params = [period_format, str(fiscal_year or 2024), period_format]
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
        
        cursor.execute(sql, params)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        result = {
            "data": [dict(zip(columns, row)) for row in rows],
            "report_type": report_type,
            "period": period,
            "total_records": len(rows),
            "parameters": {
                "fiscal_year": fiscal_year,
                "department": department
            }
        }
        
        conn.close()
        return result
        
    except Exception as e:
        return {"error": f"Financial report query failed: {str(e)}"}

@tool
def query_inventory_data(
    analysis_type: str,
    category: Optional[str] = None,
    warehouse: Optional[str] = None,
    low_stock_threshold: Optional[int] = None
) -> Dict[str, Any]:
    """
    查询库存数据
    
    Args:
        analysis_type: 分析类型 - "stock_levels", "movement_history", "low_stock", "warehouse_summary"
        category: 产品类别筛选
        warehouse: 仓库筛选
        low_stock_threshold: 低库存阈值
    
    Returns:
        查询结果字典
    """
    try:
        conn = get_db_connection("inventory")
        cursor = conn.cursor()
        
        # 根据分析类型构建查询
        if analysis_type == "stock_levels":
            sql = """
            SELECT p.product_name, p.category, i.quantity, i.warehouse,
                   i.reorder_level, i.last_updated
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            WHERE p.category = COALESCE(?, p.category)
            AND i.warehouse = COALESCE(?, i.warehouse)
            ORDER BY i.quantity ASC
            """
            params = [category, warehouse]
            
        elif analysis_type == "movement_history":
            sql = """
            SELECT m.transaction_date, m.transaction_type, m.quantity_change,
                   p.product_name, p.category, m.warehouse
            FROM inventory_movements m
            JOIN products p ON m.product_id = p.product_id
            WHERE p.category = COALESCE(?, p.category)
            AND m.warehouse = COALESCE(?, m.warehouse)
            ORDER BY m.transaction_date DESC
            LIMIT 100
            """
            params = [category, warehouse]
            
        elif analysis_type == "low_stock":
            sql = """
            SELECT p.product_name, p.category, i.quantity, i.reorder_level,
                   i.warehouse, (i.reorder_level - i.quantity) as shortage_amount
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            WHERE i.quantity <= COALESCE(?, i.reorder_level)
            AND p.category = COALESCE(?, p.category)
            AND i.warehouse = COALESCE(?, i.warehouse)
            ORDER BY shortage_amount DESC
            """
            params = [low_stock_threshold, category, warehouse]
            
        elif analysis_type == "warehouse_summary":
            sql = """
            SELECT i.warehouse, COUNT(DISTINCT p.product_id) as total_products,
                   SUM(i.quantity) as total_quantity,
                   SUM(CASE WHEN i.quantity <= i.reorder_level THEN 1 ELSE 0 END) as low_stock_items
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            WHERE p.category = COALESCE(?, p.category)
            GROUP BY i.warehouse
            ORDER BY total_quantity DESC
            """
            params = [category]
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
        
        cursor.execute(sql, params)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        result = {
            "data": [dict(zip(columns, row)) for row in rows],
            "analysis_type": analysis_type,
            "total_records": len(rows),
            "parameters": {
                "category": category,
                "warehouse": warehouse,
                "low_stock_threshold": low_stock_threshold
            }
        }
        
        conn.close()
        return result
        
    except Exception as e:
        return {"error": f"Inventory data query failed: {str(e)}"}

@tool
def query_custom_reports(
    report_name: str,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    执行自定义报表查询
    
    Args:
        report_name: 预定义报表名称
        parameters: 报表参数
    
    Returns:
        查询结果字典
    """
    try:
        conn = get_db_connection("sales")
        cursor = conn.cursor()
        
        # 预定义的复杂报表查询
        predefined_reports = {
            "sales_performance": {
                "sql": """
                SELECT 
                    strftime('%Y-%m', o.order_date) as month,
                    SUM(o.total_amount) as total_sales,
                    COUNT(o.order_id) as order_count,
                    AVG(o.total_amount) as avg_order_value,
                    COUNT(DISTINCT o.customer_id) as unique_customers
                FROM sales_orders o
                WHERE o.order_date BETWEEN ? AND ?
                GROUP BY strftime('%Y-%m', o.order_date)
                ORDER BY month DESC
                """,
                "params": lambda p: [p.get("start_date", "2024-01-01"), p.get("end_date", "2024-12-31")]
            },
            "customer_segmentation": {
                "sql": """
                SELECT 
                    c.customer_id,
                    c.name,
                    c.email,
                    COUNT(o.order_id) as total_orders,
                    SUM(o.total_amount) as total_spent,
                    AVG(o.total_amount) as avg_order_value,
                    MAX(o.order_date) as last_order_date
                FROM customers c
                LEFT JOIN sales_orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_id, c.name, c.email
                HAVING total_orders > 0
                ORDER BY total_spent DESC
                LIMIT ?
                """,
                "params": lambda p: [p.get("limit", 100)]
            },
            "product_performance": {
                "sql": """
                SELECT 
                    p.product_id,
                    p.product_name,
                    p.category,
                    p.price,
                    SUM(oi.quantity) as total_sold,
                    SUM(oi.quantity * p.price) as total_revenue,
                    COUNT(DISTINCT oi.order_id) as orders_count
                FROM products p
                JOIN order_items oi ON p.product_id = oi.product_id
                JOIN sales_orders o ON oi.order_id = o.order_id
                WHERE o.order_date BETWEEN ? AND ?
                GROUP BY p.product_id, p.product_name, p.category, p.price
                ORDER BY total_revenue DESC
                LIMIT ?
                """,
                "params": lambda p: [p.get("start_date", "2024-01-01"), p.get("end_date", "2024-12-31"), p.get("limit", 50)]
            }
        }
        
        if report_name not in predefined_reports:
            raise ValueError(f"Unknown report: {report_name}")
        
        report = predefined_reports[report_name]
        params = report["params"](parameters or {})
        
        cursor.execute(report["sql"], params)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        result = {
            "data": [dict(zip(columns, row)) for row in rows],
            "report_name": report_name,
            "total_records": len(rows),
            "parameters": parameters or {}
        }
        
        conn.close()
        return result
        
    except Exception as e:
        return {"error": f"Custom report query failed: {str(e)}"}

# 创建 Reporting Agent
reporting_agent = create_deep_agent(
    model=model,
    tools=[
        query_sales_data,
        query_user_analytics,
        query_financial_reports,
        query_inventory_data,
        query_custom_reports
    ],
    system_prompt="""你是一个专业的数据报表分析师。你的任务是帮助用户查询和分析各种业务数据。

## 可用的工具

1. **query_sales_data** - 查询销售数据
   - 支持多种查询类型：daily_sales, monthly_sales, regional_sales, product_sales, top_products
   - 可以按日期、地区、产品类别进行筛选

2. **query_user_analytics** - 查询用户分析数据
   - 支持多种指标：active_users, user_retention, session_duration, conversion_rate
   - 可以按时间周期、用户群体、平台进行筛选

3. **query_financial_reports** - 查询财务报表
   - 支持多种报表类型：revenue, expenses, profit_loss, cash_flow
   - 可以按周期、年份、部门进行筛选

4. **query_inventory_data** - 查询库存数据
   - 支持多种分析类型：stock_levels, movement_history, low_stock, warehouse_summary
   - 可以按类别、仓库、库存阈值进行筛选

5. **query_custom_reports** - 执行自定义报表
   - 支持预定义的复杂报表：sales_performance, customer_segmentation, product_performance

## 工作流程

1. **理解用户需求**：仔细分析用户的问题，确定需要查询的数据类型
2. **选择合适的工具**：根据问题类型选择最合适的查询工具
3. **构建查询参数**：根据用户需求构建合适的查询参数
4. **执行查询**：调用选定的工具执行查询
5. **分析结果**：对查询结果进行解释和分析
6. **提供建议**：基于数据提供有价值的业务洞察和建议

## 注意事项

- 确保使用正确的日期格式 (YYYY-MM-DD)
- 根据用户的具体需求调整查询参数
- 对于复杂问题，可能需要多次查询来获取完整信息
- 始终提供清晰的解释和有价值的业务洞察
""",
    memory=["./AGENTS.md"],
    backend=None  # 使用默认后端
)

if __name__ == "__main__":
    # 测试示例
    result = reporting_agent.invoke({
        "messages": [
            "请帮我查询最近30天的每日销售数据，并分析销售趋势"
        ]
    })
    
    for msg in result.get("messages", []):
        if hasattr(msg, "content") and msg.content:
            print(msg.content)