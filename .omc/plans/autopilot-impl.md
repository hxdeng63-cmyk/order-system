# 避雷功能实现计划

## 目标
用户可将商品加入"避雷"列表（黑名单），与收藏功能完全对称。

## 数据模型

### 新建数据库表 `dislikes`
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY | |
| user_id | INTEGER | 用户ID |
| product_id | INTEGER | 商品ID |
| created_at | DATETIME | 添加时间 |

唯一约束: `(user_id, product_id)`

## 后端实现

### 任务 1: 数据库表
- **文件**: `order-system-backend/database.py`
- **操作**: 添加 `dislikes` 表创建语句和索引

### 任务 2: API 路由
- **文件**: `order-system-backend/routers/dislike.py` (新建)
- **接口**:
  - `POST /api/products/{product_id}/dislike` — toggle 避雷（已存在则删除，不存在则添加）
  - `GET /api/user/dislikes` — 获取避雷列表（JOIN products 返回完整商品信息）

### 任务 3: 模型定义
- **文件**: `order-system-backend/models.py`
- **新增**: `DislikeProductResponse` 响应模型

### 任务 4: 路由注册
- **文件**: `order-system-backend/main.py`
- **操作**: 注册 `/api` 路由包含 dislike 路由

## 前端实现

### 任务 5: API 路径
- **文件**: `order-system-uniapp/src/api/index.js`
- **新增**: `userDislikes: \`${API_BASE}/user/dislikes\``

### 任务 6: Store 方法
- **文件**: `order-system-uniapp/src/store/index.js`
- **新增**:
  - `state.dislikes[]`
  - `loadDislikes()` — 加载避雷列表
  - `isDisliked(productId)` — 检查是否已避雷
  - `toggleDislike(product)` — toggle 避雷

### 任务 7: 避雷列表页
- **文件**: `order-system-uniapp/src/pages/dislike/index.vue` (新建)
- **功能**: 空状态 + 网格卡片 + 删除功能，与 favorite 页完全对称

### 任务 8: 商品详情页
- **文件**: `order-system-uniapp/src/pages/product-detail/index.vue`
- **操作**: 在收藏按钮旁新增"🚫 避雷"按钮，点击调用 toggleDislike

### 任务 9: 商品列表过滤
- **文件**: `order-system-uniapp/src/pages/index/index.vue`
- **文件**: `order-system-uniapp/src/pages/category/index.vue`
- **操作**: 加载商品时过滤掉已避雷商品

### 任务 10: 路由注册
- **文件**: `order-system-uniapp/src/pages.json`
- **新增**: `pages/dislike/index`

## 依赖关系
任务 1 → 任务 2 → 任务 3 → 任务 4（后端顺序）
任务 5 → 任务 6 → 任务 7（前端 API/Store/页面）
任务 6 → 任务 8（详情页依赖 store）
任务 6 → 任务 9（列表页依赖 store）
任务 7 → 任务 10（路由最后注册）

## 验收标准
- [ ] POST `/api/products/{id}/dislike` toggle 正常工作
- [ ] GET `/api/user/dislikes` 返回完整商品信息
- [ ] 商品详情页可添加/移除避雷
- [ ] 避雷列表页正常显示/删除
- [ ] 首页和分类页不显示已避雷商品
- [ ] 避雷状态在刷新后保持
