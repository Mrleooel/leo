# 社区医疗健康平台

基于Python全栈开发的社区医疗健康管理系统，采用Flask + SQLAlchemy + Bootstrap 5 + HTMX技术栈。

## 功能特性

### 核心功能
- **患者管理**: 患者信息录入、查询、编辑
- **医生管理**: 医生信息管理、排班状态
- **预约管理**: 预约创建、状态跟踪
- **药品管理**: 药品库存、分类管理
- **数据看板**: 可视化图表展示
- **报表生成**: Excel报表导出

### 技术特性
- **响应式设计**: Bootstrap 5现代化UI
- **动态交互**: HTMX无刷新操作
- **数据可视化**: Plotly图表展示
- **系统设计图**: Diagrams库生成架构图
- **用户认证**: Flask-Login安全登录

## 技术栈

- **后端**: Flask + SQLAlchemy + SQLite
- **前端**: Bootstrap 5 + HTMX + Plotly.js
- **数据库**: SQL Server
- **图表**: Plotly + Diagrams
- **报表**: Pandas + OpenPyXL



## 项目结构

```
Project/
├── app.py                 # 主应用文件
├── config.py             # 配置文件
├── models.py             # 数据库模型
├── routes.py             # 路由定义
├── init_data.py          # 初始化数据
├── requirements.txt      # 依赖包
├── README.md            # 项目说明
├── utils/               # 工具模块
│   ├── diagrams.py      # 图表生成
│   └── reporting.py     # 报表生成
├── templates/           # HTML模板
│   ├── base.html       # 基础模板
│   ├── login.html      # 登录页面
│   ├── dashboard.html  # 数据看板
│   ├── patients.html   # 患者管理
│   ├── doctors.html    # 医生管理
│   ├── appointments.html # 预约管理
│   ├── medicines.html  # 药品管理
│   └── errors/         # 错误页面
├── static/             # 静态文件
└── reports/           # 报表文件
```

## 数据库设计

### 核心表结构
1. **患者表(Patient)**: 患者基本信息
2. **医生表(Doctor)**: 医生信息和排班
3. **预约表(Appointment)**: 预约记录
4. **药品表(Medicine)**: 药品库存信息
5. **处方表(Prescription)**: 处方开具记录
6. **用户表(User)**: 系统用户认证

### 关系设计
- 患者 ↔ 预约 (一对多)
- 医生 ↔ 预约 (一对多)
- 预约 ↔ 处方 (一对多)
- 药品 ↔ 处方 (一对多)

## API接口

### 查询接口
- `GET /search/appointments` - 患者预约查询
- `GET /search/doctors` - 医生接诊查询
- `GET /search/medicines` - 药品库存查询

### 报表接口
- `GET /report/medicines` - 药品销售报表
- `GET /report/appointments` - 预约报表
- `GET /report/patients` - 患者报表

### 可视化接口
- `GET /dashboard/department_distribution` - 科室分布图
- `GET /dashboard/medicine_top10` - 药品销量TOP10

## 功能演示

### 1. 数据看板
- 统计卡片显示关键指标
- 科室分布饼图
- 药品销量柱状图
- 快速查询功能

### 2. 患者管理
- 患者列表展示
- 添加/编辑患者信息
- 患者信息查询

### 3. 医生管理
- 医生列表和状态
- 添加/编辑医生信息
- 排班管理
- 科室分类

### 4. 预约管理
- 预约创建和跟踪
- 状态管理
- 时间安排

### 5. 药品管理
- 药品库存管理
- 添加/编辑药品信息
- 分类展示
- 价格和库存监控

## 系统特色

### 现代化UI设计
- Bootstrap 5响应式布局
- 渐变色彩搭配
- 图标化操作界面

### 动态交互体验
- HTMX无刷新操作
- 实时数据更新
- 流畅的用户体验

### 数据可视化
- Plotly交互式图表
- 实时数据展示
- 多维度分析

### 系统设计图
- ER关系图
- 流程活动图
- 系统架构图

## 部署说明

### 开发环境
```bash
# 使用SQLite数据库
export DATABASE_URL=sqlite:///medical_platform.db
python app.py
```

### 生产环境
```bash
# 配置SQL Server
export DATABASE_URL=mssql+pyodbc://user:pass@server/database
export SECRET_KEY=your-secret-key
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

