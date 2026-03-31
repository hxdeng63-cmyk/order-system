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


# 1. POST /api/products/{product_id}/dislike - Toggle 避雷
@router.post("/products/{product_id}/dislike")
async def toggle_dislike(
    product_id: int,
    authorization: Optional[str] = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")

    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="无效的token")

    user_id = payload.get("sub")

    async with get_db() as db:
        # 检查商品是否存在
        cursor = await db.execute(
            "SELECT id FROM products WHERE id = ? AND status = 1",
            (product_id,)
        )
        product = await cursor.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")

        # 检查是否已存在于避雷列表
        cursor = await db.execute(
            "SELECT id FROM dislikes WHERE user_id = ? AND product_id = ?",
            (user_id, product_id)
        )
        existing = await cursor.fetchone()

        if existing:
            # 取消避雷（删除）
            await db.execute(
                "DELETE FROM dislikes WHERE user_id = ? AND product_id = ?",
                (user_id, product_id)
            )
            await db.commit()

            # 获取商品信息
            cursor = await db.execute(
                "SELECT id, name, price, icon, tag FROM products WHERE id = ?",
                (product_id,)
            )
            product = await cursor.fetchone()

            return {
                "code": 200,
                "message": "已取消避雷",
                "data": {
                    "isDisliked": False,
                    "product": {
                        "id": product["id"],
                        "name": product["name"],
                        "price": product["price"],
                        "icon": product["icon"] or "",
                        "tag": product["tag"] or ""
                    }
                }
            }
        else:
            # 添加到避雷列表
            await db.execute(
                "INSERT INTO dislikes (user_id, product_id) VALUES (?, ?)",
                (user_id, product_id)
            )
            await db.commit()

            # 获取商品信息
            cursor = await db.execute(
                "SELECT id, name, price, icon, tag FROM products WHERE id = ?",
                (product_id,)
            )
            product = await cursor.fetchone()

            return {
                "code": 200,
                "message": "已加入避雷列表",
                "data": {
                    "isDisliked": True,
                    "product": {
                        "id": product["id"],
                        "name": product["name"],
                        "price": product["price"],
                        "icon": product["icon"] or "",
                        "tag": product["tag"] or ""
                    }
                }
            }


# 2. GET /api/user/dislikes - 获取避雷列表
@router.get("/user/dislikes")
async def get_dislikes(authorization: str = Header(...)):
    current_user = await get_current_user(authorization)
    user_id = current_user["user_id"]

    async with get_db() as db:
        cursor = await db.execute(
            """SELECT d.id, d.product_id as productId, d.created_at as addedAt,
                      p.name, p.price, p.icon, p.tag
               FROM dislikes d
               JOIN products p ON d.product_id = p.id
               WHERE d.user_id = ?
               ORDER BY d.created_at DESC""",
            (user_id,)
        )
        rows = await cursor.fetchall()

        dislikes = [
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

        return make_response(data=dislikes)
