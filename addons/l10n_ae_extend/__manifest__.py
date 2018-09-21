# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2014 Tech Receptives (<http://techreceptives.com>)

{
    'name': 'U.A.E. - Accounting Extend',
    'author': 'Tech Receptives',
    'website': 'http://www.techreceptives.com',
    'category': 'Localization',
    'description': """
United Arab Emirates accounting chart and localization.
=======================================================

    """,
    'depends': ['account_invoicing', 'l10n_ae', 'sale_management', 'purchase'],
    'data': [
             'data/journal_data.xml',
             'data/config_type_data.xml',
             'views/config_type.xml',
             'views/company_view.xml',
             'views/purchase_order_view.xml',
             'views/sale_order_view.xml',
             'views/account_invoice_view.xml',
    ],
}
