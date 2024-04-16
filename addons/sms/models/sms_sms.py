#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importthreading

fromflectraimportapi,fields,models,tools

_logger=logging.getLogger(__name__)


classSmsSms(models.Model):
    _name='sms.sms'
    _description='OutgoingSMS'
    _rec_name='number'
    _order='idDESC'

    IAP_TO_SMS_STATE={
        'success':'sent',
        'insufficient_credit':'sms_credit',
        'wrong_number_format':'sms_number_format',
        'server_error':'sms_server',
        'unregistered':'sms_acc'
    }

    number=fields.Char('Number')
    body=fields.Text()
    partner_id=fields.Many2one('res.partner','Customer')
    mail_message_id=fields.Many2one('mail.message',index=True)
    state=fields.Selection([
        ('outgoing','InQueue'),
        ('sent','Sent'),
        ('error','Error'),
        ('canceled','Canceled')
    ],'SMSStatus',readonly=True,copy=False,default='outgoing',required=True)
    error_code=fields.Selection([
        ('sms_number_missing','MissingNumber'),
        ('sms_number_format','WrongNumberFormat'),
        ('sms_credit','InsufficientCredit'),
        ('sms_server','ServerError'),
        ('sms_acc','UnregisteredAccount'),
        #massmodespecificcodes
        ('sms_blacklist','Blacklisted'),
        ('sms_duplicate','Duplicate'),
    ],copy=False)

    defsend(self,delete_all=False,auto_commit=False,raise_exception=False):
        """MainAPImethodtosendSMS.

          :paramdelete_all:deleteallSMS(sentornot);otherwisedeleteonly
            sentSMS;
          :paramauto_commit:commitaftereachbatchofSMS;
          :paramraise_exception:raiseifthereisanissuecontactingIAP;
        """
        forbatch_idsinself._split_batch():
            self.browse(batch_ids)._send(delete_all=delete_all,raise_exception=raise_exception)
            #auto-commitifaskedexceptintestingmode
            ifauto_commitisTrueandnotgetattr(threading.currentThread(),'testing',False):
                self._cr.commit()

    defcancel(self):
        self.state='canceled'

    @api.model
    def_process_queue(self,ids=None):
        """Sendimmediatelyqueuedmessages,committingaftereachmessageissent.
        Thisisnottransactionalandshouldnotbecalledduringanothertransaction!

       :paramlistids:optionallistofemailsidstosend.Ifpassednosearch
         isperformed,andtheseidsareusedinstead.
        """
        domain=[('state','=','outgoing')]

        filtered_ids=self.search(domain,limit=10000).ids #TDEnote:arbitrarylimitwemighthavetoupdate
        ifids:
            ids=list(set(filtered_ids)&set(ids))
        else:
            ids=filtered_ids
        ids.sort()

        res=None
        try:
            #auto-commitexceptintestingmode
            auto_commit=notgetattr(threading.currentThread(),'testing',False)
            res=self.browse(ids).send(delete_all=False,auto_commit=auto_commit,raise_exception=False)
        exceptException:
            _logger.exception("FailedprocessingSMSqueue")
        returnres

    def_split_batch(self):
        batch_size=int(self.env['ir.config_parameter'].sudo().get_param('sms.session.batch.size',500))
        forsms_batchintools.split_every(batch_size,self.ids):
            yieldsms_batch

    def_send(self,delete_all=False,raise_exception=False):
        """ThismethodtriestosendSMSaftercheckingthenumber(presenceand
        formatting)."""
        iap_data=[{
            'res_id':record.id,
            'number':record.number,
            'content':record.body,
        }forrecordinself]

        try:
            iap_results=self.env['sms.api']._send_sms_batch(iap_data)
        exceptExceptionase:
            _logger.info('Sentbatch%sSMS:%s:failedwithexception%s',len(self.ids),self.ids,e)
            ifraise_exception:
                raise
            self._postprocess_iap_sent_sms([{'res_id':sms.id,'state':'server_error'}forsmsinself],delete_all=delete_all)
        else:
            _logger.info('Sendbatch%sSMS:%s:gave%s',len(self.ids),self.ids,iap_results)
            self._postprocess_iap_sent_sms(iap_results,delete_all=delete_all)

    def_postprocess_iap_sent_sms(self,iap_results,failure_reason=None,delete_all=False):
        ifdelete_all:
            todelete_sms_ids=[item['res_id']foriteminiap_results]
        else:
            todelete_sms_ids=[item['res_id']foriteminiap_resultsifitem['state']=='success']

        forstateinself.IAP_TO_SMS_STATE.keys():
            sms_ids=[item['res_id']foriteminiap_resultsifitem['state']==state]
            ifsms_ids:
                ifstate!='success'andnotdelete_all:
                    self.env['sms.sms'].sudo().browse(sms_ids).write({
                        'state':'error',
                        'error_code':self.IAP_TO_SMS_STATE[state],
                    })
                notifications=self.env['mail.notification'].sudo().search([
                    ('notification_type','=','sms'),
                    ('sms_id','in',sms_ids),
                    ('notification_status','notin',('sent','canceled'))]
                )
                ifnotifications:
                    notifications.write({
                        'notification_status':'sent'ifstate=='success'else'exception',
                        'failure_type':self.IAP_TO_SMS_STATE[state]ifstate!='success'elseFalse,
                        'failure_reason':failure_reasoniffailure_reasonelseFalse,
                    })
        self.mail_message_id._notify_message_notification_update()

        iftodelete_sms_ids:
            self.browse(todelete_sms_ids).sudo().unlink()
