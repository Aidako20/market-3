#coding:utf-8
fromcollectionsimportdefaultdict
importhashlib
importhmac
importlogging
fromdatetimeimportdatetime
fromdateutilimportrelativedelta
importpprint
importpsycopg2

fromflectraimportapi,exceptions,fields,models,_,SUPERUSER_ID
fromflectra.toolsimportconsteq,float_round,image_process,ustr
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.tools.miscimportDEFAULT_SERVER_DATETIME_FORMAT
fromflectra.tools.miscimportformatLang
fromflectra.httpimportrequest
fromflectra.osvimportexpression

fromflectra.addons.base.models.ir_modelimportMODULE_UNINSTALL_FLAG

_logger=logging.getLogger(__name__)


def_partner_format_address(address1=False,address2=False):
    return''.join((address1or'',address2or'')).strip()


def_partner_split_name(partner_name):
    return[''.join(partner_name.split()[:-1]),''.join(partner_name.split()[-1:])]


defcreate_missing_journal_for_acquirers(cr,registry):
    env=api.Environment(cr,SUPERUSER_ID,{})
    env['payment.acquirer']._create_missing_journal_for_acquirers()


classPaymentAcquirer(models.Model):
    """AcquirerModel.Eachspecificacquirercanextendthemodelbyadding
    itsownfields,usingtheacquirer_nameasaprefixforthenewfields.
    Usingtherequired_if_provider='<name>'attributeonfieldsitispossible
    tohaverequiredfieldsthatdependonaspecificacquirer.

    Eachacquirerhasalinktoanir.ui.viewrecordthatisatemplateof
    abuttonusedtodisplaythepaymentform.Seeexamplesin``payment_ingenico``
    and``payment_paypal``modules.

    Methodsthatshouldbeaddedinanacquirer-specificimplementation:

     -``<name>_form_generate_values(self,reference,amount,currency,
       partner_id=False,partner_values=None,tx_custom_values=None)``:
       methodthatgeneratesthevaluesusedtorendertheformbuttontemplate.
     -``<name>_get_form_action_url(self):``:methodthatreturnstheurlof
       thebuttonform.Itisusedforexampleinecommerceapplicationifyou
       wanttopostsomedatatotheacquirer.
     -``<name>_compute_fees(self,amount,currency_id,country_id)``:computes
       thefeesoftheacquirer,usinggenericfieldsdefinedontheacquirer
       model(seefieldsdefinition).

    Eachacquirershouldalsodefinecontrollerstohandlecommunicationbetween
    OpenERPandtheacquirer.Itgenerallyconsistsinreturnurlsgiventothe
    buttonformandthattheacquirerusestosendthecustomerbackafterthe
    transaction,withtransactiondetailsgivenasaPOSTrequest.
    """
    _name='payment.acquirer'
    _description='PaymentAcquirer'
    _order='module_state,state,sequence,name'

    def_valid_field_parameter(self,field,name):
        returnname=='required_if_provider'orsuper()._valid_field_parameter(field,name)

    def_get_default_view_template_id(self):
        returnself.env.ref('payment.default_acquirer_button',raise_if_not_found=False)

    name=fields.Char('Name',required=True,translate=True)
    color=fields.Integer('Color',compute='_compute_color',store=True)
    display_as=fields.Char('Displayedas',translate=True,help="Howtheacquirerisdisplayedtothecustomers.")
    description=fields.Html('Description')
    sequence=fields.Integer('Sequence',default=10,help="Determinethedisplayorder")
    provider=fields.Selection(
        selection=[('manual','CustomPaymentForm')],string='Provider',
        default='manual',required=True)
    company_id=fields.Many2one(
        'res.company','Company',
        default=lambdaself:self.env.company.id,required=True)
    view_template_id=fields.Many2one(
        'ir.ui.view','FormButtonTemplate',
        default=_get_default_view_template_id,
        help="Thistemplaterenderstheacquirerbuttonwithallnecessaryvalues.\n"
        "ItisrenderedwithqWebwiththefollowingevaluationcontext:\n"
        "tx_url:transactionURLtoposttheform\n"
        "acquirer:payment.acquirerbrowserecord\n"
        "user:currentuserbrowserecord\n"
        "reference:thetransactionreferencenumber\n"
        "currency:thetransactioncurrencybrowserecord\n"
        "amount:thetransactionamount,afloat\n"
        "partner:thebuyerpartnerbrowserecord,notnecessarilyset\n"
        "partner_values:specificvaluesaboutthebuyer,forexamplecomingfromashippingform\n"
        "tx_values:transactionvalues\n"
        "context:thecurrentcontextdictionary")
    registration_view_template_id=fields.Many2one(
        'ir.ui.view','S2SFormTemplate',domain=[('type','=','qweb')],
        help="Templateformethodregistration")
    state=fields.Selection([
        ('disabled','Disabled'),
        ('enabled','Enabled'),
        ('test','TestMode')],required=True,default='disabled',copy=False,
        help="""Intestmode,afakepaymentisprocessedthroughatest
             paymentinterface.Thismodeisadvisedwhensettingupthe
             acquirer.Watchout,testandproductionmodesrequire
             differentcredentials.""")
    capture_manually=fields.Boolean(string="CaptureAmountManually",
        help="CapturetheamountfromFlectra,whenthedeliveryiscompleted.")
    journal_id=fields.Many2one(
        'account.journal','PaymentJournal',domain="[('type','in',['bank','cash']),('company_id','=',company_id)]",
        help="""Journalwherethesuccessfultransactionswillbeposted""",ondelete='restrict')
    check_validity=fields.Boolean(string="VerifyCardValidity",
        help="""Triggeratransactionof1currencyunitanditsrefundtocheckthevalidityofnewcreditcardsenteredinthecustomerportal.
        Withoutthischeck,thevaliditywillbeverifiedattheveryfirsttransaction.""")
    country_ids=fields.Many2many(
        'res.country','payment_country_rel',
        'payment_id','country_id','Countries',
        help="Thispaymentgatewayisavailableforselectedcountries.Ifnoneisselecteditisavailableforallcountries.")

    pre_msg=fields.Html(
        'HelpMessage',translate=True,
        help='Messagedisplayedtoexplainandhelpthepaymentprocess.')
    auth_msg=fields.Html(
        'AuthorizeMessage',translate=True,
        default=lambdas:_('Yourpaymenthasbeenauthorized.'),
        help='Messagedisplayedifpaymentisauthorized.')
    pending_msg=fields.Html(
        'PendingMessage',translate=True,
        default=lambdas:_('Yourpaymenthasbeensuccessfullyprocessedbutiswaitingforapproval.'),
        help='Messagedisplayed,iforderisinpendingstateafterhavingdonethepaymentprocess.')
    done_msg=fields.Html(
        'DoneMessage',translate=True,
        default=lambdas:_('Yourpaymenthasbeensuccessfullyprocessed.Thankyou!'),
        help='Messagedisplayed,iforderisdonesuccessfullyafterhavingdonethepaymentprocess.')
    cancel_msg=fields.Html(
        'CancelMessage',translate=True,
        default=lambdas:_('Yourpaymenthasbeencancelled.'),
        help='Messagedisplayed,iforderiscancelduringthepaymentprocess.')
    save_token=fields.Selection([
        ('none','Never'),
        ('ask','Letthecustomerdecide'),
        ('always','Always')],
        string='SaveCards',default='none',
        help="Thisoptionallowscustomerstosavetheircreditcardasapaymenttokenandtoreuseitforalaterpurchase."
             "Ifyoumanagesubscriptions(recurringinvoicing),youneedittoautomaticallychargethecustomerwhenyou"
             "issueaninvoice.")
    token_implemented=fields.Boolean('SavingCardDatasupported',compute='_compute_feature_support',search='_search_is_tokenized')
    authorize_implemented=fields.Boolean('AuthorizeMechanismSupported',compute='_compute_feature_support')
    fees_implemented=fields.Boolean('FeesComputationSupported',compute='_compute_feature_support')
    fees_active=fields.Boolean('AddExtraFees')
    fees_dom_fixed=fields.Float('Fixeddomesticfees')
    fees_dom_var=fields.Float('Variabledomesticfees(inpercents)')
    fees_int_fixed=fields.Float('Fixedinternationalfees')
    fees_int_var=fields.Float('Variableinternationalfees(inpercents)')
    qr_code=fields.Boolean('EnableQRCodes',help="EnabletheuseofQR-codesforpaymentsmadeonthisprovider.")

    #TDEFIXME:removethatbrol
    module_id=fields.Many2one('ir.module.module',string='CorrespondingModule')
    module_state=fields.Selection(string='InstallationState',related='module_id.state',store=True)
    module_to_buy=fields.Boolean(string='FlectraEnterpriseModule',related='module_id.to_buy',readonly=True,store=False)

    image_128=fields.Image("Image",max_width=128,max_height=128)

    payment_icon_ids=fields.Many2many('payment.icon',string='SupportedPaymentIcons')
    payment_flow=fields.Selection(selection=[('form','Redirectiontotheacquirerwebsite'),
        ('s2s','PaymentfromFlectra')],
        default='form',required=True,string='PaymentFlow',
        help="""Note:Subscriptionsdoesnottakethisfieldinaccount,itusesservertoserverbydefault.""")
    inbound_payment_method_ids=fields.Many2many('account.payment.method',related='journal_id.inbound_payment_method_ids',readonly=False)

    @api.onchange('payment_flow')
    def_onchange_payment_flow(self):
        electronic=self.env.ref('payment.account_payment_method_electronic_in')
        ifself.token_implementedandself.payment_flow=='s2s':
            ifelectronicnotinself.inbound_payment_method_ids:
                self.inbound_payment_method_ids=[(4,electronic.id)]
        elifelectronicinself.inbound_payment_method_ids:
            self.inbound_payment_method_ids=[(2,electronic.id)]

    @api.onchange('state')
    defonchange_state(self):
        """Disabledashboarddisplayfortestacquirerjournal."""
        self.journal_id.update({'show_on_dashboard':self.state=='enabled'})

    def_search_is_tokenized(self,operator,value):
        tokenized=self._get_feature_support()['tokenize']
        if(operator,value)in[('=',True),('!=',False)]:
            return[('provider','in',tokenized)]
        return[('provider','notin',tokenized)]

    @api.depends('provider')
    def_compute_feature_support(self):
        feature_support=self._get_feature_support()
        foracquirerinself:
            acquirer.fees_implemented=acquirer.providerinfeature_support['fees']
            acquirer.authorize_implemented=acquirer.providerinfeature_support['authorize']
            acquirer.token_implemented=acquirer.providerinfeature_support['tokenize']

    @api.depends('state','module_state')
    def_compute_color(self):
        foracquirerinself:
            ifacquirer.module_idandnotacquirer.module_state=='installed':
                acquirer.color=4 #blue
            elifacquirer.state=='disabled':
                acquirer.color=3 #yellow
            elifacquirer.state=='test':
                acquirer.color=2 #orange
            elifacquirer.state=='enabled':
                acquirer.color=7 #green

    def_check_required_if_provider(self):
        """Ifthefieldhas'required_if_provider="<provider>"'attribute,thenit
        requiredifrecord.provideris<provider>."""
        field_names=[]
        enabled_acquirers=self.filtered(lambdaacq:acq.statein['enabled','test'])
        fork,finself._fields.items():
            provider=getattr(f,'required_if_provider',None)
            ifproviderandany(
                acquirer.provider==providerandnotacquirer[k]
                foracquirerinenabled_acquirers
            ):
                ir_field=self.env['ir.model.fields']._get(self._name,k)
                field_names.append(ir_field.field_description)
        iffield_names:
            raiseValidationError(_("Requiredfieldsnotfilled:%s")%",".join(field_names))

    defget_base_url(self):
        self.ensure_one()
        #priorityisalwaysgiventourl_root
        #fromtherequest
        url=''
        ifrequest:
            url=request.httprequest.url_root

        ifnoturland'website_id'inselfandself.website_id:
            url=self.website_id._get_http_domain()

        returnurlorself.env['ir.config_parameter'].sudo().get_param('web.base.url')

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
        returndict(authorize=[],tokenize=[],fees=[])

    def_prepare_account_journal_vals(self):
        '''Preparethevaluestocreatetheacquirer'sjournal.
        :return:adictionarytocreateaaccount.journalrecord.
        '''
        self.ensure_one()
        account_vals=self.company_id.chart_template_id._prepare_transfer_account_for_direct_creation(self.name,self.company_id)
        account=self.env['account.account'].create(account_vals)
        inbound_payment_method_ids=[]
        ifself.token_implementedandself.payment_flow=='s2s':
            inbound_payment_method_ids.append((4,self.env.ref('payment.account_payment_method_electronic_in').id))
        return{
            'name':self.name,
            'code':self.name.upper(),
            'sequence':999,
            'type':'bank',
            'company_id':self.company_id.id,
            'default_account_id':account.id,
            #Showthejournalondashboardiftheacquirerispublishedonthewebsite.
            'show_on_dashboard':self.state=='enabled',
            #Don'tshowpaymentmethodsinthebackend.
            'inbound_payment_method_ids':inbound_payment_method_ids,
            'outbound_payment_method_ids':[],
        }

    def_get_acquirer_journal_domain(self):
        """Returnsadomainforfindingajournalcorrespondingtoanacquirer"""
        self.ensure_one()
        code_cutoff=self.env['account.journal']._fields['code'].size
        return[
            ('name','=',self.name),
            ('code','=',self.name.upper()[:code_cutoff]),
            ('company_id','=',self.company_id.id),
        ]

    @api.model
    def_create_missing_journal_for_acquirers(self,company=None):
        '''Createthejournalforactiveacquirers.
        Wewantonejournalperacquirer.However,wecan'tcreatethemduringthe'create'ofthepayment.acquirer
        becauseeveryacquirersaredefinedonthe'payment'modulebutisactiveonlywheninstallingtheirownmodule
        (e.g.payment_paypalforPaypal).Wecan'tdothatinsuchmodulesbecausewehavenoguaranteethecharttemplate
        isalreadyinstalled.
        '''
        #Searchforinstalledacquirersmodulesthathavenojournalforthecurrentcompany.
        #Ifthismethodistriggeredbyapost_init_hook,themoduleis'toinstall'.
        #Ifthetriggercomesfromthecharttemplatewizard,themodulesarealreadyinstalled.
        company=companyorself.env.company
        acquirers=self.env['payment.acquirer'].search([
            ('module_state','in',('toinstall','installed')),
            ('journal_id','=',False),
            ('company_id','=',company.id),
        ])

        #Herewewillattempttofirstcreatethejournalsincethemostcommoncase(first
        #install)istosuccessfullytocreatethejournalfortheacquirer,inthecaseofa
        #reinstall(leastcommoncase),thecreationwillfailbecauseofauniqueconstraint
        #violation,thisisokaswecatchtheerrorandthenperformasearchifneedbe
        #andassigntheexistingjournaltoourreinstalledacquirer.Itisbettertoaskfor
        #forgivenessthantoaskforpermissionasthissavesustheoverheadofdoingaselect
        #thatwouldbeuselessinmostcases.
        Journal=journals=self.env['account.journal']
        foracquirerinacquirers.filtered(lambdal:notl.journal_idandl.company_id.chart_template_id):
            try:
                withself.env.cr.savepoint():
                    journal=Journal.create(acquirer._prepare_account_journal_vals())
            exceptpsycopg2.IntegrityErrorase:
                ife.pgcode==psycopg2.errorcodes.UNIQUE_VIOLATION:
                    journal=Journal.search(acquirer._get_acquirer_journal_domain(),limit=1)
                else:
                    raise
            acquirer.journal_id=journal
            journals+=journal
        returnjournals

    @api.model
    defcreate(self,vals):
        record=super(PaymentAcquirer,self).create(vals)
        record._check_required_if_provider()
        returnrecord

    defwrite(self,vals):
        result=super(PaymentAcquirer,self).write(vals)
        self._check_required_if_provider()
        returnresult

    defunlink(self):
        """Preventthedeletionofthepaymentacquirerifithasanxmlid."""
        external_ids=self.get_external_id()
        foracquirerinself:
            external_id=external_ids[acquirer.id]
            ifexternal_id\
               andnotexternal_id.startswith('__export__')\
               andnotself._context.get(MODULE_UNINSTALL_FLAG):
                raiseUserError(_(
                    "Youcannotdeletethepaymentacquirer%s;disableitoruninstallitinstead.",
                    acquirer.name,
                ))
        returnsuper().unlink()

    defget_acquirer_extra_fees(self,amount,currency_id,country_id):
        extra_fees={
            'currency_id':currency_id
        }
        acquirers=self.filtered(lambdax:x.fees_active)
        foracqinacquirers:
            custom_method_name='%s_compute_fees'%acq.provider
            ifhasattr(acq,custom_method_name):
                fees=getattr(acq,custom_method_name)(amount,currency_id,country_id)
                extra_fees[acq]=fees
        returnextra_fees

    defget_form_action_url(self):
        """ReturnstheformactionURL,forform-basedacquirerimplementations."""
        ifhasattr(self,'%s_get_form_action_url'%self.provider):
            returngetattr(self,'%s_get_form_action_url'%self.provider)()
        returnFalse

    def_get_available_payment_input(self,partner=None,company=None):
        """Generic(model)methodthatfetchesavailablepaymentmechanisms
        touseinallportal/eshoppagesthatwanttousethepaymentform.

        Itcontains

         *acquirers:recordsetofbothformands2sacquirers;
         *pms:recordsetofstoredcreditcarddata(akapayment.token)
                connectedtoagivenpartnertoallowcustomerstoreusethem"""
        ifnotcompany:
            company=self.env.company
        ifnotpartner:
            partner=self.env.user.partner_id

        domain=expression.AND([
            ['&',('state','in',['enabled','test']),('company_id','=',company.id)],
            ['|',('country_ids','=',False),('country_ids','in',[partner.country_id.id])]
        ])
        active_acquirers=self.search(domain)
        acquirers=active_acquirers.filtered(lambdaacq:(acq.payment_flow=='form'andacq.view_template_id)or
                                                               (acq.payment_flow=='s2s'andacq.registration_view_template_id))
        return{
            'acquirers':acquirers,
            'pms':self.env['payment.token'].search([
                ('partner_id','=',partner.id),
                ('acquirer_id','in',acquirers.ids)]),
        }

    defrender(self,reference,amount,currency_id,partner_id=False,values=None):
        """RenderstheformtemplateofthegivenacquirerasaqWebtemplate.
        :paramstringreference:thetransactionreference
        :paramfloatamount:theamountthebuyerhastopay
        :paramcurrency_id:currencyid
        :paramdictpartner_id:optionalpartner_idtofillvalues
        :paramdictvalues:adictionaryofvaluesforthetransctionthatis
        giventotheacquirer-specificmethodgeneratingtheformvalues

        Alltemplateswillreceive:

         -acquirer:thepayment.acquirerbrowserecord
         -user:thecurrentuserbrowserecord
         -currency_id:idofthetransactioncurrency
         -amount:amountofthetransaction
         -reference:referenceofthetransaction
         -partner_*:partner-relatedvalues
         -partner:optionalpartnerbrowserecord
         -'feedback_url':feedbackURL,controlerthatmanageansweroftheacquirer(withoutbaseurl)->FIXME
         -'return_url':URLforcomingbackafterpaymentvalidation(wihoutbaseurl)->FIXME
         -'cancel_url':URLiftheclientcancelsthepayment->FIXME
         -'error_url':URLifthereisanissuewiththepayment->FIXME
         -context:Flectracontext

        """
        ifvaluesisNone:
            values={}

        ifnotself.view_template_id:
            returnNone

        values.setdefault('return_url','/payment/process')
        #referenceandamount
        values.setdefault('reference',reference)
        amount=float_round(amount,2)
        values.setdefault('amount',amount)

        #currencyid
        currency_id=values.setdefault('currency_id',currency_id)
        ifcurrency_id:
            currency=self.env['res.currency'].browse(currency_id)
        else:
            currency=self.env.company.currency_id
        values['currency']=currency

        #Fillpartner_*usingvalues['partner_id']orpartner_idargument
        partner_id=values.get('partner_id',partner_id)
        billing_partner_id=values.get('billing_partner_id',partner_id)
        ifpartner_id:
            partner=self.env['res.partner'].browse(partner_id)
            ifpartner_id!=billing_partner_id:
                billing_partner=self.env['res.partner'].browse(billing_partner_id)
            else:
                billing_partner=partner
            values.update({
                'partner':partner,
                'partner_id':partner_id,
                'partner_name':partner.name,
                'partner_lang':partner.lang,
                'partner_email':partner.email,
                'partner_zip':partner.zip,
                'partner_city':partner.city,
                'partner_address':_partner_format_address(partner.street,partner.street2),
                'partner_country_id':partner.country_id.idorself.env.company.country_id.id,
                'partner_country':partner.country_id,
                'partner_phone':partner.phone,
                'partner_state':partner.state_id,
                'billing_partner':billing_partner,
                'billing_partner_id':billing_partner_id,
                'billing_partner_name':billing_partner.name,
                'billing_partner_commercial_company_name':billing_partner.commercial_company_name,
                'billing_partner_lang':billing_partner.lang,
                'billing_partner_email':billing_partner.email,
                'billing_partner_zip':billing_partner.zip,
                'billing_partner_city':billing_partner.city,
                'billing_partner_address':_partner_format_address(billing_partner.street,billing_partner.street2),
                'billing_partner_country_id':billing_partner.country_id.id,
                'billing_partner_country':billing_partner.country_id,
                'billing_partner_phone':billing_partner.phone,
                'billing_partner_state':billing_partner.state_id,
            })
        ifvalues.get('partner_name'):
            values.update({
                'partner_first_name':_partner_split_name(values.get('partner_name'))[0],
                'partner_last_name':_partner_split_name(values.get('partner_name'))[1],
            })
        ifvalues.get('billing_partner_name'):
            values.update({
                'billing_partner_first_name':_partner_split_name(values.get('billing_partner_name'))[0],
                'billing_partner_last_name':_partner_split_name(values.get('billing_partner_name'))[1],
            })

        #Fixaddress,countryfields
        ifnotvalues.get('partner_address'):
            values['address']=_partner_format_address(values.get('partner_street',''),values.get('partner_street2',''))
        ifnotvalues.get('partner_country')andvalues.get('partner_country_id'):
            values['country']=self.env['res.country'].browse(values.get('partner_country_id'))
        ifnotvalues.get('billing_partner_address'):
            values['billing_address']=_partner_format_address(values.get('billing_partner_street',''),values.get('billing_partner_street2',''))
        ifnotvalues.get('billing_partner_country')andvalues.get('billing_partner_country_id'):
            values['billing_country']=self.env['res.country'].browse(values.get('billing_partner_country_id'))

        #computefees
        fees_method_name='%s_compute_fees'%self.provider
        ifhasattr(self,fees_method_name):
            fees=getattr(self,fees_method_name)(values['amount'],values['currency_id'],values.get('partner_country_id'))
            values['fees']=float_round(fees,2)

        #call<name>_form_generate_valuestoupdatethetxdictwithacqurierspecificvalues
        cust_method_name='%s_form_generate_values'%(self.provider)
        ifhasattr(self,cust_method_name):
            method=getattr(self,cust_method_name)
            values=method(values)

        values.update({
            'tx_url': self._context.get(
                'tx_url',self.with_context(form_action_url_values=values).get_form_action_url()
            ),
            'submit_class':self._context.get('submit_class','btnbtn-link'),
            'submit_txt':self._context.get('submit_txt'),
            'acquirer':self,
            'user':self.env.user,
            'context':self._context,
            'type':values.get('type')or'form',
        })

        _logger.info('payment.acquirer.render:<%s>valuesrenderedforformpayment:\n%s',self.provider,pprint.pformat(values))
        returnself.view_template_id._render(values,engine='ir.qweb')

    defget_s2s_form_xml_id(self):
        ifself.registration_view_template_id:
            model_data=self.env['ir.model.data'].search([('model','=','ir.ui.view'),('res_id','=',self.registration_view_template_id.id)])
            return('%s.%s')%(model_data.module,model_data.name)
        returnFalse

    defs2s_process(self,data):
        cust_method_name='%s_s2s_form_process'%(self.provider)
        ifnotself.s2s_validate(data):
            returnFalse
        ifhasattr(self,cust_method_name):
            #AsthismethodmaybecalledinJSONandoverriddeninvariousaddons
            #letusraiseinterestingerrorsbeforehavingstrangescrashes
            ifnotdata.get('partner_id'):
                raiseValueError(_('Missingpartnerreferencewhentryingtocreateanewpaymenttoken'))
            method=getattr(self,cust_method_name)
            returnmethod(data)
        returnTrue

    defs2s_validate(self,data):
        cust_method_name='%s_s2s_form_validate'%(self.provider)
        ifhasattr(self,cust_method_name):
            method=getattr(self,cust_method_name)
            returnmethod(data)
        returnTrue

    defbutton_immediate_install(self):
        #TDEFIXME:removethatbrol
        ifself.module_idandself.module_state!='installed':
            self.module_id.button_immediate_install()
            return{
                'type':'ir.actions.client',
                'tag':'reload',
            }

classPaymentIcon(models.Model):
    _name='payment.icon'
    _description='PaymentIcon'

    name=fields.Char(string='Name')
    acquirer_ids=fields.Many2many('payment.acquirer',string="Acquirers",help="ListofAcquirerssupportingthispaymenticon.")
    image=fields.Binary(
        "Image",help="Thisfieldholdstheimageusedforthispaymenticon,limitedto1024x1024px")

    image_payment_form=fields.Binary(
        "Imagedisplayedonthepaymentform",attachment=True)

    @api.model_create_multi
    defcreate(self,vals_list):
        forvalsinvals_list:
            if'image'invals:
                image=ustr(vals['image']or'').encode('utf-8')
                vals['image_payment_form']=image_process(image,size=(45,30))
                vals['image']=image_process(image,size=(64,64))
        returnsuper(PaymentIcon,self).create(vals_list)

    defwrite(self,vals):
        if'image'invals:
            image=ustr(vals['image']or'').encode('utf-8')
            vals['image_payment_form']=image_process(image,size=(45,30))
            vals['image']=image_process(image,size=(64,64))
        returnsuper(PaymentIcon,self).write(vals)

classPaymentTransaction(models.Model):
    """TransactionModel.Eachspecificacquirercanextendthemodelbyadding
    itsownfields.

    Methodsthatcanbeaddedinanacquirer-specificimplementation:

     -``<name>_create``:methodreceivingvaluesusedwhencreatinganew
       transactionandthatreturnsadictionarythatwillupdatethosevalues.
       Thismethodcanbeusedtotweaksometransactionvalues.

    Methodsdefinedforconvention,dependingonyourcontrollers:

     -``<name>_form_feedback(self,data)``:methodthathandlesthedatacoming
       fromtheacquirerafterthetransaction.Itwillgenerallyreceivesdata
       postedbytheacquirerafterthetransaction.
    """
    _name='payment.transaction'
    _description='PaymentTransaction'
    _order='iddesc'
    _rec_name='reference'

    @api.model
    def_lang_get(self):
        returnself.env['res.lang'].get_installed()

    @api.model
    def_get_default_partner_country_id(self):
        returnself.env.company.country_id.id

    date=fields.Datetime('ValidationDate',readonly=True)
    acquirer_id=fields.Many2one('payment.acquirer',string='Acquirer',readonly=True,required=True)
    provider=fields.Selection(string='Provider',related='acquirer_id.provider',readonly=True)
    type=fields.Selection([
        ('validation','Validationofthebankcard'),
        ('server2server','ServerToServer'),
        ('form','Form'),
        ('form_save','Formwithtokenization')],'Type',
        default='form',required=True,readonly=True)
    state=fields.Selection([
        ('draft','Draft'),
        ('pending','Pending'),
        ('authorized','Authorized'),
        ('done','Done'),
        ('cancel','Canceled'),
        ('error','Error'),],
        string='Status',copy=False,default='draft',required=True,readonly=True)
    state_message=fields.Text(string='Message',readonly=True,
                                help='Fieldusedtostoreerrorand/orvalidationmessagesforinformation')
    amount=fields.Monetary(string='Amount',currency_field='currency_id',required=True,readonly=True)
    fees=fields.Monetary(string='Fees',currency_field='currency_id',readonly=True,
                           help='Feesamount;setbythesystembecausedependsontheacquirer')
    currency_id=fields.Many2one('res.currency','Currency',required=True,readonly=True)
    reference=fields.Char(string='Reference',required=True,readonly=True,index=True,
                            help='InternalreferenceoftheTX')
    acquirer_reference=fields.Char(string='AcquirerReference',readonly=True,help='ReferenceoftheTXasstoredintheacquirerdatabase')
    #duplicatepartner/transactiondatatostorethevaluesattransactiontime
    partner_id=fields.Many2one('res.partner','Customer')
    partner_name=fields.Char('PartnerName')
    partner_lang=fields.Selection(_lang_get,'Language',default=lambdaself:self.env.lang)
    partner_email=fields.Char('Email')
    partner_zip=fields.Char('Zip')
    partner_address=fields.Char('Address')
    partner_city=fields.Char('City')
    partner_country_id=fields.Many2one('res.country','Country',default=_get_default_partner_country_id,required=True)
    partner_phone=fields.Char('Phone')
    html_3ds=fields.Char('3DSecureHTML')

    callback_model_id=fields.Many2one('ir.model','CallbackDocumentModel',groups="base.group_system")
    callback_res_id=fields.Integer('CallbackDocumentID',groups="base.group_system")
    callback_method=fields.Char('CallbackMethod',groups="base.group_system")
    callback_hash=fields.Char('CallbackHash',groups="base.group_system")

    #Fieldsusedforuserredirection&paymentpostprocessing
    return_url=fields.Char('ReturnURLafterpayment')
    is_processed=fields.Boolean('Hasthepaymentbeenpostprocessed',default=False)

    #Fieldsusedforpayment.transactiontraceability.

    payment_token_id=fields.Many2one('payment.token','PaymentToken',readonly=True,
                                       domain="[('acquirer_id','=',acquirer_id)]")

    payment_id=fields.Many2one('account.payment',string='Payment',readonly=True)
    invoice_ids=fields.Many2many('account.move','account_invoice_transaction_rel','transaction_id','invoice_id',
        string='Invoices',copy=False,readonly=True,
        domain=[('move_type','in',('out_invoice','out_refund','in_invoice','in_refund'))])
    invoice_ids_nbr=fields.Integer(compute='_compute_invoice_ids_nbr',string='#ofInvoices')

    _sql_constraints=[
        ('reference_uniq','unique(reference)','Referencemustbeunique!'),
    ]

    @api.depends('invoice_ids')
    def_compute_invoice_ids_nbr(self):
        fortransinself:
            trans.invoice_ids_nbr=len(trans.invoice_ids)

    def_create_payment(self,add_payment_vals={}):
        '''Createanaccount.paymentrecordforthecurrentpayment.transaction.
        Ifthetransactionislinkedtosomeinvoices,thereconciliationwillbedoneautomatically.
        :paramadd_payment_vals:   Optionaladditionalvaluestobepassedtotheaccount.payment.createmethod.
        :return:                   Anaccount.paymentrecord.
        '''
        self.ensure_one()

        payment_vals={
            'amount':abs(self.amount),
            'payment_type':'inbound'ifself.amount>0else'outbound',
            'currency_id':self.currency_id.id,
            'partner_id':self.partner_id.commercial_partner_id.id,
            'partner_type':'customer',
            'journal_id':self.acquirer_id.journal_id.id,
            'company_id':self.acquirer_id.company_id.id,
            'payment_method_id':self.env.ref('payment.account_payment_method_electronic_in').id,
            'payment_token_id':self.payment_token_idandself.payment_token_id.idorNone,
            'payment_transaction_id':self.id,
            'ref':self.reference,
            **add_payment_vals,
        }
        payment=self.env['account.payment'].create(payment_vals)
        payment.action_post()

        #Trackthepaymenttomakeaone2one.
        self.payment_id=payment

        ifself.invoice_ids:
            self.invoice_ids.filtered(lambdamove:move.state=='draft')._post()

            (payment.line_ids+self.invoice_ids.line_ids)\
                .filtered(lambdaline:line.account_id==payment.destination_account_idandnotline.reconciled)\
                .reconcile()

        returnpayment

    defget_last_transaction(self):
        transactions=self.filtered(lambdat:t.state!='draft')
        returntransactionsandtransactions[0]ortransactions

    def_get_processing_info(self):
        """Extensiblemethodforprovidersiftheyneedspecificfields/inforegardingatxinthepaymentprocessingpage."""
        returndict()

    def_get_payment_transaction_sent_message(self):
        self.ensure_one()
        ifself.payment_token_id:
            message=_('Atransaction%swith%sinitiatedusing%screditcard.')
            message_vals=(self.reference,self.acquirer_id.name,self.payment_token_id.name)
        elifself.providerin('manual','transfer'):
            message=_('Thecustomerhasselected%stopaythisdocument.')
            message_vals=(self.acquirer_id.name)
        else:
            message=_('Atransaction%swith%sinitiated.')
            message_vals=(self.reference,self.acquirer_id.name)
        ifself.providernotin('manual','transfer'):
            message+=''+_('Waitingforpaymentconfirmation...')
        returnmessage%message_vals

    def_get_payment_transaction_received_message(self):
        self.ensure_one()
        amount=formatLang(self.env,self.amount,currency_obj=self.currency_id)
        message_vals=[self.reference,self.acquirer_id.name,amount]
        ifself.state=='pending':
            message=_('Thetransaction%swith%sfor%sispending.')
        elifself.state=='authorized':
            message=_('Thetransaction%swith%sfor%shasbeenauthorized.Waitingforcapture...')
        elifself.state=='done':
            message=_('Thetransaction%swith%sfor%shasbeenconfirmed.Therelatedpaymentisposted:%s')
            message_vals.append(self.payment_id._get_payment_chatter_link())
        elifself.state=='cancel'andself.state_message:
            message=_('Thetransaction%swith%sfor%shasbeencancelledwiththefollowingmessage:%s')
            message_vals.append(self.state_message)
        elifself.state=='error'andself.state_message:
            message=_('Thetransaction%swith%sfor%shasreturnfailedwiththefollowingerrormessage:%s')
            message_vals.append(self.state_message)
        else:
            message=_('Thetransaction%swith%sfor%shasbeencancelled.')
        returnmessage%tuple(message_vals)

    def_log_payment_transaction_sent(self):
        '''Logthemessagesayingthetransactionhasbeensenttotheremoteservertobe
        processedbytheacquirer.
        '''
        fortransinself:
            post_message=trans._get_payment_transaction_sent_message()
            forinvintrans.invoice_ids:
                inv.message_post(body=post_message)

    def_log_payment_transaction_received(self):
        '''Logthemessagesayingaresponsehasbeenreceivedfromtheremoteserverandsome
        additionalinformationsliketheold/newstate,thereferenceofthepayment...etc.
        :paramold_state:      Thestateofthetransactionbeforetheresponse.
        :paramadd_messages:   Optionaladditionalmessagestologlikethecapturestatus.
        '''
        fortransinself.filtered(lambdat:t.providernotin('manual','transfer')):
            post_message=trans._get_payment_transaction_received_message()
            forinvintrans.invoice_ids:
                inv.message_post(body=post_message)

    def_filter_transaction_state(self,allowed_states,target_state):
        """Divideasetoftransactionsaccordingtotheirstate.

        :paramtuple(string)allowed_states:tupleofallowedstatesforthetargetstate(strings)
        :paramstringtarget_state:targetstateforthefiltering
        :return:tupleoftransactionsdividedbytheirstate,inthatorder
                    tx_to_process:txthatwereintheallowedstates
                    tx_already_processed:txthatwerealreadyinthetargetstate
                    tx_wrong_state:txthatwerenotintheallowedstateforthetransition
        :rtype:tuple(recordset)
        """
        tx_to_process=self.filtered(lambdatx:tx.stateinallowed_states)
        tx_already_processed=self.filtered(lambdatx:tx.state==target_state)
        tx_wrong_state=self-tx_to_process-tx_already_processed
        return(tx_to_process,tx_already_processed,tx_wrong_state)

    def_set_transaction_pending(self):
        '''Movethetransactiontothependingstate(e.g.WireTransfer).'''
        allowed_states=('draft',)
        target_state='pending'
        (tx_to_process,tx_already_processed,tx_wrong_state)=self._filter_transaction_state(allowed_states,target_state)
        fortxintx_already_processed:
            _logger.info('Tryingtowritethesamestatetwiceontx(ref:%s,state:%s'%(tx.reference,tx.state))
        fortxintx_wrong_state:
            _logger.warning('Processedtxwithabnormalstate(ref:%s,targetstate:%s,previousstate%s,expectedpreviousstates:%s)'%(tx.reference,target_state,tx.state,allowed_states))

        tx_to_process.write({
            'state':target_state,
            'date':fields.Datetime.now(),
            'state_message':'',
        })
        tx_to_process._log_payment_transaction_received()

    def_set_transaction_authorized(self):
        '''Movethetransactiontotheauthorizedstate(e.g.Authorize).'''
        allowed_states=('draft','pending')
        target_state='authorized'
        (tx_to_process,tx_already_processed,tx_wrong_state)=self._filter_transaction_state(allowed_states,target_state)
        fortxintx_already_processed:
            _logger.info('Tryingtowritethesamestatetwiceontx(ref:%s,state:%s'%(tx.reference,tx.state))
        fortxintx_wrong_state:
            _logger.warning('Processedtxwithabnormalstate(ref:%s,targetstate:%s,previousstate%s,expectedpreviousstates:%s)'%(tx.reference,target_state,tx.state,allowed_states))
        tx_to_process.write({
            'state':target_state,
            'date':fields.Datetime.now(),
            'state_message':'',
        })
        tx_to_process._log_payment_transaction_received()

    def_set_transaction_done(self):
        '''Movethetransaction'spaymenttothedonestate(e.g.Paypal).'''
        allowed_states=('draft','authorized','pending','error')
        target_state='done'
        (tx_to_process,tx_already_processed,tx_wrong_state)=self._filter_transaction_state(allowed_states,target_state)
        fortxintx_already_processed:
            _logger.info('Tryingtowritethesamestatetwiceontx(ref:%s,state:%s'%(tx.reference,tx.state))
        fortxintx_wrong_state:
            _logger.warning('Processedtxwithabnormalstate(ref:%s,targetstate:%s,previousstate%s,expectedpreviousstates:%s)'%(tx.reference,target_state,tx.state,allowed_states))

        tx_to_process.write({
            'state':target_state,
            'date':fields.Datetime.now(),
            'state_message':'',
        })

    def_reconcile_after_transaction_done(self):
        #Validateinvoicesautomaticallyuponthetransactionisposted.
        invoices=self.mapped('invoice_ids').filtered(lambdainv:inv.state=='draft')
        invoices._post()

        #Create&Postthepayments.
        fortransinself:
            iftrans.payment_id:
                continue

            trans._create_payment()

    def_set_transaction_cancel(self):
        '''Movethetransaction'spaymenttothecancelstate(e.g.Paypal).'''
        allowed_states=('draft','authorized')
        target_state='cancel'
        (tx_to_process,tx_already_processed,tx_wrong_state)=self._filter_transaction_state(allowed_states,target_state)
        fortxintx_already_processed:
            _logger.info('Tryingtowritethesamestatetwiceontx(ref:%s,state:%s'%(tx.reference,tx.state))
        fortxintx_wrong_state:
            _logger.warning('Processedtxwithabnormalstate(ref:%s,targetstate:%s,previousstate%s,expectedpreviousstates:%s)'%(tx.reference,target_state,tx.state,allowed_states))

        #Canceltheexistingpayments.
        tx_to_process.mapped('payment_id').action_cancel()

        tx_to_process.write({'state':target_state,'date':fields.Datetime.now()})
        tx_to_process._log_payment_transaction_received()

    def_set_transaction_error(self,msg):
        '''Movethetransactiontotheerrorstate(Thirdpartyreturningerrore.g.Paypal).'''
        allowed_states=('draft','authorized','pending')
        target_state='error'
        (tx_to_process,tx_already_processed,tx_wrong_state)=self._filter_transaction_state(allowed_states,target_state)
        fortxintx_already_processed:
            _logger.info('Tryingtowritethesamestatetwiceontx(ref:%s,state:%s'%(tx.reference,tx.state))
        fortxintx_wrong_state:
            _logger.warning('Processedtxwithabnormalstate(ref:%s,targetstate:%s,previousstate%s,expectedpreviousstates:%s)'%(tx.reference,target_state,tx.state,allowed_states))

        tx_to_process.write({
            'state':target_state,
            'date':fields.Datetime.now(),
            'state_message':msg,
        })
        tx_to_process._log_payment_transaction_received()

    def_post_process_after_done(self):
        self._reconcile_after_transaction_done()
        self._log_payment_transaction_received()
        self.write({'is_processed':True})
        returnTrue

    def_cron_post_process_after_done(self):
        ifnotself:
            ten_minutes_ago=datetime.now()-relativedelta.relativedelta(minutes=10)
            #wedon'twanttoforevertrytoprocessatransactionthatdoesn'tgothrough
            #asforPaypal,itsometimetakes3or4daysforpaymentverificationduetoweekend.Set4hereshouldbefine.
            retry_limit_date=datetime.now()-relativedelta.relativedelta(days=4)
            #weretrieveallthepaymenttxthatneedtobepostprocessed
            self=self.search([('state','=','done'),
                                ('is_processed','=',False),
                                ('date','<=',ten_minutes_ago),
                                ('date','>=',retry_limit_date),
                            ])
        fortxinself:
            try:
                tx._post_process_after_done()
                self.env.cr.commit()
            exceptExceptionase:
                _logger.exception("Transactionpostprocessingfailed")
                self.env.cr.rollback()

    @api.model
    def_compute_reference_prefix(self,values):
        ifvaluesandvalues.get('invoice_ids'):
            invoices=self.new({'invoice_ids':values['invoice_ids']}).invoice_ids
            return','.join(invoices.mapped('name'))
        returnNone

    @api.model
    def_compute_reference(self,values=None,prefix=None):
        '''Computeauniquereferenceforthetransaction.
        Ifprefix:
            prefix-\d+
        Ifsomeinvoices:
            <inv_number_0>.number,<inv_number_1>,...,<inv_number_n>-x
        Ifsomesaleorders:
            <so_name_0>.number,<so_name_1>,...,<so_name_n>-x
        Else:
            tx-\d+
        :paramvalues:valuesusedtocreateanewtransaction.
        :paramprefix:customtransactionprefix.
        :return:Auniquereferenceforthetransaction.
        '''
        ifnotprefix:
            prefix=self._compute_reference_prefix(values)
            ifnotprefix:
                prefix='tx'

        #Fetchthelastreference
        #E.g.IfthelastreferenceisSO42-5,thisquerywillreturn'-5'
        self._cr.execute('''
                SELECTCAST(SUBSTRING(referenceFROM'-\d+$')ASINTEGER)ASsuffix
                FROMpayment_transactionWHEREreferenceLIKE%sORDERBYsuffix
            ''',[prefix+'-%'])
        query_res=self._cr.fetchone()
        ifquery_res:
            #Incrementthelastreferencebyone
            suffix='%s'%(-query_res[0]+1)
        else:
            #Startanewindexingfrom1
            suffix='1'

        return'%s-%s'%(prefix,suffix)

    defaction_view_invoices(self):
        action={
            'name':_('Invoices'),
            'type':'ir.actions.act_window',
            'res_model':'account.move',
            'target':'current',
        }
        invoice_ids=self.invoice_ids.ids
        iflen(invoice_ids)==1:
            invoice=invoice_ids[0]
            action['res_id']=invoice
            action['view_mode']='form'
            form_view=[(self.env.ref('account.view_move_form').id,'form')]
            if'views'inaction:
                action['views']=form_view+[(state,view)forstate,viewinaction['views']ifview!='form']
            else:
                action['views']=form_view
        else:
            action['view_mode']='tree,form'
            action['domain']=[('id','in',invoice_ids)]
        returnaction

    @api.constrains('state','acquirer_id')
    def_check_authorize_state(self):
        failed_tx=self.filtered(lambdatx:tx.state=='authorized'andtx.acquirer_id.providernotinself.env['payment.acquirer']._get_feature_support()['authorize'])
        iffailed_tx:
            raiseexceptions.ValidationError(_('The%spaymentacquirersarenotallowedtomanualcapturemode!',failed_tx.mapped('acquirer_id.name')))

    @api.model
    defcreate(self,values):
        #callcustomcreatemethodifdefined
        acquirer=self.env['payment.acquirer'].browse(values['acquirer_id'])
        ifvalues.get('partner_id'):
            partner=self.env['res.partner'].browse(values['partner_id'])

            values.update({
                'partner_name':partner.name,
                'partner_lang':partner.langorself.env.user.lang,
                'partner_email':partner.email,
                'partner_zip':partner.zip,
                'partner_address':_partner_format_address(partner.streetor'',partner.street2or''),
                'partner_city':partner.city,
                'partner_country_id':partner.country_id.idorself._get_default_partner_country_id(),
                'partner_phone':partner.phone,
            })

        #computefees
        custom_method_name='%s_compute_fees'%acquirer.provider
        ifhasattr(acquirer,custom_method_name):
            fees=getattr(acquirer,custom_method_name)(
                values.get('amount',0.0),values.get('currency_id'),values.get('partner_country_id',self._get_default_partner_country_id()))
            values['fees']=fees

        #customcreate
        custom_method_name='%s_create'%acquirer.provider
        ifhasattr(self,custom_method_name):
            values.update(getattr(self,custom_method_name)(values))

        ifnotvalues.get('reference'):
            values['reference']=self._compute_reference(values=values)

        #Defaultvalueofreferenceis
        tx=super(PaymentTransaction,self).create(values)

        #Generatecallbackhashifitisconfiguredonthetx;avoidgeneratingunnecessarystuff
        #(limitedsudoenvforcheckingcallbackpresence,mustworkformanualtransactionstoo)
        tx_sudo=tx.sudo()
        iftx_sudo.callback_model_idandtx_sudo.callback_res_idandtx_sudo.callback_method:
            tx.write({'callback_hash':tx._generate_callback_hash()})

        returntx

    def_generate_callback_hash(self):
        self.ensure_one()
        secret=self.env['ir.config_parameter'].sudo().get_param('database.secret')
        token='%s%s%s'%(self.callback_model_id.model,
                            self.callback_res_id,
                            self.sudo().callback_method)
        returnhmac.new(secret.encode('utf-8'),token.encode('utf-8'),hashlib.sha256).hexdigest()

    #--------------------------------------------------
    #FORMRELATEDMETHODS
    #--------------------------------------------------

    @api.model
    defform_feedback(self,data,acquirer_name):
        invalid_parameters,tx=None,None

        tx_find_method_name='_%s_form_get_tx_from_data'%acquirer_name
        ifhasattr(self,tx_find_method_name):
            tx=getattr(self,tx_find_method_name)(data)

        #TDETODO:form_get_invalid_parametersfrommodeltomulti
        invalid_param_method_name='_%s_form_get_invalid_parameters'%acquirer_name
        ifhasattr(self,invalid_param_method_name):
            invalid_parameters=getattr(tx,invalid_param_method_name)(data)

        ifinvalid_parameters:
            _error_message='%s:incorrecttxdata:\n'%(acquirer_name)
            foritemininvalid_parameters:
                _error_message+='\t%s:received%sinsteadof%s\n'%(item[0],item[1],item[2])
            _logger.error(_error_message)
            returnFalse

        #TDETODO:form_validatefrommodeltomulti
        feedback_method_name='_%s_form_validate'%acquirer_name
        ifhasattr(self,feedback_method_name):
            returngetattr(tx,feedback_method_name)(data)

        returnTrue

    #--------------------------------------------------
    #SERVER2SERVERRELATEDMETHODS
    #--------------------------------------------------

    defs2s_do_transaction(self,**kwargs):
        custom_method_name='%s_s2s_do_transaction'%self.acquirer_id.provider
        fortransinself:
            trans._log_payment_transaction_sent()
            ifhasattr(trans,custom_method_name):
                returngetattr(trans,custom_method_name)(**kwargs)

    defs2s_do_refund(self,**kwargs):
        custom_method_name='%s_s2s_do_refund'%self.acquirer_id.provider
        ifhasattr(self,custom_method_name):
            returngetattr(self,custom_method_name)(**kwargs)

    defs2s_capture_transaction(self,**kwargs):
        custom_method_name='%s_s2s_capture_transaction'%self.acquirer_id.provider
        ifhasattr(self,custom_method_name):
            returngetattr(self,custom_method_name)(**kwargs)

    defs2s_void_transaction(self,**kwargs):
        custom_method_name='%s_s2s_void_transaction'%self.acquirer_id.provider
        ifhasattr(self,custom_method_name):
            returngetattr(self,custom_method_name)(**kwargs)

    defs2s_get_tx_status(self):
        """Getthetxstatus."""
        invalid_param_method_name='_%s_s2s_get_tx_status'%self.acquirer_id.provider
        ifhasattr(self,invalid_param_method_name):
            returngetattr(self,invalid_param_method_name)()
        returnTrue

    defexecute_callback(self):
        res=None
        fortransactioninself:
            #limitedsudoenv,onlyforcheckingcallbackpresence,notforrunningit!
            #manualtransactionshavenocallback,andcanpasswithoutbeingrunbyadminuser
            tx_sudo=transaction.sudo()
            ifnot(tx_sudo.callback_model_idandtx_sudo.callback_res_idandtx_sudo.callback_method):
                continue

            valid_token=transaction._generate_callback_hash()
            ifnotconsteq(ustr(valid_token),transaction.callback_hash):
                _logger.warning("Invalidcallbacksignaturefortransaction%d"%(transaction.id))
                continue

            record=self.env[transaction.callback_model_id.model].browse(transaction.callback_res_id).exists()
            ifrecord:
                res=getattr(record,transaction.callback_method)(transaction)
            else:
                _logger.warning("Didnotfoundrecord%s.%sforcallbackoftransaction%d"%(transaction.callback_model_id.model,transaction.callback_res_id,transaction.id))
        returnres

    defaction_capture(self):
        ifany(t.state!='authorized'fortinself):
            raiseValidationError(_('Onlytransactionshavingtheauthorizedstatuscanbecaptured.'))
        fortxinself:
            tx.s2s_capture_transaction()

    defaction_void(self):
        ifany(t.state!='authorized'fortinself):
            raiseValidationError(_('Onlytransactionshavingthecapturestatuscanbevoided.'))
        fortxinself:
            tx.s2s_void_transaction()


classPaymentToken(models.Model):
    _name='payment.token'
    _order='partner_id,iddesc'
    _description='PaymentToken'

    name=fields.Char('Name',help='Nameofthepaymenttoken')
    short_name=fields.Char('Shortname',compute='_compute_short_name')
    partner_id=fields.Many2one('res.partner','Partner',required=True)
    acquirer_id=fields.Many2one('payment.acquirer','AcquirerAccount',required=True)
    company_id=fields.Many2one(related='acquirer_id.company_id',store=True,index=True)
    acquirer_ref=fields.Char('AcquirerRef.',required=True)
    active=fields.Boolean('Active',default=True)
    payment_ids=fields.One2many('payment.transaction','payment_token_id','PaymentTransactions')
    verified=fields.Boolean(string='Verified',default=False)

    @api.model
    defcreate(self,values):
        #callcustomcreatemethodifdefined
        ifvalues.get('acquirer_id'):
            acquirer=self.env['payment.acquirer'].browse(values['acquirer_id'])

            #customcreate
            custom_method_name='%s_create'%acquirer.provider
            ifhasattr(self,custom_method_name):
                values.update(getattr(self,custom_method_name)(values))
                #removeallnon-modelfieldsusedby(provider)_createmethodtoavoidwarning
                fields_wl=set(self._fields)&set(values)
                values={field:values[field]forfieldinfields_wl}
        returnsuper(PaymentToken,self).create(values)
    """
        @TBE:stolenshamelesslyfromtherehttps://www.paypal.com/us/selfhelp/article/why-is-there-a-$1.95-charge-on-my-card-statement-faq554
        Mostofthemare~1.50€s
    """
    VALIDATION_AMOUNTS={
        'CAD':2.45,
        'EUR':1.50,
        'GBP':1.00,
        'JPY':200,
        'AUD':2.00,
        'NZD':3.00,
        'CHF':3.00,
        'HKD':15.00,
        'SEK':15.00,
        'DKK':12.50,
        'PLN':6.50,
        'NOK':15.00,
        'HUF':400.00,
        'CZK':50.00,
        'BRL':4.00,
        'MYR':10.00,
        'MXN':20.00,
        'ILS':8.00,
        'PHP':100.00,
        'TWD':70.00,
        'THB':70.00
        }

    @api.model
    defvalidate(self,**kwargs):
        """
            Thismethodallowtoverifyifthispaymentmethodisvalidornot.
            Itdoesthisbywithdrawingacertainamountandthenrefunditrightafter.
        """
        currency=self.partner_id.currency_id

        ifself.VALIDATION_AMOUNTS.get(currency.name):
            amount=self.VALIDATION_AMOUNTS.get(currency.name)
        else:
            #Ifwedon'tfindtheuser'scurrency,thenwesetthecurrencytoEURandtheamountto1€50.
            currency=self.env['res.currency'].search([('name','=','EUR')])
            amount=1.5

        iflen(currency)!=1:
            _logger.error("Error'EUR'currencynotfoundforpaymentmethodvalidation!")
            returnFalse

        reference="VALIDATION-%s-%s"%(self.id,datetime.now().strftime('%y%m%d_%H%M%S'))
        tx=self.env['payment.transaction'].sudo().create({
            'amount':amount,
            'acquirer_id':self.acquirer_id.id,
            'type':'validation',
            'currency_id':currency.id,
            'reference':reference,
            'payment_token_id':self.id,
            'partner_id':self.partner_id.id,
            'partner_country_id':self.partner_id.country_id.id,
            'state_message':_('ThisTransactionwasautomaticallyprocessed&refundedinordertovalidateanewcreditcard.'),
        })

        kwargs.update({'3d_secure':True})
        tx.s2s_do_transaction(**kwargs)

        #if3Dsecureiscalled,thenwedonotrefundrightnow
        ifnottx.html_3ds:
            tx.s2s_do_refund()

        returntx

    @api.depends('name')
    def_compute_short_name(self):
        fortokeninself:
            token.short_name=token.name.replace('XXXXXXXXXXXX','***')

    defget_linked_records(self):
        """Thismethodreturnsadictcontainingalltherecordslinkedtothepayment.token(e.gSubscriptions),
            thekeyistheidofthepayment.tokenandthevalueisanarraythatmustfollowtheschemebelow.

            {
                token_id:[
                    'description':Themodeldescription(e.g'SaleSubscription'),
                    'id':Theidoftherecord,
                    'name':Thenameoftherecord,
                    'url':Theurltoaccesstothisrecord.
                ]
            }
        """
        return{r.id:[]forrinself}
