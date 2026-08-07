"""
Assignment 11 — Audit Log starter (TODO).

Records every interaction for forensics. Never blocks by itself —
other layers catch attacks; this layer makes them reviewable.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone


class AuditLogPlugin:
    """Framework-agnostic audit logger (wire into ADK callbacks or your pipeline)."""

    def __init__(self):
        self.name = "audit_log"
        self.logs: list[dict] = []
        self._open: dict[str, float] = {}

    def record_input(self, *, user_id: str, text: str, request_id: str | None = None):
        """Store input + start timestamp keyed by request_id/user_id."""
        if not request_id:
            import uuid
            request_id = str(uuid.uuid4())
            
        self._open[request_id] = datetime.now(timezone.utc).timestamp()
        self.logs.append({
            "request_id": request_id,
            "user_id": user_id,
            "input": text,
            "start_time": utc_now_iso(),
        })

    def record_output(
        self,
        *,
        user_id: str,
        text: str,
        blocked: bool = False,
        layer: str | None = None,
        request_id: str | None = None,
    ):
        """Store output, layer decision, latency; append to self.logs."""
        latency = None
        if request_id and request_id in self._open:
            start_ts = self._open.pop(request_id)
            latency = datetime.now(timezone.utc).timestamp() - start_ts
            
        # Find existing log entry if any
        log_entry = next((log for log in self.logs if log.get("request_id") == request_id), None)
        if log_entry:
            log_entry.update({
                "output": text,
                "blocked": blocked,
                "layer": layer,
                "latency_sec": latency,
                "end_time": utc_now_iso()
            })
        else:
            self.logs.append({
                "request_id": request_id,
                "user_id": user_id,
                "output": text,
                "blocked": blocked,
                "layer": layer,
                "latency_sec": latency,
                "end_time": utc_now_iso()
            })

    def export_json(self, filepath: str = "outputs/audit_log.json"):
        """Write logs to disk (JSON array)."""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
