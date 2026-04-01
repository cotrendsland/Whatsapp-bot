import asyncio
import httpx

SHEET_ID = "1a2R35CCW2ANqxs539Jqm7iEXPjcB4bxPhA6Tvr6_6kw"

async def test():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Catalogo"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        print(r.text[:800])

asyncio.run(test())