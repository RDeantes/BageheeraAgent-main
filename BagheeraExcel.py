import unicodedata
from datetime import datetime
from google_sheets import get_sheet
from supabase_client import fetch_empleado as fetch_supabase_empleado, update_vigencia as update_supabase_vigencia


# =========================================================
# LIMPIAR TEXTO
# =========================================================
def limpiar(texto):
    texto = str(texto).lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto.strip()


# =========================================================
# BUSCAR EMPLEADO (MATCH SEGURO)
# =========================================================
def buscar_empleado(nombre):
    try:
        sheet = get_sheet()
        registros = sheet.get_all_records()
    except Exception:
        empleado = fetch_supabase_empleado(nombre)
        return empleado

    nombre_limpio = limpiar(nombre)
    palabras_input = nombre_limpio.split()

    # EXACTO
    for row in registros:
        nombre_row = row.get("NOMBRE") or row.get("nombre") or ""
        if limpiar(nombre_row) == nombre_limpio:
            return row

    # POR COINCIDENCIAS (mínimo 2 palabras)
    mejor = None
    mejor_score = 0

    for row in registros:
        nombre_row = row.get("NOMBRE") or row.get("nombre") or ""
        palabras_excel = limpiar(nombre_row).split()

        score = sum(1 for p in palabras_input if p in palabras_excel)

        if score > mejor_score:
            mejor_score = score
            mejor = row

    if mejor_score >= 2:
        return mejor

    return None


# =========================================================
# ACTUALIZAR VIGENCIA
# =========================================================
def actualizar_vigencia(nombre, nueva_fecha):
    try:
        sheet = get_sheet()
        registros = sheet.get_all_records()
    except Exception:
        print("⚠️ No se actualizó la vigencia porque GOOGLE_CREDS no está disponible en Railway")
        return False

    for i, row in enumerate(registros):
        if limpiar(row.get("NOMBRE", "")) == limpiar(nombre):
            sheet.update_cell(i + 2, 7, str(nueva_fecha))
            print("✅ Vigencia actualizada")
            return True

    return False


# =========================================================
# OBTENER ID
# =========================================================
def obtener_proximo_id():
    sheet = get_sheet()
    registros = sheet.get_all_records()

    if not registros:
        return 1

    ids = [int(r["ID"]) for r in registros if str(r.get("ID", "")).isdigit()]
    return max(ids) + 1 if ids else 1


# =========================================================
# AGREGAR EMPLEADO
# =========================================================
def agregar_empleado(data):
    sheet = get_sheet()

    nuevo_id = obtener_proximo_id()

    fila = [
        nuevo_id,
        data.get("NOMBRE", ""),
        data.get("AREA", ""),
        data.get("PUESTO", ""),
        data.get("FECHA_INGRESO", ""),
        data.get("TIPO_CONTRATO", ""),
        data.get("VIGENCIA", ""),
        data.get("NACIONALIDAD", ""),
        data.get("SEXO", ""),
        data.get("CURP", ""),
        data.get("DOMICILIO", "")
    ]

    sheet.append_row(fila)

    print("✅ GUARDADO:", fila)
    return nuevo_id


# =========================================================
# CONTRATO DESDE SHEETS (FIX COMPLETO)
# =========================================================
def contrato_desde_excel(datos, generar_contrato_func, personalidad_func):

    persona = buscar_empleado(datos["nombre"])

    if persona is None:
        return personalidad_func("❌ No encontré al empleado")

    nombre_persona = persona.get("NOMBRE") or persona.get("nombre") or datos.get("nombre", "")

    datos_finales = {
        "tipo": datos.get("tipo", ""),
        "jornada": datos.get("jornada", ""),
        "duracion": datos.get("duracion", ""),
        "fecha_inicio": datos.get("fecha_inicio", ""),
        "fecha_termino": datos.get("fecha_termino", ""),
        "nombre": nombre_persona,
        "nacionalidad": persona.get("NACIONALIDAD") or persona.get("nacionalidad", ""),
        "sexo": persona.get("SEXO") or persona.get("sexo", ""),
        "curp": persona.get("CURP") or persona.get("curp", ""),
        "domicilio": persona.get("DOMICILIO") or persona.get("domicilio", ""),
        "puesto": persona.get("PUESTO") or persona.get("puesto", ""),
        "dias": "LUNES A SABADO"
    }

    pdf = generar_contrato_func(datos_finales)

    try:
        actualizar_vigencia(nombre_persona, datos_finales["fecha_termino"])
    except Exception:
        pass

    update_supabase_vigencia(nombre_persona, datos_finales["fecha_termino"])

    return pdf