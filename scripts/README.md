# 🛠️ 工具脚本

## 📁 脚本列表

### 数据库工具

| 脚本 | 说明 | 用途 |
|------|------|------|
| [check_db.py](check_db.py) | 数据库检查 | 检查数据库状态和数据 |
| [create_test_data.py](create_test_data.py) | 创建测试数据 | 生成完整的测试数据 |
| [create_test_data_simple.py](create_test_data_simple.py) | 创建测试数据（简化版） | 生成基础测试数据 |

### 文档更新工具

| 脚本 | 说明 | 用途 |
|------|------|------|
| [update-docs.ps1](update-docs.ps1) | 文档自动更新 | 版本发布时自动更新文档 |

### 版本更新脚本

位置：`../releases/`

| 脚本 | 说明 |
|------|------|
| [update-v0.4.0.ps1](../releases/update-v0.4.0.ps1) | v0.4.0 文档更新 |
| [update-v0.4.1.ps1](../releases/update-v0.4.1.ps1) | v0.4.1 文档更新 |

---

## 🚀 使用方法

### 数据库检查

```bash
cd scripts
python check_db.py
```

### 创建测试数据

```bash
cd scripts
python create_test_data.py
```

### 创建测试数据（简化版）

```bash
cd scripts
python create_test_data_simple.py
```

### 更新文档

```powershell
# 创建版本更新脚本
# 参考 releases/update-v0.4.1.ps1

# 执行更新
.\releases\update-v0.4.1.ps1
```

---

## 📝 注意事项

1. **数据库脚本**
   - 确保 Docker 容器正在运行
   - 备份数据库后再执行写操作

2. **文档更新脚本**
   - 需要 PowerShell 执行权限
   - 使用 `ExecutionPolicy Bypass` 执行

3. **测试数据**
   - 仅用于开发测试
   - 生产环境不要使用

---

**最后更新：** 2026-06-16
