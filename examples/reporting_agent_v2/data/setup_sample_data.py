"""
创建示例数据库和测试数据
运行此脚本来设置示例数据，用于测试 Reporting Agent
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

def create_sample_databases():
    """创建示例数据库和表结构"""
    
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    
    # 1. 创建销售数据库
    sales_conn = sqlite3.connect("data/sales.db")
    sales_cursor = sales_conn.cursor()
    
    # 创建产品表
    sales_cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price DECIMAL(10,2) NOT NULL
    )
    """)
    
    # 创建销售订单表
    sales_cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date DATE NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        status TEXT NOT NULL,
        region TEXT NOT NULL
    )
    """)
    
    # 创建订单项表
    sales_cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        item_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES sales_orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)
    
    # 插入示例产品数据
    products = [
        (1, "iPhone 15", "电子产品", 5999.00),
        (2, "MacBook Pro", "电子产品", 12999.00),
        (3, "iPad Air", "电子产品", 4399.00),
        (4, "AirPods Pro", "电子产品", 1999.00),
        (5, "Nike Air Max", "服装鞋帽", 899.00),
        (6, "Adidas运动鞋", "服装鞋帽", 699.00),
        (7, "Levi's牛仔裤", "服装鞋帽", 499.00),
        (8, "咖啡机", "家电", 1299.00),
        (9, "空气净化器", "家电", 2199.00),
        (10, "智能手表", "电子产品", 2499.00),
    ]
    
    sales_cursor.executemany("INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)", products)
    
    # 生成销售订单数据
    orders = []
    order_items = []
    
    start_date = datetime(2024, 1, 1)
    regions = ["华东", "华南", "华北", "华中", "西南", "西北", "东北"]
    
    for i in range(500):  # 生成500个订单
        order_date = start_date + timedelta(days=random.randint(0, 365))
        customer_id = random.randint(1, 1000)
        region = random.choice(regions)
        total_amount = 0
        
        # 每个订单包含1-5个商品
        num_items = random.randint(1, 5)
        for j in range(num_items):
            product_id = random.randint(1, 10)
            quantity = random.randint(1, 3)
            
            # 获取商品价格
            sales_cursor.execute("SELECT price FROM products WHERE product_id = ?", (product_id,))
            price = sales_cursor.fetchone()[0]
            
            item_total = price * quantity
            total_amount += item_total
            
            order_items.append((i+1, product_id, quantity, price))
        
        orders.append((i+1, customer_id, order_date.strftime("%Y-%m-%d"), 
                      round(total_amount, 2), "completed", region))
    
    sales_cursor.executemany("INSERT INTO sales_orders VALUES (?, ?, ?, ?, ?, ?)", orders)
    sales_cursor.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", order_items)
    
    sales_conn.commit()
    sales_conn.close()
    
    # 2. 创建用户分析数据库
    analytics_conn = sqlite3.connect("data/analytics.db")
    analytics_cursor = analytics_conn.cursor()
    
    # 创建用户活动表
    analytics_cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_activities (
        activity_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        activity_date DATE NOT NULL,
        activity_type TEXT NOT NULL,
        platform TEXT NOT NULL,
        duration INTEGER
    )
    """)
    
    # 创建用户会话表
    analytics_cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        session_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        session_date DATE NOT NULL,
        platform TEXT NOT NULL,
        session_duration INTEGER,
        pages_viewed INTEGER
    )
    """)
    
    # 创建用户留存表
    analytics_cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_retention (
        retention_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        cohort_week DATE NOT NULL,
        week_number INTEGER NOT NULL,
        retained INTEGER,
        user_segment TEXT
    )
    """)
    
    # 创建营销线索表
    analytics_cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketing_leads (
        lead_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        created_at DATE NOT NULL,
        status TEXT NOT NULL,
        source TEXT,
        user_segment TEXT
    )
    """)
    
    # 生成用户活动数据
    activities = []
    sessions = []
    retention_data = []
    leads = []
    
    for i in range(1000):  # 1000个用户
        user_id = i + 1
        
        # 生成用户活动
        for day in range(30):  # 最近30天
            activity_date = datetime.now() - timedelta(days=day)
            activity_type = random.choice(["login", "page_view", "purchase", "search"])
            platform = random.choice(["web", "mobile", "app"])
            duration = random.randint(30, 300) if activity_type != "login" else 0
            
            activities.append((i+1, activity_date.strftime("%Y-%m-%d"), 
                            activity_type, platform, duration))
        
        # 生成用户会话
        for day in range(30):
            session_date = datetime.now() - timedelta(days=day)
            if random.random() < 0.3:  # 30%的概率有会话
                platform = random.choice(["web", "mobile", "app"])
                duration = random.randint(60, 600)
                pages_viewed = random.randint(1, 20)
                
                sessions.append((i+1, session_date.strftime("%Y-%m-%d"), 
                              platform, duration, pages_viewed))
        
        # 生成留存数据
        cohort_week = datetime.now() - timedelta(weeks=random.randint(1, 12))
        week_number = random.randint(1, 12)
        retained = random.choice([0, 1])
        user_segment = random.choice(["new", "returning", "vip"])
        
        retention_data.append((i+1, cohort_week.strftime("%Y-%m-%d"), 
                            week_number, retained, user_segment))
        
        # 生成营销线索
        if random.random() < 0.1:  # 10%的概率成为线索
            created_at = datetime.now() - timedelta(days=random.randint(1, 90))
            status = random.choice(["new", "contacted", "converted", "lost"])
            source = random.choice(["organic", "paid", "referral", "social"])
            user_segment = random.choice(["new", "returning", "vip"])
            
            leads.append((i+1, created_at.strftime("%Y-%m-%d"), 
                         status, source, user_segment))
    
    analytics_cursor.executemany("INSERT INTO user_activities VALUES (?, ?, ?, ?, ?, ?)", activities)
    analytics_cursor.executemany("INSERT INTO user_sessions VALUES (?, ?, ?, ?, ?, ?)", sessions)
    analytics_cursor.executemany("INSERT INTO user_retention VALUES (?, ?, ?, ?, ?, ?)", retention_data)
    analytics_cursor.executemany("INSERT INTO marketing_leads VALUES (?, ?, ?, ?, ?, ?)", leads)
    
    analytics_conn.commit()
    analytics_conn.close()
    
    # 3. 创建财务数据库
    financial_conn = sqlite3.connect("data/financial.db")
    financial_cursor = financial_conn.cursor()
    
    # 创建财务交易表
    financial_cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_transactions (
        transaction_id INTEGER PRIMARY KEY,
        transaction_date DATE NOT NULL,
        transaction_type TEXT NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        category TEXT,
        department TEXT,
        description TEXT
    )
    """)
    
    # 生成财务交易数据
    transactions = []
    departments = ["销售部", "市场部", "技术部", "人事部", "财务部"]
    revenue_categories = ["产品销售", "服务收入", "订阅收入"]
    expense_categories = ["人员成本", "办公费用", "市场推广", "设备采购", "差旅费用"]
    
    for i in range(1000):  # 1000笔交易
        transaction_date = datetime.now() - timedelta(days=random.randint(0, 365))
        transaction_type = random.choice(["revenue", "expense"])
        
        if transaction_type == "revenue":
            amount = random.randint(1000, 50000)
            category = random.choice(revenue_categories)
            department = random.choice(["销售部", "市场部"])
        else:
            amount = random.randint(500, 20000)
            category = random.choice(expense_categories)
            department = random.choice(departments)
        
        transactions.append((transaction_date.strftime("%Y-%m-%d"), transaction_type,
                           amount, category, department, f"交易描述 {i+1}"))
    
    financial_cursor.executemany("INSERT INTO financial_transactions VALUES (?, ?, ?, ?, ?, ?)", transactions)
    
    financial_conn.commit()
    financial_conn.close()
    
    # 4. 创建库存数据库
    inventory_conn = sqlite3.connect("data/inventory.db")
    inventory_cursor = inventory_conn.cursor()
    
    # 创建库存表
    inventory_cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        inventory_id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        warehouse TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        reorder_level INTEGER NOT NULL,
        last_updated DATE NOT NULL
    )
    """)
    
    # 创建库存变动表
    inventory_cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_movements (
        movement_id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        transaction_date DATE NOT NULL,
        transaction_type TEXT NOT NULL,
        quantity_change INTEGER NOT NULL,
        warehouse TEXT NOT NULL,
        notes TEXT
    )
    """)
    
    # 生成库存数据
    inventory = []
    movements = []
    warehouses = ["北京仓", "上海仓", "广州仓", "深圳仓"]
    
    for product_id in range(1, 11):  # 10个产品
        for warehouse in warehouses:
            quantity = random.randint(10, 500)
            reorder_level = random.randint(20, 100)
            last_updated = datetime.now() - timedelta(days=random.randint(0, 30))
            
            inventory.append((product_id, warehouse, quantity, reorder_level, 
                           last_updated.strftime("%Y-%m-%d")))
            
            # 生成库存变动记录
            for i in range(random.randint(5, 20)):
                movement_date = datetime.now() - timedelta(days=random.randint(0, 90))
                transaction_type = random.choice(["in", "out"])
                quantity_change = random.randint(1, 50)
                notes = f"库存变动记录 {i+1}"
                
                movements.append((product_id, movement_date.strftime("%Y-%m-%d"), 
                                transaction_type, quantity_change, warehouse, notes))
    
    inventory_cursor.executemany("INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)", inventory)
    inventory_cursor.executemany("INSERT INTO inventory_movements VALUES (?, ?, ?, ?, ?, ?)", movements)
    
    inventory_conn.commit()
    inventory_conn.close()
    
    print("示例数据库创建完成！")
    print("数据库文件位置：")
    print("- data/sales.db (销售数据)")
    print("- data/analytics.db (用户分析数据)")
    print("- data/financial.db (财务数据)")
    print("- data/inventory.db (库存数据)")

if __name__ == "__main__":
    create_sample_databases()