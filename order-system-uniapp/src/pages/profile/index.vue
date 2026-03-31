<template>
  <view class="page">
    <!-- 用户信息头部 -->
    <view class="profile-header" @click="handleProfileClick">
      <view class="profile-avatar">
        <image src="/static/tabbar/avatar.png" mode="aspectFill" class="avatar-img" />
      </view>
      <view class="profile-info">
        <text class="profile-name">{{ profile.name }}</text>
        <text class="profile-phone">{{ profile.phone }}</text>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="profile-menu">
      <view class="profile-menu-group">
        <view class="profile-menu-item" @click="goToFavorite">
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text>❤️</text>
            </view>
            <text class="profile-menu-label">我的收藏</text>
          </view>
          <text class="profile-menu-arrow">›</text>
        </view>

        <view class="profile-menu-item" @click="showToast('功能开发中')">
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text>📍</text>
            </view>
            <text class="profile-menu-label">收货地址</text>
          </view>
          <text class="profile-menu-arrow">›</text>
        </view>

        <view class="profile-menu-item" @click="goToCoupon">
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text>🎫</text>
            </view>
            <text class="profile-menu-label">优惠券</text>
          </view>
          <text class="profile-menu-arrow">›</text>
        </view>

        <view class="profile-menu-item" @click="goToCoin">
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text>🪙</text>
            </view>
            <text class="profile-menu-label">熊熊币</text>
          </view>
          <text class="profile-menu-arrow">›</text>
        </view>
      </view>

      <view class="profile-menu-group">
        <view class="profile-menu-item" @click="goToMerchant">
          <view class="profile-menu-left">
            <view class="profile-menu-icon" style="background: #E3F2FD;">
              <text>🏪</text>
            </view>
            <text class="profile-menu-label">商家入驻/管理</text>
          </view>
          <text class="profile-menu-arrow">›</text>
        </view>
        <view class="profile-menu-item" @click="showToast('功能开发中')">
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text>⚙️</text>
            </view>
            <text class="profile-menu-label">设置</text>
          </view>
          <text class="profile-menu-arrow">›</text>
        </view>

        <view class="profile-menu-item" @click="showToast('功能开发中')">
          <view class="profile-menu-left">
            <view class="profile-menu-icon">
              <text>❓</text>
            </view>
            <text class="profile-menu-label">帮助与反馈</text>
          </view>
          <text class="profile-menu-arrow">›</text>
        </view>
      </view>

      <view class="profile-menu-group">
        <view class="profile-menu-item" @click="handleLogout">
          <view class="profile-menu-left">
            <view class="profile-menu-icon" style="background: #FFEBEE;">
              <text>🚪</text>
            </view>
            <text class="profile-menu-label" style="color: #F44336;">退出登录</text>
          </view>
          <text class="profile-menu-arrow">›</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { post } from '../../api/index.js'

export default {
  data() {
    return {
      profile: {
        name: '游客用户',
        phone: '点击登录'
      }
    }
  },
  onLoad() {
    this.loadUserInfo()
  },
  onShow() {
    this.loadUserInfo()
  },
  methods: {
    loadUserInfo() {
      const token = uni.getStorageSync('token')
      if (token) {
        const userInfo = uni.getStorageSync('user_info')
        if (userInfo) {
          try {
            const user = JSON.parse(userInfo)
            this.profile.name = user.name || '用户'
            this.profile.phone = user.phone || ''
          } catch (e) {}
        }
      } else {
        this.profile.name = '游客用户'
        this.profile.phone = '点击登录'
      }
    },
    showToast(message) {
      uni.showToast({ title: message, icon: 'none' })
    },
    handleLogout() {
      post('/api/auth/logout').catch(() => {})
      uni.removeStorageSync('token')
      uni.removeStorageSync('user_info')
      this.profile.name = '游客用户'
      this.profile.phone = '点击登录'
      uni.showToast({ title: '已退出', icon: 'success' })
    },
    goToMerchant() {
      uni.navigateTo({ url: '/pages/login/index' })
    },
    goToCoupon() {
      const token = uni.getStorageSync('token')
      if (!token) {
        uni.showToast({ title: '请先登录', icon: 'none' })
        setTimeout(() => uni.navigateTo({ url: '/pages/login/index' }), 1500)
        return
      }
      uni.navigateTo({ url: '/pages/coupon/list' })
    },
    goToCoin() {
      const token = uni.getStorageSync('token')
      if (!token) {
        uni.showToast({ title: '请先登录', icon: 'none' })
        setTimeout(() => uni.navigateTo({ url: '/pages/login/index' }), 1500)
        return
      }
      uni.navigateTo({ url: '/pages/coin/index' })
    },
    goToFavorite() {
      const token = uni.getStorageSync('token')
      if (!token) {
        uni.showToast({ title: '请先登录', icon: 'none' })
        setTimeout(() => uni.navigateTo({ url: '/pages/login/index' }), 1500)
        return
      }
      uni.navigateTo({ url: '/pages/favorite/index' })
    },
    handleProfileClick() {
      const token = uni.getStorageSync('token')
      if (!token) {
        uni.navigateTo({ url: '/pages/login/index' })
      }
    }
  }
}
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #FFFFFF;
}

.profile-header {
  padding: 48px 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  background: linear-gradient(135deg, #C8956C 0%, #D4A574 100%);
  color: white;
}

.profile-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  overflow: hidden;
  background: rgba(255,255,255,0.2);
  border: 2px solid rgba(255,255,255,0.3);
}

.avatar-img {
  width: 100%;
  height: 100%;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 18px;
  font-weight: 600;
  display: block;
  margin-bottom: 4px;
}

.profile-phone {
  font-size: 12px;
  opacity: 0.85;
}

.profile-menu {
  padding: 16px;
}

.profile-menu-group {
  background: #F7F7F7;
  border-radius: 10px;
  border: 1px solid #E5E5E5;
  overflow: hidden;
  margin-bottom: 16px;
}

.profile-menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #E5E5E5;
}

.profile-menu-item:last-child {
  border-bottom: none;
}

.profile-menu-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile-menu-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.profile-menu-label {
  font-size: 14px;
}

.profile-menu-arrow {
  color: #999999;
  font-size: 18px;
}
</style>
