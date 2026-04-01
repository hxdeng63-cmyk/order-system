from fastapi import APIRouter, HTTPException, Header
from typing import Optional
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


# 1. GET /api/user/profile - 获取用户信息
@router.get("/profile")
async def get_profile(authorization: str = Header(...)):
    current_user = await get_current_user(authorization)
    user_id = current_user["user_id"]

    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, name, phone, avatar, member_level, member_points, bound_merchant_id, created_at FROM users WHERE id=?",
            (user_id,)
        )
        user = await cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        return make_response(data={
            "id": user["id"],
            "name": user["name"],
            "phone": user["phone"],
            "avatar": user["avatar"] or "",
            "memberLevel": user["member_level"],
            "memberPoints": user["member_points"],
            "boundMerchantId": user["bound_merchant_id"],
            "createdAt": user["created_at"]
        })


# 2. PUT /api/user/profile - 更新用户信息
@router.put("/profile")
async def update_profile(req: UpdateProfileRequest, authorization: str = Header(...)):
    current_user = await get_current_user(authorization)
    user_id = current_user["user_id"]

    # 构建更新语句
    updates = []
    params = []
    if req.name is not None:
        updates.append("name = ?")
        params.append(req.name)
    if req.avatar is not None:
        updates.append("avatar = ?")
        params.append(req.avatar)

    if not updates:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")

    params.append(user_id)

    async with get_db() as db:
        await db.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
            params
        )
        await db.commit()

        # 查询更新后的用户信息
        cursor = await db.execute(
            "SELECT id, name, phone, avatar, member_level, member_points, created_at FROM users WHERE id=?",
            (user_id,)
        )
        user = await cursor.fetchone()

        return make_response(
            message="更新成功",
            data={
                "id": user["id"],
                "name": user["name"],
                "phone": user["phone"],
                "avatar": user["avatar"] or "",
                "memberLevel": user["member_level"],
                "memberPoints": user["member_points"],
                "createdAt": user["created_at"]
            }
        )


# 3. GET /api/user/favorites - 获取收藏列表
@router.get("/favorites")
async def get_favorites(authorization: str = Header(...)):
    current_user = await get_current_user(authorization)
    user_id = current_user["user_id"]

    async with get_db() as db:
        cursor = await db.execute(
            """SELECT f.id, f.product_id as productId, f.created_at as addedAt,
                      p.name, p.price, p.icon, p.tag
               FROM favorites f
               JOIN products p ON f.product_id = p.id
               WHERE f.user_id = ?
               ORDER BY f.created_at DESC""",
            (user_id,)
        )
        rows = await cursor.fetchall()

        favorites = [
            {
                "id": row["id"],
                "productId": row["productId"],
                "name": row["name"],
                "price": row["price"],
                "icon": row["icon"] or "",
                "tag": row["tag"] or "",
                "addedAt": row["addedAt"]
            }
            for row in rows
        ]

        return make_response(data=favorites)


# 4. GET /api/user/addresses - 获取收货地址列表
@router.get("/addresses")
async def get_addresses(authorization: str = Header(...)):
    current_user = await get_current_user(authorization)
    user_id = current_user["user_id"]

    async with get_db() as db:
        cursor = await db.execute(
            """SELECT id, name, phone, province, city, district, detail, is_default
               FROM addresses WHERE user_id = ? ORDER BY is_default DESC, id DESC""",
            (user_id,)
        )
        rows = await cursor.fetchall()

        addresses = [
            {
                "id": row["id"],
                "name": row["name"],
                "phone": row["phone"],
                "province": row["province"],
                "city": row["city"],
                "district": row["district"],
                "detail": row["detail"],
                "isDefault": bool(row["is_default"])
            }
            for row in rows
        ]

        return make_response(data=addresses)


# 5. GET /api/user/coupons - 获取优惠券列表（预留）
@router.get("/coupons")
async def get_coupons(authorization: str = Header(...)):
    current_user = await get_current_user(authorization)
    # 预留接口，暂返回空列表
    return make_response(data=[])


# ============ 用户绑定商家 ============
class BindMerchantRequest(BaseModel):
    inviteCode: str


@router.post("/bind-merchant")
async def bind_merchant(
    req: BindMerchantRequest,
    authorization: str = Header(...)
):
    """用户通过邀请码绑定商家（一对一关系）"""
    current_user = await get_current_user(authorization)
    user_id = current_user["user_id"]

    if not req.inviteCode or len(req.inviteCode) != 6:
        return make_response(code=400, message="邀请码格式不正确")

    async with get_db() as db:
        # 检查用户是否已绑定商家
        cursor = await db.execute(
            "SELECT bound_merchant_id FROM users WHERE id = ?",
            (user_id,)
        )
        user_row = await cursor.fetchone()
        if user_row and user_row["bound_merchant_id"]:
            # 查询已绑定的商家信息
            cursor = await db.execute(
                "SELECT id, name FROM merchants WHERE id = ?",
                (user_row["bound_merchant_id"],)
            )
            existing = await cursor.fetchone()
            if existing:
                return make_response(code=400, message=f"您已绑定商家：{existing['name']}", data={"merchantId": existing["id"], "merchantName": existing["name"]})

        # 通过邀请码查找商家
        cursor = await db.execute(
            "SELECT id, name, invite_code FROM merchants WHERE invite_code = ?",
            (req.inviteCode,)
        )
        merchant = await cursor.fetchone()

        if not merchant:
            return make_response(code=404, message="邀请码无效")

        # 检查商家是否已被其他用户绑定
        cursor = await db.execute(
            "SELECT id, name FROM users WHERE bound_merchant_id = ? AND id != ?",
            (merchant["id"], user_id)
        )
        existing_binding = await cursor.fetchone()
        if existing_binding:
            return make_response(code=400, message="该商家已被其他用户绑定")

        # 执行绑定
        await db.execute(
            "UPDATE users SET bound_merchant_id = ? WHERE id = ?",
            (merchant["id"], user_id)
        )
        await db.commit()

        return make_response(message="绑定成功", data={
            "merchantId": merchant["id"],
            "merchantName": merchant["name"]
        })


@router.get("/bind-status")
async def get_bind_status(authorization: str = Header(...)):
    """获取用户绑定状态"""
    current_user = await get_current_user(authorization)
    user_id = current_user["user_id"]

    async with get_db() as db:
        cursor = await db.execute(
            "SELECT bound_merchant_id FROM users WHERE id = ?",
            (user_id,)
        )
        user_row = await cursor.fetchone()

        if not user_row or not user_row["bound_merchant_id"]:
            return make_response(data={"bound": False, "merchantId": None, "merchantName": None})

        cursor = await db.execute(
            "SELECT id, name, phone, address, avatar FROM merchants WHERE id = ?",
            (user_row["bound_merchant_id"],)
        )
        merchant = await cursor.fetchone()

        if not merchant:
            return make_response(data={"bound": False, "merchantId": None, "merchantName": None})

        return make_response(data={
            "bound": True,
            "merchantId": merchant["id"],
            "merchantName": merchant["name"],
            "merchantPhone": merchant["phone"] or "",
            "merchantAddress": merchant["address"] or "",
            "merchantAvatar": merchant["avatar"] or ""
        })
