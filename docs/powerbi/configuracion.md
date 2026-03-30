# Configuración de Power BI

## Importar los CSVs

`Inicio → Obtener datos → Texto o CSV` → navegás a `data/outputs/` → importás cada archivo.

Repetir 5 veces (una por cada CSV).

---

## Tipos de columna en Power Query

Abrí `Inicio → Transformar datos`. En cada tabla, hacé clic en el paso **"Tipo cambiado"** del panel derecho y corregí los tipos según esta tabla:

### dim_clientes

| Columna | Tipo correcto |
|---|---|
| `ID_Cliente` | Número entero |
| `cuit` | **Texto** ← cambiar de Int64 |
| `nombre_cliente` | Texto |
| `gerente_responsable` | Texto |
| `cuit_es_dummy` | Verdadero/Falso |

Buscar `{"cuit", Int64.Type}` y cambiar a `{"cuit", type text}`.

### dim_relevamiento

| Columna | Tipo correcto |
|---|---|
| `cuit` | **Texto** ← cambiar de Int64 |

Misma corrección que en dim_clientes.

### fact_ejecuciones

| Columna | Tipo correcto |
|---|---|
| `iniciado` | Fecha/hora |
| `finalizado` | Fecha/hora |
| `duracion_segundos` | Número decimal |
| `anio` | Número entero |
| `mes` | Número entero |
| `cuit_cliente` | Texto |
| `en_relevamiento` | Verdadero/Falso |

### fact_esperado

| Columna | Tipo correcto |
|---|---|
| `cuit` | **Texto** |
| `anio` | Número entero |
| `mes` | Número entero |
| `ejecuciones_esperadas` | Número entero |

---

## Tabla Activos (Personal.xlsx)

Personal.xlsx se carga directamente en Power BI (no por el pipeline). En Power Query se crea la columna `username` extrayendo el prefijo del email:

`Agregar columna → Columna personalizada`:

```
Nombre: username
Fórmula: Text.Lower(Text.BeforeDelimiter([e-mail], "@"))
```

Luego filtrar blancos y quitar duplicados en la columna `username`.

---

## Cerrar y aplicar

Después de todas las correcciones de tipos: `Cerrar y aplicar`.
