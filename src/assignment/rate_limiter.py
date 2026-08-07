"""
Assignment 11 — Rate Limiter starter (TODO).

Sliding-window, per-user rate limiting. Blocks abuse that other
guardrail layers do not address (flooding / cost attacks).
"""
from __future__ import annotations

from collections import defaultdict, deque
import time

from google.adk.plugins import base_plugin
from google.genai import types


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_update = time.time()

    def consume(self, tokens: int = 1) -> bool:
        now = time.time()
        # Refill tokens based on time passed
        time_passed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + time_passed * self.refill_rate)
        self.last_update = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

class RateLimitPlugin(base_plugin.BasePlugin):
    """Block users who exceed max_requests within window_seconds using Token Bucket."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        super().__init__(name="rate_limiter")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Refill rate: tokens per second
        refill_rate = max_requests / window_seconds
        # Dictionary mapping (user_id, ip_address) to TokenBucket
        self.user_buckets: dict[tuple[str, str], TokenBucket] = defaultdict(
            lambda: TokenBucket(capacity=max_requests, refill_rate=refill_rate)
        )
        self.blocked_count = 0
        self.total_count = 0

    def _block_response(self, message: str) -> types.Content:
        return types.Content(
            role="model",
            parts=[types.Part.from_text(text=message)],
        )

    async def on_user_message_callback(self, *, invocation_context, user_message):
        """Return Content to block, or None to allow."""
        self.total_count += 1
        user_id = getattr(invocation_context, "user_id", None) or "anonymous"
        ip_address = getattr(invocation_context, "ip_address", None) or "127.0.0.1"
        
        bucket = self.user_buckets[(user_id, ip_address)]

        if not bucket.consume(1):
            self.blocked_count += 1
            # Calculate wait time for 1 token
            wait = 1.0 / bucket.refill_rate
            return self._block_response(
                f"Rate limit exceeded. Try again in {wait:.1f}s."
            )
            
        return None
