<template>
  <view class="page">
    <view class="form">
      <view class="form-item">
        <text class="form-label">商家</text>
        <picker
          class="form-picker"
          :value="merchantIndex"
          :range="merchants"
          range-key="name"
          @change="onMerchantChange"
        >
          <view class="picker-value">
            {{ selectedMerchant ? selectedMerchant.name : '请选择商家' }}
          </view>
        </picker>
      </view>

      <view class="form-item">
        <text class="form-label">申请数量</text>
        <input
          class="form-input"
          type="number"
          v-model="amountStr"
          placeholder="请输入需要的熊币数量"
        />
      </view>

      <view class="form-item">
        <text class="form-label">留言</text>
        <textarea
          class="form-textarea"
          v-model="message"
          placeholder="请输入留言（选填）"
          rows="3"
        />
      </view>

      <view class="btn-submit" @click="submitRequest">
        <text>提交申请</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { get, post } from '../../api/index.js'

const merchants = ref([])
const merchantIndex = ref(-1)
const selectedMerchant = ref(null)
const amountStr = ref('')
const message = ref('')

async function loadMerchants() {
  try {
    // 注意：实际项目中应调用获取商家列表API
    // 这里使用默认商家ID 1，实际应根据商户入驻情况调整
    merchants.value = [{ id: 1, name: '布布厨房' }]
    if (merchants.value.length > 0) {
      merchantIndex.value = 0
      selectedMerchant.value = merchants.value[0]
    }
  } catch (e) {
    console.error('加载商家失败', e)
  }
}

function onMerchantChange(e) {
  merchantIndex.value = e.detail.value
  selectedMerchant.value = merchants.value[merchantIndex.value]
}

async function submitRequest() {
  const val = parseFloat(amountStr.value)
  if (!amountStr.value || val <= 0) {
    uni.showToast({ title: '请输入有效数量', icon: 'none' })
    return
  }

  const merchantId = selectedMerchant.value?.id || 1

  try {
    const res = await post('/api/coins/request', {
      merchantId: merchantId,
      amountRequested: val,
      message: message.value
    })
    if (res.code === 200) {
      uni.showToast({ title: '申请已发送', icon: 'success' })
      setTimeout(() => {
        uni.navigateBack()
      }, 1500)
    } else {
      uni.showToast({ title: res.message || '提交失败', icon: 'none' })
    }
  } catch (e) {
    uni.showToast({ title: '提交失败', icon: 'none' })
  }
}

onMounted(() => {
  loadMerchants()
})
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #F7F7F7;
  padding: 16px;
}

.form {
  background: #FFFFFF;
  border-radius: 10px;
  padding: 16px;
}

.form-item {
  margin-bottom: 20px;
}

.form-label {
  font-size: 13px;
  color: #666666;
  display: block;
  margin-bottom: 8px;
}

.form-picker {
  background: #F7F7F7;
  border-radius: 6px;
  padding: 12px;
}

.picker-value {
  font-size: 14px;
  color: #333333;
}

.form-input {
  background: #F7F7F7;
  border-radius: 6px;
  padding: 12px;
  font-size: 14px;
}

.form-textarea {
  background: #F7F7F7;
  border-radius: 6px;
  padding: 12px;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
}

.btn-submit {
  background: #C8956C;
  color: #FFFFFF;
  text-align: center;
  padding: 14px;
  border-radius: 24px;
  font-size: 15px;
  margin-top: 24px;
}
</style>
