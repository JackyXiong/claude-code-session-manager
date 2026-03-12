#!/usr/bin/env python3
"""
删除 Session
"""

import json
import os
import sys
import shutil
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


def find_session_info(short_id):
    """根据短 ID 查找 session 信息"""
    projects_dir = get_claude_dir() / "projects"

    if not projects_dir.exists():
        return None, None

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        for session_file in project_dir.glob("*.jsonl"):
            session_id = session_file.stem
            if session_id.startswith(short_id):
                return session_id, session_file

    return None, None


def move_to_trash(session_file, session_id):
    """移动 session 文件到回收站"""
    trash_dir = get_claude_dir() / "sessions" / "trash"
    trash_dir.mkdir(parents=True, exist_ok=True)

    # 添加时间戳到文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f"{session_id}_{timestamp}.jsonl"
    dest_file = trash_dir / new_name

    try:
        shutil.move(str(session_file), str(dest_file))
        return True
    except Exception as e:
        print(f"Error moving to trash: {e}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: delete_session.py <session_id> [--permanent]")
        print("Example: delete_session.py a1b2c3d")
        print("         delete_session.py a1b2c3d --permanent  (永久删除)")
        sys.exit(1)

    short_id = sys.argv[1]
    permanent = '--permanent' in sys.argv

    # 查找 session
    full_id, session_file = find_session_info(short_id)
    if not full_id:
        print(f"Error: Session '{short_id}' not found")
        sys.exit(1)

    # 获取 session 信息用于显示
    metadata = load_metadata()
    session_meta = metadata.get('sessions', {}).get(full_id, {})
    name = session_meta.get('name', '未命名')

    print(f"Session: {name} ({short_id})")
    print(f"文件: {session_file}")

    if permanent:
        print("\n⚠️  此操作将永久删除该 session，无法恢复！")
    else:
        print("\n🗑️  此操作将移动 session 到回收站")

    # 实际删除操作
    if permanent:
        try:
            os.remove(session_file)
            print(f"✅ Session 文件已永久删除")
        except Exception as e:
            print(f"❌ 删除失败: {e}")
            sys.exit(1)
    else:
        if move_to_trash(session_file, full_id):
            print(f"✅ Session 已移动到回收站: ~/.claude/sessions/trash/")
        else:
            print(f"❌ 移动失败")
            sys.exit(1)

    # 清理元数据
    if full_id in metadata.get('sessions', {}):
        del metadata['sessions'][full_id]
        save_metadata(metadata)
        print("✅ 元数据已清理")

    print(f"\nSession '{short_id}' 已成功删除")


if __name__ == "__main__":
    main()
