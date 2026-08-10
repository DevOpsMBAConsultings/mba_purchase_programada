# Módulo mayormente de datos: reutiliza mis.report / mis.report.kpi /
# mis.report.instance de mis_builder y account.account.tag del núcleo de
# account.
#
# Excepciones Python:
# - hooks.py, que aplica el color de marca de la empresa (Ajustes >
#   Diseño del Documento) a los estilos MIS al instalar el módulo.
# - models/res_company.py, un método mínimo para volver a aplicar ese
#   color desde la acción contextual de la ficha de Empresa (no puede
#   llamar a hooks.py directo desde la ir.actions.server: ver hooks.py).
from . import hooks
from . import models
from .hooks import post_init_hook
