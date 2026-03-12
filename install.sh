#!/bin/bash
# Session Manager 安装脚本

set -e

echo "🚀 Claude Code Session Manager 安装脚本"
echo "========================================"
echo ""

# 检查 Claude Code 目录
CLAUDE_DIR="$HOME/.claude"
SKILL_DIR="$CLAUDE_DIR/skills/session-manager"

if [ ! -d "$CLAUDE_DIR" ]; then
    echo "❌ 错误: 未找到 Claude Code 配置目录: $CLAUDE_DIR"
    echo "请先安装并运行 Claude Code 一次"
    exit 1
fi

echo "✅ 找到 Claude Code 配置目录: $CLAUDE_DIR"

# 检查是否已安装
if [ -d "$SKILL_DIR" ]; then
    echo "⚠️  Session Manager 已安装"
    read -p "是否覆盖安装? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "安装已取消"
        exit 0
    fi
    echo "正在更新..."
else
    echo "正在安装 Session Manager..."
fi

# 创建目录
mkdir -p "$SKILL_DIR/scripts"

# 复制文件
echo "📦 复制文件..."
cp -r scripts/* "$SKILL_DIR/scripts/"
cp SKILL.md "$SKILL_DIR/"
cp README.md "$SKILL_DIR/" 2>/dev/null || true

# 设置权限
echo "🔧 设置权限..."
chmod +x "$SKILL_DIR/scripts/"*.py
chmod +x "$SKILL_DIR/scripts/"*.sh

# 验证安装
echo "✅ 验证安装..."
if [ -f "$SKILL_DIR/scripts/list_sessions.py" ]; then
    echo "  ✓ list_sessions.py"
fi
if [ -f "$SKILL_DIR/scripts/switch_session.sh" ]; then
    echo "  ✓ switch_session.sh"
fi
if [ -f "$SKILL_DIR/scripts/rename_session.py" ]; then
    echo "  ✓ rename_session.py"
fi
if [ -f "$SKILL_DIR/scripts/toggle_favorite.py" ]; then
    echo "  ✓ toggle_favorite.py"
fi
if [ -f "$SKILL_DIR/scripts/delete_session.py" ]; then
    echo "  ✓ delete_session.py"
fi
if [ -f "$SKILL_DIR/scripts/search_session.py" ]; then
    echo "  ✓ search_session.py"
fi
if [ -f "$SKILL_DIR/SKILL.md" ]; then
    echo "  ✓ SKILL.md"
fi

echo ""
echo "🎉 安装完成!"
echo ""
echo "使用以下命令开始使用："
echo "  /session list        - 列出所有会话"
echo "  /session switch <id> - 切换到指定会话"
echo "  /session favorite <id> - 收藏会话"
echo ""
echo "查看完整文档: $SKILL_DIR/README.md"
