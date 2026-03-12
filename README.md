# Claude Code Session Manager

跨项目管理和切换 Claude Code 会话的 Skill。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-green.svg)](https://claude.ai/code)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 功能

- 📋 **跨项目列表** - 查看所有项目的 session，按最后活跃时间排序
- ⚡ **快速切换** - 在新终端窗口中恢复指定 session
- 🏷️ **智能命名** - 根据对话内容自动生成 session 名称
- ⭐ **收藏管理** - 标记重要 session
- 🔍 **全文搜索** - 按项目路径、名称、内容搜索

## 安装

```bash
git clone https://github.com/yourusername/claude-code-session-manager.git
cd claude-code-session-manager
./install.sh
```

或手动安装：

```bash
cp -r session-manager ~/.claude/skills/
chmod +x ~/.claude/skills/session-manager/scripts/*
```

## 使用

```bash
# 列出所有 session
/session list

# 切换到指定 session（新开终端）
/session switch <id>

# 重命名 session
/session rename <id> "新名称"

# 收藏/取消收藏
/session favorite <id>

# 搜索 session
/session search <关键词>

# 删除 session
/session delete <id>
```

## 命令详解

### /session list

列出所有 session，显示 ID、项目名称、摘要、消息数、最后活跃时间和收藏状态。

```
ID        项目名称              名称/摘要              消息数    最后活跃        收藏
--------  --------------------  -------------------    -------  --------------  ----
a1b2c3d   ask-me-anything       Session管理器设计      45       2分钟前         ⭐
e4f5g6h   report-api            API 项目分析           23       1小时前
```

### /session switch <id>

在新终端窗口中切换到指定 session。支持 macOS (Terminal.app) 和 Linux (gnome-terminal/konsole/xterm)。

### /session rename <id> [name]

重命名 session。如果不指定 name，会自动生成智能名称。

### /session favorite <id>

切换 session 的收藏状态。收藏状态在列表中显示为 ⭐。

### /session search <keyword>

搜索 session，支持项目路径、名称、内容搜索。

### /session delete <id>

删除 session。默认移动到回收站 `~/.claude/sessions/trash/`，加 `--permanent` 永久删除。

## 项目结构

```
session-manager/
├── SKILL.md              # Skill 定义
├── install.sh            # 安装脚本
├── scripts/
│   ├── list_sessions.py
│   ├── switch_session.sh
│   ├── rename_session.py
│   ├── toggle_favorite.py
│   ├── delete_session.py
│   └── search_session.py
├── docs/
│   ├── CHANGELOG.md
│   └── LICENSE
└── README.md
```

## 智能命名规则

自动命名基于第一条用户消息：
- 识别关键词：修复、添加、创建、删除、重构、分析、测试、实现、优化等
- 结合操作内容生成摘要
- 限制长度在 30 字符以内

## 系统要求

- macOS 或 Linux
- Python 3.8+
- Claude Code

## License

MIT - 详见 [LICENSE](docs/LICENSE)
