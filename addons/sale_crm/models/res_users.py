#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResUsers(models.Model):
    _inherit='res.users'

    target_sales_invoiced=fields.Integer('InvoicedinSalesOrdersTarget')
