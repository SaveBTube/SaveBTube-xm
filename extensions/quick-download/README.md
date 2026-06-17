# Bosco Tsang 快速下载浏览器扩展

此扩展示例支持 Chrome / Edge，在扩展弹窗中输入 Bosco Tsang 服务器地址、API Key 和下载链接，即可快速提交下载任务。

## 使用步骤

1. 进入 `Settings` 页面，创建一个 API Key。
2. 在浏览器扩展管理页面启用“开发者模式”。
3. 加载已解压的扩展程序，选择 `extensions/quick-download/` 目录。
4. 打开扩展：
   - 服务地址（例如 `http://localhost:8080`）
   - API Key
   - 下载链接（扩展会自动读取当前标签页 URL，也可以手动输入）
   - 质量
5. 点击“快速下载”提交任务。

## 右键菜单

扩展已集成右键菜单：

- 右键页面空白处选择“Bosco Tsang 快速下载当前页面”
- 右键链接选择“Bosco Tsang 快速下载链接”

菜单点击后会自动打开扩展弹窗并填充链接。

## API 说明

扩展调用接口：`POST /api/quick-download`

请求头：
- `Content-Type: application/json`
- `X-API-Key: <你的 API Key>`

请求体：
```json
{
  "url": "https://...",
  "quality": "best"
}
```

返回示例：
```json
{
  "status": "started",
  "task_id": "...",
  "platform": "YouTube"
}
```
