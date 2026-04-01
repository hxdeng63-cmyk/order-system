<template>
  <view class="page">
    <!-- 搜索栏 -->
    <view class="search-bar">
      <input
        class="search-input"
        v-model="keyword"
        placeholder="搜索商家名称"
        @confirm="handleSearch"
      />
      <button class="search-btn" @click="handleSearch">搜索</button>
    </view>

    <!-- 商家列表 -->
    <view class="merchant-list" v-if="merchants.length > 0">
      <view
        class="merchant-card"
        v-for="merchant in merchants"
        :key="merchant.id"
        @click="selectMerchant(merchant)"
      >
        <view class="merchant-info">
          <view class="merchant-avatar">
            <image
              v-if="merchant.avatar"
              :src="merchant.avatar"
              mode="aspectFill"
            />
            <text v-else class="avatar-placeholder">{{ merchant.name.slice(0, 1) }}</text>
          </view>
          <view class="merchant-detail">
            <text class="merchant-name">{{ merchant.name }}</text>
            <text class="merchant-address" v-if="merchant.address">{{ merchant.address }}</text>
            <text class="merchant-phone" v-if="merchant.phone">{{ merchant.phone }}</text>
          </view>
        </view>
        <view class="merchant-action">
          <text class="select-btn">选择</text>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else-if="!loading">
      <text class="empty-text">暂无商家</text>
    </view>

    <!-- 加载中 -->
    <view class="loading-state" v-if="loading">
      <text>加载中...</text>
    </view>
  </view>
</template>

<script>
import { get } from '../../api/index.js'

export default {
  data() {
    return {
      loading: false,
      merchants: [],
      keyword: '',
      page: 1,
      total: 0
    }
  },
  onLoad() {
    this.loadMerchants()
  },
  onShow() {
    // 如果有全局选中的商家，刷新一下
    const currentMerchantId = uni.getStorageSync('current_merchant_id')
    if (currentMerchantId) {
      // 可以高亮当前选中的商家
    }
  },
  methods: {
    async loadMerchants() {
      this.loading = true
      try {
        const res = await get('/api/merchants', {
          search: this.keyword || undefined,
          page: this.page,
          limit: 20
        })
        if (res.code === 200) {
          this.merchants = res.data.list || []
          this.total = res.data.total || 0
        }
      } catch (e) {
        console.error('加载商家列表失败', e)
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
      this.loading = false
    },
    handleSearch() {
      this.page = 1
      this.loadMerchants()
    },
    selectMerchant(merchant) {
      // 保存当前选中的商家
      uni.setStorageSync('current_merchant_id', merchant.id)
      uni.setStorageSync('current_merchant_name', merchant.name)
      uni.setStorageSync('current_merchant', JSON.stringify(merchant))

      uni.showToast({
        title: `已选择：${merchant.name}`,
        icon: 'success'
      })

      // 返回上一页或跳转到首页
      setTimeout(() => {
        const pages = getCurrentPages()
        if (pages.length > 1) {
          uni.navigateBack()
        } else {
          uni.switchTab({ url: '/pages/index/index' })
        }
      }, 1000)
    }
  }
}
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #F7F7F7;
}

.search-bar {
  display: flex;
  padding: 24rpx 32rpx;
  background: #FFFFFF;
  gap: 16rpx;
}

.search-input {
  flex: 1;
  height: 72rpx;
  padding: 0 24rpx;
  background: #F7F7F7;
  border-radius: 36rpx;
  font-size: 28rpx;
  border: 1px solid #E5E5E5;
}

.search-btn {
  width: 120rpx;
  height: 72rpx;
  line-height: 72rpx;
  background: #C8956C;
  color: #fff;
  border: none;
  border-radius: 36rpx;
  font-size: 28rpx;
  padding: 0;
}

.merchant-list {
  padding: 24rpx 32rpx;
}

.merchant-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  margin-bottom: 24rpx;
}

.merchant-info {
  display: flex;
  align-items: center;
  gap: 24rpx;
  flex: 1;
}

.merchant-avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 16rpx;
  background: #F7F7F7;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;

  image {
    width: 100%;
    height: 100%;
  }
}

.avatar-placeholder {
  font-size: 48rpx;
  font-weight: 600;
  color: #C8956C;
}

.merchant-detail {
  flex: 1;
}

.merchant-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #1A1A1A;
  display: block;
  margin-bottom: 8rpx;
}

.merchant-address {
  font-size: 24rpx;
  color: #999999;
  display: block;
  margin-bottom: 4rpx;
}

.merchant-phone {
  font-size: 24rpx;
  color: #999999;
}

.merchant-action {
  margin-left: 24rpx;
}

.select-btn {
  padding: 12rpx 24rpx;
  background: #C8956C;
  color: #FFFFFF;
  border-radius: 24rpx;
  font-size: 26rpx;
}

.empty-state {
  padding: 120rpx 0;
  text-align: center;
}

.empty-text {
  font-size: 28rpx;
  color: #999999;
}

.loading-state {
  padding: 48rpx 0;
  text-align: center;
  color: #999999;
  font-size: 28rpx;
}
</style>
