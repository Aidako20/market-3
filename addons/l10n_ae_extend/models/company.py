# Part of Flectra. See LICENSE file for full copyright and licensing details.


from flectra import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    rc_vat_account_id = fields.Many2one('account.account', 'Reverse Charge Account', required=True)
