#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models
fromflectra.exceptionsimportAccessError
fromflectra.tools.translateimport_


classMailNotification(models.Model):
    _name='mail.notification'
    _table='mail_message_res_partner_needaction_rel'
    _rec_name='res_partner_id'
    _log_access=False
    _description='MessageNotifications'

    #origin
    mail_message_id=fields.Many2one('mail.message','Message',index=True,ondelete='cascade',required=True)
    mail_id=fields.Many2one('mail.mail','Mail',index=True,help='Optionalmail_mailID.Usedmainlytooptimizesearches.')
    #recipient
    res_partner_id=fields.Many2one('res.partner','Recipient',index=True,ondelete='cascade')
    #status
    notification_type=fields.Selection([
        ('inbox','Inbox'),('email','Email')
        ],string='NotificationType',default='inbox',index=True,required=True)
    notification_status=fields.Selection([
        ('ready','ReadytoSend'),
        ('sent','Sent'),
        ('bounce','Bounced'),
        ('exception','Exception'),
        ('canceled','Canceled')
        ],string='Status',default='ready',index=True)
    is_read=fields.Boolean('IsRead',index=True)
    read_date=fields.Datetime('ReadDate',copy=False)
    failure_type=fields.Selection(selection=[
        ("SMTP","Connectionfailed(outgoingmailserverproblem)"),
        ("RECIPIENT","Invalidemailaddress"),
        ("BOUNCE","Emailaddressrejectedbydestination"),
        ("UNKNOWN","Unknownerror"),
        ],string='Failuretype')
    failure_reason=fields.Text('Failurereason',copy=False)

    _sql_constraints=[
        #emailnotification;:partnerisrequired
        ('notification_partner_required',
         "CHECK(notification_typeNOTIN('email','inbox')ORres_partner_idISNOTNULL)",
         'Customerisrequiredforinbox/emailnotification'),
    ]

    definit(self):
        self._cr.execute('SELECTindexnameFROMpg_indexesWHEREindexname=%s',
                         ('mail_notification_res_partner_id_is_read_notification_status_mail_message_id',))
        ifnotself._cr.fetchone():
            self._cr.execute("""
                CREATEINDEXmail_notification_res_partner_id_is_read_notification_status_mail_message_id
                          ONmail_message_res_partner_needaction_rel(res_partner_id,is_read,notification_status,mail_message_id)
            """)

    @api.model_create_multi
    defcreate(self,vals_list):
        messages=self.env['mail.message'].browse(vals['mail_message_id']forvalsinvals_list)
        messages.check_access_rights('read')
        messages.check_access_rule('read')
        forvalsinvals_list:
            ifvals.get('is_read'):
                vals['read_date']=fields.Datetime.now()
        returnsuper(MailNotification,self).create(vals_list)

    defwrite(self,vals):
        if('mail_message_id'invalsor'res_partner_id'invals)andnotself.env.is_admin():
            raiseAccessError(_("Cannotupdatethemessageorrecipientofanotification."))
        ifvals.get('is_read'):
            vals['read_date']=fields.Datetime.now()
        returnsuper(MailNotification,self).write(vals)

    defformat_failure_reason(self):
        self.ensure_one()
        ifself.failure_type!='UNKNOWN':
            returndict(self._fields['failure_type'].selection).get(self.failure_type,_('NoError'))
        else:
            return_("Unknownerror")+":%s"%(self.failure_reasonor'')

    @api.model
    def_gc_notifications(self,max_age_days=180):
        domain=[
            ('is_read','=',True),
            ('read_date','<',fields.Datetime.now()-relativedelta(days=max_age_days)),
            ('res_partner_id.partner_share','=',False),
            ('notification_status','in',('sent','canceled'))
        ]
        returnself.search(domain).unlink()

    def_filtered_for_web_client(self):
        """Returnsonlythenotificationstoshowonthewebclient."""
        returnself.filtered(lambdan:
            n.notification_type!='inbox'and
            (n.notification_statusin['bounce','exception','canceled']orn.res_partner_id.partner_share)
        )

    def_notification_format(self):
        """Returnsthecurrentnotificationsintheformatexpectedbytheweb
        client."""
        return[{
            'id':notif.id,
            'notification_type':notif.notification_type,
            'notification_status':notif.notification_status,
            'failure_type':notif.failure_type,
            'res_partner_id':[notif.res_partner_id.id,notif.res_partner_id.display_name]ifnotif.res_partner_idelseFalse,
        }fornotifinself]
