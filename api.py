from fastapi import FastAPI
from BagheeraBrain import generar_contrato_directo
from supabase_client import update_vigencia, debug_vigencia

app = FastAPI()

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
