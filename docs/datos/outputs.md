# Archivos de salida

El pipeline genera 6 archivos en `data/outputs/` en cada ejecución. Los CSVs se sobreescriben completamente; el Excel de diagnóstico también.

Todos los CSVs usan encoding `UTF-8-sig` (UTF-8 con BOM), que es el encoding que Power BI requiere para leer correctamente caracteres especiales como `ñ`, `á`, `é`, etc.

---

## dim_clientes.csv

**Filas:** 46
**Descripción:** Catálogo de clientes activos del Relevamiento. Una fila por CUIT único. Es el lado "Uno" de la relación con `fact_ejecuciones` en Power BI.

| Columna | Tipo | Descripción |
|---|---|---|
| `ID_Cliente` | Int64 | Identificador interno del Relevamiento. |
| `cuit` | text | CUIT limpio sin guiones. **Clave primaria** para relaciones en Power BI. |
| `nombre_cliente` | text | Nombre del cliente. |
| `gerente_responsable` | text | Gerente a cargo. Usado como filtro "Línea de servicio" en Power BI. |
| `cuit_es_dummy` | logical | `True` si el CUIT es un placeholder pendiente de actualizar. |

!!! note "Por qué 46 y no 47"
    Spotify aparece dos veces en el Relevamiento con el mismo CUIT. El `drop_duplicates` del pipeline elimina la fila duplicada, dejando 46 clientes únicos.

---

## dim_herramientas.csv

**Filas:** 26
**Descripción:** Catálogo completo de herramientas y procesos. Incluye tanto las 11 herramientas del Relevamiento como los 15 procesos externos que aparecen en DB_Server pero no en el Relevamiento.

| Columna | Tipo | Descripción |
|---|---|---|
| `herramienta` | text | Nombre canónico de la herramienta. **Clave primaria.** |
| `en_relevamiento` | logical | `True` si la herramienta está en el Relevamiento BPS. |

---

## dim_relevamiento.csv

**Filas:** 517
**Descripción:** Cruce de cliente × herramienta con el flag de si el cliente debe usar esa herramienta. Se usa en Power BI como tabla suelta (sin relaciones) para mostrar qué se espera de cada cliente.

| Columna | Tipo | Descripción |
|---|---|---|
| `ID_Cliente` | Int64 | ID del cliente. |
| `cuit` | text | CUIT del cliente. |
| `nombre_cliente` | text | Nombre del cliente. |
| `herramienta` | text | Herramienta asignada. |
| `usa_herramienta` | logical | `True` si el cliente debe ejecutar esta herramienta. |
| `gerente_responsable` | text | Gerente del cliente. |

---

## fact_ejecuciones.csv

**Filas:** 30.881
**Descripción:** Tabla de hechos principal. Una fila por ejecución de bot registrada en DB_Server. Es la tabla central del modelo de Power BI.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | Int64 | Clave primaria de la ejecución (viene de DB_Server). |
| `username` | text | Operador que ejecutó el bot. |
| `proceso_original` | text | Nombre del proceso tal como está en DB_Server. |
| `herramienta` | text | Herramienta canónica mapeada desde `proceso_original`. FK → `dim_herramientas`. |
| `en_relevamiento` | logical | `True` si el proceso corresponde a una herramienta del Relevamiento. |
| `estado` | text | Estado original de DB_Server (sin normalizar). |
| `estado_normalizado` | text | Estado canónico: `Correcto`, `Erroneo`, `Con Observaciones`, `Correo no enviado`. |
| `iniciado` | datetime | Timestamp de inicio. |
| `finalizado` | datetime | Timestamp de fin. |
| `duracion_segundos` | number | Duración de la ejecución en segundos (≥ 0). |
| `tipo_cliente` | text | `CUIT`, `NOMBRE`, o `VACIO`. |
| `cuit_cliente` | text | CUIT del cliente. FK → `dim_clientes`. Vacío si tipo es VACIO o NOMBRE sin resolver. |
| `nombre_cliente_canonico` | text | Nombre del cliente para display. Viene de `dim_clientes` si tiene CUIT, o del texto histórico si no. |
| `gerente_responsable` | text | Gerente del cliente. Solo disponible para clientes con CUIT resuelto. |
| `items_count` | text | Cantidad de ítems procesados. Alta tasa de nulos. |
| `observaciones` | text | Observaciones. Alta tasa de nulos. |
| `anio` | Int64 | Año de `iniciado`. `NA` si la fecha es nula. |
| `mes` | Int64 | Mes de `iniciado`. `NA` si la fecha es nula. |
| `semana` | Int64 | Semana ISO de `iniciado`. `NA` si la fecha es nula. |

!!! tip "Por qué anio/mes son Int64 y no int"
    Algunas filas no tienen fecha en `iniciado`. Si se usara `int` normal, los nulos se convertirían a `0`, y Power BI mostraría `0` como valor de año y mes. Con `Int64` (tipo nullable de pandas) los nulos se exportan como vacíos en el CSV y Power BI los trata como blancos.

---

## fact_esperado.csv

**Filas:** 2.376
**Descripción:** Tabla de ejecuciones esperadas. Una fila por combinación (cliente, herramienta, mes) donde el cliente debería haber ejecutado ese bot. Se usa en Power BI junto con `fact_ejecuciones` para la vista Real vs Esperado.

| Columna | Tipo | Descripción |
|---|---|---|
| `cuit` | text | CUIT del cliente. |
| `nombre_cliente` | text | Nombre del cliente. |
| `herramienta` | text | Herramienta que se espera ejecutar. |
| `anio` | int | Año del período esperado. |
| `mes` | int | Mes del período esperado. |
| `ejecuciones_esperadas` | int | Siempre `1`. Se espera 1 ejecución por cliente × herramienta × mes. |

El cálculo es: 108 combinaciones cliente × herramienta (donde `usa_herramienta = True`) × 22 meses del período real = **2.376 filas**.

---

## diagnostico_matcheo.xlsx

**Descripción:** Reporte de calidad de datos. No se usa en Power BI. Sirve para que el equipo monitoree la calidad del pipeline después de cada ejecución.

| Sheet | Descripción |
|---|---|
| `resumen_general` | KPIs: totales, % con CUIT, % sin cliente, estados |
| `cobertura_tipo_cliente` | Distribución CUIT/NOMBRE/VACIO con porcentajes |
| `procesos_sin_cliente` | Procesos con más registros sin cliente asignado |
| `procesos_sin_relevam` | Procesos que no están en el Relevamiento |
| `top_clientes` | Top 50 clientes por ejecuciones con tasa de éxito |
| `top_procesos` | Todos los procesos con conteos y tasa de éxito |
| `errores_por_proceso` | Combinaciones proceso × cliente con más errores |
