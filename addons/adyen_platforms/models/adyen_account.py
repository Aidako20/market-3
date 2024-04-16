#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importos
importrequests
importuuid
fromwerkzeug.urlsimporturl_join

fromflectraimportapi,fields,models,_
fromflectra.httpimportrequest
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.toolsimportdate_utils

fromflectra.addons.adyen_platforms.utilimportAdyenProxyAuth

ADYEN_AVAILABLE_COUNTRIES=['US','AT','AU','BE','CA','CH','CZ','DE','ES','FI','FR','GB','GR','HR','IE','IT','LT','LU','NL','PL','PT']
TIMEOUT=60


classAdyenAddressMixin(models.AbstractModel):
    _name='adyen.address.mixin'
    _description='AdyenforPlatformsAddressMixin'

    country_id=fields.Many2one('res.country',string='Country',domain=[('code','in',ADYEN_AVAILABLE_COUNTRIES)],required=True)
    country_code=fields.Char(related='country_id.code')
    state_id=fields.Many2one('res.country.state',string='State',domain="[('country_id','=?',country_id)]")
    state_code=fields.Char(related='state_id.code')
    city=fields.Char('City',required=True)
    zip=fields.Char('ZIP',required=True)
    street=fields.Char('Street',required=True)
    house_number_or_name=fields.Char('HouseNumberOrName',required=True)


classAdyenIDMixin(models.AbstractModel):
    _name='adyen.id.mixin'
    _description='AdyenforPlatformsIDMixin'

    id_type=fields.Selection(string='PhotoIDtype',selection=[
        ('PASSPORT','Passport'),
        ('ID_CARD','IDCard'),
        ('DRIVING_LICENSE','DrivingLicense'),
    ])
    id_front=fields.Binary('PhotoIDFront',help="Allowedformats:jpg,pdf,png.Maximumallowedsize:4MB.")
    id_front_filename=fields.Char()
    id_back=fields.Binary('PhotoIDBack',help="Allowedformats:jpg,pdf,png.Maximumallowedsize:4MB.")
    id_back_filename=fields.Char()

    defwrite(self,vals):
        res=super(AdyenIDMixin,self).write(vals)

        #Checkfileformats
        ifvals.get('id_front'):
            self._check_file_requirements(vals.get('id_front'),vals.get('id_front_filename'))
        ifvals.get('id_back'):
            self._check_file_requirements(vals.get('id_back'),vals.get('id_back_filename'))

        foradyen_accountinself:
            ifvals.get('id_front'):
                document_type=adyen_account.id_type
                ifadyen_account.id_typein['ID_CARD','DRIVING_LICENSE']:
                    document_type+='_FRONT'
                adyen_account._upload_photo_id(document_type,adyen_account.id_front,adyen_account.id_front_filename)
            ifvals.get('id_back')andadyen_account.id_typein['ID_CARD','DRIVING_LICENSE']:
                document_type=adyen_account.id_type+'_BACK'
                adyen_account._upload_photo_id(document_type,adyen_account.id_back,adyen_account.id_back_filename)
            returnres

    @api.model
    def_check_file_requirements(self,content,filename):
        file_extension=os.path.splitext(filename)[1]
        file_size=int(len(content)*3/4)#Computefile_sizeinbytes
        iffile_extensionnotin['.jpeg','.jpg','.pdf','.png']:
            raiseValidationError(_('AllowedfileformatsforphotoIDsarejpeg,jpg,pdforpng'))
        iffile_size>>20>4or(file_size>>10<1andfile_extension=='.pdf')or(file_size>>10<100andfile_extension!='.pdf'):
            raiseValidationError(_('PhotoIDfilesizemustbebetween100kB(1kBforPDFs)and4MB'))

    def_upload_photo_id(self,document_type,content,filename):
        #TherequesttobesenttoAdyenwillbedifferentforIndividuals,
        #Shareholders,etc.Thismethodshouldbeimplementedbythemodels
        #inheritingthismixin
        raiseNotImplementedError()


classAdyenAccount(models.Model):
    _name='adyen.account'
    _inherit=['mail.thread','adyen.id.mixin','adyen.address.mixin']

    _description='AdyenforPlatformsAccount'
    _rec_name='full_name'

    #Credentials
    proxy_token=fields.Char('ProxyToken')
    adyen_uuid=fields.Char('AdyenUUID')
    account_holder_code=fields.Char('AccountHolderCode',default=lambdaself:uuid.uuid4().hex)

    company_id=fields.Many2one('res.company',default=lambdaself:self.env.company)
    payout_ids=fields.One2many('adyen.payout','adyen_account_id',string='Payouts')
    shareholder_ids=fields.One2many('adyen.shareholder','adyen_account_id',string='Shareholders')
    bank_account_ids=fields.One2many('adyen.bank.account','adyen_account_id',string='BankAccounts')
    transaction_ids=fields.One2many('adyen.transaction','adyen_account_id',string='Transactions')
    transactions_count=fields.Integer(compute='_compute_transactions_count')

    is_business=fields.Boolean('Isabusiness',required=True)

    #ContactInfo
    full_name=fields.Char(compute='_compute_full_name')
    email=fields.Char('Email',required=True)
    phone_number=fields.Char('PhoneNumber',required=True)

    #Individual
    first_name=fields.Char('FirstName')
    last_name=fields.Char('LastName')
    date_of_birth=fields.Date('Dateofbirth')
    document_number=fields.Char('IDNumber',
        help="ThetypeofIDNumberrequireddependsonthecountry:\n"
             "US:SocialSecurityNumber(9digitsorlast4digits)\n"
             "Canada:SocialInsuranceNumber\nItaly:Codicefiscale\n"
             "Australia:DocumentNumber")
    document_type=fields.Selection(string='DocumentType',selection=[
        ('ID','ID'),
        ('PASSPORT','Passport'),
        ('VISA','Visa'),
        ('DRIVINGLICENSE','Drivinglicense'),
    ],default='ID')

    #Business
    legal_business_name=fields.Char('LegalBusinessName')
    doing_business_as=fields.Char('DoingBusinessAs')
    registration_number=fields.Char('RegistrationNumber')

    #KYC
    kyc_status=fields.Selection(string='KYCStatus',selection=[
        ('awaiting_data','Datatoprovide'),
        ('pending','Waitingforvalidation'),
        ('passed','Confirmed'),
        ('failed','Failed'),
    ],required=True,default='pending')
    kyc_status_message=fields.Char('KYCStatusMessage',readonly=True)

    _sql_constraints=[
        ('adyen_uuid_uniq','UNIQUE(adyen_uuid)','AdyenUUIDshouldbeunique'),
    ]

    @api.depends('transaction_ids')
    def_compute_transactions_count(self):
        foradyen_account_idinself:
            adyen_account_id.transactions_count=len(adyen_account_id.transaction_ids)

    @api.depends('first_name','last_name','legal_business_name')
    def_compute_full_name(self):
        foradyen_account_idinself:
            ifadyen_account_id.is_business:
                adyen_account_id.full_name=adyen_account_id.legal_business_name
            else:
                adyen_account_id.full_name="%s%s"%(adyen_account_id.first_name,adyen_account_id.last_name)

    @api.model
    defcreate(self,values):
        adyen_account_id=super(AdyenAccount,self).create(values)
        self.env.company.adyen_account_id=adyen_account_id.id

        #Createaccountonflectrahq.com,proxyandAdyen
        response=adyen_account_id._adyen_rpc('create_account_holder',adyen_account_id._format_data())

        #Saveadyen_uuidandproxy_token,thathavebeengeneratedbyflectrahq.comandtheproxy
        adyen_account_id.with_context(update_from_adyen=True).write({
            'adyen_uuid':response['adyen_uuid'],
            'proxy_token':response['proxy_token'],
        })

        #Adefaultpayoutiscreatedforalladyenaccounts
        adyen_account_id.env['adyen.payout'].with_context(update_from_adyen=True).create({
            'code':response['adyen_response']['accountCode'],
            'adyen_account_id':adyen_account_id.id,
        })
        returnadyen_account_id

    defwrite(self,vals):
        res=super(AdyenAccount,self).write(vals)
        ifnotself.env.context.get('update_from_adyen'):
            self._adyen_rpc('update_account_holder',self._format_data())
        returnres

    defunlink(self):
        foradyen_account_idinself:
            adyen_account_id._adyen_rpc('close_account_holder',{
                'accountHolderCode':adyen_account_id.account_holder_code,
            })
        returnsuper(AdyenAccount,self).unlink()

    @api.model
    defaction_create_redirect(self):
        '''
        AccessingtheFormViewtocreateanAdyenaccountneedstobedonethroughthisaction.
        Theactionwillredirecttheusertoaccounts.flectrahq.comtolinkanFlectrauser_idtotheAdyen
        account.Afterlogginginonflectrahq.comtheuserwillberedirectedtohisDBwithatokenin
        theURL.ThistokenisthenneededtocreatetheAdyenaccount.
        '''
        ifself.env.company.adyen_account_id:
            #Anaccountalreadyexists,showit
            return{
                'name':_('AdyenAccount'),
                'view_mode':'form',
                'res_model':'adyen.account',
                'res_id':self.env.company.adyen_account_id.id,
                'type':'ir.actions.act_window',
            }
        return_url=url_join(self.env['ir.config_parameter'].sudo().get_param('web.base.url'),'adyen_platforms/create_account')
        onboarding_url=self.env['ir.config_parameter'].sudo().get_param('adyen_platforms.onboarding_url')
        return{
            'type':'ir.actions.act_url',
            'url':url_join(onboarding_url,'get_creation_token?return_url=%s'%return_url),
        }

    defaction_show_transactions(self):
        return{
            'name':_('Transactions'),
            'view_mode':'tree,form',
            'domain':[('adyen_account_id','=',self.id)],
            'res_model':'adyen.transaction',
            'type':'ir.actions.act_window',
            'context':{'group_by':['adyen_payout_id']}
        }

    def_upload_photo_id(self,document_type,content,filename):
        self._adyen_rpc('upload_document',{
            'documentDetail':{
                'accountHolderCode':self.account_holder_code,
                'documentType':document_type,
                'filename':filename,
            },
            'documentContent':content.decode(),
        })

    def_format_data(self):
        data={
            'accountHolderCode':self.account_holder_code,
            'accountHolderDetails':{
                'address':{
                    'country':self.country_id.code,
                    'stateOrProvince':self.state_id.codeorNone,
                    'city':self.city,
                    'postalCode':self.zip,
                    'street':self.street,
                    'houseNumberOrName':self.house_number_or_name,
                },
                'email':self.email,
                'fullPhoneNumber':self.phone_number,
            },
            'legalEntity':'Business'ifself.is_businesselse'Individual',
        }

        ifself.is_business:
            data['accountHolderDetails']['businessDetails']={
                'legalBusinessName':self.legal_business_name,
                'doingBusinessAs':self.doing_business_as,
                'registrationNumber':self.registration_number,
            }
        else:
            data['accountHolderDetails']['individualDetails']={
                'name':{
                    'firstName':self.first_name,
                    'lastName':self.last_name,
                    'gender':'UNKNOWN',
                },
                'personalData':{
                    'dateOfBirth':str(self.date_of_birth),
                }
            }

            #documentDatacannotbepresentinthedataifnotset
            ifself.document_number:
                data['accountHolderDetails']['individualDetails']['personalData']['documentData']=[{
                    'number':self.document_number,
                    'type':self.document_type,
                }]

        returndata

    def_adyen_rpc(self,operation,adyen_data={}):
        ifoperation=='create_account_holder':
            url=self.env['ir.config_parameter'].sudo().get_param('adyen_platforms.onboarding_url')
            params={
                'creation_token':request.session.get('adyen_creation_token'),
                'adyen_data':adyen_data,
            }
            auth=None
        else:
            url=self.env['ir.config_parameter'].sudo().get_param('adyen_platforms.proxy_url')
            params={
                'adyen_uuid':self.adyen_uuid,
                'adyen_data':adyen_data,
            }
            auth=AdyenProxyAuth(self)

        payload={
            'jsonrpc':'2.0',
            'params':params,
        }
        try:
            req=requests.post(url_join(url,operation),json=payload,auth=auth,timeout=TIMEOUT)
            req.raise_for_status()
        exceptrequests.exceptions.Timeout:
            raiseUserError(_('AtimeoutoccuredwhiletryingtoreachtheAdyenproxy.'))
        exceptExceptionase:
            raiseUserError(_('TheAdyenproxyisnotreachable,pleasetryagainlater.'))
        response=req.json()

        if'error'inresponse:
            name=response['error']['data'].get('name').rpartition('.')[-1]
            ifname=='ValidationError':
                raiseValidationError(response['error']['data'].get('arguments')[0])
            else:
                raiseUserError(_("WehadtroublesreachingAdyen,pleaseretrylaterorcontactthesupportiftheproblempersists"))

        result=response.get('result')
        if'verification'inresult:
            self._update_kyc_status(result['verification'])

        returnresult

    @api.model
    def_sync_adyen_cron(self):
        self._sync_adyen_kyc_status()
        self.env['adyen.transaction'].sync_adyen_transactions()
        self.env['adyen.payout']._process_payouts()

    @api.model
    def_sync_adyen_kyc_status(self):
        foradyen_account_idinself.search([]):
            data=adyen_account_id._adyen_rpc('get_account_holder',{
                'accountHolderCode':adyen_account_id.account_holder_code,
            })
            adyen_account_id._update_kyc_status(data['verification'])

    def_update_kyc_status(self,checks):
        all_checks_status=[]

        #AccountHolderChecks
        account_holder_checks=checks.get('accountHolder',{})
        account_holder_messages=[]
        forcheckinaccount_holder_checks.get('checks'):
            all_checks_status.append(check['status'])
            kyc_status_message=self._get_kyc_message(check)
            ifkyc_status_message:
                account_holder_messages.append(kyc_status_message)

        #ShareholdersChecks
        shareholder_checks=checks.get('shareholders',{})
        shareholder_messages=[]
        kyc_status_message=False
        forscinshareholder_checks:
            shareholder_status=[]
            shareholder_id=self.shareholder_ids.filtered(lambdashareholder:shareholder.shareholder_uuid==sc['shareholderCode'])
            forcheckinsc.get('checks'):
                all_checks_status.append(check['status'])
                shareholder_status.append(check['status'])
                kyc_status_message=self._get_kyc_message(check)
                ifkyc_status_message:
                    shareholder_messages.append('[%s]%s'%(shareholder_id.display_name,kyc_status_message))
            shareholder_id.with_context(update_from_adyen=True).write({
                'kyc_status':self.get_status(shareholder_status),
                'kyc_status_message':kyc_status_message,
            })

        #BankAccountChecks
        bank_account_checks=checks.get('bankAccounts',{})
        bank_account_messages=[]
        kyc_status_message=False
        forbacinbank_account_checks:
            bank_account_status=[]
            bank_account_id=self.bank_account_ids.filtered(lambdabank_account:bank_account.bank_account_uuid==bac['bankAccountUUID'])
            forcheckinbac.get('checks'):
                all_checks_status.append(check['status'])
                bank_account_status.append(check['status'])
                kyc_status_message=self._get_kyc_message(check)
                ifkyc_status_message:
                    bank_account_messages.append('[%s]%s'%(bank_account_id.display_name,kyc_status_message))
            bank_account_id.with_context(update_from_adyen=True).write({
                'kyc_status':self.get_status(bank_account_status),
                'kyc_status_message':kyc_status_message,
            })

        kyc_status=self.get_status(all_checks_status)
        kyc_status_message=self.env['ir.qweb']._render('adyen_platforms.kyc_status_message',{
            'kyc_status':dict(self._fields['kyc_status'].selection)[kyc_status],
            'account_holder_messages':account_holder_messages,
            'shareholder_messages':shareholder_messages,
            'bank_account_messages':bank_account_messages,
        })

        ifkyc_status_message.decode()!=self.kyc_status_message:
            self.sudo().message_post(body=kyc_status_message,subtype_xmlid="mail.mt_comment")#MessagefromFlectraBot

        self.with_context(update_from_adyen=True).write({
            'kyc_status':kyc_status,
            'kyc_status_message':kyc_status_message,
        })

    @api.model
    defget_status(self,statuses):
        ifany(statusin['FAILED']forstatusinstatuses):
            return'failed'
        ifany(statusin['INVALID_DATA','RETRY_LIMIT_REACHED','AWAITING_DATA']forstatusinstatuses):
            return'awaiting_data'
        ifany(statusin['DATA_PROVIDED','PENDING']forstatusinstatuses):
            return'pending'
        return'passed'

    @api.model
    def_get_kyc_message(self,check):
        ifcheck.get('summary',{}).get('kycCheckDescription'):
            returncheck['summary']['kycCheckDescription']
        ifcheck.get('requiredFields',{}):
            return_('Missingrequiredfields:')+','.join(check.get('requiredFields'))
        return''


classAdyenShareholder(models.Model):
    _name='adyen.shareholder'
    _inherit=['adyen.id.mixin','adyen.address.mixin']
    _description='AdyenforPlatformsShareholder'
    _rec_name='full_name'

    adyen_account_id=fields.Many2one('adyen.account',ondelete='cascade')
    shareholder_reference=fields.Char('Reference',default=lambdaself:uuid.uuid4().hex)
    shareholder_uuid=fields.Char('UUID')#GivenbyAdyen
    first_name=fields.Char('FirstName',required=True)
    last_name=fields.Char('LastName',required=True)
    full_name=fields.Char(compute='_compute_full_name')
    date_of_birth=fields.Date('Dateofbirth',required=True)
    document_number=fields.Char('IDNumber',
            help="ThetypeofIDNumberrequireddependsonthecountry:\n"
             "US:SocialSecurityNumber(9digitsorlast4digits)\n"
             "Canada:SocialInsuranceNumber\nItaly:Codicefiscale\n"
             "Australia:DocumentNumber")

    #KYC
    kyc_status=fields.Selection(string='KYCStatus',selection=[
        ('awaiting_data','Datatoprovide'),
        ('pending','Waitingforvalidation'),
        ('passed','Confirmed'),
        ('failed','Failed'),
    ],required=True,default='pending')
    kyc_status_message=fields.Char('KYCStatusMessage',readonly=True)

    @api.depends('first_name','last_name')
    def_compute_full_name(self):
        foradyen_shareholder_idinself:
            adyen_shareholder_id.full_name='%s%s'%(adyen_shareholder_id.first_name,adyen_shareholder_id.last_name)

    @api.model
    defcreate(self,values):
        adyen_shareholder_id=super(AdyenShareholder,self).create(values)
        response=adyen_shareholder_id.adyen_account_id._adyen_rpc('update_account_holder',adyen_shareholder_id._format_data())
        shareholders=response['accountHolderDetails']['businessDetails']['shareholders']
        created_shareholder=next(shareholderforshareholderinshareholdersifshareholder['shareholderReference']==adyen_shareholder_id.shareholder_reference)
        adyen_shareholder_id.with_context(update_from_adyen=True).write({
            'shareholder_uuid':created_shareholder['shareholderCode'],
        })
        returnadyen_shareholder_id

    defwrite(self,vals):
        res=super(AdyenShareholder,self).write(vals)
        ifnotself.env.context.get('update_from_adyen'):
            self.adyen_account_id._adyen_rpc('update_account_holder',self._format_data())
        returnres

    defunlink(self):
        forshareholder_idinself:
            shareholder_id.adyen_account_id._adyen_rpc('delete_shareholders',{
                'accountHolderCode':shareholder_id.adyen_account_id.account_holder_code,
                'shareholderCodes':[shareholder_id.shareholder_uuid],
            })
        returnsuper(AdyenShareholder,self).unlink()

    def_upload_photo_id(self,document_type,content,filename):
        self.adyen_account_id._adyen_rpc('upload_document',{
            'documentDetail':{
                'accountHolderCode':self.adyen_account_id.account_holder_code,
                'shareholderCode':self.shareholder_uuid,
                'documentType':document_type,
                'filename':filename,
            },
            'documentContent':content.decode(),
        })

    def_format_data(self):
        data={
            'accountHolderCode':self.adyen_account_id.account_holder_code,
            'accountHolderDetails':{
                'businessDetails':{
                    'shareholders':[{
                        'shareholderCode':self.shareholder_uuidorNone,
                        'shareholderReference':self.shareholder_reference,
                        'address':{
                            'city':self.city,
                            'country':self.country_code,
                            'houseNumberOrName':self.house_number_or_name,
                            'postalCode':self.zip,
                            'stateOrProvince':self.state_id.codeorNone,
                            'street':self.street,
                        },
                        'name':{
                            'firstName':self.first_name,
                            'lastName':self.last_name,
                            'gender':'UNKNOWN'
                        },
                        'personalData':{
                            'dateOfBirth':str(self.date_of_birth),
                        }
                    }]
                }
            }
        }

        #documentDatacannotbepresentinthedataifnotset
        ifself.document_number:
            data['accountHolderDetails']['businessDetails']['shareholders'][0]['personalData']['documentData']=[{
                'number':self.document_number,
                'type':'ID',
            }]

        returndata

classAdyenBankAccount(models.Model):
    _name='adyen.bank.account'
    _description='AdyenforPlatformsBankAccount'

    adyen_account_id=fields.Many2one('adyen.account',ondelete='cascade')
    bank_account_reference=fields.Char('Reference',default=lambdaself:uuid.uuid4().hex)
    bank_account_uuid=fields.Char('UUID')#GivenbyAdyen
    owner_name=fields.Char('OwnerName',required=True)
    country_id=fields.Many2one('res.country',string='Country',domain=[('code','in',ADYEN_AVAILABLE_COUNTRIES)],required=True)
    country_code=fields.Char(related='country_id.code')
    currency_id=fields.Many2one('res.currency',string='Currency',required=True)
    iban=fields.Char('IBAN')
    account_number=fields.Char('AccountNumber')
    branch_code=fields.Char('BranchCode')
    bank_code=fields.Char('BankCode')
    account_type=fields.Selection(string='AccountType',selection=[
        ('checking','Checking'),
        ('savings','Savings'),
    ])
    owner_country_id=fields.Many2one('res.country',string='OwnerCountry')
    owner_state_id=fields.Many2one('res.country.state','OwnerState',domain="[('country_id','=?',owner_country_id)]")
    owner_street=fields.Char('OwnerStreet')
    owner_city=fields.Char('OwnerCity')
    owner_zip=fields.Char('OwnerZIP')
    owner_house_number_or_name=fields.Char('OwnerHouseNumberorName')

    bank_statement=fields.Binary('BankStatement',help="Youneedtoprovideabankstatementtoallowpayouts.\
        Thefilemustbeabankstatement,ascreenshotofyouronlinebankingenvironment,aletterfromthebankorachequeandmustcontain\
        thelogoofthebankorit'snameinauniquefont,thebankaccountdetails,thenameoftheaccountholder.\
        Allowedformats:jpg,pdf,png.Maximumallowedsize:10MB.")
    bank_statement_filename=fields.Char()

    #KYC
    kyc_status=fields.Selection(string='KYCStatus',selection=[
        ('awaiting_data','Datatoprovide'),
        ('pending','Waitingforvalidation'),
        ('passed','Confirmed'),
        ('failed','Failed'),
    ],required=True,default='pending')
    kyc_status_message=fields.Char('KYCStatusMessage',readonly=True)

    @api.model
    defcreate(self,values):
        adyen_bank_account_id=super(AdyenBankAccount,self).create(values)
        response=adyen_bank_account_id.adyen_account_id._adyen_rpc('update_account_holder',adyen_bank_account_id._format_data())
        bank_accounts=response['accountHolderDetails']['bankAccountDetails']
        created_bank_account=next(bank_accountforbank_accountinbank_accountsifbank_account['bankAccountReference']==adyen_bank_account_id.bank_account_reference)
        adyen_bank_account_id.with_context(update_from_adyen=True).write({
            'bank_account_uuid':created_bank_account['bankAccountUUID'],
        })
        returnadyen_bank_account_id

    defwrite(self,vals):
        res=super(AdyenBankAccount,self).write(vals)
        ifnotself.env.context.get('update_from_adyen'):
            self.adyen_account_id._adyen_rpc('update_account_holder',self._format_data())
        if'bank_statement'invals:
            self._upload_bank_statement(vals['bank_statement'],vals['bank_statement_filename'])
        returnres

    defunlink(self):
        forbank_account_idinself:
            bank_account_id.adyen_account_id._adyen_rpc('delete_bank_accounts',{
                'accountHolderCode':bank_account_id.adyen_account_id.account_holder_code,
                'bankAccountUUIDs':[bank_account_id.bank_account_uuid],
            })
        returnsuper(AdyenBankAccount,self).unlink()

    def_format_data(self):
        return{
            'accountHolderCode':self.adyen_account_id.account_holder_code,
            'accountHolderDetails':{
                'bankAccountDetails':[{
                    'accountNumber':self.account_numberorNone,
                    'accountType':self.account_typeorNone,
                    'bankAccountReference':self.bank_account_reference,
                    'bankAccountUUID':self.bank_account_uuidorNone,
                    'bankCode':self.bank_codeorNone,
                    'branchCode':self.branch_codeorNone,
                    'countryCode':self.country_code,
                    'currencyCode':self.currency_id.name,
                    'iban':self.ibanorNone,
                    'ownerCity':self.owner_cityorNone,
                    'ownerCountryCode':self.owner_country_id.codeorNone,
                    'ownerHouseNumberOrName':self.owner_house_number_or_nameorNone,
                    'ownerName':self.owner_name,
                    'ownerPostalCode':self.owner_ziporNone,
                    'ownerState':self.owner_state_id.codeorNone,
                    'ownerStreet':self.owner_streetorNone,
                }],
            }
        }

    def_upload_bank_statement(self,content,filename):
        file_extension=os.path.splitext(filename)[1]
        file_size=len(content.encode('utf-8'))
        iffile_extensionnotin['.jpeg','.jpg','.pdf','.png']:
            raiseValidationError(_('Allowedfileformatsforbankstatementsarejpeg,jpg,pdforpng'))
        iffile_size>>20>10or(file_size>>10<10andfile_extension!='.pdf'):
            raiseValidationError(_('Bankstatementsmustbegreaterthan10kB(exceptforPDFs)andsmallerthan10MB'))

        self.adyen_account_id._adyen_rpc('upload_document',{
            'documentDetail':{
                'accountHolderCode':self.adyen_account_id.account_holder_code,
                'bankAccountUUID':self.bank_account_uuid,
                'documentType':'BANK_STATEMENT',
                'filename':filename,
            },
            'documentContent':content,
        })


classAdyenPayout(models.Model):
    _name='adyen.payout'
    _description='AdyenforPlatformsPayout'

    @api.depends('payout_schedule')
    def_compute_next_scheduled_payout(self):
        today=fields.date.today()
        foradyen_payout_idinself:
            adyen_payout_id.next_scheduled_payout=date_utils.end_of(today,adyen_payout_id.payout_schedule)

    adyen_account_id=fields.Many2one('adyen.account',ondelete='cascade')
    adyen_bank_account_id=fields.Many2one('adyen.bank.account',string='BankAccount',
        help='Thebankaccounttowhichthepayoutistobemade.Ifleftblank,abankaccountisautomaticallyselected')
    name=fields.Char('Name',default='Default',required=True)
    code=fields.Char('AccountCode')
    payout_schedule=fields.Selection(string='Schedule',selection=[
        ('day','Daily'),
        ('week','Weekly'),
        ('month','Monthly'),
    ],default='week',required=True)
    next_scheduled_payout=fields.Date('Nextscheduledpayout',compute=_compute_next_scheduled_payout,store=True)
    transaction_ids=fields.One2many('adyen.transaction','adyen_payout_id',string='Transactions')

    @api.model
    defcreate(self,values):
        adyen_payout_id=super(AdyenPayout,self).create(values)
        ifnotadyen_payout_id.env.context.get('update_from_adyen'):
            response=adyen_payout_id.adyen_account_id._adyen_rpc('create_payout',{
                'accountHolderCode':adyen_payout_id.adyen_account_id.account_holder_code,
            })
            adyen_payout_id.with_context(update_from_adyen=True).write({
                'code':response['accountCode'],
            })
        returnadyen_payout_id

    defunlink(self):
        foradyen_payout_idinself:
            adyen_payout_id.adyen_account_id._adyen_rpc('close_payout',{
                'accountCode':adyen_payout_id.code,
            })
        returnsuper(AdyenPayout,self).unlink()

    @api.model
    def_process_payouts(self):
        foradyen_payout_idinself.search([('next_scheduled_payout','<',fields.Date.today())]):
            adyen_payout_id.send_payout_request(notify=False)
            adyen_payout_id._compute_next_scheduled_payout()

    defsend_payout_request(self,notify=True):
        response=self.adyen_account_id._adyen_rpc('account_holder_balance',{
            'accountHolderCode':self.adyen_account_id.account_holder_code,
        })
        balances=next(account_balance['detailBalance']['balance']foraccount_balanceinresponse['balancePerAccount']ifaccount_balance['accountCode']==self.code)
        ifnotifyandnotbalances:
            self.env['bus.bus'].sendone(
                (self._cr.dbname,'res.partner',self.env.user.partner_id.id),
                {'type':'simple_notification','title':_('Nopendingbalance'),'message':_('Nobalanceiscurrentlyawaitngpayout.')}
            )
        forbalanceinbalances:
            response=self.adyen_account_id._adyen_rpc('payout_request',{
                'accountCode':self.code,
                'accountHolderCode':self.adyen_account_id.account_holder_code,
                'bankAccountUUID':self.adyen_bank_account_id.bank_account_uuidorNone,
                'amount':balance,
            })
            ifnotifyandresponse['resultCode']=='Received':
                currency_id=self.env['res.currency'].search([('name','=',balance['currency'])])
                value=round(balance['value']/(10**currency_id.decimal_places),2)#Convertfromminorunits
                amount=str(value)+currency_id.symbolifcurrency_id.position=='after'elsecurrency_id.symbol+str(value)
                message=_('Successfullysentpayoutrequestfor%s',amount)
                self.env['bus.bus'].sendone(
                    (self._cr.dbname,'res.partner',self.env.user.partner_id.id),
                    {'type':'simple_notification','title':_('PayoutRequestsent'),'message':message}
                )

    def_fetch_transactions(self,page=1):
        response=self.adyen_account_id._adyen_rpc('get_transactions',{
            'accountHolderCode':self.adyen_account_id.account_holder_code,
            'transactionListsPerAccount':[{
                'accountCode':self.code,
                'page':page,
            }]
        })
        transaction_list=response['accountTransactionLists'][0]
        returntransaction_list['transactions'],transaction_list['hasNextPage']
