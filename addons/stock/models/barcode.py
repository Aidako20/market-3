#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classBarcodeRule(models.Model):
    _inherit='barcode.rule'

    type=fields.Selection(selection_add=[
        ('weight','WeightedProduct'),
        ('location','Location'),
        ('lot','Lot'),
        ('package','Package')
    ],ondelete={
        'weight':'setdefault',
        'location':'setdefault',
        'lot':'setdefault',
        'package':'setdefault',
    })
