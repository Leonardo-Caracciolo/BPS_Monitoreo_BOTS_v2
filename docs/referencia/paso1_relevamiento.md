# paso1_relevamiento.py

Construye `dim_clientes` y `dim_relevamiento` a partir del Relevamiento BPS. Usa `merge_datos()` como base y aplica las transformaciones necesarias para que las tablas sean válidas en el modelo de Power BI.

## Responsabilidad

Tomar el output crudo de `merge_datos()` y producir dos tablas limpias y válidas para el modelo estrella de Power BI:

1. `dim_clientes`: catálogo de clientes con CUIT único como clave primaria.
2. `dim_relevamiento`: cruce cliente × herramienta con flag de uso.

## Transformaciones aplicadas

### Sobre dim_clientes

**1. Limpieza de CUIT** — `_limpiar_cuit()`

Los CUITs en el Excel tienen guiones: `"30-71757936-0"`. Power BI necesita el CUIT sin guiones para hacer join con `fact_ejecuciones[cuit_cliente]` que tampoco los tiene.

```
"30-71757936-0"  →  "30717579360"
"30 71757936 0"  →  "30717579360"  (también quita espacios)
NULL             →  ""
```

**2. Detección de CUITs dummy** — `_es_cuit_dummy()`

25 de los 47 clientes tienen CUITs placeholder (`"00000000001"`, `"00000000002"`, etc.) porque aún no se cargaron los CUITs reales. La función los detecta verificando que el valor sea numérico y menor a 100.

```python
_es_cuit_dummy("00000000001")  # → True
_es_cuit_dummy("30717579360")  # → False
```

**3. Deduplicación por ID_Cliente**

Elimina filas con el mismo `ID_Cliente`. No debería haber duplicados, pero se aplica defensivamente.

**4. Deduplicación por CUIT** ← *crítico para Power BI*

Elimina CUITs duplicados manteniendo la primera ocurrencia. Esto resuelve el caso de Spotify que aparece dos veces (ID 1 y ID 4) con el mismo CUIT `30717579360`.

Sin esta deduplicación, Power BI rechaza la relación Many-to-One con el error:
```
"Column 'cuit' in Table 'dim_clientes' contains a duplicate value
and this is not allowed for columns on the one side of a many-to-one
relationship"
```

### Sobre dim_relevamiento

**5. Normalización de herramienta**

Colapsa espacios dobles en nombres de herramienta. Por ejemplo, `"Acrobat Tools  "` tiene dos espacios al final en el Excel original. La normalización lo deja como `"Acrobat Tools"`.

**6. Conversión Usa Herramienta → bool**

Convierte `"SI"` → `True`, `"NO"` → `False`, nulos → `False`.

**7. Limpieza del CUIT en herramientas**

El CUIT que llegó por el join de `merge_datos()` también tiene guiones. Se aplica la misma limpieza que en dim_clientes.

## Funciones

::: paso1_relevamiento._limpiar_cuit

::: paso1_relevamiento._es_cuit_dummy

::: paso1_relevamiento.leer_relevamiento

## Ejemplo de uso

```python
from pathlib import Path
from paso1_relevamiento import leer_relevamiento

dim_clientes, dim_relevamiento = leer_relevamiento(
    Path("data/inputs/Relevamiento_BPS_Organizado_-_v2.xlsm")
)

print(dim_clientes.shape)
# (46, 5)  ← 46 porque Spotify duplicado fue eliminado

print(dim_clientes.dtypes)
# ID_Cliente             int64
# cuit                  object  ← texto, no número
# nombre_cliente        object
# gerente_responsable   object
# cuit_es_dummy           bool

# Ver clientes con CUIT pendiente
print(dim_clientes[dim_clientes["cuit_es_dummy"] == True]["nombre_cliente"].tolist())
# ['INDUSTRIAS LEAR DE ARGENTINA S.R.L.', 'AUTH0', 'adidas Argentina S.A.', ...]
# 25 clientes en total

print(dim_relevamiento.shape)
# (517, 6)

# Ver herramientas que cada cliente debe usar
debe_usar = dim_relevamiento[dim_relevamiento["usa_herramienta"] == True]
print(debe_usar.groupby("herramienta").size().sort_values(ascending=False))
```
