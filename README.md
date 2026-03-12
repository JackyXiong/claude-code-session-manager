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

## 使用方式

**用自然语言表达意图**，Claude 会自动执行对应操作：

```
列出所有 session
查看我的会话
切换到 session a1b2c3d
重命名 session a1b2c3d 为"修复登录Bug"
收藏 session a1b2c3d
搜索包含 api 的 session
删除 session a1b2c3d
```

## 支持的自然语言指令

| 意图 | 示例说法 |
|-----|---------|
| 列出/查看 | "列出所有 session"、"查看我的会话"、"有哪些 session" |
| 切换/打开 | "切换到 session xxx"、"打开 session xxx"、"恢复之前的会话" |
| 重命名 | "重命名 session xxx"、"给 session 起个名字"、"自动生成名称" |
| 收藏 | "收藏 session xxx"、"标记为重要"、"取消收藏" |
| 删除 | "删除 session xxx"、"清理 session"、"永久删除" |
| 搜索 | "搜索包含 xxx 的 session"、"查找 session" |

## 功能详解

### 列出 Session

显示 ID、项目名称、摘要、消息数、最后活跃时间和收藏状态。

```
ID        项目名称              名称/摘要              消息数    最后活跃        收藏
--------  --------------------  -------------------    -------  --------------  ----
a1b2c3d   ask-me-anything       Session管理器设计      45       2分钟前         ⭐
e4f5g6h   report-api            API 项目分析           23       1小时前
```

### 切换 Session

在新终端窗口中切换到指定 session。支持 macOS (Terminal.app) 和 Linux (gnome-terminal/konsole/xterm)。

### 重命名 Session

重命名 session。如果不指定名称，会自动生成智能名称。

**智能命名规则：**
- 基于第一条用户消息
- 识别关键词：修复、添加、创建、删除、重构、分析、测试等
- 限制长度在 30 字符以内

### 收藏 Session

切换 session 的收藏状态。收藏状态在列表中显示为 ⭐。

### 搜索 Session

搜索 session，支持项目路径、名称、内容搜索。

### 删除 Session

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

## 系统要求

- macOS 或 Linux
- Python 3.8+
- Claude Code

## License

MIT - 详见 [LICENSE](docs/LICENSE)
