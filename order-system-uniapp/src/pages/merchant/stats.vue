<template>
  <view class="merchant-stats">
    <!-- Header -->
    <view class="page-header">
      <text class="page-title">数据统计</text>
    </view>

    <!-- Date Picker -->
    <view class="stats-date-picker">
      <!-- API: GET /api/merchant/stats?date=today -->
      <button
        class="date-btn"
        :class="{ active: dateRange === 'today' }"
        @click="switchDate('today')"
      >今日</button>
      <button
        class="date-btn"
        :class="{ active: dateRange === 'week' }"
        @click="switchDate('week')"
      >本周</button>
      <button
        class="date-btn"
        :class="{ active: dateRange === 'month' }"
        @click="switchDate('month')"
      >本月</button>
      <button
        class="date-btn"
        :class="{ active: dateRange === 'custom' }"
        @click="switchDate('custom')"
      >自定义</button>
    </view>

    <!-- Stats Cards -->
    <view class="stats-cards">
      <!-- API: GET /api/merchant/stats/revenue -->
      <view class="stats-card">
        <text class="stats-card-label">总营收</text>
        <text class="stats-card-value">¥{{ (stats.revenue || 0).toLocaleString() }}</text>
        <text class="stats-card-change up" v-if="stats.revenueChange > 0">↑ {{ stats.revenueChange }}% 较上周</text>
        <text class="stats-card-change down" v-else-if="stats.revenueChange < 0">↓ {{ Math.abs(stats.revenueChange) }}% 较上周</text>
        <text class="stats-card-change" v-else>- 持平</text>
      </view>
      <view class="stats-card">
        <text class="stats-card-label">订单数</text>
        <text class="stats-card-value">{{ stats.orders }}</text>
        <text class="stats-card-change up" v-if="stats.ordersChange > 0">↑ {{ stats.ordersChange }}% 较上周</text>
        <text class="stats-card-change down" v-else-if="stats.ordersChange < 0">↓ {{ Math.abs(stats.ordersChange) }}% 较上周</text>
        <text class="stats-card-change" v-else>- 持平</text>
      </view>
      <view class="stats-card">
        <text class="stats-card-label">客单价</text>
        <text class="stats-card-value">¥{{ stats.avgOrderValue }}</text>
        <text class="stats-card-change down" v-if="stats.avgChange > 0">↑ {{ stats.avgChange }}% 较上周</text>
        <text class="stats-card-change up" v-else-if="stats.avgChange < 0">↓ {{ Math.abs(stats.avgChange) }}% 较上周</text>
        <text class="stats-card-change" v-else>- 持平</text>
      </view>
      <view class="stats-card">
        <text class="stats-card-label">商品数</text>
        <text class="stats-card-value">{{ stats.productCount }}</text>
        <text class="stats-card-change" style="color: #999;">- 持平</text>
      </view>
    </view>

    <!-- Sales Trend -->
    <view class="section-header">
      <text class="section-title">销售趋势</text>
      <!-- API: GET /api/merchant/stats/trend -->
    </view>
    <view class="stats-chart">
      <view class="chart-placeholder">
        <text class="iconfont">📈</text>
        <text>近7天销售趋势图</text>
      </view>
    </view>

    <!-- Top Products -->
    <view class="section-header">
      <text class="section-title">热销商品 TOP5</text>
      <!-- API: GET /api/merchant/stats/top-products -->
    </view>
    <view class="stats-top-products">
      <view class="top-product-item" v-for="(product, index) in topProducts" :key="index">
        <view class="top-rank" :class="getRankClass(index)">{{ index + 1 }}</view>
        <view class="top-product-info">
          <text class="top-product-name">{{ product.name }}</text>
          <text class="top-product-sales">销量 {{ product.sales }} / 占比 {{ product.share }}%</text>
        </view>
        <text class="top-product-revenue">¥{{ (product.revenue || 0).toLocaleString() }}</text>
      </view>
    </view>

    <!-- Bottom Nav -->
    <view class="bottom-nav">
      <view class="nav-item" @click="goToHome">
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
      <view class="nav-item active">
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
import { merchantGet } from '../../api/index.js'

export default {
  data() {
    return {
      dateRange: 'today',
      stats: {
        revenue: 0,
        revenueChange: 0,
        orders: 0,
        ordersChange: 0,
        avgOrderValue: 0,
        avgChange: 0,
        productCount: 0
      },
      trend: [],
      topProducts: []
    }
  },
  onLoad() {
    this.loadStats()
  },
  onShow() {
    this.loadStats()
  },
  onPullDownRefresh() {
    this.loadStats().then(() => {
      uni.stopPullDownRefresh()
    })
  },
  methods: {
    async loadStats() {
      try {
        const res = await merchantGet(`/api/merchant/stats?date=${this.dateRange}`)
        if (res.code === 200 && res.data) {
          this.stats = res.data
          this.trend = res.data.trend || []
          this.topProducts = res.data.topProducts || []
        }
      } catch (e) {
        console.error('加载统计失败', e)
      }
    },
    async switchDate(range) {
      this.dateRange = range
      this.loadStats()
    },
    getRankClass(index) {
      const classes = ['gold', 'silver', 'bronze']
      return classes[index] || ''
    },
    goToHome() {
      uni.navigateTo({ url: '/pages/merchant/index' })
    },
    goToOrder() {
      uni.navigateTo({ url: '/pages/merchant/order' })
    },
    goToProduct() {
      uni.navigateTo({ url: '/pages/merchant/product' })
    },
    goToProfile() {
      uni.navigateTo({ url: '/pages/merchant/profile' })
    }
  }
}
</script>

<style scoped>
.merchant-stats {
  min-height: 100vh;
  background: #F7F7F7;
  padding-bottom: 120rpx;
}

.page-header {
  padding: 24rpx 32rpx;
  background: #fff;
  border-bottom: 1px solid #E5E5E5;
}

.page-title {
  font-size: 40rpx;
  font-weight: 700;
}

.stats-date-picker {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 32rpx;
  justify-content: center;
  background: #fff;
}

.date-btn {
  padding: 8rpx 32rpx;
  background: #F7F7F7;
  border: 1px solid #E5E5E5;
  border-radius: 8rpx;
  font-size: 24rpx;
  color: #666;
}

.date-btn.active {
  background: #C8956C;
  color: #fff;
  border-color: #C8956C;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24rpx;
  padding: 0 32rpx 32rpx;
}

.stats-card {
  background: #fff;
  border-radius: 20rpx;
  border: 1px solid #E5E5E5;
  padding: 24rpx;
}

.stats-card-label {
  font-size: 22rpx;
  color: #999;
  display: block;
  margin-bottom: 8rpx;
}

.stats-card-value {
  font-size: 48rpx;
  font-weight: 600;
  color: #1A1A1A;
  font-family: 'DM Mono', monospace;
  display: block;
}

.stats-card-change {
  font-size: 20rpx;
  margin-top: 8rpx;
  display: block;
}

.stats-card-change.up {
  color: #4CAF50;
}

.stats-card-change.down {
  color: #F44336;
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

.stats-chart {
  margin: 0 32rpx 32rpx;
  background: #fff;
  border-radius: 20rpx;
  border: 1px solid #E5E5E5;
  padding: 48rpx;
  height: 300rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  color: #999;
}

.chart-placeholder .iconfont {
  font-size: 64rpx;
}

.chart-placeholder text:last-child {
  font-size: 24rpx;
}

.stats-top-products {
  margin: 0 32rpx;
  background: #fff;
  border-radius: 20rpx;
  border: 1px solid #E5E5E5;
  padding: 16rpx 24rpx;
}

.top-product-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 16rpx 0;
  border-bottom: 1px solid #E5E5E5;
}

.top-product-item:last-child {
  border-bottom: none;
}

.top-rank {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: #F5EDE6;
  color: #C8956C;
  font-size: 22rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.top-rank.gold {
  background: #FFF8E1;
  color: #FFA000;
}

.top-rank.silver {
  background: #F5F5F5;
  color: #9E9E9E;
}

.top-rank.bronze {
  background: #FFF3E0;
  color: #E65100;
}

.top-product-info {
  flex: 1;
}

.top-product-name {
  font-size: 26rpx;
  font-weight: 500;
  display: block;
  margin-bottom: 4rpx;
}

.top-product-sales {
  font-size: 22rpx;
  color: #999;
}

.top-product-revenue {
  font-size: 26rpx;
  font-weight: 500;
  font-family: 'DM Mono', monospace;
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
