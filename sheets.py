import httpx
import csv
import io
import json

SHEET_ID = "1DlVFqCplp_TgjEoXri0CwWe87kxqB11nixmS0eKBz3U"
BASE_URL = "https://docs.google.com/spreadsheets/d/" + SHEET_ID + "/gviz/tq?tqx=out:csv"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxVJll_ZahbTkQ2OIMQZ3ONBNLKlpjwP7Iz1bE_YAh6EIXgH5GbElRgEWYGBldpy_3s/exec"

# ── Precio por referencia ─────────────────────────────────────────────────────
# El inventario no tiene columna de precio, se mantiene este mapa.
# Si en el futuro agregas precio al Sheet, puedes leerlo desde allí.
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
    Lee la hoja INVENTARIO con estructura:
      Col A (row[0]): PRODUCTO       — nombre del grupo (vacío en filas de variante)
      Col B (row[1]): CÓDIGO PRODUCTO — referencia/código (ej. SNM, LPRS)
      Col C (row[2]): DESCRIPCIÓN    — descripción completa de cada variante
      Col D (row[3]): Stock inicio de mes
      Col E (row[4]): INGRESOS
      Col F (row[5]): VENTAS
      Col G (row[6]): STOCK actual

    Agrupa por nombre de producto (col A) y muestra:
      - Nombre del producto (col A del grupo)
      - Descripción completa de cada variante (col C)
      - Tallas con stock > 0
      - Precio
      - Referencias internas (solo para el bot, nunca se muestran al cliente)
    """
    url = BASE_URL + "&sheet=INVENTARIO"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    reader = csv.reader(io.StringIO(response.text))
    rows = list(reader)

    # grupos: { "SAFARI NEGRA": [ {ref, desc, talla, stock, precio}, ... ] }
    grupos: dict = {}
    grupo_actual = ""
    nombre_producto_actual = ""  # Nombre limpio del grupo (col A)

    for row in rows:
        if len(row) < 7:
            continue

        col_a = row[0].strip()   # PRODUCTO (nombre grupo)
        col_b = row[1].strip()   # CÓDIGO PRODUCTO (referencia)
        col_c = row[2].strip()   # DESCRIPCIÓN completa
        col_g = row[6].strip()   # STOCK actual

        # Saltar encabezado
        if col_b == "CÓDIGO PRODUCTO" or col_a == "PRODUCTO":
            continue

        # Saltar filas sin código o sin descripción
        if not col_b or not col_c:
            continue

        # Si col A tiene valor, actualizar el grupo actual
        if col_a:
            grupo_actual = col_a
            nombre_producto_actual = col_a.title()

        # Si aún no tenemos grupo definido, saltar
        if not grupo_actual:
            continue

        # Parsear stock — manejar celdas con fórmulas que pueden traer decimales
        try:
            stock = int(float(col_g))
        except (ValueError, TypeError):
            continue

        # Solo incluir variantes con stock positivo
        if stock <= 0:
            continue

        # Precio desde el mapa fijo
        ref_upper = col_b.upper()
        precio_val = PRECIOS.get(ref_upper, 0)
        precio_fmt = "${:,}".format(precio_val).replace(",", ".") if precio_val else "Consultar"

        # Extraer talla: última palabra de la descripción en mayúsculas
        # Ej: "Chaqueta Safari Negra M" → talla = "M"
        partes_desc = col_c.split()
        talla = partes_desc[-1].upper() if partes_desc else ""

        if grupo_actual not in grupos:
            grupos[grupo_actual] = {
                "nombre": nombre_producto_actual,
                "items": []
            }

        grupos[grupo_actual]["items"].append({
            "ref":    col_b,
            "desc":   col_c,          # descripción completa tal como viene del Sheet
            "talla":  talla,
            "stock":  stock,
            "precio": precio_fmt,
            "precio_val": precio_val,
        })

    if not grupos:
        return "No hay productos disponibles en este momento."

    # ── Construir texto del catálogo ──────────────────────────────────────────
    # Formato por grupo:
    #   - [Nombre Producto] — $precio
    #     Descripción: [desc variante 1], [desc variante 2], ...
    #     Tallas disponibles: S, M, L, XL
    #     Refs (interno): S:SNS (stock 3) | M:SNM (stock 5) | ...
    lineas = []
    for grupo_key, grupo_data in grupos.items():
        items = grupo_data["items"]
        nombre_limpio = grupo_data["nombre"]
        precio_display = items[0]["precio"]

        # Descripciones únicas de las variantes disponibles
        descripciones = list(dict.fromkeys(i["desc"] for i in items))
        desc_str = " / ".join(descripciones)

        # Tallas disponibles
        tallas_str = ", ".join(i["talla"] for i in items)

        # Referencias internas (el bot las usa internamente, nunca las menciona al cliente)
        refs_str = " | ".join(
            f"{i['talla']}:{i['ref']} (stock {i['stock']})"
            for i in items
        )

        lineas.append(
            f"- {nombre_limpio} | Precio: {precio_display}\n"
            f"  Descripción: {desc_str}\n"
            f"  Tallas disponibles: {tallas_str}\n"
            f"  Refs: {refs_str}"
        )

    return "\n\n".join(lineas)


async def registrar_pedido(telefono: str, nombre: str, cedula: str,
                            referencia: str, producto: str, talla: str,
                            color: str, cantidad: int, precio: int,
                            direccion: str, barrio: str, ciudad: str) -> bool:
    """
    Envía el pedido al Apps Script, que se encarga de:
      1. Registrar en la hoja BASE 2026
      2. Descontar stock en la hoja VENTAS del INVENTARIO
      3. Notificar al vendedor por WhatsApp y email
    """
    try:
        data = {
            "telefono":   telefono,
            "nombre":     nombre,
            "cedula":     cedula,
            "referencia": referencia.upper(),  # siempre mayúscula para coincidir con el Sheet
            "producto":   producto,
            "talla":      talla,
            "color":      color,
            "cantidad":   cantidad,
            "precio":     precio,
            "direccion":  direccion,
            "barrio":     barrio,
            "ciudad":     ciudad
        }

        # Primer intento (sin seguir redirects para capturar la URL real)
        async with httpx.AsyncClient(follow_redirects=False) as client:
            r1 = await client.post(
                APPS_SCRIPT_URL,
                content=json.dumps(data),
                headers={"Content-Type": "application/json"},
                timeout=15.0
            )

        # Apps Script suele devolver un redirect 302 → seguirlo manualmente
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