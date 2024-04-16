#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_
fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.tools.float_utilsimportfloat_compare

importlogging
importpprint

_logger=logging.getLogger(__name__)


classTransferPaymentAcquirer(models.Model):
    _inherit='payment.acquirer'

    provider=fields.Selection(selection_add=[
        ('transfer','ManualPayment')
    ],default='transfer',ondelete={'transfer':'setdefault'})

    @api.model
    def_create_missing_journal_for_acquirers(self,company=None):
        #Bydefault,thewiretransfermethodusesthedefaultBankjournal.
        company=companyorself.env.company
        acquirers=self.env['payment.acquirer'].search(
            [('provider','=','transfer'),('journal_id','=',False),('company_id','=',company.id)])

        bank_journal=self.env['account.journal'].search(
            [('type','=','bank'),('company_id','=',company.id)],limit=1)
        ifbank_journal:
            acquirers.write({'journal_id':bank_journal.id})
        returnsuper(TransferPaymentAcquirer,self)._create_missing_journal_for_acquirers(company=company)

    deftransfer_get_form_action_url(self):
        return'/payment/transfer/feedback'

    def_format_transfer_data(self):
        company_id=self.env.company.id
        #filteronlybankaccountsmarkedasvisible
        journals=self.env['account.journal'].search([('type','=','bank'),('company_id','=',company_id)])
        accounts=journals.mapped('bank_account_id').name_get()
        bank_title=_('BankAccounts')iflen(accounts)>1else_('BankAccount')
        bank_accounts=''.join(['<ul>']+['<li>%s</li>'%nameforid,nameinaccounts]+['</ul>'])
        post_msg=_('''<div>
<h3>Pleaseusethefollowingtransferdetails</h3>
<h4>%(bank_title)s</h4>
%(bank_accounts)s
<h4>Communication</h4>
<p>Pleaseusetheordernameascommunicationreference.</p>
</div>''')%{
            'bank_title':bank_title,
            'bank_accounts':bank_accounts,
        }
        returnpost_msg

    @api.model
    defcreate(self,values):
        """Hookincreatetocreateadefaultpending_msg.Thisisdoneincreate
        tohaveaccesstothenameandothercreationvalues.Ifnopending_msg
        oravoidpending_msgisgivenatcreation,generateadefaultone."""
        ifvalues.get('provider')=='transfer'andnotvalues.get('pending_msg'):
            values['pending_msg']=self._format_transfer_data()
        returnsuper(TransferPaymentAcquirer,self).create(values)

    defwrite(self,values):
        """Hookinwritetocreateadefaultpending_msg.Seecreate()."""
        ifnotvalues.get('pending_msg',False)andall(notacquirer.pending_msgandacquirer.provider!='transfer'foracquirerinself)andvalues.get('provider')=='transfer':
            values['pending_msg']=self._format_transfer_data()
        returnsuper(TransferPaymentAcquirer,self).write(values)


classTransferPaymentTransaction(models.Model):
    _inherit='payment.transaction'

    @api.model
    def_transfer_form_get_tx_from_data(self,data):
        reference,amount,currency_name=data.get('reference'),data.get('amount'),data.get('currency_name')
        tx=self.search([('reference','=',reference)])

        ifnottxorlen(tx)>1:
            error_msg=_('receiveddataforreference%s')%(pprint.pformat(reference))
            ifnottx:
                error_msg+=_(';noorderfound')
            else:
                error_msg+=_(';multipleorderfound')
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        returntx

    def_transfer_form_get_invalid_parameters(self,data):
        invalid_parameters=[]

        iffloat_compare(float(data.get('amount')or'0.0'),self.amount,2)!=0:
            invalid_parameters.append(('amount',data.get('amount'),'%.2f'%self.amount))
        ifdata.get('currency')!=self.currency_id.name:
            invalid_parameters.append(('currency',data.get('currency'),self.currency_id.name))

        returninvalid_parameters

    def_transfer_form_validate(self,data):
        _logger.info('Validatedtransferpaymentfortx%s:setaspending'%(self.reference))
        self._set_transaction_pending()
        returnTrue
