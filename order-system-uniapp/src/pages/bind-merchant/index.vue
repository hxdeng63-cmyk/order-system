<template>
  <view class="page">
    <view class="header">
      <text class="title">绑定商家</text>
      <text class="subtitle">输入商家提供的邀请码完成绑定</text>
    </view>

    <!-- 已绑定状态 -->
    <view class="bound-status" v-if="bindStatus.bound">
      <view class="bound-card">
        <text class="bound-label">已绑定商家</text>
        <text class="bound-name">{{ bindStatus.merchantName }}</text>
        <text class="bound-info" v-if="bindStatus.merchantPhone">电话：{{ bindStatus.merchantPhone }}</text>
        <text class="bound-info" v-if="bindStatus.merchantAddress">地址：{{ bindStatus.merchantAddress }}</text>
      </view>
    </view>

    <!-- 未绑定状态 -->
    <view class="bind-form" v-else>
      <view class="form-item">
        <text class="form-label">邀请码</text>
        <input
          class="form-input"
          v-model="inviteCode"
          placeholder="请输入6位邀请码"
          type="number"
          maxlength="6"
        />
      </view>
      <button class="btn-bind" @click="handleBind" :loading="loading">
        <text v-if="!loading">确认绑定</text>
        <text v-else>绑定中...</text>
      </button>
    </view>

    <view class="tips">
      <text class="tips-title">温馨提示</text>
      <text class="tips-text">1. 请向您的商家获取邀请码</text>
      <text class="tips-text">2. 一个用户只能绑定一个商家</text>
      <text class="tips-text">3. 绑定后可在"我的"页面查看商家信息</text>
    </view>
  </view>
</template>

<script>
import { get, post } from '../../api/index.js'

export default {
  data() {
    return {
      loading: false,
      inviteCode: '',
      bindStatus: {
        bound: false,
        merchantId: null,
        merchantName: '',
        merchantPhone: '',
        merchantAddress: ''
      }
    }
  },
  onLoad() {
    this.loadBindStatus()
  },
  methods: {
    async loadBindStatus() {
      const token = uni.getStorageSync('token')
      if (!token) {
        uni.showToast({ title: '请先登录', icon: 'none' })
        setTimeout(() => {
          uni.navigateTo({ url: '/pages/login/index' })
        }, 1500)
        return
      }

      try {
        const res = await get('/api/user/bind-status')
        if (res.code === 200) {
          this.bindStatus = res.data || { bound: false }
        }
      } catch (e) {
        console.error('获取绑定状态失败', e)
      }
    },
    async handleBind() {
      if (!this.inviteCode) {
        uni.showToast({ title: '请输入邀请码', icon: 'none' })
        return
      }
      if (this.inviteCode.length !== 8) {
        uni.showToast({ title: '邀请码为8位字符', icon: 'none' })
        return
      }

      this.loading = true
      try {
        const res = await post('/api/user/bind-merchant', {
          inviteCode: this.inviteCode
        })

        if (res.code === 200) {
          uni.showToast({ title: '绑定成功', icon: 'success' })
          this.bindStatus = {
            bound: true,
            merchantId: res.data.merchantId,
            merchantName: res.data.merchantName
          }
          // 更新全局用户状态
          const userInfo = uni.getStorageSync('user_info')
          if (userInfo) {
            const user = JSON.parse(userInfo)
            user.boundMerchantId = res.data.merchantId
            uni.setStorageSync('user_info', JSON.stringify(user))
          }
        } else {
          uni.showToast({ title: res.message || '绑定失败', icon: 'none' })
        }
      } catch (e) {
        uni.showToast({ title: '绑定失败，请检查网络', icon: 'none' })
      }
      this.loading = false
    }
  }
}
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #F7F7F7;
  padding: 32rpx;
}

.header {
  text-align: center;
  padding: 48rpx 0;
}

.title {
  font-size: 40rpx;
  font-weight: 700;
  color: #1A1A1A;
  display: block;
  margin-bottom: 16rpx;
}

.subtitle {
  font-size: 28rpx;
  color: #999999;
}

.bind-form {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
}

.form-item {
  margin-bottom: 32rpx;
}

.form-label {
  font-size: 28rpx;
  color: #666666;
  display: block;
  margin-bottom: 12rpx;
}

.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  background: #F7F7F7;
  border-radius: 12rpx;
  font-size: 32rpx;
  text-align: center;
  letter-spacing: 8rpx;
  border: 1px solid #E5E5E5;
}

.btn-bind {
  width: 100%;
  height: 88rpx;
  background: #C8956C;
  color: #FFFFFF;
  border: none;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-bind:active {
  opacity: 0.85;
}

.bound-status {
  margin-bottom: 32rpx;
}

.bound-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 48rpx 32rpx;
  text-align: center;
}

.bound-label {
  font-size: 24rpx;
  color: #999999;
  display: block;
  margin-bottom: 16rpx;
}

.bound-name {
  font-size: 36rpx;
  font-weight: 700;
  color: #C8956C;
  display: block;
  margin-bottom: 24rpx;
}

.bound-info {
  font-size: 28rpx;
  color: #666666;
  display: block;
  margin-bottom: 8rpx;
}

.tips {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 32rpx;
}

.tips-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1A1A1A;
  display: block;
  margin-bottom: 16rpx;
}

.tips-text {
  font-size: 24rpx;
  color: #999999;
  display: block;
  margin-bottom: 8rpx;
}
</style>
