# """
# settings.py
# -----------
# Configuración centralizada: paths, mapeos y constantes.
# """

# from pathlib import Path

# # ─── Paths ────────────────────────────────────────────────────────────────────
# ROOT = Path(__file__).resolve().parent

# INPUTS_DIR  = ROOT / "data" / "inputs"
# OUTPUTS_DIR = ROOT / "data" / "outputs"

# PATH_DB_SERVER    = INPUTS_DIR / "DB_Server.xlsx"
# PATH_RELEVAMIENTO = INPUTS_DIR / "Relevamiento BPS_Organizado - v2.xlsm"

# PATH_TABLA_CUITS  = INPUTS_DIR / "Tabla_Cuits.xlsx"

# OUT_DIM_CLIENTES     = OUTPUTS_DIR / "dim_clientes.csv"
# OUT_DIM_HERRAMIENTAS = OUTPUTS_DIR / "dim_herramientas.csv"
# OUT_DIM_RELEVAMIENTO = OUTPUTS_DIR / "dim_relevamiento.csv"
# OUT_FACT_EJECUCIONES = OUTPUTS_DIR / "fact_ejecuciones.csv"
# OUT_DIAGNOSTICO      = OUTPUTS_DIR / "diagnostico_matcheo.xlsx"

# # ─── Variantes de nombres de cliente ─────────────────────────────────────────
# # Clave: nombre exacto en DB_Server.cliente
# # Valor: nombre canónico a usar en el dashboard
# CLIENTE_VARIANTES: dict[str, str] = {
#     "Copetro": "COPETRO", "copetro": "COPETRO",
#     "copetro_ROA": "COPETRO", "COPETRO_ROA": "COPETRO",
#     "Kodak": "KODAK", "kodak": "KODAK",
#     "ULTRAGENYX ARGENTINA S.R.L": "ULTRAGENYX", "Ultragenyx": "ULTRAGENYX",
#     "J&J ARGENTINA S.A": "J&J",
#     "SPOTIFY ARGENTINA S.A": "SPOTIFY", "SPOTIFY ARGENTINA S.A.": "SPOTIFY", "Spotify": "SPOTIFY",
#     "Ternium": "TERNIUM",
#     "Tenaris": "TENARIS",
#     "ExxonMobil": "EXXONMOBIL", "Exxonmobil": "EXXONMOBIL",
#     "Techint": "TECHINT",
#     "Ford": "FORD",
#     "Amazon": "AMAZON",
#     "Newmont": "NEWMONT",
#     "Sanofi": "SANOFI",
#     "Roche": "ROCHE",
#     "Philips": "PHILIPS", "PHILIPS ARGENTINA SOCIEDAD ANONIMA": "PHILIPS",
#     "Mars": "MARS",
#     "Genpact": "GENPACT", "GENPACT ARGENTINA S.R.L.": "GENPACT",
#     "Allflex": "ALLFLEX", "allflex": "ALLFLEX",
#     "Allflex MO": "ALLFLEX", "Allflex - MO": "ALLFLEX",
#     "Allflex - ROA": "ALLFLEX", "Allflex ROA": "ALLFLEX",
#     "tetra": "TETRA", "Tetra": "TETRA",
#     "Ingredion": "INGREDION", "INGREDION ARGENTINA SRL": "INGREDION",
#     "helmerich": "HELMERICH", "Helmerich": "HELMERICH",
#     "ITT  CAN": "ITT CAN",
#     "Bunge S.A.": "BUNGE",
#     "30-69555646-9": "30695556469",
#     "Expeditors": "EXPEDITORS", "EXPEDITORS ARGENTINA S.A.": "EXPEDITORS",
#     "ALBEMARLE ARGENTINA S.R.L.": "ALBEMARLE", "ALBEMARLE ARGENTINA S.R.L": "ALBEMARLE",
#     "CAÑA DE CASTILLA S.R.L.": "CAÑA DE CASTILLA", "Caña de Castilla S.R.L": "CAÑA DE CASTILLA",
# }

# # ─── Mapeo proceso DB_Server → herramienta canónica ──────────────────────────
# # Consolida variantes de nombre de proceso al nombre de herramienta del Relevamiento
# PROCESO_A_HERRAMIENTA: dict[str, str] = {
#     "NFE Alert":                                                     "NFE Alert",
#     "ACROBAT TOOLS":                                                 "Acrobat Tools",
#     "GUI: Padrones Impositivos (Nac & Prov)":                        "Padrones Impositivos - ComplyPro",
#     "GUI: Control Percepciones":                                     "Padrones Impositivos - ComplyPro",
#     "GUI: Control de Percepciones Sufridas":                         "Padrones Impositivos - ComplyPro",
#     "GUI: Control Correlatividad":                                   "Control de correlatividad - ComplyPro",
#     "GUI: Controlar correlatividad":                                 "Control de correlatividad - ComplyPro",
#     "AFIP voucher correlativity control":                            "Control de correlatividad - ComplyPro",
#     "GUI: Identificación Duplicados":                                "Control de duplicados - ComplyPro",
#     "GUI: Detección de duplicados":                                  "Control de duplicados - ComplyPro",
#     "GUI:  Detección de duplicados":                                 "Control de duplicados - ComplyPro",
#     "GUI: Descarga de Deducciones Sufridas":                         "Descarga de deducciones - ComplyPro",
#     "Descarga de Deducciones Sufridas":                              "Descarga de deducciones - ComplyPro",
#     "GUI: Identificación de registros faltantes":                    "Identificacion de registros faltantes - ComplyPro",
#     "GUI: Control Registros Faltantes":                              "Identificacion de registros faltantes - ComplyPro",
#     "GUI: Conciliación Deducciones (ERP vs Fisco Nac & Prov)":       "Conciliacion de Deducciones - ComplyPro",
#     "GUI: Control Totales":                                          "Sumarizacion y control por totales - ComplyPro",
#     "GUI: Controlar Totales":                                        "Sumarizacion y control por totales - ComplyPro",
#     "GUI: Sumarización & Control por Totales":                       "Sumarizacion y control por totales - ComplyPro",
#     "Permisos de Embarque":                                          "Permisos de Embarque MOA Reingenieria",
#     "Tracking de Vencimientos":                                      "Calendarios Impositivos",
#     "WP - Impuestos a las Ganancias":                                "WP - Impuestos a las Ganancias",
#     "WP - Imp Gcias Personas Fisicas":                               "WP - Imp Gcias Personas Fisicas",
#     "Tablas Ratio Report para informes de Precios de Transferencia": "Tablas Ratio Report - Precios de Transferencia",
#     "CARGA DDJJ - F2668":                                            "CARGA DDJJ - F2668",
#     "GUI: Instalación":                                              "GUI: Instalacion",
#     "GUI: Actualizacion":                                            "GUI: Actualizacion",
#     "UY - Envio Recibo de sueldos":                                  "UY - Envio Recibo de Sueldos",
#     "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Profesional": "SLATAM - Validacion Tiempos",
#     "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Socio":       "SLATAM - Validacion Tiempos",
#     "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Seun":        "SLATAM - Validacion Tiempos",
#     "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Marketplace": "SLATAM - Validacion Tiempos",
#     "Payroll - Match recibo CUIL en PDF":                            "Payroll - Match Recibo CUIL",
#     "MX - Ultragenyx":                                               "MX - Ultragenyx",
#     "CO - Ultragenyx":                                               "CO - Ultragenyx",
#     "F572":                                                          "F572",
#     "Carga de Autonomos VEP":                                        "Carga de Autonomos VEP",
#     "Proceso Bunge":                                                 "Proceso Bunge",
#     "Revision de Domicilios Fiscales Electronicos":                  "Revision Domicilios Fiscales Electronicos",
# }

# # Procesos sin herramienta en el Relevamiento (flag en_relevamiento=False)
# PROCESOS_SIN_HERRAMIENTA: set[str] = {
#     "WP - Impuestos a las Ganancias",
#     "WP - Imp Gcias Personas Fisicas",
#     "Tablas Ratio Report para informes de Precios de Transferencia",
#     "CARGA DDJJ - F2668",
#     "GUI: Instalación",
#     "GUI: Actualizacion",
#     "UY - Envio Recibo de sueldos",
#     "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Profesional",
#     "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Socio",
#     "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Seun",
#     "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Marketplace",
#     "Payroll - Match recibo CUIL en PDF",
#     "MX - Ultragenyx",
#     "CO - Ultragenyx",
#     "F572",
#     "Carga de Autonomos VEP",
#     "Proceso Bunge",
#     "Revision de Domicilios Fiscales Electronicos",
# }



"""
settings.py
-----------
Configuración centralizada: paths, mapeos y constantes.
"""

from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent

INPUTS_DIR  = ROOT / "data" / "inputs"
OUTPUTS_DIR = ROOT / "data" / "outputs"

PATH_DB_SERVER    = INPUTS_DIR / "DB_Server.xlsx"
PATH_RELEVAMIENTO = INPUTS_DIR / "Relevamiento BPS_Organizado - v2.xlsm"
PATH_TABLA_CUITS  = INPUTS_DIR / "Tabla_Cuits.xlsx"

OUT_DIM_CLIENTES     = OUTPUTS_DIR / "dim_clientes.csv"
OUT_DIM_HERRAMIENTAS = OUTPUTS_DIR / "dim_herramientas.csv"
OUT_DIM_RELEVAMIENTO = OUTPUTS_DIR / "dim_relevamiento.csv"
OUT_FACT_EJECUCIONES = OUTPUTS_DIR / "fact_ejecuciones.csv"
OUT_FACT_ESPERADO    = OUTPUTS_DIR / "fact_esperado.csv"
OUT_DIAGNOSTICO      = OUTPUTS_DIR / "diagnostico_matcheo.xlsx"

# ─── Variantes de nombres de cliente ─────────────────────────────────────────
CLIENTE_VARIANTES: dict[str, str] = {
    "Copetro": "COPETRO", "copetro": "COPETRO",
    "copetro_ROA": "COPETRO", "COPETRO_ROA": "COPETRO",
    "Kodak": "KODAK", "kodak": "KODAK",
    "ULTRAGENYX ARGENTINA S.R.L": "ULTRAGENYX", "Ultragenyx": "ULTRAGENYX",
    "J&J ARGENTINA S.A": "J&J",
    "SPOTIFY ARGENTINA S.A": "SPOTIFY", "SPOTIFY ARGENTINA S.A.": "SPOTIFY", "Spotify": "SPOTIFY",
    "Ternium": "TERNIUM",
    "Tenaris": "TENARIS",
    "ExxonMobil": "EXXONMOBIL", "Exxonmobil": "EXXONMOBIL",
    "Techint": "TECHINT",
    "Ford": "FORD",
    "Amazon": "AMAZON",
    "Newmont": "NEWMONT",
    "Sanofi": "SANOFI",
    "Roche": "ROCHE",
    "Philips": "PHILIPS", "PHILIPS ARGENTINA SOCIEDAD ANONIMA": "PHILIPS",
    "Mars": "MARS",
    "Genpact": "GENPACT", "GENPACT ARGENTINA S.R.L.": "GENPACT",
    "Allflex": "ALLFLEX", "allflex": "ALLFLEX",
    "Allflex MO": "ALLFLEX", "Allflex - MO": "ALLFLEX",
    "Allflex - ROA": "ALLFLEX", "Allflex ROA": "ALLFLEX",
    "tetra": "TETRA", "Tetra": "TETRA",
    "Ingredion": "INGREDION", "INGREDION ARGENTINA SRL": "INGREDION",
    "helmerich": "HELMERICH", "Helmerich": "HELMERICH",
    "ITT  CAN": "ITT CAN",
    "Bunge S.A.": "BUNGE",
    "30-69555646-9": "30695556469",
    "Expeditors": "EXPEDITORS", "EXPEDITORS ARGENTINA S.A.": "EXPEDITORS",
    "ALBEMARLE ARGENTINA S.R.L.": "ALBEMARLE", "ALBEMARLE ARGENTINA S.R.L": "ALBEMARLE",
    "CAÑA DE CASTILLA S.R.L.": "CAÑA DE CASTILLA", "Caña de Castilla S.R.L": "CAÑA DE CASTILLA",
}

# ─── Mapeo proceso DB_Server → herramienta canónica ──────────────────────────
PROCESO_A_HERRAMIENTA: dict[str, str] = {
    "NFE Alert":                                                     "NFE Alert",
    "ACROBAT TOOLS":                                                 "Acrobat Tools",
    "GUI: Padrones Impositivos (Nac & Prov)":                        "Padrones Impositivos - ComplyPro",
    "GUI: Control Percepciones":                                     "Padrones Impositivos - ComplyPro",
    "GUI: Control de Percepciones Sufridas":                         "Padrones Impositivos - ComplyPro",
    "GUI: Control Correlatividad":                                   "Control de correlatividad - ComplyPro",
    "GUI: Controlar correlatividad":                                 "Control de correlatividad - ComplyPro",
    "AFIP voucher correlativity control":                            "Control de correlatividad - ComplyPro",
    "GUI: Identificación Duplicados":                                "Control de duplicados - ComplyPro",
    "GUI: Detección de duplicados":                                  "Control de duplicados - ComplyPro",
    "GUI:  Detección de duplicados":                                 "Control de duplicados - ComplyPro",
    "GUI: Descarga de Deducciones Sufridas":                         "Descarga de deducciones - ComplyPro",
    "Descarga de Deducciones Sufridas":                              "Descarga de deducciones - ComplyPro",
    "GUI: Identificación de registros faltantes":                    "Identificacion de registros faltantes - ComplyPro",
    "GUI: Control Registros Faltantes":                              "Identificacion de registros faltantes - ComplyPro",
    "GUI: Conciliación Deducciones (ERP vs Fisco Nac & Prov)":       "Conciliacion de Deducciones - ComplyPro",
    "GUI: Control Totales":                                          "Sumarizacion y control por totales - ComplyPro",
    "GUI: Controlar Totales":                                        "Sumarizacion y control por totales - ComplyPro",
    "GUI: Sumarización & Control por Totales":                       "Sumarizacion y control por totales - ComplyPro",
    "Permisos de Embarque":                                          "Permisos de Embarque MOA Reingenieria",
    "Tracking de Vencimientos":                                      "Calendarios Impositivos",
    "WP - Impuestos a las Ganancias":                                "WP - Impuestos a las Ganancias",
    "WP - Imp Gcias Personas Fisicas":                               "WP - Imp Gcias Personas Fisicas",
    "Tablas Ratio Report para informes de Precios de Transferencia": "Tablas Ratio Report - Precios de Transferencia",
    "CARGA DDJJ - F2668":                                            "CARGA DDJJ - F2668",
    "GUI: Instalación":                                              "GUI: Instalacion",
    "GUI: Actualizacion":                                            "GUI: Actualizacion",
    "UY - Envio Recibo de sueldos":                                  "UY - Envio Recibo de Sueldos",
    "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Profesional": "SLATAM - Validacion Tiempos",
    "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Socio":       "SLATAM - Validacion Tiempos",
    "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Seun":        "SLATAM - Validacion Tiempos",
    "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Marketplace": "SLATAM - Validacion Tiempos",
    "Payroll - Match recibo CUIL en PDF":                            "Payroll - Match Recibo CUIL",
    "MX - Ultragenyx":                                               "MX - Ultragenyx",
    "CO - Ultragenyx":                                               "CO - Ultragenyx",
    "F572":                                                          "F572",
    "Carga de Autonomos VEP":                                        "Carga de Autonomos VEP",
    "Proceso Bunge":                                                 "Proceso Bunge",
    "Revision de Domicilios Fiscales Electronicos":                  "Revision Domicilios Fiscales Electronicos",
}

PROCESOS_SIN_HERRAMIENTA: set[str] = {
    "WP - Impuestos a las Ganancias",
    "WP - Imp Gcias Personas Fisicas",
    "Tablas Ratio Report para informes de Precios de Transferencia",
    "CARGA DDJJ - F2668",
    "GUI: Instalación",
    "GUI: Actualizacion",
    "UY - Envio Recibo de sueldos",
    "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Profesional",
    "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Socio",
    "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Seun",
    "Operaciones SLATAM & Talento - Validacion de tiempos y utilizacion - Marketplace",
    "Payroll - Match recibo CUIL en PDF",
    "MX - Ultragenyx",
    "CO - Ultragenyx",
    "F572",
    "Carga de Autonomos VEP",
    "Proceso Bunge",
    "Revision de Domicilios Fiscales Electronicos",
}