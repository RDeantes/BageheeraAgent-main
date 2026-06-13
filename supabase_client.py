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
            res = client.table(tabla).select("*").execute()
            data = getattr(res, "data", None) or []
            vencidos = []
            for row in data:
                fecha = _normalize_date(row.get("vigencia") or row.get("fecha_termino") or row.get("fecha_fin"))
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
