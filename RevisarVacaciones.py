#generame el script de python para revisar las vacaciones por mes, el script se llamara RevisarVacaciones.py y debe leer el archivo de excel CONCENTRADO_EMPLEADOS.xlsx y mostrar los empleados que cumplen años de ingreso en el mes que le solicite a bagira. el script debe recibir como argumento el mes que se le solicita a bagira, por ejemplo: "Enero", "Febrero", etc. y debe mostrar los empleados que cumplen años de ingreso en ese mes. el script debe mostrar el nombre del empleado y la fecha de ingreso.  
import pandas as pd
import sys
import os

# 🧠 Obtener el mes (con modo seguro)
if len(sys.argv) > 1:
    mes = sys.argv[1].lower()
else:
    mes = "abril"  # 👈 valor por defecto para pruebas

# 📂 Ruta del archivo (misma carpeta del script)
ruta = os.path.join(os.path.dirname(__file__), 'CONCENTRADO_EMPLEADOS.xlsx')

df = pd.read_excel(ruta)

# 🧹 Limpiar nombres de columnas
df.columns = df.columns.str.strip().str.upper()

# 🔍 Detectar columna de fecha de ingreso automáticamente
col_fecha = None
for col in df.columns:
    if "INGRESO" in col:
        col_fecha = col
        break

if not col_fecha:
    print("❌ No encontré la columna de fecha de ingreso")
    exit()

# 🔄 Convertir a fecha
df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')

# 📅 Diccionario de meses en español
meses = {
    "enero":1, "febrero":2, "marzo":3, "abril":4,
    "mayo":5, "junio":6, "julio":7, "agosto":8,
    "septiembre":9, "octubre":10, "noviembre":11, "diciembre":12
}

mes_num = meses.get(mes)

if not mes_num:
    print("❌ Mes no válido")
    exit()

# 🎯 Filtrar empleados por mes de ingreso
df['MES'] = df[col_fecha].dt.month
vacaciones = df[df['MES'] == mes_num]

# 🔍 Detectar columna de nombre automáticamente
col_nombre = None
for col in df.columns:
    if "NOMBRE" in col:
        col_nombre = col
        break

if not col_nombre:
    print("❌ No encontré la columna de nombre")
    exit()

# 📢 Mostrar resultados
if vacaciones.empty:
    print(f"No hay empleados que cumplan aniversario en {mes}")
else:
    print(f"Empleados que cumplen aniversario en {mes}:\n")
    print(vacaciones[[col_nombre, col_fecha]])