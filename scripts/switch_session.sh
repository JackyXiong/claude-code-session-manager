#!/bin/bash
# 切换到指定 Session（在新终端窗口中打开）

SESSION_ID=$1

if [ -z "$SESSION_ID" ]; then
    echo "Usage: $0 <session_id>"
    echo "Example: $0 a1b2c3d4"
    exit 1
fi

# 查找完整的 session ID 和项目路径
CLAUDE_DIR="$HOME/.claude/projects"
PROJECT_PATH=""
FULL_SESSION_ID=""

for project_dir in "$CLAUDE_DIR"/*; do
    if [ -d "$project_dir" ]; then
        for session_file in "$project_dir"/*.jsonl; do
            if [ -f "$session_file" ]; then
                basename=$(basename "$session_file" .jsonl)
                if [[ "$basename" == "$SESSION_ID"* ]]; then
                    FULL_SESSION_ID="$basename"
                    # 解码项目路径
                    project_encoded=$(basename "$project_dir")
                    PROJECT_PATH=$(echo "$project_encoded" | sed 's/-/\//g' | sed 's/_/ /g')
                    break 2
                fi
            fi
        done
    fi
done

if [ -z "$FULL_SESSION_ID" ]; then
    echo "Error: Session '$SESSION_ID' not found"
    exit 1
fi

if [ -z "$PROJECT_PATH" ]; then
    echo "Error: Could not determine project path for session"
    exit 1
fi

# 检查项目路径是否存在
if [ ! -d "$PROJECT_PATH" ]; then
    echo "Warning: Project path '$PROJECT_PATH' does not exist"
    echo "Opening terminal without changing directory..."
    PROJECT_PATH="$HOME"
fi

echo "Opening session $FULL_SESSION_ID in $PROJECT_PATH..."

# 根据操作系统打开新终端
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_PATH' && claude --resume $FULL_SESSION_ID\""
    osascript -e "tell application \"Terminal\" to activate"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$PROJECT_PATH' && claude --resume $FULL_SESSION_ID; exec bash"
    elif command -v konsole &> /dev/null; then
        konsole --workdir "$PROJECT_PATH" -e "claude --resume $FULL_SESSION_ID"
    elif command -v xterm &> /dev/null; then
        xterm -e "cd '$PROJECT_PATH' && claude --resume $FULL_SESSION_ID"
    else
        echo "Error: No supported terminal emulator found"
        exit 1
    fi
else
    echo "Error: Unsupported operating system: $OSTYPE"
    exit 1
fi

echo "Session opened in new terminal window"
