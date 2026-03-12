#!/usr/bin/env python3
"""
切换 Session 收藏状态
"""

import json
import sys
from pathlib import Path
from datetime import datetime


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


def main():
    if len(sys.argv) < 2:
        print("Usage: toggle_favorite.py <session_id>")
        print("Example: toggle_favorite.py a1b2c3d")
        sys.exit(1)

    short_id = sys.argv[1]

    # 查找完整 session ID
    full_id = find_full_session_id(short_id)
    if not full_id:
        print(f"Error: Session '{short_id}' not found")
        sys.exit(1)

    # 加载元数据
    metadata = load_metadata()

    if 'sessions' not in metadata:
        metadata['sessions'] = {}

    if full_id not in metadata['sessions']:
        metadata['sessions'][full_id] = {}

    # 切换收藏状态
    current_status = metadata['sessions'][full_id].get('is_favorite', False)
    new_status = not current_status
    metadata['sessions'][full_id]['is_favorite'] = new_status
    metadata['sessions'][full_id]['updated_at'] = datetime.now().isoformat()

    # 保存
    if save_metadata(metadata):
        status_str = "⭐ 已收藏" if new_status else "未收藏"
        print(f"✅ Session '{short_id}' {status_str}")
    else:
        print(f"❌ Failed to update favorite status")
        sys.exit(1)


if __name__ == "__main__":
    main()
