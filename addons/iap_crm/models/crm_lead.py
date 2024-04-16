#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classLead(models.Model):
    _inherit='crm.lead'

    reveal_id=fields.Char(string='RevealID',help="TechnicalIDofrevealrequestdonebyIAP.")
