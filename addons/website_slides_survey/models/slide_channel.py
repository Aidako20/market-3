#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classChannel(models.Model):
    _inherit='slide.channel'

    nbr_certification=fields.Integer("NumberofCertifications",compute='_compute_slides_statistics',store=True)
