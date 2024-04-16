#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classMailMail(models.Model):
    _inherit='mail.mail'

    fetchmail_server_id=fields.Many2one('fetchmail.server',"InboundMailServer",readonly=True,index=True)
