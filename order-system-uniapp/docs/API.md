# 点单系统 API 接口文档

## 一、认证模块 `/api/auth`

### 1.1 发送验证码
```
POST /api/auth/send-code
```
**请求参数：**
```json
{
  "phone": "13812345678",
  "type": "register"  // register | login | reset
}
```
**响应：**
```json
{
  "code": 200,
  "message": "验证码已发送",
  "data": {
    "expiresIn": 300
  }
}
```

---

### 1.2 用户注册
```
POST /api/auth/register
```
**请求参数：**
```json
{
  "phone": "13812345678",
  "code": "123456",
  "password": "xxxxxx"
}
```
**响应：**
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "token": "eyJhbGc...",
    "refreshToken": "eyJhbGc...",
    "expiresIn": 604800,
    "user": {
      "id": 1,
      "name": "用户",
      "phone": "13812345678",
      "avatar": "https://xxx/avatar.jpg",
      "memberLevel": "silver"
    }
  }
}
```

---

### 1.3 用户登录
```
POST /api/auth/login
```
**请求参数：**
```json
{
  "phone": "13812345678",
  "password": "xxxxxx"
}
```
**响应：**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGc...",
    "refreshToken": "eyJhbGc...",
    "expiresIn": 604800,
    "user": {
      "id": 1,
      "name": "用户",
      "phone": "13812345678",
      "avatar": "https://xxx/avatar.jpg",
      "memberLevel": "silver"
    }
  }
}
```

---

### 1.4 微信一键登录
```
POST /api/auth/wechat-login
```
**请求参数：**
```json
{
  "code": "xxxxxxxx"
}
```
**响应：**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGc...",
    "isNewUser": false,
    "user": { ... }
  }
}
```

---

### 1.5 忘记密码
```
POST /api/auth/reset-password
```
**请求参数：**
```json
{
  "phone": "13812345678",
  "code": "123456",
  "newPassword": "xxxxxx"
}
```
**响应：**
```json
{
  "code": 200,
  "message": "密码重置成功"
}
```

---

### 1.6 刷新 Token
```
POST /api/auth/refresh-token
```
**请求参数：**
```json
{
  "refreshToken": "eyJhbGc..."
}
```
**响应：**
```json
{
  "code": 200,
  "data": {
    "token": "eyJhbGc...",
    "expiresIn": 604800
  }
}
```

---

### 1.7 退出登录
```
POST /api/auth/logout
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "message": "退出成功"
}
```

---

## 二、用户模块 `/api/user`

### 2.1 获取用户信息
```
GET /api/user/profile
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "用户",
    "phone": "13812345678",
    "avatar": "https://xxx/avatar.jpg",
    "memberLevel": "silver",
    "memberPoints": 1250,
    "createdAt": "2024-01-01T00:00:00Z"
  }
}
```

---

### 2.2 更新用户信息
```
PUT /api/user/profile
```
**请求头：**
```
Authorization: Bearer <token>
```
**请求参数：**
```json
{
  "name": "新名字",
  "avatar": "https://xxx/new-avatar.jpg"
}
```
**响应：**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": { ... }
}
```

---

### 2.3 获取收藏列表
```
GET /api/user/favorites
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "data": [
    { "id": 1, "productId": 1, "addedAt": "2024-03-25T10:00:00Z" }
  ]
}
```

---

### 2.4 获取收货地址
```
GET /api/user/addresses
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "张三",
      "phone": "13812345678",
      "province": "广东省",
      "city": "深圳市",
      "district": "南山区",
      "detail": "科技园xxx路xx号",
      "isDefault": true
    }
  ]
}
```

---

### 2.5 获取优惠券
```
GET /api/user/coupons
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "新人满减券",
      "type": "reduction",
      "value": 10,
      "minAmount": 50,
      "expireAt": "2024-12-31T23:59:59Z",
      "status": "available"
    }
  ]
}
```

---

## 三、商品模块 `/api`

### 3.1 获取分类列表
```
GET /api/categories
```
**响应：**
```json
{
  "code": 200,
  "data": [
    { "id": 1, "name": "奶茶", "icon": "cup" },
    { "id": 2, "name": "水果", "icon": "apple" },
    { "id": 3, "name": "甜品", "icon": "cake" },
    { "id": 4, "name": "主食", "icon": "utensils" }
  ]
}
```

---

### 3.2 获取商品列表
```
GET /api/products
```
**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| categoryId | number | 分类ID |
| keyword | string | 搜索关键词 |
| sort | string | hot / new / price |
| limit | number | 返回数量 |

**响应：**
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "珍珠奶茶",
      "desc": "Q弹珍珠 经典口感",
      "price": 18,
      "originalPrice": 24,
      "categoryId": 1,
      "icon": "cup",
      "tag": "热销",
      "sales": 999
    }
  ]
}
```

---

### 3.3 获取商品详情
```
GET /api/products/:id
```
**响应：**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "珍珠奶茶",
    "desc": "Q弹珍珠 经典口感",
    "price": 18,
    "originalPrice": 24,
    "categoryId": 1,
    "icon": "cup",
    "tag": "热销",
    "images": ["https://xxx/1.jpg"],
    "specs": [
      { "name": "默认", "price": 18 },
      { "name": "大杯", "price": 21 }
    ]
  }
}
```

---

### 3.4 搜索商品
```
GET /api/products/search?q=奶茶
```
**响应：**
```json
{
  "code": 200,
  "data": [...]
}
```

---

### 3.5 收藏/取消收藏商品
```
POST /api/products/:id/favorite
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "message": "收藏成功"
}
```

---

## 四、购物车模块 `/api/cart`

### 4.1 获取购物车
```
GET /api/cart
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": 1,
        "productId": 1,
        "name": "珍珠奶茶",
        "price": 18,
        "qty": 1,
        "spec": "默认",
        "checked": true
      }
    ],
    "total": 18
  }
}
```

---

### 4.2 添加商品到购物车
```
POST /api/cart/items
```
**请求头：**
```
Authorization: Bearer <token>
```
**请求参数：**
```json
{
  "productId": 1,
  "qty": 1,
  "spec": "默认",
  "price": 18
}
```
**响应：**
```json
{
  "code": 200,
  "message": "添加成功"
}
```

---

### 4.3 更新购物车商品数量
```
PUT /api/cart/items/:id
```
**请求头：**
```
Authorization: Bearer <token>
```
**请求参数：**
```json
{
  "qty": 2
}
```
**响应：**
```json
{
  "code": 200,
  "message": "更新成功"
}
```

---

### 4.4 删除购物车商品
```
DELETE /api/cart/items/:id
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "message": "删除成功"
}
```

---

### 4.5 清空购物车
```
POST /api/cart/clear
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "message": "清空成功"
}
```

---

### 4.6 获取购物车总价
```
GET /api/cart/total
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "data": {
    "total": 58,
    "discount": 10,
    "finalTotal": 48
  }
}
```

---

## 五、订单模块 `/api/orders`

### 5.1 创建订单
```
POST /api/orders
```
**请求头：**
```
Authorization: Bearer <token>
```
**请求参数：**
```json
{
  "items": [
    { "productId": 1, "qty": 1, "price": 18, "spec": "默认" }
  ],
  "couponId": 1,
  "addressId": 1,
  "remark": "少糖"
}
```
**响应：**
```json
{
  "code": 200,
  "message": "下单成功",
  "data": {
    "orderId": "20240325001",
    "total": 18
  }
}
```

---

### 5.2 获取订单列表
```
GET /api/orders
```
**请求头：**
```
Authorization: Bearer <token>
```
**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | all / pending / processing / completed / cancelled |
| page | number | 页码 |
| limit | number | 每页数量 |

**响应：**
```json
{
  "code": 200,
  "data": [
    {
      "id": "20240325001",
      "status": "pending",
      "time": "2024-03-25 14:30:25",
      "items": [
        { "name": "珍珠奶茶", "qty": 1, "price": 18 }
      ],
      "total": 18
    }
  ]
}
```

---

### 5.3 获取订单详情
```
GET /api/orders/:id
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "data": {
    "id": "20240325001",
    "status": "pending",
    "time": "2024-03-25 14:30:25",
    "items": [...],
    "total": 18,
    "address": { ... },
    "coupon": { ... }
  }
}
```

---

### 5.4 取消订单
```
PUT /api/orders/:id/cancel
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "message": "取消成功"
}
```

---

### 5.5 确认收货
```
PUT /api/orders/:id/complete
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "message": "确认收货成功"
}
```

---

## 六、商家端模块 `/api/merchant`

### 6.1 获取商家信息
```
GET /api/merchant/profile
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "奶茶铺子",
    "avatar": "https://xxx/avatar.jpg",
    "phone": "13812345678"
  }
}
```

---

### 6.2 获取今日统计
```
GET /api/merchant/today-stats
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "data": {
    "revenue": 1280,
    "orderCount": 32,
    "pendingCount": 5
  }
}
```

---

### 6.3 获取订单列表（商家）
```
GET /api/merchant/orders
```
**请求头：**
```
Authorization: Bearer <token>
```
**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | all / new / processing / completed |
| page | number | 页码 |

**响应：**
```json
{
  "code": 200,
  "data": [...]
}
```

---

### 6.4 接单
```
PUT /api/merchant/orders/:id/accept
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "message": "接单成功"
}
```

---

### 6.5 拒单
```
PUT /api/merchant/orders/:id/reject
```
**请求头：**
```
Authorization: Bearer <token>
```
**请求参数：**
```json
{
  "reason": "食材已用完"
}
```
**响应：**
```json
{
  "code": 200,
  "message": "已拒单"
}
```

---

### 6.6 完成订单
```
PUT /api/merchant/orders/:id/complete
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "message": "订单已完成"
}
```

---

### 6.7 获取商品列表（商家）
```
GET /api/merchant/products
```
**请求头：**
```
Authorization: Bearer <token>
```
**响应：**
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "珍珠奶茶",
      "price": 18,
      "category": "奶茶",
      "status": "on",  // on | off
      "sales": 999
    }
  ]
}
```

---

### 6.8 添加商品
```
POST /api/merchant/products
Content-Type: multipart/form-data
```
**请求头：**
```
Authorization: Bearer <token>
```
**请求参数：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 商品名称 |
| desc | string | 否 | 商品描述 |
| price | number | 是 | 商品价格 |
| categoryId | number | 是 | 分类ID |
| icon | string | 否 | 图标名称 |
| image | file | 否 | 商品图片（支持 jpg/png/webp，建议 400x400，最大 2MB） |

**响应：**
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 11,
    "image": "https://xxx/products/11.jpg"
  }
}
```

---

### 6.9 上传商品图片
```
POST /api/merchant/upload/image
Content-Type: multipart/form-data
```
**请求头：**
```
Authorization: Bearer <token>
```
**请求参数：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | file | 是 | 图片文件（支持 jpg/png/webp，最大 2MB） |

**响应：**
```json
{
  "code": 200,
  "data": {
    "url": "https://xxx/products/xxx.jpg"
  }
}
```

---

### 6.10 更新商品
```
PUT /api/merchant/products/:id
```
**请求头：**
```
Authorization: Bearer <token>
```
**请求参数：**
```json
{
  "name": "新名称",
  "price": 22,
  "status": "off"
}
```
**响应：**
```json
{
  "code": 200,
  "message": "更新成功"
}
```

---

### 6.11 获取统计数据
```
GET /api/merchant/stats
```
**请求头：**
```
Authorization: Bearer <token>
```
**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| date | string | today / week / month |

**响应：**
```json
{
  "code": 200,
  "data": {
    "revenue": 8560,
    "orderCount": 186,
    "avgOrderValue": 46,
    "productCount": 12,
    "trend": [
      { "date": "2024-03-19", "revenue": 1200, "orders": 30 },
      { "date": "2024-03-20", "revenue": 1100, "orders": 28 }
    ],
    "topProducts": [
      { "id": 1, "name": "珍珠奶茶", "sales": 86, "revenue": 1548 }
    ]
  }
}
```

---

## 七、错误码规范

| code | 说明 |
|------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | Token 无效/过期 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 422 | 业务逻辑错误 |
| 500 | 服务器错误 |

**业务逻辑错误示例：**
```json
{
  "code": 422,
  "message": "验证码错误",
  "errorCode": "INVALID_CODE"
}
```

| errorCode | 说明 |
|-----------|------|
| INVALID_CODE | 验证码错误 |
| CODE_EXPIRED | 验证码已过期 |
| PHONE_EXISTED | 手机号已注册 |
| PHONE_NOT_EXIST | 手机号未注册 |
| PASSWORD_ERROR | 密码错误 |

---

## 八、通用字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| token | string | JWT 访问令牌 |
| refreshToken | string | JWT 刷新令牌 |
| expiresIn | number | 过期时间（秒） |
| memberLevel | string | 会员等级：normal / silver / gold / platinum |
| orderStatus | string | 订单状态：pending / processing / completed / cancelled |
