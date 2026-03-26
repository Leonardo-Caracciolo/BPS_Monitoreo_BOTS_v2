# BPS Monitoreo Bots — Pipeline ETL

Pipeline de procesamiento de datos que consolida ejecuciones de bots automatizados con el relevamiento de clientes y herramientas asignadas, produciendo tablas limpias para Power BI.

---

## Estructura del proyecto

```
BPS_Monitoreo_Bots/
│
├── main.py                    ← Entry point. Ejecutar esto.
├── settings.py                ← Paths, constantes y diccionarios de mapeo
├── clean_datos.py             ← Lectura y limpieza de DB_Server.xlsx
├── merge_datos.py             ← Lectura y join de sheets del Relevamiento
├── paso1_relevamiento.py      ← Construye dim_clientes y dim_relevamiento
├── paso2_db_server.py         ← Clasifica y enriquece las ejecuciones
├── paso3_fact_ejecuciones.py  ← Construye la tabla de hechos principal
├── construir_esperado.py      ← Construye fact_esperado (Real vs Esperado)
├── paso4_diagnostico.py       ← Genera reporte de calidad en Excel
│
└── data/
    ├── inputs/                ← Archivos fuente (no modificar)
    │   ├── DB_Server.xlsx
    │   ├── Relevamiento_BPS_Organizado_-_v2.xlsm
    │   └── Tabla_Cuits.xlsx
    │
    └── outputs/               ← Tablas generadas para Power BI
        ├── dim_clientes.csv
        ├── dim_herramientas.csv
        ├── dim_relevamiento.csv
        ├── fact_ejecuciones.csv
        ├── fact_esperado.csv
        └── diagnostico_matcheo.xlsx
```

---

## Requisitos

```
pandas>=2.0.0
openpyxl>=3.1.0
```

Instalar con:

```bash
pip install pandas openpyxl
```

---

## Cómo ejecutar

```bash
python main.py
```

Tiempo estimado: menos de 30 segundos.

---

## Archivos de entrada

| Archivo | Descripción | Sheet |
|---|---|---|
| `DB_Server.xlsx` | 30.881 ejecuciones reales de bots | Tabla Monitoreos |
| `Relevamiento_BPS_Organizado_-_v2.xlsm` | Clientes y herramientas asignadas | Clientes + Uso de herramientas |
| `Tabla_Cuits.xlsx` | Lookup razón social → CUIT | (hoja principal) |

---

## Archivos de salida

| Archivo | Filas | Descripción |
|---|---|---|
| `dim_clientes.csv` | 46 | Un registro por cliente único (clave: cuit) |
| `dim_herramientas.csv` | 26 | Catálogo de herramientas con flag en_relevamiento |
| `dim_relevamiento.csv` | 517 | Cruce cliente × herramienta con flag usa_herramienta |
| `fact_ejecuciones.csv` | 30.881 | Tabla de hechos principal |
| `fact_esperado.csv` | 2.376 | Ejecuciones esperadas por cliente × herramienta × mes |
| `diagnostico_matcheo.xlsx` | — | 7 hojas de diagnóstico de calidad de datos |

---

## Modelo de datos en Power BI

```
dim_clientes ←── fact_ejecuciones ──→ dim_herramientas
                        │
                        └──────────────────→ Activos (Personal.xlsx)

dim_relevamiento  (suelta — sin relaciones)
fact_esperado     (suelta — sin relaciones)
```

### Relaciones a crear

| Desde (Muchos) | Hacia (Uno) | Cardinalidad | Cross-filter |
|---|---|---|---|
| `fact_ejecuciones[cuit_cliente]` | `dim_clientes[cuit]` | Many to One | Single |
| `fact_ejecuciones[herramienta]` | `dim_herramientas[herramienta]` | Many to One | Single |
| `fact_ejecuciones[username]` | `Activos[username]` | Many to One | Single |

---

## Medidas DAX principales

Todas se crean seleccionando `fact_ejecuciones` → `Nueva medida`:

```dax
Total Ejecuciones    = COUNTROWS(fact_ejecuciones)
Corridas Exitosas    = CALCULATE(COUNTROWS(fact_ejecuciones), fact_ejecuciones[estado_normalizado] = "Correcto")
Ejecuciones Erroneas = CALCULATE(COUNTROWS(fact_ejecuciones), fact_ejecuciones[estado_normalizado] = "Erroneo")
Tasa Exito %         = DIVIDE([Corridas Exitosas], [Total Ejecuciones], 0) * 100
Clientes Ejecutados  = DISTINCTCOUNT(fact_ejecuciones[nombre_cliente_canonico])
```

Real vs Esperado (en `fact_esperado`):

```dax
Ejecuciones Esperadas = SUM(fact_esperado[ejecuciones_esperadas])
Cumplimiento %        = DIVIDE([Corridas Exitosas], [Ejecuciones Esperadas], 0) * 100
```

---

## Mantenimiento

### Actualizar con datos nuevos

1. Reemplazá los archivos en `data/inputs/`
2. Corrés `python main.py`
3. En Power BI: `Inicio → Actualizar`

### Agregar una variante nueva de cliente

Editá el diccionario `CLIENTE_VARIANTES` en `settings.py`:

```python
CLIENTE_VARIANTES: dict[str, str] = {
    ...
    "Nombre nuevo tal cual aparece en DB_Server": "NOMBRE_CANONICO",
}
```

### Agregar un proceso nuevo al mapeo

Editá `PROCESO_A_HERRAMIENTA` en `settings.py`:

```python
PROCESO_A_HERRAMIENTA: dict[str, str] = {
    ...
    "Nombre exacto del proceso en DB_Server": "Herramienta del Relevamiento",
}
```

### Migración futura a SQL

En `paso2_db_server.py`, reemplazar:

```python
df = clean_datos(str(path_db))
```

Por:

```python
import sqlalchemy
engine = sqlalchemy.create_engine("tu_connection_string")
df = pd.read_sql("SELECT * FROM monitoreo_bots", engine)
```