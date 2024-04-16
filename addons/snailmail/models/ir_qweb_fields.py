#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,models


classContact(models.AbstractModel):
    _inherit='ir.qweb.field.contact'

    @api.model
    defvalue_to_html(self,value,options):
        ifself.env.context.get('snailmail_layout'):
           value=value.with_context(snailmail_layout=self.env.context['snailmail_layout'])
        returnsuper(Contact,self).value_to_html(value,options)

    @api.model
    defrecord_to_html(self,record,field_name,options):
        ifself.env.context.get('snailmail_layout'):
           record=record.with_context(snailmail_layout=self.env.context['snailmail_layout'])
        returnsuper(Contact,self).record_to_html(record,field_name,options)
