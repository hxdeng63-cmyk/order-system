# Docker 部署常见问题 (Q&A)

## 1. 本地开发环境快速启动

```bash
# 方式一：直接运行
python -m uvicorn main:app --host 127.0.0.1 --port 8087

# 方式二：Docker Compose
docker-compose up --build

# 方式三：生产环境（Nginx反向代理）
docker-compose -f deploy/docker-compose-production.yml up --build -d
```

## 2. 构建镜像

```bash
# 开发环境镜像
docker build -t order-system-backend:dev .

# 生产环境镜像（多阶段构建，更小）
docker build -t order-system-backend:latest --target runner .

# 带标签
docker build -t order-system-backend:1.0.0 .
```

## 3. 运行容器

```bash
# 前台运行
docker-compose up --build

# 后台运行
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 查看运行状态
docker-compose ps
```

## 4. 进入容器调试

```bash
# 进入容器 bash
docker exec -it order-system-backend bash

# 检查健康状态
docker inspect --format='{{.State.Health.Status}}' order-system-backend

# 查看环境变量
docker exec order-system-backend env
```

## 5. 数据库持久化

数据存储在 Docker volumes 中：
- `app_data` - SQLite 数据库文件
- `app_uploads` - 上传的文件

```bash
# 查看 volumes
docker volume ls

# 备份数据
docker run --rm -v order-system-backend_app_data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data

# 恢复数据
docker run --rm -v order-system-backend_app_data:/data -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz -C /
```

## 6. 健康检查

```bash
# 手动检查
curl http://localhost:8088/health

# Docker healthcheck 状态
docker inspect --format='{{if .State.Health.Status}}{{.State.Health.Status}}{{else}}no healthcheck{{end}}' order-system-backend
```

## 7. 常见问题排查

### 端口冲突
```bash
# 检查端口占用
netstat -ano | grep 8088

# 或使用 Docker
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

### 权限问题
容器使用非 root 用户 (appuser:1000) 运行。如果需要写入权限：
```bash
# 修改本地目录权限
chmod -R 777 ./data ./static/uploads

# 或在 docker-compose.yml 中指定用户
user: "1000:1000"
```

### 镜像构建失败
```bash
# 清理 Docker 缓存
docker builder prune -a

# 重新构建
docker build --no-cache -t order-system-backend:latest .
```

### 容器无法启动
```bash
# 查看详细日志
docker-compose logs backend

# 检查 env 文件
cat .env
```

## 8. 生产环境部署

```bash
# 1. 配置生产环境变量
cp .env .env.production
vim .env.production  # 修改 SECRET_KEY, DATABASE_URL 等

# 2. 构建并启动
docker-compose -f deploy/docker-compose-production.yml up --build -d

# 3. 检查健康状态
curl http://127.0.0.1:8088/health

# 4. 查看日志
docker-compose -f deploy/docker-compose-production.yml logs -f
```

## 9. 更新部署

```bash
# 拉取最新代码后重新构建
docker-compose -f deploy/docker-compose-production.yml up --build -d

# 或只重建特定服务
docker-compose -f deploy/docker-compose-production.yml build backend
docker-compose -f deploy/docker-compose-production.yml up -d backend
```

## 10. 停止和清理

```bash
# 停止容器（保留数据）
docker-compose stop

# 停止并删除容器
docker-compose down

# 停止并删除容器和数据卷（慎用！）
docker-compose down -v
```

## 11. 多架构构建 (可选)

```bash
# 构建 ARM64 和 AMD64 双架构
docker buildx build --platform linux/amd64,linux/arm64 \
  -t order-system-backend:latest \
  --push .
```

## 12. 环境变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `PORT` | 服务端口 | `8088` |
| `PYTHONUNBUFFERED` | Python 日志实时输出 | `1` |
| `LOG_LEVEL` | 日志级别 | `INFO`, `DEBUG` |

## 13. Docker 与本地代码同步

开发时使用 volume 挂载代码：
```yaml
# docker-compose.yml 中已配置
volumes:
  - ./:/app  # 开发时取消注释这行
```

## 14. 性能调优

```yaml
# docker-compose.yml 中可添加
deploy:
  resources:
    limits:
      memory: 512M
    reservations:
      memory: 256M
```

## 15. 安全建议

1. 生产环境使用 `127.0.0.1:8088` 绑定端口
2. 不在 volume 中存储敏感文件
3. 定期更新基础镜像：`docker pull python:3.11-slim`
4. 使用只读 rootfs：[Readonly Rootfs](https://docs.docker.com/engine/security/#the-readonly-option)
