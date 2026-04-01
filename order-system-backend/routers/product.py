from fastapi import APIRouter, HTTPException, Query, Header
from typing import Optional
from models import *
from database import get_db, get_merchant_product_table, get_user_bound_merchant_id
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
    authorization: Optional[str] = Header(None),
    merchantId: Optional[int] = Query(None, description="商家ID筛选"),
    categoryId: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),  # hot/new/price
    limit: Optional[int] = Query(None)
):
    async with get_db() as db:
        target_merchant_id = None

        # 如果指定了 merchantId 则直接用该商家表
        if merchantId is not None:
            target_merchant_id = merchantId
        else:
            # 未指定商家时，检查用户是否登录并绑定商家
            if authorization:
                token = authorization.replace("Bearer ", "")
                payload = decode_token(token)
                if payload and payload.get("type") == "user":
                    user_id = int(payload.get("sub"))
                    target_merchant_id = await get_user_bound_merchant_id(db, user_id)

        # 获取商品表名
        if target_merchant_id:
            product_table = await get_merchant_product_table(db, target_merchant_id)
        else:
            product_table = "products"

        # 构建 WHERE 条件
        where_clauses = ["status = 1"]
        params = []

        if categoryId is not None:
            where_clauses.append("category_id = ?")
            params.append(categoryId)

        if keyword:
            where_clauses.append("(name LIKE ? OR `desc` LIKE ?)")
            params.append(f"%{keyword}%")
            params.append(f"%{keyword}%")

        where_sql = " AND ".join(where_clauses)

        # 排序
        if sort == "hot":
            order_sql = " ORDER BY sales DESC"
        elif sort == "new":
            order_sql = " ORDER BY id DESC"
        elif sort == "price":
            order_sql = " ORDER BY price ASC"
        else:
            order_sql = " ORDER BY id DESC"

        limit_sql = f" LIMIT {limit}" if limit else ""

        # 查询商家表
        sql = f"""
            SELECT id, name, `desc`, price, original_price, category_id,
                   icon, tag, sales, status
            FROM {product_table}
            WHERE {where_sql}
            {order_sql}
            {limit_sql}
        """
        cursor = await db.execute(sql, params)
        rows = await cursor.fetchall()

        # 获取商家名称（如果有多商家）
        merchant_name = ""
        if target_merchant_id:
            cursor = await db.execute("SELECT name FROM merchants WHERE id = ?", (target_merchant_id,))
            m_row = await cursor.fetchone()
            merchant_name = m_row["name"] if m_row else ""

        # 预加载所有分类
        cat_rows = await db.execute("SELECT id, name FROM categories")
        cat_map = {row["id"]: row["name"] for row in await cat_rows.fetchall()}

        products = []
        for r in rows:
            cat_name = cat_map.get(r["category_id"], "") if r["category_id"] else ""
            products.append({
                "id": r["id"],
                "name": r["name"],
                "desc": r["desc"],
                "price": r["price"],
                "originalPrice": r["original_price"],
                "categoryId": r["category_id"],
                "categoryName": cat_name,
                "icon": r["icon"] or "",
                "tag": r["tag"],
                "sales": r["sales"],
                "status": r["status"],
                "merchantId": target_merchant_id or 1,
                "merchantName": merchant_name
            })
        return {"code": 200, "data": products}


# 3. 搜索商品
@router.get("/products/search")
async def search_products(
    q: str = Query(..., min_length=1),
    authorization: Optional[str] = Header(None)
):
    async with get_db() as db:
        # 确定查询的商家
        target_merchant_id = None
        if authorization:
            token = authorization.replace("Bearer ", "")
            payload = decode_token(token)
            if payload and payload.get("type") == "user":
                user_id = int(payload.get("sub"))
                target_merchant_id = await get_user_bound_merchant_id(db, user_id)

        if target_merchant_id:
            # 查询商家专属表
            product_table = await get_merchant_product_table(db, target_merchant_id)
            cursor = await db.execute(f"""
                SELECT p.id, p.name, p.desc, p.price, p.original_price, p.category_id,
                       p.icon, p.tag, p.sales, p.status, c.name as category_name, c.icon as category_icon,
                       m.name as merchant_name
                FROM {product_table} p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN merchants m ON p.merchant_id = m.id
                WHERE p.status = 1 AND (p.name LIKE ? OR p.desc LIKE ?)
                ORDER BY p.id DESC
            """, (f"%{q}%", f"%{q}%"))
            rows = await cursor.fetchall()
        else:
            # 未绑定商家，查询共享表
            cursor = await db.execute("""
                SELECT p.id, p.name, p.desc, p.price, p.original_price, p.category_id,
                       p.icon, p.tag, p.sales, p.status, c.name as category_name, c.icon as category_icon,
                       m.name as merchant_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN merchants m ON p.merchant_id = m.id
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
            "status": r["status"],
            "merchantId": target_merchant_id or 1,
            "merchantName": r["merchant_name"] or ""
        } for r in rows]
        return {"code": 200, "data": products}


# 4. 获取商品详情
@router.get("/products/{product_id}")
async def get_product_detail(
    product_id: int,
    authorization: Optional[str] = Header(None),
    merchantId: Optional[int] = Query(None, description="商家ID")
):
    import json

    async with get_db() as db:
        # 确定查询的商家
        target_merchant_id = merchantId
        if not target_merchant_id and authorization:
            token = authorization.replace("Bearer ", "")
            payload = decode_token(token)
            if payload and payload.get("type") == "user":
                user_id = int(payload.get("sub"))
                target_merchant_id = await get_user_bound_merchant_id(db, user_id)

        if target_merchant_id:
            product_table = await get_merchant_product_table(db, target_merchant_id)
            cursor = await db.execute(f"""
                SELECT p.id, p.name, p.desc, p.price, p.original_price, p.category_id,
                       p.icon, p.tag, p.sales, p.status, p.images
                FROM {product_table} p
                WHERE p.id = ? AND p.status = 1
            """, (product_id,))
            row = await cursor.fetchone()
        else:
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
    authorization: Optional[str] = Header(None),
    merchantId: Optional[int] = Query(None, description="商家ID")
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")

    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="无效的token")

    user_id = payload.get("sub")

    async with get_db() as db:
        # 确定商家
        target_merchant_id = merchantId
        if not target_merchant_id:
            target_merchant_id = await get_user_bound_merchant_id(db, user_id)

        if not target_merchant_id:
            raise HTTPException(status_code=400, detail="无法确定商家")

        # 获取商家商品表并检查商品是否存在
        product_table = await get_merchant_product_table(db, target_merchant_id)
        cursor = await db.execute(
            f"SELECT id, name, price, icon, tag FROM {product_table} WHERE id = ? AND status = 1",
            (product_id,)
        )
        product = await cursor.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")

        # 检查是否已收藏
        cursor = await db.execute(
            "SELECT id FROM favorites WHERE user_id = ? AND product_id = ? AND merchant_id = ?",
            (user_id, product_id, target_merchant_id)
        )
        existing = await cursor.fetchone()

        if existing:
            # 取消收藏
            await db.execute(
                "DELETE FROM favorites WHERE user_id = ? AND product_id = ? AND merchant_id = ?",
                (user_id, product_id, target_merchant_id)
            )
            await db.commit()

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
                "INSERT INTO favorites (user_id, product_id, merchant_id) VALUES (?, ?, ?)",
                (user_id, product_id, target_merchant_id)
            )
            await db.commit()

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
