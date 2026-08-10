# -*- coding: utf-8 -*-
"""
Auto-tema: alinea los estilos de subtotal/total de los 4 reportes MIS al
color de marca YA configurado en cada empresa (Ajustes > Ajustes Generales
> Diseño del Documento -> res.company.primary_color), sin que nadie tenga
que editar el módulo por cliente.

Se ejecuta solo (post_init_hook) al instalar el módulo. Si el cliente
cambia su color de marca DESPUÉS de instalado, hay una acción contextual
en la ficha de la Empresa ("MBA: Sincronizar tema de reportes MIS con la
marca", ver data/ir_actions_server.xml) que vuelve a correr esta misma
lógica sin necesidad de tocar código ni la base de datos a mano.

Si la empresa no tiene primary_color configurado (nunca abrió el asistente
de Diseño del Documento), no se toca nada: los reportes se quedan con la
paleta por defecto definida en data/mis_report_style.xml.
"""
import re


def _lighten_hex(hex_color, factor=0.85):
    """Mezcla hex_color con blanco. factor=0 -> color original,
    factor=1 -> blanco puro. 0.85 da un tinte claro apto para fondo de
    fila de subtotal sin perder legibilidad del texto."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    r = round(r + (255 - r) * factor)
    g = round(g + (255 - g) * factor)
    b = round(b + (255 - b) * factor)
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def _pick_contrast_text(hex_color):
    """Texto blanco sobre colores oscuros, texto oscuro sobre colores
    claros, calculado por luminancia percibida (evita texto ilegible si
    el color de marca de un cliente futuro resulta ser claro/pastel)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#FFFFFF" if luminance < 140 else "#1A1A1A"


def _apply_brand_theme(env):
    company = env.company
    primary = (company.primary_color or "").strip()
    if not re.match(r"^#[0-9A-Fa-f]{6}$", primary):
        # Sin color de marca configurado todavía: se deja la paleta por
        # defecto del módulo tal cual está en data/mis_report_style.xml.
        return

    style_total = env.ref(
        "mba_estados_financieros_mis.style_total", raise_if_not_found=False
    )
    style_subtotal = env.ref(
        "mba_estados_financieros_mis.style_subtotal", raise_if_not_found=False
    )
    style_subtotal_indent = env.ref(
        "mba_estados_financieros_mis.style_subtotal_indent",
        raise_if_not_found=False,
    )

    light_tint = _lighten_hex(primary, 0.85)
    text_color = _pick_contrast_text(primary)

    if style_total:
        style_total.write({"background_color": primary, "color": text_color})
    if style_subtotal:
        style_subtotal.write({"background_color": light_tint})
    if style_subtotal_indent:
        style_subtotal_indent.write({"background_color": light_tint})


def post_init_hook(env):
    _apply_brand_theme(env)
