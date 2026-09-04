"""Shared slowapi Limiter instance — in-process, per-IP, no new infra
(decision-73, trd.md). Registered on the FastAPI app in main.py; individual
routes opt in via @limiter.limit(...).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
