#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,api,_
fromflectra.exceptionsimportUserError
fromflectra.httpimportrequest


classAccountChartTemplate(models.Model):

    _inherit='account.chart.template'

    def_get_fp_vals(self,company,position):
        res=super()._get_fp_vals(company,position)
        ifcompany.country_id.code=="AR":
            res['l10n_ar_afip_responsibility_type_ids']=[
                (6,False,position.l10n_ar_afip_responsibility_type_ids.ids)]
        returnres

    def_prepare_all_journals(self,acc_template_ref,company,journals_dict=None):
        """IfArgentinianchart,wemodifythedefaultsvaluesofsalesjournaltobeapreprintedjournal
        """
        res=super()._prepare_all_journals(acc_template_ref,company,journals_dict=journals_dict)
        ifcompany.country_id.code=="AR":
            forvalsinres:
                ifvals['type']=='sale':
                    vals.update({
                        "name":"VentasPreimpreso",
                        "code":"0001",
                        "l10n_ar_afip_pos_number":1,
                        "l10n_ar_afip_pos_partner_id":company.partner_id.id,
                        "l10n_ar_afip_pos_system":'II_IM',
                        "l10n_ar_share_sequences":True,
                        "refund_sequence":False
                    })
        returnres

    @api.model
    def_get_ar_responsibility_match(self,chart_template_id):
        """returnresponsibilitytypethatmatchwiththegivenchart_template_id
        """
        match={
            self.env.ref('l10n_ar.l10nar_base_chart_template').id:self.env.ref('l10n_ar.res_RM'),
            self.env.ref('l10n_ar.l10nar_ex_chart_template').id:self.env.ref('l10n_ar.res_IVAE'),
            self.env.ref('l10n_ar.l10nar_ri_chart_template').id:self.env.ref('l10n_ar.res_IVARI'),
        }
        returnmatch.get(chart_template_id)

    def_load(self,sale_tax_rate,purchase_tax_rate,company):
        """SetcompaniesAFIPResponsibilityandCountryifARCoAisinstalled,alsosettaxcalculationrounding
        methodrequiredinordertoproperlyvalidatematchAFIPinvoices.

        Also,raiseawarningiftheuseristryingtoinstallaCoAthatdoesnotmatchwiththedefinedAFIP
        Responsibilitydefinedinthecompany
        """
        self.ensure_one()
        coa_responsibility=self._get_ar_responsibility_match(self.id)
        ifcoa_responsibility:
            company_responsibility=company.l10n_ar_afip_responsibility_type_id
            company.write({
                'l10n_ar_afip_responsibility_type_id':coa_responsibility.id,
                'country_id':self.env['res.country'].search([('code','=','AR')]).id,
                'tax_calculation_rounding_method':'round_globally',
            })
            #setCUITidentificationtype(whichistheargentinianvat)inthecreatedcompanypartnerinsteadof
            #thedefaultVATtype.
            company.partner_id.l10n_latam_identification_type_id=self.env.ref('l10n_ar.it_cuit')

        res=super()._load(sale_tax_rate,purchase_tax_rate,company)

        #IfResponsableMonotributistaremovethedefaultpurchasetax
        ifself==self.env.ref('l10n_ar.l10nar_base_chart_template')or\
           self==self.env.ref('l10n_ar.l10nar_ex_chart_template'):
            company.account_purchase_tax_id=self.env['account.tax']

        returnres
