#!/bin/bash

# Read JSON input from stdin
input=$(cat)

# Extract current directory and model info
current_dir=$(echo "$input" | jq -r '.workspace.current_dir')
model_name=$(echo "$input" | jq -r '.model.display_name')

# Get shortened directory (basename)
short_dir=$(basename "$current_dir")

# Get git branch if in a git repo (skip optional locks to avoid conflicts)
git_branch=""
if git -C "$current_dir" rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git -C "$current_dir" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [ -n "$branch" ]; then
        git_branch=" (${branch})"
    fi
fi

# Calculate context window percentage
usage=$(echo "$input" | jq '.context_window.current_usage')
context_info=""
if [ "$usage" != "null" ]; then
    current=$(echo "$usage" | jq '.input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens')
    size=$(echo "$input" | jq '.context_window.context_window_size')
    if [ "$size" -gt 0 ]; then
        pct=$((current * 100 / size))
        context_info=" [${pct}% context used]"
    fi
fi

# Output status line with colors
printf "\033[36m%s\033[0m:\033[32m%s\033[0m%s\033[33m%s\033[0m" \
    "$model_name" \
    "$short_dir" \
    "$git_branch" \
    "$context_info"
