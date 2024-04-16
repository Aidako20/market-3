#coding:utf-8
importbase64
importdatetime
importlogging
importtime
fromhashlibimportnewashashnew
frompprintimportpformat
fromunicodedataimportnormalize

importrequests
fromlxmlimportetree,objectify
fromwerkzeugimporturls

fromflectraimportapi,fields,models,_
fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.addons.payment_ingenico.controllers.mainimportOgoneController
fromflectra.addons.payment_ingenico.dataimportogone
fromflectra.httpimportrequest
fromflectra.toolsimportDEFAULT_SERVER_DATE_FORMAT,ustr
fromflectra.tools.float_utilsimportfloat_compare,float_repr,float_round

_logger=logging.getLogger(__name__)


classPaymentAcquirerOgone(models.Model):
    _inherit='payment.acquirer'

    provider=fields.Selection(selection_add=[
        ('ogone','Ingenico')
    ],ondelete={'ogone':'setdefault'})
    ogone_pspid=fields.Char('PSPID',required_if_provider='ogone',groups='base.group_user')
    ogone_userid=fields.Char('APIUserID',required_if_provider='ogone',groups='base.group_user')
    ogone_password=fields.Char('APIUserPassword',required_if_provider='ogone',groups='base.group_user')
    ogone_shakey_in=fields.Char('SHAKeyIN',required_if_provider='ogone',groups='base.group_user')
    ogone_shakey_out=fields.Char('SHAKeyOUT',required_if_provider='ogone',groups='base.group_user')
    ogone_alias_usage=fields.Char('AliasUsage',default="Allowsavingmypaymentdata",
                                    help="IfyouwanttouseOgoneAliases,thisdefault"
                                    "AliasUsagewillbepresentedtothecustomerasthe"
                                    "reasonyouwanttokeephispaymentdata")

    def_get_feature_support(self):
        """Getadvancedfeaturesupportbyprovider.

        Eachprovidershouldadditstechnicalinthecorresponding
        keyforthefollowingfeatures:
            *fees:supportpaymentfeescomputations
            *authorize:supportauthorizingpayment(separates
                         authorizationandcapture)
            *tokenize:supportsavingpaymentdatainapayment.tokenize
                        object
        """
        res=super(PaymentAcquirerOgone,self)._get_feature_support()
        res['tokenize'].append('ogone')
        returnres

    def_get_ogone_urls(self,environment):
        """OgoneURLS:
         -standardorder:POSTaddressforform-based"""
        return{
            'ogone_standard_order_url':'https://secure.ogone.com/ncol/%s/orderstandard_utf8.asp'%(environment,),
            'ogone_direct_order_url':'https://secure.ogone.com/ncol/%s/orderdirect_utf8.asp'%(environment,),
            'ogone_direct_query_url':'https://secure.ogone.com/ncol/%s/querydirect_utf8.asp'%(environment,),
            'ogone_afu_agree_url':'https://secure.ogone.com/ncol/%s/AFU_agree.asp'%(environment,),
            'ogone_maintenance_direct_url':'https://secure.ogone.com/ncol/%s/maintenancedirect.asp'%(environment,),
        }

    def_ogone_generate_shasign(self,inout,values):
        """Generatetheshasignforincomingoroutgoingcommunications.

        :paramstringinout:'in'(flectracontactingogone)or'out'(ogone
                             contactingflectra).Inthislastcaseonlysome
                             fieldsshouldbecontained(seee-Commercebasic)
        :paramdictvalues:transactionvalues

        :returnstring:shasign
        """
        assertinoutin('in','out')
        assertself.provider=='ogone'
        key=getattr(self,'ogone_shakey_'+inout)

        deffilter_key(key):
            ifinout=='in':
                returnTrue
            else:
                #SHA-OUTkeys
                #sourcehttps://payment-services.ingenico.com/int/en/ogone/support/guides/integrationguides/e-commerce/transaction-feedback
                keys=[
                    'AAVADDRESS',
                    'AAVCHECK',
                    'AAVMAIL',
                    'AAVNAME',
                    'AAVPHONE',
                    'AAVZIP',
                    'ACCEPTANCE',
                    'ALIAS',
                    'AMOUNT',
                    'BIC',
                    'BIN',
                    'BRAND',
                    'CARDNO',
                    'CCCTY',
                    'CN',
                    'COLLECTOR_BIC',
                    'COLLECTOR_IBAN',
                    'COMPLUS',
                    'CREATION_STATUS',
                    'CREDITDEBIT',
                    'CURRENCY',
                    'CVCCHECK',
                    'DCC_COMMPERCENTAGE',
                    'DCC_CONVAMOUNT',
                    'DCC_CONVCCY',
                    'DCC_EXCHRATE',
                    'DCC_EXCHRATESOURCE',
                    'DCC_EXCHRATETS',
                    'DCC_INDICATOR',
                    'DCC_MARGINPERCENTAGE',
                    'DCC_VALIDHOURS',
                    'DEVICEID',
                    'DIGESTCARDNO',
                    'ECI',
                    'ED',
                    'EMAIL',
                    'ENCCARDNO',
                    'FXAMOUNT',
                    'FXCURRENCY',
                    'IP',
                    'IPCTY',
                    'MANDATEID',
                    'MOBILEMODE',
                    'NBREMAILUSAGE',
                    'NBRIPUSAGE',
                    'NBRIPUSAGE_ALLTX',
                    'NBRUSAGE',
                    'NCERROR',
                    'ORDERID',
                    'PAYID',
                    'PAYIDSUB',
                    'PAYMENT_REFERENCE',
                    'PM',
                    'SCO_CATEGORY',
                    'SCORING',
                    'SEQUENCETYPE',
                    'SIGNDATE',
                    'STATUS',
                    'SUBBRAND',
                    'SUBSCRIPTION_ID',
                    'TICKET',
                    'TRXDATE',
                    'VC',
                ]
                returnkey.upper()inkeys

        items=sorted((k.upper(),v)fork,vinvalues.items())
        sign=''.join('%s=%s%s'%(k,v,key)fork,vinitemsifvandfilter_key(k))
        sign=sign.encode("utf-8")

        hash_function=self.env['ir.config_parameter'].sudo().get_param('payment_ogone.hash_function')
        ifnothash_functionorhash_function.lower()notin['sha1','sha256','sha512']:
            hash_function='sha1'

        shasign=hashnew(hash_function)
        shasign.update(sign)
        returnshasign.hexdigest()

    defogone_form_generate_values(self,values):
        base_url=self.get_base_url()
        ogone_tx_values=dict(values)
        param_plus={
            'return_url':ogone_tx_values.pop('return_url',False)
        }
        temp_ogone_tx_values={
            'PSPID':self.ogone_pspid,
            'ORDERID':values['reference'],
            'AMOUNT':float_repr(float_round(values['amount'],2)*100,0),
            'CURRENCY':values['currency']andvalues['currency'].nameor'',
            'LANGUAGE':values.get('partner_lang'),
            'CN':values.get('partner_name'),
            'EMAIL':values.get('partner_email'),
            'OWNERZIP':values.get('partner_zip'),
            'OWNERADDRESS':values.get('partner_address'),
            'OWNERTOWN':values.get('partner_city'),
            'OWNERCTY':values.get('partner_country')andvalues.get('partner_country').codeor'',
            'OWNERTELNO':values.get('partner_phone'),
            'ACCEPTURL':urls.url_join(base_url,OgoneController._accept_url),
            'DECLINEURL':urls.url_join(base_url,OgoneController._decline_url),
            'EXCEPTIONURL':urls.url_join(base_url,OgoneController._exception_url),
            'CANCELURL':urls.url_join(base_url,OgoneController._cancel_url),
            'PARAMPLUS':urls.url_encode(param_plus),
        }
        ifself.save_tokenin['ask','always']:
            temp_ogone_tx_values.update({
                'ALIAS':'FLECTRA-NEW-ALIAS-%s'%time.time(),   #somethingunique,
                'ALIASUSAGE':values.get('alias_usage')orself.ogone_alias_usage,
            })
        shasign=self._ogone_generate_shasign('in',temp_ogone_tx_values)
        temp_ogone_tx_values['SHASIGN']=shasign
        ogone_tx_values.update(temp_ogone_tx_values)
        returnogone_tx_values

    defogone_get_form_action_url(self):
        self.ensure_one()
        environment='prod'ifself.state=='enabled'else'test'
        returnself._get_ogone_urls(environment)['ogone_standard_order_url']

    defogone_s2s_form_validate(self,data):
        error=dict()

        mandatory_fields=["cc_number","cc_cvc","cc_holder_name","cc_expiry","cc_brand"]
        #Validation
        forfield_nameinmandatory_fields:
            ifnotdata.get(field_name):
                error[field_name]='missing'

        returnFalseiferrorelseTrue

    defogone_s2s_form_process(self,data):
        values={
            'cc_number':data.get('cc_number'),
            'cc_cvc':int(data.get('cc_cvc')),
            'cc_holder_name':data.get('cc_holder_name'),
            'cc_expiry':data.get('cc_expiry'),
            'cc_brand':data.get('cc_brand'),
            'acquirer_id':int(data.get('acquirer_id')),
            'partner_id':int(data.get('partner_id'))
        }
        pm_id=self.env['payment.token'].sudo().create(values)
        returnpm_id


classPaymentTxOgone(models.Model):
    _inherit='payment.transaction'
    #ogonestatus
    _ogone_valid_tx_status=[5,9,8]
    _ogone_wait_tx_status=[41,50,51,52,55,56,91,92,99]
    _ogone_pending_tx_status=[46,81,82]  #46=3DSHTMLresponse
    _ogone_cancel_tx_status=[1]

    #--------------------------------------------------
    #FORMRELATEDMETHODS
    #--------------------------------------------------

    @api.model
    def_ogone_form_get_tx_from_data(self,data):
        """Givenadatadictcomingfromogone,verifyitandfindtherelated
        transactionrecord.Createapaymenttokenifanaliasisreturned."""
        reference,pay_id,shasign,alias=data.get('orderID'),data.get('PAYID'),data.get('SHASIGN'),data.get('ALIAS')
        ifnotreferenceornotpay_idornotshasign:
            error_msg=_('Ogone:receiveddatawithmissingreference(%s)orpay_id(%s)orshasign(%s)')%(reference,pay_id,shasign)
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        #findtx->@TDENOTEusepaytid?
        tx=self.search([('reference','=',reference)])
        ifnottxorlen(tx)>1:
            error_msg=_('Ogone:receiveddataforreference%s')%(reference)
            ifnottx:
                error_msg+=_(';noorderfound')
            else:
                error_msg+=_(';multipleorderfound')
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        #verifyshasign
        shasign_check=tx.acquirer_id._ogone_generate_shasign('out',data)
        ifshasign_check.upper()!=shasign.upper():
            error_msg=_('Ogone:invalidshasign,received%s,computed%s,fordata%s')%(shasign,shasign_check,data)
            _logger.info(error_msg)
            raiseValidationError(error_msg)

        ifnottx.acquirer_reference:
            tx.acquirer_reference=pay_id

        #aliaswascreatedonogoneserver,storeit
        ifaliasandtx.type=='form_save':
            Token=self.env['payment.token']
            domain=[('acquirer_ref','=',alias)]
            cardholder=data.get('CN')
            ifnotToken.search_count(domain):
                _logger.info('Ogone:savingalias%sforpartner%s'%(data.get('CARDNO'),tx.partner_id))
                ref=Token.create({'name':data.get('CARDNO')+('-'+cardholderifcardholderelse''),
                                    'partner_id':tx.partner_id.id,
                                    'acquirer_id':tx.acquirer_id.id,
                                    'acquirer_ref':alias})
                tx.write({'payment_token_id':ref.id})

        returntx

    def_ogone_form_get_invalid_parameters(self,data):
        invalid_parameters=[]

        #TODO:txn_id:shouldbefalseatdraft,setafterwards,andverifiedwithtxndetails
        ifself.acquirer_referenceanddata.get('PAYID')!=self.acquirer_reference:
            invalid_parameters.append(('PAYID',data.get('PAYID'),self.acquirer_reference))
        #checkwhatisbought
        iffloat_compare(float(data.get('amount','0.0')),self.amount,2)!=0:
            invalid_parameters.append(('amount',data.get('amount'),'%.2f'%self.amount))
        ifdata.get('currency')!=self.currency_id.name:
            invalid_parameters.append(('currency',data.get('currency'),self.currency_id.name))

        returninvalid_parameters

    def_ogone_form_validate(self,data):
        ifself.statenotin['draft','pending']:
            _logger.info('Ogone:tryingtovalidateanalreadyvalidatedtx(ref%s)',self.reference)
            returnTrue

        status=int(data.get('STATUS','0'))
        ifstatusinself._ogone_valid_tx_status:
            vals={
                'date':datetime.datetime.strptime(data['TRXDATE'],'%m/%d/%y').strftime(DEFAULT_SERVER_DATE_FORMAT),
                'acquirer_reference':data['PAYID'],
            }
            ifdata.get('ALIAS')andself.partner_idand\
               (self.type=='form_save'orself.acquirer_id.save_token=='always')\
               andnotself.payment_token_id:
                pm=self.env['payment.token'].create({
                    'partner_id':self.partner_id.id,
                    'acquirer_id':self.acquirer_id.id,
                    'acquirer_ref':data.get('ALIAS'),
                    'name':'%s-%s'%(data.get('CARDNO'),data.get('CN'))
                })
                vals.update(payment_token_id=pm.id)
            self.write(vals)
            ifself.payment_token_id:
                self.payment_token_id.verified=True
            self._set_transaction_done()
            self.execute_callback()
            #ifthistransactionisavalidationone,thenwerefundthemoneywejustwithdrawn
            ifself.type=='validation':
                self.s2s_do_refund()

            returnTrue
        elifstatusinself._ogone_cancel_tx_status:
            self.write({'acquirer_reference':data.get('PAYID')})
            self._set_transaction_cancel()
        elifstatusinself._ogone_pending_tx_statusorstatusinself._ogone_wait_tx_status:
            self.write({'acquirer_reference':data.get('PAYID')})
            self._set_transaction_pending()
        else:
            error='Ogone:feedbackerror:%(error_str)s\n\n%(error_code)s:%(error_msg)s'%{
                'error_str':data.get('NCERRORPLUS'),
                'error_code':data.get('NCERROR'),
                'error_msg':ogone.OGONE_ERROR_MAP.get(data.get('NCERROR')),
            }
            _logger.info(error)
            self.write({
                'state_message':error,
                'acquirer_reference':data.get('PAYID'),
            })
            self._set_transaction_cancel()
            returnFalse

    #--------------------------------------------------
    #S2SRELATEDMETHODS
    #--------------------------------------------------
    defogone_s2s_do_transaction(self,**kwargs):
        #TODO:createtxwiths2stype
        account=self.acquirer_id
        reference=self.referenceor"FLECTRA-%s-%s"%(datetime.datetime.now().strftime('%y%m%d_%H%M%S'),self.partner_id.id)

        param_plus={
            'return_url':kwargs.get('return_url',False)
        }

        data={
            'PSPID':account.ogone_pspid,
            'USERID':account.ogone_userid,
            'PSWD':account.ogone_password,
            'ORDERID':reference,
            'AMOUNT':int(self.amount*100),
            'CURRENCY':self.currency_id.name,
            'OPERATION':'SAL',
            'ECI':9,  #Recurring(fromeCommerce)
            'ALIAS':self.payment_token_id.acquirer_ref,
            'RTIMEOUT':30,
            'PARAMPLUS':urls.url_encode(param_plus),
            'EMAIL':self.partner_id.emailor'',
            'CN':self.partner_id.nameor'',
        }

        ifrequest:
            data['REMOTE_ADDR']=request.httprequest.remote_addr

        ifkwargs.get('3d_secure'):
            data.update({
                'FLAG3D':'Y',
                'LANGUAGE':self.partner_id.langor'en_US',
            })

            forurlin'acceptdeclineexception'.split():
                key='{0}_url'.format(url)
                val=kwargs.pop(key,None)
                ifval:
                    key='{0}URL'.format(url).upper()
                    data[key]=val

        data['SHASIGN']=self.acquirer_id._ogone_generate_shasign('in',data)

        direct_order_url=self.acquirer_id._get_ogone_urls('prod'ifself.acquirer_id.state=='enabled'else'test')['ogone_direct_order_url']

        logged_data=data.copy()
        logged_data.pop('PSWD')
        _logger.info("ogone_s2s_do_transaction:SendingvaluestoURL%s,values:\n%s",direct_order_url,pformat(logged_data))
        result=requests.post(direct_order_url,data=data).content

        try:
            tree=objectify.fromstring(result)
            _logger.info('ogone_s2s_do_transaction:Valuesreceived:\n%s',etree.tostring(tree,pretty_print=True,encoding='utf-8'))
        exceptetree.XMLSyntaxError:
            #invalidresponsefromogone
            _logger.exception('Invalidxmlresponsefromogone')
            _logger.info('ogone_s2s_do_transaction:Valuesreceived:\n%s',result)
            raise

        returnself._ogone_s2s_validate_tree(tree)

    defogone_s2s_do_refund(self,**kwargs):
        account=self.acquirer_id
        reference=self.referenceor"FLECTRA-%s-%s"%(datetime.datetime.now().strftime('%y%m%d_%H%M%S'),self.partner_id.id)

        data={
            'PSPID':account.ogone_pspid,
            'USERID':account.ogone_userid,
            'PSWD':account.ogone_password,
            'ORDERID':reference,
            'AMOUNT':int(self.amount*100),
            'CURRENCY':self.currency_id.name,
            'OPERATION':'RFS',
            'PAYID':self.acquirer_reference,
        }
        data['SHASIGN']=self.acquirer_id._ogone_generate_shasign('in',data)

        direct_order_url=self.acquirer_id._get_ogone_urls('prod'ifself.acquirer_id.state=='enabled'else'test')['ogone_maintenance_direct_url']

        logged_data=data.copy()
        logged_data.pop('PSWD')
        _logger.info("ogone_s2s_do_refund:SendingvaluestoURL%s,values:\n%s",direct_order_url,pformat(logged_data))
        result=requests.post(direct_order_url,data=data).content

        try:
            tree=objectify.fromstring(result)
            _logger.info('ogone_s2s_do_refund:Valuesreceived:\n%s',etree.tostring(tree,pretty_print=True,encoding='utf-8'))
        exceptetree.XMLSyntaxError:
            #invalidresponsefromogone
            _logger.exception('Invalidxmlresponsefromogone')
            _logger.info('ogone_s2s_do_refund:Valuesreceived:\n%s',result)
            raise

        returnself._ogone_s2s_validate_tree(tree)

    def_ogone_s2s_validate(self):
        tree=self._ogone_s2s_get_tx_status()
        returnself._ogone_s2s_validate_tree(tree)

    def_ogone_s2s_validate_tree(self,tree,tries=2):
        ifself.statenotin['draft','pending']:
            _logger.info('Ogone:tryingtovalidateanalreadyvalidatedtx(ref%s)',self.reference)
            returnTrue

        status=int(tree.get('STATUS')or0)
        ifstatusinself._ogone_valid_tx_status:
            self.write({
                'date':datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                'acquirer_reference':tree.get('PAYID'),
            })
            iftree.get('ALIAS')andself.partner_idand\
               (self.type=='form_save'orself.acquirer_id.save_token=='always')\
               andnotself.payment_token_id:
                pm=self.env['payment.token'].create({
                    'partner_id':self.partner_id.id,
                    'acquirer_id':self.acquirer_id.id,
                    'acquirer_ref':tree.get('ALIAS'),
                    'name':tree.get('CARDNO'),
                })
                self.write({'payment_token_id':pm.id})
            ifself.payment_token_id:
                self.payment_token_id.verified=True
            self._set_transaction_done()
            self.execute_callback()
            #ifthistransactionisavalidationone,thenwerefundthemoneywejustwithdrawn
            ifself.type=='validation':
                self.s2s_do_refund()
            returnTrue
        elifstatusinself._ogone_cancel_tx_status:
            self.write({'acquirer_reference':tree.get('PAYID')})
            self._set_transaction_cancel()
        elifstatusinself._ogone_pending_tx_status:
            vals={
                'acquirer_reference':tree.get('PAYID'),
            }
            ifstatus==46:#HTML3DS
                vals['html_3ds']=ustr(base64.b64decode(tree.HTML_ANSWER.text))
            self.write(vals)
            self._set_transaction_pending()
        elifstatusinself._ogone_wait_tx_statusandtries>0:
            time.sleep(0.5)
            self.write({'acquirer_reference':tree.get('PAYID')})
            tree=self._ogone_s2s_get_tx_status()
            returnself._ogone_s2s_validate_tree(tree,tries-1)
        else:
            error='Ogone:feedbackerror:%(error_str)s\n\n%(error_code)s:%(error_msg)s'%{
                'error_str':tree.get('NCERRORPLUS'),
                'error_code':tree.get('NCERROR'),
                'error_msg':ogone.OGONE_ERROR_MAP.get(tree.get('NCERROR')),
            }
            _logger.info(error)
            self.write({
                'state_message':error,
                'acquirer_reference':tree.get('PAYID'),
            })
            self._set_transaction_cancel()
            returnFalse

    def_ogone_s2s_get_tx_status(self):
        account=self.acquirer_id
        #reference=tx.referenceor"FLECTRA-%s-%s"%(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'),tx.partner_id.id)

        data={
            'PAYID':self.acquirer_reference,
            'PSPID':account.ogone_pspid,
            'USERID':account.ogone_userid,
            'PSWD':account.ogone_password,
        }

        query_direct_url=self.acquirer_id._get_ogone_urls('prod'ifself.acquirer_id.state=='enabled'else'test')['ogone_direct_query_url']

        logged_data=data.copy()
        logged_data.pop('PSWD')

        _logger.info("_ogone_s2s_get_tx_status:SendingvaluestoURL%s,values:\n%s",query_direct_url,pformat(logged_data))
        result=requests.post(query_direct_url,data=data).content

        try:
            tree=objectify.fromstring(result)
            _logger.info('_ogone_s2s_get_tx_status:Valuesreceived:\n%s',etree.tostring(tree,pretty_print=True,encoding='utf-8'))
        exceptetree.XMLSyntaxError:
            #invalidresponsefromogone
            _logger.exception('Invalidxmlresponsefromogone')
            _logger.info('_ogone_s2s_get_tx_status:Valuesreceived:\n%s',result)
            raise

        returntree


classPaymentToken(models.Model):
    _inherit='payment.token'

    defogone_create(self,values):
        ifvalues.get('cc_number'):
            #createaaliasviabatch
            values['cc_number']=values['cc_number'].replace('','')
            acquirer=self.env['payment.acquirer'].browse(values['acquirer_id'])
            alias='FLECTRA-NEW-ALIAS-%s'%time.time()

            expiry=str(values['cc_expiry'][:2])+str(values['cc_expiry'][-2:])
            line='ADDALIAS;%(alias)s;%(cc_holder_name)s;%(cc_number)s;%(expiry)s;%(cc_brand)s;%(pspid)s'
            line=line%dict(values,alias=alias,expiry=expiry,pspid=acquirer.ogone_pspid)

            data={
                'FILE_REFERENCE':alias,
                'TRANSACTION_CODE':'MTR',
                'OPERATION':'SAL',
                'NB_PAYMENTS':1,  #evenifwedonotactuallyhaveanypayment,ogonewantittonotbe0
                'FILE':normalize('NFKD',line).encode('ascii','ignore'), #OgoneBatchmustbeASCIIonly
                'REPLY_TYPE':'XML',
                'PSPID':acquirer.ogone_pspid,
                'USERID':acquirer.ogone_userid,
                'PSWD':acquirer.ogone_password,
                'PROCESS_MODE':'CHECKANDPROCESS',
            }

            url=acquirer._get_ogone_urls('prod'ifacquirer.state=='enabled'else'test')['ogone_afu_agree_url']
            _logger.info("ogone_create:Creatingnewalias%sviaurl%s",alias,url)
            result=requests.post(url,data=data).content

            try:
                tree=objectify.fromstring(result)
            exceptetree.XMLSyntaxError:
                _logger.exception('Invalidxmlresponsefromogone')
                returnNone

            error_code=error_str=None
            ifhasattr(tree,'PARAMS_ERROR'):
                error_code=tree.NCERROR.text
                error_str='PARAMSERROR:%s'%(tree.PARAMS_ERROR.textor'',)
            else:
                node=tree.FORMAT_CHECK
                error_node=getattr(node,'FORMAT_CHECK_ERROR',None)
                iferror_nodeisnotNone:
                    error_code=error_node.NCERROR.text
                    error_str='CHECKERROR:%s'%(error_node.ERROR.textor'',)

            iferror_code:
                error_msg=tree.get(error_code)
                error='%s\n\n%s:%s'%(error_str,error_code,error_msg)
                _logger.error(error)
                raiseException(error)

            return{
                'acquirer_ref':alias,
                'name':'XXXXXXXXXXXX%s-%s'%(values['cc_number'][-4:],values['cc_holder_name'])
            }
        return{}
