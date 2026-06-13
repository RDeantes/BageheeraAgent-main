import pandas as pd
import os

ruta = os.path.join(os.path.dirname(__file__), 'CONCENTRADO_EMPLEADOS.xlsx')
df = pd.read_excel(ruta)

df.columns = df.columns.str.strip().str.upper()
df['VIGENCIA'] = pd.to_datetime(df['VIGENCIA'], errors='coerce')

hoy = pd.Timestamp.today().normalize()

vencidos = df[df['VIGENCIA'] < hoy]

print(" CONTRATOS VENCIDOS:\n")
print(vencidos['NOMBRE'])


