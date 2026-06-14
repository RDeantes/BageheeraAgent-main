import os
from fastapi import FastAPI, Header, HTTPException
from BagheeraBrain import generar_contrato_directo
from supabase_client import update_vigencia, debug_vigencia
from vigencias import listar_vencidos

app = FastAPI()

CRON_SECRET = os.getenv("CRON_SECRET", "")


def _verificar_cron(x_cron_secret: str):
    if CRON_SECRET and x_cron_secret != CRON_SECRET:
        raise HTTPException(status_code=401, detail="No autorizado")


@app.get("/")
def root():
    return {"status": "Bagheera API activa 🐱"}

@app.post("/contrato")
def generar(data: dict):
    archivo = generar_contrato_directo(
        data["nombre"],
        data["fecha_inicio"],
        data["fecha_termino"]
    )
    return {
        "status": "ok",
        "archivo": archivo
    }

@app.get("/debug-vigencia/{nombre}")
def debug(nombre: str):
    """Muestra lo que hay en Supabase para ese empleado."""
    return debug_vigencia(nombre)

@app.post("/forzar-vigencia")
def forzar_vigencia(data: dict):
    """Actualiza fecha_vigencia directamente. Body: {nombre, fecha_vigencia}"""
    ok = update_vigencia(data["nombre"], data["fecha_vigencia"])
    return {"actualizado": ok, "nombre": data["nombre"], "fecha_vigencia": data["fecha_vigencia"]}


@app.get("/check-vigencias")
def check_vigencias(x_cron_secret: str = Header(default="")):
    """Endpoint llamado por el Cron Job de Railway cada día."""
    _verificar_cron(x_cron_secret)

    vencidos = listar_vencidos()

    if not vencidos:
        return {"status": "ok", "mensaje": "No hay contratos vencidos.", "vencidos": []}

    return {
        "status": "alerta",
        "total": len(vencidos),
        "vencidos": vencidos,
    }
