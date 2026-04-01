from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv
load_dotenv()

from database import init_db
from init_data import init_test_data
from utils.logger import get_logger

# 初始化日志
logger = get_logger('main')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    await init_db()
    await init_test_data()
    # 确保上传目录存在
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    uploads_dir = os.path.join(static_dir, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    logger.info("应用启动成功")
    yield
    # 关闭时清理
    logger.info("应用关闭")

app = FastAPI(title="点单系统API", version="1.0.0", lifespan=lifespan)

# CORS配置
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5179,http://localhost:8088").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（用于图片访问）
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# 健康检查
@app.get("/")
async def root():
    return {"message": "点单系统API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# 导入并注册路由（路由文件暂为空，稍后填充）
from routers import auth, user, product, cart, order, merchant, dislike
from routers.merchants import router as merchants_router
from routers.upload import router as upload_router
from routers.coins import router as coins_router
from routers.coupons import router as coupons_router

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(user.router, prefix="/api/user", tags=["用户"])
app.include_router(product.router, prefix="/api", tags=["商品"])
app.include_router(dislike.router, prefix="/api", tags=["商品"])
app.include_router(cart.router, prefix="/api/cart", tags=["购物车"])
app.include_router(order.router, prefix="/api/orders", tags=["订单"])
app.include_router(merchant.router, prefix="/api/merchant", tags=["商家"])
app.include_router(merchants_router, prefix="/api/merchants", tags=["商家"])
app.include_router(upload_router)
app.include_router(coins_router, prefix="/api/coins", tags=["熊币"])
app.include_router(coupons_router, prefix="/api/coupons", tags=["优惠券"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8088, reload=True)
