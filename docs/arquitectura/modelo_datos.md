# Modelo de Datos

## Esquema estrella

El modelo sigue un esquema estrella donde `fact_ejecuciones` es la tabla central y las dimensiones cuelgan de ella.

```
                    dim_clientes
                    ─────────────
                    cuit (PK) ◄──────────── fact_ejecuciones[cuit_cliente]
                    nombre_cliente                    │
                    gerente_responsable               │
                    cuit_es_dummy                     │
                                                      │
                    dim_herramientas                  │
                    ─────────────────                 │
                    herramienta (PK) ◄────────────────┤ fact_ejecuciones[herramienta]
                    en_relevamiento                   │
                                                      │
                    Activos (Personal.xlsx)            │
                    ──────────────────────            │
                    username (PK) ◄───────────────────┘ fact_ejecuciones[username]


dim_relevamiento    → tabla suelta (sin relaciones)
fact_esperado       → tabla suelta (sin relaciones)
```

---

## Columnas de fact_ejecuciones

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | int | PK de la ejecución (viene de DB_Server) |
| `username` | str | Operador que ejecutó el bot |
| `proceso_original` | str | Nombre exacto del proceso en DB_Server |
| `herramienta` | str | Herramienta canónica (mapeada desde proceso) |
| `en_relevamiento` | bool | True si el proceso está en el Relevamiento |
| `estado` | str | Estado original de DB_Server |
| `estado_normalizado` | str | Estado canónico (Correcto/Erroneo/Con Observaciones/Correo no enviado) |
| `iniciado` | datetime | Timestamp de inicio |
| `finalizado` | datetime | Timestamp de fin |
| `duracion_segundos` | float | Duración en segundos (≥ 0) |
| `tipo_cliente` | str | CUIT / NOMBRE / VACIO |
| `cuit_cliente` | str | CUIT del cliente (vacío si no resuelto) |
| `nombre_cliente_canonico` | str | Nombre del cliente para display |
| `gerente_responsable` | str | Gerente (solo si tiene CUIT resuelto) |
| `items_count` | str | Cantidad de ítems procesados (nullable) |
| `observaciones` | str | Observaciones (nullable) |
| `anio` | Int64 | Año de iniciado (nullable — no 0) |
| `mes` | Int64 | Mes de iniciado (nullable — no 0) |
| `semana` | Int64 | Semana ISO de iniciado (nullable) |

---

## Columnas de dim_clientes

| Columna | Tipo | Descripción |
|---|---|---|
| `ID_Cliente` | int | Identificador interno del Relevamiento |
| `cuit` | str | CUIT limpio sin guiones — **PK** |
| `nombre_cliente` | str | Nombre del cliente |
| `gerente_responsable` | str | Gerente responsable |
| `cuit_es_dummy` | bool | True si el CUIT es placeholder pendiente |

---

## Columnas de dim_herramientas

| Columna | Tipo | Descripción |
|---|---|---|
| `herramienta` | str | Nombre canónico de la herramienta — **PK** |
| `en_relevamiento` | bool | True si está en el Relevamiento de clientes |

---

## Columnas de dim_relevamiento

| Columna | Tipo | Descripción |
|---|---|---|
| `ID_Cliente` | int | Identificador del cliente |
| `cuit` | str | CUIT del cliente |
| `nombre_cliente` | str | Nombre del cliente |
| `herramienta` | str | Herramienta asignada |
| `usa_herramienta` | bool | True si el cliente debe ejecutar esta herramienta |
| `gerente_responsable` | str | Gerente responsable |

---

## Columnas de fact_esperado

| Columna | Tipo | Descripción |
|---|---|---|
| `cuit` | str | CUIT del cliente |
| `nombre_cliente` | str | Nombre del cliente |
| `herramienta` | str | Herramienta esperada |
| `anio` | int | Año del período |
| `mes` | int | Mes del período |
| `ejecuciones_esperadas` | int | Siempre 1 — se espera 1 ejecución por mes |

---

## Relaciones en Power BI

| Desde (Muchos) | Hacia (Uno) | Cardinalidad | Cross-filter |
|---|---|---|---|
| `fact_ejecuciones[cuit_cliente]` | `dim_clientes[cuit]` | Many to One | Single |
| `fact_ejecuciones[herramienta]` | `dim_herramientas[herramienta]` | Many to One | Single |
| `fact_ejecuciones[username]` | `Activos[username]` | Many to One | Single |

`dim_relevamiento` y `fact_esperado` están sueltas, sin relaciones.

!!! warning "Cross-filter siempre Single"
    Usar `Both` en cualquiera de estas relaciones genera ambigüedad de rutas en Power BI y causa errores en columnas como `gerente_responsable`.
