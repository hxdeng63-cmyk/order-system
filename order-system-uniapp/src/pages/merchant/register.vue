<template>
  <view class="page">
    <view class="register-header">
      <image class="header-image" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20260327195529_139_3.jpg" mode="aspectFill"></image>
      <view class="header-text">
        <text class="register-title">商家注册</text>
        <text class="register-subtitle">创建您的商家账号</text>
      </view>
    </view>

    <view class="register-form">
      <view class="form-item">
        <text class="form-label">姓名</text>
        <input
          class="form-input"
          v-model="form.name"
          placeholder="请输入商家姓名（2-20字符）"
          type="text"
          maxlength="20"
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
import { merchantPost } from '../../api/index.js'

export default {
  data() {
    return {
      loading: false,
      form: {
        name: '',
        password: '',
        confirmPassword: ''
      }
    }
  },
  methods: {
    async handleRegister() {
      if (!this.form.name) {
        uni.showToast({ title: '请输入姓名', icon: 'none' })
        return
      }
      if (this.form.name.length < 2 || this.form.name.length > 20) {
        uni.showToast({ title: '姓名长度必须在2-20字符之间', icon: 'none' })
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
        const res = await merchantPost('/api/merchant/register', {
          name: this.form.name,
          password: this.form.password,
          confirmPassword: this.form.confirmPassword
        })

        if (res.code === 200) {
          uni.setStorageSync('merchant_token', res.data.token)
          uni.setStorageSync('merchant_info', JSON.stringify(res.data.merchant))
          uni.showToast({ title: '注册成功', icon: 'success' })
          setTimeout(() => {
            uni.navigateTo({ url: '/pages/merchant/index' })
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
