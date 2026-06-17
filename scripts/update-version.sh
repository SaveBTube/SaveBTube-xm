#!/bin/bash

# ===========================================
# Bosco Tsang - 版本号自动更新脚本
# 遵循语义化版本规范
# ===========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}  Bosco Tsang - 版本更新工具${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# 获取当前版本号（从 main.py）
CURRENT_VERSION=$(grep -oP 'version="\K[0-9]+\.[0-9]+\.[0-9]+' backend/main.py 2>/dev/null || echo "0.3.0")

# 解析版本号
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

echo -e "当前版本: ${GREEN}v$CURRENT_VERSION${NC}"
echo ""

# 显示更新类型选项
echo -e "${YELLOW}请选择更新类型：${NC}"
echo -e "  1. ${GREEN}修订号 (PATCH)${NC} - Bug 修复 (0.3.0 → 0.3.1)"
echo -e "  2. ${BLUE}次版本号 (MINOR)${NC} - 新功能 (0.3.0 → 0.4.0)"
echo -e "  3. ${RED}主版本号 (MAJOR)${NC} - 破坏性变更 (0.3.0 → 1.0.0)"
echo ""

read -p "输入选项 (1/2/3): " choice

case $choice in
  1)
    PATCH=$((PATCH + 1))
    UPDATE_TYPE="PATCH"
    ;;
  2)
    MINOR=$((MINOR + 1))
    PATCH=0
    UPDATE_TYPE="MINOR"
    ;;
  3)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    UPDATE_TYPE="MAJOR"
    ;;
  *)
    echo -e "${RED}❌ 无效选项${NC}"
    exit 1
    ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  版本更新确认${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo -e "更新类型: ${YELLOW}$UPDATE_TYPE${NC}"
echo -e "版本变更: ${RED}v$CURRENT_VERSION${NC} → ${GREEN}v$NEW_VERSION${NC}"
echo ""

# 确认更新
read -p "是否继续？(y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}操作已取消${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}🔄 开始更新版本...${NC}"
echo ""

# 1. 更新 backend/main.py 中的版本号
echo -e "${BLUE}[1/3] 更新 backend/main.py...${NC}"
if [ -f "backend/main.py" ]; then
    sed -i "s/version=\"$CURRENT_VERSION\"/version=\"$NEW_VERSION\"/g" backend/main.py
    echo -e "  ${GREEN}✓${NC} backend/main.py 已更新"
else
    echo -e "  ${YELLOW}⚠${NC} backend/main.py 不存在，跳过"
fi

# 2. 更新前端 package.json 中的版本号
echo -e "${BLUE}[2/3] 更新 frontend/package.json...${NC}"
if [ -f "frontend/package.json" ]; then
    # 使用 node 或 sed 更新 JSON
    if command -v node &> /dev/null; then
        node -e "
            const fs = require('fs');
            const pkg = JSON.parse(fs.readFileSync('frontend/package.json', 'utf8'));
            pkg.version = '$NEW_VERSION';
            fs.writeFileSync('frontend/package.json', JSON.stringify(pkg, null, 2) + '\n');
        "
        echo -e "  ${GREEN}✓${NC} frontend/package.json 已更新"
    else
        # 备用方案：使用 sed
        sed -i "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/g" frontend/package.json
        echo -e "  ${GREEN}✓${NC} frontend/package.json 已更新 (sed)"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} frontend/package.json 不存在，跳过"
fi

# 3. 更新 CHANGELOG.md
echo -e "${BLUE}[3/3] 更新 CHANGELOG.md...${NC}"
if [ -f "CHANGELOG.md" ]; then
    TODAY=$(date +%Y-%m-%d)
    
    # 检查是否已有该版本的标题
    if grep -q "## \[v$NEW_VERSION\]" CHANGELOG.md; then
        echo -e "  ${YELLOW}⚠${NC} CHANGELOG.md 中已存在 v$NEW_VERSION 标题"
    else
        # 在 "[未发布]" 后添加新版本标题
        sed -i "s/## \[未发布\]/## [未发布]\n\n## [v$NEW_VERSION] - $TODAY/" CHANGELOG.md
        echo -e "  ${GREEN}✓${NC} CHANGELOG.md 已添加 v$NEW_VERSION 标题"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} CHANGELOG.md 不存在，跳过"
fi

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  ✅ 版本更新完成！${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""

# 显示后续步骤
echo -e "${YELLOW}📝 后续步骤：${NC}"
echo ""
echo -e "  1. 更新 CHANGELOG.md 中的变更内容"
echo -e "  2. 提交更改:"
echo -e "     ${BLUE}git add .${NC}"
echo -e "     ${BLUE}git commit -m \"chore: 版本更新至 v$NEW_VERSION\"${NC}"
echo -e "  3. 打标签:"
echo -e "     ${BLUE}git tag v$NEW_VERSION${NC}"
echo -e "     ${BLUE}git push origin v$NEW_VERSION${NC}"
echo -e "  4. 推送代码:"
echo -e "     ${BLUE}git push origin main${NC}"
echo ""
echo -e "${GREEN}新版本: v$NEW_VERSION${NC}"
