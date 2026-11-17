"""
Navigation History Module
Uses array-based stacks for Back, Forward, and Undo operations, a Python
list for route records, and JSON for local persistence.
"""

import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from stacks import ArrayStack


class HistoryManager:
    """Manages navigation history, Back/Forward state, and persistence."""

    def __init__(self, persistence_file: str = "history_data.json"):
        self.persistence_file = persistence_file
        self.back_stack = ArrayStack(capacity=200)
        self.forward_stack = ArrayStack(capacity=200)
        self.undo_stack = ArrayStack(capacity=200)
        self.history_records: List[Dict[str, Any]] = []
        self._next_id = 1
        self._load()

    def add_search(self, src: str, dst: str, mode: str = "driving", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Record a route search action."""
        metadata = metadata or {}
        record = {
            "id": self._next_id,
            "src": src,
            "dst": dst,
            "mode": mode,
            "time": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata,
            "distance_km": metadata.get("distance_km"),
            "duration_min": metadata.get("duration_min")
        }
        self._next_id += 1

        back_before = self.back_stack.to_list()
        forward_before = self.forward_stack.to_list()
        self.back_stack.push(record)
        self.forward_stack = ArrayStack(capacity=200)
        self.undo_stack.push({
            "action": "add_search", "record": record,
            "back_before": back_before, "forward_before": forward_before
        })

        self.history_records.append(record)
        self._save()
        return record

    def back(self) -> Optional[Dict[str, Any]]:
        """Navigate back to previously visited location."""
        if self.back_stack.size() <= 1:
            return None
        current = self.back_stack.pop()
        self.forward_stack.push(current)
        return self.back_stack.peek()

    def forward(self) -> Optional[Dict[str, Any]]:
        """Navigate forward to next location."""
        if self.forward_stack.is_empty():
            return None
        next_record = self.forward_stack.pop()
        self.back_stack.push(next_record)
        return next_record

    def undo_last_action(self) -> Optional[Dict[str, Any]]:
        """Undo last recorded search or delete action."""
        if self.undo_stack.is_empty():
            return None

        last_op = self.undo_stack.pop()
        action = last_op.get("action")
        record = last_op.get("record")

        if action == "add_search":
            rec_id = record.get("id")
            self.history_records = [r for r in self.history_records if r.get("id") != rec_id]
            self._restore_navigation_stacks(
                last_op.get("back_before", self.history_records),
                last_op.get("forward_before", [])
            )
            self._save()
            return {"status": "undone", "action": "add_search", "undone_record": record}

        elif action == "delete":
            index = min(last_op.get("index", len(self.history_records)), len(self.history_records))
            self.history_records.insert(index, record)
            self._restore_navigation_stacks(
                last_op.get("back_before", self.history_records),
                last_op.get("forward_before", [])
            )
            self._save()
            return {"status": "undone", "action": "delete", "restored_record": record}

        return None

    def delete_record(self, record_id: int) -> bool:
        """Delete specific record by id."""
        for i, rec in enumerate(self.history_records):
            if rec.get("id") == record_id:
                deleted = self.history_records.pop(i)
                back_before = self.back_stack.to_list()
                forward_before = self.forward_stack.to_list()
                self.undo_stack.push({
                    "action": "delete", "record": deleted, "index": i,
                    "back_before": back_before, "forward_before": forward_before
                })
                self._restore_navigation_stacks(
                    [r for r in back_before if r.get("id") != record_id],
                    [r for r in forward_before if r.get("id") != record_id]
                )
                self._save()
                return True
        return False

    def clear(self) -> None:
        """Clear all search history."""
        self.history_records.clear()
        self.back_stack = ArrayStack(capacity=200)
        self.forward_stack = ArrayStack(capacity=200)
        self.undo_stack = ArrayStack(capacity=200)
        self._save()

    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent search history in reverse chronological order."""
        return list(reversed(self.history_records))[:limit]

    def _restore_navigation_stacks(self, back_items, forward_items) -> None:
        """Restore Back and Forward from saved bottom-to-top stack snapshots."""
        self.back_stack = ArrayStack(capacity=200)
        self.forward_stack = ArrayStack(capacity=200)
        for record in back_items[-200:]:
            self.back_stack.push(record)
        for record in forward_items[-200:]:
            self.forward_stack.push(record)

    def _save(self) -> None:
        """Persist history list to JSON file."""
        try:
            with open(self.persistence_file, "w", encoding="utf-8") as f:
                json.dump({
                    "next_id": self._next_id,
                    "records": self.history_records
                }, f, indent=2)
        except Exception:
            pass

    def _load(self) -> None:
        """Load history from JSON file if available."""
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.history_records = data.get("records", [])
                    self._next_id = data.get("next_id", len(self.history_records) + 1)
                    self._restore_navigation_stacks(self.history_records, [])
            except Exception:
                self.history_records = []

