import httpx
import csv
import io
import json

SHEET_ID = "1DlVFqCplp_TgjEoXri0CwWe87kxqB11nixmS0eKBz3U"
BASE_URL = "https://docs.google.com/spreadsheets/d/" + SHEET_ID + "/gviz/tq?tqx=out:csv"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycby-y47lkAuFzbCS8v7sJ5Di6PcKb1xSGenFDdZVF8paP9-fJHdBva3-zsVk9CHUHJkk/exec"

async def get_catalogo() -> str:
    url = BASE_URL + "&sheet=Catalogo"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    reader = csv.reader(io.StringIO(response.text))
    rows = list(reader)

    productos = []
    for row in rows:
        if len(row) < 10:
            continue
        if not row[0].startswith("R"):
            continue
        if row[9].strip() != "Activo":
            continue

        precio_raw = row[6].strip().replace("$", "").replace(".", "").replace(",", "").strip()
        try:
            precio = int(precio_raw)
            precio_fmt = "${:,}".format(precio).replace(",", ".")
        except:
            precio_fmt = row[6]

        producto = (
            "- " + row[2] +
            " | Tallas: " + row[4] +
            " | Colores: " + row[5] +
            " | Precio: " + precio_fmt +
            " | Stock: " + row[7] + " uds" +
            " | Ref: " + row[8]
        )
        productos.append(producto)

    if not productos:
        return "No hay productos disponibles en este momento."

    return "\n".join(productos)


async def registrar_pedido(telefono: str, nombre: str, cedula: str,
                            referencia: str, producto: str, talla: str,
                            color: str, cantidad: int, precio: int,
                            direccion: str, barrio: str, ciudad: str) -> bool:
    try:
        data = {
            "telefono":   telefono,
            "nombre":     nombre,
            "cedula":     cedula,
            "referencia": referencia,
            "producto":   producto,
            "talla":      talla,
            "color":      color,
            "cantidad":   cantidad,
            "precio":     precio,
            "direccion":  direccion,
            "barrio":     barrio,
            "ciudad":     ciudad
        }

        async with httpx.AsyncClient(follow_redirects=False) as client:
            r1 = await client.post(
                APPS_SCRIPT_URL,
                content=json.dumps(data),
                headers={"Content-Type": "application/json"},
                timeout=15.0
            )

        if r1.status_code in (301, 302, 303, 307, 308) and "location" in r1.headers:
            redirect_url = r1.headers["location"]
            print("[REDIRECT] " + redirect_url)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    redirect_url,
                    content=json.dumps(data),
                    headers={"Content-Type": "application/json"},
                    timeout=15.0
                )
        else:
            response = r1

        print("[APPS SCRIPT RAW] " + response.text[:300])
        result = response.json()
        if result.get("status") == "ok":
            print("[PEDIDO OK] " + result.get("pedido", ""))
            return True
        else:
            print("[PEDIDO ERROR] " + str(result))
            return False
    except Exception as e:
        print("[ERROR PEDIDO] " + str(e))
        return False