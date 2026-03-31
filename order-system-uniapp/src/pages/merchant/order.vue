<template>
  <view class="merchant-order">
    <!-- Header -->
    <view class="page-header">
      <text class="page-title">订单管理</text>
      <view class="refresh-btn" @click="loadOrders">
        <text>🔄</text>
      </view>
    </view>

    <!-- Order Tabs -->
    <view class="order-tabs">
      <view
        class="order-tab"
        :class="{ active: currentTab === 'all' }"
        @click="switchTab('all')"
      >
        全部 <text class="order-tab-count" v-if="counts.all > 0">{{ counts.all }}</text>
      </view>
      <view
        class="order-tab"
        :class="{ active: currentTab === 'pending' }"
        @click="switchTab('pending')"
      >
        新订单 <text class="order-tab-count" v-if="counts.pending > 0">{{ counts.pending }}</text>
      </view>
      <view
        class="order-tab"
        :class="{ active: currentTab === 'processing' }"
        @click="switchTab('processing')"
      >
        进行中 <text class="order-tab-count" v-if="counts.processing > 0">{{ counts.processing }}</text>
      </view>
      <view
        class="order-tab"
        :class="{ active: currentTab === 'completed' }"
        @click="switchTab('completed')"
      >
        已完成
      </view>
    </view>

    <!-- Order List -->
    <scroll-view scroll-y class="order-scroll">
      <view class="order-list">
        <view class="order-card" v-for="order in filteredOrders" :key="order.id">
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
          <view class="order-remark" v-if="order.customerNote">
            <text class="remark-label">备注：</text>
            <text class="remark-text">{{ order.customerNote }}</text>
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
            <view class="order-actions" v-else-if="order.status === 'completed' || order.status === 'received' || order.status === 'cancelled'">
              <button class="btn-delete" @click="handleOrder(order, 'delete')">删除</button>
            </view>
            <view class="order-actions" v-else>
              <text class="order-done-text">已完成</text>
            </view>
          </view>
        </view>

        <view class="empty-state" v-if="filteredOrders.length === 0">
          <text class="iconfont">📋</text>
          <text>暂无订单</text>
        </view>
      </view>
    </scroll-view>

    <!-- Bottom Nav -->
    <view class="bottom-nav">
      <view class="nav-item" @click="goToHome">
        <image class="nav-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E9%A6%96%E9%A1%B5.jpg" mode="aspectFit"></image>
        <text>首页</text>
      </view>
      <view class="nav-item active">
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
import { merchantGet, merchantPut, merchantDel } from '../../api/index.js'

export default {
  data() {
    return {
      currentTab: 'all',
      orders: [],
      counts: {
        all: 0,
        pending: 0,
        processing: 0,
        completed: 0
      }
    }
  },
  computed: {
    filteredOrders() {
      if (this.currentTab === 'all') {
        return this.orders.filter(o => o.status !== 'cancelled')
      }
      if (this.currentTab === 'pending') {
        return this.orders.filter(o => o.status === 'pending' || o.status === 'paid')
      }
      if (this.currentTab === 'completed') {
        return this.orders.filter(o => o.status === 'completed' || o.status === 'received')
      }
      return this.orders.filter(o => o.status === this.currentTab)
    }
  },
  onLoad() {
    this.loadOrders()
  },
  onShow() {
    this.loadOrders()
  },
  onPullDownRefresh() {
    this.loadOrders().then(() => {
      uni.stopPullDownRefresh()
    })
  },
  methods: {
    async loadOrders() {
      try {
        const res = await merchantGet('/api/merchant/orders')
        if (res.code === 200 && res.data) {
          this.orders = res.data.list || []
          this.updateCounts()
        }
      } catch (e) {
        console.error('加载订单失败', e)
      }
    },
    updateCounts() {
      this.counts = {
        all: this.orders.filter(o => o.status !== 'cancelled').length,
        pending: this.orders.filter(o => o.status === 'pending' || o.status === 'paid').length,
        processing: this.orders.filter(o => o.status === 'processing').length,
        completed: this.orders.filter(o => o.status === 'completed').length
      }
    },
    switchTab(tab) {
      this.currentTab = tab
      this.loadOrders()
    },
    getStatusClass(status) {
      const map = {
        pending: 'new',
        paid: 'new',
        processing: 'processing',
        completed: 'completed'
      }
      return map[status] || ''
    },
    getStatusText(status) {
      const map = {
        pending: '待支付',
        paid: '待接单',
        processing: '制作中',
        completed: '已完成',
        cancelled: '已取消',
        received: '已取餐'
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
        } else if (action === 'delete') {
          uni.showModal({
            title: '确认删除',
            content: '确定要删除该订单吗？',
            confirmColor: '#F44336',
            success: async (res) => {
              if (res.confirm) {
                await merchantDel(`/api/merchant/orders/${order.id}`)
                uni.showToast({ title: '已删除', icon: 'success' })
                this.loadOrders()
              }
            }
          })
          return
        }
        this.updateCounts()
      } catch (e) {
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },
    goToHome() {
      uni.navigateTo({ url: '/pages/merchant/index' })
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
.merchant-order {
  min-height: 100vh;
  background: #F7F7F7;
  padding-bottom: 120rpx;
}

.page-header {
  padding: 32rpx;
  background: #fff;
  border-bottom: 1px solid #E5E5E5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 40rpx;
  font-weight: 700;
}

.refresh-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F7F7F7;
  border-radius: 50%;
  font-size: 16px;
}

.order-tabs {
  display: flex;
  padding: 32rpx;
  gap: 48rpx;
  background: #fff;
  border-bottom: 1px solid #E5E5E5;
}

.order-tab {
  font-size: 28rpx;
  color: #999;
  padding-bottom: 16rpx;
  border-bottom: 4rpx solid transparent;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.order-tab.active {
  color: #C8956C;
  border-bottom-color: #C8956C;
  font-weight: 500;
}

.order-tab-count {
  background: #F44336;
  color: #fff;
  font-size: 20rpx;
  font-weight: 600;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
}

.order-scroll {
  height: calc(100vh - 280rpx);
}

.order-list {
  padding: 24rpx 32rpx;
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

.order-items {
  padding: 24rpx;
}

.order-remark {
  padding: 16rpx 24rpx;
  background: #FFF9E6;
  border-top: 1px solid #F5E6D3;
  display: flex;
  gap: 8rpx;
}

.remark-label {
  font-size: 22rpx;
  color: #999;
}

.remark-text {
  font-size: 22rpx;
  color: #666;
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

.btn-accept {
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
  padding: 8rpx 24rpx;
  background: #C8956C;
  color: #fff;
  border: none;
  border-radius: 8rpx;
  font-size: 24rpx;
  font-weight: 500;
}

.btn-delete {
  padding: 8rpx 24rpx;
  background: #FFEBEE;
  color: #F44336;
  border: none;
  border-radius: 8rpx;
  font-size: 24rpx;
  font-weight: 500;
}

.order-done-text {
  font-size: 22rpx;
  color: #999;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  padding: 80rpx 0;
  color: #999;
  font-size: 28rpx;
}

.empty-state .iconfont {
  font-size: 80rpx;
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
