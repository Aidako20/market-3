#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields,_
fromflectra.exceptionsimportUserError


classResCurrency(models.Model):
    _inherit='res.currency'

    display_rounding_warning=fields.Boolean(string="DisplayRoundingWarning",compute='_compute_display_rounding_warning',
        help="Technicalfield.Usedtotellwhetherornottodisplaytheroundingwarning.Thewarninginformsaroundingfactorchangemightbedangerousonres.currency'sformview.")


    @api.depends('rounding')
    def_compute_display_rounding_warning(self):
        forrecordinself:
            record.display_rounding_warning=record.id\
                                              andrecord._origin.rounding!=record.rounding\
                                              andrecord._origin._has_accounting_entries()

    defwrite(self,vals):
        if'rounding'invals:
            rounding_val=vals['rounding']
            forrecordinself:
                if(rounding_val>record.roundingorrounding_val==0)andrecord._has_accounting_entries():
                    raiseUserError(_("Youcannotreducethenumberofdecimalplacesofacurrencywhichhasalreadybeenusedtomakeaccountingentries."))

        returnsuper(ResCurrency,self).write(vals)

    def_has_accounting_entries(self):
        """ReturnsTrueiffthiscurrencyhasbeenusedtogenerate(hence,round)
        somemovelines(eitherastheirforeigncurrency,orasthemaincurrency
        oftheircompany).
        """
        self.ensure_one()
        returnbool(self.env['account.move.line'].search_count(['|',('currency_id','=',self.id),('company_currency_id','=',self.id)]))

    @api.model
    def_get_query_currency_table(self,options):
        '''Constructthecurrencytableasamappingcompany->ratetoconverttheamounttotheuser'scompany
        currencyinamulti-company/multi-currencyenvironment.
        Thecurrency_tableisasmallpostgresqltableconstructwithVALUES.
        :paramoptions:Thereportoptions.
        :return:       Thequeryrepresentingthecurrencytable.
        '''

        user_company=self.env.company
        user_currency=user_company.currency_id
        ifoptions.get('multi_company',False):
            companies=self.env.companies
            conversion_date=options['date']['date_to']
            currency_rates=companies.mapped('currency_id')._get_rates(user_company,conversion_date)
        else:
            companies=user_company
            currency_rates={user_currency.id:1.0}

        conversion_rates=[]
        forcompanyincompanies:
            conversion_rates.extend((
                company.id,
                currency_rates[user_company.currency_id.id]/currency_rates[company.currency_id.id],
                user_currency.decimal_places,
            ))
        query='(VALUES%s)AScurrency_table(company_id,rate,precision)'%','.join('(%s,%s,%s)'foriincompanies)
        returnself.env.cr.mogrify(query,conversion_rates).decode(self.env.cr.connection.encoding)
