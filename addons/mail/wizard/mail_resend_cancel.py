#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models


classMailResendCancel(models.TransientModel):
    _name='mail.resend.cancel'
    _description='Dismissnotificationforresendbymodel'

    model=fields.Char(string='Model')
    help_message=fields.Char(string='Helpmessage',compute='_compute_help_message')

    @api.depends('model')
    def_compute_help_message(self):
        forwizardinself:
            wizard.help_message=_("Areyousureyouwanttodiscard%smaildeliveryfailures?Youwon'tbeabletore-sendthesemailslater!")%(wizard._context.get('unread_counter'))

    defcancel_resend_action(self):
        author_id=self.env.user.partner_id.id
        forwizardinself:
            self._cr.execute("""
                                SELECTnotif.id,mes.id
                                FROMmail_message_res_partner_needaction_relnotif
                                JOINmail_messagemes
                                    ONnotif.mail_message_id=mes.id
                                WHEREnotif.notification_type='email'ANDnotif.notification_statusIN('bounce','exception')
                                    ANDmes.model=%s
                                    ANDmes.author_id=%s
                            """,(wizard.model,author_id))
            res=self._cr.fetchall()
            notif_ids=[row[0]forrowinres]
            messages_ids=list(set([row[1]forrowinres]))
            ifnotif_ids:
                self.env["mail.notification"].browse(notif_ids).sudo().write({'notification_status':'canceled'})
                self.env["mail.message"].browse(messages_ids)._notify_message_notification_update()
        return{'type':'ir.actions.act_window_close'}
