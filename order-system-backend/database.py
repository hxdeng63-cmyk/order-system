import aiosqlite
import os
from typing import Optional
from contextlib import asynccontextmanager

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "order_system.db")

async def init_db():
    """初始化数据库表"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # 启用外键约束
        await db.execute("PRAGMA foreign_keys = ON")

        # Users表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT DEFAULT '用户',
                avatar TEXT DEFAULT '',
                member_level TEXT DEFAULT 'normal',
                member_points INTEGER DEFAULT 0,
                bound_merchant_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bound_merchant_id) REFERENCES merchants(id)
            )
        """)

        # Merchants表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS merchants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                avatar TEXT DEFAULT '',
                invite_code TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Categories表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                icon TEXT DEFAULT ''
            )
        """)

        # Products表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                desc TEXT DEFAULT '',
                price REAL NOT NULL,
                original_price REAL,
                category_id INTEGER,
                icon TEXT DEFAULT '',
                images TEXT DEFAULT '[]',
                tag TEXT DEFAULT '',
                status INTEGER DEFAULT 1,
                sales INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)

        # Cart Items表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                merchant_id INTEGER NOT NULL,
                qty INTEGER DEFAULT 1,
                spec TEXT DEFAULT '默认',
                checked INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (merchant_id) REFERENCES merchants(id)
            )
        """)

        # Orders表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                total REAL DEFAULT 0,
                remark TEXT DEFAULT '',
                address_id INTEGER,
                coupon_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Order Items表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                qty INTEGER NOT NULL,
                price REAL NOT NULL,
                spec TEXT DEFAULT '默认',
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        # Addresses表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                province TEXT DEFAULT '',
                city TEXT DEFAULT '',
                district TEXT DEFAULT '',
                detail TEXT DEFAULT '',
                is_default INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Favorites表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                merchant_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (merchant_id) REFERENCES merchants(id),
                UNIQUE(user_id, product_id, merchant_id)
            )
        """)

        # Dislikes表（避雷/不喜欢列表）
        await db.execute("""
            CREATE TABLE IF NOT EXISTS dislikes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id),
                UNIQUE(user_id, product_id)
            )
        """)

        # Verification Codes表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS verification_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT NOT NULL,
                code TEXT NOT NULL,
                type TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Notifications表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_id INTEGER NOT NULL,
                type TEXT DEFAULT 'order',
                title TEXT NOT NULL,
                content TEXT DEFAULT '',
                read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (merchant_id) REFERENCES merchants(id)
            )
        """)

        # Coupons表（保留原结构，兼容旧代码）
        await db.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                discount REAL NOT NULL,
                min_amount REAL DEFAULT 0,
                status INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Coupon Templates表（预置5种优惠券模板）
        await db.execute("""
            CREATE TABLE IF NOT EXISTS coupon_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                discount REAL NOT NULL,
                type TEXT DEFAULT 'percent',
                min_amount REAL DEFAULT 0,
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Merchant Coupons表（商家创建的优惠券实例）
        await db.execute("""
            CREATE TABLE IF NOT EXISTS merchant_coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_id INTEGER NOT NULL,
                template_id INTEGER NOT NULL,
                total_count INTEGER DEFAULT 100,
                remaining_count INTEGER DEFAULT 100,
                status INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (merchant_id) REFERENCES merchants(id),
                FOREIGN KEY (template_id) REFERENCES coupon_templates(id)
            )
        """)

        # User Coupons表（用户持有的优惠券）
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                merchant_coupon_id INTEGER NOT NULL,
                status TEXT DEFAULT 'unused',
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP,
                used_order_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (merchant_coupon_id) REFERENCES merchant_coupons(id)
            )
        """)

        # User Coins表（用户熊币余额）
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_coins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                balance REAL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Coin Transactions表（熊币交易记录）
        await db.execute("""
            CREATE TABLE IF NOT EXISTS coin_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                order_id TEXT,
                remark TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Coin Requests表（熊币不足通知）
        await db.execute("""
            CREATE TABLE IF NOT EXISTS coin_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                merchant_id INTEGER NOT NULL,
                amount_requested REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                message TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (merchant_id) REFERENCES merchants(id)
            )
        """)

        # ===== 字段迁移：兼容已有数据库 =====
        # merchants.invite_code 列
        cursor = await db.execute("PRAGMA table_info(merchants)")
        merchant_cols = [row[1] for row in await cursor.fetchall()]
        if 'invite_code' not in merchant_cols:
            await db.execute("ALTER TABLE merchants ADD COLUMN invite_code TEXT")
            await db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_merchants_invite_code ON merchants(invite_code)")

        # users.bound_merchant_id 列
        cursor = await db.execute("PRAGMA table_info(users)")
        user_cols = [row[1] for row in await cursor.fetchall()]
        if 'bound_merchant_id' not in user_cols:
            await db.execute("ALTER TABLE users ADD COLUMN bound_merchant_id INTEGER")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_users_bound_merchant ON users(bound_merchant_id)")

        # cart_items.merchant_id 列（多商家支持）
        cursor = await db.execute("PRAGMA table_info(cart_items)")
        cart_cols = [row[1] for row in await cursor.fetchall()]
        if 'merchant_id' not in cart_cols:
            await db.execute("ALTER TABLE cart_items ADD COLUMN merchant_id INTEGER DEFAULT 1")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_cart_items_merchant_id ON cart_items(merchant_id)")

        # favorites.merchant_id 列（多商家支持）
        cursor = await db.execute("PRAGMA table_info(favorites)")
        fav_cols = [row[1] for row in await cursor.fetchall()]
        if 'merchant_id' not in fav_cols:
            await db.execute("ALTER TABLE favorites ADD COLUMN merchant_id INTEGER DEFAULT 1")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_favorites_merchant_id ON favorites(merchant_id)")

        # products.images 列
        cursor = await db.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in await cursor.fetchall()]
        if 'images' not in columns:
            await db.execute("ALTER TABLE products ADD COLUMN images TEXT DEFAULT '[]'")
        # products.merchant_id 列（多商家支持）
        if 'merchant_id' not in columns:
            await db.execute("ALTER TABLE products ADD COLUMN merchant_id INTEGER DEFAULT 1")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_products_merchant_id ON products(merchant_id)")

        # orders.merchant_deleted 列
        cursor = await db.execute("PRAGMA table_info(orders)")
        order_columns = [row[1] for row in await cursor.fetchall()]
        if 'merchant_deleted' not in order_columns:
            await db.execute("ALTER TABLE orders ADD COLUMN merchant_deleted INTEGER DEFAULT 0")
        if 'user_deleted' not in order_columns:
            await db.execute("ALTER TABLE orders ADD COLUMN user_deleted INTEGER DEFAULT 0")
        # orders.merchant_id 列（多商家支持）
        if 'merchant_id' not in order_columns:
            await db.execute("ALTER TABLE orders ADD COLUMN merchant_id INTEGER DEFAULT 1")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_orders_merchant_id ON orders(merchant_id)")

        # merchant_product_tables 表（商家商品表记录）
        await db.execute("""
            CREATE TABLE IF NOT EXISTS merchant_product_tables (
                merchant_id INTEGER PRIMARY KEY,
                table_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 为已有商家创建商品表（如果不存在）
        cursor = await db.execute("SELECT id FROM merchants")
        for row in await cursor.fetchall():
            merchant_id = row[0]
            table_name = f"merchant_{merchant_id}_products"
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    desc TEXT DEFAULT '',
                    price REAL NOT NULL,
                    original_price REAL,
                    category_id INTEGER,
                    icon TEXT DEFAULT '',
                    images TEXT DEFAULT '[]',
                    tag TEXT DEFAULT '',
                    status INTEGER DEFAULT 1,
                    sales INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                INSERT OR IGNORE INTO merchant_product_tables (merchant_id, table_name)
                VALUES (?, ?)
            """, (merchant_id, table_name))
        # ====================================

        # 预置5种优惠券模板（如果不存在）
        cursor = await db.execute("SELECT COUNT(*) FROM coupon_templates")
        count = await cursor.fetchone()
        if count[0] == 0:
            templates = [
                ('9折券', 0.1, 'percent', 0, '消费可享受9折优惠'),
                ('8折券', 0.2, 'percent', 0, '消费可享受8折优惠'),
                ('5折券', 0.5, 'percent', 0, '消费可享受5折优惠'),
                ('1折券', 0.9, 'percent', 0, '消费可享受1折优惠'),
                ('免单券', 1.0, 'percent', 0, '消费可全额减免'),
            ]
            for t in templates:
                await db.execute("""
                    INSERT INTO coupon_templates (name, discount, type, min_amount, description)
                    VALUES (?, ?, ?, ?, ?)
                """, t)

        # 添加索引（如果不存在）
        indexes = [
            ("idx_orders_user_id", "CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)"),
            ("idx_orders_status", "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)"),
            ("idx_orders_created_at", "CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)"),
            ("idx_coin_transactions_user_id", "CREATE INDEX IF NOT EXISTS idx_coin_transactions_user_id ON coin_transactions(user_id)"),
            ("idx_user_coupons_user_id", "CREATE INDEX IF NOT EXISTS idx_user_coupons_user_id ON user_coupons(user_id)"),
            ("idx_user_coupons_status", "CREATE INDEX IF NOT EXISTS idx_user_coupons_status ON user_coupons(status)"),
            ("idx_cart_items_user_id", "CREATE INDEX IF NOT EXISTS idx_cart_items_user_id ON cart_items(user_id)"),
            ("idx_addresses_user_id", "CREATE INDEX IF NOT EXISTS idx_addresses_user_id ON addresses(user_id)"),
            ("idx_favorites_user_id", "CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id)"),
            ("idx_dislikes_user_id", "CREATE INDEX IF NOT EXISTS idx_dislikes_user_id ON dislikes(user_id)"),
        ]
        for idx_name, idx_sql in indexes:
            await db.execute(idx_sql)

        await db.commit()

async def create_merchant_products_table(db, merchant_id: int):
    """为指定商家创建专属商品表"""
    table_name = f"merchant_{merchant_id}_products"
    await db.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            desc TEXT DEFAULT '',
            price REAL NOT NULL,
            original_price REAL,
            category_id INTEGER,
            icon TEXT DEFAULT '',
            images TEXT DEFAULT '[]',
            tag TEXT DEFAULT '',
            status INTEGER DEFAULT 1,
            sales INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # 记录到 merchant_product_tables
    await db.execute("""
        INSERT OR IGNORE INTO merchant_product_tables (merchant_id, table_name)
        VALUES (?, ?)
    """, (merchant_id, table_name))


async def create_merchant_product_tables_record(db):
    """创建商家商品表记录表"""
    await db.execute("""
        CREATE TABLE IF NOT EXISTS merchant_product_tables (
            merchant_id INTEGER PRIMARY KEY,
            table_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


async def get_merchant_product_table(db, merchant_id: int) -> str:
    """获取商家商品表名"""
    cursor = await db.execute(
        "SELECT table_name FROM merchant_product_tables WHERE merchant_id = ?",
        (merchant_id,)
    )
    row = await cursor.fetchone()
    if row:
        return row["table_name"]
    return "products"  # 回退到旧表


async def get_user_bound_merchant_id(db, user_id: int) -> Optional[int]:
    """获取用户绑定的商家ID"""
    cursor = await db.execute(
        "SELECT bound_merchant_id FROM users WHERE id = ?",
        (user_id,)
    )
    row = await cursor.fetchone()
    return row["bound_merchant_id"] if row else None


@asynccontextmanager
async def get_db():
    """获取数据库连接的上下文管理器"""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()
