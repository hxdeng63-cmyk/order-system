"""
图片上传模块 - 阿里云OSS存储
"""

import os
import uuid
from datetime import datetime


def _get_oss_config():
    """从环境变量获取 OSS 配置"""
    return {
        "bucket": os.environ.get("OSS_BUCKET", "tempduanju"),
        "endpoint": os.environ.get("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com"),
        "access_key_id": os.environ.get("OSS_ACCESS_KEY_ID", ""),
        "access_key_secret": os.environ.get("OSS_ACCESS_KEY_SECRET", ""),
        "region": os.environ.get("OSS_REGION", "cn-beijing"),
    }


def _generate_filename(original_filename: str) -> str:
    """生成唯一文件名"""
    ext = _get_extension(original_filename)
    timestamp = int(datetime.now().timestamp())
    unique = uuid.uuid4().hex[:8]
    return f"{timestamp}_{unique}{ext}"


def _get_extension(filename: str) -> str:
    """获取文件扩展名"""
    import os
    ext = os.path.splitext(filename)[1] if filename else ''
    return ext.lower() if ext else '.jpg'


def save_file(file_content: bytes, original_filename: str) -> str:
    """
    保存文件到阿里云OSS

    Args:
        file_content: 文件二进制内容
        original_filename: 原始文件名

    Returns:
        文件访问URL
    """
    import oss2

    config = _get_oss_config()
    auth = oss2.Auth(config['access_key_id'], config['access_key_secret'])
    bucket = oss2.Bucket(auth, config['endpoint'], config['bucket'])

    filename = _generate_filename(original_filename)

    # 上传文件
    bucket.put_object(filename, file_content)

    # 返回OSS访问URL
    return f"https://{config['bucket']}.{config['endpoint']}/{filename}"


def delete_file(file_url: str) -> bool:
    """
    从OSS删除文件

    Args:
        file_url: OSS文件访问URL

    Returns:
        是否删除成功
    """
    import oss2
    from urllib.parse import urlparse

    try:
        config = _get_oss_config()
        auth = oss2.Auth(config['access_key_id'], config['access_key_secret'])
        bucket = oss2.Bucket(auth, config['endpoint'], config['bucket'])

        # 从URL中提取文件名
        parsed = urlparse(file_url)
        filename = parsed.path.lstrip('/')

        bucket.delete_object(filename)
        return True
    except Exception as e:
        print(f"OSS删除失败: {e}")
        return False


# 向后兼容
save_local_file = save_file
