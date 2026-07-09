# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import re

class AccountMove(models.Model):
    _inherit = "account.move"

    dgi_document_type_id = fields.Many2one(
        "dgi.document.type",
        string="Tipo de documento (DGI)",
        tracking=True,
    )

    dgi_naturaleza_operacion = fields.Selection(
        selection=[
            ("01", "01 Venta"),
            ("02", "02 Exportación"),
            ("10", "10 Transferencia"),
            ("11", "11 Devolución"),
            ("12", "12 Remesa"),
            ("13", "13 Consignación"),
            ("20", "20 Compra"),
            ("21", "21 Importación"),
        ],
        string="Naturaleza de la Operación",
        tracking=True,
        default="01",
    )
    
    dgi_tipo_operacion = fields.Selection(
        selection=[
            ("", "—"),
            ("1", "Salida o Venta"),
            ("2", "Entrada o Compra"),
        ],
        string="Tipo de la Operación",
        tracking=True,
        default="1",
    )

    dgi_payment_method_id = fields.Many2one(
        "dgi.payment.method",
        string="Método de Pago (DGI)",
        tracking=True,
    )

    dgi_payment_term_type = fields.Selection(
        selection=[
            ("", "—"),
            ("contado", "Contado"),
            ("credito", "Crédito/Plazo"),
        ],
        string="Plazos",
        default="contado",
        required=True,
        tracking=True,
    )

    # Missing DGI Fields
    dgi_plazo_option = fields.Selection(
        selection=[
            ("", "—"),
            ("30", "30 días"),
            ("60", "60 días"),
            ("90", "90 días"),
            ("other", "Otro"),
        ],
        string="Plazo (DGI)",
        help="Opción de plazo para ventas a crédito.",
    )
    dgi_plazo_due_date = fields.Date(
        string="Fecha de vencimiento (DGI)",
        tracking=True,
    )
    dgi_payment_method_other_desc = fields.Char(
        string="Descripción forma de pago",
        tracking=True,
    )
    dgi_payment_notes = fields.Text(
        string="Notas complementarias",
        tracking=True,
    )
    dgi_retention_type_id = fields.Many2one(
        "dgi.retention.type",
        string="Retención",
    )
    dgi_retention_amount = fields.Monetary(
        string="Monto Retención",
        currency_field="currency_id",
        compute="_compute_dgi_retention_amount",
    )
    dgi_retention_readonly = fields.Boolean(
        string="Retención Auto-seleccionada",
        compute="_compute_dgi_retention_auto",
    )
    dgi_retention_receptor_filter = fields.Char(
        string="Filtro Receptor Retención",
        compute="_compute_dgi_retention_receptor_filter",
    )
    dgi_amount_untaxed = fields.Monetary(string="Base Imponible DGI", currency_field="currency_id")
    dgi_amount_taxes = fields.Monetary(string="Impuestos DGI", currency_field="currency_id")
    dgi_amount_total = fields.Monetary(string="Total a pagar DGI", currency_field="currency_id")
    dgi_show_retention_block = fields.Boolean(
        string="Mostrar Retención",
        compute="_compute_dgi_show_retention_block",
    )
    dgi_is_from_sale = fields.Boolean(
        string="Viene de Cotización",
        compute="_compute_dgi_is_from_sale",
        store=True,
        help="True si la factura fue generada desde una cotización/orden de venta aprobada."
    )

    @api.depends("invoice_origin", "move_type")
    def _compute_dgi_is_from_sale(self):
        for move in self:
            # Las notas de crédito siempre se pueden editar
            if move.move_type == 'out_refund':
                move.dgi_is_from_sale = False
                continue
            # Si tiene documento de origen (viene de una cotización/orden de venta), bloquearlo
            move.dgi_is_from_sale = bool(move.invoice_origin)

    @api.depends("partner_id", "fiscal_position_id")
    def _compute_dgi_show_retention_block(self):
        """
        Mostrar el bloque de retención/exento si el cliente tiene posición fiscal
        de retención o exento de impuestos.
        """
        for move in self:
            show = False
            if move.move_type in ('out_invoice', 'out_refund'):
                fp = move.fiscal_position_id
                if not fp and move.partner_id:
                    fp = move.partner_id.property_account_position_id
                if fp and 'retenci' in (fp.name or '').lower():
                    show = True
            move.dgi_show_retention_block = show

    @api.depends("partner_id", "fiscal_position_id")
    def _compute_dgi_retention_auto(self):
        """
        Auto-selecciona el tipo de retención según tipo de cliente + posición fiscal.
        - Gobierno: auto-select código 1 (100%) o 2 (50%), readonly
        - Contribuyente: el usuario escoge entre código 4 o 7, editable
        """
        RetType = self.env["dgi.retention.type"]
        for move in self:
            if move.move_type not in ('out_invoice', 'out_refund'):
                move.dgi_retention_readonly = False
                continue

            fp = move.fiscal_position_id
            if not fp and move.partner_id:
                fp = move.partner_id.property_account_position_id
            fp_name = (fp.name or '').lower() if fp else ''
            receptor = move.partner_id.l10n_pa_receptor_tipo or ''

            if not fp or 'retenci' not in fp_name:
                move.dgi_retention_readonly = False
                continue

            # Detectar porcentaje de la posición fiscal
            is_100 = '100' in fp_name
            is_50 = '50' in fp_name

            if receptor == '03':  # Gobierno
                if is_100:
                    ret = RetType.search([('code', '=', '1'), ('receptor_type', '=', 'gobierno')], limit=1)
                elif is_50:
                    ret = RetType.search([('code', '=', '2'), ('receptor_type', '=', 'gobierno')], limit=1)
                else:
                    ret = False
                if ret and move.dgi_retention_type_id != ret:
                    move.dgi_retention_type_id = ret
                move.dgi_retention_readonly = True

            elif receptor == '01':  # Contribuyente
                # No auto-seleccionar, el usuario escoge entre 4 y 7
                move.dgi_retention_readonly = False

            else:
                move.dgi_retention_readonly = False

    @api.depends("partner_id")
    def _compute_dgi_retention_receptor_filter(self):
        """Mapea tipo receptor del partner al receptor_type del modelo dgi.retention.type."""
        MAPPING = {'01': 'contribuyente', '03': 'gobierno'}
        for move in self:
            receptor = move.partner_id.l10n_pa_receptor_tipo or ''
            move.dgi_retention_receptor_filter = MAPPING.get(receptor, '')

    @api.depends("line_ids.balance", "line_ids.tax_line_id")
    def _compute_dgi_retention_amount(self):
        """
        Calcula el monto de retención desde las líneas de impuestos reales.
        Las retenciones son impuestos con amount negativo (ej: -50% del ITBMS).
        Non-stored para recalcular en tiempo real durante edición.
        """
        for move in self:
            if move.move_type not in ('out_invoice', 'out_refund'):
                move.dgi_retention_amount = 0.0
                continue

            # Buscar líneas de impuestos de retención (impuestos con amount < 0)
            retention_amount = 0.0
            for line in move.line_ids:
                if line.tax_line_id and line.tax_line_id.amount < 0:
                    retention_amount += abs(line.balance)
            move.dgi_retention_amount = retention_amount

    # Campos PAC y DGI genéricos
    l10n_pa_cufe = fields.Char(string="CUFE", copy=False, index=True, tracking=True)
    l10n_pa_qr_url = fields.Char(string="URL del Código QR", copy=False)
    l10n_pa_pac_status = fields.Selection([
        ('draft', 'No Enviado'),
        ('sent', 'Enviado'),
        ('accepted', 'Aceptado DGI'),
        ('cancelled', 'Anulado DGI'),
        ('error', 'Error / Rechazado'),
    ], string="Estado DGI/PAC", default='draft', copy=False, tracking=True)
    l10n_pa_pac_error = fields.Text(string="Error del PAC", copy=False)
    l10n_pa_pac_request = fields.Text(string="JSON Enviado (PAC)", copy=False)
    l10n_pa_pac_response = fields.Text(string="Respuesta PAC", copy=False)
    
    def action_l10n_pa_send_to_pac(self):
        """
        Método base que debe ser extendido por los conectores (HKA, Digifact, etc.).
        Deberá armar el payload (XML/JSON), enviarlo al PAC, e hidratar 
        l10n_pa_cufe y l10n_pa_qr_url.
        """
        self.ensure_one()
        raise NotImplementedError(_("Debe instalar un módulo conector PAC (Ej: mba_pa_edi_hka) para emitir la factura electrónica."))

    def _pa_next_numero(self):
        """
        Siguiente número fiscal para esta empresa/diario.
        Busca el MAX numérico entre todas las facturas HKA enviadas al PAC + 1.

        IMPORTANTE: Se excluyen números > 9,999,999 para evitar contaminación
        de esquemas legacy (ej. Digifact usa formato YYMMDDXXXX que produce
        números como 202600009, mucho mayores que los secuenciales de HKA).
        """
        self.ensure_one()
        # Umbral: ninguna empresa en PA emitirá más de 9 millones de facturas
        # electrónicas, pero cualquier número Digifact supera los 200 millones.
        MAX_VALID = 9_999_999

        domain = [
            ('company_id', '=', self.company_id.id),
            ('journal_id', '=', self.journal_id.id),
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('l10n_pa_pac_status', 'in', ('sent', 'accepted', 'cancelled', 'error')),
            ('name', '!=', False),
            ('name', '!=', '/'),
        ]
        moves = self.sudo().search_read(domain, ['name'], order='id desc')

        max_num = 0
        for m in moves:
            digits = re.sub(r'\D', '', m['name'] or '')
            try:
                n = int(digits) if digits else 0
                # Ignorar números de otros esquemas (Digifact, etc.)
                if 0 < n <= MAX_VALID and n > max_num:
                    max_num = n
            except (ValueError, TypeError):
                pass

        return str(max_num + 1).zfill(10)

    @api.onchange('partner_id')
    def _onchange_partner_dgi_validated(self):
        """
        Evita usar un cliente que no ha sido validado con la DGI.
        Si no está validado, muestra una advertencia y limpia el campo.
        Solo aplica a facturas de clientes.
        También copia las notas complementarias del contacto al borrador.
        """
        if self.partner_id and self.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
            partner_valid = self.partner_id.l10n_pa_is_dgi_validated
            if not partner_valid and self.partner_id.parent_id:
                partner_valid = self.partner_id.parent_id.l10n_pa_is_dgi_validated
                
            if not partner_valid:
                partner_name = self.partner_id.name
                self.partner_id = False
                return {
                    'warning': {
                        'title': _("Cliente no Validado con DGI"),
                        'message': _(
                            "El cliente '%s' no ha sido validado con la DGI y no puede ser utilizado en facturación.\n\n"
                            "Por favor, abra la ficha del contacto y asegúrese de que la alerta roja de validación desaparezca (Validando RUC o Método de pago si es Consumidor Final)."
                        ) % (partner_name,),
                    }
                }

            # Copiar notas complementarias del contacto al borrador de factura
            partner = self.partner_id
            inv_partner_id = partner.address_get(['invoice']).get('invoice')
            if inv_partner_id:
                inv_partner = self.env['res.partner'].browse(inv_partner_id)
                notes = inv_partner.dgi_payment_notes or partner.dgi_payment_notes
            else:
                notes = partner.dgi_payment_notes
            if notes:
                self.dgi_payment_notes = notes


    @api.constrains('partner_id', 'move_type', 'state')
    def _check_partner_dgi_validated(self):
        """
        No permitir facturar si el cliente no está validado con la DGI.
        Solo aplica a facturas de clientes (out_invoice, out_refund) cuando se van a publicar o guardar.
        """
        for move in self:
            if move.move_type in ['out_invoice', 'out_refund', 'out_receipt'] and move.partner_id:
                partner_valid = move.partner_id.l10n_pa_is_dgi_validated
                if not partner_valid and move.partner_id.parent_id:
                    partner_valid = move.partner_id.parent_id.l10n_pa_is_dgi_validated
                    
                if not partner_valid:
                    raise UserError(
                        _("El cliente '%s' no ha sido validado con la DGI.\n\n"
                          "Por favor, abra la ficha del contacto y valide sus datos antes de guardar la factura.") % (move.partner_id.name,)
                    )

    def action_post(self):
        if self.env.context.get('skip_pac_send'):
            return super(AccountMove, self).action_post()
            
        for move in self:
            if move.move_type in ('out_invoice', 'out_refund') and move.company_id.account_fiscal_country_id.code == 'PA':
                # Return wizard action instead of posting directly
                return {
                    'name': _('Confirmar y Enviar Factura a DGI (PAC)'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'mba_pa_edi.confirmar.enviar.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_move_id': move.id},
                }
        
        return super(AccountMove, self).action_post()
