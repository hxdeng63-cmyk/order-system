<template>
  <view class="page">
    <view class="category-container">
      <!-- 左侧分类列表 -->
      <scroll-view class="category-left" scroll-y>
        <view
          v-for="category in categories"
          :key="category.id"
          class="category-left-item"
          :class="{ active: store.state.currentCategory === category.id }"
          @click="store.selectCategory(category.id)"
        >
          <text>{{ category.name }}</text>
        </view>
      </scroll-view>

      <!-- 右侧商品列表 -->
      <scroll-view class="category-right" scroll-y>
        <view class="category-header">
          <text class="category-title">{{ currentCategoryName }}</text>
        </view>
        <view class="product-list">
          <view
            v-for="product in visibleProducts"
            :key="product.id"
            class="list-product-item"
            @click="openDetail(product)"
          >
            <view class="list-product-image">
              <image v-if="product.icon && (product.icon.startsWith('/') || product.icon.includes('://'))" :src="product.icon" mode="aspectFill" class="list-product-img" />
              <text v-else class="icon">{{ getIconText(product.icon) }}</text>
            </view>
            <view class="list-product-info">
              <text class="list-product-name">{{ product.name }}</text>
              <text class="list-product-desc">{{ product.desc }}</text>
              <view class="list-product-bottom">
                <text class="product-price">¥{{ product.price }}</text>
                <view class="btn-add" @click.stop="quickAddToCart(product)">
                  <text>+</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useStore } from '../../store/index.js'
import { get } from '../../api/index.js'
import { mockCategories, mockProducts } from '../../api/mock.js'

const store = useStore()
const categories = ref(mockCategories)
const allProducts = ref(mockProducts)

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

async function loadCategories() {
  try {
    const res = await get('/api/categories')
    if (res.code === 200 && res.data) {
      categories.value = res.data
      if (res.data.length > 0 && !store.state.currentCategory) {
        store.selectCategory(res.data[0].id)
      }
    }
  } catch (e) {
    console.error('加载分类失败', e)
  }
}

async function loadProductsByCategory(categoryId) {
  try {
    const res = await get(`/api/products?categoryId=${categoryId}`)
    if (res.code === 200 && res.data) {
      allProducts.value = res.data
    }
  } catch (e) {
    console.error('加载商品失败', e)
  }
}

onMounted(async () => {
  await loadCategories()
  await loadProductsByCategory(store.state.currentCategory)
})

watch(() => store.state.currentCategory, (newId) => {
  loadProductsByCategory(newId)
})

const currentCategoryName = computed(() => {
  const category = categories.value.find(c => c.id === store.state.currentCategory)
  return category?.name || ''
})

const currentProducts = computed(() => {
  return allProducts.value.filter(p => p.categoryId === store.state.currentCategory)
})

// 过滤掉已避雷的商品
const visibleProducts = computed(() => {
  return currentProducts.value.filter(p => !store.isDisliked(p.id))
})

function openDetail(product) {
  store.selectProduct(product)
  uni.navigateTo({ url: `/pages/product-detail/index?id=${product.id}` })
}

function quickAddToCart(product) {
  store.addToCart(product)
}
</script>

<style scoped lang="scss">
.page {
  height: 100vh;
  background: #FFFFFF;
  padding-bottom: env(safe-area-inset-bottom);
}

.category-container {
  display: flex;
  height: 100%;
}

.category-left {
  width: 90px;
  min-width: 90px;
  background: #F7F7F7;
  border-right: 1px solid #E5E5E5;
}

.category-left-item {
  padding: 16px 8px;
  text-align: center;
  font-size: 12px;
  color: #666666;
  border-left: 3px solid transparent;
}

.category-left-item.active {
  background: #FFFFFF;
  color: #C8956C;
  border-left-color: #C8956C;
  font-weight: 500;
}

.category-right {
  flex: 1;
  padding: 16px;
}

.category-header {
  margin-bottom: 16px;
}

.category-title {
  font-size: 16px;
  font-weight: 600;
}

.product-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.list-product-item {
  display: flex;
  gap: 16px;
  padding: 8px;
  background: #F7F7F7;
  border-radius: 10px;
  border: 1px solid #E5E5E5;
}

.list-product-image {
  width: 80px;
  height: 80px;
  min-width: 80px;
  background: #FFFFFF;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #E5E5E5;
}

.icon {
  font-size: 28px;
}

.list-product-img {
  width: 100%;
  height: 100%;
  border-radius: 6px;
}

.list-product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.list-product-name {
  font-size: 14px;
  font-weight: 500;
}

.list-product-desc {
  font-size: 11px;
  color: #999999;
}

.list-product-bottom {
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
