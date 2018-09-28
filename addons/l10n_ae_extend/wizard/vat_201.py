# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class Vat201Report(models.TransientModel):

    _name = "vat.201.report"
    _description = "Vat 201"

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(related='company_id.currency_id')

    def print_report(self, data):
        data['form'] = self.read(['date_from', 'date_to', 'company_id', 'currency_id'])[0]
        # data['form']['currency_id'] = self.env.user.company_id.currency_id
        # data['date_from'] = form_data['date_from'] or False
        # data['date_to'] = form_data['date_to'] or False
        print("=====data======", data)

        # invoices = self.env['account.invoice'].search([('date_invoice', '<=', self.date_to), ('date_invoice', '>=', self.date_from)])
        # data['invoices'] = invoices
        return self.env.ref('l10n_ae_extend.action_report_vat_201').report_action(self, data=data)