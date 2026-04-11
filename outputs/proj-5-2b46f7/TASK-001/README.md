# Personal Blog Backend

个人博客系统后端 - FastAPI 实现

## 任务信息
- **任务码**: TASK-001
- **任务名称**: 后端 - 项目初始化与依赖配置

## 项目结构

```
backend/
├── main.py           # FastAPI 应用入口
├── database.py       # 数据库配置
├── models.py         # SQLAlchemy 数据模型
├── schemas.py        # Pydantic 数据验证模式
├── config.py         # 应用配置
├── requirements.txt  # Python 依赖包
├── .env.example      # 环境变量示例
└── README.md         # 项目说明
```

## 依赖包

- **fastapi**: 现代、快速的 Web 框架
- **uvicorn**: ASGI 服务器
- **sqlalchemy**: ORM 数据库工具
- **bcrypt**: 密码哈希
- **python-multipart**: 表单数据解析
- **pydantic**: 数据验证
- **python-jose**: JWT 令牌处理
- **passlib**: 密码哈希库

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件修改配置
```

### 3. 运行开发服务器

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

或

```bash
python main.py
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | / | 根路径，返回欢迎信息 |
| GET | /health | 健康检查 |

## 开发说明

- 数据库使用 SQLite（开发环境）
- 支持 CORS，前端开发服务器地址已配置
- API 文档自动生成
