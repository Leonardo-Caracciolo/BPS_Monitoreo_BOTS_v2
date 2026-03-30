# Instalación y ejecución

## Requisitos

- Python 3.10 o superior
- Las siguientes librerías:

```
pandas>=2.0.0
openpyxl>=3.1.0
```

## Instalación

```bash
pip install pandas openpyxl
```

## Estructura de carpetas

Antes de ejecutar, la carpeta debe tener esta estructura:

```
BPS_Monitoreo_Bots/
├── main.py
├── settings.py
├── clean_datos.py
├── merge_datos.py
├── paso1_relevamiento.py
├── paso2_db_server.py
├── paso3_fact_ejecuciones.py
├── construir_esperado.py
├── paso4_diagnostico.py
└── data/
    ├── inputs/
    │   ├── DB_Server.xlsx                          ← Requerido
    │   ├── Relevamiento_BPS_Organizado_-_v2.xlsm  ← Requerido
    │   └── Tabla_Cuits.xlsx                        ← Requerido
    └── outputs/                                    ← Se genera automáticamente
```

## Nombres de archivos requeridos

Los nombres deben coincidir exactamente con los definidos en `settings.py`:

| Constante en settings.py | Nombre de archivo esperado |
|---|---|
| `PATH_DB_SERVER` | `DB_Server.xlsx` |
| `PATH_RELEVAMIENTO` | `Relevamiento_BPS_Organizado_-_v2.xlsm` |
| `PATH_TABLA_CUITS` | `Tabla_Cuits.xlsx` |

Si el archivo tiene un nombre distinto, hay dos opciones:

1. Renombrar el archivo para que coincida.
2. Editar `settings.py` y cambiar el nombre en la constante correspondiente.

## Ejecución

```bash
# Desde la raíz del proyecto
python main.py
```

### Salida esperada

```
────────────────────────────────────────────────────────────
  PASO 1 | Leyendo Relevamiento BPS...
────────────────────────────────────────────────────────────
  merge_datos: Clientes=47 filas, Uso herramientas=517 filas
  → dim_clientes:        46 filas
  → dim_relevamiento:   517 filas

────────────────────────────────────────────────────────────
  PASO 2 | Leyendo y clasificando DB_Server...
────────────────────────────────────────────────────────────
  clean_datos: 30,881 filas leídas
  → Total ejecuciones: 30,881
     VACIO       : 17,220  (55.8%)
     NOMBRE      : 13,659  (44.2%)
     CUIT        :      2  (0.0%)

────────────────────────────────────────────────────────────
  PASO 3 | Construyendo fact_ejecuciones...
────────────────────────────────────────────────────────────
  → fact_ejecuciones: 30,881 filas
  → Herramientas únicas: 26
  → Clientes con CUIT:   184
  → En Relevamiento:     10,702 (34.7%)

────────────────────────────────────────────────────────────
  PASO 4 | Construyendo fact_esperado (Real vs Esperado)...
────────────────────────────────────────────────────────────
  → fact_esperado: 2,376 filas (108 combinaciones × 22 meses)

────────────────────────────────────────────────────────────
  PASO 5 | Exportando tablas para Power BI...
────────────────────────────────────────────────────────────
  ✅ dim_clientes.csv          → 46 filas
  ✅ dim_herramientas.csv      → 26 filas
  ✅ dim_relevamiento.csv      → 517 filas
  ✅ fact_ejecuciones.csv      → 30,881 filas
  ✅ fact_esperado.csv         → 2,376 filas

────────────────────────────────────────────────────────────
  ✅ Pipeline finalizado correctamente
────────────────────────────────────────────────────────────
```

## Actualización de datos

Cuando haya datos nuevos en DB_Server o cambios en el Relevamiento:

1. Reemplazá los archivos en `data/inputs/` con las versiones nuevas.
2. Ejecutá `python main.py`.
3. En Power BI: `Inicio → Actualizar`.

Power BI relee los CSVs automáticamente y actualiza todos los gráficos.

## Errores comunes

### `FileNotFoundError`
El archivo no está en `data/inputs/` o el nombre no coincide exactamente.
Verificar mayúsculas, guiones y extensión.

### `PermissionError` al generar el diagnóstico
El archivo `diagnostico_matcheo.xlsx` está abierto en Excel. Cerrarlo y volver a ejecutar.

### `KeyError: 'Tabla Monitoreos'`
El sheet en DB_Server.xlsx no se llama exactamente `"Tabla Monitoreos"`. Verificar el nombre en el Excel o actualizarlo en `settings.py` (`SHEET_DB_SERVER`).

### Valores `0` en columnas `anio` y `mes` en Power BI
Las columnas `anio` y `mes` en el CSV usan tipo `Int64` de pandas, que Power Query puede interpretar como `Int64.Type`. Si el tipo se cambió a `Int64.Type` en Power Query en vez de `type number`, verificar que el paso "Tipo cambiado" tenga `{"anio", Int64.Type}` y `{"mes", Int64.Type}`.
