<template>
  <view class="page">
    <view class="register-header">
      <image class="header-image" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20260327195529_139_3.jpg" mode="aspectFill"></image>
      <view class="header-text">
        <text class="register-title">用户注册</text>
        <text class="register-subtitle">创建您的账号</text>
      </view>
    </view>

    <view class="register-form">
      <view class="form-item">
        <text class="form-label">商家邀请码</text>
        <input
          class="form-input"
          v-model="form.inviteCode"
          placeholder="请输入8位邀请码"
          type="text"
          maxlength="8"
        />
      </view>
      <view class="form-item">
        <text class="form-label">电话号码</text>
        <input
          class="form-input"
          v-model="form.phone"
          placeholder="请输入11位手机号"
          type="number"
          maxlength="11"
        />
      </view>
      <view class="form-item">
        <text class="form-label">密码</text>
        <input
          class="form-input"
          v-model="form.password"
          placeholder="请输入密码（6-20字符）"
          password
          maxlength="20"
        />
      </view>
      <view class="form-item">
        <text class="form-label">确认密码</text>
        <input
          class="form-input"
          v-model="form.confirmPassword"
          placeholder="请再次输入密码"
          password
          maxlength="20"
        />
      </view>
      <button class="btn-register" @click="handleRegister" :loading="loading">
        <text v-if="!loading">注册</text>
        <text v-else>注册中...</text>
      </button>
      <view class="form-footer">
        <text class="link-text" @click="goLogin">已有账号？去登录</text>
      </view>
    </view>
  </view>
</template>

<script>
import { post } from '../../api/index.js'

export default {
  data() {
    return {
      loading: false,
      form: {
        inviteCode: '',
        phone: '',
        password: '',
        confirmPassword: ''
      }
    }
  },
  methods: {
    async handleRegister() {
      if (!this.form.inviteCode) {
        uni.showToast({ title: '请输入商家邀请码', icon: 'none' })
        return
      }
      if (this.form.inviteCode.length !== 8) {
        uni.showToast({ title: '邀请码为8位字符', icon: 'none' })
        return
      }
      if (!this.form.phone) {
        uni.showToast({ title: '请输入手机号', icon: 'none' })
        return
      }
      if (this.form.phone.length !== 11 || !/^\d+$/.test(this.form.phone)) {
        uni.showToast({ title: '请输入正确的11位手机号', icon: 'none' })
        return
      }
      if (!this.form.password) {
        uni.showToast({ title: '请输入密码', icon: 'none' })
        return
      }
      if (this.form.password.length < 6 || this.form.password.length > 20) {
        uni.showToast({ title: '密码长度必须在6-20字符之间', icon: 'none' })
        return
      }
      if (this.form.password !== this.form.confirmPassword) {
        uni.showToast({ title: '两次密码输入不一致', icon: 'none' })
        return
      }

      this.loading = true
      try {
        const res = await post('/api/auth/register', {
          phone: this.form.phone,
          password: this.form.password,
          confirmPassword: this.form.confirmPassword,
          inviteCode: this.form.inviteCode || undefined
        })

        if (res.code === 200) {
          uni.setStorageSync('token', res.data.token)
          uni.setStorageSync('user_info', JSON.stringify(res.data.user))
          // 更新全局用户状态
          const app = getApp()
          if (app.globalData) {
            app.globalData.user = res.data.user
          }
          uni.showToast({ title: '注册成功', icon: 'success' })
          setTimeout(() => {
            uni.switchTab({ url: '/pages/profile/index' })
          }, 1000)
        } else {
          uni.showToast({ title: res.message || '注册失败', icon: 'none' })
        }
      } catch (e) {
        uni.showToast({ title: e.message || '注册失败，请检查网络', icon: 'none' })
      }
      this.loading = false
    },
    goLogin() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #FFFFFF;
}

.register-header {
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

.register-title {
  font-size: 40rpx;
  font-weight: 700;
  display: block;
  margin-bottom: 12rpx;
}

.register-subtitle {
  font-size: 28rpx;
  opacity: 0.85;
}

.register-form {
  padding: 48rpx 32rpx 32rpx;
}

.form-item {
  margin-bottom: 32rpx;
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

.btn-register {
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

.btn-register:active {
  opacity: 0.85;
}

.form-footer {
  margin-top: 32rpx;
  text-align: center;
}

.link-text {
  font-size: 26rpx;
  color: #C8956C;
}
</style>
