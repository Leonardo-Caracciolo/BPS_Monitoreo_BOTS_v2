# Archivos de entrada

Los tres archivos de entrada se colocan en `data/inputs/` y no deben modificarse manualmente. El pipeline los lee pero nunca los escribe.

---

## DB_Server.xlsx

**Ruta:** `data/inputs/DB_Server.xlsx`
**Sheet:** `Tabla Monitoreos`
**Filas:** 30.881
**Descripción:** Registro de todas las ejecuciones de bots. Es la fuente de verdad de lo que ocurrió realmente.

### Columnas

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | INT | Clave primaria de la ejecución. Autoincremental. |
| `username` | VARCHAR | Nombre de usuario del operador que ejecutó el bot. Ejemplo: `lmarinaro`, `amiriarte`. |
| `proceso` | VARCHAR | Nombre del proceso/bot ejecutado. 39 valores únicos en el dataset actual. |
| `estado` | VARCHAR | Estado de la ejecución. Tiene múltiples variantes inconsistentes (ver normalización en paso3). |
| `iniciado` | DATETIME | Timestamp de inicio de la ejecución. |
| `finalizado` | DATETIME | Timestamp de fin de la ejecución. |
| `cliente` | VARCHAR | **Campo problemático.** Puede tener tres formatos: CUIT numérico, nombre libre con errores, o estar vacío. |
| `items_count` | INT | Cantidad de ítems procesados. Alta tasa de nulos. |
| `observaciones` | TEXT | Observaciones de la ejecución. Alta tasa de nulos. |

### El campo `cliente` — problema central

El campo `cliente` tiene tres formatos distintos:

| Tipo | Cantidad | Porcentaje | Ejemplo |
|---|---|---|---|
| VACIO | 17.220 | 55.8% | `NULL`, `"No definido"` |
| NOMBRE | 13.659 | 44.2% | `"FACEBOOK ARGENTINA S.R.L"` |
| CUIT | 2 | 0.0% | `"30717579360"` |

**Por qué hay tantos vacíos:** la columna `cliente` no existía en los primeros meses del sistema. Se agregó después, por eso los datos históricos la tienen vacía.

**Por qué los nombres tienen errores:** los operadores la llenaban manualmente. El mismo cliente puede aparecer como `"TECHINT"`, `"Techint"`, o `"TECHINT S.A"`. El pipeline resuelve esto con el diccionario `CLIENTE_VARIANTES` en `settings.py`.

**De ahora en adelante:** todos los registros nuevos usarán CUIT numérico como valor del campo `cliente`, eliminando el problema de inconsistencia.

### Variantes detectadas (36 grupos)

Los 36 grupos de variantes más importantes que se normalizan:

| Variantes en DB_Server | → | Nombre canónico |
|---|---|---|
| `"TECHINT"`, `"Techint"` | → | `TECHINT` |
| `"ExxonMobil"`, `"Exxonmobil"`, `"EXXONMOBIL"` | → | `EXXONMOBIL` |
| `"TENARIS"`, `"Tenaris"` | → | `TENARIS` |
| `"SPOTIFY ARGENTINA S.A"`, `"SPOTIFY ARGENTINA S.A."`, `"Spotify"` | → | `SPOTIFY` |
| `"J&J ARGENTINA S.A"`, `"J&J"` | → | `J&J` |
| `"ULTRAGENYX ARGENTINA S.R.L"`, `"Ultragenyx"` | → | `ULTRAGENYX` |

Ver lista completa en `settings.py` → `CLIENTE_VARIANTES`.

---

## Relevamiento_BPS_Organizado_-_v2.xlsm

**Ruta:** `data/inputs/Relevamiento_BPS_Organizado_-_v2.xlsm`
**Sheets:** `Clientes` y `Uso de herramientas`
**Descripción:** Define qué clientes están activos y qué herramientas debería ejecutar cada uno.

### Sheet: Clientes

**Filas:** 47

| Columna | Tipo | Descripción |
|---|---|---|
| `ID_Cliente` | INT | Identificador interno. Clave para el join con "Uso de herramientas". |
| `Cliente` | VARCHAR | Nombre del cliente. |
| `Cuit` | VARCHAR | CUIT con guiones (ej: `"30-71757936-0"`). El pipeline los limpia. |
| `Gerente responsable` | VARCHAR | Gerente a cargo. Se usa como filtro de línea de servicio en Power BI. |

!!! warning "CUITs pendientes"
    25 de los 47 clientes tienen CUITs placeholder (`00000000001`, `00000000002`, etc.). Estos clientes no pueden relacionarse con las ejecuciones de DB_Server hasta que se actualicen con los CUITs reales. Se identifican con el flag `cuit_es_dummy = True` en `dim_clientes.csv`.

!!! warning "Spotify duplicado"
    Spotify aparece con dos `ID_Cliente` distintos (1 y 4) pero el mismo CUIT `30717579360`. El pipeline lo resuelve con `drop_duplicates(subset=["cuit"])` en `paso1_relevamiento.py`.

### Sheet: Uso de herramientas

**Filas:** 517 (47 clientes × 11 herramientas)

| Columna | Tipo | Descripción |
|---|---|---|
| `ID_Cliente` | INT | Clave foránea hacia la sheet Clientes. |
| `Cliente` | VARCHAR | Nombre del cliente (denormalizado). |
| `Herramienta` | VARCHAR | Nombre de la herramienta. 11 valores únicos. |
| `Usa Herramienta` | VARCHAR | `"SI"` o `"NO"`. El pipeline lo convierte a `bool`. |
| `Gerente responsable` | VARCHAR | Gerente del cliente. |

!!! note "Columna Cuit faltante"
    Esta sheet no tiene la columna `Cuit` originalmente. `merge_datos.py` la agrega mediante un `left join` con la sheet Clientes usando `ID_Cliente` como clave.

### Herramientas relevadas (11)

| Herramienta |
|---|
| NFE Alert |
| Acrobat Tools |
| Calendarios Impositivos |
| Padrones Impositivos - ComplyPro |
| Control de correlatividad - ComplyPro |
| Control de duplicados - ComplyPro |
| Descarga de deducciones - ComplyPro |
| Identificacion de registros faltantes - ComplyPro |
| Conciliacion de Deducciones - ComplyPro |
| Sumarizacion y control por totales - ComplyPro |
| Permisos de Embarque MOA Reingenieria |

---

## Tabla_Cuits.xlsx

**Ruta:** `data/inputs/Tabla_Cuits.xlsx`
**Filas:** 9.249
**Descripción:** Tabla de lookup para intentar resolver nombres históricos de clientes a CUITs.

### Columnas

| Columna | Tipo | Descripción |
|---|---|---|
| `no_cliente` | INT | Identificador interno del cliente. |
| `razon_social` | VARCHAR | Razón social oficial del cliente. |
| `RFC` | VARCHAR | Campo que contiene el CUIT (nombre heredado de un sistema anterior). Tiene 1.880 nulos. |

### Efectividad del lookup

De los 476 nombres únicos en DB_Server de tipo NOMBRE, solo **20** se resuelven a CUIT usando esta tabla. La razón es que los nombres en DB_Server suelen ser abreviaciones o variantes informales que no coinciden exactamente con las razones sociales de Tabla_Cuits.

Por ejemplo, `"FACEBOOK ARGENTINA S.R.L"` en DB_Server debería coincidir con alguna entrada de Tabla_Cuits, pero puede que esté como `"FACEBOOK ARGENTINA S.R.L."` (con punto final) o completamente diferente.
