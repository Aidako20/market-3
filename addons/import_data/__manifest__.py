{
    'name': 'Import Data for Partners, Invoices and Receipts',
    'summary': 'Import Data',
    'version': '1.0',
    'category': 'Custom',
    'author': 'FlectraHQ',
    'website': 'https://flectrahq.com',
    'license': 'LGPL-3',
    'depends': ['l10n_in', 'account_invoicing'],
    'data': [
            'data/res.partner.csv',
            'data/res.partner-cust_demo.csv',
            'data/product.category.csv',
            'data/product.product.csv',
            'data/account.invoice.csv',
            'data/account.payment.csv'
             ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True
}
