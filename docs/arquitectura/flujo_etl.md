# Flujo ETL

## Diagrama de pasos

```
┌─────────────────────────┐    ┌─────────────────────────────────────┐
│   DB_Server.xlsx        │    │   Relevamiento_BPS_v2.xlsm          │
│   30.881 ejecuciones    │    │   Sheet Clientes (47 filas)          │
│                         │    │   Sheet Uso de herramientas (517 f.) │
└───────────┬─────────────┘    └───────────────┬─────────────────────┘
            │                                  │
            ▼                                  ▼
    ┌───────────────┐                 ┌─────────────────┐
    │ clean_datos() │                 │  merge_datos()  │
    │               │                 │  Join por       │
    │ strip/replace │                 │  ID_Cliente     │
    │ espacios en   │                 │  Agrega Cuit a  │
    │ strings       │                 │  herramientas   │
    └───────┬───────┘                 └────────┬────────┘
            │                                  │
            │          Tabla_Cuits.xlsx         │
            │          (lookup nombre→CUIT)     │
            │                 │                 │
            ▼                 ▼                 ▼
    ┌─────────────────────────┐      ┌────────────────────────────┐
    │   paso2_db_server()     │      │  paso1_relevamiento()      │
    │                         │      │                            │
    │ 1. Normalizar variantes │      │ 1. Limpiar CUITs           │
    │    (CLIENTE_VARIANTES)  │      │ 2. Detectar CUITs dummy    │
    │ 2. Clasificar cliente:  │      │ 3. Deduplicar por CUIT     │
    │    CUIT/NOMBRE/VACIO    │      │ 4. Normalizar herramientas │
    │ 3. Lookup nombre→CUIT   │      │ 5. Convertir SI/NO → bool  │
    │ 4. Calcular duración    │      │                            │
    │ 5. Extraer año/mes      │      │ → dim_clientes (46 filas)  │
    │    (Int64, no 0)        │      │ → dim_relevamiento (517 f) │
    └───────────┬─────────────┘      └──────────────┬─────────────┘
                │                                   │
                └──────────────┬────────────────────┘
                               │
                               ▼
                    ┌─────────────────────────┐
                    │  paso3_fact_ejecuciones()│
                    │                         │
                    │ 1. Mapear proceso →      │
                    │    herramienta canónica  │
                    │    (PROCESO_A_HERRAM.)   │
                    │ 2. Flag en_relevamiento  │
                    │ 3. Normalizar estados    │
                    │    (9 variantes → 4)     │
                    │ 4. Join con dim_clientes │
                    │    por CUIT              │
                    │                         │
                    │ → fact_ejecuciones       │
                    │   (30.881 filas)         │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴──────────────────┐
                    │                               │
                    ▼                               ▼
        ┌─────────────────────┐       ┌─────────────────────────┐
        │ construir_esperado()│       │  paso4_diagnostico()    │
        │                     │       │                         │
        │ Cross join:         │       │ 7 hojas de análisis:    │
        │ debe_usar × periodos│       │ - resumen_general       │
        │ 108 × 22 = 2.376    │       │ - cobertura_tipo_cliente│
        │                     │       │ - procesos_sin_cliente  │
        │ → fact_esperado     │       │ - procesos_sin_relevam  │
        │   (2.376 filas)     │       │ - top_clientes          │
        └─────────────────────┘       │ - top_procesos          │
                                      │ - errores_por_proceso   │
                                      └─────────────────────────┘
```

---

## Orden de ejecución en main.py

| Paso | Función | Entrada | Salida |
|---|---|---|---|
| 1 | `leer_relevamiento()` | Relevamiento.xlsm | dim_clientes, dim_relevamiento |
| 2 | `leer_db_server()` | DB_Server.xlsx + Tabla_Cuits.xlsx | df_db (enriquecido) |
| 3 | `construir_fact_ejecuciones()` | df_db + dim_clientes | fact_ejecuciones |
| 4 | `construir_esperado()` | dim_relevamiento + fact | fact_esperado |
| 5 | Exportar CSVs | — | 5 archivos .csv |
| 6 | `generar_diagnostico()` | fact + dim_clientes + dim_relevamiento | diagnostico_matcheo.xlsx |

---

## Decisiones de diseño

### Por qué `Int64` y no `int` en año/mes/semana

Las columnas `anio`, `mes` y `semana` se calculan a partir de `iniciado`. Algunas filas en DB_Server tienen `iniciado` vacío (NaT). Con `int64` estándar, los nulos se convierten automáticamente a `0.0` float, lo que hace que Power BI muestre `0` como un año y un mes válidos en los segmentadores.

Con `Int64` (pandas nullable integer), los nulos quedan como `pd.NA` y Power BI los muestra en blanco, no como `0`.

### Por qué dim_relevamiento está suelta en Power BI

Si se conecta `dim_relevamiento` a `dim_clientes` y a `dim_herramientas`, Power BI detecta dos rutas para llegar a `dim_clientes` desde `fact_ejecuciones`:

- Ruta directa: `fact_ejecuciones → dim_clientes`
- Ruta indirecta: `fact_ejecuciones → dim_herramientas ← dim_relevamiento → dim_clientes`

Esto genera ambigüedad y Power BI lanza errores en columnas como `gerente_responsable`. La solución es dejar `dim_relevamiento` sin relaciones.

### Por qué el cross join en construir_esperado

El expected se calcula dinámicamente extrayendo los meses reales de `fact_ejecuciones`. Esto asegura que cuando el dataset crezca a nuevos meses, el expected se extienda automáticamente al re-ejecutar el pipeline, sin necesidad de configuración manual.
