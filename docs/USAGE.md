# 系统使用教程

## 1. 登录与初始设置

1. 访问系统登录页面。
2. 如果是首次使用，默认管理员账号：`admin` / `admin123`。
3. 登录后建议立即修改管理员密码，并根据需要创建普通用户。
4. 管理员可在“设置”页面中配置代理、API Key 和邀请码。

## 2. 立即下载

在首页的“快速下载”栏：

1. 在输入框中粘贴要下载的链接。
2. 支持平台包括：
   - YouTube
   - X (Twitter)
   - QQ音乐
   - 小红书
   - 抖音
   - Bilibili
   - 微博
   - 以及 yt-dlp 支持的更多平台。
3. 选择下载类型：
   - `最佳质量`：下载视频和音频的最佳组合
   - `1080p`：优先下载 1080p 视频
   - `720p`：优先下载 720p 视频
   - `仅音频`：提取音频并保存为 MP3
   - `仅图片`：下载页面中的图片内容
4. 点击“立即下载”，系统会将任务添加到下载队列。

## 3. 下载管理

在“下载管理”页面可以：

- 查看下载中、已完成、失败的任务数量
- 根据平台、状态、类型筛选任务
- 重试失败任务、重命名任务、删除任务

## 4. 支持的下载类型

系统支持：

- 视频下载（4K / 1080p / 720p 等）
- 音频提取（MP3）
- 图片下载

如果某个平台 URL 支持图片下载，可选择“仅图片”进行下载。

## 5. Cookies 登录下载

部分平台在未登录或区域限制下需要 Cookies 才能正常下载高清内容，尤其是：

- QQ音乐
- X / Twitter
- YouTube Premium 内容
- 小红书
- 微博

### 5.1 导出 Cookies 步骤

1. 在 Chrome / Edge 中安装 `Get cookies.txt LOCALLY` 或类似扩展。
2. 登录目标平台账号。
3. 使用扩展导出 Cookies，保存为 Netscape 格式文本文件。
4. 将文件放入项目根目录的 `cookies/` 目录。

### 5.2 文件命名规则

将 Cookies 文件命名为对应平台：

- `youtube.txt`
- `x.txt`
- `qqmusic.txt`
- `xiaohongshu.txt`
- `weibo.txt`
- `bilibili.txt`
- `douyin.txt`
- `kuaishou.txt`
- `instagram.txt`
- `tiktok.txt`

### 5.3 示例

如果你需要下载 QQ音乐内容：

1. 登录 QQ音乐网页。
2. 导出 Cookies。
3. 将文件重命名为 `qqmusic.txt`。
4. 保存到 `cookies/` 目录。
5. 在系统中使用 QQ音乐链接发起下载。

## 6. 管理员权限说明

- 只有管理员可以访问“设置”中的代理配置。
- 普通用户无法修改代理设置。

## 7. 配置文件 BoscoTsang.toml

项目根目录新增 `BoscoTsang.toml`，用于配置代理和运行时行为。

示例内容：

```toml
[proxy]
enabled = true
mode = "auto"
http = "http://127.0.0.1:8080"
https = "http://127.0.0.1:8080"
bypass_cidrs = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8"]

[download]
download_dir = ""

[logging]
level = "INFO"
```

- `proxy.enabled`：是否启用代理。
- `proxy.mode`：`global` 为全局代理，`none` 为禁用代理，`auto` 为仅对国外目标走代理，国内/本地目标直连。
- `proxy.http` / `proxy.https`：代理服务器地址。
- `proxy.bypass_cidrs`：本地/国内网段，命中这些地址时会绕过代理。

修改配置后，重启服务即可生效。

## 8. 常见问题

### 下载失败怎么办？

- 检查链接是否正确。
- 如果是登录内容，按“Cookies 下载”说明导出 Cookies。
- 检查代理设置是否正确，或尝试关闭代理。

### 如何下载图片？

在“快速下载”选择“仅图片”，并粘贴包含图片内容的链接。

### 如何下载音频？

选择“仅音频”，系统会提取并保存音频文件。

## 8. CLI 使用

如果你使用本地 CLI：

```bash
bosco url "https://youtube.com/watch?v=xxx"
bosco url "https://x.com/xxx"
bosco url "https://y.qq.com/n/xxx"
```

> 如果需要指定下载类型，当前前端界面提供了“最佳质量 / 1080p / 720p / 仅音频 / 仅图片”选项。
