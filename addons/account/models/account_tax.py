#-*-coding:utf-8-*-
fromflectraimportapi,fields,models,_
fromflectra.osvimportexpression
fromflectra.tools.float_utilsimportfloat_roundasround
fromflectra.exceptionsimportUserError,ValidationError

importmath
importlogging


TYPE_TAX_USE=[
    ('sale','Sales'),
    ('purchase','Purchases'),
    ('none','None'),
]


classAccountTaxGroup(models.Model):
    _name='account.tax.group'
    _description='TaxGroup'
    _order='sequenceasc,id'

    name=fields.Char(required=True,translate=True)
    sequence=fields.Integer(default=10)
    property_tax_payable_account_id=fields.Many2one('account.account',company_dependent=True,string='Taxcurrentaccount(payable)')
    property_tax_receivable_account_id=fields.Many2one('account.account',company_dependent=True,string='Taxcurrentaccount(receivable)')
    property_advance_tax_payment_account_id=fields.Many2one('account.account',company_dependent=True,string='AdvanceTaxpaymentaccount')

    def_any_is_configured(self,company_id):
        domain=expression.OR([[('property_tax_payable_account_id','!=',False)],
                                [('property_tax_receivable_account_id','!=',False)],
                                [('property_advance_tax_payment_account_id','!=',False)]])
        group_with_config=self.with_company(company_id).search_count(domain)
        returngroup_with_config>0


classAccountTax(models.Model):
    _name='account.tax'
    _description='Tax'
    _order='sequence,id'
    _check_company_auto=True

    @api.model
    def_default_tax_group(self):
        returnself.env['account.tax.group'].search([],limit=1)

    name=fields.Char(string='TaxName',required=True)
    type_tax_use=fields.Selection(TYPE_TAX_USE,string='TaxType',required=True,default="sale",
        help="Determineswherethetaxisselectable.Note:'None'meansataxcan'tbeusedbyitself,howeveritcanstillbeusedinagroup.'adjustment'isusedtoperformtaxadjustment.")
    tax_scope=fields.Selection([('service','Services'),('consu','Goods')],string="TaxScope",help="Restricttheuseoftaxestoatypeofproduct.")
    amount_type=fields.Selection(default='percent',string="TaxComputation",required=True,
        selection=[('group','GroupofTaxes'),('fixed','Fixed'),('percent','PercentageofPrice'),('division','PercentageofPriceTaxIncluded')],
        help="""
    -GroupofTaxes:Thetaxisasetofsubtaxes.
    -Fixed:Thetaxamountstaysthesamewhatevertheprice.
    -PercentageofPrice:Thetaxamountisa%oftheprice:
        e.g100*(1+10%)=110(notpriceincluded)
        e.g110/(1+10%)=100(priceincluded)
    -PercentageofPriceTaxIncluded:Thetaxamountisadivisionoftheprice:
        e.g180/(1-10%)=200(notpriceincluded)
        e.g200*(1-10%)=180(priceincluded)
        """)
    active=fields.Boolean(default=True,help="Setactivetofalsetohidethetaxwithoutremovingit.")
    company_id=fields.Many2one('res.company',string='Company',required=True,readonly=True,default=lambdaself:self.env.company)
    children_tax_ids=fields.Many2many('account.tax',
        'account_tax_filiation_rel','parent_tax','child_tax',
        check_company=True,
        string='ChildrenTaxes')
    sequence=fields.Integer(required=True,default=1,
        help="Thesequencefieldisusedtodefineorderinwhichthetaxlinesareapplied.")
    amount=fields.Float(required=True,digits=(16,4),default=0.0)
    description=fields.Char(string='LabelonInvoices')
    price_include=fields.Boolean(string='IncludedinPrice',default=False,
        help="Checkthisifthepriceyouuseontheproductandinvoicesincludesthistax.")
    include_base_amount=fields.Boolean(string='AffectBaseofSubsequentTaxes',default=False,
        help="Ifset,taxeswhicharecomputedafterthisonewillbecomputedbasedonthepricetaxincluded.")
    analytic=fields.Boolean(string="IncludeinAnalyticCost",help="Ifset,theamountcomputedbythistaxwillbeassignedtothesameanalyticaccountastheinvoiceline(ifany)")
    tax_group_id=fields.Many2one('account.tax.group',string="TaxGroup",default=_default_tax_group,required=True)
    #Technicalfieldtomakethe'tax_exigibility'fieldinvisibleifthesamenamedfieldissettofalsein'res.company'model
    hide_tax_exigibility=fields.Boolean(string='HideUseCashBasisOption',related='company_id.tax_exigibility',readonly=True)
    tax_exigibility=fields.Selection(
        [('on_invoice','BasedonInvoice'),
         ('on_payment','BasedonPayment'),
        ],string='TaxDue',default='on_invoice',
        help="BasedonInvoice:thetaxisdueassoonastheinvoiceisvalidated.\n"
        "BasedonPayment:thetaxisdueassoonasthepaymentoftheinvoiceisreceived.")
    cash_basis_transition_account_id=fields.Many2one(string="CashBasisTransitionAccount",
        check_company=True,
        domain="[('deprecated','=',False),('company_id','=',company_id)]",
        comodel_name='account.account',
        help="Accountusedtotransitionthetaxamountforcashbasistaxes.Itwillcontainthetaxamountaslongastheoriginalinvoicehasnotbeenreconciled;atreconciliation,thisamountcancelledonthisaccountandputontheregulartaxaccount.")
    invoice_repartition_line_ids=fields.One2many(string="DistributionforInvoices",comodel_name="account.tax.repartition.line",inverse_name="invoice_tax_id",copy=True,help="Distributionwhenthetaxisusedonaninvoice")
    refund_repartition_line_ids=fields.One2many(string="DistributionforRefundInvoices",comodel_name="account.tax.repartition.line",inverse_name="refund_tax_id",copy=True,help="Distributionwhenthetaxisusedonarefund")
    tax_fiscal_country_id=fields.Many2one(string='FiscalCountry',comodel_name='res.country',related='company_id.account_tax_fiscal_country_id',help="Technicalfieldusedtorestrictthedomainofaccounttagsfortaxrepartitionlinescreatedforthistax.")
    country_code=fields.Char(related='company_id.country_id.code',readonly=True)

    _sql_constraints=[
        ('name_company_uniq','unique(name,company_id,type_tax_use,tax_scope)','Taxnamesmustbeunique!'),
    ]

    @api.model
    defdefault_get(self,fields_list):
        #company_idisaddedsothatwearesuretofetchadefaultvaluefromittouseinrepartitionlines,below
        rslt=super(AccountTax,self).default_get(fields_list+['company_id'])

        company_id=rslt.get('company_id')
        company=self.env['res.company'].browse(company_id)

        if'refund_repartition_line_ids'infields_list:
            #Wewriteontherelatedcountry_idfieldsothatthefieldisrecomputed.Withoutthat,itwillstayemptyuntilwesavetherecord.
            rslt['refund_repartition_line_ids']=[
                (0,0,{'repartition_type':'base','factor_percent':100.0,'tag_ids':[],'company_id':company_id,'tax_fiscal_country_id':company.country_id.id}),
                (0,0,{'repartition_type':'tax','factor_percent':100.0,'tag_ids':[],'company_id':company_id,'tax_fiscal_country_id':company.country_id.id}),
            ]

        if'invoice_repartition_line_ids'infields_list:
            #Wewriteontherelatedcountry_idfieldsothatthefieldisrecomputed.Withoutthat,itwillstayemptyuntilwesavetherecord.
            rslt['invoice_repartition_line_ids']=[
                (0,0,{'repartition_type':'base','factor_percent':100.0,'tag_ids':[],'company_id':company_id,'tax_fiscal_country_id':company.country_id.id}),
                (0,0,{'repartition_type':'tax','factor_percent':100.0,'tag_ids':[],'company_id':company_id,'tax_fiscal_country_id':company.country_id.id}),
            ]

        returnrslt

    def_check_repartition_lines(self,lines):
        self.ensure_one()

        base_line=lines.filtered(lambdax:x.repartition_type=='base')
        iflen(base_line)!=1:
            raiseValidationError(_("Invoiceandcreditnotedistributionshouldeachcontainexactlyonelineforthebase."))

    @api.constrains('invoice_repartition_line_ids','refund_repartition_line_ids')
    def_validate_repartition_lines(self):
        forrecordinself:
            #ifthetaxisanaggregationofitssub-taxes(group)itcanhavenorepartitionlines
            ifrecord.amount_type=='group'and\
                    notrecord.invoice_repartition_line_idsand\
                    notrecord.refund_repartition_line_ids:
                continue

            invoice_repartition_line_ids=record.invoice_repartition_line_ids.sorted()
            refund_repartition_line_ids=record.refund_repartition_line_ids.sorted()
            record._check_repartition_lines(invoice_repartition_line_ids)
            record._check_repartition_lines(refund_repartition_line_ids)

            iflen(invoice_repartition_line_ids)!=len(refund_repartition_line_ids):
                raiseValidationError(_("Invoiceandcreditnotedistributionshouldhavethesamenumberoflines."))

            ifnotinvoice_repartition_line_ids.filtered(lambdax:x.repartition_type=='tax')or\
                    notrefund_repartition_line_ids.filtered(lambdax:x.repartition_type=='tax'):
                raiseValidationError(_("Invoiceandcreditnoterepartitionshouldhaveatleastonetaxrepartitionline."))

            index=0
            whileindex<len(invoice_repartition_line_ids):
                inv_rep_ln=invoice_repartition_line_ids[index]
                ref_rep_ln=refund_repartition_line_ids[index]
                ifinv_rep_ln.repartition_type!=ref_rep_ln.repartition_typeorinv_rep_ln.factor_percent!=ref_rep_ln.factor_percent:
                    raiseValidationError(_("Invoiceandcreditnotedistributionshouldmatch(samepercentages,inthesameorder)."))
                index+=1

    @api.constrains('children_tax_ids','type_tax_use')
    def_check_children_scope(self):
        fortaxinself:
            ifnottax._check_m2m_recursion('children_tax_ids'):
                raiseValidationError(_("Recursionfoundfortax'%s'.")%(tax.name,))
            ifany(child.type_tax_usenotin('none',tax.type_tax_use)orchild.tax_scope!=tax.tax_scopeforchildintax.children_tax_ids):
                raiseValidationError(_('Theapplicationscopeoftaxesinagroupmustbeeitherthesameasthegrouporleftempty.'))

    @api.constrains('company_id')
    def_check_company_consistency(self):
        ifnotself:
            return

        self.flush(['company_id'])
        self._cr.execute('''
            SELECTline.id
            FROMaccount_move_lineline
            JOINaccount_taxtaxONtax.id=line.tax_line_id
            WHEREline.tax_line_idIN%s
            ANDline.company_id!=tax.company_id

            UNIONALL

            SELECTline.id
            FROMaccount_move_line_account_tax_reltax_rel
            JOINaccount_taxtaxONtax.id=tax_rel.account_tax_id
            JOINaccount_move_linelineONline.id=tax_rel.account_move_line_id
            WHEREtax_rel.account_tax_idIN%s
            ANDline.company_id!=tax.company_id
        ''',[tuple(self.ids)]*2)
        ifself._cr.fetchone():
            raiseUserError(_("Youcan'tchangethecompanyofyourtaxsincetherearesomejournalitemslinkedtoit."))

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        default=dict(defaultor{})
        if'name'notindefault:
            default['name']=_("%s(Copy)")%self.name
        returnsuper(AccountTax,self).copy(default=default)

    defname_get(self):
        name_list=[]
        type_tax_use=dict(self._fields['type_tax_use']._description_selection(self.env))
        tax_scope=dict(self._fields['tax_scope']._description_selection(self.env))
        forrecordinself:
            name=record.name
            ifself._context.get('append_type_to_tax_name'):
                name+='(%s)'%type_tax_use.get(record.type_tax_use)
            ifrecord.tax_scope:
                name+='(%s)'%tax_scope.get(record.tax_scope)
            name_list+=[(record.id,name)]
        returnname_list

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        """Returnsalistoftuplescontainingid,name,asinternallyitiscalled{defname_get}
            resultformat:{[(id,name),(id,name),...]}
        """
        args=argsor[]
        ifoperator=='ilike'andnot(nameor'').strip():
            domain=[]
        else:
            connector='&'ifoperatorinexpression.NEGATIVE_TERM_OPERATORSelse'|'
            domain=[connector,('description',operator,name),('name',operator,name)]
        returnself._search(expression.AND([domain,args]),limit=limit,access_rights_uid=name_get_uid)

    @api.model
    def_search(self,args,offset=0,limit=None,order=None,count=False,access_rights_uid=None):
        context=self._contextor{}

        ifcontext.get('move_type'):
            ifcontext.get('move_type')in('out_invoice','out_refund'):
                args+=[('type_tax_use','=','sale')]
            elifcontext.get('move_type')in('in_invoice','in_refund'):
                args+=[('type_tax_use','=','purchase')]

        ifcontext.get('journal_id'):
            journal=self.env['account.journal'].browse(context.get('journal_id'))
            ifjournal.typein('sale','purchase'):
                args+=[('type_tax_use','=',journal.type)]

        returnsuper(AccountTax,self)._search(args,offset,limit,order,count=count,access_rights_uid=access_rights_uid)

    @api.onchange('amount')
    defonchange_amount(self):
        ifself.amount_typein('percent','division')andself.amount!=0.0andnotself.description:
            self.description="{0:.4g}%".format(self.amount)

    @api.onchange('amount_type')
    defonchange_amount_type(self):
        ifself.amount_type!='group':
            self.children_tax_ids=[(5,)]
        ifself.amount_type=='group':
            self.description=None

    @api.onchange('price_include')
    defonchange_price_include(self):
        ifself.price_include:
            self.include_base_amount=True

    def_compute_amount(self,base_amount,price_unit,quantity=1.0,product=None,partner=None):
        """Returnstheamountofasingletax.base_amountistheactualamountonwhichthetaxisapplied,whichis
            price_unit*quantityeventuallyaffectedbyprevioustaxes(iftaxisinclude_base_amountXORprice_include)
        """
        self.ensure_one()

        ifself.amount_type=='fixed':
            #Usecopysigntotakeintoaccountthesignofthebaseamountwhichincludesthesign
            #ofthequantityandthesignoftheprice_unit
            #Amountisthefixedpriceforthetax,itcanbenegative
            #Baseamountincludedthesignofthequantityandthesignoftheunitpriceandwhen
            #aproductisreturned,itcanbedoneeitherbychangingthesignofquantityorbychangingthe
            #signofthepriceunit.
            #Whenthepriceunitisequalto0,thesignofthequantityisabsorbedinbase_amountthen
            #a"else"caseisneeded.
            ifbase_amount:
                returnmath.copysign(quantity,base_amount)*self.amount
            else:
                returnquantity*self.amount

        price_include=self._context.get('force_price_include',self.price_include)

        #base*(1+tax_amount)=new_base
        ifself.amount_type=='percent'andnotprice_include:
            returnbase_amount*self.amount/100
        #<=>new_base=base/(1+tax_amount)
        ifself.amount_type=='percent'andprice_include:
            returnbase_amount-(base_amount/(1+self.amount/100))
        #base/(1-tax_amount)=new_base
        ifself.amount_type=='division'andnotprice_include:
            returnbase_amount/(1-self.amount/100)-base_amountif(1-self.amount/100)else0.0
        #<=>new_base*(1-tax_amount)=base
        ifself.amount_type=='division'andprice_include:
            returnbase_amount-(base_amount*(self.amount/100))
        #defaultvalueforcustomamount_type
        return0.0

    defjson_friendly_compute_all(self,price_unit,currency_id=None,quantity=1.0,product_id=None,partner_id=None,is_refund=False):
        """Calledbythereconciliationtocomputetaxesonwriteoffduringbankreconciliation
        """
        ifcurrency_id:
            currency_id=self.env['res.currency'].browse(currency_id)
        ifproduct_id:
            product_id=self.env['product.product'].browse(product_id)
        ifpartner_id:
            partner_id=self.env['res.partner'].browse(partner_id)

        #Wefirstneedtofindoutwhetherthistaxcomputationismadeforarefund
        tax_type=selfandself[0].type_tax_use

        ifself._context.get('manual_reco_widget'):
            is_refund=is_refundor(tax_type=='sale'andprice_unit>0)or(tax_type=='purchase'andprice_unit<0)
        else:
            is_refund=is_refundor(tax_type=='sale'andprice_unit<0)or(tax_type=='purchase'andprice_unit>0)

        rslt=self.with_context(caba_no_transition_account=True)\
                   .compute_all(price_unit,currency=currency_id,quantity=quantity,product=product_id,partner=partner_id,is_refund=is_refund)

        #Thereconciliationwidgetcallsthisfunctiontogeneratewriteoffsonbankjournals,
        #sothesignofthetagsmightneedtobeinverted,sothatthetaxreport
        #computationcantreatthemasanyothermiscellaneousoperations,while
        #keepingacomputationinlinewiththeeffectthetaxwouldhavehadonaninvoice.

        if(tax_type=='sale'andnotis_refund)or(tax_type=='purchase'andis_refund):
            base_tags=self.env['account.account.tag'].browse(rslt['base_tags'])
            rslt['base_tags']=self.env['account.move.line']._revert_signed_tags(base_tags).ids

            fortax_resultinrslt['taxes']:
                tax_tags=self.env['account.account.tag'].browse(tax_result['tag_ids'])
                tax_result['tag_ids']=self.env['account.move.line']._revert_signed_tags(tax_tags).ids

        returnrslt

    defflatten_taxes_hierarchy(self,create_map=False):
        #Flattensthetaxescontainedinthisrecordset,returningallthe
        #childrenatthebottomofthehierarchy,inarecordset,orderedbysequence.
        #  Eg.consideringlettersastaxesandalphabeticorderassequence:
        #  [G,B([A,D,F]),E,C]willbecomputedas[A,D,F,C,E,G]
        #Ifcreate_mapisTrue,anadditionalvalueisreturned,adictionary
        #mappingeachchildtaxtoitsparentgroup
        all_taxes=self.env['account.tax']
        groups_map={}
        fortaxinself.sorted(key=lambdar:r.sequence):
            iftax.amount_type=='group':
                flattened_children=tax.children_tax_ids.flatten_taxes_hierarchy()
                all_taxes+=flattened_children
                forflat_childinflattened_children:
                    groups_map[flat_child]=tax
            else:
                all_taxes+=tax

        ifcreate_map:
            returnall_taxes,groups_map

        returnall_taxes

    defget_tax_tags(self,is_refund,repartition_type):
        rep_lines=self.mapped(is_refundand'refund_repartition_line_ids'or'invoice_repartition_line_ids')
        returnrep_lines.filtered(lambdax:x.repartition_type==repartition_type).mapped('tag_ids')

    defcompute_all(self,price_unit,currency=None,quantity=1.0,product=None,partner=None,is_refund=False,handle_price_include=True):
        """Returnsallinformationrequiredtoapplytaxes(inself+theirchildrenincaseofataxgroup).
            Weconsiderthesequenceoftheparentforgroupoftaxes.
                Eg.consideringlettersastaxesandalphabeticorderassequence:
                [G,B([A,D,F]),E,C]willbecomputedas[A,D,F,C,E,G]

            'handle_price_include'isusedwhenweneedtoignorealltaxincludedinprice.IfFalse,itmeansthe
            amountpassedtothismethodwillbeconsideredasthebaseofallcomputations.

        RETURN:{
            'total_excluded':0.0,   #Totalwithouttaxes
            'total_included':0.0,   #Totalwithtaxes
            'total_void'   :0.0,   #Totalwiththosetaxes,thatdon'thaveanaccountset
            'taxes':[{              #Onedictforeachtaxinselfandtheirchildren
                'id':int,
                'name':str,
                'amount':float,
                'sequence':int,
                'account_id':int,
                'refund_account_id':int,
                'analytic':boolean,
            }],
        }"""
        ifnotself:
            company=self.env.company
        else:
            company=self[0].company_id

        #1)Flattenthetaxes.
        taxes,groups_map=self.flatten_taxes_hierarchy(create_map=True)

        #2)Dealwiththeroundingmethods
        ifnotcurrency:
            currency=company.currency_id

        #Bydefault,foreachtax,taxamountwillfirstbecomputed
        #androundedatthe'Account'decimalprecisionforeach
        #PO/SO/invoicelineandthentheseroundedamountswillbe
        #summed,leadingtothetotalamountforthattax.But,ifthe
        #companyhastax_calculation_rounding_method=round_globally,
        #westillfollowthesamemethod,butweuseamuchlarger
        #precisionwhenweroundthetaxamountforeachline(weuse
        #the'Account'decimalprecision+5),andthatwayit'slike
        #roundingafterthesumofthetaxamountsofeachline
        prec=currency.rounding

        #Insomecases,itisnecessarytoforce/preventtheroundingofthetaxandthetotal
        #amounts.Forexample,inSO/POline,wedon'twanttoroundthepriceunitatthe
        #precisionofthecurrency.
        #Thecontextkey'round'allowstoforcethestandardbehavior.
        round_tax=Falseifcompany.tax_calculation_rounding_method=='round_globally'elseTrue
        if'round'inself.env.context:
            round_tax=bool(self.env.context['round'])

        ifnotround_tax:
            prec*=1e-5

        #3)Iteratethetaxesinthereversedsequenceordertoretrievetheinitialbaseofthecomputation.
        #    tax | base | amount |
        #/\----------------------------
        #||tax_1| XXXX |         |<-wearelookingforthat,it'sthetotal_excluded
        #||tax_2|  ..  |         |
        #||tax_3|  ..  |         |
        #|| ... |  ..  |   ..   |
        #   ----------------------------
        defrecompute_base(base_amount,fixed_amount,percent_amount,division_amount):
            #Recomputethenewbaseamountbasedonincludedfixed/percentamountsandthecurrentbaseamount.
            #Example:
            # tax | amount |  type  | price_include |
            #-----------------------------------------------
            #tax_1|  10%   |percent | t
            #tax_2|  15    |  fix   | t
            #tax_3|  20%   |percent | t
            #tax_4|  10%   |division| t
            #-----------------------------------------------

            #ifbase_amount=145,thenewbaseiscomputedas:
            #(145-15)/(1.0+30%)*90%=130/1.3*90%=90
            return(base_amount-fixed_amount)/(1.0+percent_amount/100.0)*(100-division_amount)/100

        #Thefirst/lastbasemustabsolutelyberoundedtoworkinroundglobally.
        #Indeed,thesumofalltaxes('taxes'keyintheresultdictionary)mustbestrictlyequalsto
        #'price_included'-'price_excluded'whatevertheroundingmethod.
        #
        #Exampleusingtheglobalroundingwithoutanydecimals:
        #Supposetwoinvoicelines:27000and10920,bothhavinga19%priceincludedtax.
        #
        #                  Line1                     Line2
        #-----------------------------------------------------------------------
        #total_included:  27000                      10920
        #tax:             27000/1.19=4310.924    10920/1.19=1743.529
        #total_excluded:  22689.076                  9176.471
        #
        #Iftheroundingofthetotal_excludedisn'tmadeattheend,itcouldleadtosomeroundingissues
        #whensummingthetaxamounts,e.g.oninvoices.
        #Inthatcase:
        # -amount_untaxedwillbe22689+9176=31865
        # -amount_taxwillbe4310.924+1743.529=6054.453~6054
        # -amount_totalwillbe31865+6054=37919!=37920=27000+10920
        #
        #Byperformingaroundingattheendtocomputetheprice_excludedamount,theamount_taxwillbestrictly
        #equalsto'price_included'-'price_excluded'afterroundingandthen:
        #  Line1:sum(taxes)=27000-22689=4311
        #  Line2:sum(taxes)=10920-2176=8744
        #  amount_tax=4311+8744=13055
        #  amount_total=31865+13055=37920
        base=currency.round(price_unit*quantity)

        #Forthecomputationofmovelines,wecouldhaveanegativebasevalue.
        #Inthiscase,computeallwithpositivevaluesandnegatethemattheend.
        sign=1
        ifcurrency.is_zero(base):
            sign=self._context.get('force_sign',1)
        elifbase<0:
            sign=-1
        ifbase<0:
            base=-base

        #Storethetotalstoreachwhenusingprice_includetaxes(onlythelastpriceincludedinrow)
        total_included_checkpoints={}
        i=len(taxes)-1
        store_included_tax_total=True
        #Keeptrackoftheaccumulatedincludedfixed/percentamount.
        incl_fixed_amount=incl_percent_amount=incl_division_amount=0
        #Storethetaxamountswecomputewhilesearchingforthetotal_excluded
        cached_tax_amounts={}
        ifhandle_price_include:
            fortaxinreversed(taxes):
                tax_repartition_lines=(
                    is_refund
                    andtax.refund_repartition_line_ids
                    ortax.invoice_repartition_line_ids
                ).filtered(lambdax:x.repartition_type=="tax")
                sum_repartition_factor=sum(tax_repartition_lines.mapped("factor"))

                iftax.include_base_amount:
                    base=recompute_base(base,incl_fixed_amount,incl_percent_amount,incl_division_amount)
                    incl_fixed_amount=incl_percent_amount=incl_division_amount=0
                    store_included_tax_total=True
                iftax.price_includeorself._context.get('force_price_include'):
                    iftax.amount_type=='percent':
                        incl_percent_amount+=tax.amount*sum_repartition_factor
                    eliftax.amount_type=='division':
                        incl_division_amount+=tax.amount*sum_repartition_factor
                    eliftax.amount_type=='fixed':
                        incl_fixed_amount+=abs(quantity)*tax.amount*sum_repartition_factor
                    else:
                        #tax.amount_type==other(python)
                        tax_amount=tax._compute_amount(base,sign*price_unit,quantity,product,partner)*sum_repartition_factor
                        incl_fixed_amount+=tax_amount
                        #Avoidunecessaryre-computation
                        cached_tax_amounts[i]=tax_amount
                    #Incaseofazerotax,donotstorethebaseamountsincethetaxamountwill
                    #bezeroanyway.GroupandPythontaxeshaveanamountofzero,sodonottake
                    #themintoaccount.
                    ifstore_included_tax_totaland(
                        tax.amountortax.amount_typenotin("percent","division","fixed")
                    ):
                        total_included_checkpoints[i]=base
                        store_included_tax_total=False
                i-=1

        total_excluded=currency.round(recompute_base(base,incl_fixed_amount,incl_percent_amount,incl_division_amount))

        #4)Iteratethetaxesinthesequenceordertocomputemissingtaxamounts.
        #Startthecomputationofaccumulatedamountsatthetotal_excludedvalue.
        base=total_included=total_void=total_excluded

        #Flagindicatingthecheckpointusedinprice_includetoavoidroundingissuemustbeskippedsincethebase
        #amounthaschangedbecausewearecurrentlymixingprice-includedandprice-excludedinclude_base_amount
        #taxes.
        skip_checkpoint=False

        taxes_vals=[]
        i=0
        cumulated_tax_included_amount=0
        fortaxintaxes:
            tax_repartition_lines=(is_refundandtax.refund_repartition_line_idsortax.invoice_repartition_line_ids).filtered(lambdax:x.repartition_type=='tax')
            sum_repartition_factor=sum(tax_repartition_lines.mapped('factor'))

            price_include=self._context.get('force_price_include',tax.price_include)

            #computethetax_amount
            ifnotskip_checkpointandprice_includeandtotal_included_checkpoints.get(i)isnotNoneandsum_repartition_factor!=0:
                #Weknowthetotaltoreachforthattax,sowemakeasubstractiontoavoidanyroundingissues
                tax_amount=total_included_checkpoints[i]-(base+cumulated_tax_included_amount)
                cumulated_tax_included_amount=0
            else:
                tax_amount=tax.with_context(force_price_include=False)._compute_amount(
                    base,sign*price_unit,quantity,product,partner)

            #Roundthetax_amountmultipliedbythecomputedrepartitionlinesfactor.
            tax_amount=round(tax_amount,precision_rounding=prec)
            factorized_tax_amount=round(tax_amount*sum_repartition_factor,precision_rounding=prec)

            ifprice_includeandtotal_included_checkpoints.get(i)isNone:
                cumulated_tax_included_amount+=factorized_tax_amount

            #Ifthetaxaffectsthebaseofsubsequenttaxes,itstaxmovelinesmust
            #receivethebasetagsandtag_idsofthesetaxes,sothatthetaxreportcomputes
            #therighttotal
            subsequent_taxes=self.env['account.tax']
            subsequent_tags=self.env['account.account.tag']
            iftax.include_base_amount:
                subsequent_taxes=taxes[i+1:]
                subsequent_tags=subsequent_taxes.get_tax_tags(is_refund,'base')

            #Computethetaxlineamountsbymultiplyingeachfactorwiththetaxamount.
            #Then,spreadthetaxroundingtoensuretheconsistencyofeachlineindependentlywiththefactorized
            #amount.E.g:
            #
            #Supposeataxhaving4x50%repartitionlineappliedonataxamountof0.03with2decimalplaces.
            #Thefactorized_tax_amountwillbe0.06(200%x0.03).However,eachlinetakenindependentlywillcompute
            #50%*0.03=0.01withrounding.Itmeansthereis0.06-0.04=0.02astotal_rounding_errortodispatch
            #inlinesas2x0.01.
            repartition_line_amounts=[round(tax_amount*line.factor,precision_rounding=prec)forlineintax_repartition_lines]
            total_rounding_error=round(factorized_tax_amount-sum(repartition_line_amounts),precision_rounding=prec)
            nber_rounding_steps=int(abs(total_rounding_error/currency.rounding))
            rounding_error=round(nber_rounding_stepsandtotal_rounding_error/nber_rounding_stepsor0.0,precision_rounding=prec)

            forrepartition_line,line_amountinzip(tax_repartition_lines,repartition_line_amounts):

                ifnber_rounding_steps:
                    line_amount+=rounding_error
                    nber_rounding_steps-=1

                taxes_vals.append({
                    'id':tax.id,
                    'name':partnerandtax.with_context(lang=partner.lang).nameortax.name,
                    'amount':sign*line_amount,
                    'base':round(sign*base,precision_rounding=prec),
                    'sequence':tax.sequence,
                    'account_id':tax.cash_basis_transition_account_id.idiftax.tax_exigibility=='on_payment'\
                                                                             andnotself._context.get('caba_no_transition_account')\
                                                                          elserepartition_line.account_id.id,
                    'analytic':tax.analytic,
                    'price_include':price_include,
                    'tax_exigibility':tax.tax_exigibility,
                    'tax_repartition_line_id':repartition_line.id,
                    'group':groups_map.get(tax),
                    'tag_ids':(repartition_line.tag_ids+subsequent_tags).ids,
                    'tax_ids':subsequent_taxes.ids,
                })

                ifnotrepartition_line.account_id:
                    total_void+=line_amount

            #Affectsubsequenttaxes
            iftax.include_base_amount:
                base+=factorized_tax_amount
                ifnotprice_include:
                    skip_checkpoint=True

            total_included+=factorized_tax_amount
            i+=1

        return{
            'base_tags':taxes.mapped(is_refundand'refund_repartition_line_ids'or'invoice_repartition_line_ids').filtered(lambdax:x.repartition_type=='base').mapped('tag_ids').ids,
            'taxes':taxes_vals,
            'total_excluded':sign*total_excluded,
            'total_included':sign*currency.round(total_included),
            'total_void':sign*currency.round(total_void),
        }

    @api.model
    def_fix_tax_included_price(self,price,prod_taxes,line_taxes):
        """Subtracttaxamountfrompricewhencorresponding"priceincluded"taxesdonotapply"""
        #FIXMEgetcurrencyinparam?
        prod_taxes=prod_taxes._origin
        line_taxes=line_taxes._origin
        incl_tax=prod_taxes.filtered(lambdatax:taxnotinline_taxesandtax.price_include)
        ifincl_tax:
            returnincl_tax.compute_all(price)['total_excluded']
        returnprice

    @api.model
    def_fix_tax_included_price_company(self,price,prod_taxes,line_taxes,company_id):
        ifcompany_id:
            #Tokeepthesamebehaviorasin_compute_tax_id
            prod_taxes=prod_taxes.filtered(lambdatax:tax.company_id==company_id)
            line_taxes=line_taxes.filtered(lambdatax:tax.company_id==company_id)
        returnself._fix_tax_included_price(price,prod_taxes,line_taxes)


classAccountTaxRepartitionLine(models.Model):
    _name="account.tax.repartition.line"
    _description="TaxRepartitionLine"
    _order='sequence,repartition_type,id'
    _check_company_auto=True

    factor_percent=fields.Float(string="%",required=True,help="Factortoapplyontheaccountmovelinesgeneratedfromthisdistributionline,inpercents")
    factor=fields.Float(string="FactorRatio",compute="_compute_factor",help="Factortoapplyontheaccountmovelinesgeneratedfromthisdistributionline")
    repartition_type=fields.Selection(string="BasedOn",selection=[('base','Base'),('tax','oftax')],required=True,default='tax',help="Baseonwhichthefactorwillbeapplied.")
    account_id=fields.Many2one(string="Account",
        comodel_name='account.account',
        domain="[('deprecated','=',False),('company_id','=',company_id),('internal_type','notin',('receivable','payable'))]",
        check_company=True,
        help="Accountonwhichtopostthetaxamount")
    tag_ids=fields.Many2many(string="TaxGrids",comodel_name='account.account.tag',domain=[('applicability','=','taxes')],copy=True)
    invoice_tax_id=fields.Many2one(comodel_name='account.tax',
        ondelete='cascade',
        check_company=True,
        help="Thetaxsettoapplythisdistributiononinvoices.Mutuallyexclusivewithrefund_tax_id")
    refund_tax_id=fields.Many2one(comodel_name='account.tax',
        ondelete='cascade',
        check_company=True,
        help="Thetaxsettoapplythisdistributiononrefundinvoices.Mutuallyexclusivewithinvoice_tax_id")
    tax_id=fields.Many2one(comodel_name='account.tax',compute='_compute_tax_id')
    tax_fiscal_country_id=fields.Many2one(string="FiscalCountry",comodel_name='res.country',related='company_id.account_tax_fiscal_country_id',help="Technicalfieldusedtorestricttagsdomaininformview.")
    company_id=fields.Many2one(string="Company",comodel_name='res.company',compute="_compute_company",store=True,help="Thecompanythisdistributionlinebelongsto.")
    sequence=fields.Integer(string="Sequence",default=1,
        help="Theorderinwhichdistributionlinesaredisplayedandmatched.Forrefundstoworkproperly,invoicedistributionlinesshouldbearrangedinthesameorderasthecreditnotedistributionlinestheycorrespondto.")
    use_in_tax_closing=fields.Boolean(string="TaxClosingEntry")

    @api.onchange('account_id','repartition_type')
    def_on_change_account_id(self):
        ifnotself.account_idorself.repartition_type=='base':
            self.use_in_tax_closing=False
        else:
            self.use_in_tax_closing=self.account_id.internal_groupnotin('income','expense')

    @api.constrains('invoice_tax_id','refund_tax_id')
    defvalidate_tax_template_link(self):
        forrecordinself:
            ifrecord.invoice_tax_idandrecord.refund_tax_id:
                raiseValidationError(_("Taxdistributionlinesshouldapplytoeitherinvoicesorrefunds,notbothatthesametime.invoice_tax_idandrefund_tax_idshouldnotbesettogether."))

    @api.depends('factor_percent')
    def_compute_factor(self):
        forrecordinself:
            record.factor=record.factor_percent/100.0

    @api.depends('invoice_tax_id.company_id','refund_tax_id.company_id')
    def_compute_company(self):
        forrecordinself:
            record.company_id=record.invoice_tax_idandrecord.invoice_tax_id.company_id.idorrecord.refund_tax_id.company_id.id

    @api.depends('invoice_tax_id','refund_tax_id')
    def_compute_tax_id(self):
        forrecordinself:
            record.tax_id=record.invoice_tax_idorrecord.refund_tax_id

    @api.onchange('repartition_type')
    def_onchange_repartition_type(self):
        ifself.repartition_type=='base':
            self.account_id=None
