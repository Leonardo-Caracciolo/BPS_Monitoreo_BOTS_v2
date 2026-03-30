# Arquitectura

## Decisión de diseño: monolítica plana

El proyecto usa una **arquitectura monolítica plana**: todos los archivos `.py` viven en la raíz del proyecto, sin carpetas de módulos ni paquetes. Esta decisión fue tomada deliberadamente porque:

- Son pocos archivos (9 en total).
- El proyecto no va a escalar en complejidad.
- Facilita la lectura y el mantenimiento para alguien que no conoce el código.
- No requiere configurar `PYTHONPATH` ni `__init__.py`.

## Separación de responsabilidades

Aunque el proyecto es plano, cada archivo tiene una responsabilidad única y bien definida:

| Archivo | Responsabilidad |
|---|---|
| `settings.py` | Centraliza todos los paths y diccionarios de configuración. Es el único lugar que hay que tocar al agregar un nuevo mapeo. |
| `clean_datos.py` | Solo lectura y limpieza básica de strings. Sin lógica de negocio. |
| `merge_datos.py` | Solo lectura del Relevamiento y join entre sheets. Sin lógica de negocio. |
| `paso1_relevamiento.py` | Transforma lo que devuelve `merge_datos()` en tablas válidas para Power BI. |
| `paso2_db_server.py` | Transforma lo que devuelve `clean_datos()` aplicando clasificación y normalización de negocio. |
| `paso3_fact_ejecuciones.py` | Une los resultados de paso1 y paso2 en la tabla de hechos final. |
| `construir_esperado.py` | Genera la tabla de comparación Real vs Esperado. |
| `paso4_diagnostico.py` | Genera el reporte de calidad. No produce tablas para Power BI. |
| `main.py` | Orquesta la ejecución de todos los pasos en orden. |

## Modelo de datos (Star Schema)

El pipeline produce un modelo estrella para Power BI:

```
                    dim_clientes
                    ┌──────────────┐
                    │ cuit (PK)    │
                    │ nombre       │
                    │ gerente      │
                    │ cuit_dummy   │
                    └──────┬───────┘
                           │ M:1 Single
                           │
dim_herramientas    fact_ejecuciones         Activos (Personal)
┌──────────────┐   ┌──────────────────┐     ┌──────────────┐
│herramienta(PK)│←─│ cuit_cliente (FK)│     │username (PK) │
│en_relevamiento│  │ herramienta (FK) │────→│ linea        │
└──────────────┘  │ username (FK)    │     │ sublinea     │
      M:1 Single  │ estado_normaliz. │     └──────────────┘
                  │ iniciado         │           M:1 Single
                  │ finalizado       │
                  │ duracion_seg     │
                  │ tipo_cliente     │
                  │ en_relevamiento  │
                  │ anio / mes       │
                  └──────────────────┘

dim_relevamiento   fact_esperado
(suelta)           (suelta)
```

### Por qué dim_relevamiento y fact_esperado están sueltas

Power BI detecta **rutas ambiguas** cuando hay múltiples caminos para llegar a una misma tabla. Si `dim_relevamiento` estuviera conectada a `dim_clientes` y también lo estuviera `fact_ejecuciones`, Power BI no sabría qué camino usar al filtrar y tiraría error.

Ambas tablas se usan directamente en los visuales de Power BI sin necesidad de relaciones formales.

## Flujo de ejecución

```
main.py
  │
  ├── PASO 1: leer_relevamiento(PATH_RELEVAMIENTO)
  │     └── merge_datos()               ← lee .xlsm, join sheets
  │         → dim_clientes (46 filas)
  │         → dim_relevamiento (517 filas)
  │
  ├── PASO 2: leer_db_server(PATH_DB_SERVER, PATH_TABLA_CUITS)
  │     └── clean_datos()               ← lee .xlsx, limpia strings
  │         → CLIENTE_VARIANTES         ← normaliza variantes
  │         → clasificar CUIT/NOMBRE/VACIO
  │         → lookup nombre→CUIT
  │         → calcular duracion, anio, mes, semana
  │         → df_db (30.881 filas)
  │
  ├── PASO 3: construir_fact_ejecuciones(df_db, dim_clientes)
  │         → PROCESO_A_HERRAMIENTA     ← mapea proceso→herramienta
  │         → _ESTADO_MAP               ← normaliza estados
  │         → join con dim_clientes por cuit
  │         → fact_ejecuciones (30.881 filas, 19 columnas)
  │
  ├── PASO 4: construir_esperado(dim_relevamiento, fact)
  │         → cross join usa_herramienta=True × períodos reales
  │         → fact_esperado (2.376 filas)
  │
  ├── PASO 5: exportar CSVs → data/outputs/
  │
  └── PASO 6: generar_diagnostico() → diagnostico_matcheo.xlsx
```

## Decisión: Personal.xlsx fuera del pipeline

El archivo `Personal.xlsx` (que contiene `Linea` y `Sublinea` de cada operador) **no se procesa en el pipeline Python**. Se importa directamente en Power BI y se transforma con Power Query (columna `username` = `Text.Lower(Text.BeforeDelimiter([e-mail], "@"))`).

Esta decisión se tomó porque el archivo tiene una estructura que el usuario ya maneja desde Power Query, y agregar otro paso al pipeline para algo que se puede hacer en Power BI directamente agrega complejidad innecesaria.

## Migración futura a SQL

Cuando DB_Server pase de Excel a la tabla SQL `monitoreo_bots`, el único cambio necesario está en `paso2_db_server.py`:

```python
# Antes (Excel)
df = clean_datos(str(path_db))

# Después (SQL)
import sqlalchemy
engine = sqlalchemy.create_engine("postgresql://user:pass@host/db")
df = pd.read_sql("SELECT * FROM monitoreo_bots", engine)
df = df.apply(
    lambda col: col.str.strip().str.replace(r"\s+", " ", regex=True)
    if col.dtype == "object" else col
)
```

El resto del pipeline permanece idéntico.
