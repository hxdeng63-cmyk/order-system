<template>
  <view class="page">
    <!-- 余额卡片 -->
    <view class="balance-card">
      <text class="balance-label">熊熊币余额</text>
      <view class="balance-amount">
        <text class="coin-icon">🪙</text>
        <text class="balance-value">{{ balance }}</text>
      </view>
      <view class="balance-actions">
        <view class="btn-request" @click="goRequest">
          <text>申请熊币</text>
        </view>
      </view>
    </view>

    <!-- 交易记录 -->
    <view class="section">
      <text class="section-title">交易记录</text>
      <view class="transaction-list" v-if="transactions.length > 0">
        <view
          v-for="item in transactions"
          :key="item.id"
          class="transaction-item"
        >
          <view class="trans-left">
            <text class="trans-type">{{ getTypeText(item.type) }}</text>
            <text class="trans-time">{{ formatTime(item.createdAt) }}</text>
          </view>
          <view class="trans-right">
            <text
              class="trans-amount"
              :class="{ positive: item.amount > 0, negative: item.amount < 0 }"
            >
              {{ item.amount > 0 ? '+' : '' }}{{ item.amount }}
            </text>
          </view>
        </view>
      </view>
      <view class="empty-state" v-else>
        <text class="empty-text">暂无交易记录</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get } from '../../api/index.js'

const balance = ref(0)
const transactions = ref([])

async function loadBalance() {
  try {
    const res = await get('/api/coins/balance')
    if (res.code === 200) {
      balance.value = res.data.balance || 0
      transactions.value = res.data.transactions || []
    }
  } catch (e) {
    console.error('加载熊币失败', e)
  }
}

function getTypeText(type) {
  const map = {
    grant: '商家发放',
    spend: '订单消费',
    refund: '退款返还'
  }
  return map[type] || type
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  return timeStr.split(' ')[0]
}

function goRequest() {
  uni.navigateTo({ url: '/pages/coin/request' })
}

onMounted(() => {
  loadBalance()
})
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #F7F7F7;
}

.balance-card {
  background: linear-gradient(135deg, #C8956C 0%, #E8C4A8 100%);
  padding: 24px 16px;
  color: #FFFFFF;
  margin-bottom: 16px;
}

.balance-label {
  font-size: 12px;
  opacity: 0.9;
}

.balance-amount {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0 16px;
}

.coin-icon {
  font-size: 28px;
}

.balance-value {
  font-size: 36px;
  font-weight: 700;
  font-family: monospace;
}

.balance-actions {
  display: flex;
  gap: 12px;
}

.btn-request {
  background: rgba(255,255,255,0.3);
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 13px;
}

.section {
  background: #FFFFFF;
  padding: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 12px;
  display: block;
}

.transaction-list {
  display: flex;
  flex-direction: column;
}

.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #F0F0F0;
}

.transaction-item:last-child {
  border-bottom: none;
}

.trans-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.trans-type {
  font-size: 13px;
  color: #333333;
}

.trans-time {
  font-size: 11px;
  color: #999999;
}

.trans-right {
  display: flex;
  align-items: center;
}

.trans-amount {
  font-size: 15px;
  font-weight: 600;
  font-family: monospace;
}

.trans-amount.positive {
  color: #4CAF50;
}

.trans-amount.negative {
  color: #666666;
}

.empty-state {
  padding: 24px 0;
  text-align: center;
}

.empty-text {
  font-size: 12px;
  color: #999999;
}
</style>
