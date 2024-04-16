#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models,tools


classMailCCMixin(models.AbstractModel):
    _name='mail.thread.cc'
    _inherit='mail.thread'
    _description='EmailCCmanagement'

    email_cc=fields.Char('Emailcc',help='Listofccfromincomingemails.')

    def_mail_cc_sanitized_raw_dict(self,cc_string):
        '''returnadictofsanitize_email:raw_emailfromastringofcc'''
        ifnotcc_string:
            return{}
        return{tools.email_normalize(email):tools.formataddr((name,tools.email_normalize(email)))
            for(name,email)intools.email_split_tuples(cc_string)}

    @api.model
    defmessage_new(self,msg_dict,custom_values=None):
        ifcustom_valuesisNone:
            custom_values={}
        cc_values={
            'email_cc':",".join(self._mail_cc_sanitized_raw_dict(msg_dict.get('cc')).values()),
        }
        cc_values.update(custom_values)
        returnsuper(MailCCMixin,self).message_new(msg_dict,cc_values)

    defmessage_update(self,msg_dict,update_vals=None):
        '''Addsccemailtoself.email_ccwhiletryingtokeepemailasrawaspossiblebutunique'''
        ifupdate_valsisNone:
            update_vals={}
        cc_values={}
        new_cc=self._mail_cc_sanitized_raw_dict(msg_dict.get('cc'))
        ifnew_cc:
            old_cc=self._mail_cc_sanitized_raw_dict(self.email_cc)
            new_cc.update(old_cc)
            cc_values['email_cc']=",".join(new_cc.values())
        cc_values.update(update_vals)
        returnsuper(MailCCMixin,self).message_update(msg_dict,cc_values)

    def_message_get_suggested_recipients(self):
        recipients=super(MailCCMixin,self)._message_get_suggested_recipients()
        forrecordinself:
            ifrecord.email_cc:
                foremailintools.email_split_and_format(record.email_cc):
                    record._message_add_suggested_recipient(recipients,email=email,reason=_('CCEmail'))
        returnrecipients
