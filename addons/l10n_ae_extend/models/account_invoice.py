# Part of Flectra. See LICENSE file for full copyright and licensing details.


from flectra import fields, models, api, _
from flectra.exceptions import Warning

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _default_config_type(self):
        domain = [('journal_id.type', '=', 'purchase')]
        if self._context.get('type', False) in ['out_invoice', 'out_refund']:
            domain = [('journal_id.type', '=', 'sale')]
        return self.journal_config_type.search(domain, limit=1)

    journal_config_type = fields.Many2one('journal.config.type', 'Type', default=_default_config_type, readonly=True, states={'draft': [('readonly', False)]})
    reverse_charge = fields.Boolean('Reverse Charge', readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('journal_config_type')
    def onchange_journal_config_type(self):
        if self.journal_config_type:
            self.journal_id = self.journal_config_type.journal_id.id
            self.account_id = self.journal_config_type.journal_id.default_debit_account_id.id
        else:
            self.journal_id = self._default_journal()

    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        super(AccountInvoice, self)._compute_residual()
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        if self.reverse_charge:
            residual = self.residual - self.amount_tax
            self.residual_signed = abs(residual) * sign
            self.residual = abs(residual)

    @api.multi
    def action_invoice_open(self):
        if not self.reverse_charge:
            return super(AccountInvoice, self).action_invoice_open()
        if not self.company_id.rc_vat_account_id:
            raise Warning(_('Define Reverse Charge Vat in Company!'))
        list_data = []
        account_tax_obj = self.env['account.tax']
        for tax_line in self.tax_line_ids:
            list_data.append((0, 0, {
                'name': tax_line.name,
                'partner_id': self.partner_id.parent_id.id or self.partner_id.id,
                'account_id': tax_line.account_id.id,
                'debit': tax_line.amount_total,
                'move_id': False,
                'invoice_id': self.id,
                'tax_line_id': account_tax_obj.search([('name', 'ilike', tax_line.name)]),
                'quantity': 1,
                }
            ))
        total_tax_amount = self.amount_tax
        self.invoice_line_ids.update({'invoice_line_tax_ids': [[6, 0, []]]})
        self.update({'tax_line_ids': [[6, 0, []]], 'amount_tax': 0.0})
        res = super(AccountInvoice, self).action_invoice_open()
        for move_line_id in list_data:
            move_line_id[2].update({'move_id': self.move_id.id})
        list_data.append((0, 0, {
                    'name': '/',
                    'partner_id': self.partner_id.parent_id.id or self.partner_id.id,
                    'account_id': self.company_id.rc_vat_account_id.id,
                    'credit': total_tax_amount,
                    'move_id': self.move_id.id,
                    'invoice_id': self.id,
                    'quantity': 1,
                    }
                ))
        self.move_id.state = 'draft'
        self.move_id.line_ids = list_data
        self.move_id.post()
        return res

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        self.journal_config_type = self.purchase_id.journal_config_type.id
        self.reverse_charge = self.purchase_id.reverse_charge,
        return super(AccountInvoice, self).purchase_order_change()

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        self.journal_id = self.journal_config_type.journal_id.id
        self.account_id = self.journal_config_type.journal_id.default_debit_account_id.id
        return res
