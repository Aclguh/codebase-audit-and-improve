#!/usr/bin/env python3
"""
IMPROVEMENTS.md Progress Tracker & Task Parser
Dynamically parses task tables and checklists in IMPROVEMENTS.md,
calculates completion metrics, and supports CI check exit codes.
"""

import os
import sys
import re
import json

# Ensure UTF-8 output encoding across all operating systems and Windows CI runners
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Priority tokens must stand alone: "P2P" and "OPT-01" are not priorities.
PRIORITY_TOKEN_RE = re.compile(r'(?i)(?<![A-Za-z0-9])(P\d+)(?![A-Za-z0-9])')

def clean_cell(text):
    """Strip markdown bolding, italics, backticks and extra whitespace."""
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = re.sub(r'[*`_~]', '', cleaned)
    return cleaned.strip()

def is_status_done(val):
    """Determine if a status cell represents completion."""
    if not val:
        return False
    # Direct brackets match: [x], [X], [v], [V], [✓], [✔], [✅], [☑], [√], [y], [Y]
    if re.search(r'\[[xXvVyY✓✔✅☑√]\]', val):
        return True
    # Unicode and check symbols anywhere in cell
    if any(sym in val for sym in ('✓', '✔', '✅', '☑', '√')):
        return True
    # Strip markdown markers
    clean_v = clean_cell(val).lower()
    # Check if cleaned text starts with standard completion keywords (even if followed by commit hash, PR, or note)
    if re.match(r'^(?:done|completed|complete|pass|passed|finished|ok|resolved|fixed|closed|merged|success|implemented|yes|true)\b', clean_v):
        return True
    # Chinese completion prefixes (handles colon, dash, whitespace or immediate trailing text)
    for zh_kw in ('已完成', '完成', '已解决', '已修复', '已实现', '通过'):
        if clean_v.startswith(zh_kw):
            return True
    if clean_v in ('[x]', '[v]', '[y]', 'y', 'yes', 'true', '已完成', '完成', '通过', 'pass', 'ok', 'merged', 'done', 'implemented'):
        return True
    return False

def header_contains(cell, keywords):
    """Return True when a header cell matches one of the keywords.

    ASCII keywords use word boundaries so short tokens such as ``id`` do not
    match unrelated words (for example ``Valid``). Non-ASCII keywords keep
    substring semantics so Chinese headers such as ``任务状态`` still match.
    """
    for keyword in keywords:
        if keyword.isascii():
            pattern = r'(?<![a-z0-9])' + re.escape(keyword) + r's?(?![a-z0-9])'
            if re.search(pattern, cell):
                return True
        elif keyword in cell:
            return True
    return False

def parse_header_columns(header_cells):
    """Map column indices based on header names."""
    col_map = {}
    for idx, cell in enumerate(header_cells):
        c = clean_cell(cell).lower()
        if len(c) > 30:
            continue
        # Status is checked before name: headers such as "Task Status" and
        # "任务状态" also contain "task"/"任务" but denote the status column.
        if header_contains(c, ['优先级', 'priority', 'level', 'severity', 'prio', 'sev']):
            col_map['priority'] = idx
        elif header_contains(c, ['标识', 'id', 'task id', '编号', 'opt']):
            col_map['id'] = idx
        elif header_contains(c, ['状态', 'status', 'state', '进度', 'progress', 'done', 'completed', 'complete', 'finished', 'resolved']):
            col_map['status'] = idx
        elif header_contains(c, ['涉及文件', '文件', 'file', 'files', 'path']):
            col_map['files'] = idx
        elif header_contains(c, ['收益', 'benefit', 'impact']):
            col_map['benefit'] = idx
        elif header_contains(c, ['任务名称', '任务', 'task', 'name', 'title', '描述', 'description', 'action', 'item', 'todo']):
            col_map['name'] = idx
    return col_map

def parse_improvements_file(filepath):
    if not os.path.exists(filepath):
        return None, f"File not found: {filepath}"
        
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        
    tasks = []
    in_table = False
    col_map = {}
    in_fence = False
    fence_char = ""
    fence_length = 0

    for idx, line in enumerate(lines):
        line_clean = line.strip()

        # 0. Skip fenced code blocks so documented examples are never counted.
        if in_fence:
            closing_fence = re.match(r'^(`{3,}|~{3,})\s*$', line_clean)
            if closing_fence and closing_fence.group(1)[0] == fence_char and len(closing_fence.group(1)) >= fence_length:
                in_fence = False
            in_table = False
            col_map = {}
            continue

        opening_fence = re.match(r'^(`{3,}|~{3,})', line_clean)
        if opening_fence:
            in_fence = True
            fence_char = opening_fence.group(1)[0]
            fence_length = len(opening_fence.group(1))
            in_table = False
            col_map = {}
            continue

        # 1. Parse Markdown Tables
        if line_clean.startswith("|") and line_clean.endswith("|"):
            raw_cells = [c.strip() for c in line_clean.split("|")[1:-1]]
            
            # Check if this row is followed by a separator line (| :--- | :---: |)
            is_followed_by_separator = False
            if idx + 1 < len(lines):
                next_clean = lines[idx + 1].strip()
                if next_clean.startswith("|") and next_clean.endswith("|"):
                    next_cells = [c.strip() for c in next_clean.split("|")[1:-1]]
                    if next_cells and all(re.match(r'^:?-+:?$', c) for c in next_cells):
                        is_followed_by_separator = True

            # Check if this is a table header
            if is_followed_by_separator:
                detected_map = parse_header_columns(raw_cells)
                has_status = 'status' in detected_map
                has_identity = any(key in detected_map for key in ('id', 'priority', 'name'))
                # Accept tables with a status column, or name-based tables that
                # carry an id/priority. This keeps compact "ID | Task" tables.
                is_task_table = (has_status and has_identity) or (
                    'name' in detected_map and ('id' in detected_map or 'priority' in detected_map)
                )
                if is_task_table:
                    col_map = detected_map
                    in_table = True
                    continue
            
            # Skip separator line (| :--- | :---: |)
            if all(re.match(r'^:?-+:?$', c) for c in raw_cells):
                continue
                
            if in_table and col_map:
                status_idx = col_map.get('status')
                id_idx = col_map.get('id')
                prio_idx = col_map.get('priority')
                name_idx = col_map.get('name')
                
                # Check if row has status or defaults to pending
                if status_idx is not None and status_idx < len(raw_cells):
                    status_raw = raw_cells[status_idx]
                    is_done = is_status_done(status_raw)
                else:
                    is_done = False
                    
                task_id = clean_cell(raw_cells[id_idx]) if (id_idx is not None and id_idx < len(raw_cells)) else f"TASK-{len(tasks)+1:02d}"
                raw_prio = clean_cell(raw_cells[prio_idx]).upper() if (prio_idx is not None and prio_idx < len(raw_cells)) else "P2"
                m_prio = PRIORITY_TOKEN_RE.search(raw_prio)
                priority = m_prio.group(1).upper() if m_prio else "P2"
                name = clean_cell(raw_cells[name_idx]) if (name_idx is not None and name_idx < len(raw_cells)) else ""
                
                if not name and len(raw_cells) > 2:
                    name = clean_cell(raw_cells[2])
                    
                # Valid task row check
                if task_id or name:
                    tasks.append({
                        "line": idx + 1,
                        "priority": priority,
                        "id": task_id if task_id else f"OPT-{len(tasks)+1:02d}",
                        "name": name,
                        "done": is_done
                    })
                    continue
        else:
            in_table = False
            col_map = {}
            
        # 2. Parse Markdown Checklists
        m_list = re.match(r'^(?:[-*+]|\d+\.)\s*\[([ xXvVyY✓✔✅☑√]|\s*)\](?!\()\s*(.+)$', line_clean)
        if m_list:
            bracket_val = m_list.group(1).strip()
            is_done = is_status_done(bracket_val) or is_status_done(f"[{bracket_val}]")
            rest = m_list.group(2).strip()

            # Priority extraction: e.g. [P0], **[P0]**, **P0**, (P0), [P0级]
            priority = "GENERAL"
            m_prio = PRIORITY_TOKEN_RE.search(rest)
            if m_prio:
                priority = m_prio.group(1).upper()
                # Consume the surrounding emphasis/brackets and a trailing "级"
                # qualifier so "[P0级] OPT-07" leaves the task ID intact.
                rest = re.sub(
                    r'[*_`\[(]*' + re.escape(m_prio.group(0)) + r'(?:\s*级)?[*_`\])]*[:：\-\s]*',
                    '', rest, count=1
                ).strip()

            # Task ID extraction: e.g. [OPT-01], **OPT-01**, OPT-01, TASK-01
            task_id = None
            m_explicit = re.match(r'^(?:[*_`\[(]+)?([A-Za-z0-9_\-#]+)(?:[*_`\])]+)?[:：\-\s]+', rest)
            if m_explicit:
                candidate = m_explicit.group(1)
                is_bracketed = bool(re.match(r'^[\[(][^\])]+[\])]', rest))
                has_separator = bool(re.search(r'[A-Za-z]+[-_]\d+|\d+[-_][A-Za-z]+', candidate))
                is_issue_num = bool(re.match(r'^#\d+$', candidate))
                is_standard_prefix = bool(re.match(r'^(?:OPT|TASK|ISSUE|TODO|FEAT|FIX|SEC|PERF|BUG|ARCH|CHORE|TEST)\d+$', candidate, re.IGNORECASE))
                if is_bracketed or has_separator or is_issue_num or is_standard_prefix:
                    task_id = candidate.upper()
                    rest = rest[m_explicit.end():].strip()
            if not task_id:
                task_id = f"OPT-{len(tasks)+1:02d}"

            name = rest.strip()
            if not name:
                name = task_id

            tasks.append({
                "line": idx + 1,
                "priority": priority,
                "id": task_id,
                "name": name,
                "done": is_done
            })

    return tasks, None

def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print("Usage: track-progress [options] [path/to/IMPROVEMENTS.md]")
        print("   or: python scripts/track_progress.py [options] [path/to/IMPROVEMENTS.md]\n")
        print("IMPROVEMENTS.md Progress Tracker & Task Parser")
        print("Dynamically parses task tables and checklists, calculating completion metrics.\n")
        print("Options:")
        print("  --check          Exit with code 1 if any tasks are still pending (CI gate)")
        print("  --json           Output detailed progress metrics in JSON format")
        print("  --quiet          Suppress human-readable console progress report")
        print("  -h, --help       Show this help message and exit")
        sys.exit(0)

    as_json = "--json" in args
    check_mode = "--check" in args
    quiet = "--quiet" in args
    
    file_args = [a for a in args if not a.startswith("--")]
    target_file = file_args[0] if file_args else "IMPROVEMENTS.md"
    
    tasks, err = parse_improvements_file(target_file)
    if err:
        if as_json:
            print(json.dumps({"error": err, "file": target_file}, ensure_ascii=False))
        else:
            print(f"[!] Error: {err}")
        sys.exit(2)
        
    if not tasks:
        if as_json:
            print(json.dumps({"error": "No tracked tasks found", "file": target_file, "tasks": []}, ensure_ascii=False))
        else:
            print(f"[!] No tracked tasks found in {target_file}")
        sys.exit(2)
        
    total = len(tasks)
    completed = sum(1 for t in tasks if t['done'])
    pending = total - completed
    pct = (completed / total * 100) if total > 0 else 0.0
    
    # Priority breakdown
    priorities = sorted(list(set(t['priority'] for t in tasks)))
    by_priority = {}
    for p in priorities:
        p_tasks = [t for t in tasks if t['priority'] == p]
        by_priority[p] = {
            "total": len(p_tasks),
            "completed": sum(1 for t in p_tasks if t['done']),
            "pending": len(p_tasks) - sum(1 for t in p_tasks if t['done'])
        }

    if as_json:
        result = {
            "file": target_file,
            "total": total,
            "completed": completed,
            "pending": pending,
            "percentage": round(pct, 1),
            "is_all_completed": pending == 0,
            "by_priority": by_priority,
            "tasks": tasks
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if check_mode and pending > 0:
            sys.exit(1)
        sys.exit(0)

    if not quiet:
        print("=" * 65)
        print(f"Task Progress Report: {target_file}")
        print(f"Total: {total} | Completed: {completed} | Pending: {pending} | Progress: {pct:.1f}%")
        print("=" * 65)
        
        for p in priorities:
            stats = by_priority[p]
            print(f"[{p}] {stats['completed']}/{stats['total']} completed")
            for t in [t for t in tasks if t['priority'] == p]:
                status_symbol = "✓" if t['done'] else "○"
                print(f"    {status_symbol} [{t['id']}] {t['name']}")
                
        print("-" * 65)
        if pending == 0:
            print("🎉 ALL TASKS COMPLETED (100%)! Ready for final verification, cleanup, and CI push.")
        else:
            print(f"⏳ {pending} task(s) remaining. Continue atomic execution loop.")
        print("=" * 65)

    if check_mode and pending > 0:
        sys.exit(1)
        
    sys.exit(0)

if __name__ == "__main__":
    main()
