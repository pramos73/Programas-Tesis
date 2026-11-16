# ============================================
# TESIS COMPARACIÓN DE EFICIENCIA ENTRE PANELES SOLARES FIJOS VS MÓVILES
# ============================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from scipy.stats import pearsonr, spearmanr
import math
from scipy.interpolate import UnivariateSpline
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# ============================================
# CONFIGURACIÓN
# ============================================
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300

DÍAS_ANALIZADOS = [
datetime(2026, 5, 11).date(),
datetime(2026, 5, 12).date(),
datetime(2026, 5, 13).date(),
datetime(2026, 5, 14).date(),
datetime(2026, 5, 15).date(),
datetime(2026, 5, 17).date(),
datetime(2026, 5, 18).date(),
datetime(2026, 5, 19).date(),
datetime(2026, 5, 20).date(),
datetime(2026, 5, 21).date()
]

UMBRAL_POTENCIA = 0.01

# ============================================
# 1. CARGA DE DATOS
# ============================================
print("Leyendo mediciones.csv ...")
df = pd.read_csv('mediciones.csv', parse_dates=['Fecha_Hora'], dayfirst=True)
print(df.head())
print(df['Fecha_Hora'].dtype)
print(df['Fecha_Hora'].min(), df['Fecha_Hora'].max())

# ============================================
# 1a. CONTEO DE FILAS TOTALES Y VÁLIDAS
# ============================================
total_filas = len(df)
print(f"📄 Total de filas en mediciones.csv: {total_filas}")

filas_fecha_valida = df['Fecha_Hora'].notna().sum()
print(f"✅ Filas con fecha/hora válida: {filas_fecha_valida}")

columnas_potencia = [col for col in df.columns if 'Potencia' in col]
if columnas_potencia:
mask_potencia_valida = df[columnas_potencia].gt(0).any(axis=1)
filas_potencia_valida = mask_potencia_valida.sum()
print(f"⚡ Filas con al menos una potencia > 0 W: {filas_potencia_valida}")
else:
filas_potencia_valida = 0
print("⚠️ No se encontraron columnas de potencia")

filas_completas_validas = (df['Fecha_Hora'].notna() & mask_potencia_valida).sum() if columnas_potencia else filas_fecha_valida
print(f"🌟 Filas completamente válidas (fecha OK + potencia > 0): {filas_completas_validas}")
porcentaje = (filas_completas_validas / total_filas) * 100 if total_filas > 0 else 0
print(f"📊 Porcentaje de validez: {porcentaje:.2f}%")

# ============================================
# 2. CORRECCIÓN DE POTENCIA CERO
# ============================================
def corregir_potencia(df, potencia_col, corriente_col, voltaje_col):
cond = (df[potencia_col] <= UMBRAL_POTENCIA) & (df[corriente_col] > 0) & (df[voltaje_col] > 0)
nueva_potencia = df[corriente_col] * df[voltaje_col]
df.loc[cond, potencia_col] = nueva_potencia[cond]
return df

correcciones = [
('🔵 Potencia_2G (W)', '🔵 Corriente_2G (A)', '🔵 Voltaje_2G (V)'),
('🟢 Panel1G_Potencia (W)', '🟢 Panel1G_Corriente (A)', '🟢 Panel1G_Voltaje (V)'),
('🟢 Panel2FIJO_Potencia (W)', '🟢 Panel2FIJO_Corriente (A)', '🟢 Panel2FIJO_Voltaje (V)'),
('🟢 Panel3FIJOA_Potencia (W)', '🟢 Panel3FIJOA_Corriente (A)', '🟢 Panel3FIJOA_Voltaje (V)'),
('🟢 Panel3FIJOB_Potencia (W)', '🟢 Panel3FIJOB_Corriente (A)', '🟢 Panel3FIJOB_Voltaje (V)')
]

for pot, corriente, volt in correcciones:
if pot in df.columns and corriente in df.columns and volt in df.columns:
df = corregir_potencia(df, pot, corriente, volt)
print(f"Corregida columna {pot}")
else:
print(f"Advertencia: no se encontraron las columnas {pot}, {corriente}, {volt}")

# ============================================
# 3. FILTRADO: HORARIO 10-17HS Y DÍAS SOLEADOS
# ============================================
df['hora'] = df['Fecha_Hora'].dt.hour
df = df[(df['hora'] >= 10) & (df['hora'] <= 17)]
df.drop(columns=['hora'], inplace=True)

df['fecha'] = df['Fecha_Hora'].dt.date
df = df[df['fecha'].isin(DÍAS_ANALIZADOS)]
print(f"Filas después de filtros: {len(df)}")

# ============================================
# 4. CREAR COLUMNA DELTA (SUMA DE 3A+3B)
# ============================================
df['Potencia_Delta (W)'] = df['🟢 Panel3FIJOA_Potencia (W)'] + df['🟢 Panel3FIJOB_Potencia (W)']

# ============================================
# 5. DICCIONARIOS DE PANELES
# ============================================
sistemas = {
	'2GDL': '🔵 Potencia_2G (W)',
	'1GDL': '🟢 Panel1G_Potencia (W)',
	'Fijo2A': '🟢 Panel2FIJO_Potencia (W)',
	'Delta (3A+3B)': 'Potencia_Delta (W)'
}
individuales = {
	'Fijo3A': '🟢 Panel3FIJOA_Potencia (W)',
	'Fijo3B': '🟢 Panel3FIJOB_Potencia (W)'
}
todos_los_paneles = {**sistemas, **individuales}

# ============================================
# 6a. CÁLCULO DE ENERGÍA DIARIA (Wh)
# ============================================
delta_h = 1/60   # cada minuto = 1/60 hora
for nombre, col in todos_los_paneles.items():
df[f'Energia_{nombre}'] = df[col] * delta_h

cols_energia = [f'Energia_{nombre}' for nombre in todos_los_paneles.keys()]
energia_diaria = df.groupby('fecha')[cols_energia].sum().round(2)
energia_diaria.columns = [c.replace('Energia_', '') for c in energia_diaria.columns]

# ============================================
# 6b. CÁLCULO DE PROMEDIOS CLIMÁTICOS DIARIOS Y PORCENTAJES DE CONDICIÓN CLIMÁTICA
# ============================================
col_temp = '🟠 Temp_Externa (C°)'
col_hum = '🟠 Hum_Externa (%)'
col_lux = '🔵 Luz_Local (Lux)'
col_cond = '🟠 Condicion_Clima'

clima_diario = None
if all(col in df.columns for col in [col_temp, col_hum, col_lux]):
clima_diario = df.groupby('fecha')[[col_temp, col_hum, col_lux]].mean().round(2)
clima_diario.columns = ['Temp_Promedio (C°)', 'Hum_Promedio (%)', 'Lux_Promedio (Lux)']
print("\n✅ Promedios climáticos diarios (10-17h):")
print(clima_diario)
else:
print("\n⚠️ Advertencia: No se encontraron todas las columnas de Temp/Hum/Lux. Se omitirán.")

if col_cond in df.columns:
cond_counts = df.groupby(['fecha', col_cond]).size().reset_index(name='conteo')
total_por_dia = df.groupby('fecha').size().reset_index(name='total')
cond_counts = cond_counts.merge(total_por_dia, on='fecha')
cond_counts['porcentaje'] = (cond_counts['conteo'] / cond_counts['total']) * 100
cond_counts['porcentaje'] = cond_counts['porcentaje'].round(1)
cond_pivot = cond_counts.pivot(index='fecha', columns=col_cond, values='porcentaje').fillna(0)
orden_condiciones = ['cielo claro', 'nubes dispersas', 'algo de nubes', 'nubes', 'muy nuboso']
columnas_existentes = [c for c in orden_condiciones if c in cond_pivot.columns]
otras = [c for c in cond_pivot.columns if c not in orden_condiciones]
cond_pivot = cond_pivot[columnas_existentes + otras]
print("\n✅ Porcentajes diarios de condición climática (%):")
print(cond_pivot)
if clima_diario is not None:
clima_diario = clima_diario.join(cond_pivot)
else:
clima_diario = cond_pivot.copy()
print("\n⚠️ Solo se generó la tabla de porcentajes (sin Temp/Hum/Lux).")
else:
print("\n⚠️ No se encontró la columna de condición climática ('🟠 Condicion_Clima').")

if clima_diario is not None:
print("\n📊 Tabla climática completa (promedios y porcentajes):")
print(clima_diario)
clima_diario.to_csv('clima_diario_completo.csv')
print("Tabla climática guardada en 'clima_diario_completo.csv'")
else:
print("\n❌ No se pudo generar ninguna tabla climática.")

print("\nEnergía diaria acumulada (Wh):")
print(energia_diaria)
energia_diaria.to_csv('energia_diaria.csv')
print("Tabla de energía guardada en 'energia_diaria.csv'")

# ============================================
# 6c. CORRELACIÓN ENERGÍA GENERADA vs VARIABLES CLIMÁTICAS
# ============================================
df_analisis = energia_diaria.join(clima_diario)
print("\n📊 Datos combinados para análisis de correlación:")
print(df_analisis.head())
df_analisis.to_csv('analisis_energia_clima.csv')
print("Archivo guardado: analisis_energia_clima.csv\n")

paneles_interes = ['2GDL', '1GDL', 'Fijo2A', 'Delta (3A+3B)']
vars_pred = ['Lux_Promedio (Lux)', 'cielo claro', 'Temp_Promedio (C°)', 'Hum_Promedio (%)']

# Figura 1: Energía vs Lux (2 paneles por figura)
fig1, axes1 = plt.subplots(1, 2, figsize=(12, 5))
for ax, panel in zip(axes1, ['2GDL', '1GDL']):
if panel in df_analisis.columns:
ax.scatter(df_analisis['Lux_Promedio (Lux)'], df_analisis[panel], alpha=0.7, edgecolors='k')
z = np.polyfit(df_analisis['Lux_Promedio (Lux)'], df_analisis[panel], 1)
p = np.poly1d(z)
ax.plot(df_analisis['Lux_Promedio (Lux)'].sort_values(),
p(df_analisis['Lux_Promedio (Lux)'].sort_values()), 'r--')
corr = df_analisis['Lux_Promedio (Lux)'].corr(df_analisis[panel])
ax.set_title(f'{panel} (r = {corr:.2f})')
ax.set_xlabel('Lux promedio')
ax.set_ylabel('Energía diaria (Wh)')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('corr_energia_vs_lux_seguidores.png')

fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))
for ax, panel in zip(axes2, ['Fijo2A', 'Delta (3A+3B)']):
if panel in df_analisis.columns:
ax.scatter(df_analisis['Lux_Promedio (Lux)'], df_analisis[panel], alpha=0.7, edgecolors='k')
z = np.polyfit(df_analisis['Lux_Promedio (Lux)'], df_analisis[panel], 1)
p = np.poly1d(z)
ax.plot(df_analisis['Lux_Promedio (Lux)'].sort_values(),
p(df_analisis['Lux_Promedio (Lux)'].sort_values()), 'r--')
corr = df_analisis['Lux_Promedio (Lux)'].corr(df_analisis[panel])
ax.set_title(f'{panel} (r = {corr:.2f})')
ax.set_xlabel('Lux promedio')
ax.set_ylabel('Energía diaria (Wh)')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('corr_energia_vs_lux_fijos_delta.png')

# Figura 3: Energía vs % Cielo claro
fig3, axes3 = plt.subplots(1, 2, figsize=(12, 5))
for ax, panel in zip(axes3, ['2GDL', 'Fijo2A']):
if panel in df_analisis.columns and 'cielo claro' in df_analisis.columns:
ax.scatter(df_analisis['cielo claro'], df_analisis[panel], alpha=0.7, edgecolors='k')
z = np.polyfit(df_analisis['cielo claro'], df_analisis[panel], 1)
p = np.poly1d(z)
ax.plot(df_analisis['cielo claro'].sort_values(),
p(df_analisis['cielo claro'].sort_values()), 'r--')
corr = df_analisis['cielo claro'].corr(df_analisis[panel])
ax.set_title(f'{panel} (r = {corr:.2f})')
ax.set_xlabel('% Cielo claro')
ax.set_ylabel('Energía diaria (Wh)')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('corr_energia_vs_cielo_claro.png')

# Figura 4: Energía vs Temperatura
fig4, axes4 = plt.subplots(1, 2, figsize=(12, 5))
for ax, panel in zip(axes4, ['2GDL', 'Fijo2A']):
if panel in df_analisis.columns and 'Temp_Promedio (C°)' in df_analisis.columns:
ax.scatter(df_analisis['Temp_Promedio (C°)'], df_analisis[panel], alpha=0.7, edgecolors='k')
z = np.polyfit(df_analisis['Temp_Promedio (C°)'], df_analisis[panel], 1)
p = np.poly1d(z)
ax.plot(df_analisis['Temp_Promedio (C°)'].sort_values(),
p(df_analisis['Temp_Promedio (C°)'].sort_values()), 'r--')
corr = df_analisis['Temp_Promedio (C°)'].corr(df_analisis[panel])
ax.set_title(f'{panel} (r = {corr:.2f})')
ax.set_xlabel('Temperatura promedio (°C)')
ax.set_ylabel('Energía diaria (Wh)')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('corr_energia_vs_temp.png')

# Figura 5: Energía vs Humedad
fig5, axes5 = plt.subplots(1, 2, figsize=(12, 5))
for ax, panel in zip(axes5, ['2GDL', 'Fijo2A']):
if panel in df_analisis.columns and 'Hum_Promedio (%)' in df_analisis.columns:
ax.scatter(df_analisis['Hum_Promedio (%)'], df_analisis[panel], alpha=0.7, edgecolors='k')
z = np.polyfit(df_analisis['Hum_Promedio (%)'], df_analisis[panel], 1)
p = np.poly1d(z)
ax.plot(df_analisis['Hum_Promedio (%)'].sort_values(),
p(df_analisis['Hum_Promedio (%)'].sort_values()), 'r--')
corr = df_analisis['Hum_Promedio (%)'].corr(df_analisis[panel])
ax.set_title(f'{panel} (r = {corr:.2f})')
ax.set_xlabel('Humedad promedio (%)')
ax.set_ylabel('Energía diaria (Wh)')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('corr_energia_vs_humedad.png')
print("✅ Análisis de correlación completado. Figuras guardadas.")

# Cálculo de correlación de Pearson con IC y p-valor
x_var = 'Lux_Promedio (Lux)'
results = []
for panel in paneles_interes:
if panel in df_analisis.columns:
data = df_analisis[[x_var, panel]].dropna()
x = data[x_var]
y = data[panel]
if len(x) >= 3:
r, p_value = pearsonr(x, y)
z_fisher = 0.5 * math.log((1 + r) / (1 - r))
se_z = 1 / math.sqrt(len(x) - 3)
z_critical = 1.96
lower_z = z_fisher - z_critical * se_z
upper_z = z_fisher + z_critical * se_z
lower_r = (math.exp(2 * lower_z) - 1) / (math.exp(2 * lower_z) + 1)
upper_r = (math.exp(2 * upper_z) - 1) / (math.exp(2 * upper_z) + 1)
results.append({
	'Panel': panel,
	'r (Pearson)': round(r, 3),
	'p-valor': f'{p_value:.4e}' if p_value < 0.001 else round(p_value, 4),
	'IC 95% inferior': round(lower_r, 3),
	'IC 95% superior': round(upper_r, 3),
	'n (pares)': len(x)
})
else:
results.append({'Panel': panel, 'Observación': 'Datos insuficientes'})
df_corr_stats = pd.DataFrame(results)
print("\n=== CORRELACIÓN ENERGÍA vs LUX (con p-valor e IC 95%) ===")
print(df_corr_stats.to_string(index=False))
df_corr_stats.to_csv('correlacion_energia_lux.csv', index=False)
print("\nTabla guardada como 'correlacion_energia_lux.csv'")

# Correlación de Spearman con otras variables climáticas
vars_climaticas = ['Lux_Promedio (Lux)', 'Temp_Promedio (C°)', 'Hum_Promedio (%)', 'cielo claro']
paneles_spearman = ['2GDL', '1GDL', 'Fijo2A', 'Delta (3A+3B)']
spearman_results = []
for panel in paneles_spearman:
for var in vars_climaticas:
if panel in df_analisis.columns and var in df_analisis.columns:
data = df_analisis[[var, panel]].dropna()
if len(data) >= 3:
rho, p_val = spearmanr(data[var], data[panel])
spearman_results.append({
	'Panel': panel,
	'Variable climática': var,
	'rho (Spearman)': round(rho, 3),
	'p-valor': f'{p_val:.4e}' if p_val < 0.001 else round(p_val, 4),
	'n': len(data)
})
else:
spearman_results.append({'Panel': panel, 'Variable climática': var, 'rho (Spearman)': 'Datos insuficientes', 'p-valor': '-', 'n': 0})
df_spearman = pd.DataFrame(spearman_results)
print("\n=== CORRELACIÓN DE SPEARMAN (energía vs. variables climáticas) ===")
print(df_spearman.to_string(index=False))
df_spearman.to_csv('correlacion_spearman_energia_clima.csv', index=False)
print("Tabla guardada: correlacion_spearman_energia_clima.csv")

# Matriz de correlación de Spearman (mapa de calor)
cols_corr = paneles_spearman + vars_climaticas
df_corr_spearman = df_analisis[cols_corr].dropna().corr(method='spearman')
plt.figure(figsize=(10, 8))
sns.heatmap(df_corr_spearman, annot=True, fmt='.2f', cmap='coolwarm', center=0, square=True, linewidths=0.5)
plt.title('Matriz de correlación de Spearman (energía vs clima)')
plt.tight_layout()
plt.savefig('matriz_correlacion_spearman.png')

# Diagrama de dispersión adicional para Delta (3A+3B) con suavizado
delta_energia = [128.63, 120.03, 100.64, 108.57, 88.41, 110.54, 103.01, 111.3, 81.13, 113.61]
delta_lux = [37900.14, 38142, 23759.2, 28767.58, 26264.06, 28520.85, 26687.6, 24770.01, 15772.1, 20595.7]
plt.figure(figsize=(8,6))
sns.scatterplot(x=delta_lux, y=delta_energia, s=100, color='blue', label='Datos')
z = np.polyfit(delta_lux, delta_energia, 1)
p = np.poly1d(z)
x_line = np.linspace(min(delta_lux), max(delta_lux), 100)
plt.plot(x_line, p(x_line), 'r--', label=f'Regresión lineal (r={0.756:.3f})')
sorted_idx = np.argsort(delta_lux)
lux_sorted = np.array(delta_lux)[sorted_idx]
energia_sorted = np.array(delta_energia)[sorted_idx]
x_smooth = np.linspace(min(delta_lux), max(delta_lux), 300)
try:
spl = UnivariateSpline(lux_sorted, energia_sorted, k=3, s=2)
y_smooth = spl(x_smooth)
plt.plot(x_smooth, y_smooth, 'g-', linewidth=2, label='Suavizado (spline)')
except:
z2 = np.polyfit(delta_lux, delta_energia, 2)
p2 = np.poly1d(z2)
plt.plot(x_line, p2(x_line), 'g-', label='Ajuste cuadrático')
plt.xlabel('Lux promedio (lx)')
plt.ylabel('Energía diaria (Wh)')
plt.title('Delta (3A+3B): Energía vs. Lux')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('delta_energia_vs_lux_suavizado.png', dpi=300)

# ============================================
# 7. GRÁFICA 1: POTENCIA INSTANTÁNEA (DÍA REPRESENTATIVO)
# ============================================
energia_total_dia = energia_diaria[list(sistemas.keys())].sum(axis=1)
dia_ejemplo = energia_total_dia.idxmax()
print(f"\nDía representativo (mayor energía): {dia_ejemplo}")

df_dia = df[df['fecha'] == dia_ejemplo].sort_values('Fecha_Hora')
plt.figure(figsize=(8,4.5))
sombra_inicio = pd.Timestamp(dia_ejemplo).replace(hour=13, minute=0, second=0)
sombra_fin = pd.Timestamp(dia_ejemplo).replace(hour=14, minute=0, second=0)
plt.axvspan(sombra_inicio, sombra_fin, alpha=0.2, color='gray', label='Sombra de antena (13-14h)')
todos_para_grafico = {**sistemas, **individuales}
for nombre, col in todos_para_grafico.items():
plt.plot(df_dia['Fecha_Hora'], df_dia[col], label=nombre, linewidth=1.5)
if '🟠 Condicion_Clima' in df_dia.columns:
freq = df_dia['🟠 Condicion_Clima'].value_counts()
total = len(df_dia)
porcentajes = (freq / total * 100).round(1)
clima_str = ", ".join([f"{p}% {cond}" for cond, p in porcentajes.items()])
else:
clima_str = "Sin datos de clima"
plt.text(0.02, 0.98, f"Clima: {clima_str}",
transform=plt.gca().transAxes, fontsize=8, verticalalignment='top',
bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
if clima_diario is not None and dia_ejemplo in clima_diario.index:
temp_val = clima_diario.loc[dia_ejemplo, 'Temp_Promedio (C°)']
hum_val = clima_diario.loc[dia_ejemplo, 'Hum_Promedio (%)']
lux_val = clima_diario.loc[dia_ejemplo, 'Lux_Promedio (Lux)']
temp_label = f"Temp: {temp_val}°C"
hum_label = f"Hum: {hum_val}%"
lux_label = f"Lux: {lux_val:.0f}"
handles, labels = plt.gca().get_legend_handles_labels()
handles.append(Patch(facecolor='none', edgecolor='none'))
labels.append(temp_label)
handles.append(Patch(facecolor='none', edgecolor='none'))
labels.append(hum_label)
handles.append(Patch(facecolor='none', edgecolor='none'))
labels.append(lux_label)
plt.legend(handles=handles, labels=labels, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
else:
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
plt.xlabel('Hora')
plt.ylabel('Potencia (W)')
plt.title(f'Potencia instantánea - {dia_ejemplo.strftime("%d/%m/%Y")}')
plt.xticks(rotation=45)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('potencia_dia_representativo.png', dpi=300)

# ============================================
# 8. GRÁFICA 2: ENERGÍA DIARIA (BARRAS AGRUPADAS)
# ============================================
dias_analizados = len(energia_diaria)
energia_long = energia_diaria.reset_index().melt(id_vars='fecha', var_name='Panel', value_name='Energía (Wh)')
plt.figure(figsize=(8,4.5))
sns.barplot(data=energia_long, x='fecha', y='Energía (Wh)', hue='Panel')
plt.ylabel('Energía acumulada (Wh)')
plt.title(f'Energía diaria por panel ({dias_analizados} días analizados)')
plt.xticks(rotation=45)
plt.legend(bbox_to_anchor=(1.05,1), loc='upper left')
plt.tight_layout()
plt.savefig('energia_diaria_barras.png')

# ============================================
# 9. GRÁFICA 3: BOXPLOT DISTRIBUCIÓN DE POTENCIA
# ============================================
col_potencias = list(todos_los_paneles.values())
df_power_long = df.melt(id_vars='fecha', value_vars=col_potencias, var_name='Panel', value_name='Potencia (W)')
reverse_map = {v: k for k, v in todos_los_paneles.items()}
df_power_long['Panel'] = df_power_long['Panel'].map(reverse_map)
plt.figure(figsize=(8,4.5))
sns.boxplot(data=df_power_long, x='Panel', y='Potencia (W)', notch=True)
elementos_leyenda = [
Patch(facecolor='gray', edgecolor='black', label='Caja → 50% central de los datos (Q1–Q3)'),
Line2D([0], [0], color='black', lw=2, label='Línea central → Mediana (potencia típica)'),
Line2D([0], [0], color='black', lw=1, linestyle='--', label='Bigotes → Rango típico (sin atípicos)'),
Line2D([0], [0], marker='o', color='red', linestyle='None', markersize=5, label='Puntos → Eventos extremos (outliers)')
]
plt.legend(handles=elementos_leyenda, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
plt.ylabel('Potencia (W)')
plt.title('Distribución de potencia (10-17h, días analizados)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('boxplot_potencias.png')

# ============================================
# 10. ANÁLISIS DE RENDIMIENTO Y EFICIENCIA RELATIVA
# ============================================
print("\n=== ESTADÍSTICAS DESCRIPTIVAS (Potencia en W) ===")
for nombre, col in todos_los_paneles.items():
if col in df.columns:
media = df[col].mean()
mediana = df[col].median()
maximo = df[col].max()
print(f"{nombre:15} | Media: {media:6.2f} | Mediana: {mediana:5.2f} | Máx: {maximo:5.2f}")
if 'Fijo3A' in individuales and 'Fijo3B' in individuales:
df['Dif_3A_3B'] = df['🟢 Panel3FIJOA_Potencia (W)'] - df['🟢 Panel3FIJOB_Potencia (W)']
print(f"\nDiferencia media (3A - 3B): {df['Dif_3A_3B'].mean():.2f} W")

# Contribución porcentual con datos climáticos
print("\n=== CONTRIBUCIÓN PORCENTUAL DE CADA PANEL RESPECTO A LA ENERGÍA TOTAL DE TODOS LOS PANELES ===")
if '🟠 Condicion_Clima' in df.columns:
freq_clima = df.groupby(['fecha', '🟠 Condicion_Clima']).size().reset_index(name='conteo')
total_por_dia = df.groupby('fecha').size().reset_index(name='total')
freq_clima = freq_clima.merge(total_por_dia, on='fecha')
freq_clima['porcentaje'] = (freq_clima['conteo'] / freq_clima['total']) * 100
freq_clima['porcentaje'] = freq_clima['porcentaje'].round(1)
clima_porcentajes_texto = {}
for fecha in freq_clima['fecha'].unique():
sub = freq_clima[freq_clima['fecha'] == fecha].sort_values('porcentaje', ascending=False)
partes = [f"{row['porcentaje']}% {row['🟠 Condicion_Clima']}" for _, row in sub.iterrows()]
clima_porcentajes_texto[fecha] = "con: " + ", ".join(partes)
else:
clima_porcentajes_texto = {}
print("⚠️ No se encontró columna '🟠 Condicion_Clima'")

for dia in energia_diaria.index:
total_todos = energia_diaria.loc[dia, list(todos_los_paneles.keys())].sum()
if total_todos == 0:
print(f"\nDía {dia.strftime('%d/%m/%Y')}: sin datos")
continue
clima_texto = clima_porcentajes_texto.get(dia, "sin datos climáticos")
if clima_diario is not None and dia in clima_diario.index:
t = clima_diario.loc[dia, 'Temp_Promedio (C°)']
h = clima_diario.loc[dia, 'Hum_Promedio (%)']
l = clima_diario.loc[dia, 'Lux_Promedio (Lux)']
clima_texto += f" | 🌡️ {t}°C | 💧 {h}% | ☀️ {l:.0f} Lux"
print(f"\nDía {dia.strftime('%d/%m/%Y')} estuvo {clima_texto}:")
for panel in todos_los_paneles.keys():
proporcion = 100 * energia_diaria.loc[dia, panel] / total_todos
print(f"  {panel:15} : {proporcion:.1f}%")

# Tabla de estadísticas descriptivas de potencia
stats_list = []
for nombre, columna in todos_los_paneles.items():
if columna in df.columns:
datos = df[columna].dropna()
if len(datos) > 0:
q1 = datos.quantile(0.25)
q3 = datos.quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5*iqr
upper_bound = q3 + 1.5*iqr
outliers = datos[(datos < lower_bound) | (datos > upper_bound)]
stats = {
	'Panel': nombre,
	'Media (W)': round(datos.mean(), 2),
	'Mediana (W)': round(datos.median(), 2),
	'Q1 (W)': round(q1, 2),
	'Q3 (W)': round(q3, 2),
	'IQR (W)': round(iqr, 2),
	'Mínimo (W)': round(datos.min(), 2),
	'Máximo (W)': round(datos.max(), 2),
	'Outliers': len(outliers)
}
stats_list.append(stats)
df_stats = pd.DataFrame(stats_list).set_index('Panel')
print("\n=== ESTADÍSTICAS DE POTENCIA POR PANEL (Watts) ===")
print(df_stats.to_string())
df_stats.to_csv('estadisticas_potencia.csv')
print("\nTabla guardada como 'estadisticas_potencia.csv'")

# ============================================
# SERIE TEMPORAL DE ENERGÍA DIARIA + LUX PROMEDIO
# ============================================
paneles_principales = ['2GDL', '1GDL', 'Fijo2A', 'Delta (3A+3B)']
fig, ax1 = plt.subplots(figsize=(12, 6))
for panel in paneles_principales:
if panel in energia_diaria.columns:
ax1.plot(energia_diaria.index, energia_diaria[panel], marker='o', linewidth=2, label=panel)
ax1.set_xlabel('Fecha')
ax1.set_ylabel('Energía diaria (Wh)', color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.grid(alpha=0.3)
ax1.legend(loc='upper left')
if clima_diario is not None and 'Lux_Promedio (Lux)' in clima_diario.columns:
ax2 = ax1.twinx()
fechas_comunes = energia_diaria.index.intersection(clima_diario.index)
lux_values = clima_diario.loc[fechas_comunes, 'Lux_Promedio (Lux)']
ax2.plot(fechas_comunes, lux_values, 'k--', marker='s', linewidth=2, label='Lux promedio')
ax2.set_ylabel('Lux promedio (lx)', color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax2.legend(loc='upper right')
plt.title('Evolución diaria de la energía generada y Lux promedio')
plt.xticks(rotation=45)
fig.tight_layout()
plt.savefig('serie_temporal_energia_con_lux.png')

# ============================================
# EFICIENCIA NORMALIZADA (Wh/W)
# ============================================
nominales = {'2GDL': 6, '1GDL': 6, 'Fijo2A': 6, 'Delta (3A+3B)': 12, 'Fijo3A': 6, 'Fijo3B': 6}
energia_media = energia_diaria.mean().round(2)
eficiencia_norm = {panel: energia_media[panel] / nominales[panel] for panel in energia_media.index if panel in nominales}
df_eficiencia_norm = pd.DataFrame.from_dict(eficiencia_norm, orient='index', columns=['Wh/W']).sort_values('Wh/W', ascending=False)
plt.figure(figsize=(8,5))
bars = plt.bar(df_eficiencia_norm.index, df_eficiencia_norm['Wh/W'], color='skyblue', edgecolor='black')
for bar in bars:
height = bar.get_height()
plt.text(bar.get_x() + bar.get_width()/2., height + 0.2, f'{height:.2f}', ha='center', va='bottom', fontsize=9)
plt.ylabel('Energía media por vatio nominal (Wh/W)')
plt.xlabel('Panel')
plt.title('Eficiencia normalizada (energía diaria / potencia nominal)')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('eficiencia_normalizada_wh_por_w.png')

# ============================================
# EFICIENCIA RELATIVA (vs mejor fijo)
# ============================================
if 'df_stats' not in locals():
medianas = {}
for nombre, columna in todos_los_paneles.items():
if columna in df.columns:
medianas[nombre] = df[columna].median()
df_stats = pd.DataFrame.from_dict(medianas, orient='index', columns=['Mediana (W)'])
referencia = df_stats.loc['Fijo2A', 'Mediana (W)']
eficiencia_relativa = (df_stats['Mediana (W)'] / referencia) * 100
eficiencia_relativa = eficiencia_relativa.sort_values(ascending=False)
colores = ['#2E86AB' if 'GDL' in p else '#A23B72' for p in eficiencia_relativa.index]
plt.figure(figsize=(8,5))
bars = plt.bar(eficiencia_relativa.index, eficiencia_relativa.values, color=colores, edgecolor='black')
for bar in bars:
height = bar.get_height()
plt.text(bar.get_x() + bar.get_width()/2., height + 2, f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
plt.ylabel('Eficiencia relativa (%)', fontsize=12)
plt.xlabel('Panel', fontsize=12)
plt.title('Eficiencia relativa respecto al mejor panel fijo (Fijo2A = 100%)', fontsize=13)
plt.ylim(0, max(eficiencia_relativa) * 1.15)
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('eficiencia_relativa_vs_fijo.png', dpi=300)
print("\nEficiencia relativa (%):")
print(eficiencia_relativa.round(1))

# ============================================
# ANÁLISIS INTEGRAL: Lux, potencia, temperatura, humedad, condición climática
# ============================================
vars_ambientales = ['🔵 Luz_Local (Lux)', '🟠 Temp_Externa (C°)', '🔵 Hum_Local (%)']
paneles_clave = {
	'2GDL (seguidor 2 ejes)': '🔵 Potencia_2G (W)',
	'1GDL (seguidor 1 eje)': '🟢 Panel1G_Potencia (W)',
	'Fijo2A (mejor fijo)': '🟢 Panel2FIJO_Potencia (W)',
	'Delta (3A+3B)': 'Potencia_Delta (W)'
}
for nombre, col in paneles_clave.items():
if col not in df.columns:
print(f"⚠️ Advertencia: columna '{col}' no encontrada para {nombre}")

# Matriz de correlación
columnas_corr = vars_ambientales + list(paneles_clave.values())
df_corr = df[columnas_corr].dropna()
corr_matrix = df_corr.corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, square=True, linewidths=0.5)
plt.title('Matriz de correlación: potencia vs variables ambientales')
plt.tight_layout()
plt.savefig('correlacion_ambiental.png')

# Gráficos de dispersión Potencia vs Lux
paneles_lista = list(paneles_clave.items())
grupo1 = paneles_lista[:2]
grupo2 = paneles_lista[2:]
fig1, axes1 = plt.subplots(1, 2, figsize=(12, 5))
for ax, (nombre, col) in zip(axes1, grupo1):
if col in df.columns:
mask = (df['🔵 Luz_Local (Lux)'] > 0) & (df[col] > 0)
x = df.loc[mask, '🔵 Luz_Local (Lux)']
y = df.loc[mask, col]
if len(x) > 0:
ax.scatter(x, y, alpha=0.3, s=10)
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
ax.plot(x.sort_values(), p(x.sort_values()), 'r--', linewidth=2)
ax.set_title(f'{nombre}\nPendiente: {z[0]*1000:.2f} W/klux')
else:
ax.text(0.5, 0.5, 'Sin datos válidos', ha='center', transform=ax.transAxes)
ax.set_xlabel('Lux (iluminancia)')
ax.set_ylabel('Potencia (W)')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('potencia_vs_lux_seguidores.png')

fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))
for ax, (nombre, col) in zip(axes2, grupo2):
if col in df.columns:
mask = (df['🔵 Luz_Local (Lux)'] > 0) & (df[col] > 0)
x = df.loc[mask, '🔵 Luz_Local (Lux)']
y = df.loc[mask, col]
if len(x) > 0:
ax.scatter(x, y, alpha=0.3, s=10)
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
ax.plot(x.sort_values(), p(x.sort_values()), 'r--', linewidth=2)
ax.set_title(f'{nombre}\nPendiente: {z[0]*1000:.2f} W/klux')
else:
ax.text(0.5, 0.5, 'Sin datos válidos', ha='center', transform=ax.transAxes)
ax.set_xlabel('Lux (iluminancia)')
ax.set_ylabel('Potencia (W)')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('potencia_vs_lux_fijos_delta.png')

# Boxplots de potencia por condición climática
cond_col = '🟠 Condicion_Clima'
if cond_col in df.columns:
fig1, axes1 = plt.subplots(1, 2, figsize=(14, 5))
for ax, (nombre, col) in zip(axes1, grupo1):
if col in df.columns:
df_box = df[[cond_col, col]].dropna()
order = df_box.groupby(cond_col)[col].median().sort_values(ascending=False).index
sns.boxplot(data=df_box, x=cond_col, y=col, order=order, ax=ax)
ax.set_title(nombre)
ax.set_xlabel('Condición climática')
ax.set_ylabel('Potencia (W)')
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig('potencia_vs_condicion_seguidores.png')
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
for ax, (nombre, col) in zip(axes2, grupo2):
if col in df.columns:
df_box = df[[cond_col, col]].dropna()
order = df_box.groupby(cond_col)[col].median().sort_values(ascending=False).index
sns.boxplot(data=df_box, x=cond_col, y=col, order=order, ax=ax)
ax.set_title(nombre)
ax.set_xlabel('Condición climática')
ax.set_ylabel('Potencia (W)')
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig('potencia_vs_condicion_fijos_delta.png')

# Eficiencia normalizada (W/klux)
eficiencia_klux = {}
for nombre, col in paneles_clave.items():
if col in df.columns and '🔵 Luz_Local (Lux)' in df.columns:
mask = (df['🔵 Luz_Local (Lux)'] > 0) & (df[col] > 0)
if mask.sum() > 0:
relacion = (df.loc[mask, col] / df.loc[mask, '🔵 Luz_Local (Lux)']).mean() * 1000
eficiencia_klux[nombre] = relacion
else:
eficiencia_klux[nombre] = np.nan
df_eficiencia = pd.DataFrame.from_dict(eficiencia_klux, orient='index', columns=['W/klux']).round(2).sort_values('W/klux', ascending=False)
print("\n=== EFICIENCIA NORMALIZADA (W por cada 1000 lux) ===")
print(df_eficiencia.to_string())
df_eficiencia.to_csv('eficiencia_normalizada.csv')

# Gráfico potencia vs temperatura y humedad (ejemplo 2GDL)
panel_ejemplo = '🔵 Potencia_2G (W)'
if panel_ejemplo in df.columns:
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
mask_temp = (df['🟠 Temp_Externa (C°)'].notna()) & (df[panel_ejemplo] > 0)
ax1.scatter(df.loc[mask_temp, '🟠 Temp_Externa (C°)'], df.loc[mask_temp, panel_ejemplo], alpha=0.3, s=10)
ax1.set_xlabel('Temperatura externa (°C)')
ax1.set_ylabel('Potencia 2GDL (W)')
ax1.set_title('Potencia vs Temperatura')
ax1.grid(alpha=0.3)
mask_hum = (df['🔵 Hum_Local (%)'].notna()) & (df[panel_ejemplo] > 0)
ax2.scatter(df.loc[mask_hum, '🔵 Hum_Local (%)'], df.loc[mask_hum, panel_ejemplo], alpha=0.3, s=10)
ax2.set_xlabel('Humedad externa (%)')
ax2.set_ylabel('Potencia 2GDL (W)')
ax2.set_title('Potencia vs Humedad')
ax2.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('potencia_vs_temp_humedad.png')
else:
print("No se encontró columna de potencia para el panel ejemplo (2GDL).")

print("\nAnálisis integral completado. Archivos generados: correlación, scatter, boxplots, eficiencia normalizada.")
print("\nScript finalizado. Archivos generados: .csv y múltiples gráficos .png")
plt.show()