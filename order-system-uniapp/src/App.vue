<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  console.log('========== 点单系统 API 接口配置 ==========')
  console.log('【用户端】')
  console.log('  商品相关:')
  console.log('    GET  /api/categories           - 获取分类列表')
  console.log('    GET  /api/products            - 获取商品列表')
  console.log('    GET  /api/products/:id        - 获取商品详情')
  console.log('    GET  /api/products/search?q=  - 搜索商品')
  console.log('  购物车:')
  console.log('    GET  /api/cart                - 获取购物车')
  console.log('    POST /api/cart/items          - 添加商品到购物车')
  console.log('    PUT  /api/cart/items/:id     - 更新购物车商品数量')
  console.log('  DELETE /api/cart/items/:id     - 删除购物车商品')
  console.log('    POST /api/cart/clear         - 清空购物车')
  console.log('  订单:')
  console.log('    POST /api/orders              - 创建订单')
  console.log('    GET  /api/orders              - 获取订单列表')
  console.log('    GET  /api/orders/:id          - 获取订单详情')
  console.log('    PUT  /api/orders/:id/cancel  - 取消订单')
  console.log('    PUT  /api/orders/:id/pay     - 支付订单')
  console.log('  用户:')
  console.log('    GET  /api/user/profile        - 获取用户信息')
  console.log('    PUT  /api/user/profile        - 更新用户信息')
  console.log('  认证:')
  console.log('    POST /api/auth/login          - 用户登录')
  console.log('    POST /api/auth/register       - 用户注册')
  console.log('    POST /api/auth/logout         - 退出登录')
  console.log('')
  console.log('【商家端】')
  console.log('    POST /api/merchant/login      - 商家登录')
  console.log('    GET  /api/merchant/profile    - 商家信息')
  console.log('    GET  /api/merchant/today-stats - 今日统计')
  console.log('    GET  /api/merchant/earnings   - 收益信息')
  console.log('    GET  /api/merchant/orders    - 商家订单列表')
  console.log('    PUT  /api/merchant/orders/:id/accept  - 接单')
  console.log('    PUT  /api/merchant/orders/:id/reject  - 拒单')
  console.log('    PUT  /api/merchant/orders/:id/complete  - 完成订单')
  console.log('    GET  /api/merchant/products   - 商品列表')
  console.log('    POST /api/merchant/products  - 添加商品')
  console.log('    PUT  /api/merchant/products/:id - 更新商品')
  console.log('    PUT  /api/merchant/products/:id/status - 切换状态')
  console.log('    GET  /api/merchant/stats     - 统计概览')
  console.log('========================================')
})
</script>

<style>
@import '@/uni.scss';

/* 全局样式 */
page {
  background-color: #FFFFFF;
  font-family: 'Inter', -apple-system, sans-serif;
  font-size: 16px;
  color: #1A1A1A;
}

.container {
  padding-bottom: 100px;
}
</style>
