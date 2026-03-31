from fastapi import APIRouter, HTTPException, Query, Header
from typing import Optional
from models import *
from database import get_db
from utils.security import decode_token

router = APIRouter()

# 1. 获取分类列表
@router.get("/categories")
async def get_categories():
    async with get_db() as db:
        cursor = await db.execute("SELECT id, name, icon FROM categories ORDER BY id")
        rows = await cursor.fetchall()
        categories = [{"id": r["id"], "name": r["name"], "icon": r["icon"]} for r in rows]
        return {"code": 200, "data": categories}


# 2. 获取商品列表
@router.get("/products")
async def get_products(
    categoryId: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),  # hot/new/price
    limit: Optional[int] = Query(None)
):
    sql = """
        SELECT p.id, p.name, p.desc, p.price, p.original_price, p.category_id,
               p.icon, p.tag, p.sales, p.status, c.name as category_name, c.icon as category_icon
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.status = 1
    """
    params = []

    if categoryId is not None:
        sql += " AND p.category_id = ?"
        params.append(categoryId)

    if keyword:
        sql += " AND (p.name LIKE ? OR p.desc LIKE ?)"
        params.append(f"%{keyword}%")
        params.append(f"%{keyword}%")

    # 排序
    if sort == "hot":
        sql += " ORDER BY p.sales DESC"
    elif sort == "new":
        sql += " ORDER BY p.id DESC"
    elif sort == "price":
        sql += " ORDER BY p.price ASC"
    else:
        sql += " ORDER BY p.id DESC"

    if limit:
        sql += " LIMIT ?"
        params.append(limit)

    async with get_db() as db:
        cursor = await db.execute(sql, params)
        rows = await cursor.fetchall()
        products = [{
            "id": r["id"],
            "name": r["name"],
            "desc": r["desc"],
            "price": r["price"],
            "originalPrice": r["original_price"],
            "categoryId": r["category_id"],
            "categoryName": r["category_name"] or "",
            "icon": r["icon"] or r["category_icon"] or "",
            "tag": r["tag"],
            "sales": r["sales"],
            "status": r["status"]
        } for r in rows]
        return {"code": 200, "data": products}


# 3. 搜索商品
@router.get("/products/search")
async def search_products(q: str = Query(..., min_length=1)):
    async with get_db() as db:
        cursor = await db.execute("""
            SELECT p.id, p.name, p.desc, p.price, p.original_price, p.category_id,
                   p.icon, p.tag, p.sales, p.status, c.name as category_name, c.icon as category_icon
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.status = 1 AND (p.name LIKE ? OR p.desc LIKE ?)
            ORDER BY p.id DESC
        """, (f"%{q}%", f"%{q}%"))
        rows = await cursor.fetchall()
        products = [{
            "id": r["id"],
            "name": r["name"],
            "desc": r["desc"],
            "price": r["price"],
            "originalPrice": r["original_price"],
            "categoryId": r["category_id"],
            "categoryName": r["category_name"] or "",
            "icon": r["icon"] or r["category_icon"] or "",
            "tag": r["tag"],
            "sales": r["sales"],
            "status": r["status"]
        } for r in rows]
        return {"code": 200, "data": products}


# 4. 获取商品详情
@router.get("/products/{product_id}")
async def get_product_detail(product_id: int):
    import json

    async with get_db() as db:
        cursor = await db.execute("""
            SELECT p.id, p.name, p.desc, p.price, p.original_price, p.category_id,
                   p.icon, p.tag, p.sales, p.status, p.images
            FROM products p
            WHERE p.id = ? AND p.status = 1
        """, (product_id,))
        row = await cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="商品不存在")

        # 解析images字段
        images = []
        if row["images"]:
            try:
                images = json.loads(row["images"]) if isinstance(row["images"], str) else row["images"]
            except:
                images = []

        return {"code": 200, "data": {
            "id": row["id"],
            "name": row["name"],
            "desc": row["desc"],
            "price": row["price"],
            "originalPrice": row["original_price"],
            "categoryId": row["category_id"],
            "icon": row["icon"] or "",
            "tag": row["tag"],
            "images": images,
            "specs": [{"name": "默认", "price": row["price"]}],
            "sales": row["sales"]
        }}


# 5. 收藏/取消收藏
@router.post("/products/{product_id}/favorite")
async def toggle_favorite(
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

        # 检查是否已收藏
        cursor = await db.execute(
            "SELECT id FROM favorites WHERE user_id = ? AND product_id = ?",
            (user_id, product_id)
        )
        existing = await cursor.fetchone()

        if existing:
            # 取消收藏
            await db.execute(
                "DELETE FROM favorites WHERE user_id = ? AND product_id = ?",
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
                "message": "已取消收藏",
                "data": {
                    "isFavorite": False,
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
            # 添加收藏
            await db.execute(
                "INSERT INTO favorites (user_id, product_id) VALUES (?, ?)",
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
                "message": "收藏成功",
                "data": {
                    "isFavorite": True,
                    "product": {
                        "id": product["id"],
                        "name": product["name"],
                        "price": product["price"],
                        "icon": product["icon"] or "",
                        "tag": product["tag"] or ""
                    }
                }
            }
