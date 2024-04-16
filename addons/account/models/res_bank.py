#-*-coding:utf-8-*-
importbase64

fromflectraimportapi,models,fields,_
fromflectra.exceptionsimportUserError
fromflectra.tools.imageimportimage_data_uri

importwerkzeug
importwerkzeug.exceptions

classResPartnerBank(models.Model):
    _inherit='res.partner.bank'

    def_build_qr_code_vals(self,amount,free_communication,structured_communication,currency,debtor_partner,qr_method=None,silent_errors=True):
        """ReturnstheQR-codevalsneededtogeneratetheQR-codereportlinktopaythisaccountwiththegivenparameters,
        orNoneifnoQR-codecouldbegenerated.

        :paramamount:Theamounttobepaid
        :paramfree_communication:FreecommunicationtoaddtothepaymentwhengeneratingonewiththeQR-code
        :paramstructured_communication:StructuredcommunicationtoaddtothepaymentwhengeneratingonewiththeQR-code
        :paramcurrency:Thecurrencyinwhichamountisexpressed
        :paramdebtor_partner:ThepartnertowhichthisQR-codeisaimed(sotheonewhowillhavetopay)
        :paramqr_method:TheQRgenerationmethodtobeusedtomaketheQR-code.IfNone,thefirstonegivingaresultwillbeused.
        :paramsilent_errors:Iftrue,forbidserrorstoberaisedifsometestedQR-codeformatcan'tbegeneratedbecauseofincorrectdata.
        """
        ifnotself:
            returnNone

        self.ensure_one()

        ifnotcurrency:
            raiseUserError(_("CurrencymustalwaysbeprovidedinordertogenerateaQR-code"))

        available_qr_methods=self.get_available_qr_methods_in_sequence()
        candidate_methods=qr_methodand[(qr_method,dict(available_qr_methods)[qr_method])]oravailable_qr_methods
        forcandidate_method,candidate_nameincandidate_methods:
            ifself._eligible_for_qr_code(candidate_method,debtor_partner,currency):
                error_message=self._check_for_qr_code_errors(candidate_method,amount,currency,debtor_partner,free_communication,structured_communication)

                ifnoterror_message:
                    return{
                        'qr_method':candidate_method,
                        'amount':amount,
                        'currency':currency,
                        'debtor_partner':debtor_partner,
                        'free_communication':free_communication,
                        'structured_communication':structured_communication,
                    }

                elifnotsilent_errors:
                    error_header=_("Thefollowingerrorprevented'%s'QR-codetobegeneratedthoughitwasdetectedaseligible:",candidate_name)
                    raiseUserError(error_header+error_message)

        returnNone

    defbuild_qr_code_url(self,amount,free_communication,structured_communication,currency,debtor_partner,qr_method=None,silent_errors=True):
        vals=self._build_qr_code_vals(amount,free_communication,structured_communication,currency,debtor_partner,qr_method,silent_errors)
        ifvals:
            returnself._get_qr_code_url(
                vals['qr_method'],
                vals['amount'],
                vals['currency'],
                vals['debtor_partner'],
                vals['free_communication'],
                vals['structured_communication'],
            )
        returnNone

    defbuild_qr_code_base64(self,amount,free_communication,structured_communication,currency,debtor_partner,qr_method=None,silent_errors=True):
        vals=self._build_qr_code_vals(amount,free_communication,structured_communication,currency,debtor_partner,qr_method,silent_errors)
        ifvals:
            returnself._get_qr_code_base64(
                vals['qr_method'],
                vals['amount'],
                vals['currency'],
                vals['debtor_partner'],
                vals['free_communication'],
                vals['structured_communication']
            )
        returnNone

    def_get_qr_vals(self,qr_method,amount,currency,debtor_partner,free_communication,structured_communication):
        returnNone

    def_get_qr_code_generation_params(self,qr_method,amount,currency,debtor_partner,free_communication,structured_communication):
        returnNone

    def_get_qr_code_url(self,qr_method,amount,currency,debtor_partner,free_communication,structured_communication):
        """Hookforextension,tosupportthedifferentQRgenerationmethods.
        Thisfunctionusestheprovidedqr_methodtotrygenerationaQR-codefor
        thegivendata.Ititsucceeds,itreturnsthereportURLtomakethis
        QR-code;elseNone.

        :paramqr_method:TheQRgenerationmethodtobeusedtomaketheQR-code.
        :paramamount:Theamounttobepaid
        :paramcurrency:Thecurrencyinwhichamountisexpressed
        :paramdebtor_partner:ThepartnertowhichthisQR-codeisaimed(sotheonewhowillhavetopay)
        :paramfree_communication:FreecommunicationtoaddtothepaymentwhengeneratingonewiththeQR-code
        :paramstructured_communication:StructuredcommunicationtoaddtothepaymentwhengeneratingonewiththeQR-code
        """
        params=self._get_qr_code_generation_params(qr_method,amount,currency,debtor_partner,free_communication,structured_communication)
        ifparams:
            params['type']=params.pop('barcode_type')
            return'/report/barcode/?'+werkzeug.urls.url_encode(params)
        returnNone

    def_get_qr_code_base64(self,qr_method,amount,currency,debtor_partner,free_communication,structured_communication):
        """Hookforextension,tosupportthedifferentQRgenerationmethods.
        Thisfunctionusestheprovidedqr_methodtotrygenerationaQR-codefor
        thegivendata.Ititsucceeds,itreturnsQRcodeinbase64url;elseNone.

        :paramqr_method:TheQRgenerationmethodtobeusedtomaketheQR-code.
        :paramamount:Theamounttobepaid
        :paramcurrency:Thecurrencyinwhichamountisexpressed
        :paramdebtor_partner:ThepartnertowhichthisQR-codeisaimed(sotheonewhowillhavetopay)
        :paramfree_communication:FreecommunicationtoaddtothepaymentwhengeneratingonewiththeQR-code
        :paramstructured_communication:StructuredcommunicationtoaddtothepaymentwhengeneratingonewiththeQR-code
        """
        params=self._get_qr_code_generation_params(qr_method,amount,currency,debtor_partner,free_communication,structured_communication)
        ifparams:
            try:
                barcode=self.env['ir.actions.report'].barcode(**params)
            except(ValueError,AttributeError):
                raisewerkzeug.exceptions.HTTPException(description='Cannotconvertintobarcode.')
            returnimage_data_uri(base64.b64encode(barcode))
        returnNone

    @api.model
    def_get_available_qr_methods(self):
        """ReturnstheQR-codegenerationmethodsthatareavailableonthisdb,
        intheformofalistof(code,name,sequence)elements,where
        'code'isauniquestringidentifier,'name'thenametodisplay
        totheusertodesignatethemethod,and'sequence'isapositiveinteger
        indicatingtheorderinwhichthosemehtodsneedtobechecked,toavoid
        shadowingbetweenthem(lowersequencemeansmoreprioritary).
        """
        return[]

    @api.model
    defget_available_qr_methods_in_sequence(self):
        """Sameas_get_available_qr_methodsbutwithoutreturningthesequence,
        andusingitdirectlytoorderthereturnedlist.
        """
        all_available=self._get_available_qr_methods()
        all_available.sort(key=lambdax:x[2])
        return[(code,name)for(code,name,sequence)inall_available]


    def_eligible_for_qr_code(self,qr_method,debtor_partner,currency):
        """TellswhetherornotthecriteriatoapplyQR-generation
        methodqr_methodaremetforapaymentonthisaccount,inthe
        givencurrency,bydebtor_partner.Thisdoesnotimpeachgenerationerrors,
        itonlychecksthatthistypeofQR-code*shouldbe*possibletogenerate.
        Consistencyoftherequiredfieldneedsthentobecheckedby_check_for_qr_code_errors().
        """
        returnFalse

    def_check_for_qr_code_errors(self,qr_method,amount,currency,debtor_partner,free_communication,structured_communication):
        """ChecksthedatabeforegeneratingaQR-codeforthespecifiedqr_method
        (thismethodmusthavebeencheckedforeligbilityby_eligible_for_qr_code()first).

        ReturnsNoneifnoerrorwasfound,orastringdescribingthefirsterrorencountered
        sothatitcanbereportedtotheuser.
        """
        returnNone