#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importrandom
importstring

fromflectraimportapi,fields,models
fromflectra.osvimportexpression


classMailingTrace(models.Model):
    """ImprovestatisticsmodeltoaddSMSsupport.Mainattributesof
    statisticsmodelareused,onlysomespecificdataisrequired."""
    _inherit='mailing.trace'
    CODE_SIZE=3

    trace_type=fields.Selection(selection_add=[
        ('sms','SMS')
    ],ondelete={'sms':'setdefault'})
    sms_sms_id=fields.Many2one('sms.sms',string='SMS',index=True,ondelete='setnull')
    sms_sms_id_int=fields.Integer(
        string='SMSID(tech)',
        help='IDoftherelatedsms.sms.Thisfieldisanintegerfieldbecause'
             'therelatedsms.smscanbedeletedseparatelyfromitsstatistics.'
             'HowevertheIDisneededforseveralactionandcontrollers.',
        index=True,
    )
    sms_number=fields.Char('Number')
    sms_code=fields.Char('Code')
    failure_type=fields.Selection(selection_add=[
        ('sms_number_missing','MissingNumber'),
        ('sms_number_format','WrongNumberFormat'),
        ('sms_credit','InsufficientCredit'),
        ('sms_server','ServerError'),
        ('sms_acc','UnregisteredAccount'),
        #massmodespecificcodes
        ('sms_blacklist','Blacklisted'),
        ('sms_duplicate','Duplicate'),
    ])

    @api.model_create_multi
    defcreate(self,values_list):
        forvaluesinvalues_list:
            if'sms_sms_id'invalues:
                values['sms_sms_id_int']=values['sms_sms_id']
            ifvalues.get('trace_type')=='sms'andnotvalues.get('sms_code'):
                values['sms_code']=self._get_random_code()
        returnsuper(MailingTrace,self).create(values_list)

    def_get_random_code(self):
        """Generatearandomcodefortrace.Uniquenessisnotreallynecessary
        asitservesasobfuscationwhenunsubscribing.Avalidtrio
        code/mailing_id/numberwillberequested."""
        return''.join(random.choice(string.ascii_letters+string.digits)fordummyinrange(self.CODE_SIZE))

    def_get_records_from_sms(self,sms_sms_ids=None,additional_domain=None):
        ifnotself.idsandsms_sms_ids:
            domain=[('sms_sms_id_int','in',sms_sms_ids)]
        else:
            domain=[('id','in',self.ids)]
        ifadditional_domain:
            domain=expression.AND([domain,additional_domain])
        returnself.search(domain)

    defset_failed(self,failure_type):
        fortraceinself:
            trace.write({'exception':fields.Datetime.now(),'failure_type':failure_type})

    defset_sms_sent(self,sms_sms_ids=None):
        statistics=self._get_records_from_sms(sms_sms_ids,[('sent','=',False)])
        statistics.write({'sent':fields.Datetime.now()})
        returnstatistics

    defset_sms_clicked(self,sms_sms_ids=None):
        statistics=self._get_records_from_sms(sms_sms_ids,[('clicked','=',False)])
        statistics.write({'clicked':fields.Datetime.now()})
        returnstatistics

    defset_sms_ignored(self,sms_sms_ids=None):
        statistics=self._get_records_from_sms(sms_sms_ids,[('ignored','=',False)])
        statistics.write({'ignored':fields.Datetime.now()})
        returnstatistics

    defset_sms_exception(self,sms_sms_ids=None):
        statistics=self._get_records_from_sms(sms_sms_ids,[('exception','=',False)])
        statistics.write({'exception':fields.Datetime.now()})
        returnstatistics
