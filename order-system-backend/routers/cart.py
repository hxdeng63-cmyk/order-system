from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
from models import *
from database import get_db
from utils.security import decode_token

router = APIRouter()


async def get_current_user(authorization: str = Header(...)) -> dict:
    """从token获取当前用户"""
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的token")
    return {"user_id": int(payload.get("sub"))}


@router.get("")
async def get_cart(current_user: dict = Depends(get_current_user)):
    """获取购物车"""
    user_id = current_user["user_id"]
    async with get_db() as db:
        cursor = await db.execute("""
            SELECT ci.id, ci.product_id, p.name, p.price, p.icon, ci.qty, ci.spec, ci.checked
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.user_id = ?
            ORDER BY ci.created_at DESC
        """, (user_id,))
        rows = await cursor.fetchall()

        items = []
        total = 0.0
        for row in rows:
            item_total = row["price"] * row["qty"]
            items.append({
                "id": row["id"],
                "productId": row["product_id"],
                "name": row["name"],
                "price": row["price"],
                "icon": row["icon"],
                "qty": row["qty"],
                "spec": row["spec"],
                "checked": bool(row["checked"])
            })
            if row["checked"]:
                total += item_total

        return {"code": 200, "data": {"items": items, "total": total}}


class AddCartItemRequest(BaseModel):
    productId: int
    qty: int = 1
    spec: str = "默认"
    price: Optional[float] = None  # 前端发送但忽略，使用服务器价格


@router.post("/items")
async def add_cart_item(
    item: AddCartItemRequest,
    current_user: dict = Depends(get_current_user)
):
    """添加商品到购物车"""
    user_id = current_user["user_id"]

    # 验证商品存在且上架
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, name, price, status FROM products WHERE id = ?",
            (item.productId,)
        )
        product = await cursor.fetchone()

        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")

        if product["status"] != 1:
            raise HTTPException(status_code=400, detail="商品已下架")

        # 检查该商品是否已在购物车
        cursor = await db.execute("""
            SELECT id, qty FROM cart_items
            WHERE user_id = ? AND product_id = ? AND spec = ?
        """, (user_id, item.productId, item.spec))
        existing = await cursor.fetchone()

        if existing:
            # 更新数量
            new_qty = existing["qty"] + item.qty
            await db.execute("""
                UPDATE cart_items SET qty = ? WHERE id = ?
            """, (new_qty, existing["id"]))
        else:
            # 插入新记录
            await db.execute("""
                INSERT INTO cart_items (user_id, product_id, qty, spec, checked)
                VALUES (?, ?, ?, ?, 1)
            """, (user_id, item.productId, item.qty, item.spec))

        await db.commit()

    return {"code": 200, "message": "添加成功"}


class UpdateCartItemRequest(BaseModel):
    qty: Optional[int] = None
    checked: Optional[bool] = None


@router.put("/items/{item_id}")
async def update_cart_item(
    item_id: int,
    req: UpdateCartItemRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新商品数量或选中状态"""
    user_id = current_user["user_id"]

    async with get_db() as db:
        # 检查item是否属于该用户
        cursor = await db.execute("""
            SELECT id FROM cart_items WHERE id = ? AND user_id = ?
        """, (item_id, user_id))
        item = await cursor.fetchone()

        if not item:
            raise HTTPException(status_code=404, detail="购物车商品不存在")

        # 构建更新语句
        updates = []
        params = []

        if req.qty is not None:
            if req.qty <= 0:
                await db.execute("DELETE FROM cart_items WHERE id = ?", (item_id,))
                await db.commit()
                return {"code": 200, "message": "删除成功"}
            updates.append("qty = ?")
            params.append(req.qty)

        if req.checked is not None:
            updates.append("checked = ?")
            params.append(1 if req.checked else 0)

        if updates:
            params.append(item_id)
            await db.execute(
                f"UPDATE cart_items SET {', '.join(updates)} WHERE id = ?",
                params
            )
            await db.commit()

    return {"code": 200, "message": "更新成功"}


@router.delete("/items/{item_id}")
async def delete_cart_item(
    item_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除商品"""
    user_id = current_user["user_id"]

    async with get_db() as db:
        # 检查item是否属于该用户
        cursor = await db.execute("""
            SELECT id FROM cart_items WHERE id = ? AND user_id = ?
        """, (item_id, user_id))
        item = await cursor.fetchone()

        if not item:
            raise HTTPException(status_code=404, detail="购物车商品不存在")

        await db.execute("DELETE FROM cart_items WHERE id = ?", (item_id,))
        await db.commit()

    return {"code": 200, "message": "删除成功"}


@router.post("/clear")
async def clear_cart(current_user: dict = Depends(get_current_user)):
    """清空购物车"""
    user_id = current_user["user_id"]

    async with get_db() as db:
        await db.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
        await db.commit()

    return {"code": 200, "message": "清空成功"}


@router.get("/total")
async def get_cart_total(current_user: dict = Depends(get_current_user)):
    """获取购物车总价"""
    user_id = current_user["user_id"]

    async with get_db() as db:
        cursor = await db.execute("""
            SELECT ci.qty, ci.checked, p.price
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.user_id = ?
        """, (user_id,))
        rows = await cursor.fetchall()

        total = 0.0
        for row in rows:
            if row["checked"]:
                total += row["price"] * row["qty"]

        discount = 0.0
        final_total = total - discount

        return {
            "code": 200,
            "data": {
                "total": total,
                "discount": discount,
                "finalTotal": final_total
            }
        }
