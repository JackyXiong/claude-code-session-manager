#!/usr/bin/env python3
"""
列出所有 Claude Code Session
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def get_claude_dir():
    """获取 Claude Code 配置目录"""
    return Path.home() / ".claude"


def parse_timestamp(ts):
    """解析时间戳"""
    if isinstance(ts, (int, float)):
        # 毫秒时间戳
        if ts > 1e12:
            ts = ts / 1000
        return datetime.fromtimestamp(ts)
    elif isinstance(ts, str):
        # ISO 格式 - 使用 naive datetime 以保持一致性
        try:
            ts = ts.replace('Z', '+00:00')
            dt = datetime.fromisoformat(ts)
            # 转换为 naive datetime
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt
        except:
            return None
    return None


def format_relative_time(dt):
    """格式化为相对时间"""
    if not dt:
        return "未知"

    now = datetime.now()
    diff = now - dt

    if diff.days == 0:
        seconds = diff.seconds
        if seconds < 60:
            return "刚刚"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}分钟前"
        else:
            hours = seconds // 3600
            return f"{hours}小时前"
    elif diff.days == 1:
        return "昨天"
    elif diff.days < 7:
        return f"{diff.days}天前"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks}周前"
    else:
        return dt.strftime("%Y-%m-%d")


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


def get_project_name(project_path):
    """从项目路径获取项目名称"""
    if not project_path:
        return "未知"
    # 项目路径是原始路径，如 /Users/xiongjie/aicode/ask-me-anything
    return os.path.basename(project_path)


def decode_project_path(encoded_name):
    """解码项目名称

    Claude Code 使用 URL-safe base64 或简单的替换编码
    实际上它看起来像是把路径中的 / 替换为 -
    如: -Users-xiongjie-aicode-ask-me-anything
    需要还原为: /Users/xiongjie/aicode/ask-me-anything
    """
    # 简单的替换：- 还原为 /，然后去掉开头的 /
    decoded = encoded_name.replace('-', '/')
    return decoded


def scan_sessions():
    """扫描所有 session"""
    projects_dir = get_claude_dir() / "projects"
    sessions = []

    if not projects_dir.exists():
        return sessions

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        # 解码项目路径
        project_path = decode_project_path(project_dir.name)

        # 查找所有 session 文件
        for session_file in project_dir.glob("*.jsonl"):
            session_id = session_file.stem

            # 跳过非 session 文件（如临时文件）
            if not session_id[0].isalnum():
                continue

            # 解析 session 文件
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                if not lines:
                    continue

                # 获取消息数量（过滤系统消息）
                message_count = 0
                first_message = None
                last_timestamp = None

                for line in lines:
                    try:
                        data = json.loads(line)
                        msg_type = data.get('type', '')

                        if msg_type == 'user':
                            message_count += 1
                            content = data.get('message', {}).get('content', '')
                            text = None

                            if isinstance(content, list):
                                for item in content:
                                    if item.get('type') == 'text':
                                        text = item.get('text', '')
                                        break
                            elif isinstance(content, str):
                                text = content

                            # 跳过系统生成的消息，找真正的用户输入
                            if text and first_message is None:
                                # 跳过这些系统标记
                                skip_prefixes = [
                                    '[Request interrupted',
                                    '<local-command-caveat>',
                                    '<command-message>',
                                    '[Request interrupted by user]',
                                ]
                                is_system = any(text.strip().startswith(p) for p in skip_prefixes)

                                if not is_system:
                                    first_message = text

                        # 获取时间戳
                        ts = data.get('timestamp')
                        if ts:
                            parsed = parse_timestamp(ts)
                            if parsed:
                                last_timestamp = parsed
                    except:
                        continue

                sessions.append({
                    'id': session_id[:8],  # 缩短 ID
                    'full_id': session_id,
                    'project_path': project_path,
                    'project_name': get_project_name(project_path),
                    'message_count': message_count,
                    'last_active': last_timestamp,
                    'first_message': first_message or "无消息",
                })

            except Exception as e:
                print(f"Error reading {session_file}: {e}", file=sys.stderr)
                continue

    return sessions


def truncate_text(text, max_len):
    """截断文本"""
    if not text:
        return ""
    text = text.replace('\n', ' ').strip()
    if len(text) > max_len:
        return text[:max_len-3] + "..."
    return text


def generate_summary(first_message):
    """生成会话摘要"""
    if not first_message:
        return "无消息"

    # 清理文本
    text = first_message.strip()

    # 跳过纯命令
    if text.startswith('<command-name>'):
        return "命令执行"

    # 跳过纯系统标记
    if text.startswith(('<local-command-caveat>', '[Request interrupted by user]')):
        return "系统消息"

    # 对于 "Implement the following plan:" 开头的，提取后面的标题
    if text.startswith('Implement the following plan:'):
        remaining = text[len('Implement the following plan:'):].strip()
        # 提取第一行作为标题
        first_line = remaining.split('\n')[0].strip()
        # 去掉开头的 # 和空格
        if first_line.startswith('#'):
            first_line = first_line.lstrip('#').strip()
        if first_line:
            return truncate_text(first_line, 25)

    # 对于 markdown 标题 # xxx，提取标题内容
    if text.startswith('#'):
        # 提取第一行并清理
        first_line = text.split('\n')[0].strip()
        first_line = first_line.lstrip('#').strip()
        if first_line:
            return truncate_text(first_line, 25)

    # 正常的用户消息，直接截断显示
    return truncate_text(text, 25)


def main():
    # 加载元数据
    metadata = load_metadata()

    # 扫描 sessions
    sessions = scan_sessions()

    # 按最后活跃时间排序
    sessions.sort(key=lambda x: x['last_active'] or datetime.min, reverse=True)

    # 打印表头
    print(f"{'ID':<10} {'项目名称':<20} {'名称/摘要':<25} {'消息数':<8} {'最后活跃':<12} {'收藏'}")
    print("-" * 90)

    # 打印 sessions
    for session in sessions:
        session_meta = metadata.get('sessions', {}).get(session['full_id'], {})

        name = session_meta.get('name', '')
        summary = name if name else generate_summary(session['first_message'])
        is_fav = "⭐" if session_meta.get('is_favorite', False) else ""
        last_active = format_relative_time(session['last_active'])

        print(f"{session['id']:<10} {session['project_name']:<20} {summary:<25} "
              f"{session['message_count']:<8} {last_active:<12} {is_fav}")

    print(f"\n共 {len(sessions)} 个会话")


if __name__ == "__main__":
    main()
