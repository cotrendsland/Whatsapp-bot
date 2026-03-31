import asyncio
import httpx

SHEET_ID = "16F1XhdpC8U6hQF5_h1LR9bAqx_3hxIZ4HYjOt-KnKkw"

async def test():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Catalogo"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        print(r.text[:800])

asyncio.run(test())