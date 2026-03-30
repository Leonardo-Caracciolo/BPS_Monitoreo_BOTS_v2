# merge_datos.py

Función base de lectura del Relevamiento BPS y join entre sus dos sheets. Fue escrita originalmente por el usuario del proyecto.

## Responsabilidad

Esta función tiene **una sola responsabilidad**: leer las dos sheets del Relevamiento y agregar la columna `Cuit` a la sheet "Uso de herramientas" mediante un join. No aplica lógica de negocio adicional.

## Por qué existe el join

El Relevamiento tiene dos sheets que deben unirse para poder usar el CUIT como clave de cruce:

```
Sheet "Clientes"              Sheet "Uso de herramientas"
┌─────────────┬───────┐      ┌─────────────┬─────────────────┬──────────────────┐
│ ID_Cliente  │ Cuit  │      │ ID_Cliente  │ Herramienta     │ Usa Herramienta  │
├─────────────┼───────┤      ├─────────────┼─────────────────┼──────────────────┤
│ 1           │ 307.. │ ←──→ │ 1           │ NFE Alert       │ SI               │
│ 2           │ 307.. │      │ 1           │ Acrobat Tools   │ SI               │
│ ...         │ ...   │      │ 2           │ NFE Alert       │ NO               │
└─────────────┴───────┘      └─────────────┴─────────────────┴──────────────────┘
                                            ↑
                               Cuit NO EXISTE aquí originalmente
```

Después del join, "Uso de herramientas" tiene la columna `Cuit` y puede usarse para cruzar con DB_Server.

## Función

::: merge_datos.merge_datos

## Ejemplo de uso

```python
from merge_datos import merge_datos

df_clientes, df_herramientas = merge_datos(
    "data/inputs/Relevamiento_BPS_Organizado_-_v2.xlsm"
)

print(df_clientes.shape)
# (47, 4)

print(df_clientes.columns.tolist())
# ['ID_Cliente', 'Cliente', 'Cuit', 'Gerente responsable']

print(df_herramientas.shape)
# (517, 6)

print(df_herramientas.columns.tolist())
# ['ID_Cliente', 'Cliente', 'Herramienta', 'Usa Herramienta',
#  'Gerente responsable', 'Cuit']
```

## Cómo se usa en el pipeline

`merge_datos()` es llamada al inicio de `leer_relevamiento()` en `paso1_relevamiento.py`:

```python
from merge_datos import merge_datos

def leer_relevamiento(path):
    # merge_datos hace la lectura y el join
    df_clientes, df_herramientas = merge_datos(str(path))
    
    # Después de esto, paso1 aplica las transformaciones de negocio
    # (limpiar CUITs, detectar dummies, deduplicar, etc.)
    # ...
```
