#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,tools,_


classBaseModel(models.AbstractModel):
    _inherit='base'

    def_alias_get_error_message(self,message,message_dict,alias):
        ifalias.alias_contact=='employees':
            email_from=tools.decode_message_header(message,'From')
            email_address=tools.email_split(email_from)[0]
            employee=self.env['hr.employee'].search([('work_email','ilike',email_address)],limit=1)
            ifnotemployee:
                employee=self.env['hr.employee'].search([('user_id.email','ilike',email_address)],limit=1)
            ifnotemployee:
                return_('restrictedtoemployees')
            returnFalse
        returnsuper(BaseModel,self)._alias_get_error_message(message,message_dict,alias)
