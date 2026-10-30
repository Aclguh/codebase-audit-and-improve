#!/usr/bin/env python3
"""
IMPROVEMENTS.md Progress Tracker & Task Parser
Parses task tables in IMPROVEMENTS.md and calculates completion metrics.
"""

import os
import sys
import re

def parse_improvements_file(filepath):
    if not os.path.exists(filepath):
        print(f"[!] Error: File not found: {filepath}")
        sys.exit(1)
        
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        
    tasks = []
    # Match markdown table row with priority and status:
    # e.g.: | **P0** | **OPT-01** | Task Name | Benefit | file | [ ] |
    # or:   | P0 | OPT-01 | Task Name | Benefit | file | [x] |
    table_pattern = re.compile(
        r'\|\s*\*?\*?(P\d+)\*?\*?\s*\|\s*\*?\*?([A-Za-z0-9_\-]+)\*?\*?\s*\|\s*([^\|]+)\s*\|\s*([^\|]+)\s*\|\s*([^\|]+)\s*\|\s*\[([ xX])\]\s*\|'
    )
    
    # Generic checklist match:
    # e.g.: - [ ] OPT-01: description
    list_pattern = re.compile(
        r'-\s*\[([ xX])\]\s*\*?\*?([A-Za-z0-9_\-]+)\*?\*?\s*[:：]?\s*(.*)'
    )
    
    for idx, line in enumerate(lines):
        line_clean = line.strip()
        m_table = table_pattern.search(line_clean)
        if m_table:
            priority = m_table.group(1).upper()
            task_id = m_table.group(2)
            name = m_table.group(3).strip()
            is_done = m_table.group(6).strip().lower() == 'x'
            tasks.append({
                "line": idx + 1,
                "priority": priority,
                "id": task_id,
                "name": name,
                "done": is_done
            })
            continue
            
        m_list = list_pattern.search(line_clean)
        if m_list:
            is_done = m_list.group(1).strip().lower() == 'x'
            task_id = m_list.group(2)
            name = m_list.group(3).strip()
            tasks.append({
                "line": idx + 1,
                "priority": "GENERAL",
                "id": task_id,
                "name": name,
                "done": is_done
            })

    return tasks

def main():
    target_file = sys.argv[1] if len(sys.argv) > 1 else "IMPROVEMENTS.md"
    tasks = parse_improvements_file(target_file)
    
    if not tasks:
        print(f"[!] No tracked tasks found in {target_file}")
        return
        
    total = len(tasks)
    completed = sum(1 for t in tasks if t['done'])
    pending = total - completed
    pct = (completed / total * 100) if total > 0 else 0.0
    
    print("=" * 60)
    print(f"Task Progress Report: {target_file}")
    print(f"Total Tasks: {total} | Completed: {completed} | Pending: {pending} | Progress: {pct:.1f}%")
    print("=" * 60)
    
    # Priority breakdown
    priorities = sorted(list(set(t['priority'] for t in tasks)))
    for p in priorities:
        p_tasks = [t for t in tasks if t['priority'] == p]
        p_done = sum(1 for t in p_tasks if t['done'])
        p_total = len(p_tasks)
        print(f"[{p}] {p_done}/{p_total} completed")
        for t in p_tasks:
            status_symbol = "✓" if t['done'] else "○"
            print(f"    {status_symbol} [{t['id']}] {t['name']}")
            
    print("-" * 60)
    if pending == 0:
        print("🎉 ALL TASKS COMPLETED (100%)! Ready for final verification, cleanup, and CI push.")
    else:
        print(f"⏳ {pending} task(s) remaining. Continue atomic execution loop.")
    print("=" * 60)

if __name__ == "__main__":
    main()
