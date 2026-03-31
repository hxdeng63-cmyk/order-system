<template>
  <view class="page">
    <view class="cart-header">
      <text class="cart-title">购物车</text>
      <text class="cart-clear" @click="store.clearCart">清空</text>
    </view>

    <!-- 购物车商品列表 -->
    <view class="cart-items" v-if="store.state.cart.length > 0">
      <view
        v-for="item in store.state.cart"
        :key="item.id"
        class="cart-item"
      >
        <view
          class="cart-item-checkbox"
          :class="{ checked: item.checked }"
          @click="store.toggleCartItem(item.id)"
        >
          <text>{{ item.checked ? '✓' : '○' }}</text>
        </view>
        <view class="cart-item-image">
          <image
            v-if="item.icon && (item.icon.startsWith('/') || item.icon.includes('://'))"
            :src="item.icon"
            mode="aspectFill"
            class="item-img"
          />
          <text v-else class="icon">{{ getIconText(item.icon) }}</text>
        </view>
        <view class="cart-item-info">
          <view>
            <text class="cart-item-name">{{ item.name }}</text>
            <text class="cart-item-spec">默认</text>
          </view>
          <view class="cart-item-bottom">
            <text class="cart-item-price">¥{{ item.price }}</text>
            <view class="stepper">
              <view class="stepper-btn" @click="store.updateCartItem(item.id, -1)">
                <text>-</text>
              </view>
              <text class="stepper-num">{{ item.qty }}</text>
              <view class="stepper-btn" @click="store.updateCartItem(item.id, 1)">
                <text>+</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 优惠选择区 -->
      <view class="discount-section">
        <view class="discount-row" @click="showCouponModal">
          <text class="discount-label">优惠券</text>
          <view class="discount-value">
            <text>{{ selectedCoupon ? selectedCoupon.templateName : '未使用' }}</text>
            <text class="arrow">›</text>
          </view>
        </view>

        <view class="discount-row coin-display">
          <text class="discount-label">熊币抵扣</text>
          <text class="coin-balance">可用: {{ store.state.coinBalance }}</text>
        </view>

        <view class="discount-row remark-row">
          <text class="discount-label">备注</text>
          <input
            class="remark-input"
            v-model="orderRemark"
            placeholder="可填写口味要求等"
            placeholder-class="remark-placeholder"
          />
        </view>

        <!-- 优惠明细 -->
        <view class="discount-detail" v-if="selectedCoupon || store.state.coinBalance > 0">
          <view class="detail-row">
            <text>原价</text>
            <text>¥{{ store.cartTotal.value }}</text>
          </view>
          <view class="detail-row" v-if="couponDiscount > 0">
            <text>优惠券</text>
            <text class="discount-text">-¥{{ couponDiscount }}</text>
          </view>
          <view class="detail-row" v-if="store.state.coinBalance > 0">
            <text>熊币抵扣</text>
            <text class="discount-text">-¥{{ coinDeductDisplay }}</text>
          </view>
          <view class="detail-row final">
            <text>实付</text>
            <text class="final-price">¥{{ finalTotal }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <text class="empty-icon">🛒</text>
      <text class="empty-title">购物车空空如也</text>
      <text class="empty-desc">快去添加喜欢的商品吧</text>
      <view class="btn-secondary" @click="goHome">
        <text>去逛逛</text>
      </view>
    </view>

    <!-- 底部结算栏 -->
    <view class="cart-footer" v-if="store.state.cart.length > 0">
      <view class="cart-total">
        <text class="cart-total-label">合计</text>
        <text class="cart-total-price">¥{{ finalTotal }}</text>
      </view>
      <view
        class="btn-checkout"
        :class="{ disabled: store.checkedCartCount.value === 0 }"
        @click="doCheckout"
      >
        <text>去结算 ({{ store.checkedCartCount.value }})</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from '../../store/index.js'

const store = useStore()

const selectedCoupon = ref(null)
const orderRemark = ref('')

const iconMap = {
  'cup': '🧋',
  'milk': '🥛',
  'headphones': '🍹',
  'gift': '🥤',
  'flag': '🍎',
  'star': '🍰',
  'hand-up': '🍱',
  'apple': '🍎',
  'cake': '🍰',
  'utensils': '🍱',
}

function getIconText(name) {
  return iconMap[name] || '📦'
}

// 计算优惠券折扣
const couponDiscount = computed(() => {
  if (!selectedCoupon.value) return 0
  const total = store.cartTotal.value
  return Math.min(total * selectedCoupon.value.discount, total)
})

// 计算最终金额（熊币自动全额抵扣）
const finalTotal = computed(() => {
  const total = store.cartTotal.value
  const afterCoupon = total - couponDiscount.value
  const coinDeduct = Math.min(store.state.coinBalance, afterCoupon)
  return Math.max(0, afterCoupon - coinDeduct).toFixed(2)
})

// 熊币抵扣显示
const coinDeductDisplay = computed(() => {
  const total = store.cartTotal.value
  const afterCoupon = total - couponDiscount.value
  return Math.min(store.state.coinBalance, afterCoupon).toFixed(2)
})

function showCouponModal() {
  const coupons = store.state.availableCoupons
  if (coupons.length === 0) {
    uni.showToast({ title: '暂无可用优惠券', icon: 'none' })
    return
  }
  const items = ['不使用优惠券', ...coupons.map(c => c.templateName)]
  uni.showActionSheet({
    itemList: items,
    success: (res) => {
      if (res.tapIndex === 0) {
        selectedCoupon.value = null
      } else {
        selectedCoupon.value = coupons[res.tapIndex - 1]
      }
    }
  })
}

function doCheckout() {
  const couponId = selectedCoupon.value ? selectedCoupon.value.id : null
  // 熊币自动使用（不超过折后价）
  const afterCoupon = store.cartTotal.value - couponDiscount.value
  const coins = Math.min(store.state.coinBalance, afterCoupon)
  store.checkout(couponId, coins, orderRemark.value)
}

onMounted(() => {
  store.syncCart()
  store.loadCoupons()
  store.loadCoinBalance()
})

function goHome() {
  uni.switchTab({ url: '/pages/index/index' })
}
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #FFFFFF;
  padding-bottom: 120px;
}

.cart-header {
  padding: 24px 16px 16px;
  border-bottom: 1px solid #E5E5E5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cart-title {
  font-size: 20px;
  font-weight: 700;
}

.cart-clear {
  font-size: 12px;
  color: #F44336;
}

.cart-items {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cart-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #F7F7F7;
  border-radius: 10px;
  border: 1px solid #E5E5E5;
}

.cart-item-checkbox {
  display: flex;
  align-items: center;
  color: #999999;
  font-size: 20px;
}

.cart-item-checkbox.checked {
  color: #C8956C;
}

.cart-item-image {
  width: 70px;
  height: 70px;
  min-width: 70px;
  background: #FFFFFF;
  border-radius: 6px;
  border: 1px solid #E5E5E5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon {
  font-size: 24px;
}

.cart-item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.cart-item-name {
  font-size: 14px;
  font-weight: 500;
  display: block;
}

.cart-item-spec {
  font-size: 11px;
  color: #999999;
  display: block;
}

.cart-item-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cart-item-price {
  font-family: monospace;
  font-size: 14px;
  font-weight: 500;
  color: #C8956C;
}

.stepper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stepper-btn {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid #E5E5E5;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #666666;
}

.stepper-num {
  font-size: 14px;
  font-weight: 500;
  min-width: 24px;
  text-align: center;
}

.discount-section {
  background: #FFF9F5;
  border: 1px solid #E8C4A8;
  border-radius: 10px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.discount-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.discount-label {
  font-size: 13px;
  color: #666666;
}

.discount-value {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #C8956C;
}

.arrow {
  font-size: 16px;
  color: #C8956C;
}

.coin-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.coin-input {
  background: #FFFFFF;
  border: 1px solid #E5E5E5;
  border-radius: 6px;
  padding: 4px 10px;
  width: 70px;
  font-size: 13px;
  text-align: right;
}

.coin-balance {
  font-size: 12px;
  color: #999999;
}

.remark-row {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.remark-input {
  width: 100%;
  background: #FFFFFF;
  border: 1px solid #E5E5E5;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 13px;
  color: #333333;
}

.remark-placeholder {
  color: #CCCCCC;
}

.coin-display {
  flex-direction: row;
  justify-content: space-between;
}

.item-img {
  width: 70px;
  height: 70px;
  border-radius: 6px;
}

.discount-detail {
  background: #FFFFFF;
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666666;
}

.detail-row.final {
  padding-top: 8px;
  border-top: 1px dashed #E5E5E5;
  font-weight: 600;
  color: #333333;
}

.discount-text {
  color: #4CAF50;
}

.final-price {
  color: #C8956C;
  font-size: 15px;
  font-weight: 700;
  font-family: monospace;
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

.cart-footer {
  position: fixed;
  bottom: 50px;
  left: 0;
  right: 0;
  background: #FFFFFF;
  border-top: 1px solid #E5E5E5;
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 999;
}

.cart-total {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  gap: 4px;
}

.cart-total-label {
  font-size: 12px;
  color: #999999;
}

.cart-total-price {
  font-family: monospace;
  font-size: 16px;
  font-weight: 600;
  color: #C8956C;
}

.btn-checkout {
  padding: 8px 20px;
  background: #C8956C;
  color: white;
  border-radius: 20px;
  font-size: 13px;
}

.btn-checkout.disabled {
  background: #CCCCCC;
}
</style>
