import httpx

async def fetch_quote() -> dict:
    # Simple public API; if it ever changes, swap provider later.
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get("https://api.quotable.io/random")
        resp.raise_for_status()
        return resp.json()