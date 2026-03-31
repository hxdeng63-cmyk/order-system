<template>
  <view class="page">
    <!-- 空状态 -->
    <view class="empty-state" v-if="favorites.length === 0">
      <text class="empty-icon">❤️</text>
      <text class="empty-text">暂无收藏</text>
      <view class="empty-btn" @click="goShopping">
        <text>去逛逛</text>
      </view>
    </view>

    <!-- 商品列表 -->
    <view class="product-grid" v-else>
      <view
        v-for="item in favorites"
        :key="item.id || item.productId"
        class="product-card"
        @click="openDetail(item)"
      >
        <view class="product-image">
          <image
            v-if="item.icon && (item.icon.startsWith('/') || item.icon.includes('://'))"
            :src="item.icon"
            mode="aspectFill"
            class="product-img"
          />
          <text v-else class="product-icon">{{ getIconText(item.icon) }}</text>
        </view>
        <view class="product-info">
          <text class="product-name">{{ item.name }}</text>
          <text class="product-price">¥{{ item.price }}</text>
        </view>
        <view class="delete-btn" @click.stop="removeFavorite(item)">
          <text>删除</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from '../../store/index.js'
import { get, post } from '../../api/index.js'

const store = useStore()
const favorites = ref([])

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

onMounted(async () => {
  await loadFavorites()
})

async function loadFavorites() {
  try {
    const res = await get('/api/user/favorites')
    if (res.code === 200) {
      favorites.value = res.data || []
    }
  } catch (e) {
    console.error('加载收藏失败', e)
  }
}

function openDetail(item) {
  store.selectProduct(item)
  uni.navigateTo({ url: `/pages/product-detail/index?id=${item.productId || item.id}` })
}

async function removeFavorite(item) {
  try {
    const res = await uni.request({
      url: `/api/products/${item.productId || item.id}/favorite`,
      method: 'POST',
      header: {
        'Authorization': `Bearer ${uni.getStorageSync('token')}`
      }
    })
    if (res.data.code === 200) {
      favorites.value = favorites.value.filter(f => (f.productId || f.id) !== (item.productId || item.id))
      uni.showToast({ title: '已取消收藏', icon: 'success' })
    }
  } catch (e) {
    uni.showToast({ title: '删除失败', icon: 'none' })
  }
}

function goShopping() {
  uni.switchTab({ url: '/pages/index/index' })
}
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #F7F7F7;
  padding: 16px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-top: 120px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 14px;
  color: #999999;
  margin-bottom: 24px;
}

.empty-btn {
  padding: 12px 32px;
  background: #C8956C;
  color: white;
  border-radius: 24px;
  font-size: 14px;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.product-card {
  background: #FFFFFF;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #E5E5E5;
  position: relative;
}

.product-image {
  height: 140px;
  background: #F7F7F7;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-img {
  width: 100%;
  height: 100%;
}

.product-icon {
  font-size: 48px;
}

.product-info {
  padding: 12px;
}

.product-name {
  font-size: 13px;
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-price {
  font-family: monospace;
  font-size: 15px;
  font-weight: 600;
  color: #C8956C;
}

.delete-btn {
  position: absolute;
  right: 8px;
  top: 8px;
  padding: 4px 12px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border-radius: 12px;
  font-size: 11px;
}
</style>
