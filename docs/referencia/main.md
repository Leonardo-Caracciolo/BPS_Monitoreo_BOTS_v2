# main.py

Entry point del pipeline. Orquesta la ejecución de todos los pasos en el orden correcto, imprime el progreso y exporta los CSVs finales.

## Responsabilidad

Coordinar la llamada a cada paso en el orden correcto, pasando los DataFrames de un paso al siguiente, y exportar los resultados.

## Cómo ejecutar

```bash
python main.py
```

## Estructura de ejecución

```
main()
  │
  ├── PASO 1: leer_relevamiento()
  │     ├── Llama a merge_datos()
  │     ├── Limpia CUITs
  │     ├── Detecta dummies
  │     ├── Deduplica por CUIT
  │     └── Produce: dim_clientes, dim_relevamiento
  │
  ├── Construye dim_herramientas desde dim_relevamiento
  │   (herramientas únicas con en_relevamiento=True)
  │
  ├── PASO 2: leer_db_server()
  │     ├── Llama a clean_datos()
  │     ├── Construye lookup nombre→CUIT
  │     ├── Normaliza variantes (CLIENTE_VARIANTES)
  │     ├── Clasifica CUIT/NOMBRE/VACIO
  │     ├── Calcula duracion_segundos, anio, mes, semana
  │     └── Produce: df_db
  │
  ├── PASO 3: construir_fact_ejecuciones()
  │     ├── Mapea proceso→herramienta (PROCESO_A_HERRAMIENTA)
  │     ├── Calcula en_relevamiento
  │     ├── Normaliza estados (_ESTADO_MAP)
  │     ├── Join con dim_clientes por CUIT
  │     ├── Agrega herramientas externas a dim_herramientas
  │     └── Produce: fact_ejecuciones, dim_herramientas final
  │
  ├── PASO 4: construir_esperado()
  │     ├── Filtra usa_herramienta=True del relevamiento
  │     ├── Extrae períodos reales de fact_ejecuciones
  │     ├── Cross join combinaciones × períodos
  │     └── Produce: fact_esperado
  │
  ├── PASO 5: Exportar CSVs
  │     ├── dim_clientes.csv
  │     ├── dim_herramientas.csv
  │     ├── dim_relevamiento.csv
  │     ├── fact_ejecuciones.csv
  │     └── fact_esperado.csv
  │
  └── PASO 6: generar_diagnostico()
        └── diagnostico_matcheo.xlsx
```

## Detalle de cada paso en main.py

### Construcción de dim_herramientas

`dim_herramientas` no tiene un paso dedicado. Se construye en dos partes dentro de `main.py`:

**Parte 1** — después del PASO 1: herramientas del Relevamiento (en_relevamiento=True):
```python
dim_herramientas = (
    dim_relevamiento[["herramienta"]]
    .drop_duplicates()
    .assign(en_relevamiento=True)
    .sort_values("herramienta")
    .reset_index(drop=True)
)
```

**Parte 2** — después del PASO 3: agrega procesos externos (en_relevamiento=False):
```python
herr_extra = (
    fact[~fact["en_relevamiento"]][["herramienta"]]
    .drop_duplicates()
    .assign(en_relevamiento=False)
)
dim_herramientas = pd.concat([dim_herramientas, herr_extra]).drop_duplicates()
```

Esto produce las 26 herramientas: 11 del Relevamiento + 15 procesos externos.

## Código fuente

```python
import pandas as pd

from settings import (
    PATH_DB_SERVER, PATH_RELEVAMIENTO, PATH_TABLA_CUITS,
    OUTPUTS_DIR,
    OUT_DIM_CLIENTES, OUT_DIM_HERRAMIENTAS, OUT_DIM_RELEVAMIENTO,
    OUT_FACT_EJECUCIONES, OUT_FACT_ESPERADO, OUT_DIAGNOSTICO,
)
from paso1_relevamiento      import leer_relevamiento
from paso2_db_server         import leer_db_server
from paso3_fact_ejecuciones  import construir_fact_ejecuciones
from construir_esperado      import construir_esperado
from paso4_diagnostico       import generar_diagnostico


def banner(texto: str) -> None:
    sep = "─" * 60
    print(f"\n{sep}\n  {texto}\n{sep}")


def main() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    # ... ver código completo en main.py
```
