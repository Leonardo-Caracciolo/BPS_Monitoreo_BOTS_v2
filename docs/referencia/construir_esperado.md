# construir_esperado.py

Genera `fact_esperado`: tabla de ejecuciones esperadas por cliente × herramienta × mes. Se usa en Power BI para construir la vista "Real vs Esperado".

## Responsabilidad

Generar una tabla que define cuántas veces debería haberse ejecutado cada bot para cada cliente en cada mes del período. Esta tabla se compara con `fact_ejecuciones` en Power BI para medir el cumplimiento.

## Lógica de negocio

La definición de "esperado" es:

> Un cliente debería ejecutar **1 vez por mes** cada herramienta donde `Usa Herramienta = True` en el Relevamiento.

## Algoritmo: cross join

La tabla se construye como un **producto cartesiano** entre:

- **debe_usar** (108 filas): combinaciones cliente × herramienta donde `usa_herramienta = True`
- **periodos** (22 filas): meses reales que aparecen en `fact_ejecuciones`

```
108 combinaciones × 22 meses = 2.376 filas
```

El cross join se implementa con una columna auxiliar `_key = 1` en ambos DataFrames:

```python
debe_usar["_key"] = 1
periodos["_key"]  = 1
fact_esperado = debe_usar.merge(periodos, on="_key").drop(columns=["_key"])
```

Esta es la técnica estándar en pandas para generar un producto cartesiano, ya que pandas no tiene un operador nativo de cross join.

## Por qué los períodos son dinámicos

Los meses se extraen de `fact_ejecuciones` en lugar de definirse estáticamente (ej: "desde Abr 2024 hasta Ene 2026"). Esto asegura que:

1. Al re-ejecutar el pipeline con nuevos datos, `fact_esperado` se extiende automáticamente a los nuevos meses.
2. No hay que actualizar manualmente ninguna constante cuando llegan datos de un mes nuevo.

## Uso en Power BI

`fact_esperado` se carga en Power BI como tabla suelta (sin relaciones). Las medidas DAX comparan las dos tablas:

```dax
Ejecuciones Esperadas = SUM(fact_esperado[ejecuciones_esperadas])

Cumplimiento % = DIVIDE([Corridas Exitosas], [Ejecuciones Esperadas], 0) * 100
```

Los filtros de la página actúan sobre cada tabla independientemente. Para que el cruce funcione correctamente en un gráfico, las dos tablas deben filtrar por las mismas columnas (`cuit`/`nombre_cliente`, `herramienta`, `anio`, `mes`).

## Función

::: construir_esperado.construir_esperado

## Ejemplo de uso

```python
from construir_esperado import construir_esperado

fact_esp = construir_esperado(dim_relevamiento, fact)

print(fact_esp.shape)
# (2376, 6)

print(fact_esp.columns.tolist())
# ['cuit', 'nombre_cliente', 'herramienta', 'anio', 'mes', 'ejecuciones_esperadas']

print(fact_esp["ejecuciones_esperadas"].unique())
# [1]

# Ver qué herramientas generan más esperados
print(fact_esp.groupby("herramienta")["ejecuciones_esperadas"].sum().sort_values(ascending=False))
# NFE Alert                        418  (19 clientes que deben usarlo × 22 meses)
# Padrones Impositivos - ComplyPro 506  (23 clientes × 22 meses)
# ...
```

## Extensión futura: frecuencia variable

En la versión actual, todas las herramientas tienen `ejecuciones_esperadas = 1`. Si en el futuro alguna herramienta debe ejecutarse más de una vez por mes, se puede agregar una columna `frecuencia_mensual` en el Relevamiento y usarla aquí:

```python
# Versión futura
fact_esperado["ejecuciones_esperadas"] = fact_esperado.apply(
    lambda row: frecuencia_map.get(row["herramienta"], 1),
    axis=1
)
```
