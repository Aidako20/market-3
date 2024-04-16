#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importtime
importlogging

frompsycopg2importsql,DatabaseError

fromflectraimportapi,fields,models,_
fromflectra.toolsimportDEFAULT_SERVER_DATETIME_FORMAT
fromflectra.exceptionsimportValidationError,UserError
fromflectra.addons.base.models.res_partnerimportWARNING_MESSAGE,WARNING_HELP

_logger=logging.getLogger(__name__)

classAccountFiscalPosition(models.Model):
    _name='account.fiscal.position'
    _description='FiscalPosition'
    _order='sequence'

    sequence=fields.Integer()
    name=fields.Char(string='FiscalPosition',required=True)
    active=fields.Boolean(default=True,
        help="Byuncheckingtheactivefield,youmayhideafiscalpositionwithoutdeletingit.")
    company_id=fields.Many2one(
        comodel_name='res.company',
        string='Company',required=True,readonly=True,
        default=lambdaself:self.env.company)
    account_ids=fields.One2many('account.fiscal.position.account','position_id',string='AccountMapping',copy=True)
    tax_ids=fields.One2many('account.fiscal.position.tax','position_id',string='TaxMapping',copy=True)
    note=fields.Text('Notes',translate=True,help="Legalmentionsthathavetobeprintedontheinvoices.")
    auto_apply=fields.Boolean(string='DetectAutomatically',help="Applyautomaticallythisfiscalposition.")
    vat_required=fields.Boolean(string='VATrequired',help="ApplyonlyifpartnerhasaVATnumber.")
    country_id=fields.Many2one('res.country',string='Country',
        help="Applyonlyifdeliverycountrymatches.")
    country_group_id=fields.Many2one('res.country.group',string='CountryGroup',
        help="Applyonlyifdeliverycountrymatchesthegroup.")
    state_ids=fields.Many2many('res.country.state',string='FederalStates')
    zip_from=fields.Char(string='ZipRangeFrom')
    zip_to=fields.Char(string='ZipRangeTo')
    #Tobeusedinhidingthe'FederalStates'field('attrs'inviewside)whenselected'Country'has0states.
    states_count=fields.Integer(compute='_compute_states_count')

    def_compute_states_count(self):
        forpositioninself:
            position.states_count=len(position.country_id.state_ids)

    @api.constrains('zip_from','zip_to')
    def_check_zip(self):
        forpositioninself:
            ifposition.zip_fromandposition.zip_toandposition.zip_from>position.zip_to:
                raiseValidationError(_('Invalid"ZipRange",pleaseconfigureitproperly.'))

    defmap_tax(self,taxes,product=None,partner=None):
        ifnotself:
            returntaxes
        tmap={
            g["tax_src_id"][0]:g["dest_ids"]
            forginself.env["account.fiscal.position.tax"].read_group(
                [
                    ("id","in",self.tax_ids.ids),
                    ("tax_src_id","in",[t._origin.idfortintaxesift._originandt._origin.id]),
                ],
                ["dest_ids:array_agg(tax_dest_id)"],
                groupby="tax_src_id",
            )
        }
        #getmappedtaxes,removeNonewhichmeansthemappingistono-tax
        result_ids=set().union(*tmap.values())-{None}
        #fortaxeswithoutmappingatall,eventono-tax,wethenkeepthetax
        result_ids.update(tax.idfortaxintaxesiftax._originandtax._origin.idnotintmap)
        returnself.env["account.tax"].browse(result_ids)

    defmap_account(self,account):
        forposinself.account_ids:
            ifpos.account_src_id==account:
                returnpos.account_dest_id
        returnaccount

    defmap_accounts(self,accounts):
        """Receiveadictionaryhavingaccountsinvaluesandtrytoreplacethoseaccountsaccordinglytothefiscalposition.
        """
        ref_dict={}
        forlineinself.account_ids:
            ref_dict[line.account_src_id]=line.account_dest_id
        forkey,accinaccounts.items():
            ifaccinref_dict:
                accounts[key]=ref_dict[acc]
        returnaccounts

    @api.onchange('country_id')
    def_onchange_country_id(self):
        ifself.country_id:
            self.zip_from=self.zip_to=self.country_group_id=False
            self.state_ids=[(5,)]
            self.states_count=len(self.country_id.state_ids)

    @api.onchange('country_group_id')
    def_onchange_country_group_id(self):
        ifself.country_group_id:
            self.zip_from=self.zip_to=self.country_id=False
            self.state_ids=[(5,)]

    @api.model
    def_convert_zip_values(self,zip_from='',zip_to=''):
        max_length=max(len(zip_from),len(zip_to))
        ifzip_from.isdigit():
            zip_from=zip_from.rjust(max_length,'0')
        ifzip_to.isdigit():
            zip_to=zip_to.rjust(max_length,'0')
        returnzip_from,zip_to

    @api.model
    defcreate(self,vals):
        zip_from=vals.get('zip_from')
        zip_to=vals.get('zip_to')
        ifzip_fromandzip_to:
            vals['zip_from'],vals['zip_to']=self._convert_zip_values(zip_from,zip_to)
        returnsuper(AccountFiscalPosition,self).create(vals)

    defwrite(self,vals):
        zip_from=vals.get('zip_from')
        zip_to=vals.get('zip_to')
        ifzip_fromorzip_to:
            forrecinself:
                vals['zip_from'],vals['zip_to']=self._convert_zip_values(zip_fromorrec.zip_from,zip_toorrec.zip_to)
        returnsuper(AccountFiscalPosition,self).write(vals)

    @api.model
    def_get_fpos_by_region(self,country_id=False,state_id=False,zipcode=False,vat_required=False):
        ifnotcountry_id:
            returnFalse
        base_domain=[
            ('auto_apply','=',True),
            ('vat_required','=',vat_required),
            ('company_id','in',[self.env.company.id,False]),
        ]
        null_state_dom=state_domain=[('state_ids','=',False)]
        null_zip_dom=zip_domain=[('zip_from','=',False),('zip_to','=',False)]
        null_country_dom=[('country_id','=',False),('country_group_id','=',False)]

        ifzipcode:
            zip_domain=[('zip_from','<=',zipcode),('zip_to','>=',zipcode)]

        ifstate_id:
            state_domain=[('state_ids','=',state_id)]

        domain_country=base_domain+[('country_id','=',country_id)]
        domain_group=base_domain+[('country_group_id.country_ids','=',country_id)]

        #Builddomaintosearchrecordswithexactmatchingcriteria
        fpos=self.search(domain_country+state_domain+zip_domain,limit=1)
        #returnrecordsthatfitthemostthecriteria,andfallbackonlessspecificfiscalpositionsifanycanbefound
        ifnotfposandstate_id:
            fpos=self.search(domain_country+null_state_dom+zip_domain,limit=1)
        ifnotfposandzipcode:
            fpos=self.search(domain_country+state_domain+null_zip_dom,limit=1)
        ifnotfposandstate_idandzipcode:
            fpos=self.search(domain_country+null_state_dom+null_zip_dom,limit=1)

        #fallback:countrygroupwithnostate/ziprange
        ifnotfpos:
            fpos=self.search(domain_group+null_state_dom+null_zip_dom,limit=1)

        ifnotfpos:
            #Fallbackoncatchall(nocountry,nogroup)
            fpos=self.search(base_domain+null_country_dom,limit=1)
        returnfpos

    @api.model
    defget_fiscal_position(self,partner_id,delivery_id=None):
        """
        :return:fiscalpositionfound(recordset)
        :rtype::class:`account.fiscal.position`
        """
        ifnotpartner_id:
            returnself.env['account.fiscal.position']

        #Thiscanbeeasilyoverriddentoapplymorecomplexfiscalrules
        PartnerObj=self.env['res.partner']
        partner=PartnerObj.browse(partner_id)
        delivery=PartnerObj.browse(delivery_id)

        company=self.env.company
        eu_country_codes=set(self.env.ref('base.europe').country_ids.mapped('code'))
        intra_eu=vat_exclusion=False
        ifcompany.vatandpartner.vat:
            intra_eu=company.vat[:2]ineu_country_codesandpartner.vat[:2]ineu_country_codes
            vat_exclusion=company.vat[:2]==partner.vat[:2]

        #Ifcompanyandpartnerhavethesamevatprefix(andarebothwithintheEU),useinvoicing
        ifnotdeliveryor(intra_euandvat_exclusion):
            delivery=partner

        #partnermanuallysetfiscalpositionalwayswin
        ifdelivery.property_account_position_idorpartner.property_account_position_id:
            returndelivery.property_account_position_idorpartner.property_account_position_id

        #FirstsearchonlymatchingVATpositions
        vat_required=bool(partner.vat)
        fp=self._get_fpos_by_region(delivery.country_id.id,delivery.state_id.id,delivery.zip,vat_required)

        #ThenifVATrequiredfoundnomatch,trypositionsthatdonotrequireit
        ifnotfpandvat_required:
            fp=self._get_fpos_by_region(delivery.country_id.id,delivery.state_id.id,delivery.zip,False)

        returnfporself.env['account.fiscal.position']


classAccountFiscalPositionTax(models.Model):
    _name='account.fiscal.position.tax'
    _description='TaxMappingofFiscalPosition'
    _rec_name='position_id'
    _check_company_auto=True

    position_id=fields.Many2one('account.fiscal.position',string='FiscalPosition',
        required=True,ondelete='cascade')
    company_id=fields.Many2one('res.company',string='Company',related='position_id.company_id',store=True)
    tax_src_id=fields.Many2one('account.tax',string='TaxonProduct',required=True,check_company=True)
    tax_dest_id=fields.Many2one('account.tax',string='TaxtoApply',check_company=True)

    _sql_constraints=[
        ('tax_src_dest_uniq',
         'unique(position_id,tax_src_id,tax_dest_id)',
         'Ataxfiscalpositioncouldbedefinedonlyonetimeonsametaxes.')
    ]


classAccountFiscalPositionAccount(models.Model):
    _name='account.fiscal.position.account'
    _description='AccountsMappingofFiscalPosition'
    _rec_name='position_id'
    _check_company_auto=True

    position_id=fields.Many2one('account.fiscal.position',string='FiscalPosition',
        required=True,ondelete='cascade')
    company_id=fields.Many2one('res.company',string='Company',related='position_id.company_id',store=True)
    account_src_id=fields.Many2one('account.account',string='AccountonProduct',
        check_company=True,required=True,
        domain="[('deprecated','=',False),('company_id','=',company_id)]")
    account_dest_id=fields.Many2one('account.account',string='AccounttoUseInstead',
        check_company=True,required=True,
        domain="[('deprecated','=',False),('company_id','=',company_id)]")

    _sql_constraints=[
        ('account_src_dest_uniq',
         'unique(position_id,account_src_id,account_dest_id)',
         'Anaccountfiscalpositioncouldbedefinedonlyonetimeonsameaccounts.')
    ]


classResPartner(models.Model):
    _name='res.partner'
    _inherit='res.partner'

    @api.depends_context('company')
    def_credit_debit_get(self):
        tables,where_clause,where_params=self.env['account.move.line'].with_context(state='posted',company_id=self.env.company.id)._query_get()
        where_params=[tuple(self.ids)]+where_params
        ifwhere_clause:
            where_clause='AND'+where_clause
        self._cr.execute("""SELECTaccount_move_line.partner_id,act.type,SUM(account_move_line.amount_residual)
                      FROM"""+tables+"""
                      LEFTJOINaccount_accountaON(account_move_line.account_id=a.id)
                      LEFTJOINaccount_account_typeactON(a.user_type_id=act.id)
                      WHEREact.typeIN('receivable','payable')
                      ANDaccount_move_line.partner_idIN%s
                      ANDaccount_move_line.reconciledISNOTTRUE
                      """+where_clause+"""
                      GROUPBYaccount_move_line.partner_id,act.type
                      """,where_params)
        treated=self.browse()
        forpid,type,valinself._cr.fetchall():
            partner=self.browse(pid)
            iftype=='receivable':
                partner.credit=val
                ifpartnernotintreated:
                    partner.debit=False
                    treated|=partner
            eliftype=='payable':
                partner.debit=-val
                ifpartnernotintreated:
                    partner.credit=False
                    treated|=partner
        remaining=(self-treated)
        remaining.debit=False
        remaining.credit=False

    def_asset_difference_search(self,account_type,operator,operand):
        ifoperatornotin('<','=','>','>=','<='):
            return[]
        ifnotisinstance(operand,(float,int)):
            return[]
        sign=1
        ifaccount_type=='payable':
            sign=-1
        res=self._cr.execute('''
            SELECTpartner.id
            FROMres_partnerpartner
            LEFTJOINaccount_move_lineamlONaml.partner_id=partner.id
            JOINaccount_movemoveONmove.id=aml.move_id
            RIGHTJOINaccount_accountaccONaml.account_id=acc.id
            WHEREacc.internal_type=%s
              ANDNOTacc.deprecatedANDacc.company_id=%s
              ANDmove.state='posted'
            GROUPBYpartner.id
            HAVING%s*COALESCE(SUM(aml.amount_residual),0)'''+operator+'''%s''',(account_type,self.env.company.id,sign,operand))
        res=self._cr.fetchall()
        ifnotres:
            return[('id','=','0')]
        return[('id','in',[r[0]forrinres])]

    @api.model
    def_credit_search(self,operator,operand):
        returnself._asset_difference_search('receivable',operator,operand)

    @api.model
    def_debit_search(self,operator,operand):
        returnself._asset_difference_search('payable',operator,operand)

    def_invoice_total(self):
        self.total_invoiced=0
        ifnotself.ids:
            returnTrue

        all_partners_and_children={}
        all_partner_ids=[]
        forpartnerinself.filtered('id'):
            #price_totalisinthecompanycurrency
            all_partners_and_children[partner]=self.with_context(active_test=False).search([('id','child_of',partner.id)]).ids
            all_partner_ids+=all_partners_and_children[partner]

        domain=[
            ('partner_id','in',all_partner_ids),
            ('state','notin',['draft','cancel']),
            ('move_type','in',('out_invoice','out_refund')),
        ]
        price_totals=self.env['account.invoice.report'].read_group(domain,['price_subtotal'],['partner_id'])
        forpartner,child_idsinall_partners_and_children.items():
            partner.total_invoiced=sum(price['price_subtotal']forpriceinprice_totalsifprice['partner_id'][0]inchild_ids)

    def_compute_journal_item_count(self):
        AccountMoveLine=self.env['account.move.line']
        forpartnerinself:
            partner.journal_item_count=AccountMoveLine.search_count([('partner_id','=',partner.id)])

    def_compute_has_unreconciled_entries(self):
        forpartnerinself:
            #Avoiduselessworkifhas_unreconciled_entriesisnotrelevantforthispartner
            ifnotpartner.activeornotpartner.is_companyandpartner.parent_id:
                partner.has_unreconciled_entries=False
                continue
            self.env.cr.execute(
                """SELECT1FROM(
                        SELECT
                            p.last_time_entries_checkedASlast_time_entries_checked,
                            MAX(l.write_date)ASmax_date
                        FROM
                            account_move_linel
                            RIGHTJOINaccount_accountaON(a.id=l.account_id)
                            RIGHTJOINres_partnerpON(l.partner_id=p.id)
                        WHERE
                            p.id=%s
                            ANDEXISTS(
                                SELECT1
                                FROMaccount_move_linel
                                WHEREl.account_id=a.id
                                ANDl.partner_id=p.id
                                ANDl.amount_residual>0
                            )
                            ANDEXISTS(
                                SELECT1
                                FROMaccount_move_linel
                                WHEREl.account_id=a.id
                                ANDl.partner_id=p.id
                                ANDl.amount_residual<0
                            )
                        GROUPBYp.last_time_entries_checked
                    )ass
                    WHERE(last_time_entries_checkedISNULLORmax_date>last_time_entries_checked)
                """,(partner.id,))
            partner.has_unreconciled_entries=self.env.cr.rowcount==1

    defmark_as_reconciled(self):
        self.env['account.partial.reconcile'].check_access_rights('write')
        returnself.sudo().write({'last_time_entries_checked':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

    def_get_company_currency(self):
        forpartnerinself:
            ifpartner.company_id:
                partner.currency_id=partner.sudo().company_id.currency_id
            else:
                partner.currency_id=self.env.company.currency_id

    credit=fields.Monetary(compute='_credit_debit_get',search=_credit_search,
        string='TotalReceivable',help="Totalamountthiscustomerowesyou.")
    debit=fields.Monetary(compute='_credit_debit_get',search=_debit_search,string='TotalPayable',
        help="Totalamountyouhavetopaytothisvendor.")
    debit_limit=fields.Monetary('PayableLimit')
    total_invoiced=fields.Monetary(compute='_invoice_total',string="TotalInvoiced",
        groups='account.group_account_invoice,account.group_account_readonly')
    currency_id=fields.Many2one('res.currency',compute='_get_company_currency',readonly=True,
        string="Currency",help='Utilityfieldtoexpressamountcurrency')
    journal_item_count=fields.Integer(compute='_compute_journal_item_count',string="JournalItems")
    property_account_payable_id=fields.Many2one('account.account',company_dependent=True,
        string="AccountPayable",
        domain="[('internal_type','=','payable'),('deprecated','=',False),('company_id','=',current_company_id)]",
        help="Thisaccountwillbeusedinsteadofthedefaultoneasthepayableaccountforthecurrentpartner",
        required=True)
    property_account_receivable_id=fields.Many2one('account.account',company_dependent=True,
        string="AccountReceivable",
        domain="[('internal_type','=','receivable'),('deprecated','=',False),('company_id','=',current_company_id)]",
        help="Thisaccountwillbeusedinsteadofthedefaultoneasthereceivableaccountforthecurrentpartner",
        required=True)
    property_account_position_id=fields.Many2one('account.fiscal.position',company_dependent=True,
        string="FiscalPosition",
        domain="[('company_id','=',current_company_id)]",
        help="Thefiscalpositiondeterminesthetaxes/accountsusedforthiscontact.")
    property_payment_term_id=fields.Many2one('account.payment.term',company_dependent=True,
        string='CustomerPaymentTerms',
        domain="[('company_id','in',[current_company_id,False])]",
        help="Thispaymenttermwillbeusedinsteadofthedefaultoneforsalesordersandcustomerinvoices")
    property_supplier_payment_term_id=fields.Many2one('account.payment.term',company_dependent=True,
        string='VendorPaymentTerms',
        domain="[('company_id','in',[current_company_id,False])]",
        help="Thispaymenttermwillbeusedinsteadofthedefaultoneforpurchaseordersandvendorbills")
    ref_company_ids=fields.One2many('res.company','partner_id',
        string='Companiesthatreferstopartner')
    has_unreconciled_entries=fields.Boolean(compute='_compute_has_unreconciled_entries',
        help="Thepartnerhasatleastoneunreconcileddebitandcreditsincelasttimetheinvoices&paymentsmatchingwasperformed.")
    last_time_entries_checked=fields.Datetime(
        string='LatestInvoices&PaymentsMatchingDate',readonly=True,copy=False,
        help='Lasttimetheinvoices&paymentsmatchingwasperformedforthispartner.'
             'Itisseteitherifthere\'snotatleastanunreconcileddebitandanunreconciledcredit'
             'orifyouclickthe"Done"button.')
    invoice_ids=fields.One2many('account.move','partner_id',string='Invoices',readonly=True,copy=False)
    contract_ids=fields.One2many('account.analytic.account','partner_id',string='PartnerContracts',readonly=True)
    bank_account_count=fields.Integer(compute='_compute_bank_count',string="Bank")
    trust=fields.Selection([('good','GoodDebtor'),('normal','NormalDebtor'),('bad','BadDebtor')],string='Degreeoftrustyouhaveinthisdebtor',default='normal',company_dependent=True)
    invoice_warn=fields.Selection(WARNING_MESSAGE,'Invoice',help=WARNING_HELP,default="no-message")
    invoice_warn_msg=fields.Text('MessageforInvoice')
    #Computedfieldstoorderthepartnersassuppliers/customersaccordingtothe
    #amountoftheirgeneratedincoming/outgoingaccountmoves
    supplier_rank=fields.Integer(default=0,copy=False)
    customer_rank=fields.Integer(default=0,copy=False)

    def_get_name_search_order_by_fields(self):
        res=super()._get_name_search_order_by_fields()
        partner_search_mode=self.env.context.get('res_partner_search_mode')
        ifnotpartner_search_modein('customer','supplier'):
            returnres
        order_by_field='COALESCE(res_partner.%s,0)DESC,'
        ifpartner_search_mode=='customer':
            field='customer_rank'
        else:
            field='supplier_rank'

        order_by_field=order_by_field%field
        return'%s,%s'%(res,order_by_field%field)ifreselseorder_by_field

    def_compute_bank_count(self):
        bank_data=self.env['res.partner.bank'].read_group([('partner_id','in',self.ids)],['partner_id'],['partner_id'])
        mapped_data=dict([(bank['partner_id'][0],bank['partner_id_count'])forbankinbank_data])
        forpartnerinself:
            partner.bank_account_count=mapped_data.get(partner.id,0)

    def_find_accounting_partner(self,partner):
        '''Findthepartnerforwhichtheaccountingentrieswillbecreated'''
        returnpartner.commercial_partner_id

    @api.model
    def_commercial_fields(self):
        returnsuper(ResPartner,self)._commercial_fields()+\
            ['debit_limit','property_account_payable_id','property_account_receivable_id','property_account_position_id',
             'property_payment_term_id','property_supplier_payment_term_id','last_time_entries_checked']

    defaction_view_partner_invoices(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        all_child=self.with_context(active_test=False).search([('id','child_of',self.ids)])
        action['domain']=[
            ('move_type','in',('out_invoice','out_refund')),
            ('partner_id','in',all_child.ids)
        ]
        action['context']={'default_move_type':'out_invoice','move_type':'out_invoice','journal_type':'sale','search_default_unpaid':1}
        returnaction

    defcan_edit_vat(self):
        '''Can'tedit`vat`ifthereis(nondraft)issuedinvoices.'''
        can_edit_vat=super(ResPartner,self).can_edit_vat()
        ifnotcan_edit_vat:
            returncan_edit_vat
        has_invoice=self.env['account.move'].search([
            ('move_type','in',['out_invoice','out_refund']),
            ('partner_id','child_of',self.commercial_partner_id.id),
            ('state','=','posted')
        ],limit=1)
        returncan_edit_vatandnot(bool(has_invoice))

    @api.model_create_multi
    defcreate(self,vals_list):
        search_partner_mode=self.env.context.get('res_partner_search_mode')
        is_customer=search_partner_mode=='customer'
        is_supplier=search_partner_mode=='supplier'
        ifsearch_partner_mode:
            forvalsinvals_list:
                ifis_customerand'customer_rank'notinvals:
                    vals['customer_rank']=1
                elifis_supplierand'supplier_rank'notinvals:
                    vals['supplier_rank']=1
        returnsuper().create(vals_list)

    defunlink(self):
        """
        Preventthedeletionofapartner"Individual",childofacompanyif:
        -partnerin'account.move'
        -state:allstates(draftandposted)
        """
        moves=self.sudo().env['account.move'].search_count([('partner_id','in',self.ids),('state','in',['draft','posted'])])
        ifmoves:
            raiseUserError(_("Recordcannotbedeleted.PartnerusedinAccounting"))
        returnsuper(ResPartner,self).unlink()

    def_increase_rank(self,field,n=1):
        ifself.idsandfieldin['customer_rank','supplier_rank']:
            try:
                withself.env.cr.savepoint(flush=False):
                    query=sql.SQL("""
                        SELECT{field}FROMres_partnerWHEREIDIN%(partner_ids)sFORUPDATENOWAIT;
                        UPDATEres_partnerSET{field}={field}+%(n)s
                        WHEREidIN%(partner_ids)s
                    """).format(field=sql.Identifier(field))
                    self.env.cr.execute(query,{'partner_ids':tuple(self.ids),'n':n})
                    forpartnerinself:
                        self.env.cache.remove(partner,partner._fields[field])
            exceptDatabaseErrorase:
                ife.pgcode=='55P03':
                    _logger.debug('Anothertransactionalreadylockedpartnerrows.Cannotupdatepartnerranks.')
                else:
                    raisee
