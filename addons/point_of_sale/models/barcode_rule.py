#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields
fromflectra.tools.translateimport_


classBarcodeRule(models.Model):
    _inherit='barcode.rule'

    type=fields.Selection(selection_add=[
        ('weight','WeightedProduct'),
        ('price','PricedProduct'),
        ('discount','DiscountedProduct'),
        ('client','Client'),
        ('cashier','Cashier')
    ],ondelete={
        'weight':'setdefault',
        'price':'setdefault',
        'discount':'setdefault',
        'client':'setdefault',
        'cashier':'setdefault',
    })
