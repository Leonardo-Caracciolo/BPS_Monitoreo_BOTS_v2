# Visión General

## Las tres fuentes de datos

### DB_Server.xlsx

Exportación de la tabla `monitoreo_bots` de la base de datos SQL. Contiene todas las ejecuciones de bots registradas desde abril 2024.

**Columnas originales:**

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | INT | Clave primaria de la ejecución |
| `username` | VARCHAR | Operador que ejecutó el bot |
| `proceso` | VARCHAR | Nombre del proceso/bot ejecutado |
| `estado` | VARCHAR | Resultado de la ejecución |
| `iniciado` | DATETIME | Timestamp de inicio |
| `finalizado` | DATETIME | Timestamp de fin |
| `cliente` | VARCHAR | Cliente — campo inconsistente (ver abajo) |
| `items_count` | INT | Cantidad de ítems procesados (nullable) |
| `observaciones` | TEXT | Observaciones (nullable) |

**El problema del campo `cliente`:**

Este campo fue incorporado al sistema después de que ya había datos cargados, y los operadores lo llenaron manualmente sin un formato establecido. El resultado es que tiene tres formatos distintos:

```
CUIT numérico     → "30717579360"           (0.7%  — 203 filas)
Nombre libre      → "FACEBOOK ARGENTINA S.R.L"  (44.2% — 13.659 filas)
Vacío             → null / "No definido"    (55.1% — 17.220 filas)
```

Además, el mismo cliente aparece escrito de múltiples formas. Por ejemplo ExxonMobil tiene tres variantes: `ExxonMobil`, `Exxonmobil`, `EXXONMOBIL`. El pipeline normaliza 61 variantes conocidas usando el diccionario `CLIENTE_VARIANTES` en `settings.py`.

**Evolución futura:** de ahora en adelante el campo `cliente` solo va a contener CUITs. El pipeline está preparado para este cambio.

---

### Relevamiento_BPS_Organizado_v2.xlsm

Archivo Excel con dos hojas que definen qué herramientas debería ejecutar cada cliente.

**Sheet Clientes (47 filas):**

| Columna | Descripción |
|---|---|
| `ID_Cliente` | Identificador interno |
| `Cliente` | Nombre del cliente |
| `Cuit` | CUIT con guiones (`"30-71757936-0"`) |
| `Gerente responsable` | Gerente a cargo del cliente |

**Sheet Uso de herramientas (517 filas = 47 clientes × 11 herramientas):**

| Columna | Descripción |
|---|---|
| `ID_Cliente` | FK hacia sheet Clientes |
| `Cliente` | Nombre del cliente |
| `Herramienta` | Nombre de la herramienta |
| `Usa Herramienta` | SI / NO — si el cliente debe ejecutar esta herramienta |
| `Gerente responsable` | Gerente del cliente |

**El problema:** la sheet `Uso de herramientas` no tiene la columna `Cuit`. Para poder cruzar con DB_Server por CUIT, hay que hacer un join entre las dos sheets por `ID_Cliente`. Esto lo hace `merge_datos.py`.

**25 clientes con CUIT dummy:** Algunos clientes tienen CUITs placeholder (`00000000001`, `00000000002`, etc.) que fueron cargados provisionalmente. Estos se detectan con el flag `cuit_es_dummy = True` en `dim_clientes`.

---

### Tabla_Cuits.xlsx

Tabla auxiliar con 9.249 clientes y sus CUITs oficiales (razón social + RFC/CUIT). Se usa como lookup para intentar resolver los nombres históricos de DB_Server a CUITs. Solo resuelve aproximadamente 20 de 476 nombres únicos históricos, porque la mayoría de los nombres en DB_Server son abreviaciones que no coinciden exactamente con las razones sociales.

---

## Las 5 tablas de salida

```
dim_clientes          → 1 fila por CUIT único (46 filas)
dim_herramientas      → 1 fila por herramienta (26 filas)
dim_relevamiento      → 1 fila por cliente × herramienta (517 filas)
fact_ejecuciones      → 1 fila por ejecución real (30.881 filas)
fact_esperado         → 1 fila por cliente × herramienta × mes (2.376 filas)
```
