# 收藏功能详细规格

## 1. 需求概述

在现有点单系统中实现完整的用户收藏商品功能，允许用户收藏商品后在收藏列表中查看和管理。

## 2. 功能列表

### 2.1 后端 API

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取收藏列表 | GET | `/api/user/favorites` | 获取当前用户的所有收藏商品 |
| 切换收藏状态 | POST | `/api/products/{id}/favorite` | 收藏/取消收藏商品（已存在） |

### 2.2 前端页面

| 页面 | 路径 | 说明 |
|------|------|------|
| 收藏列表页 | `/pages/favorite/index.vue` | 展示用户收藏的商品列表 |

### 2.3 前端交互

| 位置 | 交互 | 说明 |
|------|------|------|
| 商品详情页 | 点击收藏图标 | 切换收藏状态 |
| 收藏列表页 | 点击商品卡片 | 跳转到商品详情页 |
| 收藏列表页 | 左滑商品卡片 | 显示取消收藏按钮 |
| 收藏列表页 | 点击取消收藏 | 从列表中移除 |

## 3. 数据模型

### 3.1 后端 Favorites 表

```sql
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE(user_id, product_id)
);
```

### 3.2 API 响应格式

#### GET /api/user/favorites

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "productId": 1,
      "name": "珍珠奶茶",
      "price": 18.0,
      "icon": "/static/cup.png",
      "tag": "热销",
      "addedAt": "2024-03-25 10:30:00"
    }
  ]
}
```

## 4. 页面设计

### 4.1 收藏列表页 (`/pages/favorite/index.vue`)

- 顶部返回按钮
- 空状态提示（无收藏时）
- 商品列表网格布局（2列）
- 每个商品卡片：图片、名称、价格、标签
- 点击卡片跳转商品详情

### 4.2 商品详情页收藏按钮

- 位置：商品图片右上角
- 图标：心形（空心=未收藏，实心=已收藏）
- 颜色：已收藏显示红色

## 5. 实现任务

### 后端
1. 在 `routers/user.py` 添加 `GET /api/user/favorites` 接口
2. 修改 `routers/product.py` 的 `POST /api/products/{id}/favorite` 返回完整商品信息

### 前端
1. 创建收藏列表页面 `src/pages/favorite/index.vue`
2. 在 `src/pages.json` 添加路由配置
3. 修改商品详情页，添加收藏功能 UI
4. 在 `src/api/index.js` 添加收藏列表 API 路径
5. 在 `src/store/index.js` 添加收藏列表加载函数
6. 在 `src/pages/profile/index.vue` 修改"我的收藏"跳转链接

## 6. 技术约束

- 前端：UniApp + Vue3
- 后端：FastAPI + aiosqlite
- 不使用 mock 数据，所有数据从 API 加载
