<template>
  <view class="merchant-profile">
    <!-- Profile Header -->
    <view class="profile-header">
      <!-- API: GET /api/merchant/profile -->
      <view class="profile-avatar">
        <image class="avatar-img" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E5%A4%B4%E5%83%8F.jpg" mode="aspectFill"></image>
      </view>
      <view class="profile-info">
        <text class="profile-name">{{ merchant.name }}</text>
        <text class="profile-shop-name">商家ID: {{ merchant.id }}</text>
      </view>
    </view>

    <!-- Menu Groups -->
    <view class="profile-menu">
      <!-- Shop Info Group -->
      <view class="profile-menu-group">
        <view class="profile-menu-item" @click="goToShopInfo">
          <!-- API: GET /api/merchant/shop-info -->
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <image class="menu-icon-img" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E5%A4%B4%E5%83%8F.jpg" mode="aspectFit"></image>
            </view>
            <text class="profile-menu-label">店铺信息</text>
          </view>
          <view class="profile-menu-arrow">
            <text class="iconfont">›</text>
          </view>
        </view>
        <view class="profile-menu-item" @click="goToCategories">
          <!-- API: GET /api/categories -->
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text class="iconfont">📂</text>
            </view>
            <text class="profile-menu-label">商品分类</text>
          </view>
          <view class="profile-menu-arrow">
            <text class="iconfont">›</text>
          </view>
        </view>
        <view class="profile-menu-item" @click="goToEarnings">
          <!-- API: GET /api/merchant/earnings -->
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text class="iconfont">💰</text>
            </view>
            <text class="profile-menu-label">账户与收益</text>
          </view>
          <view class="profile-menu-arrow">
            <text class="iconfont">›</text>
          </view>
        </view>
      </view>

      <!-- Coupon & Coin Group -->
      <view class="profile-menu-group">
        <view class="profile-menu-item" @click="goToCouponManage">
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text class="iconfont">🎫</text>
            </view>
            <text class="profile-menu-label">优惠券管理</text>
          </view>
          <view class="profile-menu-arrow">
            <text class="iconfont">›</text>
          </view>
        </view>
        <view class="profile-menu-item" @click="goToCoinManage">
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text class="iconfont">🪙</text>
            </view>
            <text class="profile-menu-label">熊币管理</text>
          </view>
          <view class="profile-menu-arrow">
            <text class="iconfont">›</text>
          </view>
        </view>
      </view>

      <!-- Settings Group -->
      <view class="profile-menu-group">
        <view class="profile-menu-item" @click="goToNotifications">
          <!-- API: GET /api/merchant/notifications -->
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text class="iconfont">🔔</text>
            </view>
            <text class="profile-menu-label">消息通知</text>
          </view>
          <view class="profile-menu-arrow">
            <text class="iconfont">›</text>
          </view>
        </view>
        <view class="profile-menu-item" @click="goToSettings">
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text class="iconfont">⚙️</text>
            </view>
            <text class="profile-menu-label">设置</text>
          </view>
          <view class="profile-menu-arrow">
            <text class="iconfont">›</text>
          </view>
        </view>
        <view class="profile-menu-item" @click="goToHelp">
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text class="iconfont">❓</text>
            </view>
            <text class="profile-menu-label">帮助与反馈</text>
          </view>
          <view class="profile-menu-arrow">
            <text class="iconfont">›</text>
          </view>
        </view>
        <view class="profile-menu-item" @click="handleLogout">
          <view class="profile-menu-left">
            <view class="profile-menu-icon" style="background: #FFEBEE;">
              <text class="iconfont">🚪</text>
            </view>
            <text class="profile-menu-label" style="color: #F44336;">退出登录</text>
          </view>
          <view class="profile-menu-arrow">
            <text class="iconfont">›</text>
          </view>
        </view>
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
      <view class="nav-item" @click="goToStats">
        <image class="nav-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E7%BB%9F%E8%AE%A1.jpg" mode="aspectFit"></image>
        <text>统计</text>
      </view>
      <view class="nav-item active">
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
      merchant: {
        id: '',
        name: '加载中...'
      }
    }
  },
  onLoad() {
    this.loadProfile()
  },
  onPullDownRefresh() {
    this.loadProfile().then(() => {
      uni.stopPullDownRefresh()
    })
  },
  methods: {
    async loadProfile() {
      const token = uni.getStorageSync('merchant_token')
      if (!token) {
        uni.showModal({
          title: '提示',
          content: '请先登录商家账号',
          success: () => {
            uni.navigateTo({ url: '/pages/login/index' })
          }
        })
        return
      }
      try {
        const res = await merchantGet('/api/merchant/profile')
        if (res.id) {
          res.name = '布布厨房'
          this.merchant = res
        }
      } catch (e) {
        console.error('加载商家信息失败', e)
        uni.removeStorageSync('merchant_token')
        uni.showToast({ title: '登录已过期', icon: 'none' })
        setTimeout(() => {
          uni.navigateTo({ url: '/pages/login/index' })
        }, 1000)
      }
    },
    handleLogout() {
      uni.removeStorageSync('merchant_token')
      uni.removeStorageSync('merchant_info')
      uni.showToast({ title: '已退出登录', icon: 'success' })
      setTimeout(() => {
        uni.navigateTo({ url: '/pages/login/index' })
      }, 1000)
    },
    goToShopInfo() {
      uni.showModal({
        title: '店铺信息',
        content: `店铺名称：${this.merchant.name}\n商家ID：${this.merchant.id}\n邀请码：${this.merchant.inviteCode || '无'}\n\n提示：邀请码用于客户注册时绑定本商家`,
        showCancel: false,
        confirmText: '知道了'
      })
    },
    goToCategories() {
      uni.showToast({ title: '商品分类', icon: 'none' })
    },
    async goToEarnings() {
      try {
        const res = await merchantGet('/api/merchant/earnings')
        uni.showModal({
          title: '账户与收益',
          content: `总余额: ¥${res.balance || 0}\n已提现: ¥${res.withdrawn || 0}\n待提现: ¥${res.pending || 0}`,
          showCancel: false
        })
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    goToCouponManage() {
      uni.navigateTo({ url: '/pages/merchant/coupon' })
    },
    goToCoinManage() {
      uni.navigateTo({ url: '/pages/merchant/coin' })
    },
    async goToNotifications() {
      try {
        const res = await merchantGet('/api/merchant/notifications')
        if (res.code === 200 && res.data) {
          const list = res.data.list || []
          if (list.length === 0) {
            uni.showToast({ title: '暂无通知', icon: 'none' })
          } else {
            const content = list.slice(0, 3).map(n => `${n.title}: ${n.content}`).join('\n')
            uni.showModal({
              title: '消息通知',
              content: content,
              showCancel: false
            })
          }
        }
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    goToSettings() {
      uni.showToast({ title: '设置', icon: 'none' })
    },
    goToHelp() {
      uni.showToast({ title: '帮助与反馈', icon: 'none' })
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
    goToStats() {
      uni.navigateTo({ url: '/pages/merchant/stats' })
    }
  }
}
</script>

<style scoped>
.merchant-profile {
  min-height: 100vh;
  background: #F7F7F7;
  padding-bottom: 120rpx;
}

.profile-header {
  padding: 48rpx 32rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  background: #C8956C;
  color: #fff;
}

.profile-avatar {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  border: 4rpx solid rgba(255,255,255,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 36rpx;
  font-weight: 600;
  display: block;
  margin-bottom: 8rpx;
}

.profile-shop-name {
  font-size: 24rpx;
  opacity: 0.85;
}

.profile-menu {
  padding: 32rpx;
}

.profile-menu-group {
  background: #fff;
  border-radius: 20rpx;
  border: 1px solid #E5E5E5;
  overflow: hidden;
  margin-bottom: 32rpx;
}

.profile-menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx;
  border-bottom: 1px solid #E5E5E5;
}

.profile-menu-item:last-child {
  border-bottom: none;
}

.profile-menu-left {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.profile-menu-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 16rpx;
  background: #F7F7F7;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-menu-icon .iconfont {
  font-size: 36rpx;
}

.menu-icon-img {
  width: 48rpx;
  height: 48rpx;
}

.profile-menu-label {
  font-size: 28rpx;
}

.profile-menu-arrow {
  color: #999;
}

.profile-menu-arrow .iconfont {
  font-size: 36rpx;
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
