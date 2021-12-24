# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields


class Users(models.Model):
    _inherit = 'res.users'

    flectrabot_state = fields.Selection(selection_add=[
        ('onboarding_canned', 'Onboarding canned'),
    ], ondelete={'onboarding_canned': lambda users: users.write({'flectrabot_state': 'disabled'})})
