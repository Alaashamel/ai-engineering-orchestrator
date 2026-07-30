from __future__ import annotations

from typing import Any

import httpx


class WebhookNotifier:
    def __init__(self, webhook_url: str | None = None):
        self._url = webhook_url

    async def notify(
        self,
        event: str,
        project_id: str,
        payload: dict[str, Any],
    ) -> None:
        if not self._url:
            return
        body = {
            "event": event,
            "project_id": project_id,
            "data": payload,
            "timestamp": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(self._url, json=body)
        except Exception:
            import structlog
            structlog.get_logger().warning("Webhook notification failed", event=event, url=self._url)

    def notify_sync(self, event: str, project_id: str, payload: dict[str, Any]) -> None:
        if not self._url:
            return
        body = {
            "event": event,
            "project_id": project_id,
            "data": payload,
            "timestamp": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
        }
        try:
            httpx.post(self._url, json=body, timeout=10)
        except Exception:
            import structlog
            structlog.get_logger().warning("Webhook notification failed", event=event, url=self._url)
