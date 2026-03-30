# Relaciones entre tablas

## Las 3 relaciones a crear

En `Vista → Modelo`, crear estas relaciones arrastrando la columna de origen sobre la columna de destino:

| # | Desde (Muchos ∞) | → | Hacia (Uno 1) | Cardinalidad | Cross-filter |
|---|---|---|---|---|---|
| 1 | `fact_ejecuciones[cuit_cliente]` | → | `dim_clientes[cuit]` | Many to One | **Single** |
| 2 | `fact_ejecuciones[herramienta]` | → | `dim_herramientas[herramienta]` | Many to One | **Single** |
| 3 | `fact_ejecuciones[username]` | → | `Activos[username]` | Many to One | **Single** |

`dim_relevamiento` y `fact_esperado` quedan **sueltas, sin ninguna relación**.

---

## Por qué Single y no Both

Con `Both`, Power BI puede propagar filtros en ambas direcciones. Esto genera ambigüedad cuando hay múltiples rutas para llegar a una tabla:

```
# Con Both en relación 1:
# Power BI detecta DOS rutas para llegar a dim_clientes:
#   Ruta A: fact_ejecuciones → dim_clientes  (directa)
#   Ruta B: fact_ejecuciones → dim_herramientas ← ... → dim_clientes  (indirecta)
# → Error en columna "gerente_responsable"
```

Con `Single`, los filtros solo viajan de la dimensión hacia el hecho, que es el comportamiento correcto para un esquema estrella.

---

## Por qué dim_relevamiento está suelta

Si se conecta `dim_relevamiento[cuit]` a `dim_clientes[cuit]`, Power BI detecta ambigüedad de rutas y lanza errores. `dim_relevamiento` se usa en visuales directamente sin necesidad de estar relacionada con las otras tablas.

---

## Errores comunes

**"Column contains duplicate values"**
→ La columna del lado "Uno" tiene duplicados. Verificar que `dim_clientes[cuit]` no tenga CUITs repetidos. Regenerar los CSVs ejecutando `python main.py`.

**"There are ambiguous paths"**
→ Hay relaciones que crean rutas ambiguas. Eliminar las relaciones de `dim_relevamiento` si las hubiera creado.

**"This field cannot be used here"**
→ Se está intentando poner una medida donde Power BI pide un campo (Eje X, Leyenda) o viceversa.
