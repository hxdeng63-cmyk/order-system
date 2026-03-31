/**
 * Mock 数据
 */

export const mockCategories = [
  { id: 1, name: '奶茶', icon: 'cup' },
  { id: 2, name: '水果', icon: 'flag' },
  { id: 3, name: '甜品', icon: 'star' },
  { id: 4, name: '主食', icon: 'hand-up' },
]

export const mockProducts = [
  { id: 1, name: '珍珠奶茶', desc: 'Q弹珍珠 经典口感', price: 18, originalPrice: 24, category: 1, icon: 'cup', tag: '热销' },
  { id: 2, name: '椰果奶茶', desc: '椰果饱满 清爽回甘', price: 20, originalPrice: 26, category: 1, icon: 'cup' },
  { id: 3, name: '芋泥波波', desc: '芋泥浓郁 波波Q弹', price: 22, originalPrice: 28, category: 1, icon: 'headphones', tag: '新品' },
  { id: 4, name: '杨枝甘露', desc: '芒果西柚 清新甜蜜', price: 24, originalPrice: 30, category: 1, icon: 'gift' },
  { id: 5, name: '时令水果盘', desc: '新鲜水果 每日鲜切', price: 32, originalPrice: 40, category: 2, icon: 'flag' },
  { id: 6, name: '水果沙拉', desc: '清爽健康 低卡轻食', price: 28, originalPrice: 35, category: 2, icon: 'star' },
  { id: 7, name: '提拉米苏', desc: '意式经典 入口即化', price: 28, originalPrice: 36, category: 3, icon: 'star' },
  { id: 8, name: '芝士蛋糕', desc: '浓郁芝士 香滑细腻', price: 32, originalPrice: 42, category: 3, icon: 'star' },
  { id: 9, name: '牛肉饭', desc: '营养均衡 饱腹之选', price: 38, originalPrice: 48, category: 4, icon: 'hand-up' },
  { id: 10, name: '鸡肉沙拉', desc: '轻食主义 健康美味', price: 32, originalPrice: 40, category: 4, icon: 'hand-up' },
]

export const mockOrders = [
  {
    id: '20240325001',
    status: 'completed',
    time: '2024-03-25 14:30',
    items: [
      { name: '珍珠奶茶', qty: 1, price: 18 },
      { name: '椰果奶茶', qty: 1, price: 20 },
      { name: '芋泥波波', qty: 1, price: 22 },
    ],
    total: 60
  },
  {
    id: '20240325002',
    status: 'processing',
    time: '2024-03-25 15:20',
    items: [
      { name: '杨枝甘露', qty: 2, price: 48 },
    ],
    total: 48
  },
  {
    id: '20240325003',
    status: 'pending',
    time: '2024-03-25 16:00',
    items: [
      { name: '提拉米苏', qty: 1, price: 28 },
      { name: '芝士蛋糕', qty: 1, price: 32 },
    ],
    total: 60
  },
]

export const mockBanners = [
  { id: 1, title: '', subtitle: '' },
  { id: 2, title: '会员专享', subtitle: '充值满100送20' },
]
