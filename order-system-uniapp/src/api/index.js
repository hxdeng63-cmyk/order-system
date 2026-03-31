/**
 * API 接口配置 - UniApp 版本
 * 使用 uni.request
 */

// API 基础地址（开发环境用 vite 代理，生产/APK 直连云端）
// 重要：APK 打包时确保这里填的是云端地址
const API_BASE_URL = 'http://47.110.86.191'
const API_BASE = API_BASE_URL + '/api'

// 获取token
function getToken() {
  return uni.getStorageSync('token') || ''
}

// 获取商户token
function getMerchantToken() {
  return uni.getStorageSync('merchant_token') || ''
}

export const API = {
  // ========== 商品相关 ==========
  categories: `${API_BASE}/categories`,
  products: `${API_BASE}/products`,
  productDetail: (id) => `${API_BASE}/products/${id}`,
  search: (q) => `${API_BASE}/products/search?q=${q}`,

  // ========== 购物车相关 ==========
  cart: `${API_BASE}/cart`,
  cartItems: `${API_BASE}/cart/items`,
  cartItem: (id) => `${API_BASE}/cart/items/${id}`,
  cartTotal: `${API_BASE}/cart/total`,
  cartClear: `${API_BASE}/cart/clear`,

  // ========== 订单相关 ==========
  orders: `${API_BASE}/orders`,
  orderDetail: (id) => `${API_BASE}/orders/${id}`,
  orderCancel: (id) => `${API_BASE}/orders/${id}/cancel`,
  orderComplete: (id) => `${API_BASE}/orders/${id}/complete`,
  orderPay: (id) => `${API_BASE}/orders/${id}/pay`,
  orderStatus: (status) => `${API_BASE}/orders?status=${status}`,

  // ========== 用户相关 ==========
  userProfile: `${API_BASE}/user/profile`,
  userFavorites: `${API_BASE}/user/favorites`,
  userDislikes: `${API_BASE}/user/dislikes`,
  userAddresses: `${API_BASE}/user/addresses`,
  userCoupons: `${API_BASE}/user/coupons`,

  // ========== 优惠券相关 ==========
  couponTemplates: `${API_BASE}/coupons/templates`,
  couponAvailable: `${API_BASE}/coupons/available`,
  couponValidate: `${API_BASE}/coupons/validate`,
  couponDelete: (id) => `${API_BASE}/coupons/user_coupons/${id}`,
  merchantCouponList: `${API_BASE}/coupons/merchant/list`,
  merchantCouponCreate: `${API_BASE}/coupons/merchant/create`,
  merchantCouponGrant: `${API_BASE}/coupons/merchant/grant`,
  merchantCouponDelete: (id) => `${API_BASE}/coupons/merchant/${id}`,

  // ========== 熊币相关 ==========
  coinBalance: `${API_BASE}/coins/balance`,
  coinRequest: `${API_BASE}/coins/request`,
  merchantCoinRequests: `${API_BASE}/coins/requests`,
  merchantCoinApprove: (id) => `${API_BASE}/coins/requests/${id}`,
  merchantCoinGrant: `${API_BASE}/coins/grant`,

  // ========== 认证相关 ==========
  login: `${API_BASE}/auth/login`,
  logout: `${API_BASE}/auth/logout`,
  register: `${API_BASE}/auth/register`,
  sendCode: `${API_BASE}/auth/send-code`,
  resetPassword: `${API_BASE}/auth/reset-password`,

  // ========== 商家相关 ==========
  merchantLogin: `${API_BASE}/merchant/login`,
  merchantProfile: `${API_BASE}/merchant/profile`,
  merchantTodayStats: `${API_BASE}/merchant/today-stats`,
  merchantEarnings: `${API_BASE}/merchant/earnings`,
  merchantOrders: `${API_BASE}/merchant/orders`,
  merchantOrdersAccept: (id) => `${API_BASE}/merchant/orders/${id}/accept`,
  merchantOrdersReject: (id) => `${API_BASE}/merchant/orders/${id}/reject`,
  merchantOrdersComplete: (id) => `${API_BASE}/merchant/orders/${id}/complete`,
  merchantProducts: `${API_BASE}/merchant/products`,
  merchantProductAdd: `${API_BASE}/merchant/products`,
  merchantProductUpdate: (id) => `${API_BASE}/merchant/products/${id}`,
  merchantProductStatus: (id) => `${API_BASE}/merchant/products/${id}/status`,
  merchantProductDelete: (id) => `${API_BASE}/merchant/products/${id}`,
  merchantStats: `${API_BASE}/merchant/stats`,
  merchantStatsTrend: `${API_BASE}/merchant/stats/trend`,
  merchantStatsTopProducts: `${API_BASE}/merchant/stats/top-products`,
  merchantNotifications: `${API_BASE}/merchant/notifications`,
  merchantNotificationRead: (id) => `${API_BASE}/merchant/notifications/${id}/read`,
}

/**
 * 通用请求封装
 */
function request(url, method = 'GET', data = null, useMerchantToken = false) {
  const token = useMerchantToken ? getMerchantToken() : getToken()
  const header = token ? { 'Authorization': `Bearer ${token}` } : {}

  console.log(`[API] ${method} ${url}`, data || '')

  return new Promise((resolve, reject) => {
    uni.request({
      url,
      method,
      data,
      header,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.removeStorageSync('merchant_token')
          uni.showToast({ title: '请重新登录', icon: 'none' })
          setTimeout(() => {
            uni.navigateTo({ url: '/pages/login/index' })
          }, 1500)
          reject(res)
        } else {
          // 返回错误信息
          const errMsg = res.data?.message || res.data?.detail || '请求失败'
          reject({ message: errMsg, ...res })
        }
      },
      fail: (err) => {
        console.error('[API] 请求失败', err)
        uni.showToast({ title: '网络错误', icon: 'none' })
        reject(err)
      }
    })
  })
}

// 公开的便捷方法
export function get(url, data = null) {
  return request(url, 'GET', data)
}

export function post(url, data = null) {
  return request(url, 'POST', data)
}

export function put(url, data = null) {
  return request(url, 'PUT', data)
}

export function del(url, data = null) {
  return request(url, 'DELETE', data)
}

// 商家端请求（自动带merchant token）
export function merchantGet(url, data = null) {
  return request(url, 'GET', data, true)
}

export function merchantPost(url, data = null) {
  return request(url, 'POST', data, true)
}

export function merchantPut(url, data = null) {
  return request(url, 'PUT', data, true)
}

export function merchantDel(url, data = null) {
  return request(url, 'DELETE', data, true)
}

/**
 * 打印 API 调用日志
 */
export function logAPI(api, method = 'GET', data = null) {
  console.log(`[API] ${method} ${api}`, data || '')
}
