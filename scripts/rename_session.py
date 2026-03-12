#!/usr/bin/env python3
"""
重命名 Session
"""

import json
import os
import sys
import re
from pathlib import Path


def get_claude_dir():
    """获取 Claude Code 配置目录"""
    return Path.home() / ".claude"


def load_metadata():
    """加载 session 元数据"""
    metadata_path = get_claude_dir() / "session-metadata.json"
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"sessions": {}}


def save_metadata(metadata):
    """保存 session 元数据"""
    metadata_path = get_claude_dir() / "session-metadata.json"
    try:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving metadata: {e}", file=sys.stderr)
        return False


def find_full_session_id(short_id):
    """根据短 ID 查找完整 ID"""
    projects_dir = get_claude_dir() / "projects"

    if not projects_dir.exists():
        return None

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        for session_file in project_dir.glob("*.jsonl"):
            session_id = session_file.stem
            if session_id.startswith(short_id):
                return session_id

    return None


def parse_session_file(session_id):
    """解析 session 文件获取信息"""
    projects_dir = get_claude_dir() / "projects"

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        session_file = project_dir / f"{session_id}.jsonl"
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                user_messages = []
                for line in lines:
                    try:
                        data = json.loads(line)
                        if data.get('type') == 'user':
                            content = data.get('message', {}).get('content', '')
                            if isinstance(content, list):
                                for item in content:
                                    if item.get('type') == 'text':
                                        text = item.get('text', '').strip()
                                        if text and not text.startswith('/'):
                                            user_messages.append(text)
                                        break
                            elif isinstance(content, str):
                                text = content.strip()
                                if text and not text.startswith('/'):
                                    user_messages.append(text)
                    except:
                        continue

                return user_messages
            except:
                return []

    return []


def generate_smart_name(messages):
    """根据消息生成智能名称"""
    if not messages:
        return "未命名会话"

    # 取第一条消息
    first_msg = messages[0]

    # 提取关键词
    keywords = {
        '修复': ['修复', 'fix', 'bug', 'debug', 'error', '解决', '报错'],
        '添加': ['添加', 'add', 'create', 'new', '创建', '新增'],
        '删除': ['删除', 'remove', 'delete', 'drop', '清理'],
        '更新': ['更新', 'update', '修改', '调整', 'change', 'edit'],
        '重构': ['重构', 'refactor', '重构代码', '整理'],
        '分析': ['分析', 'analyze', 'review', '检查', '评估'],
        '测试': ['测试', 'test', '验证', 'check'],
        '实现': ['实现', 'implement', '完成', '开发'],
        '优化': ['优化', 'optimize', '提升', '改进', 'performance'],
    }

    msg_lower = first_msg.lower()

    # 识别动作类型
    action = None
    for action_name, indicators in keywords.items():
        for indicator in indicators:
            if indicator in msg_lower or indicator in first_msg:
                action = action_name
                break
        if action:
            break

    if not action:
        action = "处理"

    # 提取主题（代码、功能、接口等）
    # 尝试找到名词性短语
    patterns = [
        r'(?:添加|创建|实现|修复|删除|更新|重构|分析|测试|优化)(?:了|一个|一下)?\s*["\']?([^"\']+)["\']?',
        r'(?:add|create|fix|implement|remove|update|refactor|analyze|test|optimize)\s+(?:the\s+)?["\']?([^"\']+)["\']?',
        r'["\']([^"\']+)["\']',
    ]

    subject = None
    for pattern in patterns:
        match = re.search(pattern, first_msg, re.IGNORECASE)
        if match:
            subject = match.group(1).strip()
            if len(subject) > 3:
                break

    if not subject:
        # 取消息的前 15 个字符作为主题
        subject = first_msg[:15].strip()

    # 组合名称
    name = f"{action}{subject}"

    # 限制长度
    if len(name) > 30:
        name = name[:27] + "..."

    return name


def main():
    if len(sys.argv) < 2:
        print("Usage: rename_session.py <session_id> [new_name]")
        print("Example: rename_session.py a1b2c3d \"修复登录Bug\"")
        print("         rename_session.py a1b2c3d  (自动生成名称)")
        sys.exit(1)

    short_id = sys.argv[1]
    new_name = sys.argv[2] if len(sys.argv) > 2 else None

    # 查找完整 session ID
    full_id = find_full_session_id(short_id)
    if not full_id:
        print(f"Error: Session '{short_id}' not found")
        sys.exit(1)

    # 加载元数据
    metadata = load_metadata()

    # 如果没有提供新名称，自动生成
    if new_name is None:
        messages = parse_session_file(full_id)
        new_name = generate_smart_name(messages)
        print(f"🤖 智能建议名称: {new_name}")
        print("(使用此名称，或重新运行命令指定新名称)")

    # 更新元数据
    if 'sessions' not in metadata:
        metadata['sessions'] = {}

    if full_id not in metadata['sessions']:
        metadata['sessions'][full_id] = {}

    metadata['sessions'][full_id]['name'] = new_name
    metadata['sessions'][full_id]['updated_at'] = json.dumps({}).replace('{}', '')  # 当前时间将在实际实现中设置

    # 保存
    if save_metadata(metadata):
        print(f"✅ Session '{short_id}' renamed to: {new_name}")
    else:
        print(f"❌ Failed to rename session")
        sys.exit(1)


if __name__ == "__main__":
    main()
