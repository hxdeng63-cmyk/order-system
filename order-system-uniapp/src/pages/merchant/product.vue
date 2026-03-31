<template>
  <view class="merchant-product">
    <!-- Header -->
    <view class="product-header">
      <text class="product-count">共 {{ products.length }} 件商品</text>
      <!-- API: POST /api/products -->
      <button class="btn-add-product" @click="showAddModal">
        <text class="iconfont">+</text> 添加商品
      </button>
    </view>

    <!-- Product List -->
    <scroll-view scroll-y class="product-scroll">
      <view class="product-list">
        <view class="product-item" v-for="product in products" :key="product.id">
          <view class="product-image">
            <image v-if="product.icon" :src="product.icon" mode="aspectFill" class="product-img" />
            <text v-else class="iconfont">🍵</text>
          </view>
          <view class="product-info">
            <view>
              <text class="product-name">{{ product.name }}</text>
              <text class="product-category">{{ getCategoryName(product.category) }}</text>
            </view>
            <view class="product-bottom">
              <text class="product-price">¥{{ product.price }}</text>
              <view class="product-actions">
                <!-- API: PUT /api/products/:id/status -->
                <text
                  class="product-status"
                  :class="{ off: product.status === 'off' }"
                  @click="toggleStatus(product)"
                >
                  {{ product.status === 'on' ? '上架中' : '已下架' }}
                </text>
                <text class="product-edit" @click="showEditModal(product)">编辑</text>
                <text class="product-delete" @click="deleteProduct(product)">删除</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- Add Product Modal -->
    <view class="modal" v-if="showModal" @click="hideModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">添加商品</text>
          <text class="modal-close" @click="hideModal">×</text>
        </view>
        <view class="modal-body">
          <view class="form-item">
            <text class="form-label">商品名称</text>
            <input class="form-input" v-model="newProduct.name" placeholder="请输入商品名称" />
          </view>
          <view class="form-item">
            <text class="form-label">商品分类</text>
            <picker :value="categoryIndex" :range="categories" range-key="name" @change="onCategoryChange">
              <view class="form-picker">
                {{ categories[categoryIndex].name }}
              </view>
            </picker>
          </view>
          <view class="form-item">
            <text class="form-label">商品价格</text>
            <input class="form-input" v-model="newProduct.price" type="number" placeholder="请输入价格" />
          </view>
          <view class="form-item">
            <text class="form-label">商品描述</text>
            <input class="form-input" v-model="newProduct.desc" placeholder="请输入描述" />
          </view>
          <view class="form-item">
            <text class="form-label">商品图片</text>
            <view class="image-upload">
              <view class="image-list">
                <view class="image-item" v-for="(img, idx) in newProduct.images" :key="idx">
                  <image :src="img" mode="aspectFill" />
                  <text class="image-remove" @click="removeImage(idx)">×</text>
                </view>
                <view class="image-add" @click="chooseImage" v-if="newProduct.images.length < 9">
                  <text class="iconfont">+</text>
                  <text class="image-tip">添加图片</text>
                </view>
              </view>
            </view>
          </view>
        </view>
        <view class="modal-footer">
          <button class="btn-cancel" @click="hideModal">取消</button>
          <button class="btn-confirm" @click="addProduct">确定</button>
        </view>
      </view>
    </view>

    <!-- Edit Product Modal -->
    <view class="modal" v-if="showEditModalFlag" @click="hideEditModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">编辑商品</text>
          <text class="modal-close" @click="hideEditModal">×</text>
        </view>
        <view class="modal-body">
          <view class="form-item">
            <text class="form-label">商品名称</text>
            <input class="form-input" v-model="editProduct.name" placeholder="请输入商品名称" />
          </view>
          <view class="form-item">
            <text class="form-label">商品分类</text>
            <picker :value="editCategoryIndex" :range="categories" range-key="name" @change="onEditCategoryChange">
              <view class="form-picker">
                {{ categories[editCategoryIndex]?.name }}
              </view>
            </picker>
          </view>
          <view class="form-item">
            <text class="form-label">商品价格</text>
            <input class="form-input" v-model="editProduct.price" type="number" placeholder="请输入价格" />
          </view>
          <view class="form-item">
            <text class="form-label">商品描述</text>
            <input class="form-input" v-model="editProduct.desc" placeholder="请输入描述" />
          </view>
          <view class="form-item">
            <text class="form-label">商品图片</text>
            <view class="image-upload">
              <view class="image-list">
                <view class="image-item" v-for="(img, idx) in editProduct.images" :key="idx">
                  <image :src="img" mode="aspectFill" />
                  <text class="image-remove" @click="removeEditImage(idx)">×</text>
                </view>
                <view class="image-add" @click="chooseEditImage" v-if="editProduct.images.length < 9">
                  <text class="iconfont">+</text>
                  <text class="image-tip">添加图片</text>
                </view>
              </view>
            </view>
          </view>
        </view>
        <view class="modal-footer">
          <button class="btn-cancel" @click="hideEditModal">取消</button>
          <button class="btn-confirm" @click="updateProduct">保存</button>
        </view>
      </view>
    </view>

    <!-- Bottom Nav -->
    <view class="bottom-nav">
      <view class="nav-item" @click="goToHome">
        <image class="nav-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E9%A6%96%E9%A1%B5.jpg" mode="aspectFit"></image>
        <text>首页</text>
      </view>
      <view class="nav-item" @click="goToOrder">
        <image class="nav-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E8%AE%A2%E5%8D%95.jpg" mode="aspectFit"></image>
        <text>订单</text>
      </view>
      <view class="nav-item active">
        <image class="nav-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E5%95%86%E5%93%81.jpg" mode="aspectFit"></image>
        <text>商品</text>
      </view>
      <view class="nav-item" @click="goToStats">
        <image class="nav-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E7%BB%9F%E8%AE%A1.jpg" mode="aspectFit"></image>
        <text>统计</text>
      </view>
      <view class="nav-item" @click="goToProfile">
        <image class="nav-icon" src="https://tempduanju.oss-cn-beijing.aliyuncs.com/%E5%95%86%E5%AE%B6%E7%AB%AF_%E6%88%91%E7%9A%84.jpg" mode="aspectFit"></image>
        <text>我的</text>
      </view>
    </view>
  </view>
</template>

<script>
import { merchantGet, merchantPost, merchantPut, merchantDel } from '../../api/index.js'
import { get } from '../../api/index.js'

export default {
  data() {
    return {
      products: [],
      categories: [],
      categoryIndex: 0,
      showModal: false,
      newProduct: {
        name: '',
        categoryId: 1,
        price: '',
        desc: '',
        icon: '',
        images: []
      },
      showEditModalFlag: false,
      editProduct: {
        id: null,
        name: '',
        categoryId: 1,
        price: '',
        desc: '',
        icon: '',
        images: []
      },
      editCategoryIndex: 0
    }
  },
  onLoad() {
    this.loadProducts()
    this.loadCategories()
  },
  onShow() {
    this.loadProducts()
  },
  onPullDownRefresh() {
    Promise.all([this.loadProducts(), this.loadCategories()]).then(() => {
      uni.stopPullDownRefresh()
    })
  },
  methods: {
    async loadCategories() {
      try {
        const res = await get('/api/categories')
        if (res.code === 200 && res.data) {
          this.categories = res.data
        }
      } catch (e) {
        console.error('加载分类失败', e)
      }
    },
    async loadProducts() {
      try {
        const res = await merchantGet('/api/merchant/products')
        if (res.code === 200 && res.data) {
          this.products = res.data
        }
      } catch (e) {
        console.error('加载商品失败', e)
      }
    },
    getCategoryName(category) {
      return category || ''
    },
    async toggleStatus(product) {
      try {
        await merchantPut(`/api/merchant/products/${product.id}/status`)
        product.status = product.status === 'on' ? 'off' : 'on'
        uni.showToast({
          title: product.status === 'on' ? '已上架' : '已下架',
          icon: 'success'
        })
      } catch (e) {
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },
    async deleteProduct(product) {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除商品「${product.name}」吗？`,
        confirmColor: '#F44336',
        success: async (res) => {
          if (res.confirm) {
            try {
              await merchantDel(`/api/merchant/products/${product.id}`)
              uni.showToast({ title: '已删除', icon: 'success' })
              this.loadProducts()
            } catch (e) {
              uni.showToast({ title: '删除失败', icon: 'none' })
            }
          }
        }
      })
    },
    showEditModal(product) {
      // 找到分类索引
      const catIndex = this.categories.findIndex(c => c.name === product.category)
      this.editCategoryIndex = catIndex >= 0 ? catIndex : 0
      this.editProduct = {
        id: product.id,
        name: product.name,
        categoryId: product.categoryId || 1,
        price: product.price,
        desc: product.desc || '',
        icon: product.icon || '',
        images: product.images || []
      }
      this.showEditModalFlag = true
    },
    hideEditModal() {
      this.showEditModalFlag = false
      this.editProduct = { id: null, name: '', categoryId: 1, price: '', desc: '', icon: '', images: [] }
      this.editCategoryIndex = 0
    },
    onEditCategoryChange(e) {
      this.editCategoryIndex = e.detail.value
      this.editProduct.categoryId = this.categories[e.detail.value].id
    },
    chooseEditImage() {
      uni.chooseImage({
        count: 9 - this.editProduct.images.length,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: async (res) => {
          for (const tempPath of res.tempFilePaths) {
            try {
              const uploadRes = await this.uploadImage(tempPath)
              if (uploadRes.code === 200) {
                this.editProduct.images.push(uploadRes.data.url)
                if (!this.editProduct.icon) {
                  this.editProduct.icon = uploadRes.data.url
                }
              }
            } catch (e) {
              console.error('上传失败', e)
            }
          }
        }
      })
    },
    removeEditImage(idx) {
      this.editProduct.images.splice(idx, 1)
      if (idx === 0 && this.editProduct.images.length > 0) {
        this.editProduct.icon = this.editProduct.images[0]
      } else if (this.editProduct.images.length === 0) {
        this.editProduct.icon = ''
      }
    },
    async updateProduct() {
      if (!this.editProduct.name) {
        uni.showToast({ title: '请输入商品名称', icon: 'none' })
        return
      }
      if (!this.editProduct.price) {
        uni.showToast({ title: '请输入价格', icon: 'none' })
        return
      }

      try {
        await merchantPut(`/api/merchant/products/${this.editProduct.id}`, {
          name: this.editProduct.name,
          desc: this.editProduct.desc,
          price: parseFloat(this.editProduct.price),
          categoryId: this.editProduct.categoryId,
          icon: this.editProduct.icon,
          images: this.editProduct.images
        })
        uni.showToast({ title: '修改成功', icon: 'success' })
        this.hideEditModal()
        this.loadProducts()
      } catch (e) {
        uni.showToast({ title: '修改失败', icon: 'none' })
      }
    },
    showAddModal() {
      this.showModal = true
    },
    hideModal() {
      this.showModal = false
      this.newProduct = { name: '', categoryId: 1, price: '', desc: '', icon: '', images: [] }
      this.categoryIndex = 0
    },
    chooseImage() {
      uni.chooseImage({
        count: 9 - this.newProduct.images.length,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: async (res) => {
          for (const tempPath of res.tempFilePaths) {
            try {
              const uploadRes = await this.uploadImage(tempPath)
              if (uploadRes.code === 200) {
                this.newProduct.images.push(uploadRes.data.url)
                // 第一张图片作为icon
                if (!this.newProduct.icon) {
                  this.newProduct.icon = uploadRes.data.url
                }
              }
            } catch (e) {
              console.error('上传失败', e)
            }
          }
        }
      })
    },
    uploadImage(filePath) {
      return new Promise((resolve, reject) => {
        uni.uploadFile({
          url: '/api/upload',
          filePath: filePath,
          name: 'file',
          success: (res) => {
            const data = JSON.parse(res.data)
            resolve(data)
          },
          fail: (err) => {
            reject(err)
          }
        })
      })
    },
    removeImage(idx) {
      this.newProduct.images.splice(idx, 1)
      // 如果删除的是icon，重新设置icon
      if (idx === 0 && this.newProduct.images.length > 0) {
        this.newProduct.icon = this.newProduct.images[0]
      } else if (this.newProduct.images.length === 0) {
        this.newProduct.icon = ''
      }
    },
    onCategoryChange(e) {
      this.categoryIndex = e.detail.value
      this.newProduct.categoryId = this.categories[e.detail.value].id
    },
    async addProduct() {
      if (!this.newProduct.name) {
        uni.showToast({ title: '请输入商品名称', icon: 'none' })
        return
      }
      if (!this.newProduct.price) {
        uni.showToast({ title: '请输入价格', icon: 'none' })
        return
      }

      try {
        await merchantPost('/api/merchant/products', {
          name: this.newProduct.name,
          desc: this.newProduct.desc,
          price: parseFloat(this.newProduct.price),
          categoryId: this.newProduct.categoryId,
          icon: this.newProduct.icon,
          images: this.newProduct.images
        })
        uni.showToast({ title: '添加成功', icon: 'success' })
        this.hideModal()
        this.loadProducts()
      } catch (e) {
        uni.showToast({ title: '添加失败', icon: 'none' })
      }
    },
    goToHome() {
      uni.navigateTo({ url: '/pages/merchant/index' })
    },
    goToOrder() {
      uni.navigateTo({ url: '/pages/merchant/order' })
    },
    goToStats() {
      uni.navigateTo({ url: '/pages/merchant/stats' })
    },
    goToProfile() {
      uni.navigateTo({ url: '/pages/merchant/profile' })
    }
  }
}
</script>

<style scoped>
.merchant-product {
  min-height: 100vh;
  background: #F7F7F7;
  padding-bottom: 120rpx;
}

.product-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 32rpx;
  background: #fff;
  border-bottom: 1px solid #E5E5E5;
}

.product-count {
  font-size: 24rpx;
  color: #999;
}

.btn-add-product {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 8rpx 32rpx;
  background: #C8956C;
  color: #fff;
  border: none;
  border-radius: 8rpx;
  font-size: 24rpx;
  font-weight: 500;
}

.btn-add-product .iconfont {
  font-size: 28rpx;
}

.product-scroll {
  height: calc(100vh - 200rpx);
}

.product-list {
  padding: 32rpx;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.product-item {
  display: flex;
  gap: 24rpx;
  padding: 24rpx;
  background: #fff;
  border-radius: 20rpx;
  border: 1px solid #E5E5E5;
}

.product-image {
  width: 140rpx;
  height: 140rpx;
  min-width: 140rpx;
  background: #FAFAFA;
  border-radius: 16rpx;
  border: 1px solid #E5E5E5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image .iconfont {
  font-size: 56rpx;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-name {
  font-size: 28rpx;
  font-weight: 500;
  display: block;
  margin-bottom: 8rpx;
}

.product-category {
  font-size: 22rpx;
  color: #999;
}

.product-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-actions {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.product-edit {
  font-size: 22rpx;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
  background: #E3F2FD;
  color: #2196F3;
}

.product-delete {
  font-size: 22rpx;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
  background: #FFEBEE;
  color: #F44336;
}

.product-price {
  font-size: 28rpx;
  font-weight: 500;
  color: #C8956C;
  font-family: 'DM Mono', monospace;
}

.product-status {
  font-size: 22rpx;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
  background: #E8F5E9;
  color: #4CAF50;
}

.product-status.off {
  background: #F5F5F5;
  color: #999;
}

/* Modal */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal-content {
  width: 600rpx;
  background: #fff;
  border-radius: 24rpx;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32rpx;
  border-bottom: 1px solid #E5E5E5;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 600;
}

.modal-close {
  font-size: 48rpx;
  color: #999;
}

.modal-body {
  padding: 32rpx;
}

.form-item {
  margin-bottom: 32rpx;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-label {
  font-size: 26rpx;
  color: #666;
  display: block;
  margin-bottom: 12rpx;
}

.form-input {
  width: 100%;
  height: 80rpx;
  padding: 0 24rpx;
  background: #F7F7F7;
  border-radius: 12rpx;
  font-size: 28rpx;
}

.form-picker {
  height: 80rpx;
  padding: 0 24rpx;
  background: #F7F7F7;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  font-size: 28rpx;
}

.image-upload {
  padding: 16rpx 0;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.image-item {
  width: 160rpx;
  height: 160rpx;
  border-radius: 12rpx;
  overflow: hidden;
  position: relative;
}

.image-item image {
  width: 100%;
  height: 100%;
}

.image-remove {
  position: absolute;
  top: 0;
  right: 0;
  width: 40rpx;
  height: 40rpx;
  background: rgba(0,0,0,0.5);
  color: #fff;
  font-size: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-add {
  width: 160rpx;
  height: 160rpx;
  border-radius: 12rpx;
  border: 2rpx dashed #ddd;
  background: #FAFAFA;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.image-add .iconfont {
  font-size: 48rpx;
  color: #999;
}

.image-tip {
  font-size: 22rpx;
  color: #999;
}

.product-img {
  width: 100%;
  height: 100%;
  border-radius: 16rpx;
}

.modal-footer {
  display: flex;
  gap: 24rpx;
  padding: 32rpx;
  border-top: 1px solid #E5E5E5;
}

.modal-footer .btn-cancel {
  flex: 1;
  height: 88rpx;
  background: #F5F5F5;
  color: #666;
  border: none;
  border-radius: 12rpx;
  font-size: 28rpx;
}

.modal-footer .btn-confirm {
  flex: 1;
  height: 88rpx;
  background: #C8956C;
  color: #fff;
  border: none;
  border-radius: 12rpx;
  font-size: 28rpx;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 1px solid #E5E5E5;
  display: flex;
  padding: 16rpx 0;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  z-index: 100;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  color: #999;
  font-size: 20rpx;
}

.nav-item.active {
  color: #C8956C;
}

.nav-item .iconfont {
  font-size: 44rpx;
}

.nav-icon {
  width: 48rpx;
  height: 48rpx;
}
</style>
