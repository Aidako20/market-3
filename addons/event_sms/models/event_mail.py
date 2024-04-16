#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classEventTypeMail(models.Model):
    _inherit='event.type.mail'

    notification_type=fields.Selection(selection_add=[
        ('sms','SMS')
    ],ondelete={'sms':'setdefault'})
    sms_template_id=fields.Many2one(
        'sms.template',string='SMSTemplate',
        domain=[('model','=','event.registration')],ondelete='restrict',
        help='ThisfieldcontainsthetemplateoftheSMSthatwillbeautomaticallysent')

    @api.model
    def_get_event_mail_fields_whitelist(self):
        returnsuper(EventTypeMail,self)._get_event_mail_fields_whitelist()+['sms_template_id']


classEventMailScheduler(models.Model):
    _inherit='event.mail'

    notification_type=fields.Selection(selection_add=[
        ('sms','SMS')
    ],ondelete={'sms':'setdefault'})
    sms_template_id=fields.Many2one(
        'sms.template',string='SMSTemplate',
        domain=[('model','=','event.registration')],ondelete='restrict',
        help='ThisfieldcontainsthetemplateoftheSMSthatwillbeautomaticallysent')

    defexecute(self):
        formailinself:
            now=fields.Datetime.now()
            ifmail.interval_type!='after_sub':
                #DonotsendSMSifthecommunicationwasscheduledbeforetheeventbuttheeventisover
                ifnotmail.mail_sentandmail.scheduled_date<=nowandmail.notification_type=='sms'and\
                        (mail.interval_type!='before_event'ormail.event_id.date_end>now)and\
                        mail.sms_template_id:
                    self.env['event.registration']._message_sms_schedule_mass(
                        template=mail.sms_template_id,
                        active_domain=[('event_id','=',mail.event_id.id),('state','!=','cancel')],
                        mass_keep_log=True
                    )
                    mail.write({'mail_sent':True})
        returnsuper(EventMailScheduler,self).execute()


classEventMailRegistration(models.Model):
    _inherit='event.mail.registration'

    defexecute(self):
        now=fields.Datetime.now()
        todo=self.filtered(lambdareg_mail:
            notreg_mail.mail_sentand\
            reg_mail.registration_id.statein['open','done']and\
            (reg_mail.scheduled_dateandreg_mail.scheduled_date<=now)and\
            reg_mail.scheduler_id.notification_type=='sms'
        )
        forreg_mailintodo:
            reg_mail.registration_id._message_sms_schedule_mass(
                template=reg_mail.scheduler_id.sms_template_id,
                mass_keep_log=True
            )
        todo.write({'mail_sent':True})

        returnsuper(EventMailRegistration,self).execute()
