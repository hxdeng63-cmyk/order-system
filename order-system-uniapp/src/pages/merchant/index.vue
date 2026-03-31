<template>
  <view class="merchant-home">
    <!-- Header -->
    <view class="merchant-header">
      <view class="merchant-header-top">
        <text class="merchant-title">商家中心</text>
        <text class="merchant-time">今日 {{ today }}</text>
      </view>
      <view class="merchant-stats">
        <view class="merchant-stat">
          <text class="merchant-stat-value">¥{{ stats.revenue }}</text>
          <text class="merchant-stat-label">今日营收</text>
        </view>
        <view class="merchant-stat">
          <text class="merchant-stat-value">{{ stats.orders }}</text>
          <text class="merchant-stat-label">今日订单</text>
        </view>
        <view class="merchant-stat">
          <text class="merchant-stat-value">{{ stats.pending }}</text>
          <text class="merchant-stat-label">待处理</text>
        </view>
      </view>
    </view>

    <!-- Quick Actions -->
    <view class="quick-actions">
      <view class="quick-action" @click="goToOrder">
        <view class="quick-action-wrapper">
          <view class="quick-action-icon">
            <image class="quick-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86_%E6%96%B0%E8%AE%A2%E5%8D%95.jpg" mode="aspectFit"></image>
          </view>
          <text class="quick-action-badge" v-if="stats.pending > 0">{{ stats.pending }}</text>
        </view>
        <text class="quick-action-label">新订单</text>
      </view>
      <view class="quick-action" @click="goToProduct">
        <view class="quick-action-icon">
          <image class="quick-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6_%E5%95%86%E5%93%81%E7%AE%A1%E7%90%86.jpg" mode="aspectFit"></image>
        </view>
        <text class="quick-action-label">商品管理</text>
      </view>
      <view class="quick-action" @click="goToStats">
        <view class="quick-action-icon">
          <image class="quick-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%BB%9F%E8%AE%A1.jpg" mode="aspectFit"></image>
        </view>
        <text class="quick-action-label">数据统计</text>
      </view>
    </view>

    <!-- Recent Orders -->
    <view class="section-header">
      <text class="section-title">最新订单</text>
      <view class="section-more" @click="goToOrder">
        <text>查看全部</text>
        <text class="iconfont">›</text>
      </view>
    </view>

    <view class="order-list">
      <view class="order-card" v-for="order in recentOrders" :key="order.id">
        <view class="order-card-header">
          <view class="order-card-info">
            <text class="order-id">订单号: {{ order.id }}</text>
            <text class="order-time">{{ order.time }}</text>
          </view>
          <text class="order-status" :class="getStatusClass(order.status)">{{ getStatusText(order.status) }}</text>
        </view>
        <view class="order-items">
          <view class="order-item-row" v-for="(item, index) in order.items" :key="index">
            <text class="order-item-name">{{ item.name }} x{{ item.qty }}</text>
            <text class="order-item-price">¥{{ item.price }}</text>
          </view>
        </view>
        <view class="order-card-footer">
          <text class="order-total">¥{{ order.total }}</text>
          <view class="order-actions" v-if="order.status === 'pending' || order.status === 'paid'">
            <button class="btn-cancel" @click="handleOrder(order, 'cancel')">拒单</button>
            <button class="btn-accept" @click="handleOrder(order, 'accept')">接单</button>
          </view>
          <view class="order-actions" v-else-if="order.status === 'processing'">
            <button class="btn-complete" @click="handleOrder(order, 'complete')">完成</button>
          </view>
          <view class="order-actions" v-else>
            <text class="order-done-text">已完成</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Bottom Nav -->
    <view class="bottom-nav">
      <view class="nav-item active">
        <image class="nav-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E9%A6%96%E9%A1%B5.jpg" mode="aspectFit"></image>
        <text>首页</text>
      </view>
      <view class="nav-item" @click="goToOrder">
        <image class="nav-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E8%AE%A2%E5%8D%95.jpg" mode="aspectFit"></image>
        <text>订单</text>
      </view>
      <view class="nav-item" @click="goToProduct">
        <image class="nav-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E5%95%86%E5%93%81.jpg" mode="aspectFit"></image>
        <text>商品</text>
      </view>
      <view class="nav-item" @click="goToStats">
        <image class="nav-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E7%BB%9F%E8%AE%A1.jpg" mode="aspectFit"></image>
        <text>统计</text>
      </view>
      <view class="nav-item" @click="goToProfile">
        <image class="nav-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E6%88%91%E7%9A%84.jpg" mode="aspectFit"></image>
        <text>我的</text>
      </view>
    </view>
  </view>
</template>

<script>
import { merchantGet, merchantPut } from '../../api/index.js'

export default {
  data() {
    return {
      today: '',
      stats: {
        revenue: 0,
        orders: 0,
        pending: 0
      },
      recentOrders: []
    }
  },
  onLoad() {
    this.today = this.formatDate(new Date())
    this.loadData()
  },
  onShow() {
    this.loadData()
  },
  onPullDownRefresh() {
    this.loadData().then(() => {
      uni.stopPullDownRefresh()
    })
  },
  methods: {
    formatDate(date) {
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${month}-${day}`
    },
    async loadData() {
      await Promise.all([
        this.loadStats(),
        this.loadOrders()
      ])
    },
    async loadStats() {
      try {
        const res = await merchantGet('/api/merchant/today-stats')
        if (res.revenue !== undefined) {
          this.stats = res
        }
      } catch (e) {
        console.error('加载商家统计失败', e)
      }
    },
    async loadOrders() {
      try {
        const res = await merchantGet('/api/merchant/orders?status=new&limit=5')
        if (res.code === 200 && res.data) {
          this.recentOrders = res.data.list || []
        }
      } catch (e) {
        console.error('加载订单失败', e)
      }
    },
    getStatusClass(status) {
      const map = {
        pending: 'new',
        paid: 'new',
        processing: 'processing',
        completed: 'completed',
        cancelled: 'cancelled'
      }
      return map[status] || ''
    },
    getStatusText(status) {
      const map = {
        pending: '待支付',
        paid: '待接单',
        processing: '制作中',
        completed: '已完成',
        cancelled: '已取消'
      }
      return map[status] || status
    },
    async handleOrder(order, action) {
      try {
        if (action === 'accept') {
          await merchantPut(`/api/merchant/orders/${order.id}/accept`)
          uni.showToast({ title: '已接单', icon: 'success' })
          order.status = 'processing'
        } else if (action === 'cancel') {
          await merchantPut(`/api/merchant/orders/${order.id}/reject`)
          uni.showToast({ title: '已拒单', icon: 'success' })
          order.status = 'cancelled'
        } else if (action === 'complete') {
          await merchantPut(`/api/merchant/orders/${order.id}/complete`)
          uni.showToast({ title: '已完成', icon: 'success' })
          order.status = 'completed'
        }
      } catch (e) {
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },
    goToOrder() {
      uni.navigateTo({ url: '/pages/merchant/order' })
    },
    goToProduct() {
      uni.navigateTo({ url: '/pages/merchant/product' })
    },
    goToStats() {
      uni.navigateTo({ url: '/pages/merchant/stats' })
    },
    goToProfile() {
      uni.navigateTo({ url: '/pages/merchant/profile' })
    }
  }
}
</script>

<style scoped>
.merchant-home {
  min-height: 100vh;
  background: #F7F7F7;
  padding-bottom: 120rpx;
}

.merchant-header {
  padding: 32rpx;
  background: #C8956C;
  color: #fff;
}

.merchant-header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.merchant-title {
  font-size: 36rpx;
  font-weight: 600;
}

.merchant-time {
  font-size: 22rpx;
  opacity: 0.85;
}

.merchant-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}

.merchant-stat {
  background: rgba(255,255,255,0.15);
  border-radius: 20rpx;
  padding: 16rpx;
  text-align: center;
}

.merchant-stat-value {
  font-size: 36rpx;
  font-weight: 600;
  font-family: 'DM Mono', monospace;
}

.merchant-stat-label {
  font-size: 20rpx;
  opacity: 0.85;
}

.quick-actions {
  display: flex;
  gap: 16rpx;
  padding: 32rpx;
}

.quick-action {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 24rpx;
  background: #fff;
  border-radius: 20rpx;
  border: 1px solid #E5E5E5;
}

.quick-action-wrapper {
  position: relative;
}

.quick-action-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #F5EDE6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-action-icon .iconfont {
  font-size: 36rpx;
}

.quick-icon {
  width: 56rpx;
  height: 56rpx;
}

.quick-action-label {
  font-size: 24rpx;
  color: #666;
}

.quick-action-badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  background: #F44336;
  color: #fff;
  font-size: 18rpx;
  font-weight: 600;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
  min-width: 32rpx;
  text-align: center;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32rpx 32rpx 16rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
}

.section-more {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #999;
}

.order-list {
  padding: 0 32rpx 32rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.order-card {
  background: #fff;
  border-radius: 20rpx;
  border: 1px solid #E5E5E5;
  overflow: hidden;
}

.order-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 24rpx;
  background: #FAFAFA;
  border-bottom: 1px solid #E5E5E5;
}

.order-card-info {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.order-id {
  font-size: 24rpx;
  color: #999;
}

.order-time {
  font-size: 20rpx;
  color: #999;
}

.order-status {
  font-size: 22rpx;
  font-weight: 500;
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
}

.order-status.new {
  background: #FFF3E0;
  color: #FF9800;
}

.order-status.processing {
  background: #E3F2FD;
  color: #2196F3;
}

.order-status.completed {
  background: #E8F5E9;
  color: #4CAF50;
}

.order-status.cancelled {
  background: #F5F5F5;
  color: #999;
}

.order-items {
  padding: 24rpx;
}

.order-item-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.order-item-row:last-child {
  margin-bottom: 0;
}

.order-item-name {
  font-size: 26rpx;
}

.order-item-price {
  font-size: 24rpx;
  color: #999;
  font-family: 'DM Mono', monospace;
}

.order-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 24rpx;
  background: #FAFAFA;
  border-top: 1px solid #E5E5E5;
}

.order-total {
  font-size: 28rpx;
  font-weight: 500;
  font-family: 'DM Mono', monospace;
}

.order-actions {
  display: flex;
  gap: 16rpx;
}

.btn-accept, .btn-complete {
  padding: 8rpx 24rpx;
  background: #4CAF50;
  color: #fff;
  border: none;
  border-radius: 8rpx;
  font-size: 24rpx;
  font-weight: 500;
}

.btn-cancel {
  padding: 8rpx 24rpx;
  background: transparent;
  color: #F44336;
  border: 1px solid #F44336;
  border-radius: 8rpx;
  font-size: 24rpx;
  font-weight: 500;
}

.btn-complete {
  background: #C8956C;
}

.order-done-text {
  font-size: 22rpx;
  color: #999;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 1px solid #E5E5E5;
  display: flex;
  padding: 16rpx 0;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  z-index: 100;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  color: #999;
  font-size: 20rpx;
}

.nav-item.active {
  color: #C8956C;
}

.nav-item .iconfont {
  font-size: 44rpx;
}

.nav-icon {
  width: 48rpx;
  height: 48rpx;
}
</style>
