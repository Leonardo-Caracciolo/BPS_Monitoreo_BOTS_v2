# settings.py

Archivo de configuración centralizada. **Es el único archivo que hay que modificar** cuando cambian los paths de los archivos de entrada/salida o cuando se agregan nuevos mapeos de clientes o procesos.

## Paths

```python
ROOT = Path(__file__).resolve().parent
```

La raíz del proyecto se detecta automáticamente a partir de la ubicación del propio archivo `settings.py`. Esto permite mover la carpeta del proyecto sin tener que cambiar rutas hardcodeadas.

```python
INPUTS_DIR  = ROOT / "data" / "inputs"
OUTPUTS_DIR = ROOT / "data" / "outputs"
```

Todos los paths de archivos se construyen relativos a estas dos carpetas base.

## CLIENTE_VARIANTES

```python
CLIENTE_VARIANTES: dict[str, str]
```

Diccionario que mapea variantes de nombres de cliente al nombre canónico.

**Clave:** nombre exacto tal como aparece en la columna `cliente` de DB_Server.
**Valor:** nombre canónico que se usará en el dashboard.

**Por qué existe:** los operadores cargaron el nombre del cliente manualmente durante meses, generando 36 grupos de variantes para el mismo cliente. Por ejemplo:

```python
"ExxonMobil": "EXXONMOBIL",
"Exxonmobil": "EXXONMOBIL",
# Ambas mapean al mismo nombre canónico
```

**Cómo agregar una nueva variante:**

```python
CLIENTE_VARIANTES: dict[str, str] = {
    # ... entradas existentes ...
    "NuevoNombreVariante": "NOMBRE_CANONICO",
}
```

## PROCESO_A_HERRAMIENTA

```python
PROCESO_A_HERRAMIENTA: dict[str, str]
```

Mapea el nombre técnico del proceso en DB_Server al nombre canónico de la herramienta en el Relevamiento.

**Por qué existe:** los nombres de procesos en DB_Server son versiones técnicas o antiguas de los nombres de herramientas en el Relevamiento. Por ejemplo:

| Proceso en DB_Server | Herramienta en Relevamiento |
|---|---|
| `"GUI: Control Correlatividad"` | `"Control de correlatividad - ComplyPro"` |
| `"GUI: Controlar correlatividad"` | `"Control de correlatividad - ComplyPro"` |
| `"AFIP voucher correlativity control"` | `"Control de correlatividad - ComplyPro"` |
| `"Tracking de Vencimientos"` | `"Calendarios Impositivos"` |

Tres procesos distintos mapean a la misma herramienta. Esto permite contar ejecuciones por herramienta de forma consistente.

**Procesos sin herramienta en el Relevamiento** también están en el diccionario, mapeando a sí mismos para que tengan un nombre canónico consistente:

```python
"WP - Impuestos a las Ganancias": "WP - Impuestos a las Ganancias",
```

**Cómo agregar un proceso nuevo:**

```python
PROCESO_A_HERRAMIENTA: dict[str, str] = {
    # ... entradas existentes ...
    "Nombre exacto del proceso en DB_Server": "Herramienta del Relevamiento",
}
```

Si el proceso no tiene herramienta en el Relevamiento, también agregar a `PROCESOS_SIN_HERRAMIENTA`.

## PROCESOS_SIN_HERRAMIENTA

```python
PROCESOS_SIN_HERRAMIENTA: set[str]
```

Set con los nombres de procesos que existen en DB_Server pero **no** tienen herramienta asignada en el Relevamiento. Se usa en `paso3_fact_ejecuciones.py` para calcular el flag `en_relevamiento`.

Un proceso en este set recibirá `en_relevamiento = False` en `fact_ejecuciones`. Esto permite en Power BI filtrar entre "procesos del Relevamiento" y "procesos externos".

Procesos en este set:

- `WP - Impuestos a las Ganancias` (9.633 ejecuciones)
- `WP - Imp Gcias Personas Fisicas` (6.781 ejecuciones)
- `Tablas Ratio Report - Precios de Transferencia` (2.517 ejecuciones)
- `CARGA DDJJ - F2668` (274 ejecuciones)
- Y otros 14 procesos con menor volumen.
