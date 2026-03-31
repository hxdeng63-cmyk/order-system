from fastapi import APIRouter, HTTPException, Header, Path
from typing import Optional, List
from models import *
from database import get_db
from utils.security import decode_token

router = APIRouter()


def make_response(data=None, message="操作成功", code=200):
    return {"code": code, "message": message, "data": data}


async def get_current_user(authorization: str = Header(...)):
    """从Authorization header解析当前用户"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的token")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的token")
    return {"user_id": int(payload.get("sub"))}


async def get_current_merchant(authorization: Optional[str] = Header(None)):
    """商家认证依赖"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    return {"merchant_id": int(payload.get("sub"))}


# ============ 通用：获取优惠券模板列表 ============
@router.get("/templates", response_model=dict)
async def get_coupon_templates():
    """获取所有优惠券模板（用户和商家共用）"""
    async with get_db() as db:
        cursor = await db.execute("""
            SELECT id, name, discount, type, min_amount, description
            FROM coupon_templates
            ORDER BY id
        """)
        rows = await cursor.fetchall()

        templates = []
        for r in rows:
            templates.append({
                "id": r["id"],
                "name": r["name"],
                "discount": r["discount"],
                "type": r["type"],
                "minAmount": r["min_amount"],
                "description": r["description"] or ""
            })

        return make_response(data=templates)


# ============ 商户端：商家查看自己创建的优惠券 ============
@router.get("/merchant/list", response_model=dict)
async def get_merchant_coupons(authorization: Optional[str] = Header(None)):
    """商家查看自己发放的优惠券列表"""
    current_merchant = await get_current_merchant(authorization)
    merchant_id = current_merchant["merchant_id"]

    async with get_db() as db:
        cursor = await db.execute("""
            SELECT mc.id, mc.merchant_id, mc.template_id,
                   ct.name as template_name, ct.discount, ct.type,
                   mc.total_count, mc.remaining_count, mc.status
            FROM merchant_coupons mc
            JOIN coupon_templates ct ON mc.template_id = ct.id
            WHERE mc.merchant_id = ?
            ORDER BY mc.created_at DESC
        """, (merchant_id,))
        rows = await cursor.fetchall()

        coupons = []
        for r in rows:
            coupons.append({
                "id": r["id"],
                "merchantId": r["merchant_id"],
                "templateId": r["template_id"],
                "templateName": r["template_name"],
                "discount": r["discount"],
                "type": r["type"],
                "totalCount": r["total_count"],
                "remainingCount": r["remaining_count"],
                "status": r["status"]
            })

        return make_response(data=coupons)


# ============ 商户端：商家创建优惠券 ============
@router.post("/merchant/create", response_model=dict)
async def create_merchant_coupon(
    req: CreateMerchantCouponRequest,
    authorization: Optional[str] = Header(None)
):
    """商家创建一个优惠券实例（从模板创建）"""
    current_merchant = await get_current_merchant(authorization)
    merchant_id = current_merchant["merchant_id"]

    if req.totalCount <= 0:
        raise HTTPException(status_code=400, detail="发放总量必须大于0")

    async with get_db() as db:
        # 检查模板是否存在
        cursor = await db.execute(
            "SELECT id FROM coupon_templates WHERE id = ?",
            (req.templateId,)
        )
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="优惠券模板不存在")

        # 检查商家是否已有该模板的优惠券
        cursor = await db.execute("""
            SELECT id FROM merchant_coupons
            WHERE merchant_id = ? AND template_id = ?
        """, (merchant_id, req.templateId))
        if await cursor.fetchone():
            raise HTTPException(status_code=400, detail="该模板优惠券已存在，请直接发放剩余数量")

        # 创建优惠券实例
        cursor = await db.execute("""
            INSERT INTO merchant_coupons (merchant_id, template_id, total_count, remaining_count, status)
            VALUES (?, ?, ?, ?, 1)
        """, (merchant_id, req.templateId, req.totalCount, req.totalCount))
        await db.commit()

        return make_response(data={"id": cursor.lastrowid}, message="优惠券创建成功")


# ============ 商户端：商家发放优惠券给用户 ============
@router.post("/merchant/grant", response_model=dict)
async def grant_coupon_to_user(
    req: GrantCouponRequest,
    authorization: Optional[str] = Header(None)
):
    """商家向用户发放优惠券"""
    current_merchant = await get_current_merchant(authorization)
    merchant_id = current_merchant["merchant_id"]

    async with get_db() as db:
        # 检查用户是否存在
        cursor = await db.execute("SELECT id FROM users WHERE id = ?", (req.userId,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="用户不存在")

        # 原子操作：只有 remaining_count > 0 时才扣减（防止并发超发）
        cursor = await db.execute("""
            UPDATE merchant_coupons
            SET remaining_count = remaining_count - 1
            WHERE id = ? AND merchant_id = ? AND remaining_count > 0
        """, (req.couponId, merchant_id))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=400, detail="优惠券已发完或不属于您")

        # 添加用户优惠券记录
        await db.execute("""
            INSERT INTO user_coupons (user_id, merchant_coupon_id, status)
            VALUES (?, ?, 'unused')
        """, (req.userId, req.couponId))

        await db.commit()

        return make_response(message="优惠券发放成功")


# ============ 商户端：删除优惠券 ============
@router.delete("/merchant/{coupon_id}", response_model=dict)
async def delete_merchant_coupon(
    coupon_id: int,
    authorization: Optional[str] = Header(None)
):
    """商家删除优惠券（只能删除未发放完的）"""
    current_merchant = await get_current_merchant(authorization)
    merchant_id = current_merchant["merchant_id"]

    async with get_db() as db:
        cursor = await db.execute("""
            SELECT id, remaining_count, total_count FROM merchant_coupons
            WHERE id = ? AND merchant_id = ?
        """, (coupon_id, merchant_id))
        coupon = await cursor.fetchone()

        if not coupon:
            raise HTTPException(status_code=404, detail="优惠券不存在")

        if coupon["remaining_count"] < coupon["total_count"]:
            raise HTTPException(status_code=400, detail="已有用户领取，无法删除")

        await db.execute("DELETE FROM merchant_coupons WHERE id = ?", (coupon_id,))
        await db.commit()

        return make_response(message="删除成功")


# ============ 用户端：获取用户可用的优惠券列表 ============
@router.get("/available", response_model=dict)
async def get_available_coupons(authorization: str = Header(...)):
    """获取用户可用的优惠券列表（未使用且有剩余的）"""
    current_user = await get_current_user(authorization)
    user_id = current_user["user_id"]

    async with get_db() as db:
        cursor = await db.execute("""
            SELECT uc.id, uc.merchant_coupon_id, uc.status, uc.assigned_at,
                   mc.template_id, ct.name, ct.discount, ct.type, ct.min_amount
            FROM user_coupons uc
            JOIN merchant_coupons mc ON uc.merchant_coupon_id = mc.id
            JOIN coupon_templates ct ON mc.template_id = ct.id
            WHERE uc.user_id = ?
            ORDER BY uc.assigned_at DESC
        """, (user_id,))
        rows = await cursor.fetchall()

        coupons = []
        for r in rows:
            coupons.append({
                "id": r["id"],
                "couponId": r["merchant_coupon_id"],
                "templateName": r["name"],
                "discount": r["discount"],
                "type": r["type"],
                "minAmount": r["min_amount"],
                "status": r["status"],
                "assignedAt": r["assigned_at"]
            })

        return make_response(data=coupons)


# ============ 用户端：删除用户优惠券 ============
@router.delete("/user_coupons/{coupon_id}", response_model=dict)
async def delete_user_coupon(
    coupon_id: int,
    authorization: str = Header(...)
):
    """用户删除自己的优惠券"""
    current_user = await get_current_user(authorization)
    user_id = current_user["user_id"]

    async with get_db() as db:
        # 检查优惠券是否存在且属于该用户
        cursor = await db.execute(
            "SELECT id FROM user_coupons WHERE id = ? AND user_id = ?",
            (coupon_id, user_id)
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="优惠券不存在")

        # 删除用户优惠券
        await db.execute(
            "DELETE FROM user_coupons WHERE id = ?",
            (coupon_id,)
        )
        await db.commit()

    return make_response(message="删除成功")


# ============ 用户端：验证优惠券是否可用（结算前） ============
@router.post("/validate", response_model=dict)
async def validate_coupon(
    coupon_id: int,
    order_amount: float,
    authorization: str = Header(...)
):
    """验证优惠券是否可用于当前订单（返回折扣金额）"""
    current_user = await get_current_user(authorization)
    user_id = current_user["user_id"]

    async with get_db() as db:
        # 查询用户是否持有该优惠券且未使用
        cursor = await db.execute("""
            SELECT uc.id, uc.status, mc.remaining_count,
                   ct.discount, ct.type, ct.min_amount, ct.name
            FROM user_coupons uc
            JOIN merchant_coupons mc ON uc.merchant_coupon_id = mc.id
            JOIN coupon_templates ct ON mc.template_id = ct.id
            WHERE uc.id = ? AND uc.user_id = ?
        """, (coupon_id, user_id))
        row = await cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="您没有此优惠券")

        if row["status"] != "unused":
            raise HTTPException(status_code=400, detail="此优惠券已使用")

        if row["remaining_count"] <= 0:
            raise HTTPException(status_code=400, detail="此优惠券已发完")

        # 检查最低消费门槛
        if order_amount < row["min_amount"]:
            raise HTTPException(
                status_code=400,
                detail=f"订单金额需满 {row['min_amount']} 元才可使用此优惠券"
            )

        # 计算折扣金额
        discount_amount = order_amount * row["discount"]
        discount_amount = min(discount_amount, order_amount)  # 不超过订单金额

        return make_response(data={
            "couponId": coupon_id,
            "couponName": row["name"],
            "discount": row["discount"],
            "discountAmount": round(discount_amount, 2),
            "finalAmount": round(order_amount - discount_amount, 2)
        })
