<template>
  <view class="page">
    <!-- 订单状态 Tab -->
    <view class="order-header">
      <view class="order-tabs">
        <view
          v-for="tab in tabs"
          :key="tab.value"
          class="order-tab"
          :class="{ active: store.state.orderFilter === tab.value }"
          @click="store.setOrderFilter(tab.value)"
        >
          <text>{{ tab.label }}</text>
        </view>
      </view>
      <view class="refresh-btn" @click="handleRefresh">
        <text>🔄</text>
      </view>
    </view>

    <!-- 订单列表 -->
    <scroll-view class="order-list" scroll-y v-if="filteredOrders.length > 0">
      <view
        v-for="order in filteredOrders"
        :key="order.id"
        class="order-card"
      >
        <view class="order-card-header">
          <text class="order-id">订单号: {{ order.id }}</text>
          <text class="order-status" :class="order.status">
            {{ statusText[order.status] }}
          </text>
        </view>
        <view class="order-items">
          <view
            v-for="(item, index) in order.items"
            :key="index"
            class="order-item-row"
          >
            <text class="order-item-name">{{ item.name }} x{{ item.qty }}</text>
            <text class="order-item-price">¥{{ item.price }}</text>
          </view>
        </view>
        <view class="order-card-footer">
          <view class="order-footer-left">
            <text class="order-time">{{ order.time }}</text>
          </view>
          <view class="order-footer-right">
            <view class="order-total-wrapper">
              <text class="order-total-label">合计</text>
              <text class="order-total-price">¥{{ order.total }}</text>
            </view>
            <view class="order-btn-group">
              <button
                v-if="order.status === 'pending'"
                class="btn-cancel-order"
                @click="cancelOrderAction(order)"
              >取消</button>
              <button
                v-if="order.status === 'pending'"
                class="btn-pay"
                @click="payOrder(order)"
              >去支付</button>
              <button
                v-if="order.status === 'completed'"
                class="btn-confirm-receipt"
                @click="confirmReceipt(order)"
              >确认取餐</button>
              <button
                v-if="order.status === 'received' || order.status === 'cancelled'"
                class="btn-delete-order"
                @click="deleteOrderAction(order)"
              >删除</button>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <text class="empty-icon">📋</text>
      <text class="empty-title">暂无订单</text>
      <text class="empty-desc">快去下单吧</text>
      <view class="btn-secondary" @click="goHome">
        <text>去点单</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { useStore } from '../../store/index.js'
import { del, put } from '../../api/index.js'

const store = useStore()

const tabs = [
  { value: 'all', label: '全部' },
  { value: 'pending', label: '待支付' },
  { value: 'paid', label: '待接单' },
  { value: 'processing', label: '制作中' },
  { value: 'completed', label: '可取餐' },
  { value: 'received', label: '已取餐' },
]

const statusText = {
  pending: '待支付',
  paid: '待接单',
  processing: '制作中',
  completed: '可取餐',
  received: '已取餐',
  cancelled: '已取消'
}

const filteredOrders = computed(() => {
  if (store.state.orderFilter === 'all') {
    return store.state.orders
  }
  return store.state.orders.filter(o => o.status === store.state.orderFilter)
})

onMounted(() => {
  store.loadOrders()
})

onPullDownRefresh(() => {
  store.loadOrders().then(() => {
    uni.stopPullDownRefresh()
  })
})

async function payOrder(order) {
  await store.payOrder(order.id)
  await store.loadOrders()
}

async function cancelOrderAction(order) {
  await store.cancelOrder(order.id)
  await store.loadOrders()
}

function handleRefresh() {
  store.loadOrders()
}

async function confirmReceipt(order) {
  console.log('【DEBUG】confirmReceipt 点击 - orderId:', order.id, '当前状态:', order.status)
  try {
    const res = await put(`/api/orders/${order.id}/complete`)
    console.log('【DEBUG】API 响应 - code:', res.code, 'message:', res.message)
    if (res.code === 200) {
      console.log('【DEBUG】开始更新本地状态')
      // 更新本地订单状态
      const updatedOrders = store.state.orders.map(o => {
        console.log('【DEBUG】遍历订单 - id:', o.id, 'status:', o.status)
        if (o.id === order.id) {
          console.log('【DEBUG】匹配到订单，更新状态为 received')
          return { ...o, status: 'received' }
        }
        return o
      })
      console.log('【DEBUG】更新后的订单列表:', updatedOrders)
      store.state.orders = updatedOrders
      console.log('【DEBUG】调用 loadOrders 重新加载')
      await store.loadOrders()
      console.log('【DEBUG】loadOrders 完成，当前 filter:', store.state.orderFilter)
    } else {
      console.log('【DEBUG】API 返回错误:', res.message)
      uni.showToast({ title: res.message || '操作失败', icon: 'none' })
    }
  } catch (e) {
    console.log('【DEBUG】catch 错误:', e)
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

async function deleteOrderAction(order) {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除该订单吗？',
    confirmColor: '#F44336',
    success: async (res) => {
      if (res.confirm) {
        try {
          await del(`/api/orders/${order.id}`)
          uni.showToast({ title: '已删除', icon: 'success' })
          await store.loadOrders()
        } catch (e) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    }
  })
}

function goHome() {
  uni.switchTab({ url: '/pages/index/index' })
}
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #FFFFFF;
  padding-bottom: env(safe-area-inset-bottom);
}

.order-tabs {
  display: flex;
  padding: 16px;
  gap: 24px;
  border-bottom: 1px solid #E5E5E5;
}

.order-header {
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

.order-tab {
  font-size: 14px;
  color: #999999;
  padding-bottom: 8px;
  border-bottom: 2px solid transparent;
}

.order-tab.active {
  color: #C8956C;
  border-bottom-color: #C8956C;
  font-weight: 500;
}

.order-list {
  padding: 16px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
  height: calc(100vh - 100px - env(safe-area-inset-bottom));
  box-sizing: border-box;
}

.order-card {
  background: #F7F7F7;
  border-radius: 10px;
  border: 1px solid #E5E5E5;
  overflow: hidden;
  margin-bottom: 16px;
}

.order-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #FFFFFF;
  border-bottom: 1px solid #E5E5E5;
}

.order-id {
  font-size: 12px;
  color: #999999;
}

.order-status {
  font-size: 12px;
  font-weight: 500;
}

.order-status.pending {
  color: #FF9800;
}

.order-status.paid {
  color: #9C27B0;
}

.order-status.processing {
  color: #2196F3;
}

.order-status.completed {
  color: #4CAF50;
}

.order-status.received {
  color: #9E9E9E;
}

.order-status.cancelled {
  color: #9E9E9E;
}

.order-items {
  padding: 12px 16px;
}

.order-item-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 8px;
}

.order-item-name {
  color: #666666;
}

.order-item-price {
  color: #999999;
}

.order-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #FFFFFF;
  border-top: 1px solid #E5E5E5;
}

.order-footer-left {
  flex-shrink: 0;
}

.order-footer-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.order-total-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.order-total-label {
  font-size: 11px;
  color: #999999;
}

.order-total-price {
  font-size: 18px;
  font-weight: 600;
  color: #C8956C;
  font-family: 'DM Mono', monospace;
}

.order-btn-group {
  display: flex;
  gap: 8px;
}

.btn-pay {
  padding: 6px 16px;
  background: #C8956C;
  color: #fff;
  border: none;
  border-radius: 16px;
  font-size: 13px;
}

.btn-cancel-order {
  padding: 6px 16px;
  background: transparent;
  color: #999;
  border: 1px solid #E5E5E5;
  border-radius: 16px;
  font-size: 13px;
}

.btn-delete-order {
  padding: 6px 16px;
  background: #FFEBEE;
  color: #F44336;
  border: none;
  border-radius: 16px;
  font-size: 13px;
}

.btn-confirm-receipt {
  padding: 6px 16px;
  background: #4CAF50;
  color: #fff;
  border: none;
  border-radius: 16px;
  font-size: 13px;
}

.order-time {
  font-size: 11px;
  color: #999999;
}

.order-total {
  font-family: monospace;
  font-size: 14px;
  font-weight: 500;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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
  margin-bottom: 24px;
}

.btn-secondary {
  padding: 8px 24px;
  border: 1px solid #C8956C;
  border-radius: 24px;
  color: #C8956C;
  font-size: 13px;
}
</style>
