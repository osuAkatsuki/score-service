from __future__ import annotations

from dotenv import load_dotenv

# Single source of truth for test env. Loaded before any app module is
# imported so starlette Config has values for every required key.
load_dotenv(".env.test")
