# Módulo de solo vistas: no define modelos ni lógica Python.
# Hereda por XPath los templates QWeb de web.external_layout_standard /
# web.external_layout_boxed / web.external_layout_bold para reemplazar el
# contenedor flexbox del header (donde va el logo) por una tabla HTML,
# porque wkhtmltopdf renderiza el header del PDF en un sub-proceso con
# soporte pobre de flexbox/CSS Grid. Ver __manifest__.py para el
# diagnóstico completo.
