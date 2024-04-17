# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields


class Challenge(models.Model):
_inherit = 'gamification.challenge'

challenge_category = fields.Selection(selection_add=[
('forum', 'Website / Forum')
], ondelete={'forum': 'set default'})
