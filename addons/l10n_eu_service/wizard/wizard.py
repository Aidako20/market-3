#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,Warning


classl10n_eu_service(models.TransientModel):
    """CreatefiscalpositionsforEUServiceVAT"""
    _name="l10n_eu_service.wizard"
    _description=__doc__

    def_get_eu_res_country_group(self):
        eu_group=self.env.ref("base.europe",raise_if_not_found=False)
        ifnoteu_group:
            raiseWarning(_('TheEuropecountrygroupcannotbefound.'
                            'Pleaseupdatethebasemodule.'))
        returneu_group

    def_get_default_company_id(self):
        returnself.env.company.id

    def_default_fiscal_position_id(self):
        user=self.env.user
        eu_id=self._get_eu_res_country_group()
        returnself.env['account.fiscal.position'].search(
            [('company_id','=',user.company_id.id),('vat_required','=',True),
             ('country_group_id.id','=',eu_id.id)],limit=1)

    def_default_tax_id(self):
        user=self.env.user
        returnself.env['account.tax'].search(
            [('company_id','=',user.company_id.id),('type_tax_use','=','sale'),
             ('amount_type','=','percent')],limit=1,order='amountdesc')

    def_default_done_country_ids(self):
        user=self.env.user
        eu_country_group=self._get_eu_res_country_group()
        returneu_country_group.country_ids-self._default_todo_country_ids()-user.company_id.country_id

    def_default_todo_country_ids(self):
        user=self.env.user
        eu_country_group=self._get_eu_res_country_group()
        eu_fiscal=self.env['account.fiscal.position'].search(
            [('country_id','in',eu_country_group.country_ids.ids),
             ('vat_required','=',False),('auto_apply','=',True),
             ('company_id','=',user.company_id.id)])
        returneu_country_group.country_ids-eu_fiscal.mapped('country_id')-user.company_id.country_id

    company_id=fields.Many2one(
        'res.company',string='Company',required=True,default=_get_default_company_id)
    fiscal_position_id=fields.Many2one(
        'account.fiscal.position',string='FiscalPosition',default=_default_fiscal_position_id,
        help="Optionalfiscalpositiontouseastemplateforgeneralaccountmapping."
             "ShouldusuallybeyourcurrentIntra-EUB2Bfiscalposition."
             "Ifnotset,nogeneralaccountmappingwillbeconfiguredforEUfiscalpositions.")
    tax_id=fields.Many2one(
        'account.tax',string='ServiceVAT',required=True,default=_default_tax_id,
        help="SelectyourcurrentVATtaxforservices.Thisisthetaxthatwillbemapped"
             "tothecorrespondingVATtaxineachEUcountryselectedbelow.")
    account_collected_id=fields.Many2one(
        "account.account",string="TaxCollectionAccount",
        help="Optionalaccounttouseforcollectingtaxamountswhensellingservicesin"
             "eachEUcountryselectedbelow.Ifnotset,thecurrentcollectingaccountof"
             "yourServiceVATwillbeused.")
    done_country_ids=fields.Many2many(
        'res.country','l10n_eu_service_country_rel_done',default=_default_done_country_ids,
        string='AlreadySupported')
    todo_country_ids=fields.Many2many(
        'res.country','l10n_eu_service_country_rel_todo',default=_default_todo_country_ids,
        string='EUCustomersFrom',required=True)

    @api.model
    defload_views(self,views,options=None):
        #Thiswizardisoutdated;itshouldn'tbeusedanymore.Usersmightstillbeabletoopenitusingthe
        #linkinthesettingsiftheydidn'tupdatethemodule.Iftheytry,wetellthem.
        raiseUserError(_("StartingJuly1st2021,OSSregulationhasreplacedMOSS.Pleasefirstupgrade'l10n_eu_service'moduleintheAppsmenu,thengobacktothissettingandclickon'Refreshtaxmapping'."))

    def_get_repartition_line_copy_values(self,original_rep_lines):
        return[(0,0,{
            'factor_percent':line.factor_percent,
            'repartition_type':line.repartition_type,
            'account_id':line.repartition_type=='tax'and(self.account_collected_id.idorline.account_id.id)orNone,
            'company_id':line.company_id.id,
            'sequence':line.sequence,
        })forlineinoriginal_rep_lines]

    defgenerate_eu_service(self):
        tax_rate=self.env["l10n_eu_service.service_tax_rate"]
        account_tax=self.env['account.tax']
        fpos=self.env['account.fiscal.position']
        forcountryinself.todo_country_ids:
            format_params={'country_name':country.name}
            tax_name=_("VATforEUServicesto%(country_name)s")%format_params
            #createanewtaxbasedontheselectedservicetax
            data_tax={
                'name':tax_name,
                'amount':tax_rate.search([('country_id','=',country.id)]).rate,
                'invoice_repartition_line_ids':self._get_repartition_line_copy_values(self.tax_id.invoice_repartition_line_ids),
                'refund_repartition_line_ids':self._get_repartition_line_copy_values(self.tax_id.refund_repartition_line_ids),
                'type_tax_use':'sale',
                'description':"EU-VAT-%s-S"%country.code,
                'sequence':1000,
            }
            tax=account_tax.create(data_tax)
            ifself.fiscal_position_id:
                account_ids=[(6,0,self.fiscal_position_id.account_ids.ids)]
            else:
                account_ids=False
            #createafiscalpositionforthecountry
            fiscal_pos_name=_("Intra-EUB2Cin%(country_name)s")%{'country_name':country.name}
            fiscal_pos_name+="(EU-VAT-%s)"%country.code
            data_fiscal={
                'name':fiscal_pos_name,
                'company_id':self.company_id.id,
                'vat_required':False,
                'auto_apply':True,
                'country_id':country.id,
                'account_ids':account_ids,
                'tax_ids':[(0,0,{'tax_src_id':self.tax_id.id,'tax_dest_id':tax.id})],
            }
            fpos.create(data_fiscal)

        return{'type':'ir.actions.act_window_close'}
