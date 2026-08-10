# Módulo de solo datos: no define modelos Python propios.
# Reutiliza mis.report / mis.report.kpi / mis.report.instance de mis_builder
# y account.account.tag del núcleo de account.
#
# Única excepción: hooks.py, que aplica el color de marca de la empresa
# (Ajustes > Diseño del Documento) a los estilos MIS al instalar el módulo.
from . import hooks
from .hooks import post_init_hook
