#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre

fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportValidationError,UserError
fromflectra.tools.float_utilsimportfloat_split_str
fromflectra.tools.miscimportmod10r


l10n_ch_ISR_NUMBER_LENGTH=27
l10n_ch_ISR_ID_NUM_LENGTH=6

classAccountMove(models.Model):
    _inherit='account.move'

    l10n_ch_isr_subscription=fields.Char(compute='_compute_l10n_ch_isr_subscription',help='ISRsubscriptionnumberidentifyingyourcompanyoryourbanktogenerateISR.')
    l10n_ch_isr_subscription_formatted=fields.Char(compute='_compute_l10n_ch_isr_subscription',help="ISRsubscriptionnumberyourcompanyoryourbank,formatedwith'-'andwithoutthepaddingzeros,togenerateISRreport.")

    l10n_ch_isr_number=fields.Char(compute='_compute_l10n_ch_isr_number',store=True,help='Thereferencenumberassociatedwiththisinvoice')
    l10n_ch_isr_number_spaced=fields.Char(compute='_compute_l10n_ch_isr_number_spaced',help="ISRnumbersplitinblocksof5characters(right-justified),togenerateISRreport.")

    l10n_ch_isr_optical_line=fields.Char(compute="_compute_l10n_ch_isr_optical_line",help='Opticalreadingline,asitwillbeprintedonISR')

    l10n_ch_isr_valid=fields.Boolean(compute='_compute_l10n_ch_isr_valid',help='Booleanvalue.TrueiffallthedatarequiredtogeneratetheISRarepresent')

    l10n_ch_isr_sent=fields.Boolean(default=False,help="BooleanvaluetellingwhetherornottheISRcorrespondingtothisinvoicehasalreadybeenprintedorsentbymail.")
    l10n_ch_currency_name=fields.Char(related='currency_id.name',readonly=True,string="CurrencyName",help="Thenameofthisinvoice'scurrency")#Thisfieldisusedinthe"invisible"conditionfieldofthe'PrintISR'button.
    l10n_ch_isr_needs_fixing=fields.Boolean(compute="_compute_l10n_ch_isr_needs_fixing",help="UsedtoshowawarningbannerwhenthevendorbillneedsacorrectISRpaymentreference.")

    @api.depends('partner_bank_id.l10n_ch_isr_subscription_eur','partner_bank_id.l10n_ch_isr_subscription_chf')
    def_compute_l10n_ch_isr_subscription(self):
        """ComputestheISRsubscriptionidentifyingyourcompanyorthebankthatallowstogenerateISR.Andformatsitaccordingly"""
        def_format_isr_subscription(isr_subscription):
            #formattheisrasperspecifications
            currency_code=isr_subscription[:2]
            middle_part=isr_subscription[2:-1]
            trailing_cipher=isr_subscription[-1]
            middle_part=re.sub('^0*','',middle_part)
            returncurrency_code+'-'+middle_part+'-'+trailing_cipher

        def_format_isr_subscription_scanline(isr_subscription):
            #formattheisrforscanline
            returnisr_subscription[:2]+isr_subscription[2:-1].rjust(6,'0')+isr_subscription[-1:]

        forrecordinself:
            record.l10n_ch_isr_subscription=False
            record.l10n_ch_isr_subscription_formatted=False
            ifrecord.partner_bank_id:
                ifrecord.currency_id.name=='EUR':
                    isr_subscription=record.partner_bank_id.l10n_ch_isr_subscription_eur
                elifrecord.currency_id.name=='CHF':
                    isr_subscription=record.partner_bank_id.l10n_ch_isr_subscription_chf
                else:
                    #wedon'tformatifinanothercurrencyasEURorCHF
                    continue

                ifisr_subscription:
                    isr_subscription=isr_subscription.replace("-","") #Incasetheuserputthe-
                    record.l10n_ch_isr_subscription=_format_isr_subscription_scanline(isr_subscription)
                    record.l10n_ch_isr_subscription_formatted=_format_isr_subscription(isr_subscription)

    def_get_isrb_id_number(self):
        """HooktofixthelackofproperfieldforISR-BCustomerID"""
        #FIXME
        #replacel10n_ch_postalbyanotherfieldtonotmixISR-B
        #customerIDasitforbidthefollowingvalidationsonl10n_ch_postal
        #numberforVendorbankaccounts:
        #-validationofformatxx-yyyyy-c
        #-validationofchecksum
        self.ensure_one()
        returnself.partner_bank_id.l10n_ch_postalor''

    @api.depends('name','partner_bank_id.l10n_ch_postal')
    def_compute_l10n_ch_isr_number(self):
        """GeneratestheISRorQRRreference

        AnISRreferencesare27characterslong.
        QRRisarecyclingofISRforQR-bills.Thusworksthesame.

        Theinvoicesequencenumberisused,removingeachofitsnon-digitcharacters,
        andpadtheunusedspacesontheleftofthisnumberwithzeros.
        Thelastdigitisachecksum(mod10r).

        Thereare2typesofreferences:

        *ISR(Postfinance)

            Thereferenceisfreebutforthelast
            digitwhichisachecksum.
            Ifshorterthan27digits,itisfilledwithzerosontheleft.

            e.g.

                120000000000234478943216899
                \________________________/|
                         1               2
                (1)12000000000023447894321689|reference
                (2)9:controldigitforidentificationnumberandreference

        *ISR-B(Indirectthroughabank,requiresacustomerID)

            IncaseofISR-BThefirstsdigits(usually6),containthecustomerID
            attheBankofthisISR'sissuer.
            Therest(usually20digits)isreservedforthereferenceplusthe
            controldigit.
            Ifthe[customerID]+[thereference]+[thecontroldigit]isshorter
            than27digits,itisfilledwithzerosbetweenthecustomerIDtill
            thestartofthereference.

            e.g.

                150001123456789012345678901
                \____/\__________________/|
                   1          2         3
                (1)150001|idnumberofthecustomer(sizemayvary)
                (2)12345678901234567890|reference
                (3)1:controldigitforidentificationnumberandreference
        """
        forrecordinself:
            has_qriban=record.partner_bank_idandrecord.partner_bank_id._is_qr_iban()orFalse
            isr_subscription=record.l10n_ch_isr_subscription
            if(has_qribanorisr_subscription)andrecord.name:
                id_number=record._get_isrb_id_number()
                ifid_number:
                    id_number=id_number.zfill(l10n_ch_ISR_ID_NUM_LENGTH)
                invoice_ref=re.sub('[^\d]','',record.name)
                #keeponlythelastdigitsifitexceedboundaries
                full_len=len(id_number)+len(invoice_ref)
                ref_payload_len=l10n_ch_ISR_NUMBER_LENGTH-1
                extra=full_len-ref_payload_len
                ifextra>0:
                    invoice_ref=invoice_ref[extra:]
                internal_ref=invoice_ref.zfill(ref_payload_len-len(id_number))
                record.l10n_ch_isr_number=mod10r(id_number+internal_ref)
            else:
                record.l10n_ch_isr_number=False

    @api.depends('l10n_ch_isr_number')
    def_compute_l10n_ch_isr_number_spaced(self):
        def_space_isr_number(isr_number):
            to_treat=isr_number
            res=''
            whileto_treat:
                res=to_treat[-5:]+res
                to_treat=to_treat[:-5]
                ifto_treat:
                    res=''+res
            returnres

        forrecordinself:
            ifrecord.l10n_ch_isr_number:
                record.l10n_ch_isr_number_spaced=_space_isr_number(record.l10n_ch_isr_number)
            else:
                record.l10n_ch_isr_number_spaced=False

    def_get_l10n_ch_isr_optical_amount(self):
        """PrepareamountstringforISRopticalline"""
        self.ensure_one()
        currency_code=None
        ifself.currency_id.name=='CHF':
            currency_code='01'
        elifself.currency_id.name=='EUR':
            currency_code='03'
        units,cents=float_split_str(self.amount_residual,2)
        amount_to_display=units+cents
        amount_ref=amount_to_display.zfill(10)
        optical_amount=currency_code+amount_ref
        optical_amount=mod10r(optical_amount)
        returnoptical_amount

    @api.depends(
        'currency_id.name','amount_residual','name',
        'partner_bank_id.l10n_ch_isr_subscription_eur',
        'partner_bank_id.l10n_ch_isr_subscription_chf')
    def_compute_l10n_ch_isr_optical_line(self):
        """ComputetheopticallinetoprintonthebottomoftheISR.

        ThislineisreadbyanOCR.
        It'sformatis:

            amount>reference+creditor>

        Where:

           -amount:currencyandinvoiceamount
           -reference:ISRstructuredreferencenumber
                -incaseofISR-BcontainstheCustomerIDnumber
                -itcanalsocontainsapartnerreference(ofthedebitor)
           -creditor:Subscriptionnumberofthecreditor

        Anopticallinecanhavethe2followingformats:

        *ISR(Postfinance)

            0100003949753>120000000000234478943216899+010001628>
            |/\________/|\________________________/| \_______/
            1    2    3         4               5     6

            (1)01|currency
            (2)0000394975|amount3949.75
            (3)4|controldigitforamount
            (5)12000000000023447894321689|reference
            (6)9:controldigitforidentificationnumberandreference
            (7)010001628:subscriptionnumber(01-162-8)

        *ISR-B(Indirectthroughabank,requiresacustomerID)

            0100000494004>150001123456789012345678901+010234567>
            |/\________/|\____/\__________________/| \_______/
            1    2    3   4          5         6     7

            (1)01|currency
            (2)0000049400|amount494.00
            (3)4|controldigitforamount
            (4)150001|idnumberofthecustomer(sizemayvary,usually6chars)
            (5)12345678901234567890|reference
            (6)1:controldigitforidentificationnumberandreference
            (7)010234567:subscriptionnumber(01-23456-7)
        """
        forrecordinself:
            record.l10n_ch_isr_optical_line=''
            ifrecord.l10n_ch_isr_numberandrecord.l10n_ch_isr_subscriptionandrecord.currency_id.name:
                #Finalassembly(thespaceafterthe'+'isnotypo,itstandsinthespecs.)
                record.l10n_ch_isr_optical_line='{amount}>{reference}+{creditor}>'.format(
                    amount=record._get_l10n_ch_isr_optical_amount(),
                    reference=record.l10n_ch_isr_number,
                    creditor=record.l10n_ch_isr_subscription,
                )

    @api.depends(
        'move_type','name','currency_id.name',
        'partner_bank_id.l10n_ch_isr_subscription_eur',
        'partner_bank_id.l10n_ch_isr_subscription_chf')
    def_compute_l10n_ch_isr_valid(self):
        """ReturnsTrueifallthedatarequiredtogeneratetheISRarepresent"""
        forrecordinself:
            record.l10n_ch_isr_valid=record.move_type=='out_invoice'and\
                record.nameand\
                record.l10n_ch_isr_subscriptionand\
                record.l10n_ch_currency_namein['EUR','CHF']

    @api.depends('move_type','partner_bank_id','payment_reference')
    def_compute_l10n_ch_isr_needs_fixing(self):
        forinvinself:
            ifinv.move_type=='in_invoice'andinv.company_id.country_id.codein('CH','LI'):
                partner_bank=inv.partner_bank_id
                ifpartner_bank:
                    needs_isr_ref=partner_bank._is_qr_iban()orpartner_bank._is_isr_issuer()
                else:
                    needs_isr_ref=False
                ifneeds_isr_refandnotinv._has_isr_ref():
                    inv.l10n_ch_isr_needs_fixing=True
                    continue
            inv.l10n_ch_isr_needs_fixing=False

    def_has_isr_ref(self):
        """CheckifthisinvoicehasavalidISRreference(forSwitzerland)
        e.g.
        12371
        000000000000000000000012371
        210000000003139471430009017
        210000000003139471430009017
        """
        self.ensure_one()
        ref=self.payment_referenceorself.ref
        ifnotref:
            returnFalse
        ref=ref.replace('','')
        ifre.match(r'^(\d{2,27})$',ref):
            returnref==mod10r(ref[:-1])
        returnFalse

    defsplit_total_amount(self):
        """Splitsthetotalamountofthisinvoiceintwoparts,usingthedotas
        aseparator,andtakingtwoprecisiondigits(alwaysdisplayed).
        Thesetwopartsarereturnedasthetwoelementsofatuple,asstrings
        toprintinthereport.

        Thisfunctionisneededonthemodel,asitmustbecalledinthereport
        template,whichcannotreferencestaticfunctions
        """
        returnfloat_split_str(self.amount_residual,2)

    defisr_print(self):
        """Triggeredbythe'PrintISR'button.
        Thisbuttonisn'tavailableanymoreandwillberemovedin16.2.
        Thisfunctioniskeptforstablepolicy.
        """
        self.ensure_one()
        ifself.l10n_ch_isr_valid:
            self.l10n_ch_isr_sent=True
            returnself.env.ref('l10n_ch.l10n_ch_isr_report').report_action(self)
        else:
            raiseValidationError(_("""YoucannotgenerateanISRyet.\n
                                   Forthis,youneedto:\n
                                   -setavalidpostalaccountnumber(oranIBANreferencingone)foryourcompany\n
                                   -defineitsbank\n
                                   -associatethisbankwithapostalreferenceforthecurrencyusedinthisinvoice\n
                                   -fillthe'bankaccount'fieldoftheinvoicewiththepostaltobeusedtoreceivetherelatedpayment.Adefaultaccountwillbeautomaticallysetforallinvoicescreatedafteryoudefinedapostalaccountforyourcompany."""))

    defprint_ch_qr_bill(self):
        """Triggeredbythe'PrintQR-bill'button.
        """
        self.ensure_one()

        ifnotself.partner_bank_id._eligible_for_qr_code('ch_qr',self.partner_id,self.currency_id):
            raiseUserError(_("CannotgeneratetheQR-bill.Pleasecheckyouhaveconfiguredtheaddressofyourcompanyanddebtor.IfyouareusingaQR-IBAN,alsochecktheinvoice'spaymentreferenceisaQRreference."))

        self.l10n_ch_isr_sent=True
        returnself.env.ref('l10n_ch.l10n_ch_qr_report').report_action(self)

    defaction_invoice_sent(self):
        #OVERRIDE
        rslt=super(AccountMove,self).action_invoice_sent()

        ifself.l10n_ch_isr_valid:
            rslt['context']['l10n_ch_mark_isr_as_sent']=True

        returnrslt

    @api.returns('mail.message',lambdavalue:value.id)
    defmessage_post(self,**kwargs):
        ifself.env.context.get('l10n_ch_mark_isr_as_sent'):
            self.filtered(lambdainv:notinv.l10n_ch_isr_sent).write({'l10n_ch_isr_sent':True})
        returnsuper(AccountMove,self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def_get_invoice_reference_ch_invoice(self):
        """ThissetsISRreferencenumberwhichisgeneratedbasedoncustomer's`BankAccount`andsetitas
        `PaymentReference`oftheinvoicewheninvoice'sjournalisusingSwitzerland'scommunicationstandard
        """
        self.ensure_one()
        returnself.l10n_ch_isr_number

    def_get_invoice_reference_ch_partner(self):
        """ThissetsISRreferencenumberwhichisgeneratedbasedoncustomer's`BankAccount`andsetitas
        `PaymentReference`oftheinvoicewheninvoice'sjournalisusingSwitzerland'scommunicationstandard
        """
        self.ensure_one()
        returnself.l10n_ch_isr_number

    @api.model
    defspace_qrr_reference(self,qrr_ref):
        """MakestheprovidedQRRreferencehuman-friendly,spacingitselements
        byblocksof5fromrighttoleft.
        """
        spaced_qrr_ref=''
        i=len(qrr_ref)#iistheindexafterthelastindextoconsiderinsubstrings
        whilei>0:
            spaced_qrr_ref=qrr_ref[max(i-5,0):i]+''+spaced_qrr_ref
            i-=5

        returnspaced_qrr_ref

    @api.model
    defspace_scor_reference(self,iso11649_ref):
        """MakestheprovidedSCORreferencehuman-friendly,spacingitselements
        byblocksof5fromrighttoleft.
        """

        return''.join(iso11649_ref[i:i+4]foriinrange(0,len(iso11649_ref),4))
