<template>
  <view class="page">
    <view class="login-header">
      <image class="header-image" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20260327195529_139_3.jpg" mode="aspectFill"></image>
      <view class="header-text">
        <text class="login-title">欢迎使用点单系统</text>
        <text class="login-subtitle">请选择登录身份</text>
      </view>
    </view>

    <!-- 身份选择 -->
    <view class="identity-section">
      <view
        class="identity-card"
        :class="{ active: identity === 'user' }"
        @click="selectIdentity('user')"
      >
        <view class="identity-icon">
          <image class="identity-img" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E4%B8%80%E4%BA%8C%E7%99%BB%E5%BD%95.jpg" mode="aspectFill"></image>
        </view>
        <view class="identity-info">
          <text class="identity-name">一二登录</text>
          <text class="identity-desc">我是一二宝，我要点餐</text>
        </view>
        <view class="identity-check" v-if="identity === 'user'">
          <text>✓</text>
        </view>
      </view>

      <view
        class="identity-card"
        :class="{ active: identity === 'merchant' }"
        @click="selectIdentity('merchant')"
      >
        <view class="identity-icon" style="background: #E3F2FD;">
          <image class="identity-img" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%B8%83%E5%B8%83%E7%99%BB%E5%BD%95.jpg" mode="aspectFill"></image>
        </view>
        <view class="identity-info">
          <text class="identity-name">布布登录</text>
          <text class="identity-desc">我是布布，我要做饭</text>
        </view>
        <view class="identity-check" v-if="identity === 'merchant'">
          <text>✓</text>
        </view>
      </view>
    </view>

    <!-- 登录表单 -->
    <view class="login-form" v-if="identity === 'user'">
      <view class="form-item">
        <text class="form-label">手机号</text>
        <input
          class="form-input"
          v-model="userForm.phone"
          placeholder="请输入手机号"
          type="number"
          maxlength="11"
        />
      </view>
      <view class="form-item">
        <text class="form-label">密码</text>
        <input
          class="form-input"
          v-model="userForm.password"
          placeholder="请输入密码"
          password
        />
      </view>
      <button class="btn-login" @click="handleUserLogin" :loading="loading">
        <text v-if="!loading">登录</text>
        <text v-else>登录中...</text>
      </button>
      <view class="form-footer">
        <text class="link-text" @click="goRegister">没有账号？去注册</text>
      </view>
      <view class="login-tip">
        <text class="tip-text">测试账号: 13800138000 / 123456</text>
      </view>
    </view>

    <view class="login-form" v-else>
      <view class="form-item">
        <text class="form-label">用户名</text>
        <input
          class="form-input"
          v-model="merchantForm.username"
          placeholder="请输入用户名"
          type="text"
        />
      </view>
      <view class="form-item">
        <text class="form-label">密码</text>
        <input
          class="form-input"
          v-model="merchantForm.password"
          placeholder="请输入密码"
          password
        />
      </view>
      <button class="btn-login" @click="handleMerchantLogin" :loading="loading">
        <text v-if="!loading">登录</text>
        <text v-else>登录中...</text>
      </button>
      <view class="form-footer">
        <text class="link-text" @click="goRegister">没有账号？去注册</text>
      </view>
      <view class="login-tip">
        <text class="tip-text">测试账号: 布布 / 123456</text>
      </view>
    </view>
  </view>
</template>

<script>
import { post, merchantPost } from '../../api/index.js'

export default {
  data() {
    return {
      identity: 'user', // user | merchant
      loading: false,
      userForm: {
        phone: '',
        password: ''
      },
      merchantForm: {
        username: '',
        password: ''
      }
    }
  },
  methods: {
    selectIdentity(type) {
      this.identity = type
    },
    async handleUserLogin() {
      if (!this.userForm.phone) {
        uni.showToast({ title: '请输入手机号', icon: 'none' })
        return
      }
      if (!this.userForm.password) {
        uni.showToast({ title: '请输入密码', icon: 'none' })
        return
      }

      this.loading = true
      try {
        const res = await post('/api/auth/login', {
          phone: this.userForm.phone,
          password: this.userForm.password
        })

        if (res.code === 200) {
          uni.setStorageSync('token', res.data.token)
          uni.setStorageSync('user_info', JSON.stringify(res.data.user))
          // 更新全局用户状态
          const app = getApp()
          if (app.globalData) {
            app.globalData.user = res.data.user
          }
          uni.showToast({ title: '登录成功', icon: 'success' })
          setTimeout(() => {
            uni.switchTab({ url: '/pages/profile/index' })
          }, 1000)
        } else {
          uni.showToast({ title: res.message || '登录失败', icon: 'none' })
        }
      } catch (e) {
        uni.showToast({ title: '登录失败，请检查网络', icon: 'none' })
      }
      this.loading = false
    },
    async handleMerchantLogin() {
      if (!this.merchantForm.username) {
        uni.showToast({ title: '请输入用户名', icon: 'none' })
        return
      }
      if (!this.merchantForm.password) {
        uni.showToast({ title: '请输入密码', icon: 'none' })
        return
      }

      this.loading = true
      try {
        const res = await merchantPost('/api/merchant/login', {
          username: this.merchantForm.username,
          password: this.merchantForm.password
        })

        if (res.code === 200) {
          uni.setStorageSync('merchant_token', res.data.token)
          uni.setStorageSync('merchant_info', JSON.stringify(res.data.merchant))
          uni.showToast({ title: '登录成功', icon: 'success' })
          setTimeout(() => {
            uni.navigateTo({ url: '/pages/merchant/index' })
          }, 1000)
        } else {
          uni.showToast({ title: res.message || '登录失败', icon: 'none' })
        }
      } catch (e) {
        uni.showToast({ title: '登录失败，请检查网络', icon: 'none' })
      }
      this.loading = false
    },
    goRegister() {
      if (this.identity === 'user') { uni.navigateTo({ url: '/pages/register/index' }) } else { uni.navigateTo({ url: '/pages/merchant/register' }) }
    }
  }
}
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #FFFFFF;
}

.login-header {
  position: relative;
  height: 400rpx;
  overflow: hidden;
}

.header-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.header-text {
  position: absolute;
  bottom: 48rpx;
  left: 32rpx;
  color: #fff;
  text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.3);
}

.login-title {
  font-size: 40rpx;
  font-weight: 700;
  display: block;
  margin-bottom: 12rpx;
}

.login-subtitle {
  font-size: 28rpx;
  opacity: 0.85;
}

.identity-section {
  padding: 32rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.identity-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 32rpx;
  background: #F7F7F7;
  border-radius: 20rpx;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.identity-card.active {
  border-color: #C8956C;
  background: #FDF8F4;
}

.identity-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: #FFF3E0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  overflow: hidden;
}

.identity-img {
  width: 100%;
  height: 100%;
}

.identity-info {
  flex: 1;
}

.identity-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #1A1A1A;
  display: block;
  margin-bottom: 8rpx;
}

.identity-desc {
  font-size: 24rpx;
  color: #999999;
}

.identity-check {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: #C8956C;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
}

.login-form {
  padding: 0 32rpx 32rpx;
}

.form-item {
  margin-bottom: 24rpx;
}

.form-label {
  font-size: 28rpx;
  color: #666;
  display: block;
  margin-bottom: 12rpx;
}

.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  background: #F7F7F7;
  border-radius: 12rpx;
  font-size: 28rpx;
  border: 1px solid #E5E5E5;
}

.btn-login {
  width: 100%;
  height: 88rpx;
  background: #C8956C;
  color: #fff;
  border: none;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: 500;
  margin-top: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-login:active {
  opacity: 0.85;
}

.form-footer {
  margin-top: 24rpx;
  text-align: center;
}

.link-text {
  font-size: 26rpx;
  color: #C8956C;
}

.login-tip {
  margin-top: 32rpx;
  text-align: center;
}

.tip-text {
  font-size: 24rpx;
  color: #999;
}
</style>
