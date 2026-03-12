#!/usr/bin/env python3
"""
搜索 Session
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict


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


def get_project_name(project_path):
    """从项目路径获取项目名称"""
    if not project_path:
        return "未知"
    return os.path.basename(project_path)


def parse_timestamp(ts):
    """解析时间戳"""
    if isinstance(ts, (int, float)):
        if ts > 1e12:
            ts = ts / 1000
        return datetime.fromtimestamp(ts)
    elif isinstance(ts, str):
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


def fuzzy_match(text, keyword):
    """模糊匹配"""
    if not text or not keyword:
        return False
    text = text.lower()
    keyword = keyword.lower()
    return keyword in text


def scan_sessions():
    """扫描所有 session"""
    projects_dir = get_claude_dir() / "projects"
    sessions = []

    if not projects_dir.exists():
        return sessions

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        project_path = project_dir.name.replace('-', '/').replace('_', ' ')

        for session_file in project_dir.glob("*.jsonl"):
            session_id = session_file.stem

            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                if not lines:
                    continue

                message_count = 0
                first_message = None
                last_timestamp = None
                all_text = []

                for line in lines:
                    try:
                        data = json.loads(line)
                        msg_type = data.get('type', '')

                        if msg_type == 'user':
                            message_count += 1
                            content = data.get('message', {}).get('content', '')
                            if isinstance(content, list):
                                for item in content:
                                    if item.get('type') == 'text':
                                        text = item.get('text', '')
                                        all_text.append(text)
                                        if first_message is None:
                                            first_message = text
                                        break
                            elif isinstance(content, str):
                                all_text.append(content)
                                if first_message is None:
                                    first_message = content

                        ts = data.get('timestamp')
                        if ts:
                            parsed = parse_timestamp(ts)
                            if parsed:
                                last_timestamp = parsed
                    except:
                        continue

                sessions.append({
                    'id': session_id[:8],
                    'full_id': session_id,
                    'project_path': project_path,
                    'project_name': get_project_name(project_path),
                    'message_count': message_count,
                    'last_active': last_timestamp,
                    'first_message': first_message or "无消息",
                    'all_text': ' '.join(all_text),
                })

            except Exception as e:
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

    # 跳过系统命令和标记
    skip_patterns = [
        '/',
        '<local-command-caveat>',
        '<command-message>',
        '[Request interrupted',
        'Caveat:',
        'Implement the following plan',
    ]
    for pattern in skip_patterns:
        if first_message.startswith(pattern) or pattern in first_message[:50]:
            return "计划/任务会话"

    return truncate_text(first_message, 25)


def search_sessions(sessions, keyword, metadata):
    """搜索 sessions"""
    results = []
    keyword_lower = keyword.lower()

    for session in sessions:
        session_meta = metadata.get('sessions', {}).get(session['full_id'], {})
        name = session_meta.get('name', '')
        tags = session_meta.get('tags', [])

        # 搜索字段
        searchable_fields = [
            session['project_name'].lower(),
            session['project_path'].lower(),
            name.lower(),
            session['first_message'].lower() if session['first_message'] else '',
            session['all_text'].lower(),
        ]
        searchable_fields.extend(tag.lower() for tag in tags)

        # 检查是否匹配
        for field in searchable_fields:
            if keyword_lower in field:
                results.append(session)
                break

    return results


def highlight_text(text, keyword):
    """高亮关键词"""
    if not text or not keyword:
        return text
    # 简单的文本高亮
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(f"\033[91m{keyword}\033[0m", text)


def main():
    if len(sys.argv) < 2:
        print("Usage: search_session.py <keyword>")
        print("Example: search_session.py 登录")
        print("         search_session.py api")
        sys.exit(1)

    keyword = sys.argv[1]

    # 加载元数据
    metadata = load_metadata()

    # 扫描 sessions
    sessions = scan_sessions()

    # 搜索
    results = search_sessions(sessions, keyword, metadata)

    if not results:
        print(f"未找到包含 '{keyword}' 的会话")
        sys.exit(0)

    # 按最后活跃时间排序
    results.sort(key=lambda x: x['last_active'] or datetime.min, reverse=True)

    # 打印结果
    print(f"找到 {len(results)} 个包含 '{keyword}' 的会话:\n")
    print(f"{'ID':<10} {'项目名称':<20} {'名称/摘要':<25} {'消息数':<8} {'最后活跃':<12} {'收藏'}")
    print("-" * 90)

    for session in results:
        session_meta = metadata.get('sessions', {}).get(session['full_id'], {})

        name = session_meta.get('name', '')
        summary = name if name else generate_summary(session['first_message'])
        is_fav = "⭐" if session_meta.get('is_favorite', False) else ""
        last_active = format_relative_time(session['last_active'])

        # 高亮匹配的项目名称和摘要
        project_name = highlight_text(session['project_name'], keyword)
        summary = highlight_text(summary, keyword)

        print(f"{session['id']:<10} {project_name:<20} {summary:<25} "
              f"{session['message_count']:<8} {last_active:<12} {is_fav}")


if __name__ == "__main__":
    main()
