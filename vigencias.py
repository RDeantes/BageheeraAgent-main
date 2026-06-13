from datetime import datetime

from google_sheets import get_sheet
from supabase_client import fetch_vencidos as fetch_supabase_vencidos


def _is_inactive_status(row):
    for key in ("status", "estado", "estado_contrato", "situacion", "situacion_contrato"):
        value = str(row.get(key) or "").strip().lower()
        if value in ("inactivo", "inactive", "desactivado", "no activo", "no_activo", "baja"):
            return True
        if value.startswith("inact"):
            return True
    return False


def listar_vencidos():
    supabase_vencidos = fetch_supabase_vencidos()
    if supabase_vencidos:
        return supabase_vencidos
    try:
        sheet = get_sheet()
        registros = sheet.get_all_records()
    except Exception:
        return []

    hoy = datetime.now().date()
    vencidos = []

    for row in registros:
        if _is_inactive_status(row):
            continue

        vigencia_raw = row.get("vigencia") or row.get("VIGENCIA") or row.get("fecha_termino") or row.get("FECHA_FIN")
        texto = str(vigencia_raw).strip()
        if not texto:
            continue

        try:
            fecha = datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            continue

        if fecha < hoy:
            vencidos.append({
                "nombre": row.get("NOMBRE") or row.get("nombre") or "",
                "vigencia": fecha.isoformat(),
                "tipo": row.get("TIPO_CONTRATO") or row.get("tipo") or "",
            })

    return vencidos
