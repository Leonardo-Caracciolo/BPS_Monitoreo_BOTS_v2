# BPS Monitoreo Bots

Pipeline ETL que consolida las ejecuciones reales de bots (`DB_Server.xlsx`) con el relevamiento de clientes y herramientas (`Relevamiento BPS.xlsm`), y produce tablas limpias para un dashboard en Power BI.

---

## Estructura del proyecto

```
BPS_Monitoreo_Bots/
│
├── main.py                    ← Entry point. Ejecutar esto.
├── settings.py                ← Paths, constantes y diccionarios de mapeo
│
├── clean_datos.py             ← Lee y limpia DB_Server.xlsx (función base)
├── merge_datos.py             ← Lee el Relevamiento y agrega CUIT a herramientas (función base)
├── paso1_relevamiento.py      ← Construye dim_clientes y dim_relevamiento
├── paso2_db_server.py         ← Clasifica y enriquece las ejecuciones
├── paso3_fact_ejecuciones.py  ← Construye la tabla de hechos principal
├── paso4_diagnostico.py       ← Genera reporte de calidad de datos
├── construir_esperado.py      ← Genera fact_esperado (Real vs Esperado)
│
├── data/
│   ├── inputs/                ← Archivos fuente (NO modificar)
│   │   ├── DB_Server.xlsx
│   │   ├── Relevamiento_BPS_Organizado_-_v2.xlsm
│   │   └── Tabla_Cuits.xlsx
│   └── outputs/               ← Tablas para Power BI (se regeneran con main.py)
│       ├── dim_clientes.csv
│       ├── dim_herramientas.csv
│       ├── dim_relevamiento.csv
│       ├── fact_ejecuciones.csv
│       ├── fact_esperado.csv
│       └── diagnostico_matcheo.xlsx
│
└── docs/                      ← Documentación detallada (MkDocs)
```

---

## Requisitos e instalación

```bash
pip install pandas openpyxl
```

## Cómo ejecutar

```bash
python main.py
```

Esto regenera los 6 archivos de `data/outputs/` en cada ejecución.

---

## Archivos de entrada

| Archivo | Descripción |
|---|---|
| `DB_Server.xlsx` | Exportación de la tabla `monitoreo_bots`. Contiene todas las ejecuciones reales de bots |
| `Relevamiento_BPS_Organizado_-_v2.xlsm` | Clientes activos y herramientas que deberían ejecutar |
| `Tabla_Cuits.xlsx` | Tabla auxiliar de 9.249 empresas para resolver nombres históricos a CUIT |

## Archivos de salida

| Archivo | Filas | Descripción |
|---|---|---|
| `dim_clientes.csv` | 46 | Un registro por cliente único (CUIT como PK) |
| `dim_herramientas.csv` | 26 | Catálogo de herramientas con flag `en_relevamiento` |
| `dim_relevamiento.csv` | 517 | Cruce cliente × herramienta del Relevamiento |
| `fact_ejecuciones.csv` | 30.881 | Tabla de hechos con todas las ejecuciones reales |
| `fact_esperado.csv` | 2.376 | Ejecuciones esperadas por cliente × herramienta × mes |
| `diagnostico_matcheo.xlsx` | — | 7 hojas de calidad de datos para revisión interna |

---

## Descripción detallada de cada archivo

### `settings.py`

Configuración centralizada. **Es el único lugar donde hay que tocar cuando cambia algo de estructura.** Nunca hay paths hardcodeados en los otros archivos.

Contiene:

- **Paths** de entrada y salida usando `pathlib.Path`
- **`CLIENTE_VARIANTES`**: diccionario de 61 entradas que normaliza variantes del nombre de un cliente al nombre canónico. Ejemplo: `"SPOTIFY ARGENTINA S.A"`, `"SPOTIFY ARGENTINA S.A."` y `"Spotify"` → `"Spotify"`. Necesario porque los operadores escribían el cliente en el campo libre de DB_Server de múltiples formas.
- **`PROCESO_A_HERRAMIENTA`**: diccionario que traduce el nombre técnico del proceso en DB_Server al nombre de herramienta del Relevamiento. Ejemplo: `"GUI: Control Correlatividad"` → `"Control de correlatividad - ComplyPro"`.
- **`PROCESOS_SIN_HERRAMIENTA`**: set de procesos que son internos y no tienen herramienta en el Relevamiento (WP - Ganancias, Tablas Ratio Report, etc.). Se usan para el flag `en_relevamiento = False`.

---

### `clean_datos.py`



Lee `DB_Server.xlsx` (sheet `Tabla Monitoreos`) y aplica limpieza de strings a todas las columnas de texto: `str.strip()` elimina espacios al inicio y final, `str.replace(r"\s+", " ")` colapsa espacios dobles.

**Devuelve:** DataFrame con 30.881 filas y 9 columnas originales (`id`, `username`, `proceso`, `estado`, `iniciado`, `finalizado`, `cliente`, `items_count`, `observaciones`).

---

### `merge_datos.py`

Lee el Relevamiento BPS (`.xlsm`) y soluciona el problema de que la sheet `Uso de herramientas` no tiene la columna `Cuit`. Hace un `left join` entre las dos sheets por `ID_Cliente` para agregar el CUIT.

**Devuelve:** `(df_clientes, df_herramientas)` — dos DataFrames, el segundo ya con la columna `Cuit`.

---

### `paso1_relevamiento.py`

Usa `merge_datos()` como base y agrega las transformaciones necesarias para el modelo de Power BI:

1. **Limpieza de CUITs**: quita guiones y espacios (`"30-71757936-0"` → `"30717579360"`)
2. **Detección de CUITs dummy**: 25 clientes tienen CUITs placeholder (`000000000X`) pendientes de actualizar — se marcan con `cuit_es_dummy = True`
3. **Deduplicación por CUIT**: Power BI requiere que la columna `cuit` en `dim_clientes` sea única (lado "Uno" de la relación). Spotify aparecía duplicado con el mismo CUIT — se resuelve con `drop_duplicates(subset=["cuit"], keep="first")`.
4. **Normalización de herramientas**: colapsa espacios dobles en nombres de herramienta
5. **Conversión `Usa Herramienta` → bool**: `"SI"` → `True`, `"NO"` → `False`

**Devuelve:** `(dim_clientes, dim_relevamiento)`
- `dim_clientes`: 46 filas, 1 por cliente con CUIT único
- `dim_relevamiento`: 517 filas, 1 por cada combinación cliente × herramienta

---

### `paso2_db_server.py`

Usa `clean_datos()` como base y resuelve el problema central del proyecto: el campo `cliente` en DB_Server tiene tres formatos distintos.

**El problema del campo `cliente`:**

| Tipo | Ejemplo | Cantidad |
|---|---|---|
| CUIT numérico | `"30717579360"` | 203 filas (0.7%) |
| Nombre libre con errores | `"SPOTIFY ARGENTINA S.A"` | 13.659 filas (44.2%) |
| Vacío | `null` / `"No definido"` | 17.220 filas (55.8%) |

**Transformaciones aplicadas:**
1. Aplica `CLIENTE_VARIANTES` para normalizar variantes de nombre
2. Clasifica cada fila en `CUIT`, `NOMBRE` o `VACIO` (columna `tipo_cliente`)
3. Para tipo `CUIT`: usa directamente como clave
4. Para tipo `NOMBRE`: intenta resolver a CUIT buscando en `Tabla_Cuits.xlsx`
5. Calcula `duracion_segundos` = `finalizado - iniciado` (clippeado a ≥ 0)
6. Extrae `anio`, `mes`, `semana` de `iniciado` en tipo `Int64` (nullable, para que los nulos no aparezcan como `0` en Power BI)

**Devuelve:** DataFrame de 30.881 filas con columnas enriquecidas.

---

### `paso3_fact_ejecuciones.py`

Construye la tabla de hechos principal uniendo lo de DB_Server con las dimensiones del Relevamiento.

**Transformaciones aplicadas:**
1. **Mapeo proceso → herramienta**: aplica `PROCESO_A_HERRAMIENTA` para traducir nombres técnicos a herramientas canónicas (muchos a uno)
2. **Flag `en_relevamiento`**: `True` si el proceso corresponde a una herramienta del Relevamiento, `False` si es un proceso interno
3. **Normalización de estados**: consolida 9+ variantes en 4 valores canónicos:
   - `"Correcto"` (incluye "Finalizado", "Correcto")
   - `"Erroneo"` (incluye "Proceso terminado con errores", "Proceso finalizado con errores", "Erróneo")
   - `"Con Observaciones"` (incluye "Finalizado con observaciones", "Proceso terminado con observaciones")
   - `"Correo no enviado"`
4. **Join con `dim_clientes`**: agrega `nombre_cliente_canonico` y `gerente_responsable` por CUIT

**Devuelve:** `fact_ejecuciones` con 30.881 filas y 19 columnas.

---

### `construir_esperado.py`

Genera la tabla `fact_esperado` para el análisis Real vs Esperado.

**Lógica:** un cliente debería ejecutar **1 vez por mes** cada herramienta donde `Usa Herramienta = SI` en el Relevamiento.

**Algoritmo (cross join):**
- Filtra las combinaciones cliente × herramienta donde `usa_herramienta = True` → **108 combinaciones**
- Extrae los meses reales del período de datos de `fact_ejecuciones` → **22 meses**
- Producto cartesiano: 108 × 22 = **2.376 filas**
- Cada fila tiene `ejecuciones_esperadas = 1`

El período se extrae dinámicamente de `fact_ejecuciones`, por lo que se extiende automáticamente cuando hay datos nuevos.

**Devuelve:** `fact_esperado` con columnas `cuit`, `nombre_cliente`, `herramienta`, `anio`, `mes`, `ejecuciones_esperadas`.

---

### `paso4_diagnostico.py`

Genera `diagnostico_matcheo.xlsx` con 7 hojas de análisis de calidad. **No produce tablas para Power BI** — es para uso interno del equipo.

| Hoja | Contenido |
|---|---|
| `resumen_general` | KPIs del pipeline: total ejecuciones, % con CUIT, % exitosas, etc. |
| `cobertura_tipo_cliente` | Distribución CUIT / NOMBRE / VACIO con porcentajes |
| `procesos_sin_cliente` | Procesos con más registros sin cliente asignado |
| `procesos_sin_relevam` | Procesos que no están en el Relevamiento |
| `top_clientes` | Top 50 clientes por volumen con tasa de éxito |
| `top_procesos` | Todos los procesos con conteos y tasa de éxito |
| `errores_por_proceso` | Errores agrupados por proceso y cliente |

---

### `main.py`

Entry point que orquesta todo en orden:

```
PASO 0: (opcional) leer_personal()    ← Linea/Sublinea por operador
PASO 1: leer_relevamiento()            ← dim_clientes + dim_relevamiento
PASO 2: leer_db_server()              ← df_db clasificado
PASO 3: construir_fact_ejecuciones()  ← fact_ejecuciones
PASO 4: construir_esperado()          ← fact_esperado
PASO 5: Exportar 5 CSVs
PASO 6: generar_diagnostico()         ← diagnostico_matcheo.xlsx
```

---

## El problema de matching de clientes — Situación actual y mejora propuesta

### Situación actual

El pipeline usa un diccionario estático `CLIENTE_VARIANTES` en `settings.py` con 61 entradas manuales. Funciona, pero tiene dos problemas:

1. **No escala**: cada vez que aparece una variante nueva hay que agregarla a mano
2. **Nombre canónico distinto al del Relevamiento**: el diccionario mapea a mayúsculas (`"SPOTIFY"`) pero el Relevamiento tiene `"Spotify"` — esto rompe el cruce Real vs Esperado en Power BI

### Mejora propuesta: matching dinámico por n-gramas de palabras

En lugar del diccionario estático, se puede implementar una función que matchee nombres por las primeras N palabras de forma dinámica. Esto no requiere ningún cambio en los archivos de Power BI.

**Cómo funciona:**

```python
# paso2_db_server.py — función nueva

def _normalizar_por_palabras(nombre: str, catalogo: dict[str, str], n_palabras: int = 1) -> str:
    """
    Busca el nombre en el catálogo comparando las primeras N palabras.
    
    Parámetros
    ----------
    nombre     : str  — nombre a normalizar (ej: "SPOTIFY ARGENTINA S.A")
    catalogo   : dict — {nombre_canonico: nombre_canonico} del Relevamiento
    n_palabras : int  — cuántas palabras usar para el match (default: 1)
    
    Retorna el nombre canónico si matchea, o el nombre original si no.
    
    Ejemplos con n_palabras=1:
        "SPOTIFY ARGENTINA S.A" → match con "Spotify" (primera palabra: "spotify" == "spotify")
        "Exxonmobil S.A."       → match con "ExxonMobil"
        
    Ejemplos con n_palabras=2:
        "J&J ARGENTINA"         → match con "J&J" si el catálogo tiene "J&J"
        "FORD ARGENTINA"        → match con "Ford"
    """
    if not nombre or pd.isna(nombre):
        return nombre
    
    palabras_input = nombre.lower().split()[:n_palabras]
    prefijo_input = " ".join(palabras_input)
    
    for nombre_canonico in catalogo:
        palabras_canonico = nombre_canonico.lower().split()[:n_palabras]
        prefijo_canonico = " ".join(palabras_canonico)
        if prefijo_input == prefijo_canonico:
            return nombre_canonico   # retorna el nombre exacto del Relevamiento
    
    return nombre  # no matcheó, retorna el original


def _construir_catalogo_relevamiento(dim_clientes: pd.DataFrame) -> dict[str, str]:
    """
    Construye el catálogo desde dim_clientes para usar como referencia de nombres canónicos.
    Retorna {nombre_cliente: nombre_cliente} — la clave y el valor son el mismo nombre canónico.
    """
    nombres = dim_clientes['nombre_cliente'].dropna().unique()
    return {n: n for n in nombres}
```

**Cómo se usaría en el pipeline:**

```python
# En paso2_db_server.py, reemplazar la línea de CLIENTE_VARIANTES:

# Antes (estático):
df["cliente_norm"] = df["cliente"].apply(
    lambda v: CLIENTE_VARIANTES.get(str(v).strip(), str(v).strip())
    if not pd.isna(v) else v
)

# Después (dinámico, n_palabras configurable):
catalogo = _construir_catalogo_relevamiento(dim_clientes)
N_PALABRAS = 1  # cambiar a 2 para mayor precisión

df["cliente_norm"] = df["cliente"].apply(
    lambda v: _normalizar_por_palabras(str(v).strip(), catalogo, N_PALABRAS)
    if not pd.isna(v) else v
)
```

**Ventajas del enfoque dinámico:**

| | Diccionario estático actual | Matching dinámico |
|---|---|---|
| Variantes nuevas | Hay que agregar a mano | Se resuelven automáticamente |
| Nombre canónico | Definido en settings.py (puede diferir del Relevamiento) | Siempre usa el nombre exacto del Relevamiento |
| Riesgo de falsos positivos | Ninguno | Con n=1: "Ford" y "Fordham" matchearían. Con n=2: mucho menor |
| Precisión configurable | No | Sí — cambiando `N_PALABRAS` |

**Cuándo usar cada valor de N_PALABRAS:**

- `N_PALABRAS = 1`: máxima cobertura, útil cuando el cliente tiene un nombre único de una sola palabra (`Spotify`, `Techint`, `Ford`). Riesgo: falsos positivos si dos clientes comparten la primera palabra.
- `N_PALABRAS = 2`: balance. Cubre la mayoría de los casos y evita falsos positivos.
- `N_PALABRAS = 3`: muy preciso, pero puede dejar sin matchear muchas variantes.

**Advertencia**: el matching dinámico no reemplaza completamente el diccionario estático para casos como `"J&J ARGENTINA S.A"` → `"J&J"` (abreviaciones que no son la primera palabra) o CUITs con formato incorrecto. Se puede usar ambos en combinación: primero el diccionario, luego el matching dinámico como fallback.

---

## Configuración de Power BI

### Tipos de columna críticos en Power Query

Al importar los CSVs, Power BI detecta automáticamente los tipos. Hay que corregir manualmente:

| Tabla | Columna | Tipo incorrecto | Tipo correcto |
|---|---|---|---|
| `dim_clientes` | `cuit` | Int64 | **Texto** |
| `dim_relevamiento` | `cuit` | Int64 | **Texto** |
| `fact_esperado` | `cuit` | Int64 | **Texto** |

Para corregir: `Inicio → Transformar datos` → seleccionar la tabla → paso "Tipo cambiado" → cambiar `Int64.Type` a `type text` en la columna `cuit`.

### Tabla Activos (Personal.xlsx)

`Personal.xlsx` se carga directamente en Power BI (no por el pipeline). En Power Query agregar columna `username`:

```m
Text.Lower(Text.BeforeDelimiter([e-mail], "@"))
```

Después filtrar blancos y quitar duplicados en la columna `username`.

### Relaciones en el modelo

Abrir `Vista → Modelo` y crear estas 3 relaciones:

| Desde (Muchos) | → | Hacia (Uno) | Cardinalidad | Cross-filter |
|---|---|---|---|---|
| `fact_ejecuciones[cuit_cliente]` | → | `dim_clientes[cuit]` | Many to One | **Single** |
| `fact_ejecuciones[herramienta]` | → | `dim_herramientas[herramienta]` | Many to One | **Single** |
| `fact_ejecuciones[username]` | → | `Activos[username]` | Many to One | **Single** |

`dim_relevamiento` y `fact_esperado` quedan **sueltas, sin relaciones**.

### Medidas DAX

Crear en `fact_ejecuciones`:

```dax
Total Ejecuciones = COUNTROWS(fact_ejecuciones)

Corridas Exitosas =
CALCULATE(COUNTROWS(fact_ejecuciones), fact_ejecuciones[estado_normalizado] = "Correcto")

Ejecuciones Erroneas =
CALCULATE(COUNTROWS(fact_ejecuciones), fact_ejecuciones[estado_normalizado] = "Erroneo")

Tasa Exito % = DIVIDE([Corridas Exitosas], [Total Ejecuciones], 0) * 100

Clientes Ejecutados = DISTINCTCOUNT(fact_ejecuciones[nombre_cliente_canonico])
```

Columna calculada en `fact_ejecuciones` (Herramientas de tabla → Nueva columna):

```dax
nombre_mes =
SWITCH(fact_ejecuciones[mes],
    1,"01-Ene", 2,"02-Feb", 3,"03-Mar", 4,"04-Abr",
    5,"05-May", 6,"06-Jun", 7,"07-Jul", 8,"08-Ago",
    9,"09-Sep", 10,"10-Oct", 11,"11-Nov", 12,"12-Dic",
    "Sin fecha"
)
```

Ordenar `nombre_mes` por la columna `mes`: Herramientas de columna → Ordenar por columna → mes.

Crear en `fact_esperado`:

```dax
Ejecuciones Esperadas = SUM(fact_esperado[ejecuciones_esperadas])

-- Versión correcta de Cumplimiento % usando TREATAS
-- (sin TREATAS el resultado es incorrecto porque las tablas están sueltas)
Corridas Exitosas RvE =
CALCULATE(
    [Corridas Exitosas],
    TREATAS(
        SUMMARIZE(fact_esperado, fact_esperado[herramienta], fact_esperado[nombre_cliente]),
        fact_ejecuciones[herramienta], fact_ejecuciones[nombre_cliente_canonico]
    )
)

Cumplimiento % = DIVIDE([Corridas Exitosas RvE], [Ejecuciones Esperadas], 0) * 100

Herramientas Esperadas = DISTINCTCOUNT(fact_esperado[herramienta])

Herramientas Ejecutadas =
CALCULATE(
    DISTINCTCOUNT(fact_ejecuciones[herramienta]),
    TREATAS(VALUES(fact_esperado[nombre_cliente]), fact_ejecuciones[nombre_cliente_canonico]),
    fact_ejecuciones[estado_normalizado] = "Correcto",
    fact_ejecuciones[en_relevamiento] = TRUE()
)
```

### Páginas del dashboard

| Página | Visuales principales | Segmentadores |
|---|---|---|
| **1 - Resumen Ejecutivo** | 3 KPI cards + Gráfico de líneas (evolución) + Tabla de bots | Línea de servicio, Cliente, Herramienta, Usuario, Fechas |
| **2 - Evolución Temporal** | Columnas apiladas por estado + Línea de Tasa Exito % | Año, Estado |
| **3 - Herramientas** | Barras horizontales + Dispersión (volumen vs calidad) + Tabla | En Relevamiento, Año |
| **4 - Clientes** | Barras Top 15 + Treemap + Tabla | Herramienta, Año, Línea de servicio |
| **5 - Usuarios** | Columnas + Barras tasa éxito + Tabla | Herramienta, Línea, Sublínea, Año |
| **6 - Real vs Esperado** | 3 KPI cards + Barras agrupadas + Tabla pivote | Herramienta, Año, Mes, Cliente (todos de fact_esperado) |
| **7 - Calidad de Datos** | Donut CUIT/NOMBRE/VACIO + Barras sin cliente + Tabla CUITs dummy | Tipo de cliente |

---

## Bugs conocidos y sus fixes

### Bug 1 — Real vs Esperado muestra 1,190% de cumplimiento

**Causa**: `Corridas Exitosas` devuelve las 28.285 totales sin filtrar por herramienta/cliente porque `fact_ejecuciones` y `fact_esperado` están desconectadas.

**Fix**: usar la medida `Corridas Exitosas RvE` con `TREATAS` (ver sección Medidas DAX).

### Bug 2 — Permisos de Embarque no cruza

**Causa**: `fact_ejecuciones` tiene `"Reingenieria"` (sin tilde) y `fact_esperado` tiene `"Reingeniería"` (con tilde). Son strings distintos.

**Fix**: ya corregido en `settings.py`. Regenerar CSVs con `python main.py`.

### Bug 3 — Nombre de cliente no coincide entre tablas

**Causa**: `CLIENTE_VARIANTES` mapea a mayúsculas (`"SPOTIFY"`) pero el Relevamiento tiene `"Spotify"`. El cruce por nombre en TREATAS falla.

**Fix pendiente**: implementar el matching dinámico descrito en la sección anterior, o actualizar `CLIENTE_VARIANTES` para que los valores coincidan exactamente con los nombres del Relevamiento.

---

## Migración futura a SQL

Cuando la fuente cambie de Excel a la tabla SQL `monitoreo_bots`, solo hay que modificar `clean_datos.py`:

```python
# Antes:
df = pd.read_excel(file_path, sheet_name="Tabla Monitoreos", engine="openpyxl")

# Después:
import sqlalchemy
engine = sqlalchemy.create_engine("postgresql://user:password@host:5432/db")
df = pd.read_sql("SELECT * FROM monitoreo_bots", engine)
```

El resto del pipeline no cambia.