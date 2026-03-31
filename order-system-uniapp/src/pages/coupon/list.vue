<template>
  <view class="page">
    <!-- 标签栏 -->
    <view class="coupon-header">
      <view class="tab-bar">
        <view
          class="tab-item"
          :class="{ active: activeTab === 'unused' }"
          @click="switchTab('unused')"
        >
          <text>未使用</text>
        </view>
        <view
          class="tab-item"
          :class="{ active: activeTab === 'used' }"
          @click="switchTab('used')"
        >
          <text>已使用</text>
        </view>
      </view>
      <view class="refresh-btn" @click="handleRefresh">
        <text>🔄</text>
      </view>
    </view>

    <!-- 优惠券列表 -->
    <view class="coupon-list" v-if="filteredCoupons.length > 0">
      <view
        v-for="coupon in filteredCoupons"
        :key="coupon.id"
        class="coupon-item"
        :class="{ disabled: coupon.status !== 'unused' }"
        :style="{ backgroundImage: 'url(' + getCouponImage(coupon.discount) + ')' }"
      >
        <view class="coupon-left">
          <view class="coupon-discount">
            <text class="discount-value">{{ coupon.discount >= 1.0 ? '免' : Math.round((1 - coupon.discount) * 10) }}</text>
            <text class="discount-unit">{{ coupon.discount >= 1.0 ? '单' : '折' }}</text>
          </view>
          <text class="coupon-name">{{ coupon.templateName }}</text>
        </view>
        <view class="coupon-right">
          <text class="coupon-status-text">
            {{ coupon.status === 'unused' ? '待使用' : '已使用' }}
          </text>
          <text class="coupon-time">{{ formatTime(coupon.assignedAt) }}</text>
          <view class="coupon-actions" v-if="coupon.status === 'used'">
            <text class="btn-delete" @click.stop="deleteCoupon(coupon)">删除</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <text class="empty-icon">🎫</text>
      <text class="empty-title">暂无优惠券</text>
      <text class="empty-desc">联系商家领取优惠券</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { get, del } from '../../api/index.js'

const activeTab = ref('unused')
const coupons = ref([])

const filteredCoupons = computed(() => {
  return coupons.value.filter(c => c.status === activeTab.value)
})

async function loadCoupons() {
  try {
    const res = await get('/api/coupons/available')
    if (res.code === 200) {
      coupons.value = res.data || []
    }
  } catch (e) {
    console.error('加载优惠券失败', e)
  }
}

function switchTab(tab) {
  activeTab.value = tab
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  return timeStr.split(' ')[0]
}

function getCouponImage(discount) {
  if (discount >= 1.0) {
    return 'https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%85%8D%E5%8D%95.jpg'
  }
  const discountKey = Math.round((1 - discount) * 10)
  const imageMap = {
    1: 'https://tempduanju.oss-cn-beijing.aliyuncs.com/1%E6%8A%98.jpg',
    5: 'https://tempduanju.oss-cn-beijing.aliyuncs.com/5%E6%8A%98.jpg',
    8: 'https://tempduanju.oss-cn-beijing.aliyuncs.com/8%E6%8A%98.jpg',
    9: 'https://tempduanju.oss-cn-beijing.aliyuncs.com/9%E6%8A%98.jpg'
  }
  return imageMap[discountKey] || imageMap[9]
}

onMounted(() => {
  loadCoupons()
})

onPullDownRefresh(() => {
  loadCoupons().then(() => {
    uni.stopPullDownRefresh()
  })
})

function handleRefresh() {
  loadCoupons()
}

async function deleteCoupon(coupon) {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除该优惠券吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del(`/api/coupons/user_coupons/${coupon.id}`)
          uni.showToast({ title: '已删除', icon: 'success' })
          loadCoupons()
        } catch (e) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    }
  })
}
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #F7F7F7;
}

.tab-bar {
  display: flex;
  gap: 140px;
  background: #FFFFFF;
  padding: 0 16px;
  border-bottom: 1px solid #E5E5E5;
}

.coupon-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 16px;
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

.tab-item {
  flex: 1;
  text-align: center;
  padding: 16px 0;
  font-size: 14px;
  color: #666666;
  position: relative;
}

.tab-item.active {
  color: #C8956C;
  font-weight: 600;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 2px;
  background: #C8956C;
  border-radius: 2px;
}

.coupon-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.coupon-item {
  display: flex;
  width: 100%;
  box-sizing: border-box;
  background: linear-gradient(135deg, #C8956C 0%, #E8C4A8 100%);
  background-size: cover;
  background-position: center;
  border-radius: 10px;
  padding: 16px;
  color: #FFFFFF;
}

.coupon-item.disabled {
  background-color: #CCCCCC;
}

.coupon-left {
  flex: 1;
  color: #000000;
}

.coupon-discount {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.discount-value {
  font-size: 32px;
  font-weight: 700;
  font-family: monospace;
}

.discount-unit {
  font-size: 14px;
}

.coupon-name {
  font-size: 12px;
  opacity: 0.9;
  margin-top: 4px;
  display: block;
}

.coupon-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
}

.coupon-status-text {
  font-size: 12px;
  background: rgba(255,255,255,0.3);
  padding: 2px 8px;
  border-radius: 10px;
}

.coupon-item.disabled .coupon-status-text {
  background: rgba(0,0,0,0.2);
}

.coupon-time {
  font-size: 11px;
  opacity: 0.8;
}

.coupon-actions {
  margin-top: 4px;
}

.btn-delete {
  font-size: 11px;
  color: #F44336;
  background: rgba(255,255,255,0.3);
  padding: 2px 8px;
  border-radius: 8px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100px 16px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 14px;
  color: #666666;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 12px;
  color: #999999;
}
</style>
