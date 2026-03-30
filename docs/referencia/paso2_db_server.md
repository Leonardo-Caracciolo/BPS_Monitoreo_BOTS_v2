# paso2_db_server.py

Lectura, normalización y clasificación de DB_Server.xlsx. Usa `clean_datos()` como base y aplica las transformaciones de negocio para enriquecer cada ejecución con información del cliente.

## Responsabilidad

Transformar el DataFrame crudo de `clean_datos()` en un DataFrame completamente clasificado y enriquecido, listo para ser consumido por `paso3_fact_ejecuciones.py`.

## El problema central: campo `cliente` inconsistente

La columna `cliente` en DB_Server tiene tres formatos posibles que requieren tratamientos distintos:

```
Tipo CUIT:    "30717579360"           → usar directamente como clave
Tipo NOMBRE:  "FACEBOOK ARGENTINA"   → normalizar variantes, intentar resolver a CUIT
Tipo VACIO:   NULL, "No definido"    → sin cliente asignado
```

Distribución actual:

| Tipo | Cantidad | % |
|---|---|---|
| VACIO | 17.220 | 55.8% |
| NOMBRE | 13.659 | 44.2% |
| CUIT | 2 | 0.0% |

## Pipeline de transformación

### Paso 1: Leer y limpiar (clean_datos)

```python
df = clean_datos(str(path_db))
# → 30.881 filas, strings con strip y collapse de espacios
```

### Paso 2: Preparar lookup nombre → CUIT

Construye un diccionario a partir de `Tabla_Cuits.xlsx` para intentar resolver nombres a CUITs:

```python
lookup_cuit = {
    "FACEBOOK ARGENTINA SRL": "30712132554",
    "SIDERCA SAIC":           "30550815997",
    # ... ~9.249 entradas, pero solo ~20 matchean con los nombres de DB_Server
}
```

La comparación es insensible a mayúsculas (se normaliza a `upper()`).

### Paso 3: Normalizar variantes (CLIENTE_VARIANTES)

Antes de clasificar, se unifican las variantes del mismo cliente:

```python
# "ExxonMobil", "Exxonmobil", "EXXONMOBIL" → todos a "EXXONMOBIL"
df["cliente_norm"] = df["cliente"].apply(
    lambda v: CLIENTE_VARIANTES.get(str(v).strip(), str(v).strip())
)
```

### Paso 4: Clasificar

```python
df["tipo_cliente"] = df["cliente_norm"].apply(_clasificar_cliente)
# → "CUIT" / "NOMBRE" / "VACIO"
```

### Paso 5: Resolver CUITs por tipo

```python
# CUIT → usar directamente
df.loc[mask_cuit, "cuit_cliente"] = df.loc[mask_cuit, "cliente_norm"]

# NOMBRE → guardar nombre + intentar resolver a CUIT
df.loc[mn, "cliente_nombre"] = df.loc[mn, "cliente_norm"]
df.loc[mn, "cuit_cliente"]   = df.loc[mn, "cliente_norm"].str.upper().map(lookup_cuit).fillna("")

# VACIO → quedan vacíos
```

### Paso 6: Calcular campos temporales

```python
df["duracion_segundos"] = (finalizado - iniciado).total_seconds().clip(lower=0)
df["anio"]   = df["iniciado"].dt.year.astype("Int64")   # Int64 para soportar nulos
df["mes"]    = df["iniciado"].dt.month.astype("Int64")
df["semana"] = df["iniciado"].dt.isocalendar().week.astype("Int64")
```

!!! important "Por qué Int64 y no int"
    `Int64` (con I mayúscula, tipo nullable de pandas) permite valores nulos sin convertirlos a `0.0`. Si se usara `.fillna(0).astype(int)`, las filas sin fecha (`NaT`) mostrarían `0` como año y mes en Power BI, contaminando los filtros.

## Funciones

::: paso2_db_server._clasificar_cliente

::: paso2_db_server._limpiar_cuit

::: paso2_db_server._duracion_segundos

::: paso2_db_server.leer_db_server

## Ejemplo de uso

```python
from pathlib import Path
from paso2_db_server import leer_db_server

df = leer_db_server(
    path_db=Path("data/inputs/DB_Server.xlsx"),
    path_tabla_cuits=Path("data/inputs/Tabla_Cuits.xlsx")
)

print(df.shape)
# (30881, 17)

print(df["tipo_cliente"].value_counts())
# VACIO     17220
# NOMBRE    13659
# CUIT          2

# Ver ejecuciones con CUIT resuelto
con_cuit = df[df["cuit_cliente"] != ""]
print(f"Con CUIT: {len(con_cuit)}")

# Ver distribución de duración
print(df[df["duracion_segundos"] > 0]["duracion_segundos"].describe())
# count    14512.0
# mean       330.7  (≈ 5.5 minutos promedio)
# max     278464.0  (≈ 77 horas — outlier)
```
