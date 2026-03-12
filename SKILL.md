---
name: session-manager
description: Session 管理器 - 跨项目管理和切换 Claude Code 会话。当用户需要列出所有 session、切换 session、重命名 session、收藏 session、删除 session 或搜索 session 时使用。支持 /session list, /session switch, /session rename, /session favorite, /session delete, /session search 等命令。
---

# Session 管理器

一个用于跨项目管理和切换 Claude Code 会话的 Skill。

## 功能

- **列出所有 Session**：跨项目查看所有会话，显示项目路径、消息数量、最后活跃时间、收藏状态
- **切换 Session**：快速在新终端窗口中恢复指定会话
- **智能命名**：自动根据对话内容生成会话名称
- **收藏管理**：标记重要会话，方便快速访问
- **搜索**：按项目路径、名称、标签搜索会话
- **删除**：安全删除会话（支持移动到回收站）

## 命令

### /session list
列出所有会话，按最后活跃时间倒序排列。

**示例输出：**
```
ID        项目名称              名称/摘要              消息数    最后活跃        收藏
--------  --------------------  -------------------    -------  --------------  ----
a1b2c3d   ask-me-anything       Session管理器设计      45       2分钟前         ⭐
e4f5g6h   report-api            添加数据导出功能       23       1小时前
i7j8k9l   test                  测试新项目             8        昨天            ⭐
```

### /session switch <id>
在新终端窗口中切换到指定会话。

**示例：**
- `/session switch a1b2c3d`

### /session rename <id> [name]
重命名会话。如果 name 为空，自动生成智能名称。

**示例：**
- `/session rename a1b2c3d "修复登录Bug"`
- `/session rename a1b2c3d` （自动生成名称）

### /session favorite <id>
切换会话的收藏状态。

**示例：**
- `/session favorite a1b2c3d`

### /session delete <id>
删除指定会话。

**示例：**
- `/session delete a1b2c3d`

### /session search <keyword>
搜索会话。

**示例：**
- `/session search "登录"`
- `/session search "api"`

## 技术实现

### Session 数据来源

Claude Code 的 session 数据存储在：
- `~/.claude/projects/<encoded-project-path>/<sessionId>.jsonl`
- `~/.claude/history.jsonl` - 包含命令历史记录

### 元数据存储

额外的 session 元数据存储在 `~/.claude/session-metadata.json`：
```json
{
  "sessions": {
    "<sessionId>": {
      "name": "用户自定义名称",
      "is_favorite": true,
      "tags": ["重要", "待续"],
      "summary": "修复登录bug的会话"
    }
  }
}
```

## 使用流程

1. **查看所有会话**：`/session list`
2. **切换到指定会话**：`/session switch <id>`
3. **标记重要会话**：`/session favorite <id>`
4. **整理会话名称**：`/session rename <id> "新名称"`

## 实现细节

执行命令时，使用对应的脚本：
- `/session list` → `python ~/.claude/skills/session-manager/scripts/list_sessions.py`
- `/session switch <id>` → `bash ~/.claude/skills/session-manager/scripts/switch_session.sh <id>`
- `/session rename <id> [name]` → `python ~/.claude/skills/session-manager/scripts/rename_session.py <id> [name]`
- `/session favorite <id>` → `python ~/.claude/skills/session-manager/scripts/toggle_favorite.py <id>`
- `/session delete <id>` → `python ~/.claude/skills/session-manager/scripts/delete_session.py <id>`
- `/session search <keyword>` → `python ~/.claude/skills/session-manager/scripts/search_session.py <keyword>`

## 智能命名规则

自动命名基于以下规则：
1. 提取用户第一条实质性消息（跳过 /clear, /init 等命令）
2. 识别关键词：修复、添加、创建、删除、重构、分析、测试等
3. 结合文件操作历史生成摘要
4. 限制长度在 30 字符以内
