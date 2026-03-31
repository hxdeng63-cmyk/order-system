from fastapi import APIRouter, UploadFile, File, HTTPException
from services.oss import save_file
import aiofiles

router = APIRouter()

# 文件大小限制 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# 允许的文件类型
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]

# 允许的扩展名
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


@router.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    上传图片接口
    返回文件访问路径
    """
    # 检查文件类型
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    # 检查文件扩展名
    import os
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的文件扩展名")

    # 读取文件内容
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过5MB限制")

    # 验证文件大小
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="文件不能为空")

    # 验证文件魔数 (magic bytes)
    magic_map = {
        b"\xff\xd8\xff": "jpeg",
        b"\x89PNG": "png",
        b"GIF87a": "gif",
        b"GIF89a": "gif",
        b"RIFF": "webp",  # WebP starts with RIFF....WEBP
    }
    file_magic = content[:4]
    is_valid = False
    for magic, fmt in magic_map.items():
        if file_magic.startswith(magic):
            is_valid = True
            break
    if not is_valid:
        raise HTTPException(status_code=400, detail="文件格式无效或已损坏")

    # 保存文件（根据配置自动选择本地或OSS）
    file_path = save_file(content, file.filename)

    return {"code": 200, "message": "上传成功", "data": {"url": file_path}}
