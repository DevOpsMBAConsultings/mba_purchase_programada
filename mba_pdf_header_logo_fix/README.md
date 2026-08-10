# mba_pdf_header_logo_fix

**v18.0.1.0.0**

Módulo Odoo 18 CE — MBA Consultings. Corrige el logo y el bloque de datos
de la empresa que no se pintan en el encabezado de reportes **PDF**
(generados con wkhtmltopdf) cuando el Diseño de Documentos activo es
Light/Standard, Boxed o Bold. La vista previa HTML dentro de Odoo se ve
bien; el problema es exclusivo del PDF.

Agnóstico de cliente: no depende de nada específico de un cliente en
particular, así que se reutiliza vía `git subtree` en cualquier repo de
cliente de MBA Consultings que use Odoo 18 CE + wkhtmltopdf, igual que
[`mba_estados_financieros_mis`](https://github.com/DevOpsMBAConsultings/mba_estados_financieros_mis).

## Causa raíz

wkhtmltopdf extrae el bloque `header` de estos 3 layouts y lo renderiza
en un sub-proceso de WebKit aparte (vía `--header-html`), con soporte
pobre de flexbox/CSS Grid — justo lo que usan `.row`/`.col-*`/`.d-flex`
de Bootstrap 5. El logo queda embebido en el PDF (confirmable con
Ghostscript) pero no se pinta en el lienzo del header.

Detalle técnico completo, evidencia del diagnóstico y justificación de
cada XPath: ver el campo `description` en
`mba_pdf_header_logo_fix/__manifest__.py`.

## Solución

Hereda por XPath (`inherit_id` + `position="replace"`) el contenedor
flexbox del header en los 3 layouts y lo reemplaza por una tabla HTML
(`<table><tr><td>`), el patrón clásico de compatibilidad para motores de
render viejos. Mantiene el logo repitiéndose en cada página (no usa el
atajo de sacar el logo del header, que perdería esa repetición en
reportes multi-página como un Estado de Cuenta). Cero cambios a archivos
del módulo `web` de Odoo.

## Alcance

Cubre Light/Standard, Boxed y Bold. Striped, Bubble, Wave y Folder no
están cubiertos todavía — mismo patrón aplica si algún cliente los usa y
presenta el mismo síntoma.

## Instalación en un repo de cliente (git subtree)

```bash
git remote add mba_pdf_header_logo_fix https://github.com/DevOpsMBAConsultings/mba_pdf_header_logo_fix.git
git subtree add --prefix=mba_pdf_header_logo_fix mba_pdf_header_logo_fix 18.0 --squash
```

Para traer actualizaciones futuras del módulo:

```bash
git subtree pull --prefix=mba_pdf_header_logo_fix mba_pdf_header_logo_fix 18.0 --squash
```

Después de traerlo al repo del cliente:

```bash
-i mba_pdf_header_logo_fix -d <base_de_datos> --stop-after-init
systemctl restart <servicio_odoo>
```

(El restart interrumpe brevemente el servicio — coordinar ventana con el
cliente si es producción.)

## Changelog

- **18.0.1.0.0** — Versión inicial. Fix de logo/header PDF para Standard,
  Boxed y Bold.
