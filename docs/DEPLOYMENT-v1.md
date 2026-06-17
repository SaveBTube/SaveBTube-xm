# 部署指南

## 前置要求

- Docker 20.10+
- Docker Compose v2+
- （可选）公网 IP 或域名（用于 Bot Webhook）

## 方式一：标准部署

```bash
git clone -b dev-improve https://github.com/SaveBTube/SaveBTube-xm.git
cd SaveBTube-xm
docker compose up -d --build
```

访问 `http://localhost:8080`，默认账号 `admin` / `admin123`。

## 方式二：包含 QQ Bot

```bash
docker compose --profile qq up -d --build
```

### QQ Bot（Lagrange）配置步骤

1. 启动后查看日志获取登录二维码：
```bash
docker compose --profile qq logs -f qq-bot
```

2. 编辑配置文件：
```bash
vim qq-bot-data/appsettings.json
```

3. 配置 HTTP 上报：
```json
{
  "Implementations": [{
    "Type": "Http",
    "Host": "*",
    "Port": 8080,
    "MessageServers": [{
      "Type": "HttpPost",
      "Url": "http://bosco-tsang:8000/api/bot/qq/webhook"
    }]
  }]
}
```

4. 重启 QQ Bot：
```bash
docker compose --profile qq restart qq-bot
```

## 方式三：HTTPS 反向代理（Nginx）

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket（如果启用）
    location /ws {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 数据备份

```bash
# 备份所有数据
tar -czf bosco-backup-$(date +%Y%m%d).tar.gz \
    downloads/ cookies/ data/ logs/

# 恢复
tar -xzf bosco-backup-*.tar.gz
```

## 更新

```bash
cd SaveBTube-xm
git pull origin dev-improve
docker compose up -d --build
```

## 常用命令

```bash
# 查看日志
docker compose logs -f bosco-tsang

# 重启
docker compose restart

# 停止
docker compose down

# 查看状态
docker compose ps
```
