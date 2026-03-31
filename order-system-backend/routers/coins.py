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


# ============ 用户端：获取熊币余额和交易记录 ============
@router.get("/balance", response_model=dict)
async def get_coin_balance(authorization: str = Header(...)):
    """获取当前用户的熊币余额和最近交易记录"""
    current_user = await get_current_user(authorization)
    user_id = current_user["user_id"]

    async with get_db() as db:
        # 获取余额
        cursor = await db.execute(
            "SELECT balance FROM user_coins WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        balance = row["balance"] if row else 0.0

        # 获取交易记录
        cursor = await db.execute("""
            SELECT id, amount, type, order_id, remark, created_at
            FROM coin_transactions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        """, (user_id,))
        transactions = await cursor.fetchall()

        trans_list = []
        for t in transactions:
            trans_list.append({
                "id": t["id"],
                "amount": t["amount"],
                "type": t["type"],
                "orderId": t["order_id"],
                "remark": t["remark"] or "",
                "createdAt": t["created_at"]
            })

        return make_response(data={
            "balance": balance,
            "transactions": trans_list
        })


# ============ 用户端：发送熊币不足通知 ============
@router.post("/request", response_model=dict)
async def create_coin_request(
    req: CoinRequestCreate,
    authorization: str = Header(...)
):
    """用户向商家发送熊币不足通知"""
    current_user = await get_current_user(authorization)
    user_id = current_user["user_id"]

    if req.amountRequested <= 0:
        raise HTTPException(status_code=400, detail="申请数量必须大于0")

    async with get_db() as db:
        # 检查用户是否存在
        cursor = await db.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
        user = await cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 插入申请记录
        cursor = await db.execute("""
            INSERT INTO coin_requests (user_id, merchant_id, amount_requested, status, message)
            VALUES (?, ?, ?, 'pending', ?)
        """, (user_id, req.merchantId, req.amountRequested, req.message or ""))
        await db.commit()

        return make_response(data={"id": cursor.lastrowid}, message="申请已发送")


# ============ 商户端：查看熊币申请列表 ============
@router.get("/requests", response_model=dict)
async def get_coin_requests(authorization: Optional[str] = Header(None)):
    """商家获取用户的熊币申请列表"""
    from routers.merchant import get_current_merchant
    current_merchant = await get_current_merchant(authorization)
    merchant_id = current_merchant["merchant_id"]

    async with get_db() as db:
        cursor = await db.execute("""
            SELECT cr.id, cr.user_id, u.name as user_name, cr.amount_requested,
                   cr.status, cr.message, cr.created_at
            FROM coin_requests cr
            JOIN users u ON cr.user_id = u.id
            WHERE cr.merchant_id = ?
            ORDER BY cr.created_at DESC
        """, (merchant_id,))
        rows = await cursor.fetchall()

        requests = []
        for r in rows:
            requests.append({
                "id": r["id"],
                "userId": r["user_id"],
                "userName": r["user_name"],
                "amountRequested": r["amount_requested"],
                "status": r["status"],
                "message": r["message"] or "",
                "createdAt": r["created_at"]
            })

        return make_response(data=requests)


# ============ 商户端：审批熊币申请 ============
@router.put("/requests/{request_id}", response_model=dict)
async def update_coin_request(
    request_id: int,
    req: CoinRequestUpdate,
    authorization: Optional[str] = Header(None)
):
    """商家审批熊币申请（approved/rejected）"""
    from routers.merchant import get_current_merchant
    current_merchant = await get_current_merchant(authorization)
    merchant_id = current_merchant["merchant_id"]

    if req.status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="状态只能是 approved 或 rejected")

    async with get_db() as db:
        # 查找申请
        cursor = await db.execute("""
            SELECT id, user_id, merchant_id, amount_requested, status
            FROM coin_requests WHERE id = ?
        """, (request_id,))
        row = await cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="申请不存在")

        if row["merchant_id"] != merchant_id:
            raise HTTPException(status_code=403, detail="无权操作此申请")

        if row["status"] != "pending":
            raise HTTPException(status_code=400, detail="该申请已处理")

        # 更新状态
        await db.execute(
            "UPDATE coin_requests SET status = ? WHERE id = ?",
            (req.status, request_id)
        )

        # 如果批准，同时发放熊币
        if req.status == "approved":
            user_id = row["user_id"]
            amount = row["amount_requested"]

            # 插入或更新用户熊币余额
            await db.execute("""
                INSERT INTO user_coins (user_id, balance, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    balance = balance + ?,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, amount, amount))

            # 记录交易
            await db.execute("""
                INSERT INTO coin_transactions (user_id, amount, type, remark)
                VALUES (?, ?, 'grant', '商家发放熊币')
            """, (user_id, amount))

            # 如果用户有留言，清除那条申请记录中的message以便发放熊币后追踪
            # 已在coin_transactions中记录

        await db.commit()

        return make_response(message="操作成功")


# ============ 商户端：直接发放熊币给用户 ============
@router.post("/grant", response_model=dict)
async def grant_coins(
    req: GrantCoinRequest,
    authorization: Optional[str] = Header(None)
):
    """商家直接向用户发放熊币"""
    from routers.merchant import get_current_merchant
    current_merchant = await get_current_merchant(authorization)
    merchant_id = current_merchant["merchant_id"]

    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="发放数量必须大于0")

    async with get_db() as db:
        # 检查用户是否存在
        cursor = await db.execute("SELECT id FROM users WHERE id = ?", (req.userId,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="用户不存在")

        # 插入或更新用户熊币余额
        await db.execute("""
            INSERT INTO user_coins (user_id, balance, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                balance = balance + ?,
                updated_at = CURRENT_TIMESTAMP
        """, (req.userId, req.amount, req.amount))

        # 记录交易
        remark = req.remark or "商家发放熊币"
        await db.execute("""
            INSERT INTO coin_transactions (user_id, amount, type, remark)
            VALUES (?, ?, 'grant', ?)
        """, (req.userId, req.amount, remark))

        await db.commit()

        return make_response(message=f"成功发放 {req.amount} 熊币给用户")
