#!/bin/bash

# ===========================================
# Bosco Tsang - 推送前清理脚本
# 过滤敏感信息，确保安全推送
# ===========================================

set -e  # 遇到错误立即退出

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}  Bosco Tsang - 推送前清理工具${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# 确认操作
echo -e "${YELLOW}⚠️  此操作将清除以下敏感信息：${NC}"
echo -e "  • Cookies 文件内容"
echo -e "  • 日志文件内容"
echo -e "  • 测试下载文件"
echo -e "  • 临时文件"
echo -e "  • Python 缓存"
echo ""

read -p "是否继续？(y/N): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}操作已取消${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}🧹 开始清理...${NC}"
echo ""

# 1. 清除 Cookies 文件
echo -e "${BLUE}[1/6] 清除 Cookies 文件...${NC}"
if [ -d "cookies" ]; then
    find ./cookies -name "*.txt" -type f -exec sh -c '> "$1"' _ {} \;
    echo -e "  ${GREEN}✓${NC} Cookies 文件已清空"
else
    echo -e "  ${YELLOW}⚠${NC} cookies 目录不存在，跳过"
fi

# 2. 清除日志文件
echo -e "${BLUE}[2/6] 清除日志文件...${NC}"
if [ -d "logs" ]; then
    find ./logs -name "*.log" -type f -exec sh -c '> "$1"' _ {} \;
    echo -e "  ${GREEN}✓${NC} 日志文件已清空"
else
    echo -e "  ${YELLOW}⚠${NC} logs 目录不存在，跳过"
fi

# 3. 清除测试下载文件
echo -e "${BLUE}[3/6] 清除测试下载文件...${NC}"
if [ -d "downloads" ]; then
    find ./downloads -mindepth 1 -delete 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} 测试下载文件已删除"
else
    echo -e "  ${YELLOW}⚠${NC} downloads 目录不存在，跳过"
fi

# 4. 清除临时文件
echo -e "${BLUE}[4/6] 清除临时文件...${NC}"
rm -f /tmp/xtwitter_cookies.txt 2>/dev/null || true
rm -f /tmp/*.txt 2>/dev/null || true
echo -e "  ${GREEN}✓${NC} 临时文件已清除"

# 5. 清除 Python 缓存
echo -e "${BLUE}[5/6] 清除 Python 缓存...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo -e "  ${GREEN}✓${NC} Python 缓存已清除"

# 6. 清除 Node 缓存
echo -e "${BLUE}[6/6] 清除 Node 缓存...${NC}"
if [ -d "frontend/node_modules/.cache" ]; then
    rm -rf frontend/node_modules/.cache
    echo -e "  ${GREEN}✓${NC} Node 缓存已清除"
else
    echo -e "  ${YELLOW}⚠${NC} Node 缓存不存在，跳过"
fi

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  ✅ 清理完成！${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""

# 显示清理后的状态
echo -e "${BLUE}📊 清理后状态：${NC}"
echo ""

# 检查 Cookies 文件
if [ -d "cookies" ]; then
    cookie_count=$(find ./cookies -name "*.txt" -type f | wc -l)
    cookie_size=$(du -sh cookies 2>/dev/null | cut -f1)
    echo -e "  Cookies: ${cookie_count} 个文件, 大小: ${cookie_size}"
fi

# 检查日志文件
if [ -d "logs" ]; then
    log_count=$(find ./logs -name "*.log" -type f | wc -l)
    log_size=$(du -sh logs 2>/dev/null | cut -f1)
    echo -e "  日志: ${log_count} 个文件, 大小: ${log_size}"
fi

# 检查下载文件
if [ -d "downloads" ]; then
    download_count=$(find ./downloads -type f 2>/dev/null | wc -l)
    download_size=$(du -sh downloads 2>/dev/null | cut -f1)
    echo -e "  下载: ${download_count} 个文件, 大小: ${download_size}"
fi

echo ""
echo -e "${YELLOW}⚠️  提醒：${NC}"
echo -e "  • 请检查 .env 文件是否包含敏感信息"
echo -e "  • 请确认 .gitignore 已正确配置"
echo -e "  • 建议使用 git status 检查变更"
echo ""
echo -e "${GREEN}现在可以安全地提交和推送代码了！${NC}"
