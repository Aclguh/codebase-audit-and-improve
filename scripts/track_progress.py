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

def clean_cell(text):
    """Strip markdown bolding, italics, backticks and extra whitespace."""
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = re.sub(r'[*`_]', '', cleaned)
    return cleaned.strip()

def is_status_done(val):
    """Determine if a status cell represents completion."""
    if not val:
        return False
    v = val.strip().lower()
    if re.search(r'\[[xX]\]', val):
        return True
    if any(sym in val for sym in ('✓', '✔', '✅', '☑', '√')):
        return True
    if v in ('done', 'completed', '已完成', '[x]', 'pass', 'passed', 'finished', 'ok', 'resolved', 'fixed'):
        return True
    return False

def parse_header_columns(header_cells):
    """Map column indices based on header names."""
    col_map = {}
    for idx, cell in enumerate(header_cells):
        c = clean_cell(cell).lower()
        if any(k in c for k in ['优先级', 'priority', 'level']):
            col_map['priority'] = idx
        elif any(k in c for k in ['标识', 'id', 'task id', '编号', 'opt']):
            col_map['id'] = idx
        elif any(k in c for k in ['任务名称', '任务', 'task', 'name', 'title', '描述', 'description']):
            if 'id' not in col_map or col_map.get('id') != idx:
                col_map['name'] = idx
        elif any(k in c for k in ['状态', 'status', 'state', '进度', 'done']):
            col_map['status'] = idx
        elif any(k in c for k in ['涉及文件', '文件', 'file', 'files', 'path']):
            col_map['files'] = idx
        elif any(k in c for k in ['收益', 'benefit', 'impact']):
            col_map['benefit'] = idx
    return col_map

def parse_improvements_file(filepath):
    if not os.path.exists(filepath):
        return None, f"File not found: {filepath}"
        
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        
    tasks = []
    in_table = False
    col_map = {}
    
    for idx, line in enumerate(lines):
        line_clean = line.strip()
        
        # 1. Parse Markdown Tables
        if line_clean.startswith("|") and line_clean.endswith("|"):
            raw_cells = [c.strip() for c in line_clean.split("|")[1:-1]]
            
            # Check if this is a table header
            if not in_table or not col_map:
                detected_map = parse_header_columns(raw_cells)
                if 'status' in detected_map or ('id' in detected_map and 'priority' in detected_map):
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
                
                # If row has enough columns
                if status_idx is not None and status_idx < len(raw_cells):
                    status_raw = raw_cells[status_idx]
                    is_done = is_status_done(status_raw)
                    
                    task_id = clean_cell(raw_cells[id_idx]) if (id_idx is not None and id_idx < len(raw_cells)) else f"TASK-{len(tasks)+1:02d}"
                    priority = clean_cell(raw_cells[prio_idx]).upper() if (prio_idx is not None and prio_idx < len(raw_cells)) else "P2"
                    name = clean_cell(raw_cells[name_idx]) if (name_idx is not None and name_idx < len(raw_cells)) else ""
                    
                    if not name and len(raw_cells) > 2:
                        name = clean_cell(raw_cells[2])
                        
                    # Valid task row check
                    if task_id or name:
                        tasks.append({
                            "line": idx + 1,
                            "priority": priority if re.match(r'^P\d+$', priority) else "P2",
                            "id": task_id if task_id else f"OPT-{len(tasks)+1:02d}",
                            "name": name,
                            "done": is_done
                        })
                        continue
        else:
            in_table = False
            col_map = {}
            
        # 2. Parse Markdown Checklists
        m_list = re.match(r'^[-*+]\s*\[([ xX])\]\s*(.+)$', line_clean)
        if m_list:
            is_done = m_list.group(1).strip().lower() == 'x'
            rest = m_list.group(2).strip()

            # Priority extraction: e.g. [P0], **[P0]**, **P0**, (P0)
            priority = "GENERAL"
            m_prio = re.search(r'\b(P\d+)\b', rest, re.IGNORECASE)
            if m_prio:
                priority = m_prio.group(1).upper()
                rest = re.sub(r'[*_`\[(]*' + re.escape(m_prio.group(0)) + r'[*_`\])]*[:：\-\s]*', '', rest, count=1).strip()

            # Task ID extraction: e.g. [OPT-01], **OPT-01**, OPT-01, TASK-01
            task_id = None
            m_id = re.search(r'\b([A-Za-z0-9_\-]+)\b', rest)
            if m_id and any(c.isdigit() for c in m_id.group(1)):
                task_id = m_id.group(1).upper()
                rest = re.sub(r'[*_`\[(]*' + re.escape(m_id.group(0)) + r'[*_`\])]*[:：\-\s]*', '', rest, count=1).strip()
            else:
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
