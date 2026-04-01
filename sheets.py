import httpx
import csv
import io
import json

SHEET_ID = "1a2R35CCW2ANqxs539Jqm7iEXPjcB4bxPhA6Tvr6_6kw"
BASE_URL = "https://docs.google.com/spreadsheets/d/" + SHEET_ID + "/gviz/tq?tqx=out:csv"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzGC7A3RwMObYcawPw2VIbTLs7WqoeAGhZEhqdsufztBdW_TNrkVo6MkwS-OY1omf6Y/exec"

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

async def registrar_pedido(telefono: str, nombre: str, referencia: str,
                            producto: str, talla: str, color: str,
                            cantidad: int, precio: int) -> bool:
    try:
        data = {
            "telefono":   telefono,
            "nombre":     nombre,
            "referencia": referencia,
            "producto":   producto,
            "talla":      talla,
            "color":      color,
            "cantidad":   cantidad,
            "precio":     precio
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                APPS_SCRIPT_URL,
                content=json.dumps(data),
                headers={"Content-Type": "application/json"},
                follow_redirects=True,
                timeout=15.0
            )
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