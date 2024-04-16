#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_


classAlias(models.Model):
    _inherit='mail.alias'

    alias_contact=fields.Selection(selection_add=[
        ('employees','AuthenticatedEmployees'),
    ],ondelete={'employees':'cascade'})

    def_get_alias_bounced_body_fallback(self,message_dict):
        ifself.alias_contact=='employees':
            return_("""Hi,<br/>
Yourdocumenthasnotbeencreatedbecauseyouremailaddressisnotrecognized.<br/>
Pleasesendemailswiththeemailaddressrecordedonyouremployeeinformation,orcontactyourHRmanager.""")
        returnsuper(Alias,self)._get_alias_bounced_body_fallback(message_dict)
