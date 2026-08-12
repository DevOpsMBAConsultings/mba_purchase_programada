# Web Responsive Customization (`web_responsive_custom`)

Pequeña extensión sobre el tema `web_responsive` (de OCA) que habilita dos configuraciones de usuario adicionales.

## Qué hace

Permite que cada usuario configure, desde sus propios ajustes de perfil, el tipo de búsqueda del menú de aplicaciones y el tema visual del menú de aplicaciones (`apps_menu_search_type`, `apps_menu_theme`) — configuraciones que `web_responsive` trae, pero que por defecto no son editables por el usuario final desde su propio perfil.

## Cómo funciona

Hereda `res.users` y agrega esos dos campos a las listas `SELF_READABLE_FIELDS` y `SELF_WRITEABLE_FIELDS`, que son los mecanismos nativos de Odoo para controlar qué campos puede leer/escribir un usuario sobre **su propio** registro (sin permisos de administrador). Al agregarlos ahí, el campo se vuelve editable desde Ajustes → Preferencias, sin necesitar acceso de administrador.

Se instala automáticamente (`auto_install`) cuando `web_responsive` está presente.

## Dependencias

- `web_responsive`

## Licencia

Ver manifest del módulo.
