#coding:utf-8
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
fromuuidimportuuid4

fromflectraimportapi,exceptions,fields,models,_


classPaymentAcquirerTest(models.Model):
    _inherit='payment.acquirer'

    provider=fields.Selection(selection_add=[
        ('test','Test')
    ],ondelete={'test':'setdefault'})

    @api.model
    defcreate(self,values):
        ifvalues.get('provider')=='test'and'state'invaluesandvalues.get('state')notin('test','disabled'):
            raiseexceptions.UserError(_('Thisacquirershouldnotbeusedforotherpurposesthantesting.'))
        returnsuper(PaymentAcquirerTest,self).create(values)

    defwrite(self,values):
        ifany(rec.provider=='test'forrecinself)and'state'invaluesandvalues.get('state')notin('test','disabled'):
            raiseexceptions.UserError(_('Thisacquirershouldnotbeusedforotherpurposesthantesting.'))
        returnsuper(PaymentAcquirerTest,self).write(values)

    @api.model
    deftest_s2s_form_process(self,data):
        """Returnaminimaltokentoallowproceedingtotransactioncreation."""
        payment_token=self.env['payment.token'].sudo().create({
            'acquirer_ref':uuid4(),
            'acquirer_id':int(data['acquirer_id']),
            'partner_id':int(data['partner_id']),
            'name':'Test-XXXXXXXXXXXX%s-%s'%(data['cc_number'][-4:],data['cc_holder_name'])
        })
        returnpayment_token


classPaymentTransactionTest(models.Model):
    _inherit='payment.transaction'

    deftest_create(self,values):
        """Automaticallysetthetransactionassuccessfuluponcreation."""
        return{'date':datetime.now(),'state':'done'}

    deftest_s2s_do_transaction(self,**kwargs):
        self.execute_callback()
