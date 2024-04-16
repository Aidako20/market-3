#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict
fromoperatorimportitemgetter

fromflectraimportexceptions,fields,models
fromflectra.toolsimportgroupby


classMailMessage(models.Model):
    """OverrideMailMessageclassinordertoaddanewtype:SMSmessages.
    Thosemessagescomeswiththeirownnotificationmethod,usingSMS
    gateway."""
    _inherit='mail.message'

    message_type=fields.Selection(selection_add=[
        ('sms','SMS')
    ],ondelete={'sms':lambdarecs:recs.write({'message_type':'email'})})
    has_sms_error=fields.Boolean(
        'HasSMSerror',compute='_compute_has_sms_error',search='_search_has_sms_error',
        help='Haserror')

    def_compute_has_sms_error(self):
        sms_error_from_notification=self.env['mail.notification'].sudo().search([
            ('notification_type','=','sms'),
            ('mail_message_id','in',self.ids),
            ('notification_status','=','exception')]).mapped('mail_message_id')
        formessageinself:
            message.has_sms_error=messageinsms_error_from_notification

    def_search_has_sms_error(self,operator,operand):
        ifoperator=='='andoperand:
            return['&',('notification_ids.notification_status','=','exception'),('notification_ids.notification_type','=','sms')]
        raiseNotImplementedError()

    defmessage_format(self):
        """OverrideinordertoretrievesdataaboutSMS(recipientnameand
            SMSstatus)

        TDEFIXME:cleantheoverallmessage_formatthingy
        """
        message_values=super(MailMessage,self).message_format()
        all_sms_notifications=self.env['mail.notification'].sudo().search([
            ('mail_message_id','in',[r['id']forrinmessage_values]),
            ('notification_type','=','sms')
        ])
        msgid_to_notif=defaultdict(lambda:self.env['mail.notification'].sudo())
        fornotifinall_sms_notifications:
            msgid_to_notif[notif.mail_message_id.id]+=notif

        formessageinmessage_values:
            customer_sms_data=[(notif.id,notif.res_partner_id.display_nameornotif.sms_number,notif.notification_status)fornotifinmsgid_to_notif.get(message['id'],[])]
            message['sms_ids']=customer_sms_data
        returnmessage_values
