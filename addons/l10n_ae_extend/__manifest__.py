# Part of Flectra. See LICENSE file for full copyright and licensing details.

{
    'name': 'U.A.E. - Accounting Extend',
    'author': 'Tech Receptives',
    'website': 'http://www.techreceptives.com',
    'category': 'Localization',
    'description': """
United Arab Emirates accounting chart and localization.
=======================================================

    """,
    'depends': ['l10n_ae', 'account_invoicing', 'sale_management', 'purchase'],
    'data': [
             'security/ir.model.access.csv',
             'data/journal_data.xml',
             'data/vat_config_type_data.xml',
             'views/report_vat_201_view.xml',
             'views/report_menu_view.xml',
             'views/vat_config_type.xml',
             'views/company_view.xml',
             'views/purchase_order_view.xml',
             'views/sale_order_view.xml',
             'views/account_invoice_view.xml',
             'wizard/vat_201_view.xml',
    ],
}
