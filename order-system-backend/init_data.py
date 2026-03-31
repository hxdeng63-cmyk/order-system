"""
初始化测试数据
在main.py启动时自动调用
"""
import aiosqlite
import os
from utils.security import get_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "order_system.db")

async def init_test_data():
    """初始化测试数据"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # 检查是否已有数据
        cursor = await db.execute("SELECT COUNT(*) FROM merchants")
        count = (await cursor.fetchone())[0]
        if count > 0:
            print("数据已存在，跳过初始化")
            return

        print("开始初始化测试数据...")

        # 1. 创建商家账号
        hashed = get_password_hash("123456")
        await db.execute("""
            INSERT INTO merchants (username, password_hash, name, phone, address)
            VALUES (?, ?, ?, ?, ?)
        """, ("布布", hashed, "奶茶铺子", "13800138001", "北京市朝阳区xxx路"))

        # 2. 创建分类
        categories = [
            ("奶茶", "cup"),
            ("水果", "apple"),
            ("甜品", "cake"),
            ("主食", "utensils"),
        ]
        for name, icon in categories:
            await db.execute("INSERT INTO categories (name, icon) VALUES (?, ?)", (name, icon))

        # 3. 创建商品
        products = [
            # 奶茶分类 (category_id=1)
            ("珍珠奶茶", "Q弹珍珠 经典口感", 18, 24, 1, "cup", "热销", 999),
            ("椰果奶茶", "椰果Q弹", 16, 22, 1, "cup", "推荐", 856),
            ("芋泥波波", "芋泥波波好喝", 20, 26, 1, "cup", "", 642),
            ("杨枝甘露", "芒果西柚组合", 22, 28, 1, "cup", "新品", 428),
            # 水果分类 (category_id=2)
            ("鲜切水果杯", "当季鲜果", 15, 20, 2, "apple", "", 356),
            ("水果沙拉", "多种水果", 25, 32, 2, "apple", "", 289),
            # 甜品分类 (category_id=3)
            ("提拉米苏", "经典意式", 28, 36, 3, "cake", "", 512),
            ("芒果班戟", "芒果奶油", 22, 28, 3, "cake", "", 445),
            # 主食分类 (category_id=4)
            ("牛肉汉堡", "手打牛肉饼", 32, 40, 4, "utensils", "", 234),
            ("意面套餐", "番茄肉酱", 28, 35, 4, "utensils", "", 189),
            ("炒饭套餐", "扬州炒饭", 20, 25, 4, "utensils", "", 312),
            ("饺子套餐", "猪肉白菜", 22, 28, 4, "utensils", "", 267),
        ]
        for name, desc, price, original_price, cat_id, icon, tag, sales in products:
            await db.execute("""
                INSERT INTO products (name, desc, price, original_price, category_id, icon, tag, status, sales)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (name, desc, price, original_price, cat_id, icon, tag, sales))

        # 4. 创建测试用户
        await db.execute("""
            INSERT INTO users (phone, password_hash, name, member_level, member_points)
            VALUES (?, ?, ?, ?, ?)
        """, ("13800138000", hashed, "测试用户", "silver", 1250))

        # 5. 创建模拟订单
        import datetime
        now = datetime.datetime.now()

        # 订单1: pending
        order1_id = now.strftime("%Y%m%d") + "001"
        await db.execute("""
            INSERT INTO orders (id, user_id, status, total, remark, created_at)
            VALUES (?, 1, 'pending', 52, '少糖', datetime('now', '-1 hour'))
        """, (order1_id,))
        await db.execute("""
            INSERT INTO order_items (order_id, product_id, product_name, qty, price, spec)
            VALUES (?, 1, '珍珠奶茶', 2, 36, '默认')
        """, (order1_id,))
        await db.execute("""
            INSERT INTO order_items (order_id, product_id, product_name, qty, price, spec)
            VALUES (?, 2, '椰果奶茶', 1, 16, '默认')
        """, (order1_id,))

        # 订单2: processing
        order2_id = now.strftime("%Y%m%d") + "002"
        await db.execute("""
            INSERT INTO orders (id, user_id, status, total, remark, created_at)
            VALUES (?, 1, 'processing', 50, '', datetime('now', '-3 hour'))
        """, (order2_id,))
        await db.execute("""
            INSERT INTO order_items (order_id, product_id, product_name, qty, price, spec)
            VALUES (?, 8, '芒果班戟', 1, 22, '默认')
        """, (order2_id,))
        await db.execute("""
            INSERT INTO order_items (order_id, product_id, product_name, qty, price, spec)
            VALUES (?, 4, '杨枝甘露', 1, 22, '默认')
        """, (order2_id,))

        # 订单3: completed
        order3_id = now.strftime("%Y%m%d") + "003"
        await db.execute("""
            INSERT INTO orders (id, user_id, status, total, remark, created_at)
            VALUES (?, 1, 'completed', 28, '', datetime('now', '-1 day'))
        """, (order3_id,))
        await db.execute("""
            INSERT INTO order_items (order_id, product_id, product_name, qty, price, spec)
            VALUES (?, 7, '提拉米苏', 1, 28, '默认')
        """, (order3_id,))

        # 6. 创建消息通知
        await db.execute("""
            INSERT INTO notifications (merchant_id, type, title, content, read, created_at)
            VALUES (1, 'order', '新订单提醒', '您有1个新订单待处理', 0, datetime('now', '-1 hour'))
        """)
        await db.execute("""
            INSERT INTO notifications (merchant_id, type, title, content, read, created_at)
            VALUES (1, 'order', '订单完成', '订单#003已完成', 1, datetime('now', '-1 day'))
        """)

        await db.commit()
        print("测试数据初始化完成！")