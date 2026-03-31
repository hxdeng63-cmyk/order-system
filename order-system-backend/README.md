# 点单系统后端 API

基于 FastAPI 构建的订单管理系统后端服务。

## 技术栈

- **框架**: FastAPI + Uvicorn
- **数据库**: SQLite (aiosqlite)
- **认证**: JWT (python-jose)
- **图片存储**: 本地静态文件

## 项目结构

```
order-system-backend/
├── main.py              # 应用入口
├── database.py          # 数据库初始化
├── models.py             # 数据模型
├── requirements.txt      # Python依赖
├── Dockerfile            # Docker镜像构建文件
├── docker-compose.yml    # Docker Compose配置
├── routers/              # API路由模块
│   ├── auth.py          # 认证相关
│   ├── user.py          # 用户相关
│   ├── product.py       # 商品相关
│   ├── cart.py          # 购物车相关
│   ├── order.py         # 订单相关
│   ├── merchant.py       # 商家相关
│   └── upload.py        # 文件上传
├── services/             # 业务服务
│   └── oss.py           # 对象存储服务
├── utils/               # 工具函数
│   └── security.py      # 安全相关
├── static/              # 静态文件
│   └── uploads/         # 上传文件目录
└── order_system.db      # SQLite数据库文件
```

## 快速开始

### 1. 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

服务将在 http://localhost:8088 启动

### 2. Docker 运行

```bash
# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 访问API文档

启动后访问自动生成的 Swagger 文档：http://localhost:8088/docs

## API 接口

### 认证接口 `/api/auth`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /register | 用户注册 |
| POST | /login | 用户登录 |
| POST | /merchant/login | 商家登录 |
| POST | /logout | 退出登录 |

### 用户接口 `/api/user`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /profile | 获取用户信息 |
| PUT | /profile | 更新用户信息 |

### 商品接口 `/api`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /categories | 获取分类列表 |
| GET | /products | 获取商品列表 |
| GET | /products/{id} | 获取商品详情 |

### 购物车接口 `/api/cart`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | | 获取购物车列表 |
| POST | | 添加商品到购物车 |
| PUT | /{id} | 更新购物车商品数量 |
| DELETE | /{id} | 删除购物车商品 |
| DELETE | | 清空购物车 |

### 订单接口 `/api/orders`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | | 创建订单 |
| GET | | 获取订单列表 |
| GET | /{id} | 获取订单详情 |
| PUT | /{id}/pay | 支付订单 |
| PUT | /{id}/cancel | 取消订单 |
| PUT | /{id}/complete | 确认收货 |
| DELETE | /{id} | 删除订单 |

### 商家接口 `/api/merchant`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /today-stats | 今日统计数据 |
| GET | /orders | 获取商家订单列表 |
| PUT | /orders/{id}/accept | 接单 |
| PUT | /orders/{id}/reject | 拒单 |
| PUT | /orders/{id}/complete | 完成订单 |
| DELETE | /orders/{id} | 删除订单 |
| GET | /products | 获取商家商品列表 |
| POST | /products | 添加商品 |
| PUT | /products/{id} | 更新商品 |
| DELETE | /products/{id} | 删除商品 |

### 文件上传
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload | 上传图片 |

## 订单状态

| 状态 | 说明 | 可执行操作 |
|------|------|-----------|
| pending | 待支付 | 取消、支付 |
| paid | 已支付/待接单 | 商家接单/拒单 |
| processing | 制作中 | 商家完成 |
| completed | 已完成 | 删除 |
| cancelled | 已取消 | 删除 |

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| PORT | 服务端口 | 8088 |
| PYTHONDONTWRITEBYTECODE | 禁止生成pyc | 1 |

## 健康检查

```bash
curl http://localhost:8088/health
```

## 数据库

使用 SQLite 数据库，文件位于 `order_system.db`。数据库表在首次启动时自动创建。

主要表结构：
- `users` - 用户表
- `merchants` - 商家表
- `categories` - 商品分类表
- `products` - 商品表
- `orders` - 订单表
- `order_items` - 订单项表
- `cart_items` - 购物车表
- `addresses` - 收货地址表
- `notifications` - 通知表
