#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre
fromstdnum.utilimportclean

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError
fromflectra.tools.miscimportmod10r


ISR_SUBSCRIPTION_CODE={'CHF':'01','EUR':'03'}
CLEARING="09000"
_re_postal=re.compile('^[0-9]{2}-[0-9]{1,6}-[0-9]$')


def_is_l10n_ch_postal(account_ref):
    """ReturnsTrueifthestringaccount_refisavalidpostalaccountnumber,
    i.e.itonlycontainsciphersandislastcipheristheresultofarecursive
    modulo10operationranovertherestofit.Shortenformwith-isalsoaccepted.
    """
    if_re_postal.match(account_refor''):
        ref_subparts=account_ref.split('-')
        account_ref=ref_subparts[0]+ref_subparts[1].rjust(6,'0')+ref_subparts[2]

    ifre.match('\d+$',account_refor''):
        account_ref_without_check=account_ref[:-1]
        returnmod10r(account_ref_without_check)==account_ref
    returnFalse

def_is_l10n_ch_isr_issuer(account_ref,currency_code):
    """ReturnsTrueifthestringaccount_refisavalidavalidISRissuer
    AnISRissuerispostalaccountnumberthatstartsby01(CHF)or03(EUR),
    """
    if(account_refor'').startswith(ISR_SUBSCRIPTION_CODE[currency_code]):
        return_is_l10n_ch_postal(account_ref)
    returnFalse


classResPartnerBank(models.Model):
    _inherit='res.partner.bank'

    l10n_ch_postal=fields.Char(
        string="SwissPostalAccount",
        readonly=False,store=True,
        compute='_compute_l10n_ch_postal',
        help="ThisfieldisusedfortheSwisspostalaccountnumberonavendoraccountandfortheclientnumberon"
             "yourownaccount.Theclientnumberismostly6numberswithout-,whilethepostalaccountnumbercan"
             "bee.g.01-162-8")

    #fieldstoconfigureISRpaymentslipgeneration
    l10n_ch_isr_subscription_chf=fields.Char(string='CHFISRSubscriptionNumber',help='ThesubscriptionnumberprovidedbythebankorPostfinancetoidentifythebank,usedtogenerateISRinCHF.eg.01-162-8')
    l10n_ch_isr_subscription_eur=fields.Char(string='EURISRSubscriptionNumber',help='ThesubscriptionnumberprovidedbythebankorPostfinancetoidentifythebank,usedtogenerateISRinEUR.eg.03-162-5')
    l10n_ch_show_subscription=fields.Boolean(compute='_compute_l10n_ch_show_subscription',default=lambdaself:self.env.company.country_id.code=='CH')

    def_is_isr_issuer(self):
        return(_is_l10n_ch_isr_issuer(self.l10n_ch_postal,'CHF')
                or_is_l10n_ch_isr_issuer(self.l10n_ch_postal,'EUR'))

    @api.constrains("l10n_ch_postal","partner_id")
    def_check_postal_num(self):
        """Validatepostalnumberformat"""
        forrecinself:
            ifrec.l10n_ch_postalandnot_is_l10n_ch_postal(rec.l10n_ch_postal):
                #l10n_ch_postalisusedforthepurposeofClientNumberonyourownaccounts,sodon'tdothecheckthere
                ifrec.partner_idandnotrec.partner_id.ref_company_ids:
                    raiseValidationError(
                        _("Thepostalnumber{}isnotvalid.\n"
                          "Itmustbeavalidpostalnumberformat.eg.10-8060-7").format(rec.l10n_ch_postal))
        returnTrue

    @api.constrains("l10n_ch_isr_subscription_chf","l10n_ch_isr_subscription_eur")
    def_check_subscription_num(self):
        """ValidateISRsubscriptionnumberformat
        Subscriptionnumbercanonlystartswith01or03
        """
        forrecinself:
            forcurrencyin["CHF","EUR"]:
                subscrip=rec.l10n_ch_isr_subscription_chfifcurrency=="CHF"elserec.l10n_ch_isr_subscription_eur
                ifsubscripandnot_is_l10n_ch_isr_issuer(subscrip,currency):
                    example="01-162-8"ifcurrency=="CHF"else"03-162-5"
                    raiseValidationError(
                        _("TheISRsubcription{}for{}numberisnotvalid.\n"
                          "Itmuststartswith{}andweavalidpostalnumberformat.eg.{}"
                          ).format(subscrip,currency,ISR_SUBSCRIPTION_CODE[currency],example))
        returnTrue

    @api.depends('partner_id','company_id')
    def_compute_l10n_ch_show_subscription(self):
        forbankinself:
            ifbank.partner_id:
                bank.l10n_ch_show_subscription=bank.partner_id.ref_company_ids.country_id.codein('CH','LI')
            elifbank.company_id:
                bank.l10n_ch_show_subscription=bank.company_id.country_id.codein('CH','LI')
            else:
                bank.l10n_ch_show_subscription=self.env.company.country_id.codein('CH','LI')

    @api.depends('acc_number','acc_type')
    def_compute_sanitized_acc_number(self):
        #Onlyremovespacesincaseitisnotpostal
        postal_banks=self.filtered(lambdab:b.acc_type=="postal")
        forbankinpostal_banks:
            bank.sanitized_acc_number=bank.acc_number
        super(ResPartnerBank,self-postal_banks)._compute_sanitized_acc_number()

    @api.model
    def_get_supported_account_types(self):
        rslt=super(ResPartnerBank,self)._get_supported_account_types()
        rslt.append(('postal',_('Postal')))
        returnrslt

    @api.model
    defretrieve_acc_type(self,acc_number):
        """Overriddenmethodenablingtherecognitionofswisspostalbank
        accountnumbers.
        """
        acc_number_split=""
        #acc_number_splitisneededtocontinuetorecognizetheaccount
        #asapostalaccountevenifthedifference
        ifacc_numberand""inacc_number:
            acc_number_split=acc_number.split("")[0]
        if_is_l10n_ch_postal(acc_number)or(acc_number_splitand_is_l10n_ch_postal(acc_number_split)):
            return'postal'
        else:
            returnsuper(ResPartnerBank,self).retrieve_acc_type(acc_number)

    @api.depends('acc_number','partner_id','acc_type')
    def_compute_l10n_ch_postal(self):
        forrecordinself:
            ifrecord.acc_type=='iban':
                record.l10n_ch_postal=self._retrieve_l10n_ch_postal(record.sanitized_acc_number)
            elifrecord.acc_type=='postal':
                ifrecord.acc_numberand""inrecord.acc_number:
                    record.l10n_ch_postal=record.acc_number.split("")[0]
                else:
                    record.l10n_ch_postal=record.acc_number
                    #IncaseofISRissuer,thisnumberisnot
                    #uniqueandwefillacc_numberwithpartner
                    #nametogiveproperinformationtotheuser
                    ifrecord.partner_idandrecord.acc_number[:2]in["01","03"]:
                        record.acc_number=("{}{}").format(record.acc_number,record.partner_id.name)

    @api.model
    def_is_postfinance_iban(self,iban):
        """PostfinanceIBANhaveformat
        CHXX09000XXXXXXXXXXXK
        Where09000istheclearingnumber
        """
        returniban.startswith(('CH','LI'))andiban[4:9]==CLEARING

    @api.model
    def_pretty_postal_num(self,number):
        """formatapostalaccountnumberoranISRsubscriptionnumber
        asperspecificationswith'-'separators.
        eg.010001628->01-162-8
        """
        ifre.match('^[0-9]{2}-[0-9]{1,6}-[0-9]$',numberor''):
            returnnumber
        currency_code=number[:2]
        middle_part=number[2:-1]
        trailing_cipher=number[-1]
        middle_part=middle_part.lstrip("0")
        returncurrency_code+'-'+middle_part+'-'+trailing_cipher

    @api.model
    def_retrieve_l10n_ch_postal(self,iban):
        """ReadsaswisspostalaccountnumberfromaanIBANandreturnsitas
        astring.ReturnsNoneifnovalidpostalaccountnumberwasfound,or
        thegivenibanwasnotfromSwissPostfinance.

        CH0909000000100080607->10-8060-7
        """
        ifself._is_postfinance_iban(iban):
            #theIBANcorrespondstoaswissaccount
            returnself._pretty_postal_num(iban[-9:])
        returnNone

    def_l10n_ch_get_qr_vals(self,amount,currency,debtor_partner,free_communication,structured_communication):
        comment=""
        iffree_communication:
            comment=(free_communication[:137]+'...')iflen(free_communication)>140elsefree_communication

        creditor_addr_1,creditor_addr_2=self._get_partner_address_lines(self.partner_id)
        debtor_addr_1,debtor_addr_2=self._get_partner_address_lines(debtor_partner)

        #Computereferencetype(emptybydefault,onlymandatoryforQR-IBAN,
        #andmustthenbe27characters-long,withmod10rcheckdigitasthe27thone,
        #justlikeISRnumberforinvoices)
        reference_type='NON'
        reference=''
        ifself._is_qr_iban():
            #_check_for_qr_code_errorsensureswecan'thaveaQR-IBANwithoutaQR-referencehere
            reference_type='QRR'
            reference=structured_communication
        elifself._is_iso11649_reference(structured_communication):
            reference_type='SCOR'
            reference=structured_communication.replace('','')

        currency=currencyorself.currency_idorself.company_id.currency_id

        return[
            'SPC',                                               #QRType
            '0200',                                              #Version
            '1',                                                 #CodingType
            self.sanitized_acc_number,                           #IBAN
            'K',                                                 #CreditorAddressType
            (self.acc_holder_nameorself.partner_id.name)[:70], #CreditorName
            creditor_addr_1,                                     #CreditorAddressLine1
            creditor_addr_2,                                     #CreditorAddressLine2
            '',                                                  #CreditorPostalCode(empty,sincewe'reusingcombinedaddreselements)
            '',                                                  #CreditorTown(empty,sincewe'reusingcombinedaddreselements)
            self.partner_id.country_id.code,                     #CreditorCountry
            '',                                                  #UltimateCreditorAddressType
            '',                                                  #Name
            '',                                                  #UltimateCreditorAddressLine1
            '',                                                  #UltimateCreditorAddressLine2
            '',                                                  #UltimateCreditorPostalCode
            '',                                                  #UltimateCreditorTown
            '',                                                  #UltimateCreditorCountry
            '{:.2f}'.format(amount),                             #Amount
            currency.name,                                       #Currency
            'K',                                                 #UltimateDebtorAddressType
            debtor_partner.commercial_partner_id.name[:70],      #UltimateDebtorName
            debtor_addr_1,                                       #UltimateDebtorAddressLine1
            debtor_addr_2,                                       #UltimateDebtorAddressLine2
            '',                                                  #UltimateDebtorPostalCode(nottobeprovidedforaddresstypeK)
            '',                                                  #UltimateDebtorPostalCity(nottobeprovidedforaddresstypeK)
            debtor_partner.country_id.code,                      #UltimateDebtorPostalCountry
            reference_type,                                      #ReferenceType
            reference,                                           #Reference
            comment,                                             #UnstructuredMessage
            'EPD',                                               #Mandatorytrailerpart
        ]

    def_get_qr_vals(self,qr_method,amount,currency,debtor_partner,free_communication,structured_communication):
        ifqr_method=='ch_qr':
            returnself._l10n_ch_get_qr_vals(amount,currency,debtor_partner,free_communication,structured_communication)
        returnsuper()._get_qr_vals(qr_method,amount,currency,debtor_partner,free_communication,structured_communication)

    def_get_qr_code_generation_params(self,qr_method,amount,currency,debtor_partner,free_communication,structured_communication):
        ifqr_method=='ch_qr':
            return{
                'barcode_type':'QR',
                'width':256,
                'height':256,
                'quiet':1,
                'mask':'ch_cross',
                'value':'\n'.join(self._get_qr_vals(qr_method,amount,currency,debtor_partner,free_communication,structured_communication)),
                #SwissQRcoderequiresErrorCorrectionLevel='M'byspecification
                'barLevel':'M',
            }
        returnsuper()._get_qr_code_generation_params(qr_method,amount,currency,debtor_partner,free_communication,structured_communication)

    def_get_partner_address_lines(self,partner):
        """Returnsatupleoftwoelementscontainingtheaddresslinestouse
        forthispartner.Line1containsthestreetandnumber,line2contains
        zipandcity.Thosetwolinesarelimitedto70characters
        """
        streets=[partner.street,partner.street2]
        line_1=''.join(filter(None,streets))
        line_2=partner.zip+''+partner.city
        returnline_1[:70],line_2[:70]

    def_check_qr_iban_range(self,iban):
        ifnotibanorlen(iban)<9:
            returnFalse
        iid_start_index=4
        iid_end_index=8
        iid=iban[iid_start_index:iid_end_index+1]
        returnre.match('\d+',iid)\
               and30000<=int(iid)<=31999#ThosevaluesforiidarereservedforQR-IBANsonly

    def_is_qr_iban(self):
        """TellswhetherornotthisbankaccounthasaQR-IBANaccountnumber.
        QR-IBANsarespecificidentifiersusedinSwitzerlandasreferencesin
        QR-codes.TheyareformedlikeregularIBANs,butareactuallysomething
        different.
        """
        self.ensure_one()

        returnself.sanitized_acc_number.startswith(('CH','LI'))\
               andself.acc_type=='iban'\
               andself._check_qr_iban_range(self.sanitized_acc_number)

    @api.model
    def_is_qr_reference(self,reference):
        """CheckswhetherthegivenreferenceisaQR-reference,i.e.itis
        madeof27digits,the27thbeingamod10rcheckonthe26previousones.
        """
        returnreference\
               andlen(reference)==27\
               andre.match('\d+$',reference)\
               andreference==mod10r(reference[:-1])

    @api.model
    def_is_iso11649_reference(self,reference):
        """CheckswhetherthegivenreferenceisaISO11649(SCOR)reference.
        """
        returnreference\
               andlen(reference)>=5\
               andlen(reference)<=25\
               andreference.startswith('RF')\
               andint(''.join(str(int(x,36))forxinclean(reference[4:]+reference[:4],'-.,/:').upper().strip()))%97==1
               #seehttps://github.com/arthurdejong/python-stdnum/blob/master/stdnum/iso11649.py

    def_eligible_for_qr_code(self,qr_method,debtor_partner,currency):
        ifqr_method=='ch_qr':
            returnself.acc_type=='iban'and\
                   (notdebtor_partnerordebtor_partner.country_id.codein('CH','LI'))\
                   andcurrency.namein('EUR','CHF')

        returnsuper()._eligible_for_qr_code(qr_method,debtor_partner,currency)

    def_check_for_qr_code_errors(self,qr_method,amount,currency,debtor_partner,free_communication,structured_communication):
        def_partner_fields_set(partner):
            returnpartner.zipand\
                   partner.cityand\
                   partner.country_id.codeand\
                   (partner.streetorpartner.street2)

        ifqr_method=='ch_qr':
            ifnot_partner_fields_set(self.partner_id):
                return_("Thepartnersetonthebankaccountmeanttoreceivethepayment(%s)musthaveacompletepostaladdress(street,zip,cityandcountry).",self.acc_number)

            ifdebtor_partnerandnot_partner_fields_set(debtor_partner):
                return_("Thepartnermusthaveacompletepostaladdress(street,zip,cityandcountry).")

            ifself._is_qr_iban()andnotself._is_qr_reference(structured_communication):
                return_("WhenusingaQR-IBANasthedestinationaccountofaQR-code,thepaymentreferencemustbeaQR-reference.")

        returnsuper()._check_for_qr_code_errors(qr_method,amount,currency,debtor_partner,free_communication,structured_communication)

    @api.model
    def_get_available_qr_methods(self):
        rslt=super()._get_available_qr_methods()
        rslt.append(('ch_qr',_("SwissQRbill"),10))
        returnrslt
