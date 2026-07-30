from orchestration.webhooks import WebhookNotifier

def test_webhook_noop_without_url():
    notifier = WebhookNotifier()
    import asyncio
    asyncio.run(notifier.notify("test", "proj-1", {}))
    notifier.notify_sync("test", "proj-1", {})
