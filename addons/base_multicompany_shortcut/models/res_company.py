import logging
from flectra import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    shortcut = fields.Char(
            string="Shortcut",
    )
