# 餐饮订单系统

基于 FastAPI + UniApp 构建的奶茶点单系统，支持用户端和商家端。

## 项目结构

```
order-system/
├── order-system-backend/     # 后端 API (FastAPI)
│   ├── main.py               # 应用入口
│   ├── database.py           # 数据库初始化
│   ├── models.py             # 数据模型
│   ├── requirements.txt      # Python 依赖
│   ├── Dockerfile            # Docker 构建文件
│   ├── docker-compose.yml    # Docker Compose 配置
│   ├── routers/              # API 路由模块
│   ├── services/             # 业务服务
│   ├── utils/                # 工具函数
│   └── static/uploads/       # 上传文件目录
│
└── order-system-uniapp/      # 前端 (UniApp)
    ├── src/
    │   ├── api/              # API 接口配置
    │   ├── pages/             # 页面
    │   ├── store/             # 状态管理
    │   ├── App.vue            # 应用入口
    │   └── main.js            # Vue 入口
    ├── static/                # 静态资源
    └── package.json
```

## 技术栈

| 端 | 技术 |
|----|------|
| 后端 | FastAPI + Uvicorn + SQLite (aiosqlite) |
| 前端 | UniApp + Vue 3 + Vite |
| 认证 | JWT (python-jose) |
| 部署 | Docker + Nginx |

## 功能

### 用户端
- 首页 - Banner、分类入口、热门商品
- 分类页 - 左右分栏导航
- 购物车 - 商品增删、数量调整、结算、备注
- 订单页 - 状态筛选、订单列表
- 个人中心 - 功能菜单
- 商品详情 - 规格选择、加入购物车
- 优惠券 - 用户查看/删除已使用优惠券
- 熊币 - 余额查询

### 商家端
- 今日统计 - 订单量、营业额
- 订单管理 - 接单/拒单/完成
- 商品管理 - 添加/编辑/删除
- 优惠券管理 - 创建/发放
- 熊币管理 - 充值/查询

## 快速开始

### 后端

```bash
cd order-system-backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

服务将在 http://localhost:8088 启动

### 前端

```bash
cd order-system-uniapp

# 安装依赖
npm install

# H5 开发
npm run dev:h5

# 微信小程序开发
npm run dev:mp-weixin
```

### Docker 部署

```bash
cd order-system-backend

# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## API 接口

### 认证 `/api/auth`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /register | 用户注册 |
| POST | /login | 用户登录 |
| POST | /merchant/login | 商家登录 |
| POST | /logout | 退出登录 |

### 用户 `/api/user`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /profile | 获取用户信息 |
| PUT | /profile | 更新用户信息 |

### 商品 `/api`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /categories | 获取分类列表 |
| GET | /products | 获取商品列表 |
| GET | /products/{id} | 获取商品详情 |

### 购物车 `/api/cart`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | | 获取购物车列表 |
| POST | | 添加商品到购物车 |
| PUT | /{id} | 更新购物车商品数量 |
| DELETE | /{id} | 删除购物车商品 |
| DELETE | | 清空购物车 |

### 订单 `/api/orders`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | | 创建订单 |
| GET | | 获取订单列表 |
| GET | /{id} | 获取订单详情 |
| PUT | /{id}/pay | 支付订单 |
| PUT | /{id}/cancel | 取消订单 |
| PUT | /{id}/complete | 确认收货 |
| DELETE | /{id} | 删除订单 |

### 商家 `/api/merchant`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /today-stats | 今日统计数据 |
| GET | /orders | 获取商家订单列表 |
| PUT | /orders/{id}/accept | 接单 |
| PUT | /orders/{id}/reject | 拒单 |
| PUT | /orders/{id}/complete | 完成订单 |
| GET | /products | 获取商家商品列表 |
| POST | /products | 添加商品 |
| PUT | /products/{id} | 更新商品 |
| DELETE | /products/{id} | 删除商品 |

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

## 健康检查

```bash
curl http://localhost:8088/health
```

## API 文档

启动后访问 Swagger 文档：http://localhost:8088/docs

## 许可证

MIT
