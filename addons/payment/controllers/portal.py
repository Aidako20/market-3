#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importhashlib
importhmac
importlogging
fromunicodedataimportnormalize
importpsycopg2
importwerkzeug

fromflectraimporthttp,_
fromflectra.httpimportrequest
fromflectra.osvimportexpression
fromflectra.toolsimportDEFAULT_SERVER_DATETIME_FORMAT,consteq,ustr
fromflectra.tools.float_utilsimportfloat_repr
fromdatetimeimportdatetime,timedelta


_logger=logging.getLogger(__name__)

classPaymentProcessing(http.Controller):

    @staticmethod
    defremove_payment_transaction(transactions):
        tx_ids_list=request.session.get("__payment_tx_ids__",[])
        iftransactions:
            fortxintransactions:
                iftx.idintx_ids_list:
                    tx_ids_list.remove(tx.id)
        else:
            returnFalse
        request.session["__payment_tx_ids__"]=tx_ids_list
        returnTrue

    @staticmethod
    defadd_payment_transaction(transactions):
        ifnottransactions:
            returnFalse
        tx_ids_list=set(request.session.get("__payment_tx_ids__",[]))|set(transactions.ids)
        request.session["__payment_tx_ids__"]=list(tx_ids_list)
        returnTrue

    @staticmethod
    defget_payment_transaction_ids():
        #returntheidsandnottherecordset,sincewemightneedto
        #sudothebrowsetoaccessalltherecord
        #Iprefertoletthecontrollerchosewhentoaccesstopayment.transactionusingsudo
        returnrequest.session.get("__payment_tx_ids__",[])

    @http.route(['/payment/process'],type="http",auth="public",website=True,sitemap=False)
    defpayment_status_page(self,**kwargs):
        #Whenthecustomerisredirecttothiswebsitepage,
        #weretrievethepaymenttransactionlistfromhissession
        tx_ids_list=self.get_payment_transaction_ids()
        payment_transaction_ids=request.env['payment.transaction'].sudo().browse(tx_ids_list).exists()

        render_ctx={
            'payment_tx_ids':payment_transaction_ids.ids,
        }
        returnrequest.render("payment.payment_process_page",render_ctx)

    @http.route(['/payment/process/poll'],type="json",auth="public")
    defpayment_status_poll(self):
        #retrievethetransactions
        tx_ids_list=self.get_payment_transaction_ids()

        payment_transaction_ids=request.env['payment.transaction'].sudo().search([
            ('id','in',list(tx_ids_list)),
            ('date','>=',(datetime.now()-timedelta(days=1)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
        ])
        ifnotpayment_transaction_ids:
            return{
                'success':False,
                'error':'no_tx_found',
            }

        processed_tx=payment_transaction_ids.filtered('is_processed')
        self.remove_payment_transaction(processed_tx)

        #createthereturneddictionnary
        result={
            'success':True,
            'transactions':[],
        }
        #populatethereturneddictionnarywiththetransactionsdata
        fortxinpayment_transaction_ids:
            message_to_display=tx.acquirer_id[tx.state+'_msg']iftx.statein['done','pending','cancel']elseNone
            tx_info={
                'reference':tx.reference,
                'state':tx.state,
                'return_url':tx.return_url,
                'is_processed':tx.is_processed,
                'state_message':tx.state_message,
                'message_to_display':message_to_display,
                'amount':tx.amount,
                'currency':tx.currency_id.name,
                'acquirer_provider':tx.acquirer_id.provider,
            }
            tx_info.update(tx._get_processing_info())
            result['transactions'].append(tx_info)

        tx_to_process=payment_transaction_ids.filtered(lambdax:x.state=='done'andx.is_processedisFalse)
        try:
            tx_to_process._post_process_after_done()
        exceptpsycopg2.OperationalErrorase:
            request.env.cr.rollback()
            result['success']=False
            result['error']="tx_process_retry"
        exceptExceptionase:
            request.env.cr.rollback()
            result['success']=False
            result['error']=str(e)
            _logger.exception("Errorwhileprocessingtransaction(s)%s,exception\"%s\"",tx_to_process.ids,str(e))

        returnresult

classWebsitePayment(http.Controller):
    @staticmethod
    def_get_acquirers_compatible_with_current_user(acquirers):
        #s2smodewillalwaysgenerateatoken,whichwedon'twantforpublicusers
        valid_flows=['form']ifrequest.env.user._is_public()else['form','s2s']
        return[acqforacqinacquirersifacq.payment_flowinvalid_flows]

    @http.route(['/my/payment_method'],type='http',auth="user",website=True)
    defpayment_method(self,**kwargs):
        acquirers=list(request.env['payment.acquirer'].search([
            ('state','in',['enabled','test']),('registration_view_template_id','!=',False),
            ('payment_flow','=','s2s'),('company_id','=',request.env.company.id)
        ]))
        partner=request.env.user.partner_id
        payment_tokens=partner.payment_token_ids
        payment_tokens|=partner.commercial_partner_id.sudo().payment_token_ids
        return_url=request.params.get('redirect','/my/payment_method')
        values={
            'pms':payment_tokens,
            'acquirers':acquirers,
            'error_message':[kwargs['error']]ifkwargs.get('error')elseFalse,
            'return_url':return_url,
            'bootstrap_formatting':True,
            'partner_id':partner.id
        }
        returnrequest.render("payment.pay_methods",values)

    @http.route(['/website_payment/pay'],type='http',auth='public',website=True,sitemap=False)
    defpay(self,reference='',order_id=None,amount=False,currency_id=None,acquirer_id=None,partner_id=False,access_token=None,**kw):
        """
        Genericpaymentpageallowingpublicandloggedinuserstopayanarbitraryamount.

        Inthecaseofapublicuseraccess,weneedtoensurethatthepaymentismadeanonymously-e.g.itshouldnotbe
        possibletopayforaspecificpartnersimplybysettingthepartner_idGETparamtoarandomid.Inthecasewhere
        apartner_idisset,wedoanaccess_tokencheckbasedonthepayment.link.wizardmodel(sincelinksforspecific
        partnersshouldbecreatedfromthereandthereonly).Alsonoteworthyisthefilteringofs2spaymentmethods-
        wedon'twanttocreatepaymenttokensforpublicusers.

        Inthecaseofaloggedinuser,thenweletaccessrightsandsecurityrulesdotheirjob.
        """
        env=request.env
        user=env.user.sudo()
        reference=normalize('NFKD',reference).encode('ascii','ignore').decode('utf-8')
        ifpartner_idandnotaccess_token:
            raisewerkzeug.exceptions.NotFound
        ifpartner_idandaccess_token:
            token_ok=request.env['payment.link.wizard'].check_token(access_token,int(partner_id),float(amount),int(currency_id))
            ifnottoken_ok:
                raisewerkzeug.exceptions.NotFound

        invoice_id=kw.get('invoice_id')

        #Defaultvalues
        values={
            'amount':0.0,
            'currency':user.company_id.currency_id,
        }

        #Checksaleorder
        iforder_id:
            try:
                order_id=int(order_id)
                ifpartner_id:
                    #`sudo`needediftheuserisnotconnected.
                    #Apublicuserwoudn'tbeabletoreadthesaleorder.
                    #With`partner_id`,anaccess_tokenshouldbevalidated,preventingadatabreach.
                    order=env['sale.order'].sudo().browse(order_id)
                else:
                    order=env['sale.order'].browse(order_id)
                values.update({
                    'currency':order.currency_id,
                    'amount':order.amount_total,
                    'order_id':order_id
                })
            except:
                order_id=None

        ifinvoice_id:
            try:
                values['invoice_id']=int(invoice_id)
            exceptValueError:
                invoice_id=None

        #Checkcurrency
        ifcurrency_id:
            try:
                currency_id=int(currency_id)
                values['currency']=env['res.currency'].browse(currency_id)
            except:
                pass

        #Checkamount
        ifamount:
            try:
                amount=float(amount)
                values['amount']=amount
            except:
                pass

        #Checkreference
        reference_values=order_idand{'sale_order_ids':[(4,order_id)]}or{}
        values['reference']=env['payment.transaction']._compute_reference(values=reference_values,prefix=reference)

        #Checkacquirer
        acquirers=None
        iforder_idandorder:
            cid=order.company_id.id
        elifkw.get('company_id'):
            try:
                cid=int(kw.get('company_id'))
            except:
                cid=user.company_id.id
        else:
            cid=user.company_id.id

        #Checkpartner
        ifnotuser._is_public():
            #NOTE:thismeansthatifthepartnerwassetintheGETparam,itgetsoverwrittenhere
            #Thisissomethingwewant,sincesecurityrulesarebasedonthepartner-assumingthe
            #access_tokencheckedoutatthestart,thisshouldhavenoimpactonthepaymentitself
            #existingbesidesmakingreconciliationpossiblymoredifficult(ifthepaymentpartneris
            #notthesameastheinvoicepartner,forexample)
            partner_id=user.partner_id.id
        elifpartner_id:
            partner_id=int(partner_id)

        values.update({
            'partner_id':partner_id,
            'bootstrap_formatting':True,
            'error_msg':kw.get('error_msg')
        })

        acquirer_domain=['&',('state','in',['enabled','test']),('company_id','=',cid)]
        ifpartner_id:
            partner=request.env['res.partner'].browse([partner_id])
            acquirer_domain=expression.AND([
            acquirer_domain,
            ['|',('country_ids','=',False),('country_ids','in',[partner.sudo().country_id.id])]
        ])
        ifacquirer_id:
            acquirers=env['payment.acquirer'].browse(int(acquirer_id))
        iforder_id:
            acquirers=env['payment.acquirer'].search(acquirer_domain)
        ifnotacquirers:
            acquirers=env['payment.acquirer'].search(acquirer_domain)

        values['acquirers']=self._get_acquirers_compatible_with_current_user(acquirers)
        ifpartner_id:
            values['pms']=request.env['payment.token'].search([
                ('acquirer_id','in',acquirers.ids),
                ('partner_id','child_of',partner.commercial_partner_id.id)
            ])
        else:
            values['pms']=[]


        returnrequest.render('payment.pay',values)

    @http.route(['/website_payment/transaction/<string:reference>/<string:amount>/<string:currency_id>',
                '/website_payment/transaction/v2/<string:amount>/<string:currency_id>/<path:reference>',
                '/website_payment/transaction/v2/<string:amount>/<string:currency_id>/<path:reference>/<int:partner_id>'],type='json',auth='public')
    deftransaction(self,acquirer_id,reference,amount,currency_id,partner_id=False,**kwargs):
        acquirer=request.env['payment.acquirer'].browse(acquirer_id)
        order_id=kwargs.get('order_id')
        invoice_id=kwargs.get('invoice_id')

        reference_values=order_idand{'sale_order_ids':[(4,order_id)]}or{}
        reference=request.env['payment.transaction']._compute_reference(values=reference_values,prefix=reference)

        values={
            'acquirer_id':int(acquirer_id),
            'reference':reference,
            'amount':float(amount),
            'currency_id':int(currency_id),
            'partner_id':partner_id,
            'type':'form_save'ifacquirer.save_token!='none'andpartner_idelse'form',
        }

        render_values={}
        iforder_id:
            values['sale_order_ids']=[(6,0,[order_id])]
            order=request.env['sale.order'].sudo().browse(order_id)
            render_values.update({
                'billing_partner_id':order.partner_invoice_id.id,
            })
        elifinvoice_id:
            values['invoice_ids']=[(6,0,[invoice_id])]

        reference_values=order_idand{'sale_order_ids':[(4,order_id)]}or{}
        reference_values.update(acquirer_id=int(acquirer_id))
        values['reference']=request.env['payment.transaction']._compute_reference(values=reference_values,prefix=reference)
        tx=request.env['payment.transaction'].sudo().with_context(lang=None).create(values)
        secret=request.env['ir.config_parameter'].sudo().get_param('database.secret')
        token_str='%s%s%s'%(tx.id,tx.reference,float_repr(tx.amount,precision_digits=tx.currency_id.decimal_places))
        token=hmac.new(secret.encode('utf-8'),token_str.encode('utf-8'),hashlib.sha256).hexdigest()
        tx.return_url='/website_payment/confirm?tx_id=%d&access_token=%s'%(tx.id,token)

        PaymentProcessing.add_payment_transaction(tx)

        render_values.update({
            'partner_id':partner_id,
            'type':tx.type,
        })

        returnacquirer.sudo().render(tx.reference,float(amount),int(currency_id),values=render_values)

    @http.route(['/website_payment/token/<string:reference>/<string:amount>/<string:currency_id>',
                '/website_payment/token/v2/<string:amount>/<string:currency_id>/<path:reference>',
                '/website_payment/token/v2/<string:amount>/<string:currency_id>/<path:reference>/<int:partner_id>'],type='http',auth='public',website=True)
    defpayment_token(self,pm_id,reference,amount,currency_id,partner_id=False,return_url=None,**kwargs):
        token=request.env['payment.token'].browse(int(pm_id))
        order_id=kwargs.get('order_id')
        invoice_id=kwargs.get('invoice_id')

        ifnottoken:
            returnrequest.redirect('/website_payment/pay?error_msg=%s'%_('Cannotsetupthepayment.'))

        values={
            'acquirer_id':token.acquirer_id.id,
            'reference':reference,
            'amount':float(amount),
            'currency_id':int(currency_id),
            'partner_id':int(partner_id),
            'payment_token_id':int(pm_id),
            'type':'server2server',
            'return_url':return_url,
        }

        iforder_id:
            values['sale_order_ids']=[(6,0,[int(order_id)])]
        ifinvoice_id:
            values['invoice_ids']=[(6,0,[int(invoice_id)])]

        tx=request.env['payment.transaction'].sudo().with_context(lang=None).create(values)
        PaymentProcessing.add_payment_transaction(tx)

        try:
            tx.s2s_do_transaction()
            secret=request.env['ir.config_parameter'].sudo().get_param('database.secret')
            token_str='%s%s%s'%(tx.id,tx.reference,float_repr(tx.amount,precision_digits=tx.currency_id.decimal_places))
            token=hmac.new(secret.encode('utf-8'),token_str.encode('utf-8'),hashlib.sha256).hexdigest()
            tx.return_url=return_urlor'/website_payment/confirm?tx_id=%d&access_token=%s'%(tx.id,token)
        exceptExceptionase:
            _logger.exception(e)
        returnrequest.redirect('/payment/process')

    @http.route(['/website_payment/confirm'],type='http',auth='public',website=True,sitemap=False)
    defconfirm(self,**kw):
        tx_id=int(kw.get('tx_id',0))
        access_token=kw.get('access_token')
        iftx_id:
            ifaccess_token:
                tx=request.env['payment.transaction'].sudo().browse(tx_id)
                secret=request.env['ir.config_parameter'].sudo().get_param('database.secret')
                valid_token_str='%s%s%s'%(tx.id,tx.reference,float_repr(tx.amount,precision_digits=tx.currency_id.decimal_places))
                valid_token=hmac.new(secret.encode('utf-8'),valid_token_str.encode('utf-8'),hashlib.sha256).hexdigest()
                ifnotconsteq(ustr(valid_token),access_token):
                    raisewerkzeug.exceptions.NotFound
            else:
                tx=request.env['payment.transaction'].browse(tx_id)
            iftx.statein['done','authorized']:
                status='success'
                message=tx.acquirer_id.done_msg
            eliftx.state=='pending':
                status='warning'
                message=tx.acquirer_id.pending_msg
            else:
                status='danger'
                message=tx.state_messageor_('Anerroroccuredduringtheprocessingofthispayment')
            PaymentProcessing.remove_payment_transaction(tx)
            returnrequest.render('payment.confirm',{'tx':tx,'status':status,'message':message})
        else:
            returnrequest.redirect('/my/home')
