from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

# 通用响应
class ResponseModel(BaseModel):
    code: int = 200
    message: str = "操作成功"
    data: Optional[Any] = None

# Auth
class SendCodeRequest(BaseModel):
    phone: str
    type: str  # register, login, reset

class RegisterRequest(BaseModel):
    phone: str
    code: str
    password: str

class LoginRequest(BaseModel):
    phone: str
    password: str

class ResetPasswordRequest(BaseModel):
    phone: str
    code: str
    newPassword: str

class UserResponse(BaseModel):
    id: int
    name: str
    phone: str
    avatar: Optional[str] = ''
    memberLevel: str = 'normal'
    memberPoints: int = 0

# Category
class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: str

# Product
class ProductResponse(BaseModel):
    id: int
    name: str
    desc: str
    price: float
    originalPrice: Optional[float] = None
    categoryId: int
    categoryName: str = ''
    icon: str
    tag: str = ''
    sales: int = 0
    status: int = 1

class SpecResponse(BaseModel):
    name: str
    price: float

class ProductDetailResponse(BaseModel):
    id: int
    name: str
    desc: str
    price: float
    originalPrice: Optional[float] = None
    categoryId: int
    icon: str
    tag: str = ''
    images: List[str] = []
    specs: List[SpecResponse] = []
    sales: int = 0

class FavoriteRequest(BaseModel):
    pass  # 只用路径参数

# Cart
class CartItemResponse(BaseModel):
    id: int
    productId: int
    name: str
    price: float
    qty: int
    spec: str
    checked: bool

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: float

class CartTotalResponse(BaseModel):
    total: float
    discount: float = 0
    finalTotal: float

# Order
class OrderItem(BaseModel):
    productId: int
    qty: int = 1
    price: float
    spec: str = "默认"

class CreateOrderRequest(BaseModel):
    items: List[OrderItem]
    couponId: Optional[int] = None
    useCoins: Optional[float] = 0  # 使用多少熊币
    addressId: Optional[int] = None
    remark: Optional[str] = ""

class OrderItemResponse(BaseModel):
    name: str
    qty: int
    price: float

class OrderResponse(BaseModel):
    id: str
    status: str
    time: str
    items: List[OrderItemResponse]
    total: float
    customerNote: Optional[str] = ''

# Merchant
class MerchantStatsResponse(BaseModel):
    revenue: float
    orders: int
    pending: int

class MerchantEarningsResponse(BaseModel):
    balance: float
    withdrawn: float
    pending: float

# User
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None

class AddressResponse(BaseModel):
    id: int
    name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    isDefault: bool

class FavoriteResponse(BaseModel):
    id: int
    productId: int
    addedAt: str

class DislikedProductResponse(BaseModel):
    id: int
    productId: int
    name: str
    price: float
    icon: str
    tag: str
    addedAt: str

# Coin Models
class CoinBalanceResponse(BaseModel):
    balance: float
    transactions: List["CoinTransactionItem"] = []

class CoinTransactionItem(BaseModel):
    id: int
    amount: float
    type: str
    orderId: Optional[str] = None
    remark: str
    createdAt: str

class GrantCoinRequest(BaseModel):
    userId: int
    amount: float
    remark: Optional[str] = ""

class CoinRequestResponse(BaseModel):
    id: int
    userId: int
    userName: str
    amountRequested: float
    status: str
    message: str
    createdAt: str

class CoinRequestCreate(BaseModel):
    merchantId: int
    amountRequested: float
    message: Optional[str] = ""

class CoinRequestUpdate(BaseModel):
    status: str  # approved / rejected

# Coupon Models
class CouponTemplateResponse(BaseModel):
    id: int
    name: str
    discount: float
    type: str
    minAmount: float
    description: str

class MerchantCouponResponse(BaseModel):
    id: int
    merchantId: int
    templateId: int
    templateName: str
    discount: float
    type: str
    totalCount: int
    remainingCount: int
    status: int

class UserCouponResponse(BaseModel):
    id: int
    couponId: int
    templateName: str
    discount: float
    type: str
    minAmount: float
    status: str
    assignedAt: str
    usedAt: Optional[str] = None

class CreateMerchantCouponRequest(BaseModel):
    templateId: int
    totalCount: int

class GrantCouponRequest(BaseModel):
    userId: int
    couponId: int
