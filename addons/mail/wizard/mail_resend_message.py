#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classMailResendMessage(models.TransientModel):
    _name='mail.resend.message'
    _description='Emailresendwizard'

    mail_message_id=fields.Many2one('mail.message','Message',readonly=True)
    partner_ids=fields.One2many('mail.resend.partner','resend_wizard_id',string='Recipients')
    notification_ids=fields.Many2many('mail.notification',string='Notifications',readonly=True)
    has_cancel=fields.Boolean(compute='_compute_has_cancel')
    partner_readonly=fields.Boolean(compute='_compute_partner_readonly')

    @api.depends("partner_ids")
    def_compute_has_cancel(self):
        self.has_cancel=self.partner_ids.filtered(lambdap:notp.resend)

    def_compute_partner_readonly(self):
        self.partner_readonly=notself.env['res.partner'].check_access_rights('write',raise_exception=False)

    @api.model
    defdefault_get(self,fields):
        rec=super(MailResendMessage,self).default_get(fields)
        message_id=self._context.get('mail_message_to_resend')
        ifmessage_id:
            mail_message_id=self.env['mail.message'].browse(message_id)
            notification_ids=mail_message_id.notification_ids.filtered(lambdanotif:notif.notification_type=='email'andnotif.notification_statusin('exception','bounce'))
            partner_ids=[(0,0,{
                "partner_id":notif.res_partner_id.id,
                "name":notif.res_partner_id.name,
                "email":notif.res_partner_id.email,
                "resend":True,
                "message":notif.format_failure_reason(),
            })fornotifinnotification_ids]
            has_user=any(notif.res_partner_id.user_idsfornotifinnotification_ids)
            ifhas_user:
                partner_readonly=notself.env['res.users'].check_access_rights('write',raise_exception=False)
            else:
                partner_readonly=notself.env['res.partner'].check_access_rights('write',raise_exception=False)
            rec['partner_readonly']=partner_readonly
            rec['notification_ids']=[(6,0,notification_ids.ids)]
            rec['mail_message_id']=mail_message_id.id
            rec['partner_ids']=partner_ids
        else:
            raiseUserError(_('Nomessage_idfoundincontext'))
        returnrec

    defresend_mail_action(self):
        """Processthewizardcontentandproceedwithsendingtherelated
            email(s),renderinganytemplatepatternsontheflyifneeded."""
        forwizardinself:
            "Ifapartnerdisappearedfrompartnerlist,wecancelthenotification"
            to_cancel=wizard.partner_ids.filtered(lambdap:notp.resend).mapped("partner_id")
            to_send=wizard.partner_ids.filtered(lambdap:p.resend).mapped("partner_id")
            notif_to_cancel=wizard.notification_ids.filtered(lambdanotif:notif.notification_type=='email'andnotif.res_partner_idinto_cancelandnotif.notification_statusin('exception','bounce'))
            notif_to_cancel.sudo().write({'notification_status':'canceled'})
            ifto_send:
                message=wizard.mail_message_id
                record=self.env[message.model].browse(message.res_id)ifmessage.is_thread_message()elseself.env['mail.thread']

                email_partners_data=[]
                forpid,cid,active,pshare,ctype,notif,groupsinself.env['mail.followers']._get_recipient_data(None,'comment',False,pids=to_send.ids):
                    ifpidandnotif=='email'ornotnotif:
                        pdata={'id':pid,'share':pshare,'active':active,'notif':'email','groups':groupsor[]}
                        ifnotpshareandnotif: #hasanuserandisnotshared,isthereforeuser
                            email_partners_data.append(dict(pdata,type='user'))
                        elifpshareandnotif: #hasanuserandisshared,isthereforeportal
                            email_partners_data.append(dict(pdata,type='portal'))
                        else: #hasnouser,isthereforecustomer
                            email_partners_data.append(dict(pdata,type='customer'))

                record._notify_record_by_email(message,{'partners':email_partners_data},check_existing=True,send_after_commit=False)

            self.mail_message_id._notify_message_notification_update()
        return{'type':'ir.actions.act_window_close'}

    defcancel_mail_action(self):
        forwizardinself:
            fornotifinwizard.notification_ids:
                notif.filtered(lambdanotif:notif.notification_type=='email'andnotif.notification_statusin('exception','bounce')).sudo().write({'notification_status':'canceled'})
            wizard.mail_message_id._notify_message_notification_update()
        return{'type':'ir.actions.act_window_close'}


classPartnerResend(models.TransientModel):
    _name='mail.resend.partner'
    _description='Partnerwithadditionalinformationformailresend'

    partner_id=fields.Many2one('res.partner',string='Partner',required=True,ondelete='cascade')
    name=fields.Char(related="partner_id.name",related_sudo=False,readonly=False)
    email=fields.Char(related="partner_id.email",related_sudo=False,readonly=False)
    resend=fields.Boolean(string="SendAgain",default=True)
    resend_wizard_id=fields.Many2one('mail.resend.message',string="Resendwizard")
    message=fields.Char(string="Helpmessage")
