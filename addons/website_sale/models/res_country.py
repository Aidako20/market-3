# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models


class ResCountry(models.Model):
_inherit = 'res.country'

def get_website_sale_countries(self, mode='billing'):
return self.sudo().search([])

def get_website_sale_states(self, mode='billing'):
return self.sudo().state_ids
