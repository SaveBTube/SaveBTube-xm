# 📝 文档更新 - 快速参考

## 🚀 一行命令更新所有文档

```powershell
.\scripts\update-docs.ps1 -Version "v0.X.X" -Changes @("变更1", "变更2") -UpdateManual
```

---

## 📋 常用场景

### 场景 1：发布新功能

```powershell
.\scripts\update-docs.ps1 -Version "v0.4.0" `
  -ChangeType "feat" `
  -Changes @("新增 TikTok 支持", "新增批量下载") `
  -UpdateManual
```

### 场景 2：修复 Bug

```powershell
.\scripts\update-docs.ps1 -Version "v0.3.1" `
  -ChangeType "fix" `
  -Changes @("修复代理问题", "修复文档访问")
```

### 场景 3：仅更新 CHANGELOG

```powershell
.\scripts\update-docs.ps1 -Version "v0.3.2" `
  -Changes @("文档系统优化")
```

---

## 🔄 完整发布流程

```powershell
# 1. 更新文档
.\scripts\update-docs.ps1 -Version "v0.4.0" `
  -Changes @("新功能...") `
  -UpdateManual

# 2. 重新构建
docker-compose up -d --build

# 3. 推送镜像
docker push boscotom/bosco-tsang:v0.4.0
docker push boscotom/bosco-tsang:latest

# 4. 创建标签
git tag v0.4.0
git push origin v0.4.0
```

---

## 📊 参数速查

| 参数 | 说明 | 示例 |
|------|------|------|
| `-Version` | 版本号 | `v0.4.0` |
| `-ChangeType` | 变更类型 | `feat`, `fix`, `perf`, `docs` |
| `-Changes` | 变更列表 | `@("变更1", "变更2")` |
| `-UpdateManual` | 更新使用手册 | （开关） |
| `-AutoCommit` | 自动提交 Git | （开关） |

---

## 💡 提示

- ✅ 脚本位置：`scripts/update-docs.ps1`
- ✅ 自动更新：CHANGELOG.md + USAGE_MANUAL.md
- ✅ 重新构建后文档会自动打包到 Docker 镜像
- ✅ 详细文档：`docs/DOCUMENT_UPDATE_GUIDE.md`

---

**每次更新后运行一行命令，文档自动同步！** 🎉
