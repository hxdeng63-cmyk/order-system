from fastapi import APIRouter, HTTPException, Header, Query, Path
from typing import Optional
import uuid
from models import *
from database import get_db, create_merchant_products_table, get_merchant_product_table
from utils.security import decode_token, verify_password, create_access_token, get_password_hash
from utils.logger import get_logger

router = APIRouter()
logger = get_logger('merchant')


async def get_current_merchant(authorization: Optional[str] = Header(None)):
    """商家认证依赖"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    return {"merchant_id": int(payload.get("sub"))}


# ============ 商家登录 ============
@router.post("/login")
async def merchant_login(req: dict):
    """商家登录"""
    username = req.get("username")
    password = req.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")

    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, username, password_hash, name, phone, address, avatar FROM merchants WHERE username = ?",
            (username,)
        )
        row = await cursor.fetchone()

        if not row or not verify_password(password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        merchant = {
            "id": row["id"],
            "username": row["username"],
            "name": row["name"],
            "phone": row["phone"] or "",
            "address": row["address"] or "",
            "avatar": row["avatar"] or ""
        }

        token = create_access_token({"sub": str(row["id"]), "type": "merchant"})

        return {"code": 200, "message": "登录成功", "data": {"token": token, "merchant": merchant}}


# ============ 商家注册 ============
class MerchantRegisterRequest(BaseModel):
    name: str
    password: str
    confirmPassword: str


@router.post("/register")
async def merchant_register(req: MerchantRegisterRequest):
    """商家注册"""
    # 验证参数
    if len(req.name) < 2 or len(req.name) > 20:
        raise HTTPException(status_code=400, detail="姓名长度必须在2-20字符之间")

    if len(req.password) < 6 or len(req.password) > 20:
        raise HTTPException(status_code=400, detail="密码长度必须在6-20字符之间")

    if req.password != req.confirmPassword:
        raise HTTPException(status_code=400, detail="两次密码输入不一致")

    async with get_db() as db:
        # 检查姓名是否已存在
        cursor = await db.execute(
            "SELECT id FROM merchants WHERE name = ?",
            (req.name,)
        )
        if await cursor.fetchone():
            raise HTTPException(status_code=400, detail="姓名已被注册")

        # 创建商家（username从name生成，确保唯一）
        hashed = get_password_hash(req.password)
        base_username = req.name.replace(" ", "").lower()

        # 检查username是否已存在
        cursor = await db.execute("SELECT id FROM merchants WHERE username = ?", (base_username,))
        if await cursor.fetchone():
            raise HTTPException(status_code=400, detail="用户名已被注册")
        username = base_username
        
        # 生成8位唯一邀请码（使用UUID后8位，碰撞概率极低）
        invite_code = uuid.uuid4().hex[-8:].upper()
        # 简单检查是否已存在（UUID碰撞概率极低）
        cursor = await db.execute("SELECT id FROM merchants WHERE invite_code = ?", (invite_code,))
        if await cursor.fetchone():
            invite_code = uuid.uuid4().hex[-8:].upper()
        
        cursor = await db.execute(
            "INSERT INTO merchants (name, username, password_hash, invite_code) VALUES (?, ?, ?, ?)",
            (req.name, username, hashed, invite_code)
        )
        await db.commit()
        merchant_id = cursor.lastrowid

        # 为新商家创建专属商品表
        await create_merchant_products_table(db, merchant_id)
        await db.commit()

        # 生成token
        token = create_access_token({"sub": str(merchant_id), "type": "merchant"})

        merchant_data = {
            "id": merchant_id,
            "name": req.name,
            "phone": "",
            "address": "",
            "avatar": "",
            "inviteCode": invite_code
        }

        return {"code": 200, "message": "注册成功", "data": {"token": token, "merchant": merchant_data}}


# ============ 商家信息 ============
@router.get("/profile")
async def get_merchant_profile(authorization: Optional[str] = Header(None)):
    """获取商家信息"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    merchant_id = int(payload.get("sub"))
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, name, phone, address, avatar, invite_code, created_at FROM merchants WHERE id = ?",
            (merchant_id,)
        )
        row = await cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="商家不存在")

        return {
            "id": row["id"],
            "name": row["name"],
            "phone": row["phone"] or "",
            "address": row["address"] or "",
            "avatar": row["avatar"] or "",
            "inviteCode": row["invite_code"] or ""
        }


# ============ 今日统计 ============
@router.get("/today-stats")
async def get_today_stats(authorization: Optional[str] = Header(None)):
    """获取今日统计"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    merchant_id = int(payload.get("sub"))
    async with get_db() as db:
        # 今日营收和订单数（使用中国时区 UTC+8）
        cursor = await db.execute("""
            SELECT COALESCE(SUM(total), 0) as revenue, COUNT(*) as orders
            FROM orders
            WHERE merchant_id = ? AND status = 'completed'
            AND date(created_at) = date('now', '+8 hours')
        """, (merchant_id,))
        row = await cursor.fetchone()
        revenue = row["revenue"] or 0
        orders = row["orders"] or 0

        # 今日待处理订单数（pending + paid），排除商家已删除的（使用中国时区）
        cursor = await db.execute("""
            SELECT COUNT(*) as pending FROM orders WHERE merchant_id = ? AND status IN ('pending', 'paid') AND merchant_deleted = 0 AND date(created_at) = date('now', '+8 hours')
        """, (merchant_id,))
        row = await cursor.fetchone()
        pending = row["pending"] or 0

        return {"revenue": revenue, "orders": orders, "pending": pending}


# ============ 收益信息 ============
@router.get("/earnings")
async def get_earnings(authorization: Optional[str] = Header(None)):
    """获取收益信息"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    async with get_db() as db:
        # 已提现（已完成订单总额）
        cursor = await db.execute("""
            SELECT COALESCE(SUM(total), 0) as withdrawn FROM orders WHERE status = 'completed'
        """)
        row = await cursor.fetchone()
        withdrawn = row["withdrawn"] or 0

        # 待提现（处理中订单总额，包括 paid 和 processing）
        cursor = await db.execute("""
            SELECT COALESCE(SUM(total), 0) as pending FROM orders WHERE status IN ('processing', 'paid')
        """)
        row = await cursor.fetchone()
        pending = row["pending"] or 0

        # balance = 已提现 + 待提现
        balance = withdrawn + pending

        return {"balance": balance, "withdrawn": withdrawn, "pending": pending}


# ============ 商家订单列表 ============
@router.get("/orders")
async def get_merchant_orders(
    authorization: Optional[str] = Header(None),
    status: Optional[str] = Query(None),  # all/new/processing/completed
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """获取商家订单列表"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    offset = (page - 1) * limit

    async with get_db() as db:
        # 从token获取merchant_id
        merchant_id = int(payload.get("sub"))

        # 构建查询条件
        where_clauses = ["1=1", "merchant_id = ?", "merchant_deleted = 0"]  # 排除商家已删除的订单
        params = [merchant_id]

        if status == "new":
            where_clauses.append("status IN ('pending', 'paid')")
        elif status == "processing":
            where_clauses.append("status = 'processing'")
        elif status == "completed":
            where_clauses.append("status = 'completed'")
        elif status == "cancelled":
            where_clauses.append("status = 'cancelled'")

        where_sql = " AND ".join(where_clauses)

        # 查询总数
        cursor = await db.execute(f"SELECT COUNT(*) as total FROM orders WHERE {where_sql}", params)
        total_row = await cursor.fetchone()
        total = total_row["total"]

        # 查询订单列表
        cursor = await db.execute(f"""
            SELECT id, user_id, status, total, remark, created_at
            FROM orders
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset])
        order_rows = await cursor.fetchall()

        orders = []
        for order_row in order_rows:
            # 查询订单项
            cursor = await db.execute("""
                SELECT product_name, qty, price FROM order_items WHERE order_id = ?
            """, (order_row["id"],))
            item_rows = await cursor.fetchall()

            items = [{
                "name": item["product_name"],
                "qty": item["qty"],
                "price": item["price"]
            } for item in item_rows]

            orders.append({
                "id": order_row["id"],
                "status": order_row["status"],
                "time": order_row["created_at"],
                "items": items,
                "total": order_row["total"],
                "customerNote": order_row["remark"] or ""
            })

        return {"code": 200, "data": {"list": orders, "total": total}}


# ============ 商家删除订单（软删除，只影响商家端） ============
@router.delete("/orders/{order_id}")
async def merchant_delete_order(
    order_id: str = Path(...),
    authorization: Optional[str] = Header(None)
):
    """商家删除订单（软删除，不影响用户端）"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")

    async with get_db() as db:
        # 检查订单是否存在且状态为completed或cancelled
        cursor = await db.execute(
            "SELECT id, status FROM orders WHERE id = ?",
            (order_id,)
        )
        row = await cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="订单不存在")

        if row["status"] not in ("completed", "cancelled", "received"):
            raise HTTPException(status_code=400, detail="只能删除已完成、已取餐或已取消的订单")

        # 标记为商家已删除
        await db.execute(
            "UPDATE orders SET merchant_deleted = 1 WHERE id = ?",
            (order_id,)
        )
        await db.commit()

    return {"code": 200, "message": "删除成功"}


# ============ 接单 ============
@router.put("/orders/{order_id}/accept")
async def accept_order(
    order_id: str = Path(...),
    authorization: Optional[str] = Header(None)
):
    """接单"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, status FROM orders WHERE id = ?",
            (order_id,)
        )
        row = await cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="订单不存在")

        if row["status"] != "paid":
            raise HTTPException(status_code=400, detail="只能接收已支付的订单")

        await db.execute("UPDATE orders SET status = 'processing' WHERE id = ?", (order_id,))
        await db.commit()

        return {"code": 200, "message": "接单成功"}


# ============ 拒单 ============
@router.put("/orders/{order_id}/reject")
async def reject_order(
    order_id: str = Path(...),
    body: Optional[dict] = None,
    authorization: Optional[str] = Header(None)
):
    """拒单"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    reason = body.get("reason") if body else None

    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, status FROM orders WHERE id = ?",
            (order_id,)
        )
        row = await cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="订单不存在")

        if row["status"] != "paid":
            raise HTTPException(status_code=400, detail="只能拒已支付的订单")

        # 更新订单状态和备注
        if reason:
            await db.execute(
                "UPDATE orders SET status = 'cancelled', remark = ? WHERE id = ?",
                (reason, order_id)
            )
        else:
            await db.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
        await db.commit()

        return {"code": 200, "message": "已拒单"}


# ============ 完成订单 ============
@router.put("/orders/{order_id}/complete")
async def complete_order(
    order_id: str = Path(...),
    authorization: Optional[str] = Header(None)
):
    """完成订单"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, status FROM orders WHERE id = ?",
            (order_id,)
        )
        row = await cursor.fetchone()
        logger.info(f"[MERCHANT COMPLETE] order_id={order_id}, 当前状态={row['status'] if row else 'not found'}")

        if not row:
            logger.warning(f"[MERCHANT COMPLETE] 订单不存在, order_id={order_id}")
            raise HTTPException(status_code=404, detail="订单不存在")

        if row["status"] != "processing":
            logger.warning(f"[MERCHANT COMPLETE] 状态不是 processing, order_id={order_id}, status={row['status']}")
            raise HTTPException(status_code=400, detail="只能完成处理中的订单")

        logger.info(f"[MERCHANT COMPLETE] 更新状态为 completed, order_id={order_id}")
        await db.execute("UPDATE orders SET status = 'completed' WHERE id = ?", (order_id,))
        await db.commit()
        logger.info(f"[MERCHANT COMPLETE] 完成成功, order_id={order_id}")

        return {"code": 200, "message": "订单已完成"}


# ============ 商品列表 ============
@router.get("/products")
async def get_merchant_products(authorization: Optional[str] = Header(None)):
    """获取商家商品列表（从per-merchant表）"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    merchant_id = int(payload.get("sub"))
    import json

    async with get_db() as db:
        product_table = await get_merchant_product_table(db, merchant_id)
        cursor = await db.execute(f"""
            SELECT p.id, p.name, p.price, p.status, p.sales, p.icon, p.images,
                   c.name as category
            FROM {product_table} p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.id DESC
        """)
        rows = await cursor.fetchall()

        products = [{
            "id": r["id"],
            "name": r["name"],
            "price": r["price"],
            "category": r["category"] or "",
            "status": "on" if r["status"] == 1 else "off",
            "sales": r["sales"] or 0,
            "icon": r["icon"] or "",
            "images": json.loads(r["images"]) if r["images"] else []
        } for r in rows]

        return {"code": 200, "data": products}


# ============ 添加商品 ============
@router.post("/products")
async def add_product(
    body: dict,
    authorization: Optional[str] = Header(None)
):
    """添加商品到商家专属表"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    merchant_id = int(payload.get("sub"))
    import json

    name = body.get("name")
    desc = body.get("desc", "")
    price = body.get("price", 0)
    category_id = body.get("categoryId")
    icon = body.get("icon", "")
    images = body.get("images", [])

    if not name or price is None:
        raise HTTPException(status_code=400, detail="商品名和价格不能为空")

    # 将images列表转为JSON字符串存储
    images_json = json.dumps(images) if images else "[]"

    async with get_db() as db:
        product_table = await get_merchant_product_table(db, merchant_id)
        cursor = await db.execute(f"""
            INSERT INTO {product_table} (name, `desc`, price, category_id, icon, images, status)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (name, desc, price, category_id, icon, images_json))
        await db.commit()
        product_id = cursor.lastrowid

        return {"code": 200, "message": "添加成功", "data": {"id": product_id}}


# ============ 更新商品 ============
@router.put("/products/{product_id}")
async def update_product(
    product_id: int = Path(...),
    body: dict = None,
    authorization: Optional[str] = Header(None)
):
    """更新商品"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    merchant_id = int(payload.get("sub"))
    async with get_db() as db:
        product_table = await get_merchant_product_table(db, merchant_id)
        cursor = await db.execute(f"SELECT id FROM {product_table} WHERE id = ?", (product_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="商品不存在")

        # 构建更新字段
        updates = []
        params = []

        if "name" in body:
            updates.append("name = ?")
            params.append(body["name"])
        if "price" in body:
            updates.append("price = ?")
            params.append(body["price"])
        if "desc" in body:
            updates.append("`desc` = ?")
            params.append(body["desc"])
        if "categoryId" in body:
            updates.append("category_id = ?")
            params.append(body["categoryId"])
        if "icon" in body:
            updates.append("icon = ?")
            params.append(body["icon"])

        if updates:
            params.append(product_id)
            await db.execute(f"UPDATE {product_table} SET {', '.join(updates)} WHERE id = ?", params)
            await db.commit()

        return {"code": 200, "message": "更新成功"}


# ============ 切换商品状态 ============
@router.put("/products/{product_id}/status")
async def toggle_product_status(
    product_id: int = Path(...),
    authorization: Optional[str] = Header(None)
):
    """切换商品状态"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    merchant_id = int(payload.get("sub"))
    async with get_db() as db:
        product_table = await get_merchant_product_table(db, merchant_id)
        cursor = await db.execute(f"SELECT id, status FROM {product_table} WHERE id = ?", (product_id,))
        row = await cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="商品不存在")

        new_status = 0 if row["status"] == 1 else 1
        await db.execute(f"UPDATE {product_table} SET status = ? WHERE id = ?", (new_status, product_id))
        await db.commit()

        return {"code": 200, "message": "状态已更新"}


# ============ 删除商品 ============
@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int = Path(...),
    authorization: Optional[str] = Header(None)
):
    """删除商品"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    merchant_id = int(payload.get("sub"))
    async with get_db() as db:
        product_table = await get_merchant_product_table(db, merchant_id)
        cursor = await db.execute(f"SELECT id FROM {product_table} WHERE id = ?", (product_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="商品不存在")

        await db.execute(f"DELETE FROM {product_table} WHERE id = ?", (product_id,))
        await db.commit()

        return {"code": 200, "message": "删除成功"}


# ============ 统计概览 ============
@router.get("/stats")
async def get_stats(
    authorization: Optional[str] = Header(None),
    date: str = Query("today")  # today/week/month
):
    """获取统计概览"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    merchant_id = int(payload.get("sub"))
    async with get_db() as db:
        product_table = await get_merchant_product_table(db, merchant_id)
        # 获取时间范围（使用中国时区 UTC+8）
        date_clause = "date('now', '+8 hours')"
        prev_date_clause = "date('now', '+8 hours', '-7 days')"

        if date == "week":
            date_clause = "date('now', '+8 hours', '-7 days')"
            prev_date_clause = "date('now', '+8 hours', '-14 days')"
        elif date == "month":
            date_clause = "date('now', '+8 hours', '-30 days')"
            prev_date_clause = "date('now', '+8 hours', '-60 days')"

        # 本期营收
        cursor = await db.execute(f"""
            SELECT COALESCE(SUM(total), 0) as revenue, COUNT(*) as orders
            FROM orders
            WHERE status = 'completed'
            AND date(created_at) >= {date_clause}
        """)
        row = await cursor.fetchone()
        revenue = row["revenue"] or 0
        orders = row["orders"] or 0

        # 上期营收（用于计算变化率）
        cursor = await db.execute(f"""
            SELECT COALESCE(SUM(total), 0) as revenue, COUNT(*) as orders
            FROM orders
            WHERE status = 'completed'
            AND date(created_at) >= {prev_date_clause}
            AND date(created_at) < {date_clause}
        """)
        prev_row = await cursor.fetchone()
        prev_revenue = prev_row["revenue"] or 0
        prev_orders = prev_row["orders"] or 0

        # 计算变化率
        revenue_change = 0
        if prev_revenue > 0:
            revenue_change = round((revenue - prev_revenue) / prev_revenue * 100, 1)

        orders_change = 0
        if prev_orders > 0:
            orders_change = round((orders - prev_orders) / prev_orders * 100, 1)

        # 平均订单金额
        avg_order_value = round(revenue / orders, 1) if orders > 0 else 0
        prev_avg = round(prev_revenue / prev_orders, 1) if prev_orders > 0 else 0
        avg_change = 0
        if prev_avg > 0:
            avg_change = round((avg_order_value - prev_avg) / prev_avg * 100, 1)

        # 商品数量（使用商家专属表）
        cursor = await db.execute(f"SELECT COUNT(*) as count FROM {product_table} WHERE status = 1")
        row = await cursor.fetchone()
        product_count = row["count"] or 0

        # 趋势数据（最近7天）
        cursor = await db.execute("""
            SELECT date(created_at) as day, COALESCE(SUM(total), 0) as revenue, COUNT(*) as orders
            FROM orders
            WHERE status = 'completed'
            AND date(created_at) >= date('now', '+8 hours', '-7 days')
            GROUP BY date(created_at)
            ORDER BY day
        """)
        trend_rows = await cursor.fetchall()

        # 补全没有数据的日期
        from datetime import datetime as dt, timedelta
        trend = []
        for i in range(7):
            day = (dt.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
            found = next((r for r in trend_rows if r["day"] == day), None)
            if found:
                trend.append({"date": day, "revenue": found["revenue"], "orders": found["orders"]})
            else:
                trend.append({"date": day, "revenue": 0, "orders": 0})

        # 热销商品TOP5（使用商家专属表）
        cursor = await db.execute(f"""
            SELECT p.id, p.name, p.sales, p.price
            FROM {product_table} p
            WHERE p.status = 1
            ORDER BY p.sales DESC
            LIMIT 5
        """)
        top_rows = await cursor.fetchall()

        # 计算总营收（用于计算占比）
        total_revenue = revenue  # 使用本期营收作为基准

        top_products = []
        for r in top_rows:
            product_revenue = (r["sales"] or 0) * (r["price"] or 0)
            share = round(product_revenue / total_revenue * 100, 1) if total_revenue > 0 else 0
            top_products.append({
                "id": r["id"],
                "name": r["name"],
                "sales": r["sales"] or 0,
                "price": r["price"] or 0,
                "revenue": product_revenue,
                "share": share
            })

        return {
            "code": 200,
            "data": {
                "revenue": revenue,
                "revenueChange": revenue_change,
                "orders": orders,
                "ordersChange": orders_change,
                "avgOrderValue": avg_order_value,
                "avgChange": avg_change,
                "productCount": product_count,
                "trend": trend,
                "topProducts": top_products
            }
        }


# ============ 趋势数据 ============
@router.get("/stats/trend")
async def get_stats_trend(authorization: Optional[str] = Header(None)):
    """获取趋势数据"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    merchant_id = int(payload.get("sub"))
    async with get_db() as db:
        product_table = await get_merchant_product_table(db, merchant_id)
        from datetime import datetime as dt, timedelta

        # 最近7天的趋势
        labels = []
        values = []

        for i in range(7, 0, -1):
            day = (dt.now() - timedelta(days=i)).strftime("%m-%d")
            labels.append(day.replace("0", "").lstrip("0").replace("-0", "-"))

            cursor = await db.execute("""
                SELECT COALESCE(SUM(total), 0) as revenue
                FROM orders
                WHERE status = 'completed'
                AND date(created_at) = date('now', ?)
            """, (f"-{i} days",))
            row = await cursor.fetchone()
            values.append(row["revenue"] or 0)

        return {"code": 200, "data": {"labels": labels, "values": values}}


# ============ 热销商品 ============
@router.get("/stats/top-products")
async def get_top_products(authorization: Optional[str] = Header(None)):
    """获取热销商品TOP5"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    merchant_id = int(payload.get("sub"))
    async with get_db() as db:
        product_table = await get_merchant_product_table(db, merchant_id)
        cursor = await db.execute(f"""
            SELECT id, name, sales, price
            FROM {product_table}
            WHERE status = 1
            ORDER BY sales DESC
            LIMIT 5
        """)
        rows = await cursor.fetchall()

        products = [{
            "id": r["id"],
            "name": r["name"],
            "sales": r["sales"] or 0,
            "price": r["price"]
        } for r in rows]

        return {"code": 200, "data": products}


# ============ 消息通知列表 ============
@router.get("/notifications")
async def get_notifications(authorization: Optional[str] = Header(None)):
    """获取消息通知列表"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    merchant_id = int(payload.get("sub"))

    async with get_db() as db:
        # 未读数
        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM notifications WHERE merchant_id = ? AND read = 0",
            (merchant_id,)
        )
        row = await cursor.fetchone()
        unread_count = row["count"] or 0

        # 通知列表
        cursor = await db.execute("""
            SELECT id, type, title, content, read, created_at
            FROM notifications
            WHERE merchant_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        """, (merchant_id,))
        rows = await cursor.fetchall()

        notifications = [{
            "id": r["id"],
            "type": r["type"],
            "title": r["title"],
            "content": r["content"] or "",
            "read": r["read"] == 1,
            "time": r["created_at"]
        } for r in rows]

        return {"code": 200, "data": {"list": notifications, "unreadCount": unread_count}}


# ============ 标记通知已读 ============
@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int = Path(...),
    authorization: Optional[str] = Header(None)
):
    """标记通知为已读"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少Authorization头")
    payload = decode_token(authorization.replace("Bearer ", ""))
    if not payload or payload.get("type") != "merchant":
        raise HTTPException(status_code=401, detail="无效的token")
    merchant_id = int(payload.get("sub"))

    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id FROM notifications WHERE id = ? AND merchant_id = ?",
            (notification_id, merchant_id)
        )
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="通知不存在")

        await db.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notification_id,))
        await db.commit()

        return {"code": 200, "message": "已标记为已读"}
