import httpx
import csv
import io
import json

SHEET_ID = "1DlVFqCplp_TgjEoXri0CwWe87kxqB11nixmS0eKBz3U"
BASE_URL = "https://docs.google.com/spreadsheets/d/" + SHEET_ID + "/gviz/tq?tqx=out:csv"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwxcRzOQbdmuwoFnn8Zo4raEsNwP5MmEtABny_PaOODPWAOkJKKzDY7PRW4ek91sQyf/exec"
# ── Precio por referencia (ajusta si tienes precios en el Sheet) ──────────────
# Como el inventario NO tiene columna de precio, se mantiene un mapa fijo.
# Si en el futuro agregas precio al Sheet, avísame y lo leemos desde allí.
PRECIOS = {
    # LOCAL PEOPLE
    "LPRS": 89000, "LPRM": 89000, "LPRL": 89000, "LPRXL": 89000,
    "LPBS": 89000, "LPBM": 89000, "LPBL": 89000, "LPBXL": 89000,
    "LPNS": 89000, "LPNM": 89000, "LPNL": 89000, "LPNXL": 89000,
    "LPACS": 89000, "LPACM": 89000, "LPACL": 89000, "LPACXL": 89000,
    "LPVBS": 89000, "LPVBM": 89000, "LPVBL": 89000, "LPVBXL": 89000, "LPVBXXL": 89000,
    # CANGURO
    "CAS": 79000, "CAM": 79000, "CAL": 79000, "CAXL": 79000,
    "CRS": 79000, "CRM": 79000, "CRL": 79000, "CRXL": 79000,
    "CVBS": 79000, "CVBM": 79000, "CVBL": 79000, "CVBXL": 79000,
    "CNS": 79000, "CNM": 79000, "CNL": 79000, "CNXL": 79000,
    "CGS": 79000, "CGM": 79000, "CGL": 79000, "CGXL": 79000,
    # DOBLE FAZ
    "RFS": 129000, "RFM": 129000, "RFL": 129000, "RFXL": 129000,
    # SAFARI
    "SNXS": 109000, "SNS": 109000, "SNM": 109000, "SNL": 109000, "SNXL": 109000, "SNXXL": 109000,
    "SVMZS": 109000, "SVMZM": 109000, "SVMZL": 109000, "SVMZXL": 109000,
    "SAS": 109000, "SAM": 109000, "SAL": 109000, "SAXL": 109000, "SAXXL": 109000,
    "SACXS": 109000, "SACS": 109000, "SACM": 109000, "SACL": 109000, "SACXL": 109000,
    "SVBXS": 109000, "SVBS": 109000, "SVBM": 109000, "SVBL": 109000, "SVBXL": 109000, "SVBXXL": 109000,
    "SBS": 109000, "SBM": 109000, "SBL": 109000, "SBXL": 109000,
    "SGS": 109000, "SGM": 109000, "SGL": 109000, "SGXL": 109000, "SGXXL": 109000,
    # VANGOH
    "VAXS": 99000, "VAS": 99000, "VAM": 99000, "VAL": 99000, "VAXL": 99000,
    # KOREANO
    "KS": 75000, "KM": 75000, "KL": 75000, "KXL": 75000,
    # CENTRICA
    "CENS": 95000, "CENM": 95000, "CENL": 95000, "CENXL": 95000,
    "CTS": 95000, "CTM": 95000, "CTL": 95000, "CTXL": 95000,
    "CERS": 95000, "CERM": 95000,
}

async def get_catalogo() -> str:
    """
    Lee la hoja INVENTARIO cuya estructura real es:
      Col A: Nombre grupo (puede estar vacío en filas de talla/color)
      Col B: Código/Referencia (ej. LPRS, SNM, ...)
      Col C: Descripción completa
      Col D: Stock inicio de mes
      Col E: Ingresos
      Col F: Ventas
      Col G: Stock actual (= D + E - F)
    """
    url = BASE_URL + "&sheet=INVENTARIO"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    reader = csv.reader(io.StringIO(response.text))
    rows = list(reader)

    # Agrupar por nombre de producto (col A cuando no está vacía)
    # Estructura: { "SAFARI NEGRA": { "ref_talla": {"desc", "stock", "precio"} } }
    grupos = {}
    grupo_actual = "Sin categoría"

    for row in rows:
        if len(row) < 7:
            continue

        col_a = row[0].strip()
        col_b = row[1].strip()   # referencia/código
        col_c = row[2].strip()   # descripción
        col_g = row[6].strip()   # stock actual

        # Saltar encabezado
        if col_a == "PRODUCTO" or col_b == "CÓDIGO PRODUCTO":
            continue

        # Si col_b está vacía o col_c vacía, saltar
        if not col_b or not col_c:
            continue

        # Actualizar grupo si col_a tiene valor
        if col_a:
            grupo_actual = col_a

        # Parsear stock
        try:
            stock = int(col_g)
        except ValueError:
            continue

        # Solo incluir con stock > 0
        if stock <= 0:
            continue

        # Extraer talla desde la descripción (última palabra en mayúscula)
        partes = col_c.split()
        talla = partes[-1].upper() if partes else ""

        # Precio
        ref_upper = col_b.upper()
        precio = PRECIOS.get(ref_upper, 0)
        precio_fmt = "${:,}".format(precio).replace(",", ".") if precio else "Consultar"

        if grupo_actual not in grupos:
            grupos[grupo_actual] = []

        grupos[grupo_actual].append({
            "ref": col_b,
            "desc": col_c,
            "talla": talla,
            "stock": stock,
            "precio": precio_fmt,
        })

    if not grupos:
        return "No hay productos disponibles en este momento."

    # Construir texto del catálogo agrupado por producto
    lineas = []
    for nombre_grupo, items in grupos.items():
        # Nombre limpio del grupo
        nombre_limpio = nombre_grupo.title()
        tallas = ", ".join(i["talla"] for i in items)
        precio = items[0]["precio"]  # mismo precio para todo el grupo

        # Refs disponibles (para uso interno del bot)
        refs = " | ".join(
            f"{i['talla']}:{i['ref']} (stock {i['stock']})"
            for i in items
        )

        lineas.append(
            f"- {nombre_limpio} | Tallas disponibles: {tallas} | Precio: {precio} | Refs: {refs}"
        )

    return "\n".join(lineas)


async def registrar_pedido(telefono: str, nombre: str, cedula: str,
                            referencia: str, producto: str, talla: str,
                            color: str, cantidad: int, precio: int,
                            direccion: str, barrio: str, ciudad: str) -> bool:
    try:
        data = {
            "telefono":   telefono,
            "nombre":     nombre,
            "cedula":     cedula,
            "referencia": referencia.upper(),   # ← siempre en mayúscula para coincidir con Sheet
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