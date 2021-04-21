# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
{
    'name': 'Test Main Flow',
    'version': '1.0',
    'category': 'Hidden/Tests',
    'description': """
This module will test the main workflow of Flectra.
It will install some main apps and will try to execute the most important actions.
""",
    'depends': ['web_tour', 'crm', 'sale_timesheet', 'purchase_stock', 'mrp', 'account'],
    'data': [
        'views/assets.xml',
    ],
    'installable': True,
    'post_init_hook': '_auto_install_enterprise_dependencies',
}
