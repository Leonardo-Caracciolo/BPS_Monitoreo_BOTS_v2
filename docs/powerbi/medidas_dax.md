# Medidas DAX

Para crear cada medida: seleccionás la tabla indicada en el panel derecho → `Inicio → Nueva medida` → pegás el código → Enter.

---

## Medidas base (en fact_ejecuciones)

```dax
Total Ejecuciones = COUNTROWS(fact_ejecuciones)
```

```dax
Corridas Exitosas =
CALCULATE(
    COUNTROWS(fact_ejecuciones),
    fact_ejecuciones[estado_normalizado] = "Correcto"
)
```

```dax
Ejecuciones Erroneas =
CALCULATE(
    COUNTROWS(fact_ejecuciones),
    fact_ejecuciones[estado_normalizado] = "Erroneo"
)
```

```dax
Tasa Exito % =
DIVIDE([Corridas Exitosas], [Total Ejecuciones], 0) * 100
```

```dax
Clientes Ejecutados =
DISTINCTCOUNT(fact_ejecuciones[nombre_cliente_canonico])
```

---

## Columna calculada nombre_mes (en fact_ejecuciones)

Esta es una **columna calculada**, no una medida. Crear con `Herramientas de tabla → Nueva columna`:

```dax
nombre_mes =
SWITCH(fact_ejecuciones[mes],
    1,  "01-Ene",  2,  "02-Feb",  3,  "03-Mar",
    4,  "04-Abr",  5,  "05-May",  6,  "06-Jun",
    7,  "07-Jul",  8,  "08-Ago",  9,  "09-Sep",
    10, "10-Oct", 11, "11-Nov", 12, "12-Dic",
    "Sin fecha"
)
```

Después: clic en la columna `nombre_mes` → `Herramientas de columna → Ordenar por columna → mes`. Esto asegura que los gráficos muestren los meses en orden cronológico.

---

## Medidas Real vs Esperado (en fact_esperado)

```dax
Ejecuciones Esperadas =
SUM(fact_esperado[ejecuciones_esperadas])
```

```dax
Cumplimiento % =
DIVIDE([Corridas Exitosas], [Ejecuciones Esperadas], 0) * 100
```

---

## Tabla de todas las medidas

| Medida | Tabla | Tipo | Uso |
|---|---|---|---|
| `Total Ejecuciones` | fact_ejecuciones | Medida | KPI general, Eje Y gráficos |
| `Corridas Exitosas` | fact_ejecuciones | Medida | KPI principal Página 1 |
| `Ejecuciones Erroneas` | fact_ejecuciones | Medida | Tabla detalle |
| `Tasa Exito %` | fact_ejecuciones | Medida | Formato condicional tablas |
| `Clientes Ejecutados` | fact_ejecuciones | Medida | KPI Página 1 |
| `nombre_mes` | fact_ejecuciones | Columna calculada | Eje X gráficos temporales |
| `Ejecuciones Esperadas` | fact_esperado | Medida | Real vs Esperado |
| `Cumplimiento %` | fact_esperado | Medida | Real vs Esperado |

---

## La regla más importante

| Zona del visual | Qué poner |
|---|---|
| Eje X | Siempre un **campo** (columna de tabla) |
| Eje Y | Siempre una **medida** |
| Leyenda | Siempre un **campo** |
| Valores | Siempre una **medida** |

Si Power BI dice `"Este campo no se puede usar aquí porque se requiere un campo que no es de medida"`, es porque se puso una medida donde va un campo o viceversa.
