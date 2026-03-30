# paso3_fact_ejecuciones.py

Construye `fact_ejecuciones`, la tabla de hechos principal del modelo de Power BI. Une el output de `leer_db_server()` con `dim_clientes` para producir la tabla completa.

## Responsabilidad

Aplicar las transformaciones finales sobre el DataFrame de ejecuciones para producir una tabla limpia, enriquecida y lista para ser cargada en Power BI.

## Transformaciones aplicadas

### 1. Mapeo proceso → herramienta

El campo `proceso_original` en DB_Server tiene nombres técnicos que no coinciden con los nombres de herramientas del Relevamiento. El diccionario `PROCESO_A_HERRAMIENTA` de `settings.py` traduce uno al otro.

Ejemplos de mapeo muchos a uno:

```
"GUI: Control Correlatividad"         → "Control de correlatividad - ComplyPro"
"GUI: Controlar correlatividad"       → "Control de correlatividad - ComplyPro"
"AFIP voucher correlativity control"  → "Control de correlatividad - ComplyPro"

"GUI: Control Totales"                → "Sumarizacion y control por totales - ComplyPro"
"GUI: Controlar Totales"              → "Sumarizacion y control por totales - ComplyPro"
"GUI: Sumarización & Control..."      → "Sumarizacion y control por totales - ComplyPro"
```

Los procesos sin mapeo en el diccionario conservan su nombre original como herramienta.

### 2. Flag en_relevamiento

```python
df["en_relevamiento"] = ~df["proceso_original"].str.strip().isin(PROCESOS_SIN_HERRAMIENTA)
```

`True` si el proceso corresponde a una herramienta del Relevamiento.
`False` si es un proceso externo (WP-Ganancias, Tablas Ratio, SLATAM, etc.).

Distribución actual:

| en_relevamiento | Ejecuciones | % |
|---|---|---|
| False | 20.179 | 65.3% |
| True | 10.702 | 34.7% |

### 3. Normalización de estados

El campo `estado` en DB_Server tiene múltiples variantes inconsistentes para el mismo resultado. El diccionario `_ESTADO_MAP` los consolida en 4 valores canónicos:

| Estado original | Estado normalizado |
|---|---|
| `"Correcto"` | `Correcto` |
| `"Finalizado"` | `Correcto` |
| `"Erróneo"`, `"Erroneo"` | `Erroneo` |
| `"Proceso terminado con errores"` | `Erroneo` |
| `"Proceso finalizado con errores"` | `Erroneo` |
| `"0"` | `Erroneo` |
| `"Finalizado con observaciones"` | `Con Observaciones` |
| `"Proceso terminado con observaciones"` | `Con Observaciones` |
| `"Proceso finalizado con observaciones"` | `Con Observaciones` |
| `"Correo no enviado"` | `Correo no enviado` |

Distribución resultante:

| Estado normalizado | Cantidad | % |
|---|---|---|
| Correcto | 28.285 | 91.6% |
| Erroneo | 2.269 | 7.4% |
| Con Observaciones | 264 | 0.9% |
| Correo no enviado | 62 | 0.2% |

Los estados que no están en el mapa conservan su valor original (fallback con `fillna`).

### 4. Join con dim_clientes

```python
lookup = dim_clientes.set_index("cuit")[["nombre_cliente", "gerente_responsable"]]
df["nombre_cliente_canonico"] = df["cuit_cliente"].map(lookup["nombre_cliente"])
df["gerente_responsable"]     = df["cuit_cliente"].map(lookup["gerente_responsable"])
```

Este join es un `map()` sobre el índice CUIT, equivalente a un left join pero más eficiente.

Resultado para `nombre_cliente_canonico`:
- Si tiene CUIT resuelto → nombre oficial del Relevamiento
- Si no tiene CUIT → nombre histórico de texto libre (de `cliente_nombre`)
- Si es VACIO → vacío

## Diccionario de estados

::: paso3_fact_ejecuciones._ESTADO_MAP

## Función

::: paso3_fact_ejecuciones.construir_fact_ejecuciones

## Ejemplo de uso

```python
from paso3_fact_ejecuciones import construir_fact_ejecuciones

fact = construir_fact_ejecuciones(df_db, dim_clientes)

print(fact.shape)
# (30881, 19)

print(fact.columns.tolist())
# ['id', 'username', 'proceso_original', 'herramienta', 'en_relevamiento',
#  'estado', 'estado_normalizado', 'iniciado', 'finalizado',
#  'duracion_segundos', 'tipo_cliente', 'cuit_cliente',
#  'nombre_cliente_canonico', 'gerente_responsable', 'items_count',
#  'observaciones', 'anio', 'mes', 'semana']

# Verificar distribución de estados
print(fact["estado_normalizado"].value_counts())
# Correcto             28285
# Erroneo               2269
# Con Observaciones      264
# Correo no enviado       62

# Verificar que el mapeo proceso→herramienta funcionó
print(fact[fact["proceso_original"] == "GUI: Control Correlatividad"]["herramienta"].unique())
# ['Control de correlatividad - ComplyPro']
```
