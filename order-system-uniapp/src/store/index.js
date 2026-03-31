/**
 * 全局状态管理
 * 使用 Vue 3 Composition API + 真实API
 */

import { reactive, computed } from 'vue'
import { get, post, put, del } from '../api/index.js'

// 全局状态
const state = reactive({
  // 购物车
  cart: [],

  // 订单
  orders: [],

  // 商品列表（缓存）
  products: [],

  // 分类列表（缓存）
  categories: [],

  // 商品详情
  selectedProduct: null,
  selectedSpec: '默认',

  // 订单筛选
  orderFilter: 'all',

  // 当前分类
  currentCategory: 1,

  // 用户信息
  user: null,
  isLoggedIn: false,

  // Toast 消息
  toastMessage: '',
  toastVisible: false,

  // 优惠券和熊币
  availableCoupons: [],
  coinBalance: 0,

  // 收藏列表
  favorites: [],

  // 避雷列表
  dislikes: [],
})

// 计算属性
const cartCount = computed(() => {
  return state.cart.reduce((sum, item) => sum + item.qty, 0)
})

const cartTotal = computed(() => {
  return state.cart.filter(i => i.checked).reduce((sum, item) => sum + item.price * item.qty, 0)
})

const checkedCartItems = computed(() => {
  return state.cart.filter(i => i.checked)
})

const checkedCartCount = computed(() => {
  return checkedCartItems.value.reduce((sum, item) => sum + item.qty, 0)
})

// ========== 分类相关 ==========
async function loadCategories() {
  try {
    const res = await get('/api/categories')
    if (res.code === 200) {
      state.categories = res.data || []
    }
  } catch (e) {
    console.error('加载分类失败', e)
  }
}

// ========== 商品相关 ==========
async function loadProducts(categoryId = null) {
  try {
    const params = categoryId ? `?categoryId=${categoryId}` : ''
    const res = await get(`/api/products${params}`)
    if (res.code === 200) {
      state.products = res.data || []
    }
  } catch (e) {
    console.error('加载商品失败', e)
  }
}

async function loadProductDetail(id) {
  try {
    const res = await get(`/api/products/${id}`)
    if (res.code === 200) {
      state.selectedProduct = res.data
    }
    return res.data
  } catch (e) {
    console.error('加载商品详情失败', e)
    return null
  }
}

// ========== 购物车相关 ==========
// 本地购物车持久化
function saveLocalCart() {
  uni.setStorageSync('local_cart', JSON.stringify(state.cart))
}

function loadLocalCart() {
  try {
    const saved = uni.getStorageSync('local_cart')
    if (saved) {
      state.cart = JSON.parse(saved)
    }
  } catch (e) {
    state.cart = []
  }
}

function isUserLoggedIn() {
  return !!uni.getStorageSync('token')
}

async function syncCart() {
  // 未登录时使用本地购物车
  if (!isUserLoggedIn()) {
    loadLocalCart()
    return
  }
  try {
    const res = await get('/api/cart')
    if (res.code === 200 && res.data) {
      state.cart = res.data.items || []
      saveLocalCart()
    }
  } catch (e) {
    // API失败时使用本地购物车
    loadLocalCart()
    console.error('同步购物车失败，使用本地数据', e)
  }
}

async function addToCart(product, price = null) {
  const actualPrice = price || product.price

  // 已登录用户调用API
  if (isUserLoggedIn()) {
    try {
      await post('/api/cart/items', {
        productId: product.id,
        qty: 1,
        spec: state.selectedSpec || '默认',
        price: actualPrice
      })
      await syncCart()
      showToast('已加入购物车')
      return
    } catch (e) {
      // API失败则使用本地购物车
      console.error('API添加购物车失败，使用本地', e)
    }
  }

  // 本地购物车逻辑
  const existingItem = state.cart.find(item => item.productId === product.id)
  if (existingItem) {
    existingItem.qty += 1
  } else {
    state.cart.push({
      id: Date.now(),
      productId: product.id,
      name: product.name,
      price: actualPrice,
      qty: 1,
      icon: product.icon,
      checked: true,
      spec: state.selectedSpec || '默认'
    })
  }
  saveLocalCart()
  showToast('已加入购物车')
}

async function updateCartItem(id, change) {
  const item = state.cart.find(i => i.id === id)
  if (!item) return

  const newQty = item.qty + change

  // 已登录用户调用API
  if (isUserLoggedIn()) {
    try {
      if (newQty <= 0) {
        await del(`/api/cart/items/${id}`)
      } else {
        await put(`/api/cart/items/${id}`, { qty: newQty })
      }
      await syncCart()
      return
    } catch (e) {
      console.error('API更新购物车失败，使用本地', e)
    }
  }

  // 本地处理
  item.qty += change
  if (item.qty <= 0) {
    state.cart = state.cart.filter(i => i.id !== id)
  }
  saveLocalCart()
}

async function toggleCartItem(id) {
  const item = state.cart.find(i => i.id === id)
  if (item) {
    const newChecked = !item.checked
    // 已登录用户调用API
    if (isUserLoggedIn()) {
      try {
        await put(`/api/cart/items/${id}`, { checked: newChecked })
      } catch (e) {
        console.error('API更新选中状态失败，使用本地', e)
      }
    }
    item.checked = newChecked
  }
}

async function clearCart() {
  if (isUserLoggedIn()) {
    try {
      await post('/api/cart/clear')
      state.cart = []
      return
    } catch (e) {
      console.error('API清空购物车失败', e)
    }
  }
  state.cart = []
  saveLocalCart()
  showToast('已清空')
}

// ========== 订单相关 ==========
async function loadOrders(status = 'all') {
  try {
    // 如果是'all'就不传status参数
    const url = status === 'all' ? '/api/orders' : `/api/orders?status=${status}`
    console.log('[loadOrders] 请求URL:', url)
    const res = await get(url)
    console.log('[loadOrders] 响应:', res)
    if (res.code === 200 && res.data) {
      state.orders = res.data.list || []
      console.log('[loadOrders] 订单列表:', state.orders)
    }
  } catch (e) {
    console.error('加载订单失败', e)
  }
}

// 防止重复下单标记
let isCheckoutInProgress = false

async function checkout(couponId = null, useCoins = 0, remark = '') {
  if (!isUserLoggedIn()) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    setTimeout(() => {
      uni.navigateTo({ url: '/pages/login/index' })
    }, 1500)
    return
  }

  const items = checkedCartItems.value
  if (items.length === 0) {
    showToast('请选择商品')
    return
  }

  // 防止重复下单
  if (isCheckoutInProgress) {
    showToast('正在下单中...')
    return
  }
  isCheckoutInProgress = true

  try {
    const orderItems = items.map(item => ({
      productId: item.productId || item.id,
      qty: item.qty,
      price: item.price,
      spec: item.spec || '默认'
    }))

    const res = await post('/api/orders', {
      items: orderItems,
      couponId,
      useCoins,
      remark
    })

    if (res.code === 200) {
      const data = res.data || {}
      const originalTotal = data.originalTotal || data.total || 0
      const couponDiscount = data.couponDiscount || 0
      const coinUsed = data.coinUsed || 0
      const finalTotal = data.finalTotal || data.total || originalTotal

      // 显示订单详情
      let message = `下单成功`
      if (couponDiscount > 0 || coinUsed > 0) {
        message += `\n原价: ¥${originalTotal}`
        if (couponDiscount > 0) message += `\n优惠券: -¥${couponDiscount}`
        if (coinUsed > 0) message += `\n熊币: -¥${coinUsed}`
        message += `\n实付: ¥${finalTotal}`
      }

      uni.showModal({
        title: '下单成功',
        content: message,
        showCancel: false,
        confirmText: '查看订单'
      }).then(res => {
        if (res.confirm) {
          uni.switchTab({ url: '/pages/order/index' })
        }
      })

      await syncCart()
      await loadOrders()
    } else {
      showToast(res.message || '下单失败')
    }
  } catch (e) {
    showToast('下单失败')
    console.error('下单失败', e)
  } finally {
    isCheckoutInProgress = false
  }
}

async function cancelOrder(orderId) {
  try {
    const res = await put(`/api/orders/${orderId}/cancel`)
    if (res.code === 200) {
      showToast('已取消')
      await loadOrders()
    }
  } catch (e) {
    showToast('取消失败')
  }
}

async function payOrder(orderId) {
  try {
    const res = await put(`/api/orders/${orderId}/pay`)
    if (res.code === 200) {
      showToast('支付成功')
      await loadOrders()
    }
  } catch (e) {
    showToast('支付失败')
  }
}

// ========== 用户相关 ==========
function setUser(userData) {
  state.user = userData
  state.isLoggedIn = !!userData
}

async function loadUserProfile() {
  try {
    const res = await get('/api/user/profile')
    if (res.code === 200) {
      setUser(res.data)
    }
  } catch (e) {
    console.error('加载用户信息失败', e)
  }
}

async function login(phone, password) {
  try {
    const res = await post('/api/auth/login', { phone, password })
    if (res.code === 200) {
      uni.setStorageSync('token', res.data.token)
      // 保存用户信息到storage
      uni.setStorageSync('user_info', JSON.stringify(res.data.user))
      setUser(res.data.user)
      return { success: true }
    } else {
      return { success: false, message: res.message }
    }
  } catch (e) {
    return { success: false, message: '登录失败' }
  }
}

function logout() {
  uni.removeStorageSync('token')
  state.user = null
  state.isLoggedIn = false
  state.cart = []
  state.orders = []
  showToast('已退出登录')
}

// ========== 优惠券和熊币相关 ==========
async function loadCoupons() {
  if (!isUserLoggedIn()) return
  try {
    const res = await get('/api/coupons/available')
    if (res.code === 200) {
      state.availableCoupons = (res.data || []).filter(c => c.status === 'unused')
    }
  } catch (e) {
    console.error('加载优惠券失败', e)
  }
}

async function loadCoinBalance() {
  if (!isUserLoggedIn()) return
  try {
    const res = await get('/api/coins/balance')
    if (res.code === 200) {
      state.coinBalance = res.data.balance || 0
    }
  } catch (e) {
    console.error('加载熊币失败', e)
  }
}

// ========== 收藏相关 ==========
async function loadFavorites() {
  if (!isUserLoggedIn()) return
  try {
    const res = await get('/api/user/favorites')
    if (res.code === 200) {
      state.favorites = res.data || []
    }
  } catch (e) {
    console.error('加载收藏失败', e)
  }
}

function isFavorite(productId) {
  return state.favorites.some(f => f.productId === productId)
}

// ========== 避雷相关 ==========
async function loadDislikes() {
  if (!isUserLoggedIn()) return
  try {
    const res = await get('/api/user/dislikes')
    if (res.code === 200) {
      state.dislikes = res.data || []
    }
  } catch (e) {
    console.error('加载避雷失败', e)
  }
}

function isDisliked(productId) {
  return state.dislikes.some(d => d.productId === productId)
}

async function toggleDislike(product) {
  if (!isUserLoggedIn()) {
    showToast('请先登录')
    setTimeout(() => {
      uni.navigateTo({ url: '/pages/login/index' })
    }, 1500)
    return
  }
  try {
    const res = await post(`/api/products/${product.id}/dislike`)
    if (res.code === 200) {
      const isNowDisliked = res.data.isDisliked
      if (isNowDisliked) {
        state.dislikes.push({
          productId: product.id,
          name: product.name,
          price: product.price,
          icon: product.icon || '',
          tag: product.tag || ''
        })
      } else {
        state.dislikes = state.dislikes.filter(d => d.productId !== product.id)
      }
      showToast(isNowDisliked ? '已加入避雷' : '已取消避雷')
    }
  } catch (e) {
    showToast('操作失败')
    console.error('避雷操作失败', e)
  }
}

// ========== 通用方法 ==========
function selectCategory(id) {
  state.currentCategory = id
}

function selectProduct(product) {
  state.selectedProduct = product
  state.selectedSpec = '默认'
}

function clearSelectedProduct() {
  state.selectedProduct = null
  state.selectedSpec = '默认'
}

function setSpec(spec) {
  state.selectedSpec = spec
}

function setOrderFilter(filter) {
  state.orderFilter = filter
}

function showToast(message, duration = 1500) {
  uni.showToast({
    title: message,
    icon: 'none',
    duration
  })
}

// 暴露 store
export function useStore() {
  return {
    state,
    cartCount,
    cartTotal,
    checkedCartItems,
    checkedCartCount,
    // 分类
    loadCategories,
    // 商品
    loadProducts,
    loadProductDetail,
    // 购物车
    syncCart,
    addToCart,
    updateCartItem,
    toggleCartItem,
    clearCart,
    // 订单
    loadOrders,
    checkout,
    cancelOrder,
    payOrder,
    // 用户
    login,
    logout,
    loadUserProfile,
    setUser,
    // 优惠券和熊币
    loadCoupons,
    loadCoinBalance,
    // 收藏
    loadFavorites,
    isFavorite,
    // 避雷
    loadDislikes,
    isDisliked,
    toggleDislike,
    // 通用
    selectCategory,
    selectProduct,
    clearSelectedProduct,
    setSpec,
    setOrderFilter,
    showToast,
  }
}
