<template>
  <view class="page">
    <!-- Tab 栏 -->
    <view class="tab-bar">
      <view class="tab-item" :class="{ active: activeTab === 'grant' }" @click="activeTab = 'grant'">
        <text>发放熊币</text>
      </view>
      <view class="tab-item" :class="{ active: activeTab === 'requests' }" @click="switchToRequests">
        <text>用户申请</text>
        <view class="badge" v-if="pendingCount > 0">{{ pendingCount }}</view>
      </view>
    </view>

    <!-- 发放熊币 -->
    <view v-if="activeTab === 'grant'" class="section">
      <view class="form-card">
        <view class="form-item">
          <text class="form-label">用户ID</text>
          <input class="form-input" type="number" v-model="grantForm.userId" placeholder="请输入用户ID" />
        </view>
        <view class="form-item">
          <text class="form-label">发放数量</text>
          <input class="form-input" type="number" v-model="grantForm.amount" placeholder="请输入熊币数量" />
        </view>
        <view class="form-item">
          <text class="form-label">备注</text>
          <input class="form-input" v-model="grantForm.remark" placeholder="选填" />
        </view>
        <view class="btn-submit" @click="grantCoins">
          <text>确认发放</text>
        </view>
      </view>
    </view>

    <!-- 用户申请列表 -->
    <view v-if="activeTab === 'requests'" class="section">
      <view class="request-list" v-if="requests.length > 0">
        <view
          v-for="req in requests"
          :key="req.id"
          class="request-card"
        >
          <view class="request-header">
            <text class="request-user">用户: {{ req.userName }}</text>
            <text class="request-amount">🪙 {{ req.amountRequested }}</text>
          </view>
          <view class="request-message" v-if="req.message">
            <text class="message-label">留言:</text>
            <text class="message-text">{{ req.message }}</text>
          </view>
          <view class="request-time">
            <text>{{ formatTime(req.createdAt) }}</text>
          </view>
          <view class="request-actions" v-if="req.status === 'pending'">
            <view class="btn-reject" @click="handleRequest(req.id, 'rejected')">
              <text>拒绝</text>
            </view>
            <view class="btn-approve" @click="handleRequest(req.id, 'approved')">
              <text>同意</text>
            </view>
          </view>
          <view class="request-status" v-else>
            <text :class="{ approved: req.status === 'approved', rejected: req.status === 'rejected' }">
              {{ req.status === 'approved' ? '已同意' : '已拒绝' }}
            </text>
          </view>
        </view>
      </view>
      <view class="empty-state" v-else>
        <text class="empty-icon">📋</text>
        <text class="empty-title">暂无申请</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { merchantGet, merchantPost, merchantPut } from '../../api/index.js'

const activeTab = ref('grant')
const requests = ref([])
const pendingCount = ref(0)

const grantForm = ref({
  userId: '',
  amount: '',
  remark: ''
})

async function loadRequests() {
  try {
    const res = await merchantGet('/api/coins/requests')
    if (res.code === 200) {
      requests.value = res.data || []
      pendingCount.value = requests.value.filter(r => r.status === 'pending').length
    }
  } catch (e) {
    console.error('加载申请失败', e)
  }
}

function switchToRequests() {
  activeTab.value = 'requests'
  loadRequests()
}

async function grantCoins() {
  if (!grantForm.value.userId) {
    uni.showToast({ title: '请输入用户ID', icon: 'none' })
    return
  }
  if (!grantForm.value.amount || parseFloat(grantForm.value.amount) <= 0) {
    uni.showToast({ title: '请输入有效数量', icon: 'none' })
    return
  }

  try {
    const res = await merchantPost('/api/coins/grant', {
      userId: parseInt(grantForm.value.userId),
      amount: parseFloat(grantForm.value.amount),
      remark: grantForm.value.remark || '商家发放'
    })
    if (res.code === 200) {
      uni.showToast({ title: '发放成功', icon: 'success' })
      grantForm.value = { userId: '', amount: '', remark: '' }
    } else {
      uni.showToast({ title: res.message || '发放失败', icon: 'none' })
    }
  } catch (e) {
    uni.showToast({ title: '发放失败', icon: 'none' })
  }
}

async function handleRequest(id, status) {
  try {
    const res = await merchantPut(`/api/coins/requests/${id}`, { status })
    if (res.code === 200) {
      uni.showToast({ title: status === 'approved' ? '已同意' : '已拒绝', icon: 'success' })
      loadRequests()
    } else {
      uni.showToast({ title: res.message || '操作失败', icon: 'none' })
    }
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  return timeStr.split(' ')[0]
}

onMounted(() => {
  // 默认加载申请列表
  loadRequests()
})
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #F7F7F7;
}

.tab-bar {
  display: flex;
  background: #FFFFFF;
  padding: 0 16px;
  border-bottom: 1px solid #E5E5E5;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 16px 0;
  font-size: 14px;
  color: #666666;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
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

.badge {
  background: #F44336;
  color: #FFFFFF;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
}

.section {
  padding: 16px;
}

.form-card {
  background: #FFFFFF;
  border-radius: 10px;
  padding: 16px;
}

.form-item {
  margin-bottom: 16px;
}

.form-label {
  font-size: 13px;
  color: #666666;
  display: block;
  margin-bottom: 8px;
}

.form-input {
  background: #F7F7F7;
  border-radius: 6px;
  padding: 12px;
  font-size: 14px;
}

.btn-submit {
  background: #C8956C;
  color: #FFFFFF;
  text-align: center;
  padding: 14px;
  border-radius: 24px;
  font-size: 15px;
  margin-top: 8px;
}

.request-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.request-card {
  background: #FFFFFF;
  border-radius: 10px;
  padding: 16px;
}

.request-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.request-user {
  font-size: 14px;
  color: #333333;
  font-weight: 500;
}

.request-amount {
  font-size: 14px;
  color: #C8956C;
  font-weight: 600;
  font-family: monospace;
}

.request-message {
  background: #F7F7F7;
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 8px;
}

.message-label {
  font-size: 12px;
  color: #666666;
}

.message-text {
  font-size: 12px;
  color: #333333;
  margin-left: 4px;
}

.request-time {
  font-size: 11px;
  color: #999999;
  margin-bottom: 12px;
}

.request-actions {
  display: flex;
  gap: 12px;
}

.btn-reject, .btn-approve {
  flex: 1;
  text-align: center;
  padding: 10px;
  border-radius: 20px;
  font-size: 13px;
}

.btn-reject {
  background: #F5F5F5;
  color: #666666;
}

.btn-approve {
  background: #C8956C;
  color: #FFFFFF;
}

.request-status {
  text-align: center;
}

.request-status text {
  font-size: 13px;
}

.request-status text.approved {
  color: #4CAF50;
}

.request-status text.rejected {
  color: #999999;
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
}
</style>
