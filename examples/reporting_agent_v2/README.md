# Reporting Agent

基于 `create_deep_agent` 框架开发的智能数据报表分析 Agent，能够根据用户问题自动选择合适的 SQL 工具来获取和分析业务数据。

## 功能特性

### 🎯 智能工具选择
- 根据用户问题自动选择最合适的查询工具
- 支持多种数据源和数据库类型
- 智能参数构建和查询优化

### 📊 多维度数据查询
- **销售数据查询**：日常销售、月度销售、区域分析、产品分析
- **用户分析**：活跃用户、留存率、会话时长、转化率
- **财务报表**：收入、支出、损益、现金流
- **库存管理**：库存水平、变动历史、低库存预警、仓库汇总
- **自定义报表**：预定义的复杂业务报表

### 🔧 技术架构
- 基于 `deepagents` 框架构建
- 使用 SQLite 作为数据存储
- 集成 LangChain 工具系统
- 支持多数据库连接管理

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 或者安装项目依赖
pip install deepagents langchain-openai python-dotenv pandas sqlite3
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
LLM_MODEL_ID=gpt-4
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.openai.com/v1
```

### 3. 初始化数据

```bash
cd examples/reporting_agent
python data/setup_sample_data.py
```

### 4. 运行 Agent

```bash
python agent.py
```

## 使用示例

### 销售数据分析

```python
# 查询最近30天的每日销售数据
result = reporting_agent.invoke({
    "messages": [
        "请帮我查询最近30天的每日销售数据，并分析销售趋势"
    ]
})

# 查询各地区的销售情况
result = reporting_agent.invoke({
    "messages": [
        "分析一下华东、华南、华北三个地区的销售业绩对比"
    ]
})
```

### 用户行为分析

```python
# 查询用户活跃度
result = reporting_agent.invoke({
    "messages": [
        "统计最近7天的日活跃用户数量"
    ]
})

# 分析用户留存率
result = reporting_agent.invoke({
    "messages": [
        "计算最近30天用户的留存率情况"
    ]
})
```

### 财务报表查询

```python
# 生成月度收入报表
result = reporting_agent.invoke({
    "messages": [
        "生成2024年上半年的月度收入报表"
    ]
})

# 分析各部门支出情况
result = reporting_agent.invoke({
    "messages": [
        "分析技术部和市场部上半年的支出对比"
    ]
})
```

### 库存管理

```python
# 查询低库存商品
result = reporting_agent.invoke({
    "messages": [
        "列出所有库存低于安全阈值的商品"
    ]
})

# 仓库库存汇总
result = reporting_agent.invoke({
    "messages": [
        "汇总各个仓库的库存情况"
    ]
})
```

### 自定义报表

```python
# 客户分群分析
result = reporting_agent.invoke({
    "messages": [
        "分析客户的购买行为，进行客户分群"
    ]
})

# 产品性能分析
result = reporting_agent.invoke({
    "messages": [
        "分析各产品的销售表现，找出最受欢迎的产品"
    ]
})
```

## 工具详解

### query_sales_data

销售数据查询工具，支持多种查询类型：

- `daily_sales`: 每日销售数据
- `monthly_sales`: 月度销售数据  
- `regional_sales`: 区域销售分析
- `product_sales`: 产品销售分析
- `top_products`: 热销产品排行

**参数：**
- `query_type`: 查询类型
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)
- `region`: 地区筛选
- `product_category`: 产品类别筛选
- `limit`: 返回记录数限制

### query_user_analytics

用户分析工具，支持多种指标：

- `active_users`: 活跃用户统计
- `user_retention`: 用户留存率
- `session_duration`: 会话时长分析
- `conversion_rate`: 转化率分析

**参数：**
- `metric`: 指标类型
- `time_period`: 时间周期 (7d, 30d, 90d, 1y)
- `user_segment`: 用户群体筛选
- `platform`: 平台筛选

### query_financial_reports

财务报表工具，支持多种报表类型：

- `revenue`: 收入报表
- `expenses`: 支出报表
- `profit_loss`: 损益表
- `cash_flow`: 现金流表

**参数：**
- `report_type`: 报表类型
- `period`: 报表周期 (daily, weekly, monthly, quarterly, yearly)
- `fiscal_year`: 财务年份
- `department`: 部门筛选

### query_inventory_data

库存管理工具，支持多种分析：

- `stock_levels`: 库存水平查询
- `movement_history`: 库存变动历史
- `low_stock`: 低库存预警
- `warehouse_summary`: 仓库库存汇总

**参数：**
- `analysis_type`: 分析类型
- `category`: 产品类别筛选
- `warehouse`: 仓库筛选
- `low_stock_threshold`: 低库存阈值

### query_custom_reports

自定义报表工具，支持预定义的复杂报表：

- `sales_performance`: 销售业绩分析
- `customer_segmentation`: 客户分群分析
- `product_performance`: 产品性能分析

**参数：**
- `report_name`: 报表名称
- `parameters`: 报表参数字典

## 数据库结构

### 销售数据库 (sales.db)
- `products`: 产品信息
- `sales_orders`: 销售订单
- `order_items`: 订单明细

### 用户分析数据库 (analytics.db)
- `user_activities`: 用户活动记录
- `user_sessions`: 用户会话数据
- `user_retention`: 用户留存数据
- `marketing_leads`: 营销线索

### 财务数据库 (financial.db)
- `financial_transactions`: 财务交易记录

### 库存数据库 (inventory.db)
- `inventory`: 库存信息
- `inventory_movements`: 库存变动记录

## 扩展开发

### 添加新的数据源

1. 在 `DB_CONFIGS` 中添加新的数据库配置
2. 创建对应的数据库连接函数
3. 实现新的查询工具函数
4. 在 Agent 中注册新工具

### 添加新的查询类型

1. 在相应的工具函数中添加新的查询类型
2. 实现对应的 SQL 查询逻辑
3. 更新工具的参数定义
4. 在系统提示中更新工具说明

### 自定义报表

1. 在 `query_custom_reports` 中添加新的报表定义
2. 实现复杂的 SQL 查询逻辑
3. 定义报表参数和返回格式
4. 更新系统提示中的报表说明

## 最佳实践

### 1. 查询优化
- 为常用查询字段添加索引
- 使用合适的查询参数限制返回数据量
- 避免复杂的 JOIN 查询影响性能

### 2. 错误处理
- 实现完善的异常处理机制
- 提供清晰的错误信息
- 支持查询失败的重试机制

### 3. 数据安全
- 实施数据访问权限控制
- 避免 SQL 注入风险
- 敏感数据脱敏处理

### 4. 用户体验
- 提供清晰的查询结果解释
- 支持多种数据格式输出
- 实现智能的参数建议

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库文件是否存在
   - 确认数据库路径配置正确
   - 检查文件权限

2. **查询结果为空**
   - 检查查询参数是否正确
   - 确认数据是否存在
   - 验证 SQL 查询语法

3. **工具调用失败**
   - 检查工具参数格式
   - 确认工具名称拼写正确
   - 查看错误日志信息

### 调试方法

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **测试数据库连接**
   ```python
   conn = get_db_connection("sales")
   conn.close()
   ```

3. **验证 SQL 查询**
   ```python
   cursor.execute("SELECT * FROM products LIMIT 5")
   print(cursor.fetchall())
   ```

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目！

### 开发流程

1. Fork 项目
2. 创建功能分支
3. 提交代码变更
4. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 代码规范
- 添加适当的注释和文档
- 编写测试用例
- 更新相关文档

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至项目维护者
- 参与项目讨论