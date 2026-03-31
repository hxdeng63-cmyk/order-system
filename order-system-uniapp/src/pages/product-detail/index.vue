<template>
  <view class="page">
    <!-- Header -->
    <view class="detail-header">
      <view class="detail-back" @click="goBack">
        <text>←</text>
      </view>
      <text class="detail-title">商品详情</text>
      <view class="detail-favorite" @click="toggleFavorite">
        <text>{{ isFavorited ? '❤️' : '🤍' }}</text>
      </view>
      <view class="detail-dislike" @click="handleDislike">
        <text>{{ isDisliked ? '🚫' : '⚪' }}</text>
      </view>
    </view>

    <!-- 商品图片 -->
    <view class="detail-image">
      <image
        v-if="product?.icon && (product.icon.startsWith('/') || product.icon.includes('://'))"
        :src="product.icon"
        mode="aspectFit"
        class="product-img"
      />
      <text v-else class="product-icon">{{ getIconText(product?.icon) }}</text>
    </view>

    <!-- 商品信息 -->
    <view class="detail-info">
      <view class="detail-price-row">
        <text class="detail-price">¥{{ currentPrice }}</text>
        <text class="detail-original-price" v-if="product?.originalPrice">
          ¥{{ product.originalPrice }}
        </text>
      </view>
      <text class="detail-name">{{ product?.name }}</text>
      <text class="detail-desc">{{ product?.desc }}</text>
    </view>

    <!-- 规格选择 -->
    <view class="detail-section">
      <text class="detail-section-title">规格</text>
      <view class="spec-options">
        <view
          v-for="spec in specs"
          :key="spec.value"
          class="spec-option"
          :class="{ active: store.state.selectedSpec === spec.value }"
          @click="store.setSpec(spec.value)"
        >
          <text>{{ spec.label }}</text>
        </view>
      </view>
    </view>

    <!-- 底部操作 -->
    <view class="detail-footer">
      <view class="detail-cart-info">
        <text class="detail-cart-label">共1件</text>
        <text class="detail-cart-price">¥{{ currentPrice }}</text>
      </view>
      <view class="btn-add-cart" @click="handleAddToCart">
        <text>加入购物车</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useStore } from '../../store/index.js'
import { get, post } from '../../api/index.js'

const store = useStore()
const isFavorited = ref(false)
const isDisliked = ref(false)

const specs = [
  { value: '默认', label: '默认' },
  { value: '大杯', label: '大杯 +3元' },
  { value: '去冰', label: '去冰' },
]

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

const product = computed(() => store.state.selectedProduct)

const currentPrice = computed(() => {
  if (!product.value) return 0
  let price = product.value.price || 0
  if (store.state.selectedSpec === '大杯') {
    price += 3
  }
  return price
})

onMounted(async () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const id = currentPage.options?.id

  if (id) {
    // 尝试从API加载
    try {
      const res = await get(`/api/products/${id}`)
      if (res.code === 200 && res.data) {
        store.selectProduct(res.data)
        store.setSpec('默认')
        // 检查是否已收藏
        await checkFavorite(id)
        // 检查是否已避雷
        await checkDislike(id)
      }
    } catch (e) {
      // 如果API失败，尝试用store中已选中的商品
      if (!product.value) {
        uni.showToast({ title: '商品不存在', icon: 'none' })
        setTimeout(() => uni.navigateBack(), 1000)
      }
    }
  } else if (!product.value) {
    uni.navigateBack()
  }
})

async function checkFavorite(productId) {
  try {
    const res = await get('/api/user/favorites')
    if (res.code === 200) {
      const favorites = res.data || []
      isFavorited.value = favorites.some(f => String(f.productId) === String(productId))
    }
  } catch (e) {
    console.error('检查收藏状态失败', e)
  }
}

async function toggleFavorite() {
  const p = product.value
  if (!p) return

  if (!uni.getStorageSync('token')) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    setTimeout(() => uni.navigateTo({ url: '/pages/login/index' }), 1500)
    return
  }

  const productId = p.id
  try {
    const res = await post(`/api/products/${productId}/favorite`)
    if (res.code === 200) {
      isFavorited.value = res.data.isFavorite
      isDisliked.value = false  // 互斥：收藏则取消避雷
      uni.showToast({ title: res.message, icon: 'success' })
    }
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

async function checkDislike(productId) {
  try {
    const res = await get('/api/user/dislikes')
    if (res.code === 200) {
      const dislikes = res.data || []
      isDisliked.value = dislikes.some(d => String(d.productId) === String(productId))
    }
  } catch (e) {
    console.error('检查避雷状态失败', e)
  }
}

async function handleDislike() {
  const p = product.value
  if (!p) return

  await store.toggleDislike(p)
  isDisliked.value = store.isDisliked(p.id)
  // 同时更新收藏状态（互斥：避雷应取消收藏）
  isFavorited.value = false
}

function goBack() {
  uni.navigateBack()
}

function handleAddToCart() {
  const p = product.value
  if (!p) return

  store.addToCart(p, currentPrice.value)
  setTimeout(() => {
    goBack()
  }, 500)
}
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #FFFFFF;
  padding-bottom: 100px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #FFFFFF;
}

.detail-back,
.detail-favorite,
.detail-dislike {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #F7F7F7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.detail-title {
  font-size: 16px;
  font-weight: 600;
}

.detail-image {
  height: 280px;
  background: #F7F7F7;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #E5E5E5;
}

.product-icon {
  font-size: 80px;
}

.product-img {
  max-width: 100%;
  max-height: 100%;
}

.detail-info {
  padding: 24px;
}

.detail-price-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 12px;
}

.detail-price {
  font-family: monospace;
  font-size: 28px;
  font-weight: 600;
  color: #C8956C;
}

.detail-original-price {
  font-size: 14px;
  color: #999999;
  text-decoration: line-through;
}

.detail-name {
  font-size: 20px;
  font-weight: 600;
  display: block;
  margin-bottom: 8px;
}

.detail-desc {
  font-size: 13px;
  color: #666666;
  line-height: 1.6;
}

.detail-section {
  padding: 16px 24px;
  border-top: 1px solid #E5E5E5;
}

.detail-section-title {
  font-size: 14px;
  font-weight: 500;
  display: block;
  margin-bottom: 12px;
}

.spec-options {
  display: flex;
  gap: 8px;
}

.spec-option {
  padding: 8px 16px;
  background: #F7F7F7;
  border: 1px solid #E5E5E5;
  border-radius: 8px;
  font-size: 12px;
}

.spec-option.active {
  background: #F5EDE6;
  border-color: #C8956C;
  color: #C8956C;
}

.detail-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #FFFFFF;
  border-top: 1px solid #E5E5E5;
  padding: 16px;
  display: flex;
  gap: 16px;
  align-items: center;
}

.detail-cart-info {
  display: flex;
  flex-direction: column;
  min-width: 80px;
}

.detail-cart-label {
  font-size: 10px;
  color: #999999;
}

.detail-cart-price {
  font-family: monospace;
  font-size: 18px;
  font-weight: 600;
  color: #C8956C;
}

.btn-add-cart {
  flex: 1;
  padding: 16px;
  background: #C8956C;
  color: white;
  border-radius: 24px;
  text-align: center;
  font-size: 15px;
  font-weight: 500;
}
</style>
