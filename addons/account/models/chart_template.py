#-*-coding:utf-8-*-
fromcollectionsimportdefaultdict

fromflectra.exceptionsimportAccessError
fromflectraimportapi,fields,models,_
fromflectraimportSUPERUSER_ID
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.httpimportrequest
fromflectra.addons.account.models.account_taximportTYPE_TAX_USE
fromflectra.toolsimporthtml_escape


importlogging

_logger=logging.getLogger(__name__)

defmigrate_set_tags_and_taxes_updatable(cr,registry,module):
    '''ThisisautilityfunctionusedtomanuallysettheflagnoupdatetoFalseontagsandaccounttaxtemplatesonlocalizationmodules
    thatneedmigration(forexampleincaseofVATreportimprovements)
    '''
    env=api.Environment(cr,SUPERUSER_ID,{})
    xml_record_ids=env['ir.model.data'].search([
        ('model','in',['account.tax.template','account.account.tag']),
        ('module','like',module)
    ]).ids
    ifxml_record_ids:
        cr.execute("updateir_model_datasetnoupdate='f'whereidin%s",(tuple(xml_record_ids),))

defpreserve_existing_tags_on_taxes(cr,registry,module):
    '''Thisisautilityfunctionusedtopreserveexistingprevioustagsduringupgradeofthemodule.'''
    env=api.Environment(cr,SUPERUSER_ID,{})
    xml_records=env['ir.model.data'].search([('model','=','account.account.tag'),('module','like',module)])
    ifxml_records:
        cr.execute("updateir_model_datasetnoupdate='t'whereidin%s",[tuple(xml_records.ids)])

defupdate_taxes_from_templates(cr,chart_template_xmlid):
    """Thismethodwilltrytoupdatetaxesbasedontheirtemplate.
    Schematicallytherearethreepossibleexecutionpath:
    [dothetemplatexmlidmatchesonetaxxmlid?]
    -NO-->we*create*anewtaxbasedonthetemplatevalues
    -YES->[arethetaxtemplateandthematchingtaxsimilarenough(detailssee`_is_tax_and_template_same`)?]
            -YES->We*update*theexistingtax'stag(andonlytags).
            -NO-->We*create*aduplicatedtaxwithtemplatevalue,andrelatedfiscalpositions.
    Thismethodismainlyusedasalocalupgradescript.
    Returnsalistoftuple(template_id,tax_id)ofnewlycreatedrecords.
    """
    def_create_taxes_from_template(company,template2tax_mapping,template2tax_to_update=None):
        """Createanewtaxesfromtemplates.Ifanoldtaxalreadyusedthesamexmlid,we
        removethexmlidfromitbutdon'tmodifyanythingelse.
        :paramcompany:thecompanyofthetaxtoinstantiate
        :paramtemplate2tax_mapping:alistoftuples(template,existing_tax)whereexisting_taxcanbeNone
        :return:alistoftuplesofids(template.id,newly_created_tax.id)
        """
        def_remove_xml_id(xml_id):
            module,name=xml_id.split('.',1)
            env['ir.model.data'].search([('module','=',module),('name','=',name)]).unlink()

        def_avoid_name_conflict(company,template):
            conflict_taxes=env['account.tax'].search([
                ('name','=',template.name),('company_id','=',company.id),
                ('type_tax_use','=',template.type_tax_use),('tax_scope','=',template.tax_scope)
            ])
            ifconflict_taxes:
                forindex,conflict_taxesinenumerate(conflict_taxes):
                    conflict_taxes.name=f"[old{indexifindex>0else''}]{conflict_taxes.name}"

        templates_to_create=env['account.tax.template'].with_context(active_test=False)
        fortemplate,old_taxintemplate2tax_mapping:
            ifold_tax:
                xml_id=old_tax.get_external_id().get(old_tax.id)
                ifxml_id:
                    _remove_xml_id(xml_id)
            _avoid_name_conflict(company,template)
            templates_to_create+=template
        new_template2tax_company=templates_to_create._generate_tax(
            company,accounts_exist=True,existing_template_to_tax=template2tax_to_update
        )['tax_template_to_tax']
        returnnew_template2tax_company.items()

    def_update_taxes_from_template(template2tax_mapping):
        """Updatethetaxes'tags(andonlytags!)basedontheircorrespondingtemplatevalues.
        :paramtemplate2tax_mapping:alistoftuples(template,existing_taxes)
        """
        fortemplate,existing_taxintemplate2tax_mapping:
            tax_rep_lines=existing_tax.invoice_repartition_line_ids+existing_tax.refund_repartition_line_ids
            template_rep_lines=template.invoice_repartition_line_ids+template.refund_repartition_line_ids
            fortax_line,template_lineinzip(tax_rep_lines,template_rep_lines):
                tags_to_add=template_line._get_tags_to_add()
                tags_to_unlink=tax_line.tag_ids
                iftags_to_add!=tags_to_unlink:
                    tax_line.write({'tag_ids':[(6,0,tags_to_add.ids)]})
                    _cleanup_tags(tags_to_unlink)

    def_get_template_to_real_xmlid_mapping(model,templates):
        """Thisfunctionusesir_model_datatoreturnamappingbetweenthetemplatesandthedata,usingtheirxmlid
        :returns:{
            company_id:{model.template.id1:model.id1,model.template.id2:model.id2},
            ...
        }
        """
        template_xmlids=[xmlid.split('.',1)[1]forxmlidintemplates.get_external_id().values()]
        res=defaultdict(dict)
        ifnottemplate_xmlids:
            returnres
        env['ir.model.data'].flush()
        env.cr.execute(
            """
            SELECT substr(data.name,0,strpos(data.name,'_'))::INTEGERASdata_company_id,
                    template.res_idAStemplate_res_id,
                    data.res_idASdata_res_id
            FROMir_model_datadata
            JOINir_model_datatemplate
            ONtemplate.name=substr(data.name,strpos(data.name,'_')+1)
            WHEREdata.model=%s
            ANDtemplate.nameIN%s
            --tax.nameisoftheform:{company_id}_{account.tax.template.name}
            """,
            [model,tuple(template_xmlids)],
        )
        forcompany_id,template_id,model_idinenv.cr.fetchall():
            res[company_id][template_id]=model_id
        returnres

    def_is_tax_and_template_same(template,tax):
        """Thisfunctioncomparesaccount.taxandaccount.tax.templaterepartitionlines.
        Ataxisconsideredthesameasthetemplateiftheyhavethesame:
            -amount_type
            -amount
            -repartitionlinespercentagesinthesameorder
        """
        iftax.children_tax_ids:
            #ifthetaxhaschildrentaxeswedon'tdochecksonrep.linesnoramount
            returntax.amount_type==template.amount_type
        else:
            tax_rep_lines=tax.invoice_repartition_line_ids+tax.refund_repartition_line_ids
            template_rep_lines=template.invoice_repartition_line_ids+template.refund_repartition_line_ids
            return(
                    tax.amount_type==template.amount_type
                    andtax.amount==template.amount
                    and(
                         len(tax_rep_lines)==len(template_rep_lines)
                         andall(
                             rep_line_tax.factor_percent==rep_line_template.factor_percent
                             forrep_line_tax,rep_line_templateinzip(tax_rep_lines,template_rep_lines)
                         )
                    )
            )

    def_cleanup_tags(tags):
        """Checksifthetagsarestillusedintaxesormovelines.Ifnotwedeleteit."""
        fortagintags:
            tax_using_tag=env['account.tax.repartition.line'].sudo().search([('tag_ids','in',tag.id)],limit=1)
            aml_using_tag=env['account.move.line'].sudo().search([('tax_tag_ids','in',tag.id)],limit=1)
            report_line_using_tag=env['account.tax.report.line'].sudo().search([('tag_ids','in',tag.id)],limit=1)
            ifnot(aml_using_tagortax_using_tagorreport_line_using_tag):
                tag.unlink()

    def_update_fiscal_positions_from_templates(chart_template,new_tax_template_by_company,all_tax_templates):
        fp_templates=env['account.fiscal.position.template'].search([('chart_template_id','=',chart_template.id)])
        template2tax=_get_template_to_real_xmlid_mapping('account.tax',all_tax_templates)
        template2fp=_get_template_to_real_xmlid_mapping('account.fiscal.position',fp_templates)

        forcompany_idinnew_tax_template_by_company:
            fp_tax_template_vals=[]
            template2fp_company=template2fp.get(company_id)
            forposition_templateinfp_templates:
                fp=env['account.fiscal.position'].browse(template2fp_company.get(position_template.id))iftemplate2fp_companyelseNone
                ifnotfp:
                    continue
                forposition_taxinposition_template.tax_ids:
                    position_tax_template_exist=fp.tax_ids.filtered(
                        lambdatax_fp:tax_fp.tax_src_id.id==template2tax.get(company_id).get(position_tax.tax_src_id.id)
                                       andtax_fp.tax_dest_id.id==(position_tax.tax_dest_idandtemplate2tax.get(company_id).get(position_tax.tax_dest_id.id)orFalse)
                    )
                    ifnotposition_tax_template_existand(
                            position_tax.tax_src_idinnew_tax_template_by_company[company_id]
                            orposition_tax.tax_dest_idinnew_tax_template_by_company[company_id]
                    ):
                        fp_tax_template_vals.append((position_tax,{
                            'tax_src_id':template2tax.get(company_id).get(position_tax.tax_src_id.id),
                            'tax_dest_id':position_tax.tax_dest_idandtemplate2tax.get(company_id).get(position_tax.tax_dest_id.id)orFalse,
                            'position_id':fp.id,
                        }))
            chart_template._create_records_with_xmlid('account.fiscal.position.tax',fp_tax_template_vals,env['res.company'].browse(company_id))

    def_process_taxes_translations(chart_template,new_template_x_taxes):
        """
        Retrievetranslationsfornewlycreatedtaxes'nameanddescription
        forlanguagesofthechart_template.
        Thoselanguagesaretheintersectionofthespoken_languagesofthechart_template
        andinstalledlanguages.
        """
        ifnotnew_template_x_taxes:
            return
        langs=chart_template._get_langs()
        iflangs:
            template_ids,tax_ids=zip(*new_template_x_taxes)
            in_ids=env['account.tax.template'].browse(template_ids)
            out_ids=env['account.tax'].browse(tax_ids)
            chart_template.process_translations(langs,'name',in_ids,out_ids)
            chart_template.process_translations(langs,'description',in_ids,out_ids)

    def_notify_accountant_managers(taxes_to_check):
        accountant_manager_group=env.ref("account.group_account_manager")
        partner_managers_ids=accountant_manager_group.users.partner_id.ids
        flectrabot_id=env.ref('base.partner_root').id
        message_body=_(
            "Pleasecheckthesetaxes.Theymightbeoutdated.Wedidnotupdatethem."
            "Indeed,theydonotexactlymatchthetaxesoftheoriginalversionofthelocalizationmodule.<br/>"
            "Youmightwanttoarchiveoradaptthem.<br/><ul>"
        )
        foraccount_taxintaxes_to_check:
            message_body+=f"<li>{html_escape(account_tax.name)}</li>"
        message_body+="</ul>"
        env['mail.thread'].message_notify(
            subject=_('Yourtaxeshavebeenupdated!'),
            author_id=flectrabot_id,
            body=message_body,
            partner_ids=partner_managers_ids,
        )

    env=api.Environment(cr,SUPERUSER_ID,{})
    chart_template=env.ref(chart_template_xmlid)
    companies=env['res.company'].search([('chart_template_id','child_of',chart_template.id)])
    templates=env['account.tax.template'].with_context(active_test=False).search([('chart_template_id','=',chart_template.id)])
    template2tax=_get_template_to_real_xmlid_mapping('account.tax',templates)
    outdated_taxes=env['account.tax']
    new_tax_template_by_company=defaultdict(env['account.tax.template'].browse) #onlycontainscompletelynewtaxes(notprevioustaxehadthexmlid)
    new_template2tax=[] #containsallcreatedtaxes
    forcompanyincompanies:
        templates_to_tax_create=[]
        templates_to_tax_update=[]
        template2oldtax_company=template2tax.get(company.id)
        fortemplateintemplates:
            tax=env['account.tax'].browse(template2oldtax_company.get(template.id))iftemplate2oldtax_companyelseNone
            ifnottaxornot_is_tax_and_template_same(template,tax):
                templates_to_tax_create.append((template,tax))
                iftax:
                    outdated_taxes+=tax
                else:
                    #weonlywanttoupdatefiscalpositionifthereisnoprevioustaxwiththemapping
                    new_tax_template_by_company[company.id]+=template
            else:
                templates_to_tax_update.append((template,tax))
        new_template2tax+=_create_taxes_from_template(company,templates_to_tax_create,templates_to_tax_update)
        _update_taxes_from_template(templates_to_tax_update)
    _update_fiscal_positions_from_templates(chart_template,new_tax_template_by_company,templates)
    ifoutdated_taxes:
        _notify_accountant_managers(outdated_taxes)
    ifhasattr(chart_template,'spoken_languages')andchart_template.spoken_languages:
        _process_taxes_translations(chart_template,new_template2tax)
    returnnew_template2tax

# ---------------------------------------------------------------
#  AccountTemplates:Account,Tax,TaxCodeandchart.+Wizard
# ---------------------------------------------------------------


classAccountGroupTemplate(models.Model):
    _name="account.group.template"
    _description='TemplateforAccountGroups'
    _order='code_prefix_start'

    parent_id=fields.Many2one('account.group.template',index=True,ondelete='cascade')
    name=fields.Char(required=True)
    code_prefix_start=fields.Char()
    code_prefix_end=fields.Char()
    chart_template_id=fields.Many2one('account.chart.template',string='ChartTemplate',required=True)


classAccountAccountTemplate(models.Model):
    _name="account.account.template"
    _description='TemplatesforAccounts'
    _order="code"

    name=fields.Char(required=True,index=True)
    currency_id=fields.Many2one('res.currency',string='AccountCurrency',help="Forcesallmovesforthisaccounttohavethissecondarycurrency.")
    code=fields.Char(size=64,required=True,index=True)
    user_type_id=fields.Many2one('account.account.type',string='Type',required=True,
        help="Thesetypesaredefinedaccordingtoyourcountry.Thetypecontainsmoreinformation"\
        "abouttheaccountanditsspecificities.")
    reconcile=fields.Boolean(string='AllowInvoices&paymentsMatching',default=False,
        help="Checkthisoptionifyouwanttheusertoreconcileentriesinthisaccount.")
    note=fields.Text()
    tax_ids=fields.Many2many('account.tax.template','account_account_template_tax_rel','account_id','tax_id',string='DefaultTaxes')
    nocreate=fields.Boolean(string='OptionalCreate',default=False,
        help="Ifchecked,thenewchartofaccountswillnotcontainthisbydefault.")
    chart_template_id=fields.Many2one('account.chart.template',string='ChartTemplate',
        help="Thisoptionalfieldallowyoutolinkanaccounttemplatetoaspecificcharttemplatethatmaydifferfromtheoneitsrootparentbelongsto.Thisallowyou"
            "todefinecharttemplatesthatextendanotherandcompleteitwithfewnewaccounts(Youdon'tneedtodefinethewholestructurethatiscommontobothseveraltimes).")
    tag_ids=fields.Many2many('account.account.tag','account_account_template_account_tag',string='Accounttag',help="Optionaltagsyoumaywanttoassignforcustomreporting")

    @api.depends('name','code')
    defname_get(self):
        res=[]
        forrecordinself:
            name=record.name
            ifrecord.code:
                name=record.code+''+name
            res.append((record.id,name))
        returnres


classAccountChartTemplate(models.Model):
    _name="account.chart.template"
    _description="AccountChartTemplate"

    name=fields.Char(required=True)
    parent_id=fields.Many2one('account.chart.template',string='ParentChartTemplate')
    code_digits=fields.Integer(string='#ofDigits',required=True,default=6,help="No.ofDigitstouseforaccountcode")
    visible=fields.Boolean(string='CanbeVisible?',default=True,
        help="SetthistoFalseifyoudon'twantthistemplatetobeusedactivelyinthewizardthatgenerateChartofAccountsfrom"
            "templates,thisisusefulwhenyouwanttogenerateaccountsofthistemplateonlywhenloadingitschildtemplate.")
    currency_id=fields.Many2one('res.currency',string='Currency',required=True)
    use_anglo_saxon=fields.Boolean(string="UseAnglo-Saxonaccounting",default=False)
    complete_tax_set=fields.Boolean(string='CompleteSetofTaxes',default=True,
        help="Thisbooleanhelpsyoutochooseifyouwanttoproposetotheusertoencodethesaleandpurchaseratesorchoosefromlist"
            "oftaxes.Thislastchoiceassumesthatthesetoftaxdefinedonthistemplateiscomplete")
    account_ids=fields.One2many('account.account.template','chart_template_id',string='AssociatedAccountTemplates')
    tax_template_ids=fields.One2many('account.tax.template','chart_template_id',string='TaxTemplateList',
        help='Listofallthetaxesthathavetobeinstalledbythewizard')
    bank_account_code_prefix=fields.Char(string='Prefixofthebankaccounts',required=True)
    cash_account_code_prefix=fields.Char(string='Prefixofthemaincashaccounts',required=True)
    transfer_account_code_prefix=fields.Char(string='Prefixofthemaintransferaccounts',required=True)
    income_currency_exchange_account_id=fields.Many2one('account.account.template',
        string="GainExchangeRateAccount",domain=[('internal_type','=','other'),('deprecated','=',False)])
    expense_currency_exchange_account_id=fields.Many2one('account.account.template',
        string="LossExchangeRateAccount",domain=[('internal_type','=','other'),('deprecated','=',False)])
    account_journal_suspense_account_id=fields.Many2one('account.account.template',string='JournalSuspenseAccount')
    default_cash_difference_income_account_id=fields.Many2one('account.account.template',string="CashDifferenceIncomeAccount")
    default_cash_difference_expense_account_id=fields.Many2one('account.account.template',string="CashDifferenceExpenseAccount")
    default_pos_receivable_account_id=fields.Many2one('account.account.template',string="PoSreceivableaccount")
    property_account_receivable_id=fields.Many2one('account.account.template',string='ReceivableAccount')
    property_account_payable_id=fields.Many2one('account.account.template',string='PayableAccount')
    property_account_expense_categ_id=fields.Many2one('account.account.template',string='CategoryofExpenseAccount')
    property_account_income_categ_id=fields.Many2one('account.account.template',string='CategoryofIncomeAccount')
    property_account_expense_id=fields.Many2one('account.account.template',string='ExpenseAccountonProductTemplate')
    property_account_income_id=fields.Many2one('account.account.template',string='IncomeAccountonProductTemplate')
    property_stock_account_input_categ_id=fields.Many2one('account.account.template',string="InputAccountforStockValuation")
    property_stock_account_output_categ_id=fields.Many2one('account.account.template',string="OutputAccountforStockValuation")
    property_stock_valuation_account_id=fields.Many2one('account.account.template',string="AccountTemplateforStockValuation")
    property_tax_payable_account_id=fields.Many2one('account.account.template',string="Taxcurrentaccount(payable)")
    property_tax_receivable_account_id=fields.Many2one('account.account.template',string="Taxcurrentaccount(receivable)")
    property_advance_tax_payment_account_id=fields.Many2one('account.account.template',string="Advancetaxpaymentaccount")
    property_cash_basis_base_account_id=fields.Many2one(
        comodel_name='account.account.template',
        domain=[('deprecated','=',False)],
        string="BaseTaxReceivedAccount",
        help="Accountthatwillbesetonlinescreatedincashbasisjournalentryandusedtokeeptrackofthe"
             "taxbaseamount.")

    @api.model
    def_prepare_transfer_account_template(self,prefix=None):
        '''Preparevaluestocreatethetransferaccountthatisanintermediaryaccountusedwhenmovingmoney
        fromaliquidityaccounttoanother.

        :return:   Adictionaryofvaluestocreateanewaccount.account.
        '''
        digits=self.code_digits
        prefix=prefixorself.transfer_account_code_prefixor''
        #Flattenthehierarchyofcharttemplates.
        chart_template=self
        chart_templates=self
        whilechart_template.parent_id:
            chart_templates+=chart_template.parent_id
            chart_template=chart_template.parent_id
        new_code=''
        fornuminrange(1,100):
            new_code=str(prefix.ljust(digits-1,'0'))+str(num)
            rec=self.env['account.account.template'].search(
                [('code','=',new_code),('chart_template_id','in',chart_templates.ids)],limit=1)
            ifnotrec:
                break
        else:
            raiseUserError(_('Cannotgenerateanunusedaccountcode.'))
        current_assets_type=self.env.ref('account.data_account_type_current_assets',raise_if_not_found=False)
        return{
            'name':_('LiquidityTransfer'),
            'code':new_code,
            'user_type_id':current_assets_typeandcurrent_assets_type.idorFalse,
            'reconcile':True,
            'chart_template_id':self.id,
        }

    @api.model
    def_create_liquidity_journal_suspense_account(self,company,code_digits):
        returnself.env['account.account'].create({
            'name':_("BankSuspenseAccount"),
            'code':self.env['account.account']._search_new_account_code(company,code_digits,company.bank_account_code_prefixor''),
            'user_type_id':self.env.ref('account.data_account_type_current_assets').id,
            'company_id':company.id,
        })

    deftry_loading(self,company=False):
        """Installsthischartofaccountsforthecurrentcompanyifnotchart
        ofaccountshadbeencreatedforityet.
        """
        #donotuse`request.env`here,itcancausedeadlocks
        ifnotcompany:
            ifrequestandhasattr(request,'allowed_company_ids'):
                company=self.env['res.company'].browse(request.allowed_company_ids[0])
            else:
                company=self.env.company
        #Ifwedon'thaveanychartofaccountonthiscompany,installthischartofaccount
        ifnotcompany.chart_template_idandnotself.existing_accounting(company):
            fortemplateinself:
                template.with_context(default_company_id=company.id)._load(15.0,15.0,company)


    def_load(self,sale_tax_rate,purchase_tax_rate,company):
        """Installsthischartofaccountsonthecurrentcompany,replacing
        theexistingoneifithadalreadyonedefined.Ifsomeaccountingentries
        hadalreadybeenmade,thisfunctionfailsinstead,triggeringaUserError.

        Also,notethatthisfunctioncanonlyberunbysomeonewithadministration
        rights.
        """
        self.ensure_one()
        #donotuse`request.env`here,itcancausedeadlocks
        #Ensureeverythingistranslatedtothecompany'slanguage,nottheuser'sone.
        self=self.with_context(lang=company.partner_id.lang).with_company(company)
        ifnotself.env.is_admin():
            raiseAccessError(_("Onlyadministratorscanloadachartofaccounts"))

        existing_accounts=self.env['account.account'].search([('company_id','=',company.id)])
        ifexisting_accounts:
            #wetolerateswitchingfromaccountingpackage(localizationmodule)aslongasthereisn'tyetanyaccounting
            #entriescreatedforthecompany.
            ifself.existing_accounting(company):
                raiseUserError(_('Couldnotinstallnewchartofaccountastherearealreadyaccountingentriesexisting.'))

            #deleteaccountingproperties
            prop_values=['account.account,%s'%(account_id,)foraccount_idinexisting_accounts.ids]
            existing_journals=self.env['account.journal'].search([('company_id','=',company.id)])
            ifexisting_journals:
                prop_values.extend(['account.journal,%s'%(journal_id,)forjournal_idinexisting_journals.ids])
            self.env['ir.property'].sudo().search(
                [('value_reference','in',prop_values)]
            ).unlink()

            #deleteaccount,journal,tax,fiscalpositionandreconciliationmodel
            models_to_delete=['account.reconcile.model','account.fiscal.position','account.tax','account.move','account.journal','account.group']
            formodelinmodels_to_delete:
                res=self.env[model].sudo().search([('company_id','=',company.id)])
                iflen(res):
                    res.unlink()
            existing_accounts.unlink()

        company.write({'currency_id':self.currency_id.id,
                       'anglo_saxon_accounting':self.use_anglo_saxon,
                       'bank_account_code_prefix':self.bank_account_code_prefix,
                       'cash_account_code_prefix':self.cash_account_code_prefix,
                       'transfer_account_code_prefix':self.transfer_account_code_prefix,
                       'chart_template_id':self.id
        })

        #setthecoacurrencytoactive
        self.currency_id.write({'active':True})

        #WhenweinstalltheCoAoffirstcompany,setthecurrencytopricetypesandpricelists
        ifcompany.id==1:
            forreferencein['product.list_price','product.standard_price','product.list0']:
                try:
                    tmp2=self.env.ref(reference).write({'currency_id':self.currency_id.id})
                exceptValueError:
                    pass

        #Ifthefloatsforsale/purchaserateshavebeenfilled,createtemplatesfromthem
        self._create_tax_templates_from_rates(company.id,sale_tax_rate,purchase_tax_rate)

        #Installallthetemplatesobjectsandgeneratetherealobjects
        acc_template_ref,taxes_ref=self._install_template(company,code_digits=self.code_digits)

        #Setdefaultcashdifferenceaccountoncompany
        ifnotcompany.account_journal_suspense_account_id:
            company.account_journal_suspense_account_id=self._create_liquidity_journal_suspense_account(company,self.code_digits)

        ifnotcompany.default_cash_difference_expense_account_id:
            company.default_cash_difference_expense_account_id=self.env['account.account'].create({
                'name':_('CashDifferenceLoss'),
                'code':self.env['account.account']._search_new_account_code(company,self.code_digits,'999'),
                'user_type_id':self.env.ref('account.data_account_type_expenses').id,
                'tag_ids':[(6,0,self.env.ref('account.account_tag_investing').ids)],
                'company_id':company.id,
            })

        ifnotcompany.default_cash_difference_income_account_id:
            company.default_cash_difference_income_account_id=self.env['account.account'].create({
                'name':_('CashDifferenceGain'),
                'code':self.env['account.account']._search_new_account_code(company,self.code_digits,'999'),
                'user_type_id':self.env.ref('account.data_account_type_revenue').id,
                'tag_ids':[(6,0,self.env.ref('account.account_tag_investing').ids)],
                'company_id':company.id,
            })

        #Setthetransferaccountonthecompany
        company.transfer_account_id=self.env['account.account'].search([
            ('code','=like',self.transfer_account_code_prefix+'%'),('company_id','=',company.id)],limit=1)

        #CreateBankjournals
        self._create_bank_journals(company,acc_template_ref)

        #Createthecurrentyearearningaccountifitwasn'tpresentintheCoA
        company.get_unaffected_earnings_account()

        #setthedefaulttaxesonthecompany
        company.account_sale_tax_id=self.env['account.tax'].search([('type_tax_use','in',('sale','all')),('company_id','=',company.id)],limit=1).id
        company.account_purchase_tax_id=self.env['account.tax'].search([('type_tax_use','in',('purchase','all')),('company_id','=',company.id)],limit=1).id

        return{}

    @api.model
    defexisting_accounting(self,company_id):
        """ReturnsTrueiffsomeaccountingentrieshavealreadybeenmadefor
        theprovidedcompany(meaninghencethatitschartofaccountscannot
        bechangedanymore).
        """
        model_to_check=['account.move.line','account.payment','account.bank.statement']
        formodelinmodel_to_check:
            ifself.env[model].sudo().search([('company_id','=',company_id.id)],limit=1):
                returnTrue
        ifself.env['account.move'].sudo().search([('company_id','=',company_id.id),('name','!=','/')],limit=1):
            returnTrue
        returnFalse

    def_create_tax_templates_from_rates(self,company_id,sale_tax_rate,purchase_tax_rate):
        '''
        Thisfunctionchecksifthischarttemplateisconfiguredascontainingafullsetoftaxes,andif
        it'snotthecase,itcreatesthetemplatesforaccount.taxobjectaccordinglytotheprovidedsale/purchaserates.
        Thenitsavesthenewtaxtemplatesasdefaulttaxestouseforthischarttemplate.

        :paramcompany_id:idofthecompanyforwhichthewizardisrunning
        :paramsale_tax_rate:theratetouseforcreatedsalestax
        :parampurchase_tax_rate:theratetouseforcreatedpurchasetax
        :return:True
        '''
        self.ensure_one()
        obj_tax_temp=self.env['account.tax.template']
        all_parents=self._get_chart_parent_ids()
        #createtaxtemplatesfrompurchase_tax_rateandsale_tax_ratefields
        ifnotself.complete_tax_set:
            ref_taxs=obj_tax_temp.search([('type_tax_use','=','sale'),('chart_template_id','in',all_parents)],order="sequence,iddesc",limit=1)
            ref_taxs.write({'amount':sale_tax_rate,'name':_('Tax%.2f%%')%sale_tax_rate,'description':'%.2f%%'%sale_tax_rate})
            ref_taxs=obj_tax_temp.search([('type_tax_use','=','purchase'),('chart_template_id','in',all_parents)],order="sequence,iddesc",limit=1)
            ref_taxs.write({'amount':purchase_tax_rate,'name':_('Tax%.2f%%')%purchase_tax_rate,'description':'%.2f%%'%purchase_tax_rate})
        returnTrue

    def_get_chart_parent_ids(self):
        """ReturnstheIDsofallancestorcharts,includingthechartitself.
            (inverseofchild_ofoperator)

            :return:theIDSofallancestorcharts,includingthechartitself.
        """
        chart_template=self
        result=[chart_template.id]
        whilechart_template.parent_id:
            chart_template=chart_template.parent_id
            result.append(chart_template.id)
        returnresult

    def_create_bank_journals(self,company,acc_template_ref):
        '''
        Thisfunctioncreatesbankjournalsandtheiraccountforeachline
        datareturnedbythefunction_get_default_bank_journals_data.

        :paramcompany:thecompanyforwhichthewizardisrunning.
        :paramacc_template_ref:thedictionarycontainingthemappingbetweentheidsofaccounttemplatesandtheids
            oftheaccountsthathavebeengeneratedfromthem.
        '''
        self.ensure_one()
        bank_journals=self.env['account.journal']
        #Createthejournalsthatwilltriggertheaccount.accountcreation
        foraccinself._get_default_bank_journals_data():
            bank_journals+=self.env['account.journal'].create({
                'name':acc['acc_name'],
                'type':acc['account_type'],
                'company_id':company.id,
                'currency_id':acc.get('currency_id',self.env['res.currency']).id,
                'sequence':10,
            })

        returnbank_journals

    @api.model
    def_get_default_bank_journals_data(self):
        """Returnsthedataneededtocreatethedefaultbankjournalswhen
        installingthischartofaccounts,intheformofalistofdictionaries.
        Theallowedkeysinthesedictionariesare:
            -acc_name:string(mandatory)
            -account_type:'cash'or'bank'(mandatory)
            -currency_id(optional,onlytobespecifiedif!=company.currency_id)
        """
        return[{'acc_name':_('Cash'),'account_type':'cash'},{'acc_name':_('Bank'),'account_type':'bank'}]

    defopen_select_template_wizard(self):
        #Addactiontoopenwizardtoselectbetweenseveraltemplates
        ifnotself.company_id.chart_template_id:
            todo=self.env['ir.actions.todo']
            action_rec=self.env['ir.model.data'].xmlid_to_object('account.action_wizard_multi_chart')
            ifaction_rec:
                todo.create({'action_id':action_rec.id,'name':_('ChooseAccountingTemplate')})
        returnTrue

    @api.model
    def_prepare_transfer_account_for_direct_creation(self,name,company):
        """Preparevaluestocreateatransferaccountdirectly,basedonthe
        method_prepare_transfer_account_template().

        Thisisneededwhendealingwithinstallationofpaymentmodules
        thatrequiresthecreationoftheirowntransferaccount.

        :paramname:       Thetransferaccountname.
        :paramcompany:    Thecompanyowningthisaccount.
        :return:           Adictionaryofvaluestocreateanewaccount.account.
        """
        vals=self._prepare_transfer_account_template()
        digits=self.code_digitsor6
        prefix=self.transfer_account_code_prefixor''
        vals.update({
            'code':self.env['account.account']._search_new_account_code(company,digits,prefix),
            'name':name,
            'company_id':company.id,
        })
        del(vals['chart_template_id'])
        returnvals

    @api.model
    defgenerate_journals(self,acc_template_ref,company,journals_dict=None):
        """
        Thismethodisusedforcreatingjournals.

        :paramacc_template_ref:Accounttemplatesreference.
        :paramcompany_id:companytogeneratejournalsfor.
        :returns:True
        """
        JournalObj=self.env['account.journal']
        forvals_journalinself._prepare_all_journals(acc_template_ref,company,journals_dict=journals_dict):
            journal=JournalObj.create(vals_journal)
            ifvals_journal['type']=='general'andvals_journal['code']==_('EXCH'):
                company.write({'currency_exchange_journal_id':journal.id})
            ifvals_journal['type']=='general'andvals_journal['code']==_('CABA'):
                company.write({'tax_cash_basis_journal_id':journal.id})
        returnTrue

    def_prepare_all_journals(self,acc_template_ref,company,journals_dict=None):
        def_get_default_account(journal_vals,type='debit'):
            #Getthedefaultaccounts
            default_account=False
            ifjournal['type']=='sale':
                default_account=acc_template_ref.get(self.property_account_income_categ_id.id)
            elifjournal['type']=='purchase':
                default_account=acc_template_ref.get(self.property_account_expense_categ_id.id)

            returndefault_account

        journals=[{'name':_('CustomerInvoices'),'type':'sale','code':_('INV'),'favorite':True,'color':11,'sequence':5},
                    {'name':_('VendorBills'),'type':'purchase','code':_('BILL'),'favorite':True,'color':11,'sequence':6},
                    {'name':_('MiscellaneousOperations'),'type':'general','code':_('MISC'),'favorite':True,'sequence':7},
                    {'name':_('ExchangeDifference'),'type':'general','code':_('EXCH'),'favorite':False,'sequence':9},
                    {'name':_('CashBasisTaxes'),'type':'general','code':_('CABA'),'favorite':False,'sequence':10}]
        ifjournals_dict!=None:
            journals.extend(journals_dict)

        self.ensure_one()
        journal_data=[]
        forjournalinjournals:
            vals={
                'type':journal['type'],
                'name':journal['name'],
                'code':journal['code'],
                'company_id':company.id,
                'default_account_id':_get_default_account(journal),
                'show_on_dashboard':journal['favorite'],
                'color':journal.get('color',False),
                'sequence':journal['sequence']
            }
            journal_data.append(vals)
        returnjournal_data

    defgenerate_properties(self,acc_template_ref,company):
        """
        Thismethodusedforcreatingproperties.

        :paramacc_template_ref:Mappingbetweenidsofaccounttemplatesandrealaccountscreatedfromthem
        :paramcompany_id:companytogeneratepropertiesfor.
        :returns:True
        """
        self.ensure_one()
        PropertyObj=self.env['ir.property']
        todo_list=[
            ('property_account_receivable_id','res.partner'),
            ('property_account_payable_id','res.partner'),
            ('property_account_expense_categ_id','product.category'),
            ('property_account_income_categ_id','product.category'),
            ('property_account_expense_id','product.template'),
            ('property_account_income_id','product.template'),
            ('property_tax_payable_account_id','account.tax.group'),
            ('property_tax_receivable_account_id','account.tax.group'),
            ('property_advance_tax_payment_account_id','account.tax.group'),
        ]
        forfield,modelintodo_list:
            account=self[field]
            value=acc_template_ref[account.id]ifaccountelseFalse
            ifvalue:
                PropertyObj._set_default(field,model,value,company=company)

        stock_properties=[
            'property_stock_account_input_categ_id',
            'property_stock_account_output_categ_id',
            'property_stock_valuation_account_id',
        ]
        forstock_propertyinstock_properties:
            account=getattr(self,stock_property)
            value=accountandacc_template_ref[account.id]orFalse
            ifvalue:
                company.write({stock_property:value})
        returnTrue

    def_install_template(self,company,code_digits=None,obj_wizard=None,acc_ref=None,taxes_ref=None):
        """Recursivelyloadthetemplateobjectsandcreatetherealobjectsfromthem.

            :paramcompany:companythewizardisrunningfor
            :paramcode_digits:numberofdigitstheaccountscodeshouldhaveintheCOA
            :paramobj_wizard:thecurrentwizardforgeneratingtheCOAfromthetemplates
            :paramacc_ref:Mappingbetweenidsofaccounttemplatesandrealaccountscreatedfromthem
            :paramtaxes_ref:Mappingbetweenidsoftaxtemplatesandrealtaxescreatedfromthem
            :returns:tuplewithadictionarycontaining
                *themappingbetweentheaccounttemplateidsandtheidsoftherealaccountsthathavebeengenerated
                  fromthem,asfirstitem,
                *asimilardictionaryformappingthetaxtemplatesandtaxes,asseconditem,
            :rtype:tuple(dict,dict,dict)
        """
        self.ensure_one()
        ifacc_refisNone:
            acc_ref={}
        iftaxes_refisNone:
            taxes_ref={}
        ifself.parent_id:
            tmp1,tmp2=self.parent_id._install_template(company,code_digits=code_digits,acc_ref=acc_ref,taxes_ref=taxes_ref)
            acc_ref.update(tmp1)
            taxes_ref.update(tmp2)
        #Ensure,evenifindividually,thateverythingistranslatedaccordingtothecompany'slanguage.
        tmp1,tmp2=self.with_context(lang=company.partner_id.lang)._load_template(company,code_digits=code_digits,account_ref=acc_ref,taxes_ref=taxes_ref)
        acc_ref.update(tmp1)
        taxes_ref.update(tmp2)
        returnacc_ref,taxes_ref

    def_load_template(self,company,code_digits=None,account_ref=None,taxes_ref=None):
        """Generatealltheobjectsfromthetemplates

            :paramcompany:companythewizardisrunningfor
            :paramcode_digits:numberofdigitstheaccountscodeshouldhaveintheCOA
            :paramacc_ref:Mappingbetweenidsofaccounttemplatesandrealaccountscreatedfromthem
            :paramtaxes_ref:Mappingbetweenidsoftaxtemplatesandrealtaxescreatedfromthem
            :returns:tuplewithadictionarycontaining
                *themappingbetweentheaccounttemplateidsandtheidsoftherealaccountsthathavebeengenerated
                  fromthem,asfirstitem,
                *asimilardictionaryformappingthetaxtemplatesandtaxes,asseconditem,
            :rtype:tuple(dict,dict,dict)
        """
        self.ensure_one()
        ifaccount_refisNone:
            account_ref={}
        iftaxes_refisNone:
            taxes_ref={}
        ifnotcode_digits:
            code_digits=self.code_digits
        AccountTaxObj=self.env['account.tax']

        #Generatetaxesfromtemplates.
        generated_tax_res=self.with_context(active_test=False).tax_template_ids._generate_tax(company)
        taxes_ref.update(generated_tax_res['tax_template_to_tax'])

        #GeneratingAccountsfromtemplates.
        account_template_ref=self.generate_account(taxes_ref,account_ref,code_digits,company)
        account_ref.update(account_template_ref)

        #Generateaccountgroups,fromtemplate
        self.generate_account_groups(company)

        #writingaccountvaluesaftercreationofaccounts
        forkey,valueingenerated_tax_res['account_dict']['account.tax'].items():
            ifvalue['cash_basis_transition_account_id']:
                AccountTaxObj.browse(key).write({
                    'cash_basis_transition_account_id':account_ref.get(value['cash_basis_transition_account_id'],False),
                })

        AccountTaxRepartitionLineObj=self.env['account.tax.repartition.line']
        forkey,valueingenerated_tax_res['account_dict']['account.tax.repartition.line'].items():
            ifvalue['account_id']:
                AccountTaxRepartitionLineObj.browse(key).write({
                    'account_id':account_ref.get(value['account_id']),
                })

        #Setthecompanyaccounts
        self._load_company_accounts(account_ref,company)

        #CreateJournals-Onlydoneforrootcharttemplate
        ifnotself.parent_id:
            self.generate_journals(account_ref,company)

        #generatepropertiesfunction
        self.generate_properties(account_ref,company)

        #GenerateFiscalPosition,FiscalPositionAccountsandFiscalPositionTaxesfromtemplates
        self.generate_fiscal_position(taxes_ref,account_ref,company)

        #Generateaccountoperationtemplatetemplates
        self.generate_account_reconcile_model(taxes_ref,account_ref,company)

        returnaccount_ref,taxes_ref

    def_load_company_accounts(self,account_ref,company):
        #Setthedefaultaccountsonthecompany
        accounts={
            'default_cash_difference_income_account_id':self.default_cash_difference_income_account_id.id,
            'default_cash_difference_expense_account_id':self.default_cash_difference_expense_account_id.id,
            'account_journal_suspense_account_id':self.account_journal_suspense_account_id.id,
            'account_cash_basis_base_account_id':self.property_cash_basis_base_account_id.id,
            'account_default_pos_receivable_account_id':self.default_pos_receivable_account_id.id,
            'income_currency_exchange_account_id':self.income_currency_exchange_account_id.id,
            'expense_currency_exchange_account_id':self.expense_currency_exchange_account_id.id,
        }

        values={}

        #Theloopistoavoidwritingwhenwehavenovalues,thusavoidingerasingtheaccountfromtheparent
        forkey,accountinaccounts.items():
            ifaccount_ref.get(account):
                values[key]=account_ref.get(account)

        company.write(values)

    defcreate_record_with_xmlid(self,company,template,model,vals):
        returnself._create_records_with_xmlid(model,[(template,vals)],company).id

    def_create_records_with_xmlid(self,model,template_vals,company):
        """Createrecordsforthegivenmodelnamewiththegivenvals,and
            createxmlidsbasedoneachrecord'stemplateandcompanyid.
        """
        ifnottemplate_vals:
            returnself.env[model]
        template_model=template_vals[0][0]
        template_ids=[template.idfortemplate,valsintemplate_vals]
        template_xmlids=template_model.browse(template_ids).get_external_id()
        data_list=[]
        fortemplate,valsintemplate_vals:
            module,name=template_xmlids[template.id].split('.',1)
            xml_id="%s.%s_%s"%(module,company.id,name)
            data_list.append(dict(xml_id=xml_id,values=vals,noupdate=True))
        returnself.env[model]._load_records(data_list)

    @api.model
    def_load_records(self,data_list,update=False):
        #Whencreatingacharttemplatecreate,fortheliquiditytransferaccount
        # -anaccount.account.template:thisallowtodefineaccount.reconcile.model.templateobjectsreferingthatliquiditytransfer
        #   accountalthoughit'snotexistinginanyxmlfile
        # -anentryinir_model_data:thisallowtostillusethemethodcreate_record_with_xmlid()anddon'tmakeanydifferencebetween
        #   regularaccountscreatedandthatliquiditytransferaccount
        records=super(AccountChartTemplate,self)._load_records(data_list,update)
        account_data_list=[]
        fordata,recordinzip(data_list,records):
            #Createthetransferaccountonlyforleafcharttemplateinthehierarchy.
            ifrecord.parent_id:
                continue
            ifdata.get('xml_id'):
                account_xml_id=data['xml_id']+'_liquidity_transfer'
                ifnotself.env.ref(account_xml_id,raise_if_not_found=False):
                    account_vals=record._prepare_transfer_account_template()
                    account_data_list.append(dict(
                        xml_id=account_xml_id,
                        values=account_vals,
                        noupdate=data.get('noupdate'),
                    ))
        self.env['account.account.template']._load_records(account_data_list,update)
        returnrecords

    def_get_account_vals(self,company,account_template,code_acc,tax_template_ref):
        """Thismethodgeneratesadictionaryofallthevaluesfortheaccountthatwillbecreated.
        """
        self.ensure_one()
        tax_ids=[]
        fortaxinaccount_template.tax_ids:
            tax_ids.append(tax_template_ref[tax.id])
        val={
                'name':account_template.name,
                'currency_id':account_template.currency_idandaccount_template.currency_id.idorFalse,
                'code':code_acc,
                'user_type_id':account_template.user_type_idandaccount_template.user_type_id.idorFalse,
                'reconcile':account_template.reconcile,
                'note':account_template.note,
                'tax_ids':[(6,0,tax_ids)],
                'company_id':company.id,
                'tag_ids':[(6,0,[t.idfortinaccount_template.tag_ids])],
            }
        returnval

    defgenerate_account(self,tax_template_ref,acc_template_ref,code_digits,company):
        """Thismethodgeneratesaccountsfromaccounttemplates.

        :paramtax_template_ref:Taxestemplatesreferenceforwritetaxes_idinaccount_account.
        :paramacc_template_ref:dictionarycontainingthemappingbetweentheaccounttemplatesandgeneratedaccounts(willbepopulated)
        :paramcode_digits:numberofdigitstouseforaccountcode.
        :paramcompany_id:companytogenerateaccountsfor.
        :returns:returnacc_template_refforreferencepurpose.
        :rtype:dict
        """
        self.ensure_one()
        account_tmpl_obj=self.env['account.account.template']
        acc_template=account_tmpl_obj.search([('nocreate','!=',True),('chart_template_id','=',self.id)],order='id')
        template_vals=[]
        foraccount_templateinacc_template:
            code_main=account_template.codeandlen(account_template.code)or0
            code_acc=account_template.codeor''
            ifcode_main>0andcode_main<=code_digits:
                code_acc=str(code_acc)+(str('0'*(code_digits-code_main)))
            vals=self._get_account_vals(company,account_template,code_acc,tax_template_ref)
            template_vals.append((account_template,vals))
        accounts=self._create_records_with_xmlid('account.account',template_vals,company)
        fortemplate,accountinzip(acc_template,accounts):
            acc_template_ref[template.id]=account.id
        returnacc_template_ref

    defgenerate_account_groups(self,company):
        """Thismethodgeneratesaccountgroupsfromaccountgroupstemplates.
        :paramcompany:companytogeneratetheaccountgroupsfor
        """
        self.ensure_one()
        group_templates=self.env['account.group.template'].search([('chart_template_id','=',self.id)])
        template_vals=[]
        forgroup_templateingroup_templates:
            vals={
                'name':group_template.name,
                'code_prefix_start':group_template.code_prefix_start,
                'code_prefix_end':group_template.code_prefix_end,
                'company_id':company.id,
            }
            template_vals.append((group_template,vals))
        groups=self._create_records_with_xmlid('account.group',template_vals,company)

    def_prepare_reconcile_model_vals(self,company,account_reconcile_model,acc_template_ref,tax_template_ref):
        """Thismethodgeneratesadictionaryofallthevaluesfortheaccount.reconcile.modelthatwillbecreated.
        """
        self.ensure_one()
        account_reconcile_model_lines=self.env['account.reconcile.model.line.template'].search([
            ('model_id','=',account_reconcile_model.id)
        ])
        return{
            'name':account_reconcile_model.name,
            'sequence':account_reconcile_model.sequence,
            'company_id':company.id,
            'rule_type':account_reconcile_model.rule_type,
            'auto_reconcile':account_reconcile_model.auto_reconcile,
            'to_check':account_reconcile_model.to_check,
            'match_journal_ids':[(6,None,account_reconcile_model.match_journal_ids.ids)],
            'match_nature':account_reconcile_model.match_nature,
            'match_amount':account_reconcile_model.match_amount,
            'match_amount_min':account_reconcile_model.match_amount_min,
            'match_amount_max':account_reconcile_model.match_amount_max,
            'match_label':account_reconcile_model.match_label,
            'match_label_param':account_reconcile_model.match_label_param,
            'match_note':account_reconcile_model.match_note,
            'match_note_param':account_reconcile_model.match_note_param,
            'match_transaction_type':account_reconcile_model.match_transaction_type,
            'match_transaction_type_param':account_reconcile_model.match_transaction_type_param,
            'match_same_currency':account_reconcile_model.match_same_currency,
            'match_total_amount':account_reconcile_model.match_total_amount,
            'match_total_amount_param':account_reconcile_model.match_total_amount_param,
            'match_partner':account_reconcile_model.match_partner,
            'match_partner_ids':[(6,None,account_reconcile_model.match_partner_ids.ids)],
            'match_partner_category_ids':[(6,None,account_reconcile_model.match_partner_category_ids.ids)],
            'line_ids':[(0,0,{
                'account_id':acc_template_ref[line.account_id.id],
                'label':line.label,
                'amount_type':line.amount_type,
                'force_tax_included':line.force_tax_included,
                'amount_string':line.amount_string,
                'tax_ids':[[4,tax_template_ref[tax.id],0]fortaxinline.tax_ids],
            })forlineinaccount_reconcile_model_lines],
        }

    defgenerate_account_reconcile_model(self,tax_template_ref,acc_template_ref,company):
        """Thismethodcreatesaccountreconcilemodels

        :paramtax_template_ref:Taxestemplatesreferenceforwritetaxes_idinaccount_account.
        :paramacc_template_ref:dictionarywiththemappingbetweentheaccounttemplatesandtherealaccounts.
        :paramcompany_id:companytocreatemodelsfor
        :returns:returnnew_account_reconcile_modelforreferencepurpose.
        :rtype:dict
        """
        self.ensure_one()
        account_reconcile_models=self.env['account.reconcile.model.template'].search([
            ('chart_template_id','=',self.id)
        ])
        foraccount_reconcile_modelinaccount_reconcile_models:
            vals=self._prepare_reconcile_model_vals(company,account_reconcile_model,acc_template_ref,tax_template_ref)
            self.create_record_with_xmlid(company,account_reconcile_model,'account.reconcile.model',vals)
        #Createadefaultruleforthereconciliationwidgetmatchinginvoicesautomatically.
        ifnotself.parent_id:
            self.env['account.reconcile.model'].sudo().create({
                "name":_('InvoicesMatchingRule'),
                "sequence":'1',
                "rule_type":'invoice_matching',
                "auto_reconcile":False,
                "match_nature":'both',
                "match_same_currency":True,
                "match_total_amount":True,
                "match_total_amount_param":100,
                "match_partner":True,
                "company_id":company.id,
            })
        returnTrue

    def_get_fp_vals(self,company,position):
        return{
            'company_id':company.id,
            'sequence':position.sequence,
            'name':position.name,
            'note':position.note,
            'auto_apply':position.auto_apply,
            'vat_required':position.vat_required,
            'country_id':position.country_id.id,
            'country_group_id':position.country_group_id.id,
            'state_ids':position.state_idsand[(6,0,position.state_ids.ids)]or[],
            'zip_from':position.zip_from,
            'zip_to':position.zip_to,
        }

    defgenerate_fiscal_position(self,tax_template_ref,acc_template_ref,company):
        """ThismethodgeneratesFiscalPosition,FiscalPositionAccounts
        andFiscalPositionTaxesfromtemplates.

        :paramtaxes_ids:Taxestemplatesreferenceforgeneratingaccount.fiscal.position.tax.
        :paramacc_template_ref:Accounttemplatesreferenceforgeneratingaccount.fiscal.position.account.
        :paramcompany_id:thecompanytogeneratefiscalpositiondatafor
        :returns:True
        """
        self.ensure_one()
        positions=self.env['account.fiscal.position.template'].search([('chart_template_id','=',self.id)])

        #firstcreatefiscalpositionsinbatch
        template_vals=[]
        forpositioninpositions:
            fp_vals=self._get_fp_vals(company,position)
            template_vals.append((position,fp_vals))
        fps=self._create_records_with_xmlid('account.fiscal.position',template_vals,company)

        #thencreatefiscalpositiontaxesandaccounts
        tax_template_vals=[]
        account_template_vals=[]
        forposition,fpinzip(positions,fps):
            fortaxinposition.tax_ids:
                tax_template_vals.append((tax,{
                    'tax_src_id':tax_template_ref[tax.tax_src_id.id],
                    'tax_dest_id':tax.tax_dest_idandtax_template_ref[tax.tax_dest_id.id]orFalse,
                    'position_id':fp.id,
                }))
            foraccinposition.account_ids:
                account_template_vals.append((acc,{
                    'account_src_id':acc_template_ref[acc.account_src_id.id],
                    'account_dest_id':acc_template_ref[acc.account_dest_id.id],
                    'position_id':fp.id,
                }))
        self._create_records_with_xmlid('account.fiscal.position.tax',tax_template_vals,company)
        self._create_records_with_xmlid('account.fiscal.position.account',account_template_vals,company)

        returnTrue


classAccountTaxTemplate(models.Model):
    _name='account.tax.template'
    _description='TemplatesforTaxes'
    _order='id'

    chart_template_id=fields.Many2one('account.chart.template',string='ChartTemplate',required=True)

    name=fields.Char(string='TaxName',required=True)
    type_tax_use=fields.Selection(TYPE_TAX_USE,string='TaxType',required=True,default="sale",
        help="Determineswherethetaxisselectable.Note:'None'meansataxcan'tbeusedbyitself,howeveritcanstillbeusedinagroup.")
    tax_scope=fields.Selection([('service','Service'),('consu','Consumable')],help="Restricttheuseoftaxestoatypeofproduct.")
    amount_type=fields.Selection(default='percent',string="TaxComputation",required=True,
        selection=[('group','GroupofTaxes'),('fixed','Fixed'),('percent','PercentageofPrice'),('division','PercentageofPriceTaxIncluded')])
    active=fields.Boolean(default=True,help="Setactivetofalsetohidethetaxwithoutremovingit.")
    children_tax_ids=fields.Many2many('account.tax.template','account_tax_template_filiation_rel','parent_tax','child_tax',string='ChildrenTaxes')
    sequence=fields.Integer(required=True,default=1,
        help="Thesequencefieldisusedtodefineorderinwhichthetaxlinesareapplied.")
    amount=fields.Float(required=True,digits=(16,4),default=0)
    description=fields.Char(string='DisplayonInvoices')
    price_include=fields.Boolean(string='IncludedinPrice',default=False,
        help="Checkthisifthepriceyouuseontheproductandinvoicesincludesthistax.")
    include_base_amount=fields.Boolean(string='AffectSubsequentTaxes',default=False,
        help="Ifset,taxeswhicharecomputedafterthisonewillbecomputedbasedonthepricetaxincluded.")
    analytic=fields.Boolean(string="AnalyticCost",help="Ifset,theamountcomputedbythistaxwillbeassignedtothesameanalyticaccountastheinvoiceline(ifany)")
    invoice_repartition_line_ids=fields.One2many(string="RepartitionforInvoices",comodel_name="account.tax.repartition.line.template",inverse_name="invoice_tax_id",copy=True,help="Repartitionwhenthetaxisusedonaninvoice")
    refund_repartition_line_ids=fields.One2many(string="RepartitionforRefundInvoices",comodel_name="account.tax.repartition.line.template",inverse_name="refund_tax_id",copy=True,help="Repartitionwhenthetaxisusedonarefund")
    tax_group_id=fields.Many2one('account.tax.group',string="TaxGroup")
    tax_exigibility=fields.Selection(
        [('on_invoice','BasedonInvoice'),
         ('on_payment','BasedonPayment'),
        ],string='TaxDue',default='on_invoice',
        help="BasedonInvoice:thetaxisdueassoonastheinvoiceisvalidated.\n"
        "BasedonPayment:thetaxisdueassoonasthepaymentoftheinvoiceisreceived.")
    cash_basis_transition_account_id=fields.Many2one(
        comodel_name='account.account.template',
        string="CashBasisTransitionAccount",
        domain=[('deprecated','=',False)],
        help="Accountusedtotransitionthetaxamountforcashbasistaxes.Itwillcontainthetaxamountaslongastheoriginalinvoicehasnotbeenreconciled;atreconciliation,thisamountcancelledonthisaccountandputontheregulartaxaccount.")

    _sql_constraints=[
        ('name_company_uniq','unique(name,type_tax_use,tax_scope,chart_template_id)','Taxnamesmustbeunique!'),
    ]

    @api.depends('name','description')
    defname_get(self):
        res=[]
        forrecordinself:
            name=record.descriptionandrecord.descriptionorrecord.name
            res.append((record.id,name))
        returnres

    def_get_tax_vals(self,company,tax_template_to_tax):
        """Thismethodgeneratesadictionaryofallthevaluesforthetaxthatwillbecreated.
        """
        #Computechildrentaxids
        children_ids=[]
        forchild_taxinself.children_tax_ids:
            iftax_template_to_tax.get(child_tax.id):
                children_ids.append(tax_template_to_tax[child_tax.id])
        self.ensure_one()
        val={
            'name':self.name,
            'type_tax_use':self.type_tax_use,
            'tax_scope':self.tax_scope,
            'amount_type':self.amount_type,
            'active':self.active,
            'company_id':company.id,
            'sequence':self.sequence,
            'amount':self.amount,
            'description':self.description,
            'price_include':self.price_include,
            'include_base_amount':self.include_base_amount,
            'analytic':self.analytic,
            'children_tax_ids':[(6,0,children_ids)],
            'tax_exigibility':self.tax_exigibility,
        }

        #Weaddrepartitionlinesiftherearesome,sothatiftherearenone,
        #default_getiscalledandcreatesthedefaultonesproperly.
        ifself.invoice_repartition_line_ids:
            val['invoice_repartition_line_ids']=self.invoice_repartition_line_ids.get_repartition_line_create_vals(company)
        ifself.refund_repartition_line_ids:
            val['refund_repartition_line_ids']=self.refund_repartition_line_ids.get_repartition_line_create_vals(company)

        ifself.tax_group_id:
            val['tax_group_id']=self.tax_group_id.id
        returnval

    def_get_tax_vals_complete(self,company,tax_template_to_tax):
        """
        Returnsadictofvaluestobeusedtocreatethetaxcorrespondingtothetemplate,assumingthe
        account.accountobjectswerealreadycreated.
        Itdiffersfromfunction_get_tax_valsbecausehere,wereplacethereferencestoaccount.templatebytheir
        correspondingaccount.accountids('cash_basis_transition_account_id'and'account_id'intheinvoiceand
        refundrepartitionlines)
        """
        vals=self._get_tax_vals(company,tax_template_to_tax)

        ifself.cash_basis_transition_account_id.code:
            cash_basis_account_id=self.env['account.account'].search([
                ('code','=like',self.cash_basis_transition_account_id.code+'%'),
                ('company_id','=',company.id)
            ],limit=1)
            ifcash_basis_account_id:
                vals.update({"cash_basis_transition_account_id":cash_basis_account_id.id})

        vals.update({
            "invoice_repartition_line_ids":self.invoice_repartition_line_ids._get_repartition_line_create_vals_complete(company),
            "refund_repartition_line_ids":self.refund_repartition_line_ids._get_repartition_line_create_vals_complete(company),
        })
        returnvals

    def_generate_tax(self,company,accounts_exist=False,existing_template_to_tax=None):
        """Thismethodgeneratetaxesfromtemplates.

            :paramcompany:thecompanyforwhichthetaxesshouldbecreatedfromtemplatesinself
            :account_exist:whetheraccountshavealreadybeencreated
            :existing_template_to_tax:mappingofalreadyexistingtemplatestotaxes[(template,tax),...]
            :returns:{
                'tax_template_to_tax':mappingbetweentaxtemplateandthenewlygeneratedtaxescorresponding,
                'account_dict':dictionarycontainingato-dolistwithalltheaccountstoassignonnewtaxes
            }
        """
        #default_company_idisneededincontexttoallowcreationofdefault
        #repartitionlinesontaxes
        ChartTemplate=self.env['account.chart.template'].with_context(default_company_id=company.id)
        todo_dict={'account.tax':{},'account.tax.repartition.line':{}}
        ifnotexisting_template_to_tax:
            existing_template_to_tax=[]
        tax_template_to_tax={template.id:tax.idfor(template,tax)inexisting_template_to_tax}

        templates_todo=list(self)
        whiletemplates_todo:
            templates=templates_todo
            templates_todo=[]

            #createtaxesinbatch
            tax_template_vals=[]
            fortemplateintemplates:
                ifall(child.idintax_template_to_taxforchildintemplate.children_tax_ids):
                    ifaccounts_exist:
                        vals=template._get_tax_vals_complete(company,tax_template_to_tax)
                    else:
                        vals=template._get_tax_vals(company,tax_template_to_tax)
                    tax_template_vals.append((template,vals))
                else:
                    #deferthecreationofthistaxtothenextbatch
                    templates_todo.append(template)
            taxes=ChartTemplate._create_records_with_xmlid('account.tax',tax_template_vals,company)

            #fillintax_template_to_taxandtodo_dict
            fortax,(template,vals)inzip(taxes,tax_template_vals):
                tax_template_to_tax[template.id]=tax.id
                #Sincetheaccountshavenotbeencreatedyet,wehavetowaitbeforefillingthesefields
                todo_dict['account.tax'][tax.id]={
                    'cash_basis_transition_account_id':template.cash_basis_transition_account_id.id,
                }

                forexisting_template,existing_taxinexisting_template_to_tax:
                    iftemplateinexisting_template.children_tax_idsandtaxnotinexisting_tax.children_tax_ids:
                        existing_tax.write({'children_tax_ids':[(4,tax.id,False)]})

                #Wealsohavetodelaytheassignationofaccountstorepartitionlines
                #Thebelowcodeassignstheaccount_idtotherepartitionlinesaccording
                #tothecorrespondingrepartitionlineinthetemplate,basedontheorder.
                #Aswejustcreatedtherepartitionlines,tax.invoice_repartition_line_idsisnotwellsorted.
                #Butwecanforcethesortbycallingsort()
                all_tax_rep_lines=tax.invoice_repartition_line_ids.sorted()+tax.refund_repartition_line_ids.sorted()
                all_template_rep_lines=template.invoice_repartition_line_ids+template.refund_repartition_line_ids
                foriinrange(0,len(all_template_rep_lines)):
                    #Weassumetemplateandtaxrepartitionlinesareinthesameorder
                    template_account=all_template_rep_lines[i].account_id
                    iftemplate_account:
                        todo_dict['account.tax.repartition.line'][all_tax_rep_lines[i].id]={
                            'account_id':template_account.id,
                        }

        ifany(template.tax_exigibility=='on_payment'fortemplateinself):
            #WhenaCoAisbeinginstalledautomaticallyandifitiscreatingaccounttax(es)whosefield`UseCashBasis`(tax_exigibility)issettoTruebydefault
            #(exampleofsuchCoA'sarel10n_frandl10n_mx)theninthe`AccountingSettings`theoption`CashBasis`shouldbecheckedbydefault.
            company.tax_exigibility=True

        return{
            'tax_template_to_tax':tax_template_to_tax,
            'account_dict':todo_dict
        }

#TaxRepartitionLineTemplate


classAccountTaxRepartitionLineTemplate(models.Model):
    _name="account.tax.repartition.line.template"
    _description="TaxRepartitionLineTemplate"

    factor_percent=fields.Float(string="%",required=True,help="Factortoapplyontheaccountmovelinesgeneratedfromthisdistributionline,inpercents")
    repartition_type=fields.Selection(string="BasedOn",selection=[('base','Base'),('tax','oftax')],required=True,default='tax',help="Baseonwhichthefactorwillbeapplied.")
    account_id=fields.Many2one(string="Account",comodel_name='account.account.template',help="Accountonwhichtopostthetaxamount")
    invoice_tax_id=fields.Many2one(comodel_name='account.tax.template',help="Thetaxsettoapplythisdistributiononinvoices.Mutuallyexclusivewithrefund_tax_id")
    refund_tax_id=fields.Many2one(comodel_name='account.tax.template',help="Thetaxsettoapplythisdistributiononrefundinvoices.Mutuallyexclusivewithinvoice_tax_id")
    tag_ids=fields.Many2many(string="FinancialTags",relation='account_tax_repartition_financial_tags',comodel_name='account.account.tag',copy=True,help="Additionaltagsthatwillbeassignedbythisrepartitionlineforuseinfinancialreports")
    use_in_tax_closing=fields.Boolean(string="TaxClosingEntry")

    #Theselasttwofieldsarehelpersusedtoeasethedeclarationofaccount.account.tagobjectsinXML.
    #Theyaredirectlylinkedtoaccount.tax.report.lineobjects,whichcreatecorresponding+and-tags
    #atcreation.Thisway,weavoiddeclaring+and-separatelyeverytime.
    plus_report_line_ids=fields.Many2many(string="PlusTaxReportLines",relation='account_tax_repartition_plus_report_line',comodel_name='account.tax.report.line',copy=True,help="Taxreportlineswhose'+'tagwillbeassignedtomovelinesbythisrepartitionline")
    minus_report_line_ids=fields.Many2many(string="MinusReportLines",relation='account_tax_repartition_minus_report_line',comodel_name='account.tax.report.line',copy=True,help="Taxreportlineswhose'-'tagwillbeassignedtomovelinesbythisrepartitionline")

    @api.model
    defcreate(self,vals):
        ifvals.get('plus_report_line_ids'):
            vals['plus_report_line_ids']=self._convert_tag_syntax_to_orm(vals['plus_report_line_ids'])

        ifvals.get('minus_report_line_ids'):
            vals['minus_report_line_ids']=self._convert_tag_syntax_to_orm(vals['minus_report_line_ids'])

        ifvals.get('tag_ids'):
            vals['tag_ids']=self._convert_tag_syntax_to_orm(vals['tag_ids'])

        ifvals.get('use_in_tax_closing')isNone:
            ifnotvals.get('account_id'):
                vals['use_in_tax_closing']=False
            else:
                internal_group=self.env['account.account.template'].browse(vals.get('account_id')).user_type_id.internal_group
                vals['use_in_tax_closing']=not(internal_group=='income'orinternal_group=='expense')

        returnsuper(AccountTaxRepartitionLineTemplate,self).create(vals)

    @api.model
    def_convert_tag_syntax_to_orm(self,tags_list):
        """Repartitionlinesgivethepossibilitytodirectlygive
        alistofidstocreatefortagsinsteadofalistofORMcommands.

        Thisfunctionchecksthattags_listusesthissyntacticsugarandreturns
        anORM-compliantversionofitifitdoes.
        """
        iftags_listandall(isinstance(elem,int)forelemintags_list):
            return[(6,False,tags_list)]
        returntags_list

    @api.constrains('invoice_tax_id','refund_tax_id')
    defvalidate_tax_template_link(self):
        forrecordinself:
            ifrecord.invoice_tax_idandrecord.refund_tax_id:
                raiseValidationError(_("Taxdistributionlinetemplatesshouldapplytoeitherinvoicesorrefunds,notbothatthesametime.invoice_tax_idandrefund_tax_idshouldnotbesettogether."))

    @api.constrains('plus_report_line_ids','minus_report_line_ids')
    defvalidate_tags(self):
        all_tax_rep_lines=self.mapped('plus_report_line_ids')+self.mapped('minus_report_line_ids')
        lines_without_tag=all_tax_rep_lines.filtered(lambdax:notx.tag_name)
        iflines_without_tag:
            raiseValidationError(_("Thefollowingtaxreportlinesareusedinsometaxdistributiontemplatethoughtheydon'tgenerateanytag:%s.Thisprobablymeansyouforgottosetatag_nameontheselines.",str(lines_without_tag.mapped('name'))))

    defget_repartition_line_create_vals(self,company):
        rslt=[(5,0,0)]
        forrecordinself:
            tags_to_add=record._get_tags_to_add()

            rslt.append((0,0,{
                'factor_percent':record.factor_percent,
                'repartition_type':record.repartition_type,
                'tag_ids':[(6,0,tags_to_add.ids)],
                'company_id':company.id,
                'use_in_tax_closing':record.use_in_tax_closing
            }))
        returnrslt

    def_get_repartition_line_create_vals_complete(self,company):
        """
        Thisfunctionreturnsalistofvaluestocreatetherepartitionlinesofataxbasedon
        oneorseveralaccount.tax.repartition.line.template.Itmimicksthefunctionget_repartition_line_create_vals
        butaddsthemissingfieldaccount_id(account.account)

        Returnsalistof(0,0,x)ORMcommandstocreatetherepartitionlinesstartingwitha(5,0,0)
        commandtocleartherepartition.
        """
        rslt=self.get_repartition_line_create_vals(company)
        foridx,template_lineinzip(range(1,len(rslt)),self): #ignorefirstORMcommand((5,0,0))
            account_id=False
            iftemplate_line.account_id:
                #takethefirstaccount.accountwhichcodebeginswiththecorrectcode
                account_id=self.env['account.account'].search([
                    ('code','=like',template_line.account_id.code+'%'),
                    ('company_id','=',company.id)
                ],limit=1).id
                ifnotaccount_id:
                    _logger.warning("Theaccountwithcode'%s'wasnotfoundbutissupposedtobelinkedtoatax",
                                    template_line.account_id.code)
            rslt[idx][2].update({
                "account_id":account_id,
            })
        returnrslt

    def_get_tags_to_add(self):
        self.ensure_one()
        tags_to_add=self.env["account.account.tag"]
        tags_to_add+=self.plus_report_line_ids.mapped("tag_ids").filtered(lambdax:notx.tax_negate)
        tags_to_add+=self.minus_report_line_ids.mapped("tag_ids").filtered(lambdax:x.tax_negate)
        tags_to_add+=self.tag_ids
        returntags_to_add

#FiscalPositionTemplates

classAccountFiscalPositionTemplate(models.Model):
    _name='account.fiscal.position.template'
    _description='TemplateforFiscalPosition'

    sequence=fields.Integer()
    name=fields.Char(string='FiscalPositionTemplate',required=True)
    chart_template_id=fields.Many2one('account.chart.template',string='ChartTemplate',required=True)
    account_ids=fields.One2many('account.fiscal.position.account.template','position_id',string='AccountMapping')
    tax_ids=fields.One2many('account.fiscal.position.tax.template','position_id',string='TaxMapping')
    note=fields.Text(string='Notes')
    auto_apply=fields.Boolean(string='DetectAutomatically',help="Applyautomaticallythisfiscalposition.")
    vat_required=fields.Boolean(string='VATrequired',help="ApplyonlyifpartnerhasaVATnumber.")
    country_id=fields.Many2one('res.country',string='Country',
        help="Applyonlyifdeliverycountrymatches.")
    country_group_id=fields.Many2one('res.country.group',string='CountryGroup',
        help="Applyonlyifdeliverycountrymatchesthegroup.")
    state_ids=fields.Many2many('res.country.state',string='FederalStates')
    zip_from=fields.Char(string='ZipRangeFrom')
    zip_to=fields.Char(string='ZipRangeTo')


classAccountFiscalPositionTaxTemplate(models.Model):
    _name='account.fiscal.position.tax.template'
    _description='TaxMappingTemplateofFiscalPosition'
    _rec_name='position_id'

    position_id=fields.Many2one('account.fiscal.position.template',string='FiscalPosition',required=True,ondelete='cascade')
    tax_src_id=fields.Many2one('account.tax.template',string='TaxSource',required=True)
    tax_dest_id=fields.Many2one('account.tax.template',string='ReplacementTax')


classAccountFiscalPositionAccountTemplate(models.Model):
    _name='account.fiscal.position.account.template'
    _description='AccountsMappingTemplateofFiscalPosition'
    _rec_name='position_id'

    position_id=fields.Many2one('account.fiscal.position.template',string='FiscalMapping',required=True,ondelete='cascade')
    account_src_id=fields.Many2one('account.account.template',string='AccountSource',required=True)
    account_dest_id=fields.Many2one('account.account.template',string='AccountDestination',required=True)


classAccountReconcileModelTemplate(models.Model):
    _name="account.reconcile.model.template"
    _description='ReconcileModelTemplate'

    #Basefields.
    chart_template_id=fields.Many2one('account.chart.template',string='ChartTemplate',required=True)
    name=fields.Char(string='ButtonLabel',required=True)
    sequence=fields.Integer(required=True,default=10)

    rule_type=fields.Selection(selection=[
        ('writeoff_button','Manuallycreateawrite-offonclickedbutton'),
        ('writeoff_suggestion','Suggestawrite-off'),
        ('invoice_matching','Matchexistinginvoices/bills')
    ],string='Type',default='writeoff_button',required=True)
    auto_reconcile=fields.Boolean(string='Auto-validate',
        help='Validatethestatementlineautomatically(reconciliationbasedonyourrule).')
    to_check=fields.Boolean(string='ToCheck',default=False,help='Thismatchingruleisusedwhentheuserisnotcertainofalltheinformationofthecounterpart.')
    matching_order=fields.Selection(
        selection=[
            ('old_first','Oldestfirst'),
            ('new_first','Newestfirst'),
        ]
    )

    #=====Conditions=====
    match_text_location_label=fields.Boolean(
        default=True,
        help="SearchintheStatement'sLabeltofindtheInvoice/Payment'sreference",
    )
    match_text_location_note=fields.Boolean(
        default=False,
        help="SearchintheStatement'sNotetofindtheInvoice/Payment'sreference",
    )
    match_text_location_reference=fields.Boolean(
        default=False,
        help="SearchintheStatement'sReferencetofindtheInvoice/Payment'sreference",
    )
    match_journal_ids=fields.Many2many('account.journal',string='Journals',
        domain="[('type','in',('bank','cash'))]",
        help='Thereconciliationmodelwillonlybeavailablefromtheselectedjournals.')
    match_nature=fields.Selection(selection=[
        ('amount_received','AmountReceived'),
        ('amount_paid','AmountPaid'),
        ('both','AmountPaid/Received')
    ],string='AmountNature',required=True,default='both',
        help='''Thereconciliationmodelwillonlybeappliedtotheselectedtransactiontype:
        *AmountReceived:Onlyappliedwhenreceivinganamount.
        *AmountPaid:Onlyappliedwhenpayinganamount.
        *AmountPaid/Received:Appliedinbothcases.''')
    match_amount=fields.Selection(selection=[
        ('lower','IsLowerThan'),
        ('greater','IsGreaterThan'),
        ('between','IsBetween'),
    ],string='Amount',
        help='Thereconciliationmodelwillonlybeappliedwhentheamountbeinglowerthan,greaterthanorbetweenspecifiedamount(s).')
    match_amount_min=fields.Float(string='AmountMinParameter')
    match_amount_max=fields.Float(string='AmountMaxParameter')
    match_label=fields.Selection(selection=[
        ('contains','Contains'),
        ('not_contains','NotContains'),
        ('match_regex','MatchRegex'),
    ],string='Label',help='''Thereconciliationmodelwillonlybeappliedwhenthelabel:
        *Contains:Thepropositionlabelmustcontainsthisstring(caseinsensitive).
        *NotContains:Negationof"Contains".
        *MatchRegex:Defineyourownregularexpression.''')
    match_label_param=fields.Char(string='LabelParameter')
    match_note=fields.Selection(selection=[
        ('contains','Contains'),
        ('not_contains','NotContains'),
        ('match_regex','MatchRegex'),
    ],string='Note',help='''Thereconciliationmodelwillonlybeappliedwhenthenote:
        *Contains:Thepropositionnotemustcontainsthisstring(caseinsensitive).
        *NotContains:Negationof"Contains".
        *MatchRegex:Defineyourownregularexpression.''')
    match_note_param=fields.Char(string='NoteParameter')
    match_transaction_type=fields.Selection(selection=[
        ('contains','Contains'),
        ('not_contains','NotContains'),
        ('match_regex','MatchRegex'),
    ],string='TransactionType',help='''Thereconciliationmodelwillonlybeappliedwhenthetransactiontype:
        *Contains:Thepropositiontransactiontypemustcontainsthisstring(caseinsensitive).
        *NotContains:Negationof"Contains".
        *MatchRegex:Defineyourownregularexpression.''')
    match_transaction_type_param=fields.Char(string='TransactionTypeParameter')
    match_same_currency=fields.Boolean(string='SameCurrencyMatching',default=True,
        help='Restricttopropositionshavingthesamecurrencyasthestatementline.')
    match_total_amount=fields.Boolean(string='AmountMatching',default=True,
        help='Thesumoftotalresidualamountpropositionsmatchesthestatementlineamount.')
    match_total_amount_param=fields.Float(string='AmountMatching%',default=100,
        help='Thesumoftotalresidualamountpropositionsmatchesthestatementlineamountunderthispercentage.')
    match_partner=fields.Boolean(string='PartnerIsSet',
        help='Thereconciliationmodelwillonlybeappliedwhenacustomer/vendorisset.')
    match_partner_ids=fields.Many2many('res.partner',string='RestrictPartnersto',
        help='Thereconciliationmodelwillonlybeappliedtotheselectedcustomers/vendors.')
    match_partner_category_ids=fields.Many2many('res.partner.category',string='RestrictPartnerCategoriesto',
        help='Thereconciliationmodelwillonlybeappliedtotheselectedcustomer/vendorcategories.')

    line_ids=fields.One2many('account.reconcile.model.line.template','model_id')
    decimal_separator=fields.Char(help="Everycharacterthatisnoradigitnorthisseparatorwillberemovedfromthematchingstring")


classAccountReconcileModelLineTemplate(models.Model):
    _name="account.reconcile.model.line.template"
    _description='ReconcileModelLineTemplate'

    model_id=fields.Many2one('account.reconcile.model.template')
    sequence=fields.Integer(required=True,default=10)
    account_id=fields.Many2one('account.account.template',string='Account',ondelete='cascade',domain=[('deprecated','=',False)])
    label=fields.Char(string='JournalItemLabel')
    amount_type=fields.Selection([
        ('fixed','Fixed'),
        ('percentage','Percentageofbalance'),
        ('regex','Fromlabel'),
    ],required=True,default='percentage')
    amount_string=fields.Char(string="Amount")
    force_tax_included=fields.Boolean(string='TaxIncludedinPrice',help='Forcethetaxtobemanagedasapriceincludedtax.')
    tax_ids=fields.Many2many('account.tax.template',string='Taxes',ondelete='restrict')
