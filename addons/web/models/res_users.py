# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import _, api, exceptions, fields, models, modules
from flectra.http import request

layouts = [
    ('chatter_bottom', 'Bottom'),
    ('chatter_sidebar', 'Sidebar'),
]

class Users(models.Model):
    """ Update of res.users class
        - add a preference for two or one column chatter layout
    """
    _name = 'res.users'
    _inherit = ['res.users']

    chatter_layout = fields.Selection(layouts, string='Chatter Layout', default=layouts[0][0])

    @api.onchange('chatter_layout')
    def change_chatter_layout(self):
        layout = {
            'chatter_sidebar': ['web.chatter_sidebar_layout'],
        }
        old_layout = self._origin.chatter_layout
        new_layout = self.chatter_layout

        def set_active(ids, active):
            if ids:
                real_ids = self.get_view_ids(ids)
                request.env['ir.ui.view'].with_context(
                    active_test=True).browse(real_ids).write(
                    {'active': active})

        if old_layout == 'chatter_sidebar' and new_layout == 'chatter_bottom':
            set_active(layout[old_layout], False)

        if new_layout == 'chatter_sidebar':
            set_active(layout[new_layout], True)

    def get_view_ids(self, xml_ids):
        ids = []
        for xml_id in xml_ids:
            if "." in xml_id:
                record_id = request.env.ref(xml_id).id
            else:
                record_id = int(xml_id)
            ids.append(record_id)
        return ids
