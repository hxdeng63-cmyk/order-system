from fastapi import APIRouter, Query
from models import *
from database import get_db

router = APIRouter()


# ============ 商家列表（客户可见） ============
@router.get("")
async def get_merchants(
    search: str = Query(None, description="搜索商家名称"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """获取商家列表（客户可见）"""
    offset = (page - 1) * limit

    async with get_db() as db:
        # 构建查询条件
        where_clauses = ["1=1"]
        params = []

        if search:
            where_clauses.append("name LIKE ?")
            params.append(f"%{search}%")

        where_sql = " AND ".join(where_clauses)

        # 查询总数
        cursor = await db.execute(
            f"SELECT COUNT(*) as total FROM merchants WHERE {where_sql}",
            params
        )
        total_row = await cursor.fetchone()
        total = total_row["total"]

        # 查询商家列表
        cursor = await db.execute(f"""
            SELECT id, name, phone, address, avatar, created_at
            FROM merchants
            WHERE {where_sql}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset])
        rows = await cursor.fetchall()

        merchants = [{
            "id": row["id"],
            "name": row["name"],
            "phone": row["phone"] or "",
            "address": row["address"] or "",
            "avatar": row["avatar"] or "",
            "createdAt": row["created_at"]
        } for row in rows]

        return {"code": 200, "data": {"list": merchants, "total": total}}


# ============ 商家详情（客户可见） ============
@router.get("/{merchant_id}")
async def get_merchant_detail(merchant_id: int):
    """获取商家详情（客户可见）"""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, name, phone, address, avatar, created_at FROM merchants WHERE id = ?",
            (merchant_id,)
        )
        row = await cursor.fetchone()

        if not row:
            return {"code": 404, "message": "商家不存在"}

        # 统计商品数量
        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM products WHERE merchant_id = ? AND status = 1",
            (merchant_id,)
        )
        product_count = (await cursor.fetchone())["count"] or 0

        return {
            "code": 200,
            "data": {
                "id": row["id"],
                "name": row["name"],
                "phone": row["phone"] or "",
                "address": row["address"] or "",
                "avatar": row["avatar"] or "",
                "createdAt": row["created_at"],
                "productCount": product_count
            }
        }
