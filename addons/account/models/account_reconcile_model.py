#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_
fromflectra.toolsimportfloat_compare,float_is_zero
fromflectra.osv.expressionimportget_unaccent_wrapper
fromflectra.exceptionsimportUserError,ValidationError
importre
frommathimportcopysign
importitertools
fromcollectionsimportdefaultdict
fromdateutil.relativedeltaimportrelativedelta

classAccountReconcileModelPartnerMapping(models.Model):
    _name='account.reconcile.model.partner.mapping'
    _description='Partnermappingforreconciliationmodels'

    model_id=fields.Many2one(comodel_name='account.reconcile.model',readonly=True,required=True,ondelete='cascade')
    partner_id=fields.Many2one(comodel_name='res.partner',string="Partner",required=True,ondelete='cascade')
    payment_ref_regex=fields.Char(string="FindTextinLabel")
    narration_regex=fields.Char(string="FindTextinNotes")

    @api.constrains('narration_regex','payment_ref_regex')
    defvalidate_regex(self):
        forrecordinself:
            ifnot(record.narration_regexorrecord.payment_ref_regex):
                raiseValidationError(_("Pleasesetatleastoneofthematchtextstocreateapartnermapping."))
            try:
                ifrecord.payment_ref_regex:
                    current_regex=record.payment_ref_regex
                    re.compile(record.payment_ref_regex)
                ifrecord.narration_regex:
                    current_regex=record.narration_regex
                    re.compile(record.narration_regex)
            exceptre.error:
                raiseValidationError(_("Thefollowingregularexpressionisinvalidtocreateapartnermapping:%s")%current_regex)

classAccountReconcileModelLine(models.Model):
    _name='account.reconcile.model.line'
    _description='Rulesforthereconciliationmodel'
    _order='sequence,id'
    _check_company_auto=True

    model_id=fields.Many2one('account.reconcile.model',readonly=True,ondelete='cascade')
    match_total_amount=fields.Boolean(related='model_id.match_total_amount')
    match_total_amount_param=fields.Float(related='model_id.match_total_amount_param')
    rule_type=fields.Selection(related='model_id.rule_type')
    company_id=fields.Many2one(related='model_id.company_id',store=True,default=lambdaself:self.env.company)
    sequence=fields.Integer(required=True,default=10)
    account_id=fields.Many2one('account.account',string='Account',ondelete='cascade',
        domain="[('deprecated','=',False),('company_id','=',company_id),('is_off_balance','=',False)]",
        required=True,check_company=True)
    journal_id=fields.Many2one('account.journal',string='Journal',ondelete='cascade',
        domain="[('type','=','general'),('company_id','=',company_id)]",
        help="Thisfieldisignoredinabankstatementreconciliation.",check_company=True)
    label=fields.Char(string='JournalItemLabel')
    amount_type=fields.Selection([
        ('fixed','Fixed'),
        ('percentage','Percentageofbalance'),
        ('regex','Fromlabel'),
    ],required=True,default='percentage')
    show_force_tax_included=fields.Boolean(compute='_compute_show_force_tax_included',help='Technicalfieldusedtoshowtheforcetaxincludedbutton')
    force_tax_included=fields.Boolean(string='TaxIncludedinPrice',help='Forcethetaxtobemanagedasapriceincludedtax.')
    amount=fields.Float(string="FloatAmount",compute='_compute_float_amount',store=True,help="Technicalshortcuttoparsetheamounttoafloat")
    amount_string=fields.Char(string="Amount",default='100',required=True,help="""Valuefortheamountofthewriteoffline
    *Percentage:Percentageofthebalance,between0and100.
    *Fixed:Thefixedvalueofthewriteoff.Theamountwillcountasadebitifitisnegative,asacreditifitispositive.
    *FromLabel:Thereisnoneedforregexdelimiter,onlytheregexisneeded.Forinstanceifyouwanttoextracttheamountfrom\nR:967293810/07AX9415126318T:5L:NABRT:3358,07C:\nYoucouldenter\nBRT:([\d,]+)""")
    tax_ids=fields.Many2many('account.tax',string='Taxes',ondelete='restrict',check_company=True)
    analytic_account_id=fields.Many2one('account.analytic.account',string='AnalyticAccount',ondelete='setnull',check_company=True)
    analytic_tag_ids=fields.Many2many('account.analytic.tag',string='AnalyticTags',check_company=True,
                                        relation='account_reconcile_model_analytic_tag_rel')

    @api.onchange('tax_ids')
    def_onchange_tax_ids(self):
        #Multipletaxeswithforce_tax_includedresultsinwrongcomputation,sowe
        #onlyallowtosettheforce_tax_includedfieldifwehaveonetaxselected
        iflen(self.tax_ids)!=1:
            self.force_tax_included=False

    @api.depends('tax_ids')
    def_compute_show_force_tax_included(self):
        forrecordinself:
            record.show_force_tax_included=Falseiflen(record.tax_ids)!=1elseTrue

    @api.onchange('amount_type')
    def_onchange_amount_type(self):
        self.amount_string=''
        ifself.amount_type=='percentage':
            self.amount_string='100'
        elifself.amount_type=='regex':
            self.amount_string='([\d,]+)'

    @api.depends('amount_string')
    def_compute_float_amount(self):
        forrecordinself:
            try:
                record.amount=float(record.amount_string)
            exceptValueError:
                record.amount=0

    @api.constrains('amount_string')
    def_validate_amount(self):
        forrecordinself:
            ifrecord.amount_type=='fixed'andrecord.amount==0:
                raiseUserError(_('Theamountisnotanumber'))
            ifrecord.amount_type=='percentage'andnot0<record.amount:
                raiseUserError(_('Theamountisnotapercentage'))
            ifrecord.amount_type=='regex':
                try:
                    re.compile(record.amount_string)
                exceptre.error:
                    raiseUserError(_('Theregexisnotvalid'))


classAccountReconcileModel(models.Model):
    _name='account.reconcile.model'
    _description='Presettocreatejournalentriesduringainvoicesandpaymentsmatching'
    _order='sequence,id'
    _check_company_auto=True

    #Basefields.
    active=fields.Boolean(default=True)
    name=fields.Char(string='Name',required=True)
    sequence=fields.Integer(required=True,default=10)
    company_id=fields.Many2one(
        comodel_name='res.company',
        string='Company',required=True,readonly=True,
        default=lambdaself:self.env.company)

    rule_type=fields.Selection(selection=[
        ('writeoff_button','Manuallycreateawrite-offonclickedbutton'),
        ('writeoff_suggestion','Suggestcounterpartvalues'),
        ('invoice_matching','Matchexistinginvoices/bills'),
    ],string='Type',default='writeoff_button',required=True)
    auto_reconcile=fields.Boolean(string='Auto-validate',
        help='Validatethestatementlineautomatically(reconciliationbasedonyourrule).')
    to_check=fields.Boolean(string='ToCheck',default=False,help='Thismatchingruleisusedwhentheuserisnotcertainofalltheinformationofthecounterpart.')
    matching_order=fields.Selection(
        selection=[
            ('old_first','Oldestfirst'),
            ('new_first','Newestfirst'),
        ],
        required=True,
        default='old_first',
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
        domain="[('type','in',('bank','cash')),('company_id','=',company_id)]",
        check_company=True,
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

    line_ids=fields.One2many('account.reconcile.model.line','model_id',copy=True)
    partner_mapping_line_ids=fields.One2many(string="PartnerMappingLines",
                                               comodel_name='account.reconcile.model.partner.mapping',
                                               inverse_name='model_id',
                                               help="Themappingusesregularexpressions.\n"
                                                    "-ToMatchthetextatthebeginningoftheline(inlabelornotes),simplyfillinyourtext.\n"
                                                    "-ToMatchthetextanywhere(inlabelornotes),putyourtextbetween.*\n"
                                                    " e.g:.*N°48748abc123.*")

    past_months_limit=fields.Integer(string="PastMonthsLimit",default=18,help="Numberofmonthsinthepasttoconsiderentriesfromwhenapplyingthismodel.")

    decimal_separator=fields.Char(default=lambdaself:self.env['res.lang']._lang_get(self.env.user.lang).decimal_point,help="Everycharacterthatisnoradigitnorthisseparatorwillberemovedfromthematchingstring")
    show_decimal_separator=fields.Boolean(compute='_compute_show_decimal_separator',help="Technicalfieldtodecideifweshouldshowthedecimalseparatorfortheregexmatchingfield.")
    number_entries=fields.Integer(string='Numberofentriesrelatedtothismodel',compute='_compute_number_entries')

    defaction_reconcile_stat(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        self._cr.execute('''
            SELECTARRAY_AGG(DISTINCTmove_id)
            FROMaccount_move_line
            WHEREreconcile_model_id=%s
        ''',[self.id])
        action.update({
            'context':{},
            'domain':[('id','in',self._cr.fetchone()[0])],
            'help':"""<pclass="o_view_nocontent_empty_folder">{}</p>""".format(_('Thisreconciliationmodelhascreatednoentrysofar')),
        })
        returnaction

    def_compute_number_entries(self):
        data=self.env['account.move.line'].read_group([('reconcile_model_id','in',self.ids)],['reconcile_model_id'],'reconcile_model_id')
        mapped_data=dict([(d['reconcile_model_id'][0],d['reconcile_model_id_count'])fordindata])
        formodelinself:
            model.number_entries=mapped_data.get(model.id,0)

    @api.depends('line_ids.amount_type')
    def_compute_show_decimal_separator(self):
        forrecordinself:
            record.show_decimal_separator=any(l.amount_type=='regex'forlinrecord.line_ids)

    @api.onchange('match_total_amount_param')
    def_onchange_match_total_amount_param(self):
        ifself.match_total_amount_param<0orself.match_total_amount_param>100:
            self.match_total_amount_param=min(max(0,self.match_total_amount_param),100)

    ####################################################
    #RECONCILIATIONPROCESS
    ####################################################

    def_get_taxes_move_lines_dict(self,tax,base_line_dict):
        '''Getmove.linesdict(tobepassedtothecreate())correspondingtoatax.
        :paramtax:            Anaccount.taxrecord.
        :parambase_line_dict: Adictrepresentingthemove.linecontainingthebaseamount.
        :return:Alistofdictrepresentingmove.linestobecreatedcorrespondingtothetax.
        '''
        self.ensure_one()
        balance=base_line_dict['balance']
        tax_type=tax.type_tax_use
        is_refund=(tax_type=='sale'andbalance>0)or(tax_type=='purchase'andbalance<0)

        res=tax.compute_all(balance,is_refund=is_refund)

        if(tax_type=='sale'andnotis_refund)or(tax_type=='purchase'andis_refund):
            base_tags=self.env['account.account.tag'].browse(res['base_tags'])
            res['base_tags']=self.env['account.move.line']._revert_signed_tags(base_tags).ids

            fortax_resultinres['taxes']:
                tax_tags=self.env['account.account.tag'].browse(tax_result['tag_ids'])
                tax_result['tag_ids']=self.env['account.move.line']._revert_signed_tags(tax_tags).ids

        new_aml_dicts=[]
        fortax_resinres['taxes']:
            ifself.company_id.currency_id.is_zero(tax_res['amount']):
                continue
            tax=self.env['account.tax'].browse(tax_res['id'])
            balance=tax_res['amount']
            name=''.join([xforxin[base_line_dict.get('name',''),tax_res['name']]ifx])
            new_aml_dicts.append({
                'account_id':tax_res['account_id']orbase_line_dict['account_id'],
                'journal_id':base_line_dict.get('journal_id',False),
                'name':name,
                'partner_id':base_line_dict.get('partner_id'),
                'balance':balance,
                'debit':balance>0andbalanceor0,
                'credit':balance<0and-balanceor0,
                'analytic_account_id':tax.analyticandbase_line_dict['analytic_account_id'],
                'analytic_tag_ids':tax.analyticandbase_line_dict['analytic_tag_ids'],
                'tax_exigible':tax_res['tax_exigibility'],
                'tax_repartition_line_id':tax_res['tax_repartition_line_id'],
                'tax_ids':[(6,0,tax_res['tax_ids'])],
                'tax_tag_ids':[(6,0,tax_res['tag_ids'])],
                'currency_id':False,
                'reconcile_model_id':self.id,
            })

            #Handlepriceincludedtaxes.
            base_balance=tax_res['base']
            base_line_dict.update({
                'balance':base_balance,
                'debit':base_balance>0andbase_balanceor0,
                'credit':base_balance<0and-base_balanceor0,
            })

        base_line_dict['tax_tag_ids']=[(6,0,res['base_tags'])]
        returnnew_aml_dicts

    def_get_write_off_move_lines_dict(self,st_line,residual_balance):
        '''Getmove.linesdict(tobepassedtothecreate())correspondingtothereconciliationmodel'swrite-offlines.
        :paramst_line:            Anaccount.bank.statement.linerecord.(possiblyempty,ifperformingmanualreconciliation)
        :paramresidual_balance:   Theresidualbalanceofthestatementline.
        :return:Alistofdictrepresentingmove.linestobecreatedcorrespondingtothewrite-offlines.
        '''
        self.ensure_one()

        ifself.rule_type=='invoice_matching'and(notself.match_total_amountor(self.match_total_amount_param==100)):
            return[]

        lines_vals_list=[]

        forlineinself.line_ids:
            currency_id=st_line.currency_idorst_line.journal_id.currency_idorself.company_id.currency_id
            ifnotline.account_idorcurrency_id.is_zero(residual_balance):
                return[]

            ifline.amount_type=='percentage':
                balance=residual_balance*(line.amount/100.0)
            elifline.amount_type=="regex":
                match=re.search(line.amount_string,st_line.payment_ref)
                ifmatch:
                    sign=1ifresidual_balance>0.0else-1
                    try:
                        extracted_match_group=re.sub(r'[^\d'+self.decimal_separator+']','',match.group(1))
                        extracted_balance=float(extracted_match_group.replace(self.decimal_separator,'.'))
                        balance=copysign(extracted_balance*sign,residual_balance)
                    exceptValueError:
                        balance=0
                else:
                    balance=0
            else:
                balance=line.amount*(1ifresidual_balance>0.0else-1)

            writeoff_line={
                'name':line.labelorst_line.payment_ref,
                'balance':balance,
                'debit':balance>0andbalanceor0,
                'credit':balance<0and-balanceor0,
                'account_id':line.account_id.id,
                'currency_id':False,
                'analytic_account_id':line.analytic_account_id.id,
                'analytic_tag_ids':[(6,0,line.analytic_tag_ids.ids)],
                'reconcile_model_id':self.id,
                'journal_id':line.journal_id.id,
                'tax_ids':[],
            }
            lines_vals_list.append(writeoff_line)

            residual_balance-=balance

            ifline.tax_ids:
                writeoff_line['tax_ids']+=[(6,None,line.tax_ids.ids)]
                tax=line.tax_ids
                #Multipletaxeswithforce_tax_includedresultsinwrongcomputation,sowe
                #onlyallowtosettheforce_tax_includedfieldifwehaveonetaxselected
                ifline.force_tax_included:
                    tax=tax[0].with_context(force_price_include=True)
                tax_vals_list=self._get_taxes_move_lines_dict(tax,writeoff_line)
                lines_vals_list+=tax_vals_list
                ifnotline.force_tax_included:
                    fortax_lineintax_vals_list:
                        residual_balance-=tax_line['balance']

        returnlines_vals_list

    def_prepare_reconciliation(self,st_line,aml_ids=[],partner=None):
        '''Preparethereconciliationofthestatementlinewithsomecounterpartlinebut
        alsowithsomeauto-generatedwrite-offlines.

        Thecomplexityofthismethodcomesfromthefactthereconciliationwillbesoftmeaning
        itwillbedoneonlyifthereconciliationwillnottriggeranerror.
        Forexample,thereconciliationwillbeskippedifweneedtocreateanopenbalancebutwe
        don'thaveapartnertogetthereceivable/payableaccount.

        Thismethodworksintwomajorsteps.First,simulatethereconciliationoftheaccount.move.line.
        Then,addsomewrite-offlinesdependingtherule'sfields.

        :paramst_line:Anaccount.bank.statement.linerecord.
        :paramaml_ids:Theidsofsomeaccount.move.linetoreconcile.
        :parampartner:Anoptionalres.partnerrecord.Ifnotspecified,fallbackonthestatementline'spartner.
        :return:Alistofdictionarytobepassedtotheaccount.bank.statement.line's'reconcile'method.
        '''
        self.ensure_one()
        journal=st_line.journal_id
        company_currency=journal.company_id.currency_id
        foreign_currency=st_line.foreign_currency_idorjournal.currency_idorcompany_currency

        liquidity_lines,suspense_lines,other_lines=st_line._seek_for_lines()

        ifst_line.to_check:
            st_line_residual=-liquidity_lines.balance
            st_line_residual_currency=st_line._prepare_move_line_default_vals()[1]['amount_currency']
        elifsuspense_lines.account_id.reconcile:
            st_line_residual=sum(suspense_lines.mapped('amount_residual'))
            st_line_residual_currency=sum(suspense_lines.mapped('amount_residual_currency'))
        else:
            st_line_residual=sum(suspense_lines.mapped('balance'))
            st_line_residual_currency=sum(suspense_lines.mapped('amount_currency'))

        has_full_write_off=any(rec_mod_line.amount==100.0forrec_mod_lineinself.line_ids)

        lines_vals_list=[]
        amls=self.env['account.move.line'].browse(aml_ids)
        st_line_residual_before=st_line_residual
        aml_total_residual=0
        foramlinamls:
            aml_total_residual+=aml.amount_residual

            ifaml.balance*st_line_residual>0:
                #Meaningtheyhavethesamesigns,sotheycan'tbereconciledtogether
                assigned_balance=-aml.amount_residual
                assigned_amount_currency=-aml.amount_residual_currency
            elifhas_full_write_off:
                assigned_balance=-aml.amount_residual
                assigned_amount_currency=-aml.amount_residual_currency
                st_line_residual-=min(assigned_balance,st_line_residual,key=abs)
                st_line_residual_currency-=min(assigned_amount_currency,st_line_residual_currency,key=abs)
            else:
                assigned_balance=min(-aml.amount_residual,st_line_residual,key=abs)
                assigned_amount_currency=min(-aml.amount_residual_currency,st_line_residual_currency,key=abs)
                st_line_residual-=assigned_balance
                st_line_residual_currency-=assigned_amount_currency

            ifaml.currency_id==foreign_currency:
                lines_vals_list.append({
                    'id':aml.id,
                    'balance':assigned_amount_currency,
                    'currency_id':foreign_currency.id,
                })
            else:
                lines_vals_list.append({
                    'id':aml.id,
                    'balance':assigned_balance,
                    'currency_id':company_currency.id,
                })

        write_off_amount=max(aml_total_residual,-st_line_residual_before,key=abs)+st_line_residual_before+st_line_residual

        reconciliation_overview,open_balance_vals=st_line._prepare_reconciliation(lines_vals_list)

        writeoff_vals_list=self._get_write_off_move_lines_dict(st_line,write_off_amount)

        forline_valsinwriteoff_vals_list:
            st_line_residual-=st_line.company_currency_id.round(line_vals['balance'])
            line_vals['currency_id']=st_line.company_currency_id.id

        #Checkwehaveenoughinformationtocreateanopenbalance.
        ifopen_balance_valsandnotopen_balance_vals.get('account_id'):
            return[]

        returnlines_vals_list+writeoff_vals_list

    def_prepare_widget_writeoff_vals(self,st_line_id,write_off_vals):
        counterpart_vals=st_line_id._prepare_counterpart_move_line_vals({
                **write_off_vals,
                'currency_id':st_line_id.company_id.currency_id.id,
            })
        return{
            **counterpart_vals,
            'balance':counterpart_vals['amount_currency'],
            'reconcile_model_id':self.id,
        }

    ####################################################
    #RECONCILIATIONCRITERIA
    ####################################################

    def_apply_rules(self,st_lines,excluded_ids=None,partner_map=None):
        '''Applycriteriatogetcandidatesforallreconciliationmodels.

        Thisfunctioniscalledinenterprisebythereconciliationwidgettomatch
        thestatementlineswiththeavailablecandidates(usingthereconciliationmodels).

        :paramst_lines:       Account.bank.statement.linesrecordset.
        :paramexcluded_ids:   Account.move.linestoexclude.
        :parampartner_map:    Dictmappingeachlinewithnewpartnereventually.
        :return:               Adictmappingeachstatementlineidwith:
            *aml_ids:     Alistofaccount.move.lineids.
            *model:       Anaccount.reconcile.modelrecord(optional).
            *status:      'reconciled'ifthelineshasbeenalreadyreconciled,'write_off'ifthewrite-offmustbe
                            appliedonthestatementline.
        '''
        #ThisfunctionsusesSQLtocomputeitsresults.Weneedtoflushbeforedoinganythingmore.
        formodel_namein('account.bank.statement','account.bank.statement.line','account.move','account.move.line','res.company','account.journal','account.account'):
            self.env[model_name].flush(self.env[model_name]._fields)

        results={line.id:{'aml_ids':[]}forlineinst_lines}

        available_models=self.filtered(lambdam:m.rule_type!='writeoff_button').sorted()
        aml_ids_to_exclude=set()#Keeptrackofalreadyprocessedamls.
        reconciled_amls_ids=set()#Keeptrackofalreadyreconciledamls.

        #Firstassociatewitheachrecmodelsallthestatementlinesforwhichitisapplicable
        lines_with_partner_per_model=defaultdict(lambda:[])
        forst_lineinst_lines:

            #Statementlinescreatedinoldversionscouldhavearesidualamountofzero.Inthatcase,don'ttryto
            #matchanything.
            ifnotst_line.amount_residual:
                continue

            mapped_partner=(partner_mapandpartner_map.get(st_line.id)andself.env['res.partner'].browse(partner_map[st_line.id]))orst_line.partner_id

            forrec_modelinavailable_models:
                partner=mapped_partnerorrec_model._get_partner_from_mapping(st_line)

                ifrec_model._is_applicable_for(st_line,partner):
                    lines_with_partner_per_model[rec_model].append((st_line,partner))

        #ExecuteonlyoneSQLqueryforeachmodel(forperformance)
        matched_lines=self.env['account.bank.statement.line']
        forrec_modelinavailable_models:

            #Wefilterthelinesforthismodel,incaseapreviousonehasalreadyfoundsomethingforthem
            filtered_st_lines_with_partner=[xforxinlines_with_partner_per_model[rec_model]ifx[0]notinmatched_lines]

            ifnotfiltered_st_lines_with_partner:
                #Nounreconciledstatementlineforthismodel
                continue

            all_model_candidates=rec_model._get_candidates(filtered_st_lines_with_partner,excluded_ids)

            forst_line,partnerinfiltered_st_lines_with_partner:
                candidates=all_model_candidates[st_line.id]
                ifcandidates:
                    model_rslt,new_reconciled_aml_ids,new_treated_aml_ids=rec_model._get_rule_result(st_line,candidates,aml_ids_to_exclude,reconciled_amls_ids,partner)

                    ifmodel_rslt:
                        #Weinjecttheselectedpartner(possiblycomingfromtherecmodel)
                        model_rslt['partner']=partner

                        results[st_line.id]=model_rslt
                        reconciled_amls_ids|=new_reconciled_aml_ids
                        aml_ids_to_exclude|=new_treated_aml_ids
                        matched_lines+=st_line

        returnresults

    def_is_applicable_for(self,st_line,partner):
        """Returnstrueiffthisreconciliationmodelcanbeusedtosearchformatches
        fortheprovidedstatementlineandpartner.
        """
        self.ensure_one()

        #Filteronjournals,amountnature,amountandpartners
        #Alltheconditionsdefinedinthisblockarenon-matchconditions.
        if((self.match_journal_idsandst_line.move_id.journal_idnotinself.match_journal_ids)
            or(self.match_nature=='amount_received'andst_line.amount<0)
            or(self.match_nature=='amount_paid'andst_line.amount>0)
            or(self.match_amount=='lower'andabs(st_line.amount)>=self.match_amount_max)
            or(self.match_amount=='greater'andabs(st_line.amount)<=self.match_amount_min)
            or(self.match_amount=='between'and(abs(st_line.amount)>self.match_amount_maxorabs(st_line.amount)<self.match_amount_min))
            or(self.match_partnerandnotpartner)
            or(self.match_partnerandself.match_partner_idsandpartnernotinself.match_partner_ids)
            or(self.match_partnerandself.match_partner_category_idsandnot(partner.category_id&self.match_partner_category_ids))
        ):
            returnFalse

        #Filteronlabel,noteandtransaction_type
        forrecord,rule_field,record_fieldin[(st_line,'label','payment_ref'),(st_line.move_id,'note','narration'),(st_line,'transaction_type','transaction_type')]:
            rule_term=(self['match_'+rule_field+'_param']or'').lower()
            record_term=(record[record_field]or'').lower()

            #Thisdefinesnon-matchconditions
            if((self['match_'+rule_field]=='contains'andrule_termnotinrecord_term)
                or(self['match_'+rule_field]=='not_contains'andrule_terminrecord_term)
                or(self['match_'+rule_field]=='match_regex'andnotre.match(rule_term,record_term))
            ):
                returnFalse

        returnTrue

    def_get_candidates(self,st_lines_with_partner,excluded_ids):
        """Returnsthematchcandidatesforthisrule,withrespecttotheprovidedparameters.

        :paramst_lines_with_partner:Alistoftuples(statement_line,partner),
                                      associatingeachstatementlinetotreatewith
                                      thecorrespondingpartner,givenbythepartnermap
        :paramexcluded_ids:asetcontainingtheidsoftheamlstoignoreduringthesearch
                             (becausetheyalreadybeenmatchedbyanotherrule)
        """
        self.ensure_one()

        #Onbigdatabases,itispossiblethatsomesetupswillcreatehugequerieswhentryingtoapplyreconciliationmodels.
        #Insuchcases,thisquerymighttakeaverylongtimetorun,essentiallyeatingupalltheavailableCPU,andproof
        #impossibletokill,becauseofthetypeofoperationsranbySQL.Toalleviatethat,weintroducetheconfigparameterbelow,
        #whichessentiallyallowscuttingthelistofstatementlinestomatchintoslices,andrunningthematchinginmultiplequeries.
        #Thisway,weavoidserveroverload,givingtheabilitytokilltheprocessiftakestoolong.
        slice_size=len(st_lines_with_partner)
        slice_size_param=self.env['ir.config_parameter'].sudo().get_param('account.reconcile_model_forced_slice_size')
        ifslice_size_param:
            converted_param=int(slice_size_param)
            ifconverted_param>0:
                slice_size=converted_param

        treatment_slices=[]
        slice_start=0
        whileslice_start<len(st_lines_with_partner):
            slice_end=slice_start+slice_size
            treatment_slices.append(st_lines_with_partner[slice_start:slice_end])
            slice_start=slice_end

        treatment_map={
            'invoice_matching':lambdarec_model,slice:rec_model._get_invoice_matching_query(slice,excluded_ids),
            'writeoff_suggestion':lambdarec_model,slice:rec_model._get_writeoff_suggestion_query(slice,excluded_ids),
        }
        rslt=defaultdict(lambda:[])
        fortreatment_sliceintreatment_slices:
            query_generator=treatment_map[self.rule_type]
            query,params=query_generator(self,treatment_slice)
            self._cr.execute(query,params)

            forcandidate_dictinself._cr.dictfetchall():
                rslt[candidate_dict['id']].append(candidate_dict)

        returnrslt

    def_get_invoice_matching_query(self,st_lines_with_partner,excluded_ids):
        '''Returnsthequeryapplyingthecurrentinvoice_matchingreconciliation
        modeltotheprovidedstatementlines.

        :paramst_lines_with_partner:Alistoftuples(statement_line,partner),
                                      associatingeachstatementlinetotreatewith
                                      thecorrespondingpartner,givenbythepartnermap
        :paramexcluded_ids:   Account.move.linestoexclude.
        :return:               (query,params)
        '''
        self.ensure_one()
        ifself.rule_type!='invoice_matching':
            raiseUserError(_('ProgrammationError:Can\'tcall_get_invoice_matching_query()fordifferentrulesthan\'invoice_matching\''))

        unaccent=get_unaccent_wrapper(self._cr)

        #N.B:'communication_flag'istheretodistinguishinvoicematchingthroughthenumber/reference
        #(higherpriority)frominvoicematchingusingthepartner(lowerpriority).
        query=r'''
        SELECT
            st_line.id                         ASid,
            aml.id                             ASaml_id,
            aml.currency_id                    ASaml_currency_id,
            aml.date_maturity                  ASaml_date_maturity,
            aml.amount_residual                ASaml_amount_residual,
            aml.amount_residual_currency       ASaml_amount_residual_currency,
            '''+self._get_select_communication_flag()+r'''AScommunication_flag,
            '''+self._get_select_payment_reference_flag()+r'''ASpayment_reference_flag
        FROMaccount_bank_statement_linest_line
        JOINaccount_movest_line_move         ONst_line_move.id=st_line.move_id
        JOINres_companycompany               ONcompany.id=st_line_move.company_id
        ,account_move_lineaml
        LEFTJOINaccount_movemove            ONmove.id=aml.move_idANDmove.state='posted'
        LEFTJOINaccount_accountaccount      ONaccount.id=aml.account_id
        LEFTJOINres_partneraml_partner      ONaml.partner_id=aml_partner.id
        LEFTJOINaccount_paymentpayment      ONpayment.move_id=move.id
        WHERE
            aml.company_id=st_line_move.company_id
            ANDmove.state='posted'
            ANDaccount.reconcileISTRUE
            ANDaml.reconciledISFALSE
            AND(account.internal_typeNOTIN('receivable','payable')ORaml.payment_idISNULL)
        '''

        #Addconditionstohandleeachofthestatementlineswewanttomatch
        st_lines_queries=[]
        forst_line,partnerinst_lines_with_partner:
            #Incasewedon'thaveanypartnerforthisline,wetryassigningonewiththerulemapping
            ifst_line.amount>0:
                st_line_subquery=r"aml.balance>0"
            else:
                st_line_subquery=r"aml.balance<0"

            ifself.match_same_currency:
                st_line_subquery+=r"ANDCOALESCE(aml.currency_id,company.currency_id)=%s"%(st_line.foreign_currency_id.idorst_line.move_id.currency_id.id)

            ifpartner:
                st_line_subquery+=r"ANDaml.partner_id=%s"%partner.id
            else:
                st_line_fields_consideration=[
                    (self.match_text_location_label,'st_line.payment_ref'),
                    (self.match_text_location_note,'st_line_move.narration'),
                    (self.match_text_location_reference,'st_line_move.ref'),
                ]

                no_partner_query="OR".join([
                    r"""
                        (
                            substring(REGEXP_REPLACE("""+sql_field+""",'[^0-9\s]','','g'),'\S(?:.*\S)*')!=''
                            AND
                            (
                                ("""+self._get_select_communication_flag()+""")
                                OR
                                ("""+self._get_select_payment_reference_flag()+""")
                            )
                        )
                        OR
                        (
                            /*Wealsomatchstatementlineswithoutpartnerswithamls
                            whosepartner'sname'sparts(splittingonspace)areallpresent
                            withinthepayment_ref,inanyorder,withanycharactersbetweenthem.*/

                            aml_partner.nameISNOTNULL
                            AND"""+unaccent(sql_field)+r"""~*('^'||(
                                SELECTstring_agg(concat('(?=.*\m',chunk[1],'\M)'),'')
                                  FROMregexp_matches("""+unaccent("aml_partner.name")+r""",'\w{3,}','g')ASchunk
                            ))
                        )
                    """
                    forconsider_field,sql_fieldinst_line_fields_consideration
                    ifconsider_field
                ])

                ifno_partner_query:
                    st_line_subquery+="AND"+no_partner_query

            st_lines_queries.append(r"st_line.id=%sAND(%s)"%(st_line.id,st_line_subquery))

        query+=r"AND(%s)"%"OR".join(st_lines_queries)

        params={}

        #Ifthisreconciliationmodeldefinesapast_months_limit,weaddacondition
        #tothequerytoonlysearchonmovelinesthatareyoungerthanthislimit.
        ifself.past_months_limit:
            date_limit=fields.Date.context_today(self)-relativedelta(months=self.past_months_limit)
            query+="ANDaml.date>=%(aml_date_limit)s"
            params['aml_date_limit']=date_limit

        #Filteroutexcludedaccount.move.line.
        ifexcluded_ids:
            query+='ANDaml.idNOTIN%(excluded_aml_ids)s'
            params['excluded_aml_ids']=tuple(excluded_ids)

        ifself.matching_order=='new_first':
            query+='ORDERBYaml_date_maturityDESC,aml_idDESC'
        else:
            query+='ORDERBYaml_date_maturityASC,aml_idASC'

        returnquery,params

    def_get_select_communication_flag(self):
        self.ensure_one()
        #Determineamatchingornotwiththestatementlinecommunicationusingtheaml.name,move.nameormove.ref.
        st_ref_list=[]
        ifself.match_text_location_label:
            st_ref_list+=['st_line.payment_ref']
        ifself.match_text_location_note:
            st_ref_list+=['st_line_move.narration']
        ifself.match_text_location_reference:
            st_ref_list+=['st_line_move.ref']

        st_ref="||''||".join(
            "COALESCE(%s,'')"%st_ref_name
            forst_ref_nameinst_ref_list
        )
        ifnotst_ref:
            return"FALSE"

        statement_compare=r"""(
                {move_field}ISNOTNULLANDsubstring(REGEXP_REPLACE({move_field},'[^0-9\s]','','g'),'\S(?:.*\S)*')!=''
                AND(
                    regexp_split_to_array(substring(REGEXP_REPLACE({move_field},'[^0-9\s]','','g'),'\S(?:.*\S)*'),'\s+')
                    &&regexp_split_to_array(substring(REGEXP_REPLACE({st_ref},'[^0-9\s]','','g'),'\S(?:.*\S)*'),'\s+')
                )
            )"""
        return"OR".join(
            statement_compare.format(move_field=field,st_ref=st_ref)
            forfieldin['aml.name','move.name','move.ref']
        )

    def_get_select_payment_reference_flag(self):
        #Determineamatchingornotwiththestatementlinecommunicationusingthemove.payment_reference.
        st_ref_list=[]
        ifself.match_text_location_label:
            st_ref_list+=['st_line.payment_ref']
        ifself.match_text_location_note:
            st_ref_list+=['st_line_move.narration']
        ifself.match_text_location_reference:
            st_ref_list+=['st_line_move.ref']
        ifnotst_ref_list:
            return"FALSE"

        #payment_referenceisnotusedonaccount.moveforpayments;refisusedinstead
        returnr'''((move.payment_referenceISNOTNULLOR(payment.idISNOTNULLANDmove.refISNOTNULL))AND({}))'''.format(
            'OR'.join(
                rf"regexp_replace(CASEWHENpayment.idISNULLTHENmove.payment_referenceELSEmove.refEND,'\s+','','g')=regexp_replace({st_ref},'\s+','','g')"
                forst_refinst_ref_list
            )
        )

    def_get_partner_from_mapping(self,st_line):
        """Findpartnerwithmappingdefinedonmodel.

        Forinvoicematchingrules,matchesthestatementlineagainsteach
        regexdefinedinpartnermapping,andreturnsthepartnercorresponding
        tothefirstonematching.

        :paramst_line(Model<account.bank.statement.line>):
            Thestatementlinethatneedsapartnertobefound
        :returnModel<res.partner>:
            Thepartnerfoundfromthemapping.Canbeemptyanemptyrecordset
            iftherewasnothingfoundfromthemappingorifthefunctionis
            notapplicable.
        """
        self.ensure_one()

        ifself.rule_typenotin('invoice_matching','writeoff_suggestion'):
            returnself.env['res.partner']

        forpartner_mappinginself.partner_mapping_line_ids:
            match_payment_ref=re.match(partner_mapping.payment_ref_regex,st_line.payment_ref)ifpartner_mapping.payment_ref_regexelseTrue
            match_narration=re.match(partner_mapping.narration_regex,st_line.narrationor'')ifpartner_mapping.narration_regexelseTrue

            ifmatch_payment_refandmatch_narration:
                returnpartner_mapping.partner_id
        returnself.env['res.partner']

    def_get_writeoff_suggestion_query(self,st_lines_with_partner,excluded_ids=None):
        '''Returnsthequeryapplyingthecurrentwriteoff_suggestionreconciliation
        modeltotheprovidedstatementlines.

        :paramst_lines_with_partner:Alistoftuples(statement_line,partner),
                                      associatingeachstatementlinetotreatewith
                                      thecorrespondingpartner,givenbythepartnermap
        :paramexcluded_ids:   Account.move.linestoexclude.
        :return:               (query,params)
        '''
        self.ensure_one()

        ifself.rule_type!='writeoff_suggestion':
            raiseUserError(_("ProgrammationError:Can'tcall_get_writeoff_suggestion_query()fordifferentrulesthan'writeoff_suggestion'"))

        query='''
            SELECT
                st_line.id                         ASid
            FROMaccount_bank_statement_linest_line
            WHEREst_line.idIN%(st_line_ids)s
        '''
        params={
            'st_line_ids':tuple(st_line.idfor(st_line,partner)inst_lines_with_partner),
        }

        returnquery,params

    def_get_rule_result(self,st_line,candidates,aml_ids_to_exclude,reconciled_amls_ids,partner_map):
        """Gettheresultofarulefromthelistofavailablecandidates,dependingonthe
        otherreconciliationsperformedbypreviousrules.
        """
        self.ensure_one()

        ifself.rule_type=='invoice_matching':
            returnself._get_invoice_matching_rule_result(st_line,candidates,aml_ids_to_exclude,reconciled_amls_ids,partner_map)
        elifself.rule_type=='writeoff_suggestion':
            returnself._get_writeoff_suggestion_rule_result(st_line,partner_map),set(),set()
        else:
            returnNone,set(),set()

    def_get_invoice_matching_rule_result(self,st_line,candidates,aml_ids_to_exclude,reconciled_amls_ids,partner):
        new_reconciled_aml_ids=set()
        new_treated_aml_ids=set()
        candidates,priorities=self._filter_candidates(candidates,aml_ids_to_exclude,reconciled_amls_ids)

        #Specialcase:theamountsarethesame,submitthelinedirectly.
        st_line_currency=st_line.foreign_currency_idorst_line.currency_id
        candidate_currencies=set(candidate['aml_currency_id']orst_line.company_id.currency_id.idforcandidateincandidates)
        ifcandidate_currencies=={st_line_currency.id}:
            forcandidateincandidates:
                residual_amount=candidate['aml_currency_id']andcandidate['aml_amount_residual_currency']orcandidate['aml_amount_residual']
                ifst_line_currency.is_zero(residual_amount+st_line.amount_residual):
                    candidates,priorities=self._filter_candidates([candidate],aml_ids_to_exclude,reconciled_amls_ids)
                    break

        #Wechecktheamountcriteriaofthereconciliationmodel,andselectthe
        #candidatesiftheypasstheverification.Candidatesfromthefirstpriority
        #level(evenalreadyselected)bypassthischeck,andareselectedanyway.
        disable_bypass=self.env['ir.config_parameter'].sudo().get_param('account.disable_rec_models_bypass')
        if(notdisable_bypassandpriorities&{1,2})orself._check_rule_propositions(st_line,candidates):
            rslt={
                'model':self,
                'aml_ids':[candidate['aml_id']forcandidateincandidates],
            }
            new_treated_aml_ids=set(rslt['aml_ids'])

            #Createwrite-offlines.
            lines_vals_list=self._prepare_reconciliation(st_line,aml_ids=rslt['aml_ids'],partner=partner)

            #Awrite-offmustbeappliediftherearesome'new'linestopropose.
            write_off_lines_vals=list(filter(lambdax:'id'notinx,lines_vals_list))
            ifnotlines_vals_listorwrite_off_lines_vals:
                rslt['status']='write_off'
                rslt['write_off_vals']=write_off_lines_vals

            #Processauto-reconciliation.Weonlydothatforthefirsttwopriorities,iftheyarenotmatchedelsewhere.
            iflines_vals_listandpriorities&{1,3}andself.auto_reconcile:
                ifnotst_line.partner_idandpartner:
                    st_line.partner_id=partner

                st_line.reconcile(lines_vals_list)
                rslt['status']='reconciled'
                rslt['reconciled_lines']=st_line.line_ids
                new_reconciled_aml_ids=new_treated_aml_ids
        else:
            rslt=None

        returnrslt,new_reconciled_aml_ids,new_treated_aml_ids

    def_check_rule_propositions(self,statement_line,candidates):
        '''Checkrestrictionsthatcan'tbehandledforeachmove.lineseparately.
        /!\Onlyusedbymodelshavingatypeequalsto'invoice_matching'.
        :paramstatement_line: Anaccount.bank.statement.linerecord.
        :paramcandidates:     Fetchedaccount.move.linesfromquery(dict).
        :return:               Trueifthereconciliationpropositionsareaccepted.Falseotherwise.
        '''
        ifnotself.match_total_amount:
            returnTrue
        ifnotcandidates:
            returnFalse

        reconciliation_overview,open_balance_vals=statement_line._prepare_reconciliation([{
            'currency_id':aml['aml_currency_id'],
            'amount_residual':aml['aml_amount_residual'],
            'amount_residual_currency':aml['aml_amount_residual_currency'],
        }foramlincandidates])

        #Matchtotalresidualamount.
        line_currency=statement_line.foreign_currency_idorstatement_line.currency_id
        line_residual=statement_line.amount_residual
        line_residual_after_reconciliation=line_residual

        forreconciliation_valsinreconciliation_overview:
            line_vals=reconciliation_vals['line_vals']
            ifline_vals['currency_id']:
                line_residual_after_reconciliation-=line_vals['amount_currency']
            else:
                line_residual_after_reconciliation-=line_vals['debit']-line_vals['credit']

        #Statementlineamountisequaltothetotalresidual.
        ifline_currency.is_zero(line_residual_after_reconciliation):
            returnTrue
        residual_difference=line_residual-line_residual_after_reconciliation
        reconciled_percentage=100-abs(line_residual_after_reconciliation)/abs(residual_difference)*100if(residual_difference!=0)else0
        returnreconciled_percentage>=self.match_total_amount_param

    def_filter_candidates(self,candidates,aml_ids_to_exclude,reconciled_amls_ids):
        """Sortsreconciliationcandidatesbypriorityandfiltersthemsothatonly
        themostprioritaryarekept.
        """
        candidates_by_priority=self._sort_reconciliation_candidates_by_priority(candidates,aml_ids_to_exclude,reconciled_amls_ids)

        #Thiscanhappenifthecandidateswerealreadyreconciledatthispoint
        ifnotcandidates_by_priority:
            return[],set()

        max_priority=min(candidates_by_priority.keys())

        filtered_candidates=candidates_by_priority[max_priority]
        filtered_priorities={max_priority,}

        ifmax_priorityin(1,3,5):
            #Wealsokeepthealreadyproposedvaluesofthesameprioritylevel
            proposed_priority=max_priority+1
            filtered_candidates+=candidates_by_priority[proposed_priority]
            ifcandidates_by_priority[proposed_priority]:
                filtered_priorities.add(proposed_priority)

        returnfiltered_candidates,filtered_priorities

    def_sort_reconciliation_candidates_by_priority(self,candidates,already_proposed_aml_ids,already_reconciled_aml_ids):
        """Sortstheprovidedcandidatesandreturnsamappingofcandidatesby
        priority(1beingthehighest).

        Theprioritiesaredefinedasfollows:

        1:payment_reference_flagistrue, sothemove'spayment_reference
           fieldmatchesthestatementline's.

        2:Sameas1,butthecandidateshavealreadybeenproposedforapreviousstatementline

        3:communication_flagistrue,soeitherthemove'sref,move'snameor
           aml'snamematchthestatementline'spaymentreference.

        4:Sameas3,butthecandidateshavealreadybeenproposedforapreviousstatementline

        5:candidatesproposedbythequery,butnomatchwiththestatement
           line'spaymentrefcouldbefound.

        6:Sameas5,butthecandidateshavealreadybeenproposedforapreviousstatementline
        """
        candidates_by_priority=defaultdict(lambda:[])

        forcandidateinfilter(lambdax:x['aml_id']notinalready_reconciled_aml_ids,candidates):

            ifcandidate['payment_reference_flag']:
                priority=1
            elifcandidate['communication_flag']:
                priority=3
            else:
                priority=5

            ifcandidate['aml_id']inalready_proposed_aml_ids:
                #So,priorities2,4and6arecreatedhere
                priority+=1

            candidates_by_priority[priority].append(candidate)

        returncandidates_by_priority

    def_get_writeoff_suggestion_rule_result(self,st_line,partner):
        #Createwrite-offlines.
        lines_vals_list=self._prepare_reconciliation(st_line,partner=partner)

        rslt={
            'model':self,
            'status':'write_off',
            'aml_ids':[],
            'write_off_vals':lines_vals_list,
        }

        #Processauto-reconciliation.
        iflines_vals_listandself.auto_reconcile:
            ifnotst_line.partner_idandpartner:
                st_line.partner_id=partner

            st_line.reconcile(lines_vals_list)
            rslt['status']='reconciled'
            rslt['reconciled_lines']=st_line.line_ids

        returnrslt
