from __future__ import annotations

import hmac
from hashlib import sha256

from fastapi import Header, HTTPException


def validate_webhook_signature(
    payload: bytes,
    signature: str = Header(None, alias="X-Webhook-Signature"),
    secret: str = "",
) -> bool:
    if not secret:
        return True
    if not signature:
        raise HTTPException(status_code=400, detail="Missing webhook signature")
    expected = hmac.new(secret.encode(), payload, sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    return True
