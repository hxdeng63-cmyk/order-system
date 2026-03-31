# 点单系统 - UniApp

奶茶点单系统的 UniApp 版本，支持 H5 和微信小程序。

## 项目结构

```
order-system-uniapp/
├── src/
│   ├── api/              # API 接口配置
│   │   └── index.js     # 请求封装
│   ├── pages/           # 页面
│   │   ├── index/       # 首页
│   │   ├── category/   # 分类页
│   │   ├── cart/       # 购物车
│   │   ├── order/      # 订单页
│   │   ├── profile/    # 个人中心
│   │   ├── product-detail/  # 商品详情
│   │   ├── coupon/     # 优惠券
│   │   └── merchant/   # 商家端
│   │       ├── index/  # 商家首页
│   │       ├── order/  # 订单管理
│   │       ├── product/# 商品管理
│   │       ├── coupon/ # 优惠券管理
│   │       ├── coin/   # 熊币管理
│   │       └── stats/  # 数据统计
│   ├── store/           # 状态管理
│   ├── App.vue          # 应用入口
│   ├── main.js          # Vue 入口
│   ├── pages.json       # 页面配置
│   ├── manifest.json    # 应用配置
│   └── uni.scss         # 全局样式
├── static/              # 静态资源
├── package.json
└── vite.config.js
```

## 运行项目

```bash
# 安装依赖
npm install

# H5 开发
npm run dev:h5

# 微信小程序开发
npm run dev:mp-weixin
```

## API 接口

| 模块 | 接口 | 方法 |
|------|------|------|
| **商品** | `/api/categories` | GET |
| | `/api/products` | GET |
| | `/api/products/:id` | GET |
| **购物车** | `/api/cart` | GET |
| | `/api/cart/items` | POST |
| | `/api/cart/items/:id` | PUT |
| | `/api/cart/clear` | POST |
| **订单** | `/api/orders` | POST/GET |
| | `/api/orders/:id` | GET |
| **优惠券** | `/api/coupons/available` | GET |
| | `/api/coupons/user_coupons/:id` | DELETE |
| **熊币** | `/api/coins/balance` | GET |
| **用户** | `/api/user/profile` | GET |
| | `/api/auth/logout` | POST |

## 功能

- [x] 首页 - Banner、分类入口、热门商品
- [x] 分类页 - 左右分栏导航
- [x] 购物车 - 商品增删、数量调整、结算、备注
- [x] 订单页 - 状态筛选、订单列表
- [x] 个人中心 - 功能菜单
- [x] 商品详情 - 规格选择、加入购物车
- [x] 优惠券 - 用户查看/删除已使用优惠券
- [x] 商家端 - 订单管理、商品管理、优惠券管理、熊币管理、统计

## 注意事项

1. TabBar 图标需要添加实际图片文件到 `static/tabs/` 目录
2. 微信小程序需要在微信公众平台配置合法域名
3. 当前使用真实 API，数据库为 SQLite
