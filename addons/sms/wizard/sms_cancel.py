#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models


classSMSCancel(models.TransientModel):
    _name='sms.cancel'
    _description='Dismissnotificationforresendbymodel'

    model=fields.Char(string='Model',required=True)
    help_message=fields.Char(string='Helpmessage',compute='_compute_help_message')

    @api.depends('model')
    def_compute_help_message(self):
        forwizardinself:
            wizard.help_message=_("Areyousureyouwanttodiscard%sSMSdeliveryfailures?Youwon'tbeabletore-sendtheseSMSlater!")%(wizard._context.get('unread_counter'))

    defaction_cancel(self):
        #TDECHECK:deletependingSMS
        author_id=self.env.user.partner_id.id
        forwizardinself:
            self._cr.execute("""
SELECTnotif.id,msg.id
FROMmail_message_res_partner_needaction_relnotif
JOINmail_messagemsg
    ONnotif.mail_message_id=msg.id
WHEREnotif.notification_type='sms'ISTRUEANDnotif.notification_statusIN('bounce','exception')
    ANDmsg.model=%s
    ANDmsg.author_id=%s""",(wizard.model,author_id))
            res=self._cr.fetchall()
            notif_ids=[row[0]forrowinres]
            message_ids=list(set([row[1]forrowinres]))
            ifnotif_ids:
                self.env['mail.notification'].browse(notif_ids).sudo().write({'notification_status':'canceled'})
            ifmessage_ids:
                self.env['mail.message'].browse(message_ids)._notify_message_notification_update()
        return{'type':'ir.actions.act_window_close'}
