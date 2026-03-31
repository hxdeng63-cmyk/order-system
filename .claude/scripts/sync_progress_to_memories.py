# -*- coding: utf-8 -*-
import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def load_payload():
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw}


def resolve_project_dir(payload):
    for key in ("cwd", "working_directory", "workingDirectory"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return Path(value)
    return Path.cwd()


def sanitize_project_dir(project_dir):
    project_dir = project_dir.resolve()
    drive = project_dir.drive.rstrip(":")
    text = str(project_dir)
    rest = text[len(project_dir.drive):].lstrip("\\/")
    rest = re.sub(r"[\\/:]+", "-", rest).strip("-")
    return f"{drive}--{rest}" if drive else rest


def resolve_session_id(payload, project_store_dir):
    for key in ("session_id", "sessionId"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    latest = sorted(project_store_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return latest[0].stem if latest else "unknown-session"


def extract_text(content):
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "").strip()
                if text:
                    texts.append(text)
        return "\n".join(texts).strip()
    return ""


def read_latest_message(jsonl_path, role):
    if not jsonl_path.exists():
        return ""
    lines = jsonl_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line in reversed(lines):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = obj.get("message") or {}
        if message.get("role") != role:
            continue
        text = extract_text(message.get("content"))
        if text:
            return text
    return ""


def load_tasks(task_dir):
    tasks = []
    if not task_dir.exists():
        return tasks
    for file_path in sorted(task_dir.glob("*.json"), key=lambda p: int(p.stem) if p.stem.isdigit() else p.stem):
        try:
            task = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        tasks.append(task)
    return tasks


def ensure_memories_file(memories_path):
    memories_path.parent.mkdir(parents=True, exist_ok=True)
    if not memories_path.exists():
        memories_path.write_text(
            "# Work Progress Memories\n\n"
            "本文件由 Claude Code Stop hook 自动维护，用于记录每轮对话后的工作进度。\n",
            encoding="utf-8",
        )


def backup_memories(memories_path, backup_path):
    if backup_path.exists():
        backup_path.unlink()
    shutil.copy2(memories_path, backup_path)
    if not backup_path.exists():
        raise RuntimeError(f"备份失败：未生成备份文件 {backup_path}")
    if backup_path.read_text(encoding="utf-8") != memories_path.read_text(encoding="utf-8"):
        raise RuntimeError("备份失败：备份内容与当前 memories 文件不一致")


def build_progress_entry(session_id, latest_user, latest_assistant, tasks):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    counts = Counter(task.get("status", "unknown") for task in tasks)
    task_lines = []
    for task in tasks:
        task_lines.append(f"  - [{task.get('status', 'unknown')}] #{task.get('id', '?')} {task.get('subject', '').strip()}")
    task_block = "\n".join(task_lines) if task_lines else "  - 未记录任务"
    latest_user = (latest_user or "未提取到最新用户文本").replace("\r", " ").strip()
    latest_assistant = (latest_assistant or "未提取到最新助手文本").replace("\r", " ").strip()
    return (
        f"\n\n## {timestamp}\n"
        f"- 会话ID：{session_id}\n"
        f"- 最新用户消息：{latest_user[:500]}\n"
        f"- 最新助手反馈：{latest_assistant[:500]}\n"
        f"- 任务统计：completed={counts.get('completed', 0)}, in_progress={counts.get('in_progress', 0)}, pending={counts.get('pending', 0)}\n"
        f"- 当前任务：\n{task_block}\n"
    )


def append_progress(memories_path, entry):
    with memories_path.open("a", encoding="utf-8") as f:
        f.write(entry)


def main():
    payload = load_payload()
    project_dir = resolve_project_dir(payload)
    project_store_dir = Path.home() / ".claude" / "projects" / sanitize_project_dir(project_dir)
    session_id = resolve_session_id(payload, project_store_dir)
    transcript_path = project_store_dir / f"{session_id}.jsonl"
    task_dir = Path.home() / ".claude" / "tasks" / session_id
    memories_path = project_dir / ".claude" / "memories.md"
    backup_path = project_dir / ".claude" / "memories.latest.bak.md"

    ensure_memories_file(memories_path)
    backup_memories(memories_path, backup_path)

    latest_user = read_latest_message(transcript_path, "user")
    latest_assistant = read_latest_message(transcript_path, "assistant")
    tasks = load_tasks(task_dir)
    entry = build_progress_entry(session_id, latest_user, latest_assistant, tasks)
    append_progress(memories_path, entry)
    print(memories_path)


if __name__ == "__main__":
    main()
