from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import random
import asyncio

from models import *
from database import get_db
from utils.security import create_access_token, decode_token, get_password_hash, verify_password

router = APIRouter()

# 错误码定义
class AuthError:
    PHONE_EXISTED = {"code": 422, "errorCode": "PHONE_EXISTED", "message": "手机号已注册"}
    INVALID_CODE = {"code": 422, "errorCode": "INVALID_CODE", "message": "验证码错误"}
    CODE_EXPIRED = {"code": 422, "errorCode": "CODE_EXPIRED", "message": "验证码已过期"}
    PHONE_NOT_EXIST = {"code": 422, "errorCode": "PHONE_NOT_EXIST", "message": "手机号不存在"}
    PASSWORD_ERROR = {"code": 422, "errorCode": "PASSWORD_ERROR", "message": "密码错误"}


def make_response(data=None, message="操作成功", code=200):
    return {"code": code, "message": message, "data": data}


def make_error(error: dict):
    return {"code": error["code"], "errorCode": error["errorCode"], "message": error["message"]}


def generate_code() -> str:
    """生成6位验证码"""
    return str(random.randint(100000, 999999))


async def send_sms_code(phone: str, code: str, code_type: str):
    """存储验证码到数据库"""
    async with get_db() as db:
        await db.execute(
            "INSERT INTO verification_codes (phone, code, type, expires_at) VALUES (?, ?, ?, datetime('now', '+5 minutes'))",
            (phone, code, code_type)
        )
        await db.commit()


async def verify_code(phone: str, code: str, code_type: str) -> bool:
    """验证验证码是否有效"""
    # Mock验证码直接通过
    if code == "123456":
        return True

    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id FROM verification_codes WHERE phone=? AND type=? AND expires_at > datetime('now') AND code=? ORDER BY id DESC LIMIT 1",
            (phone, code_type, code)
        )
        row = await cursor.fetchone()
        return row is not None


# 1. 发送验证码
@router.post("/send-code")
async def send_code(req: SendCodeRequest):
    # 生成验证码
    code = generate_code()

    # 存储验证码
    await send_sms_code(req.phone, code, req.type)

    # 实际发送短信（这里仅打印日志）
    print(f"[SMS] 发送验证码 {code} 到 {req.phone}, 类型: {req.type}")

    return make_response(data={"expiresIn": 300}, message="验证码已发送")


# 2. 用户注册
@router.post("/register")
async def register(req: RegisterRequest):
    # 验证参数
    if len(req.phone) != 11 or not req.phone.isdigit():
        return make_error({"code": 400, "errorCode": "VALIDATION_ERROR", "message": "请输入正确的11位手机号"})

    if len(req.password) < 6 or len(req.password) > 20:
        return make_error({"code": 400, "errorCode": "VALIDATION_ERROR", "message": "密码长度必须在6-20字符之间"})

    if req.password != req.confirmPassword:
        return make_error({"code": 400, "errorCode": "PASSWORD_MISMATCH", "message": "两次密码输入不一致"})

    async with get_db() as db:
        # 检查手机号是否已注册
        cursor = await db.execute("SELECT id FROM users WHERE phone=?", (req.phone,))
        if await cursor.fetchone():
            return make_error(AuthError.PHONE_EXISTED)

        # 验证邀请码并获取商家信息
        cursor = await db.execute(
            "SELECT id, name FROM merchants WHERE invite_code=?",
            (req.inviteCode,)
        )
        merchant = await cursor.fetchone()
        if not merchant:
            return make_error({"code": 400, "errorCode": "INVALID_INVITE_CODE", "message": "邀请码不存在"})
        # 检查商家是否已被绑定
        cursor = await db.execute(
            "SELECT id FROM users WHERE bound_merchant_id=?",
            (merchant["id"],)
        )
        if await cursor.fetchone():
            return make_error({"code": 400, "errorCode": "MERCHANT_ALREADY_BOUND", "message": "该商家已被其他用户绑定"})
        bound_merchant_id = merchant["id"]
        merchant_name = merchant["name"]

        # 创建用户（name默认为"用户"）
        hashed = get_password_hash(req.password)
        cursor = await db.execute(
            "INSERT INTO users (name, phone, password_hash, bound_merchant_id) VALUES (?, ?, ?, ?)",
            ("用户", req.phone, hashed, bound_merchant_id)
        )
        await db.commit()
        user_id = cursor.lastrowid

    # 生成token
    token = create_access_token({"sub": str(user_id), "type": "user"})

    user_data = {
        "id": user_id,
        "name": "用户",
        "phone": req.phone,
        "avatar": "",
        "memberLevel": "normal",
        "memberPoints": 0,
        "boundMerchantId": bound_merchant_id,
        "boundMerchantName": merchant_name
    }

    return make_response(data={"token": token, "user": user_data}, message="注册成功")


# 3. 用户登录
@router.post("/login")
async def login(req: LoginRequest):
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, phone, password_hash, name, avatar, member_level, member_points, bound_merchant_id FROM users WHERE phone=?",
            (req.phone,)
        )
        user = await cursor.fetchone()

        if not user:
            return make_error(AuthError.PHONE_NOT_EXIST)

        if not verify_password(req.password, user["password_hash"]):
            return make_error(AuthError.PASSWORD_ERROR)

        # 生成token
        token = create_access_token({"sub": str(user["id"]), "type": "user"})

        user_data = {
            "id": user["id"],
            "name": user["name"],
            "phone": user["phone"],
            "avatar": user["avatar"] or "",
            "memberLevel": user["member_level"],
            "memberPoints": user["member_points"],
            "boundMerchantId": user["bound_merchant_id"]
        }

    return make_response(data={"token": token, "user": user_data, "expiresIn": 2592000}, message="登录成功")


# 4. 重置密码
@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    # 验证验证码
    if not await verify_code(req.phone, req.code, "reset"):
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT id FROM verification_codes WHERE phone=? AND type='reset' AND expires_at <= datetime('now')",
                (req.phone,)
            )
            expired = await cursor.fetchone()
            if expired:
                return make_error(AuthError.CODE_EXPIRED)
            return make_error(AuthError.INVALID_CODE)

    async with get_db() as db:
        # 检查手机号是否存在
        cursor = await db.execute("SELECT id FROM users WHERE phone=?", (req.phone,))
        if not await cursor.fetchone():
            return make_error(AuthError.PHONE_NOT_EXIST)

        # 更新密码
        hashed = get_password_hash(req.newPassword)
        await db.execute("UPDATE users SET password_hash=? WHERE phone=?", (hashed, req.phone))
        await db.commit()

    return make_response(message="密码重置成功")


# 5. 刷新Token
@router.post("/refresh-token")
async def refresh_token(req: dict):
    # 暂用同一token逻辑
    token = req.get("refreshToken")
    if not token:
        return make_error({"code": 422, "errorCode": "INVALID_TOKEN", "message": "无效的token"})

    payload = decode_token(token)
    if not payload:
        return make_error({"code": 422, "errorCode": "INVALID_TOKEN", "message": "无效的token"})

    # 生成新token
    new_token = create_access_token({"sub": payload.get("sub"), "type": payload.get("type", "user")})

    return make_response(data={"token": new_token, "expiresIn": 604800})


# 6. 退出登录
@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    # 实际退出登录只需要前端删除本地token即可
    # 这里可以做token黑名单等后续扩展
    return make_response(message="退出成功")
