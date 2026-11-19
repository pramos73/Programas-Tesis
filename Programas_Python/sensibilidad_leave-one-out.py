import pandas as pd
import numpy as np
import warnings

# Ocultar advertencias
warnings.filterwarnings('ignore')

# 1. Cargar los datos. 
# decimal=',' para números con coma
df = pd.read_csv('mediciones.csv', low_memory=False, decimal=',')

# 2. Convertir Fecha_Hora a datetime
df['Fecha_Hora'] = pd.to_datetime(df['Fecha_Hora'], dayfirst=True)

# 3. Filtrar por la ventana horaria de 10:00 a 17:00
df = df[(df['Fecha_Hora'].dt.hour >= 10) & (df['Fecha_Hora'].dt.hour <= 17)]

# 4. Extraer solo la fecha como texto ("2026-05-11")
df['Fecha_Str'] = df['Fecha_Hora'].dt.strftime('%Y-%m-%d')

# 5. Definir los 10 días válidos que analizaste (los de mayo)
dias_validos_str = [
    '2026-05-11', '2026-05-12', '2026-05-13', '2026-05-14', '2026-05-15',
    '2026-05-17', '2026-05-18', '2026-05-19', '2026-05-20', '2026-05-21'
]

# Filtrar el dataframe solo con los días válidos
df = df[df['Fecha_Str'].isin(dias_validos_str)].copy()
print(f"Filas después del filtro de días: {len(df)}")

# 6. Nombres EXACTOS de las columnas de potencia
columnas_potencia = {
    '2GDL': '🔵 Potencia_2G (W)',
    '1GDL': '🟢 Panel1G_Potencia (W)',
    'Fijo2A': '🟢 Panel2FIJO_Potencia (W)',
    'Fijo3A': '🟢 Panel3FIJOA_Potencia (W)',
    'Fijo3B': '🟢 Panel3FIJOB_Potencia (W)'
}

# 7. Función para calcular la energía diaria
def calcular_energia_diaria(grupo):
    grupo = grupo.sort_values('Fecha_Hora')
    energias = {}
    
    t_horas = ((grupo['Fecha_Hora'] - grupo['Fecha_Hora'].iloc[0]).dt.total_seconds() / 3600).to_numpy()
    
    for nombre, col in columnas_potencia.items():
        # Al haber usado decimal=',', pandas ya leyó los datos como números.
        # Solo aseguramos que sean float y rellenamos nulos.
        P_valores = pd.to_numeric(grupo[col], errors='coerce').fillna(0).to_numpy(dtype=float)
        
        energia = np.trapezoid(P_valores, t_horas)
        energias[nombre] = energia
        
    return pd.Series(energias)

# Aplicar el cálculo por día
df_energia = df.groupby('Fecha_Str').apply(calcular_energia_diaria)

# Agregar la configuración Delta
df_energia['Delta (3A+3B)'] = df_energia['Fijo3A'] + df_energia['Fijo3B']

print("\n======================================================")
print("       ENERGÍA DIARIA CALCULADA (Wh)")
print("======================================================")
print(df_energia.round(2).to_string())
print("\n")

# 8. ANÁLISIS LEAVE-ONE-OUT (LOO)

resultados_loo = []

for dia_excluido in dias_validos_str:
    # Excluir el día actual
    df_loo = df_energia[df_energia.index != dia_excluido]
    
    # Calcular medianas (ignorando el día excluido)
    medianas = df_loo.median()
    
    # VERIFICAR LA JERARQUÍA CORRECTA: 2GDL > 1GDL > Delta > Fijo2A
    jerarquia_ok = (medianas['2GDL'] > medianas['1GDL']) and \
                   (medianas['1GDL'] > medianas['Delta (3A+3B)']) and \
                   (medianas['Delta (3A+3B)'] > medianas['Fijo2A'])
    
    resultados_loo.append({
        'Día_excluido': dia_excluido,
        'Mediana_2GDL': medianas['2GDL'],
        'Mediana_1GDL': medianas['1GDL'],
        'Mediana_Delta': medianas['Delta (3A+3B)'],
        'Mediana_Fijo2A': medianas['Fijo2A'],
        'Jerarquia_ok': jerarquia_ok
    })

df_loo = pd.DataFrame(resultados_loo)

print("======================================================")
print("       RESULTADOS LEAVE-ONE-OUT")
print("======================================================")
print(df_loo.round(2).to_string(index=False))
print("\n")

# 9. Conclusión automática
if df_loo['Jerarquia_ok'].all():
    print("✅ CONCLUSIÓN: La jerarquía 2GDL > 1GDL > Delta > Fijo2A se mantiene en TODAS las iteraciones.")
    print("Esto sugiere que la tendencia observada no depende de un día particular.")
else:
    print("⚠️ CONCLUSIÓN: La jerarquía cambia en al menos una iteración.")