import os
from datetime import datetime


try:
    from supabase import create_client
except Exception:
    create_client = None


def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    if not url or not key or create_client is None:
        return None

    try:
        return create_client(url, key)
    except Exception:
        return None


def _normalize_date(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    texto = str(value).strip()
    if not texto:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue

    return None



def fetch_vencidos():
    client = get_supabase_client()
    if not client:
        return []

    tablas = [os.getenv("SUPABASE_TABLE", "empleados"), os.getenv("SUPABASE_CONTRATOS_TABLE", "contratos")]
    hoy = datetime.now().date()

    for tabla in tablas:
        try:
            res = client.table(tabla).select("*").eq("activo", True).execute()
            data = getattr(res, "data", None) or []
            vencidos = []
            for row in data:
                fecha = _normalize_date(
                    row.get("fecha_vigencia") or row.get("vigencia")
                    or row.get("fecha_termino") or row.get("fecha_fin")
                )
                if fecha and fecha < hoy:
                    vencidos.append({
                        "nombre": row.get("nombre") or row.get("NOMBRE") or "",
                        "vigencia": fecha.isoformat(),
                        "tipo": row.get("tipo_contrato") or row.get("tipo") or "",
                        "tabla": tabla,
                    })
            if vencidos:
                return vencidos
        except Exception:
            continue

    return []


def update_vigencia(nombre, nueva_fecha):
    client = get_supabase_client()
    if not client:
        print("❌ [update_vigencia] No hay cliente Supabase. Revisar SUPABASE_URL y SUPABASE_KEY.")
        return False

    texto = str(nombre).strip()
    if not texto or not nueva_fecha:
        print(f"❌ [update_vigencia] Parámetros inválidos: nombre='{nombre}', fecha='{nueva_fecha}'")
        return False

    fecha_str = str(nueva_fecha)
    tabla = os.getenv("SUPABASE_TABLE", "empleados")
    tabla_contratos = os.getenv("SUPABASE_CONTRATOS_TABLE", "contratos")
    tablas = [tabla, tabla_contratos]

    print(f"🔍 [update_vigencia] Buscando '{texto}' en tablas {tablas} para actualizar fecha_vigencia → {fecha_str}")

    for nombre_tabla in tablas:
        try:
            # buscar por nombre (columna "nombre")
            res = client.table(nombre_tabla).select("*").ilike("nombre", f"%{texto}%").limit(1).execute()
            data = getattr(res, "data", None) or []

            # si no encontró, intentar con primeras dos palabras del nombre
            if not data and " " in texto:
                primera_palabra = texto.split()[0]
                res2 = client.table(nombre_tabla).select("*").ilike("nombre", f"%{primera_palabra}%").limit(5).execute()
                data = getattr(res2, "data", None) or []
                if data:
                    print(f"⚠️ [update_vigencia] Match parcial por '{primera_palabra}' en '{nombre_tabla}'")

            if not data:
                print(f"⚠️ [update_vigencia] No se encontró '{texto}' en tabla '{nombre_tabla}'")
                continue

            row = data[0]
            row_id = row.get("id") or row.get("id_empleado") or row.get("id_contrato")
            pk_col = "id" if row.get("id") is not None else ("id_empleado" if row.get("id_empleado") is not None else "id_contrato")
            print(f"✅ [update_vigencia] Empleado encontrado en '{nombre_tabla}': {pk_col}={row_id}, columnas={list(row.keys())}")

            # construir payload solo con columnas que existen en la fila
            columnas_candidatas = ["fecha_vigencia", "vigencia", "fecha_termino", "fecha_fin"]
            cols_presentes = [c for c in columnas_candidatas if c in row]
            if not cols_presentes:
                # la columna no está en el SELECT*, intentar actualizar fecha_vigencia directamente
                cols_presentes = ["fecha_vigencia"]
                print(f"⚠️ [update_vigencia] Ninguna columna de fecha detectada en la fila, usando 'fecha_vigencia' por defecto")

            payload = {c: fecha_str for c in cols_presentes}
            print(f"📝 [update_vigencia] Payload: {payload}")

            if row_id is not None:
                upd = client.table(nombre_tabla).update(payload).eq(pk_col, row_id).execute()
            else:
                upd = client.table(nombre_tabla).update(payload).ilike("nombre", f"%{texto}%").execute()

            upd_data = getattr(upd, "data", None)
            upd_error = getattr(upd, "error", None)
            print(f"📬 [update_vigencia] Respuesta update → data={upd_data}, error={upd_error}")

            if upd_error is None:
                print(f"✅ [update_vigencia] fecha_vigencia actualizada correctamente en '{nombre_tabla}'")
                return True
            else:
                print(f"❌ [update_vigencia] Error en update: {upd_error}")

        except Exception as e:
            print(f"❌ [update_vigencia] Excepción en tabla '{nombre_tabla}': {e}")
            continue

    print(f"❌ [update_vigencia] No se pudo actualizar fecha_vigencia para '{texto}'")
    return False


def debug_vigencia(nombre):
    """Diagnóstico: muestra el estado del empleado en Supabase."""
    client = get_supabase_client()
    if not client:
        return {"error": "Sin cliente Supabase. Verificar SUPABASE_URL y SUPABASE_KEY"}

    texto = str(nombre).strip()
    tabla = os.getenv("SUPABASE_TABLE", "empleados")
    tabla_contratos = os.getenv("SUPABASE_CONTRATOS_TABLE", "contratos")
    resultado = {}

    for nombre_tabla in [tabla, tabla_contratos]:
        try:
            res = client.table(nombre_tabla).select("*").ilike("nombre", f"%{texto}%").limit(3).execute()
            data = getattr(res, "data", None) or []
            resultado[nombre_tabla] = data
        except Exception as e:
            resultado[nombre_tabla] = {"excepcion": str(e)}

    return resultado


def fetch_empleado(nombre):
    client = get_supabase_client()
    if not client:
        return None

    tablas = [os.getenv("SUPABASE_TABLE", "empleados"), os.getenv("SUPABASE_CONTRATOS_TABLE", "contratos")]
    texto = str(nombre).strip().lower()

    for tabla in tablas:
        try:
            res = client.table(tabla).select("*").ilike("nombre", f"%{texto}%").limit(1).execute()
            data = getattr(res, "data", None) or []
            if data:
                return data[0]
        except Exception:
            continue

    return None
