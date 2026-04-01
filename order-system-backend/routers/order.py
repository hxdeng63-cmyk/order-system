from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from datetime import datetime as dt_datetime

from models import *
from database import get_db, get_user_bound_merchant_id, get_merchant_product_table
from utils.security import decode_token
from utils.logger import get_logger

router = APIRouter()
logger = get_logger('order')

# 错误码定义
class OrderError:
    ORDER_STATUS_NOT_ALLOWED = {"code": 2002, "errorCode": "ORDER_STATUS_NOT_ALLOWED", "message": "订单状态不允许此操作"}
    ORDER_NOT_FOUND = {"code": 2001, "errorCode": "ORDER_NOT_FOUND", "message": "订单不存在"}


def make_response(data=None, message="操作成功", code=200):
    return {"code": code, "message": message, "data": data}


def make_error(error: dict):
    return {"code": error["code"], "errorCode": error["errorCode"], "message": error["message"]}


def generate_order_id() -> str:
    """生成订单号：格式 2024032500001"""
    now = dt_datetime.now()
    return now.strftime("%Y%m%d") + str(now.timestamp()).replace('.', '')[-6:]


def format_time(dt: dt_datetime) -> str:
    """格式化时间为 YYYY-MM-DD HH:MM:SS"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


async def get_current_user_id(authorization: str) -> int:
    """从Authorization header提取用户ID"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="无效的token")
    return int(payload["sub"])


# 1. POST /api/orders - 创建订单
@router.post("")
async def create_order(
    req: CreateOrderRequest,
    authorization: Optional[str] = Header(None)
):
    user_id = await get_current_user_id(authorization)

    if not req.items or len(req.items) == 0:
        return make_error({"code": 400, "errorCode": "INVALID_REQUEST", "message": "订单商品不能为空"})

    # 生成订单号
    order_id = generate_order_id()

    async with get_db() as db:
        # ========== 0. 获取用户绑定的商家ID ==========
        cursor = await db.execute(
            "SELECT bound_merchant_id FROM users WHERE id = ?",
            (user_id,)
        )
        user_row = await cursor.fetchone()
        bound_merchant_id = user_row["bound_merchant_id"] if user_row else None
        if not bound_merchant_id:
            return make_error({"code": 400, "errorCode": "NO_MERCHANT_BINDING", "message": "用户未绑定商家，无法下单"})

        # ========== 1. 验证商品并计算原价 ==========
        original_total = 0.0
        validated_items = []

        # 获取商家商品表
        product_table = await get_merchant_product_table(db, bound_merchant_id)

        for item in req.items:
            cursor = await db.execute(
                f"SELECT id, name, price, status FROM {product_table} WHERE id = ?",
                (item.productId,)
            )
            product_row = await cursor.fetchone()

            if not product_row:
                return make_error({"code": 400, "errorCode": "INVALID_PRODUCT", "message": f"商品ID {item.productId} 不存在"})

            if product_row["status"] != 1:
                return make_error({"code": 400, "errorCode": "PRODUCT_UNAVAILABLE", "message": f"商品 {product_row['name']} 已下架"})

            # 使用服务器端价格，不信任客户端价格
            server_price = product_row["price"]
            item_total = server_price * item.qty
            original_total += item_total

            validated_items.append({
                "product_id": item.productId,
                "product_name": product_row["name"],
                "qty": item.qty,
                "price": server_price,
                "spec": item.spec
            })

        # ========== 2. 计算优惠券折扣 ==========
        coupon_discount = 0.0
        coupon_name = ""
        used_coupon_id = None

        if req.couponId:
            # 验证优惠券是否可用
            cursor = await db.execute("""
                SELECT uc.id, uc.status, mc.remaining_count,
                       ct.discount, ct.type, ct.min_amount, ct.name
                FROM user_coupons uc
                JOIN merchant_coupons mc ON uc.merchant_coupon_id = mc.id
                JOIN coupon_templates ct ON mc.template_id = ct.id
                WHERE uc.id = ? AND uc.user_id = ?
            """, (req.couponId, user_id))
            coupon_row = await cursor.fetchone()

            if coupon_row:
                if coupon_row["status"] == "unused" and coupon_row["remaining_count"] > 0:
                    if original_total >= coupon_row["min_amount"]:
                        coupon_discount = original_total * coupon_row["discount"]
                        coupon_discount = min(coupon_discount, original_total)
                        coupon_name = coupon_row["name"]
                        used_coupon_id = req.couponId

        # ========== 3. 计算熊币抵扣 ==========
        coin_used = 0.0
        coin_balance = 0.0

        if req.useCoins and req.useCoins > 0:
            # 获取用户熊币余额
            cursor = await db.execute(
                "SELECT balance FROM user_coins WHERE user_id = ?",
                (user_id,)
            )
            coin_row = await cursor.fetchone()
            coin_balance = coin_row["balance"] if coin_row else 0.0

            # 实际可用熊币：不能超过折后价也不能超过余额
            after_coupon = original_total - coupon_discount
            max_coin_use = min(coin_balance, after_coupon)
            coin_used = min(req.useCoins, max_coin_use)
            coin_used = max(0, coin_used)

        # ========== 4. 计算最终金额 ==========
        final_total = original_total - coupon_discount - coin_used
        final_total = max(0, final_total)  # 确保不为负

        # ========== 5. 扣减熊币（如有使用） ==========
        if coin_used > 0:
            await db.execute("""
                UPDATE user_coins SET balance = balance - ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (coin_used, user_id))

            # 记录熊币消费记录
            await db.execute("""
                INSERT INTO coin_transactions (user_id, amount, type, order_id, remark)
                VALUES (?, ?, 'spend', ?, '订单消费')
            """, (user_id, -coin_used, order_id))

        # ========== 6. 标记优惠券为已使用 ==========
        if used_coupon_id:
            await db.execute("""
                UPDATE user_coupons SET status = 'used', used_at = CURRENT_TIMESTAMP, used_order_id = ?
                WHERE id = ?
            """, (order_id, used_coupon_id))

        # ========== 7. 插入订单 ==========
        await db.execute("""
            INSERT INTO orders (id, user_id, merchant_id, status, total, remark, address_id, coupon_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_id, user_id, bound_merchant_id, 'pending', final_total, req.remark or '', req.addressId, used_coupon_id))

        # ========== 8. 插入订单项 ==========
        for item in validated_items:
            await db.execute("""
                INSERT INTO order_items (order_id, product_id, product_name, qty, price, spec)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (order_id, item["product_id"], item["product_name"], item["qty"], item["price"], item["spec"]))

        # ========== 9. 清空用户购物车中已购买的商品 ==========
        for item in req.items:
            await db.execute(
                "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
                (user_id, item.productId)
            )

        # ========== 10. 给商家发送新订单通知 ==========
        if bound_merchant_id:
            await db.execute("""
                INSERT INTO notifications (merchant_id, type, title, content)
                VALUES (?, ?, ?, ?)
            """, (bound_merchant_id, 'order', '新订单', f'您有一个新订单 {order_id}，金额 {final_total} 元'))

        await db.commit()

        # ========== 11. 返回订单信息（含优惠明细） ==========
        return make_response(data={
            "orderId": order_id,
            "originalTotal": round(original_total, 2),
            "couponDiscount": round(coupon_discount, 2),
            "couponName": coupon_name,
            "coinUsed": round(coin_used, 2),
            "coinBalance": round(coin_balance - coin_used, 2) if coin_used > 0 else round(coin_balance, 2),
            "finalTotal": round(final_total, 2)
        }, message="下单成功")


# 1.5 PUT /api/orders/:id/pay - 用户支付订单
@router.put("/{order_id}/pay")
async def pay_order(
    order_id: str,
    authorization: Optional[str] = Header(None)
):
    """用户点击支付，订单直接变为已支付（制作中）"""
    user_id = await get_current_user_id(authorization)

    async with get_db() as db:
        # 查询订单
        cursor = await db.execute(
            "SELECT id, status FROM orders WHERE id = ? AND user_id = ?",
            (order_id, user_id)
        )
        order_row = await cursor.fetchone()

        if not order_row:
            return make_error(OrderError.ORDER_NOT_FOUND)

        # 只能支付pending状态的订单
        if order_row["status"] != "pending":
            return make_error({"code": 2002, "errorCode": "ORDER_STATUS_NOT_ALLOWED", "message": "订单状态不允许支付"})

        # 更新订单状态为paid（已支付/制作中）
        await db.execute(
            "UPDATE orders SET status = 'paid' WHERE id = ?",
            (order_id,)
        )
        await db.commit()

    return make_response(message="支付成功")


# 2. GET /api/orders - 获取订单列表
@router.get("")
async def get_orders(
    status: Optional[str] = Query("all"),  # all/pending/processing/completed/cancelled
    page: Optional[int] = Query(1),
    limit: Optional[int] = Query(10),
    authorization: Optional[str] = Header(None)
):
    user_id = await get_current_user_id(authorization)

    # 构建查询条件
    where_clause = "WHERE user_id = ? AND user_deleted = 0"  # 排除用户已删除的订单
    params = [user_id]

    if status != "all":
        where_clause += " AND status = ?"
        params.append(status)

    # 计算偏移量
    offset = (page - 1) * limit

    async with get_db() as db:
        # 查询订单列表
        cursor = await db.execute(f"""
            SELECT id, status, total, remark, created_at
            FROM orders
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (*params, limit, offset))
        order_rows = await cursor.fetchall()

        # 查询总数
        cursor = await db.execute(f"""
            SELECT COUNT(*) as count FROM orders {where_clause}
        """, params)
        total_row = await cursor.fetchone()
        total_count = total_row["count"]

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
                "time": format_time(dt_datetime.strptime(order_row["created_at"], "%Y-%m-%d %H:%M:%S")) if order_row["created_at"] else "",
                "items": items,
                "total": order_row["total"]
            })

    return make_response(data={"list": orders, "total": total_count})


# 3. GET /api/orders/:id - 获取订单详情
@router.get("/{order_id}")
async def get_order_detail(
    order_id: str,
    authorization: Optional[str] = Header(None)
):
    user_id = await get_current_user_id(authorization)

    async with get_db() as db:
        # 查询订单
        cursor = await db.execute("""
            SELECT id, status, total, remark, address_id, coupon_id, created_at
            FROM orders
            WHERE id = ? AND user_id = ?
        """, (order_id, user_id))
        order_row = await cursor.fetchone()

        if not order_row:
            return make_error(OrderError.ORDER_NOT_FOUND)

        # 查询订单项
        cursor = await db.execute("""
            SELECT product_name, qty, price, spec FROM order_items WHERE order_id = ?
        """, (order_id,))
        item_rows = await cursor.fetchall()

        items = [{
            "name": item["product_name"],
            "qty": item["qty"],
            "price": item["price"],
            "spec": item["spec"]
        } for item in item_rows]

        # 查询收货地址
        address = None
        if order_row["address_id"]:
            cursor = await db.execute("""
                SELECT id, name, phone, province, city, district, detail
                FROM addresses WHERE id = ?
            """, (order_row["address_id"],))
            addr_row = await cursor.fetchone()
            if addr_row:
                address = {
                    "id": addr_row["id"],
                    "name": addr_row["name"],
                    "phone": addr_row["phone"],
                    "province": addr_row["province"],
                    "city": addr_row["city"],
                    "district": addr_row["district"],
                    "detail": addr_row["detail"]
                }

        # 查询优惠券（通过 user_coupons → merchant_coupons → coupon_templates）
        coupon = None
        if order_row["coupon_id"]:
            cursor = await db.execute("""
                SELECT uc.id, ct.name, ct.discount
                FROM user_coupons uc
                JOIN merchant_coupons mc ON uc.merchant_coupon_id = mc.id
                JOIN coupon_templates ct ON mc.template_id = ct.id
                WHERE uc.id = ?
            """, (order_row["coupon_id"],))
            coupon_row = await cursor.fetchone()
            if coupon_row:
                coupon = {
                    "id": coupon_row["id"],
                    "name": coupon_row["name"],
                    "discount": coupon_row["discount"]
                }

    return make_response(data={
        "id": order_row["id"],
        "status": order_row["status"],
        "time": format_time(dt_datetime.strptime(order_row["created_at"], "%Y-%m-%d %H:%M:%S")) if order_row["created_at"] else "",
        "items": items,
        "total": order_row["total"],
        "remark": order_row["remark"],
        "address": address,
        "coupon": coupon
    })


# 4. PUT /api/orders/:id/cancel - 取消订单
@router.put("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    authorization: Optional[str] = Header(None)
):
    user_id = await get_current_user_id(authorization)

    async with get_db() as db:
        # 查询订单（包含优惠券和熊币使用信息）
        cursor = await db.execute("""
            SELECT id, status, total, coupon_id FROM orders WHERE id = ? AND user_id = ?
        """, (order_id, user_id))
        order_row = await cursor.fetchone()

        if not order_row:
            return make_error(OrderError.ORDER_NOT_FOUND)

        # 只能取消pending状态的订单
        if order_row["status"] != "pending":
            return make_error(OrderError.ORDER_STATUS_NOT_ALLOWED)

        # 查询熊币消费记录（退款）
        cursor = await db.execute("""
            SELECT amount FROM coin_transactions WHERE order_id = ? AND type = 'spend'
        """, (order_id,))
        coin_record = await cursor.fetchone()

        # 退还熊币
        if coin_record and coin_record["amount"] < 0:
            coin_refund = abs(coin_record["amount"])
            await db.execute("""
                UPDATE user_coins SET balance = balance + ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (coin_refund, user_id))
            # 记录退款
            await db.execute("""
                INSERT INTO coin_transactions (user_id, amount, type, order_id, remark)
                VALUES (?, ?, 'refund', ?, '订单取消退款')
            """, (user_id, coin_refund, order_id))

        # 退还优惠券（如已使用）
        if order_row["coupon_id"]:
            await db.execute("""
                UPDATE user_coupons SET status = 'unused', used_at = NULL, used_order_id = NULL
                WHERE id = ?
            """, (order_row["coupon_id"],))

        # 更新订单状态为cancelled
        await db.execute(
            "UPDATE orders SET status = 'cancelled' WHERE id = ?",
            (order_id,)
        )
        await db.commit()

    return make_response(message="取消成功")


# 5. PUT /api/orders/:id/complete - 确认收货
@router.put("/{order_id}/complete")
async def complete_order(
    order_id: str,
    authorization: Optional[str] = Header(None)
):
    user_id = await get_current_user_id(authorization)

    async with get_db() as db:
        # 查询订单
        cursor = await db.execute(
            "SELECT id, status FROM orders WHERE id = ? AND user_id = ?",
            (order_id, user_id)
        )
        order_row = await cursor.fetchone()

        if not order_row:
            logger.warning(f"[确认取餐] 订单不存在, order_id={order_id}")
            return make_error(OrderError.ORDER_NOT_FOUND)

        current_status = order_row["status"]
        logger.info(f"[确认取餐] order_id={order_id}, 当前状态={current_status}, user_id={user_id}")

        # 只能确认 completed 状态的订单
        if current_status != "completed":
            logger.warning(f"[确认取餐] 状态不允许, order_id={order_id}, current_status={current_status}")
            return make_error(OrderError.ORDER_STATUS_NOT_ALLOWED)

        # 更新为已取餐状态
        logger.info(f"[确认取餐] 更新状态为 received, order_id={order_id}")
        await db.execute(
            "UPDATE orders SET status = 'received' WHERE id = ?",
            (order_id,)
        )
        await db.commit()
        logger.info(f"[确认取餐] 更新成功, order_id={order_id}")
        return make_response(message="已确认取餐")


# 6. DELETE /api/orders/:id - 删除订单（只能删除已完成或已取消的订单）
@router.delete("/{order_id}")
async def delete_order(
    order_id: str,
    authorization: Optional[str] = Header(None)
):
    user_id = await get_current_user_id(authorization)

    async with get_db() as db:
        # 查询订单
        cursor = await db.execute(
            "SELECT id, status FROM orders WHERE id = ? AND user_id = ?",
            (order_id, user_id)
        )
        order_row = await cursor.fetchone()

        if not order_row:
            return make_error(OrderError.ORDER_NOT_FOUND)

        # 只能删除completed、cancelled或received状态的订单
        if order_row["status"] not in ("completed", "cancelled", "received"):
            return make_error({"code": 2003, "errorCode": "ORDER_STATUS_NOT_ALLOWED", "message": "只能删除已完成、已取餐或已取消的订单"})

        # 软删除：标记为用户已删除，不影响商家端
        await db.execute(
            "UPDATE orders SET user_deleted = 1 WHERE id = ?",
            (order_id,)
        )
        await db.commit()

    return make_response(message="删除成功")
