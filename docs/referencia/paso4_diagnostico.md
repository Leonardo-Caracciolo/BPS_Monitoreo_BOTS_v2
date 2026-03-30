# paso4_diagnostico.py

Genera el archivo Excel de diagnóstico de calidad de datos. **No produce tablas para Power BI.** Su propósito es que el equipo pueda revisar la calidad del pipeline después de cada ejecución.

## Responsabilidad

Calcular métricas de calidad sobre `fact_ejecuciones` y escribirlas en un Excel con 7 hojas para facilitar el monitoreo y la detección de problemas.

## Hojas generadas

### resumen_general

KPIs clave del pipeline en formato lista:

| Métrica | Valor |
|---|---|
| Total ejecuciones | 30.881 |
| Con CUIT resuelto | 184 |
| Con CUIT resuelto (%) | 0.6% |
| Sin cliente (vacío) | 17.220 |
| Sin cliente (%) | 55.8% |
| Estado Correcto | 28.285 |
| Estado Correcto (%) | 91.6% |
| Estado Erróneo | 2.269 |
| Estado Erróneo (%) | 7.4% |
| Clientes únicos (Relevamiento) | 46 |
| Herramientas únicas | 11 |

### cobertura_tipo_cliente

Distribución de los tres tipos de dato en el campo `cliente` con porcentajes. Permite ver la evolución de la adopción del CUIT como formato estándar.

| tipo_cliente | ejecuciones | porcentaje |
|---|---|---|
| VACIO | 17.220 | 55.8% |
| NOMBRE | 13.659 | 44.2% |
| CUIT | 2 | 0.0% |

### procesos_sin_cliente

Qué procesos tienen más registros con `tipo_cliente = "VACIO"`. Útil para identificar qué bots se ejecutan sin asignar cliente y priorizar cuáles corregir primero.

| proceso_original | ejecuciones |
|---|---|
| WP - Impuestos a las Ganancias | 9.193 |
| GUI: Padrones Impositivos | 3.744 |
| ... | ... |

### procesos_sin_relevam

Procesos con `en_relevamiento = False`, es decir, procesos que se ejecutan pero no están en el Relevamiento. Útil para identificar qué bots deberían agregarse al Relevamiento.

### top_clientes

Top 50 clientes por volumen de ejecuciones, incluyendo conteos de correctas, erróneas y tasa de éxito calculada.

### top_procesos

Todos los procesos con sus ejecuciones, herramienta mapeada, flag `en_relevamiento` y tasa de éxito. Permite identificar qué procesos tienen baja tasa de éxito.

### errores_por_proceso

Combinaciones de proceso × cliente con más ejecuciones erróneas, ordenadas descendente. Permite identificar qué cliente-proceso tiene más problemas de calidad.

## Función

::: paso4_diagnostico.generar_diagnostico

## Ejemplo de uso

```python
from pathlib import Path
from paso4_diagnostico import generar_diagnostico

generar_diagnostico(
    fact=fact,
    dim_clientes=dim_clientes,
    dim_relevamiento=dim_relevamiento,
    output_path=Path("data/outputs/diagnostico_matcheo.xlsx")
)
# 📋 Diagnóstico generado: data/outputs/diagnostico_matcheo.xlsx
```

## Cuándo revisar el diagnóstico

- Después de cada ejecución del pipeline con datos nuevos.
- Cuando algún gráfico de Power BI muestre valores inesperados.
- Para hacer seguimiento de los CUITs dummy pendientes de actualizar.
- Para detectar si aparecieron nuevos nombres de clientes que no están en `CLIENTE_VARIANTES`.

!!! warning "Archivo abierto en Excel"
    Si `diagnostico_matcheo.xlsx` está abierto en Excel al ejecutar el pipeline, se genera un `PermissionError`. Cerrar el archivo primero.
