# settings.py

Archivo de configuración centralizada. **Es el único lugar donde se deben modificar paths, constantes y diccionarios de mapeo.** Ningún otro archivo tiene paths hardcodeados.

---

## Paths de entrada y salida

```python
ROOT          = Path(__file__).resolve().parent   # raíz del proyecto

INPUTS_DIR    = ROOT / "data" / "inputs"
OUTPUTS_DIR   = ROOT / "data" / "outputs"

PATH_DB_SERVER    = INPUTS_DIR / "DB_Server.xlsx"
PATH_RELEVAMIENTO = INPUTS_DIR / "Relevamiento_BPS_Organizado_-_v2.xlsm"
PATH_TABLA_CUITS  = INPUTS_DIR / "Tabla_Cuits.xlsx"

OUT_DIM_CLIENTES     = OUTPUTS_DIR / "dim_clientes.csv"
OUT_DIM_HERRAMIENTAS = OUTPUTS_DIR / "dim_herramientas.csv"
OUT_DIM_RELEVAMIENTO = OUTPUTS_DIR / "dim_relevamiento.csv"
OUT_FACT_EJECUCIONES = OUTPUTS_DIR / "fact_ejecuciones.csv"
OUT_FACT_ESPERADO    = OUTPUTS_DIR / "fact_esperado.csv"
OUT_DIAGNOSTICO      = OUTPUTS_DIR / "diagnostico_matcheo.xlsx"
```

---

## CLIENTE_VARIANTES

Diccionario de 61 entradas que mapea variantes del mismo cliente al nombre canónico. Se aplica en `paso2_db_server.py` antes de clasificar el campo `cliente`.

**Estructura:**

```python
CLIENTE_VARIANTES: dict[str, str] = {
    # clave: nombre exacto como aparece en DB_Server.cliente
    # valor: nombre canónico a usar en el dashboard
    "Copetro":  "COPETRO",
    "copetro":  "COPETRO",
    "ExxonMobil": "EXXONMOBIL",
    "Exxonmobil": "EXXONMOBIL",
    # ... 57 entradas más
}
```

**Cómo agregar una nueva variante:**

Si aparece un cliente con un nombre nuevo que es variante de uno ya existente, agregar la entrada al diccionario:

```python
"NUEVO NOMBRE VARIANTE": "NOMBRE_CANONICO_EXISTENTE",
```

**Grupos detectados (36 en total):**

| Nombre canónico | Variantes |
|---|---|
| `TECHINT` | `Techint` |
| `EXXONMOBIL` | `ExxonMobil`, `Exxonmobil` |
| `TENARIS` | `Tenaris` |
| `TERNIUM` | `Ternium` |
| `SPOTIFY` | `Spotify`, `SPOTIFY ARGENTINA S.A`, `SPOTIFY ARGENTINA S.A.` |
| `J&J` | `J&J ARGENTINA S.A` |
| `ULTRAGENYX` | `ULTRAGENYX ARGENTINA S.R.L`, `Ultragenyx` |
| `COPETRO` | `Copetro`, `copetro`, `copetro_ROA`, `COPETRO_ROA` |
| `ALLFLEX` | `Allflex`, `allflex`, `Allflex MO`, `Allflex - MO`, `Allflex - ROA`, `Allflex ROA` |
| ... | ... |

---

## PROCESO_A_HERRAMIENTA

Diccionario que traduce el nombre técnico del proceso en DB_Server al nombre canónico de la herramienta en el Relevamiento. Se aplica en `paso3_fact_ejecuciones.py`.

**El problema que resuelve:** los bots tienen nombres distintos en DB_Server y en el Relevamiento. Por ejemplo:

```
DB_Server proceso            →  Relevamiento herramienta
──────────────────────────────────────────────────────────
"GUI: Control Correlatividad" → "Control de correlatividad - ComplyPro"
"GUI: Controlar correlatividad" → "Control de correlatividad - ComplyPro"
"AFIP voucher correlativity control" → "Control de correlatividad - ComplyPro"
"Tracking de Vencimientos" → "Calendarios Impositivos"
"ACROBAT TOOLS" → "Acrobat Tools"
```

**Mapeo muchos a uno:** múltiples procesos pueden mapear a la misma herramienta canónica. Esto consolida todas las variantes del nombre de un mismo bot en una sola herramienta.

**Procesos sin herramienta en el Relevamiento:** algunos procesos como `WP - Impuestos a las Ganancias` (9.633 ejecuciones) no tienen herramienta en el Relevamiento porque son procesos internos. Se incluyen en el dashboard con su nombre original y `en_relevamiento = False`.

**Cómo agregar un nuevo proceso:**

```python
# En PROCESO_A_HERRAMIENTA:
"Nombre exacto del proceso en DB_Server": "Herramienta del Relevamiento",

# Si es externo (no tiene herramienta en Relevamiento):
"Nombre del proceso": "Nombre del proceso",  # mapeado a sí mismo

# Y también agregarlo a PROCESOS_SIN_HERRAMIENTA:
PROCESOS_SIN_HERRAMIENTA = {
    ...,
    "Nombre del proceso",
}
```

---

## PROCESOS_SIN_HERRAMIENTA

Set con los nombres de procesos que no tienen herramienta en el Relevamiento. Se usa en `paso3_fact_ejecuciones.py` para calcular el flag `en_relevamiento = False`.

Procesos incluidos actualmente (18):

- `WP - Impuestos a las Ganancias` (9.633 ejecuciones)
- `WP - Imp Gcias Personas Fisicas` (6.781 ejecuciones)
- `Tablas Ratio Report para informes de Precios de Transferencia` (2.517 ejecuciones)
- `CARGA DDJJ - F2668` (274 ejecuciones)
- `GUI: Instalación` (228 ejecuciones)
- `Operaciones SLATAM & Talento` (4 variantes, 294 ejecuciones en total)
- `UY - Envio Recibo de sueldos` (202 ejecuciones)
- `Payroll - Match recibo CUIL en PDF` (41 ejecuciones)
- `MX - Ultragenyx`, `CO - Ultragenyx`, `F572`, `Carga de Autonomos VEP`, `Proceso Bunge`, `Revision de Domicilios Fiscales Electronicos`

::: settings
    options:
      show_source: true
      show_root_heading: false
      members:
        - CLIENTE_VARIANTES
        - PROCESO_A_HERRAMIENTA
        - PROCESOS_SIN_HERRAMIENTA
