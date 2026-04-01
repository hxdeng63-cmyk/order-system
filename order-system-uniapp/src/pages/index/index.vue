<template>
  <view class="page">
    <!-- 商家选择栏 -->
    <view class="merchant-selector" @click="goToMerchantList">
      <text class="merchant-label">当前商家：</text>
      <text class="merchant-name">{{ currentMerchantName || '请选择商家' }}</text>
      <text class="merchant-arrow">›</text>
    </view>

    <!-- 搜索栏 -->
    <view class="home-header">
      <view class="search-bar" @click="showToast('搜索功能开发中')">
        <text class="iconfont icon-search">🔍</text>
        <input type="text" placeholder="搜索商品" disabled />
      </view>
      <view class="refresh-btn" @click="handleRefresh">
        <text>🔄</text>
      </view>
    </view>

    <!-- Banner -->
    <view class="banner-section">
      <image
        class="banner-img"
        src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%AE%A2%E6%88%B7%E7%AB%AF_banner%E5%9B%BE.jpg"
        mode="aspectFill"
      />
      <view class="banner-overlay">
        <view class="banner-top">
          <text class="banner-title">{{ banners[0]?.title }}</text>
          <view class="coin-balance" @click="goToCoin">
            <text class="coin-icon">🪙</text>
            <text class="coin-amount">{{ coinBalance }}</text>
          </view>
        </view>
        <text class="banner-subtitle">{{ banners[0]?.subtitle }}</text>
      </view>
    </view>

    <!-- 分类入口 -->
    <view class="section-header">
      <text class="section-title">分类</text>
      <view class="section-more" @click="switchTab('category')">
        <text>更多</text>
        <text class="icon">›</text>
      </view>
    </view>

    <scroll-view class="categories-scroll" scroll-x>
      <view
        v-for="category in categories"
        :key="category.id"
        class="category-item"
        @click="goToCategory(category.id)"
      >
        <view class="category-icon">
          <text class="iconfont">{{ getIconText(category.icon) }}</text>
        </view>
        <text class="category-name">{{ category.name }}</text>
      </view>
    </scroll-view>

    <!-- 热门推荐 -->
    <view class="section-header">
      <text class="section-title">热门推荐</text>
      <view class="section-more">
        <text>更多</text>
        <text class="icon">›</text>
      </view>
    </view>

    <view class="products-grid">
      <view
        v-for="product in visibleProducts"
        :key="product.id"
        class="product-card"
        @click="openDetail(product)"
      >
        <view class="product-image">
          <image v-if="product.icon && (product.icon.startsWith('/') || product.icon.includes('://'))" :src="product.icon" mode="aspectFill" class="product-img" />
          <text v-else class="product-icon">{{ getIconText(product.icon) }}</text>
          <view v-if="product.tag" class="tag">{{ product.tag }}</view>
        </view>
        <view class="product-info">
          <text class="product-name">{{ product.name }}</text>
          <text class="product-desc">{{ product.desc }}</text>
          <view class="product-footer">
            <text class="product-price">¥{{ product.price }}</text>
            <view class="btn-add" @click.stop="quickAddToCart(product)">
              <text>+</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { useStore } from '../../store/index.js'
import { get } from '../../api/index.js'
import { mockCategories, mockProducts, mockBanners } from '../../api/mock.js'

const store = useStore()

const categories = ref(mockCategories)
const banners = ref(mockBanners)
const recommendedProducts = ref(mockProducts.slice(0, 4))
const loading = ref(false)
const coinBalance = ref(0)
const currentMerchantName = ref('')
const currentMerchantId = ref(null)

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

async function loadData() {
  loading.value = true
  try {
    // 加载分类
    const catRes = await get('/api/categories')
    if (catRes.code === 200 && catRes.data) {
      categories.value = catRes.data
      if (catRes.data.length > 0) {
        store.selectCategory(catRes.data[0].id)
      }
    }

    // 获取当前选中的商家
    const currentMerchantId = uni.getStorageSync('current_merchant_id')
    
    // 加载商品（如果选了商家则按商家筛选）
    let prodUrl = '/api/products?limit=50'
    if (currentMerchantId) {
      prodUrl += `&merchantId=${currentMerchantId}`
    }
    const prodRes = await get(prodUrl)
    if (prodRes.code === 200 && prodRes.data) {
      recommendedProducts.value = prodRes.data.slice(0, 4)
      store.state.products = prodRes.data
    }

    // 加载熊币余额
    loadCoinBalance()
  } catch (e) {
    console.error('加载数据失败', e)
  }
  loading.value = false
}

async function loadCoinBalance() {
  const token = uni.getStorageSync('token')
  if (!token) return
  try {
    const res = await get('/api/coins/balance')
    if (res.code === 200 && res.data) {
      coinBalance.value = res.data.balance || 0
    }
  } catch (e) {
    // ignore
  }
}

function goToCoin() {
  uni.navigateTo({ url: '/pages/coin/index' })
}

onMounted(() => {
  loadCurrentMerchant()
  loadData()
})

onPullDownRefresh(() => {
  loadData().then(() => {
    uni.stopPullDownRefresh()
  })
})

function showToast(message) {
  uni.showToast({
    title: message,
    icon: 'none'
  })
}

function loadCurrentMerchant() {
  const name = uni.getStorageSync('current_merchant_name')
  const id = uni.getStorageSync('current_merchant_id')
  if (name) {
    currentMerchantName.value = name
    currentMerchantId.value = id
  }
}

function goToMerchantList() {
  uni.navigateTo({ url: '/pages/merchants/index' })
}

function handleRefresh() {
  loadData()
}

function switchTab(page) {
  uni.switchTab({ url: `/pages/${page}/index` })
}

function goToCategory(id) {
  store.selectCategory(id)
  uni.switchTab({ url: '/pages/category/index' })
}

function openDetail(product) {
  store.selectProduct(product)
  uni.navigateTo({ url: `/pages/product-detail/index?id=${product.id}` })
}

function quickAddToCart(product) {
  store.addToCart(product)
}

// 过滤掉已避雷的商品
const visibleProducts = computed(() => {
  return recommendedProducts.value.filter(p => !store.isDisliked(p.id))
})
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #FFFFFF;
  padding-bottom: 20px;
}

.merchant-selector {
  display: flex;
  align-items: center;
  padding: 16rpx 32rpx;
  background: linear-gradient(135deg, #C8956C 0%, #D4A574 100%);
  color: #FFFFFF;
}

.merchant-label {
  font-size: 24rpx;
  opacity: 0.9;
}

.merchant-name {
  flex: 1;
  font-size: 28rpx;
  font-weight: 600;
}

.merchant-arrow {
  font-size: 32rpx;
  opacity: 0.8;
}

.home-header {
  padding: 16px;
  position: sticky;
  top: 0;
  background: #FFFFFF;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 12px;
}

.refresh-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F7F7F7;
  border-radius: 50%;
  font-size: 18px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #F7F7F7;
  border-radius: 24px;
  padding: 8px 16px;
  border: 1px solid #E5E5E5;
}

.search-bar input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
}

.banner-section {
  padding: 0 16px 16px;
  position: relative;
}

.banner-img {
  width: 100%;
  height: 140px;
  border-radius: 16px;
  display: block;
}

.banner-overlay {
  position: absolute;
  top: 16px;
  left: 16px;
  right: 16px;
  height: 140px;
  overflow: hidden;
  border-radius: 12px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #FFFFFF;
}

.banner-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.banner-title {
  font-size: 20px;
  font-weight: 600;
  color: #FFFFFF;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.coin-balance {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255,255,255,0.25);
  padding: 4px 10px;
  border-radius: 12px;
}

.coin-icon {
  font-size: 16px;
}

.coin-amount {
  font-size: 14px;
  font-weight: 600;
  font-family: monospace;
  color: #333333;
}

.banner-subtitle {
  font-size: 12px;
  color: #FFFFFF;
  opacity: 0.9;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px 8px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
}

.section-more {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999999;
}

.categories-scroll {
  display: flex;
  gap: 16px;
  padding: 0 16px;
  white-space: nowrap;
}

.category-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  min-width: max-content;
}

.category-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #F7F7F7;
  border: 1.5px solid #E5E5E5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.category-name {
  font-size: 13px;
  color: #666666;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 16px;
}

.product-card {
  background: #F7F7F7;
  border-radius: 16px;
  border: 1px solid #E5E5E5;
  overflow: hidden;
}

.product-image {
  aspect-ratio: 1;
  background: #FFFFFF;
  border-bottom: 1px solid #E5E5E5;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.product-icon {
  font-size: 48px;
}

.product-img {
  width: 100%;
  height: 100%;
  border-radius: 16px;
}

.tag {
  position: absolute;
  top: 8px;
  left: 8px;
  background: #C8956C;
  color: white;
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 4px;
}

.product-info {
  padding: 8px 8px 16px;
}

.product-name {
  font-size: 13px;
  font-weight: 500;
  display: block;
  margin-bottom: 4px;
}

.product-desc {
  font-size: 11px;
  color: #999999;
  display: block;
  margin-bottom: 8px;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-price {
  font-family: monospace;
  font-size: 14px;
  font-weight: 500;
  color: #C8956C;
}

.btn-add {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #C8956C;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}
</style>
