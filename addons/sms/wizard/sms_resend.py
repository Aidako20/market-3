#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,exceptions,fields,models


classSMSRecipient(models.TransientModel):
    _name='sms.resend.recipient'
    _description='ResendNotification'
    _rec_name='sms_resend_id'

    sms_resend_id=fields.Many2one('sms.resend',required=True)
    notification_id=fields.Many2one('mail.notification',required=True,ondelete='cascade')
    resend=fields.Boolean(string="Resend",default=True)
    failure_type=fields.Selection(
        related='notification_id.failure_type',related_sudo=True,readonly=True)
    partner_id=fields.Many2one('res.partner','Partner',related='notification_id.res_partner_id',readonly=True)
    partner_name=fields.Char('Recipient',readonly='True')
    sms_number=fields.Char('Number')


classSMSResend(models.TransientModel):
    _name='sms.resend'
    _description='SMSResend'
    _rec_name='mail_message_id'

    @api.model
    defdefault_get(self,fields):
        result=super(SMSResend,self).default_get(fields)
        if'recipient_ids'infieldsandresult.get('mail_message_id'):
            mail_message_id=self.env['mail.message'].browse(result['mail_message_id'])
            result['recipient_ids']=[(0,0,{
                'notification_id':notif.id,
                'resend':True,
                'failure_type':notif.failure_type,
                'partner_name':notif.res_partner_id.display_nameormail_message_id.record_name,
                'sms_number':notif.sms_number,
            })fornotifinmail_message_id.notification_idsifnotif.notification_type=='sms'andnotif.notification_statusin('exception','bounce')]
        returnresult

    mail_message_id=fields.Many2one('mail.message','Message',readonly=True,required=True)
    recipient_ids=fields.One2many('sms.resend.recipient','sms_resend_id',string='Recipients')
    has_cancel=fields.Boolean(compute='_compute_has_cancel')
    has_insufficient_credit=fields.Boolean(compute='_compute_has_insufficient_credit')
    has_unregistered_account=fields.Boolean(compute='_compute_has_unregistered_account')

    @api.depends("recipient_ids.failure_type")
    def_compute_has_unregistered_account(self):
        self.has_unregistered_account=self.recipient_ids.filtered(lambdap:p.failure_type=='sms_acc')

    @api.depends("recipient_ids.failure_type")
    def_compute_has_insufficient_credit(self):
        self.has_insufficient_credit=self.recipient_ids.filtered(lambdap:p.failure_type=='sms_credit')

    @api.depends("recipient_ids.resend")
    def_compute_has_cancel(self):
        self.has_cancel=self.recipient_ids.filtered(lambdap:notp.resend)

    def_check_access(self):
        ifnotself.mail_message_idornotself.mail_message_id.modelornotself.mail_message_id.res_id:
            raiseexceptions.UserError(_('Youdonothaveaccesstothemessageand/orrelateddocument.'))
        record=self.env[self.mail_message_id.model].browse(self.mail_message_id.res_id)
        record.check_access_rights('read')
        record.check_access_rule('read')

    defaction_resend(self):
        self._check_access()

        all_notifications=self.env['mail.notification'].sudo().search([
            ('mail_message_id','=',self.mail_message_id.id),
            ('notification_type','=','sms'),
            ('notification_status','in',('exception','bounce'))
        ])
        sudo_self=self.sudo()
        to_cancel_ids=[r.notification_id.idforrinsudo_self.recipient_idsifnotr.resend]
        to_resend_ids=[r.notification_id.idforrinsudo_self.recipient_idsifr.resend]

        ifto_cancel_ids:
            all_notifications.filtered(lambdan:n.idinto_cancel_ids).write({'notification_status':'canceled'})

        ifto_resend_ids:
            record=self.env[self.mail_message_id.model].browse(self.mail_message_id.res_id)

            sms_pid_to_number=dict((r.partner_id.id,r.sms_number)for rinself.recipient_idsifr.resendandr.partner_id)
            pids=list(sms_pid_to_number.keys())
            numbers=[r.sms_numberforrinself.recipient_idsifr.resendandnotr.partner_id]

            rdata=[]
            forpid,cid,active,pshare,ctype,notif,groupsinself.env['mail.followers']._get_recipient_data(record,'sms',False,pids=pids):
                ifpidandnotif=='sms':
                    rdata.append({'id':pid,'share':pshare,'active':active,'notif':notif,'groups':groupsor[],'type':'customer'ifpshareelse'user'})
            ifrdataornumbers:
                record._notify_record_by_sms(
                    self.mail_message_id,{'partners':rdata},check_existing=True,
                    sms_numbers=numbers,sms_pid_to_number=sms_pid_to_number,
                    put_in_queue=False
                )

        self.mail_message_id._notify_message_notification_update()
        return{'type':'ir.actions.act_window_close'}

    defaction_cancel(self):
        self._check_access()

        sudo_self=self.sudo()
        sudo_self.mapped('recipient_ids.notification_id').write({'notification_status':'canceled'})
        self.mail_message_id._notify_message_notification_update()
        return{'type':'ir.actions.act_window_close'}

    defaction_buy_credits(self):
        url=self.env['iap.account'].get_credits_url(service_name='sms')
        return{
            'type':'ir.actions.act_url',
            'url':url,
        }
