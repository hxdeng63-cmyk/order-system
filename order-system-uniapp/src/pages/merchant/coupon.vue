<template>
  <view class="page">
    <!-- 创建优惠券按钮 -->
    <view class="action-bar">
      <view class="btn-create" @click="showCreateModal = true">
        <text>创建优惠券</text>
      </view>
    </view>

    <!-- 优惠券列表 -->
    <view class="coupon-list" v-if="coupons.length > 0">
      <view
        v-for="coupon in coupons"
        :key="coupon.id"
        class="coupon-card"
        :style="{ backgroundImage: 'url(' + getCouponImage(coupon.discount) + ')' }"
      >
        <view class="coupon-header">
          <text class="coupon-name">{{ coupon.templateName }}</text>
          <text class="coupon-status" :class="{ inactive: coupon.status === 0 }">
            {{ coupon.status === 1 ? '进行中' : '已下架' }}
          </text>
        </view>
        <view class="coupon-info">
          <text class="coupon-discount">{{ coupon.discount >= 1.0 ? '免单' : Math.round((1 - coupon.discount) * 10) + '折' }}</text>
          <text class="coupon-remaining">剩余 {{ coupon.remainingCount }} / {{ coupon.totalCount }}</text>
        </view>
        <view class="coupon-actions">
          <view class="btn-grant" @click="showGrantModal(coupon)">
            <text>发放</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <text class="empty-icon">🎫</text>
      <text class="empty-title">暂无优惠券</text>
      <text class="empty-desc">创建优惠券发放给用户</text>
    </view>

    <!-- 创建优惠券弹窗 -->
    <view class="modal" v-if="showCreateModal" @click="showCreateModal = false">
      <view class="modal-content" @click.stop>
        <text class="modal-title">创建优惠券</text>
        <view class="form-item">
          <text class="form-label">优惠券类型</text>
          <picker :value="createForm.templateIndex" :range="templates" range-key="name" @change="onTemplateChange">
            <view class="picker-value">{{ templates[createForm.templateIndex]?.name || '请选择' }}</view>
          </picker>
        </view>
        <view class="form-item">
          <text class="form-label">发放数量</text>
          <input class="form-input" type="number" v-model="createForm.totalCount" placeholder="请输入发放数量" />
        </view>
        <view class="modal-actions">
          <view class="btn-cancel" @click="showCreateModal = false"><text>取消</text></view>
          <view class="btn-confirm" @click="createCoupon"><text>创建</text></view>
        </view>
      </view>
    </view>

    <!-- 发放优惠券弹窗 -->
    <view class="modal" v-if="showGrantModalFlag" @click="showGrantModalFlag = false">
      <view class="modal-content" @click.stop>
        <text class="modal-title">发放优惠券</text>
        <view class="form-item">
          <text class="form-label">用户ID</text>
          <input class="form-input" type="number" v-model="grantForm.userId" placeholder="请输入用户ID" />
        </view>
        <view class="modal-actions">
          <view class="btn-cancel" @click="showGrantModalFlag = false"><text>取消</text></view>
          <view class="btn-confirm" @click="grantCoupon"><text>发放</text></view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { merchantGet, merchantPost } from '../../api/index.js'

const coupons = ref([])
const templates = ref([
  { id: 1, name: '9折券' },
  { id: 2, name: '8折券' },
  { id: 3, name: '5折券' },
  { id: 4, name: '1折券' },
  { id: 5, name: '免单券' }
])
const showCreateModal = ref(false)
const showGrantModalFlag = ref(false)
const selectedCoupon = ref(null)

const createForm = ref({
  templateIndex: 0,
  totalCount: 100
})

const grantForm = ref({
  userId: ''
})

async function loadCoupons() {
  try {
    const res = await merchantGet('/api/coupons/merchant/list')
    if (res.code === 200) {
      coupons.value = res.data || []
    }
  } catch (e) {
    console.error('加载优惠券失败', e)
  }
}

async function loadTemplates() {
  try {
    const res = await merchantGet('/api/coupons/templates')
    if (res.code === 200 && res.data) {
      templates.value = res.data
    }
  } catch (e) {
    console.error('加载优惠券模板失败', e)
  }
}

function onTemplateChange(e) {
  createForm.value.templateIndex = e.detail.value
}

async function createCoupon() {
  const template = templates.value[createForm.value.templateIndex]
  if (!template) {
    uni.showToast({ title: '请选择类型', icon: 'none' })
    return
  }
  if (!createForm.value.totalCount || createForm.value.totalCount <= 0) {
    uni.showToast({ title: '请输入有效数量', icon: 'none' })
    return
  }

  try {
    const res = await merchantPost('/api/coupons/merchant/create', {
      templateId: template.id,
      totalCount: parseInt(createForm.value.totalCount)
    })
    if (res.code === 200) {
      uni.showToast({ title: '创建成功', icon: 'success' })
      showCreateModal.value = false
      loadCoupons()
    } else {
      uni.showToast({ title: res.message || '创建失败', icon: 'none' })
    }
  } catch (e) {
    uni.showToast({ title: '创建失败', icon: 'none' })
  }
}

function showGrantModal(coupon) {
  selectedCoupon.value = coupon
  grantForm.value.userId = ''
  showGrantModalFlag.value = true
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

async function grantCoupon() {
  if (!grantForm.value.userId) {
    uni.showToast({ title: '请输入用户ID', icon: 'none' })
    return
  }

  try {
    const res = await merchantPost('/api/coupons/merchant/grant', {
      userId: parseInt(grantForm.value.userId),
      couponId: selectedCoupon.value.id
    })
    if (res.code === 200) {
      uni.showToast({ title: '发放成功', icon: 'success' })
      showGrantModalFlag.value = false
      loadCoupons()
    } else {
      uni.showToast({ title: res.message || '发放失败', icon: 'none' })
    }
  } catch (e) {
    uni.showToast({ title: '发放失败', icon: 'none' })
  }
}

onMounted(() => {
  loadTemplates()
  loadCoupons()
})

function onPullDownRefresh() {
  loadCoupons().then(() => {
    uni.stopPullDownRefresh()
  })
}
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #F7F7F7;
  padding: 16px;
}

.action-bar {
  margin-bottom: 16px;
}

.btn-create {
  background: #C8956C;
  color: #FFFFFF;
  text-align: center;
  padding: 12px;
  border-radius: 24px;
  font-size: 14px;
}

.coupon-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.coupon-card {
  background: #FFFFFF;
  background-size: cover;
  background-position: center;
  border-radius: 10px;
  padding: 16px;
}

.coupon-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.coupon-name {
  font-size: 15px;
  font-weight: 600;
  color: #333333;
}

.coupon-status {
  font-size: 11px;
  color: #4CAF50;
  background: #E8F5E9;
  padding: 2px 8px;
  border-radius: 10px;
}

.coupon-status.inactive {
  color: #999999;
  background: #F5F5F5;
}

.coupon-info {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 12px;
}

.coupon-discount {
  font-size: 24px;
  font-weight: 700;
  color: #333333;
  font-family: monospace;
}

.coupon-remaining {
  font-size: 12px;
  color: #333333;
}

.coupon-actions {
  display: flex;
  gap: 8px;
}

.btn-grant {
  background: #C8956C;
  color: #FFFFFF;
  padding: 6px 16px;
  border-radius: 16px;
  font-size: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 16px;
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

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-content {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  width: 300px;
}

.modal-title {
  font-size: 16px;
  font-weight: 600;
  display: block;
  text-align: center;
  margin-bottom: 16px;
}

.form-item {
  margin-bottom: 12px;
}

.form-label {
  font-size: 12px;
  color: #666666;
  display: block;
  margin-bottom: 6px;
}

.form-input {
  background: #F7F7F7;
  border-radius: 6px;
  padding: 10px;
  font-size: 14px;
}

.picker-value {
  background: #F7F7F7;
  border-radius: 6px;
  padding: 10px;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  text-align: center;
  padding: 10px;
  border-radius: 20px;
  font-size: 14px;
}

.btn-cancel {
  background: #F5F5F5;
  color: #666666;
}

.btn-confirm {
  background: #C8956C;
  color: #FFFFFF;
}
</style>
