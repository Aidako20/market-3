#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
fromuuidimportuuid4
importpytz

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportAccessError,ValidationError,UserError


classAccountBankStmtCashWizard(models.Model):
    _inherit='account.bank.statement.cashbox'

    @api.depends('pos_config_ids')
    @api.depends_context('current_currency_id')
    def_compute_currency(self):
        super(AccountBankStmtCashWizard,self)._compute_currency()
        forcashboxinself:
            ifcashbox.pos_config_ids:
                cashbox.currency_id=cashbox.pos_config_ids[0].currency_id.id
            elifself.env.context.get('current_currency_id'):
                cashbox.currency_id=self.env.context.get('current_currency_id')

    pos_config_ids=fields.One2many('pos.config','default_cashbox_id')
    is_a_template=fields.Boolean(default=False)

    @api.model
    defdefault_get(self,fields):
        vals=super(AccountBankStmtCashWizard,self).default_get(fields)
        if'cashbox_lines_ids'notinfields:
            returnvals
        config_id=self.env.context.get('default_pos_id')
        ifconfig_id:
            config=self.env['pos.config'].browse(config_id)
            ifconfig.last_session_closing_cashbox.cashbox_lines_ids:
                lines=config.last_session_closing_cashbox.cashbox_lines_ids
            else:
                lines=config.default_cashbox_id.cashbox_lines_ids
            ifself.env.context.get('balance',False)=='start':
                vals['cashbox_lines_ids']=[[0,0,{'coin_value':line.coin_value,'number':line.number,'subtotal':line.subtotal}]forlineinlines]
            else:
                vals['cashbox_lines_ids']=[[0,0,{'coin_value':line.coin_value,'number':0,'subtotal':0.0}]forlineinlines]
        returnvals

    def_validate_cashbox(self):
        super(AccountBankStmtCashWizard,self)._validate_cashbox()
        session_id=self.env.context.get('pos_session_id')
        ifsession_id:
            current_session=self.env['pos.session'].browse(session_id)
            ifcurrent_session.state=='new_session':
                current_session.write({'state':'opening_control'})

    defset_default_cashbox(self):
        self.ensure_one()
        current_session=self.env['pos.session'].browse(self.env.context['pos_session_id'])
        lines=current_session.config_id.default_cashbox_id.cashbox_lines_ids
        context=dict(self._context)
        self.cashbox_lines_ids.unlink()
        self.cashbox_lines_ids=[[0,0,{'coin_value':line.coin_value,'number':line.number,'subtotal':line.subtotal}]forlineinlines]

        return{
            'name':_('CashControl'),
            'view_type':'form',
            'view_mode':'form',
            'res_model':'account.bank.statement.cashbox',
            'view_id':self.env.ref('point_of_sale.view_account_bnk_stmt_cashbox_footer').id,
            'type':'ir.actions.act_window',
            'context':context,
            'target':'new',
            'res_id':self.id,
        }


classPosConfig(models.Model):
    _name='pos.config'
    _description='PointofSaleConfiguration'

    def_default_picking_type_id(self):
        returnself.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1).pos_type_id.id

    def_default_sale_journal(self):
        returnself.env['account.journal'].search([('type','=','sale'),('company_id','=',self.env.company.id),('code','=','POSS')],limit=1)

    def_default_invoice_journal(self):
        returnself.env['account.journal'].search([('type','=','sale'),('company_id','=',self.env.company.id)],limit=1)

    def_default_payment_methods(self):
        returnself.env['pos.payment.method'].search([('split_transactions','=',False),('company_id','=',self.env.company.id)])

    def_default_pricelist(self):
        returnself.env['product.pricelist'].search([('company_id','in',(False,self.env.company.id)),('currency_id','=',self.env.company.currency_id.id)],limit=1)

    def_get_group_pos_manager(self):
        returnself.env.ref('point_of_sale.group_pos_manager')

    def_get_group_pos_user(self):
        returnself.env.ref('point_of_sale.group_pos_user')

    def_compute_customer_html(self):
        forconfiginself:
            config.customer_facing_display_html=self.env['ir.qweb']._render('point_of_sale.customer_facing_display_html',{'company':self.company_id})

    name=fields.Char(string='PointofSale',index=True,required=True,help="Aninternalidentificationofthepointofsale.")
    is_installed_account_accountant=fields.Boolean(string="IstheFullAccountingInstalled",
        compute="_compute_is_installed_account_accountant")
    picking_type_id=fields.Many2one(
        'stock.picking.type',
        string='OperationType',
        default=_default_picking_type_id,
        required=True,
        domain="[('code','=','outgoing'),('warehouse_id.company_id','=',company_id)]",
        ondelete='restrict')
    journal_id=fields.Many2one(
        'account.journal',string='SalesJournal',
        domain=[('type','=','sale')],
        help="Accountingjournalusedtopostsalesentries.",
        default=_default_sale_journal,
        ondelete='restrict')
    invoice_journal_id=fields.Many2one(
        'account.journal',string='InvoiceJournal',
        domain=[('type','=','sale')],
        help="Accountingjournalusedtocreateinvoices.",
        default=_default_invoice_journal)
    currency_id=fields.Many2one('res.currency',compute='_compute_currency',string="Currency")
    iface_cashdrawer=fields.Boolean(string='Cashdrawer',help="Automaticallyopenthecashdrawer.")
    iface_electronic_scale=fields.Boolean(string='ElectronicScale',help="EnablesElectronicScaleintegration.")
    iface_vkeyboard=fields.Boolean(string='VirtualKeyBoard',help=u"Don’tturnthisoptiononifyoutakeordersonsmartphonesortablets.\nSuchdevicesalreadybenefitfromanativekeyboard.")
    iface_customer_facing_display=fields.Boolean(string='CustomerFacingDisplay',help="Showcheckouttocustomerswitharemotely-connectedscreen.")
    iface_print_via_proxy=fields.Boolean(string='PrintviaProxy',help="Bypassbrowserprintingandprintsviathehardwareproxy.")
    iface_scan_via_proxy=fields.Boolean(string='ScanviaProxy',help="EnablebarcodescanningwitharemotelyconnectedbarcodescannerandcardswipingwithaVantivcardreader.")
    iface_big_scrollbars=fields.Boolean('LargeScrollbars',help='Forimpreciseindustrialtouchscreens.')
    iface_print_auto=fields.Boolean(string='AutomaticReceiptPrinting',default=False,
        help='Thereceiptwillautomaticallybeprintedattheendofeachorder.')
    iface_print_skip_screen=fields.Boolean(string='SkipPreviewScreen',default=True,
        help='Thereceiptscreenwillbeskippedifthereceiptcanbeprintedautomatically.')
    iface_tax_included=fields.Selection([('subtotal','Tax-ExcludedPrice'),('total','Tax-IncludedPrice')],string="TaxDisplay",default='subtotal',required=True)
    iface_start_categ_id=fields.Many2one('pos.category',string='InitialCategory',
        help='Thepointofsalewilldisplaythisproductcategorybydefault.Ifnocategoryisspecified,allavailableproductswillbeshown.')
    iface_available_categ_ids=fields.Many2many('pos.category',string='AvailablePoSProductCategories',
        help='Thepointofsalewillonlydisplayproductswhicharewithinoneoftheselectedcategorytrees.Ifnocategoryisspecified,allavailableproductswillbeshown')
    selectable_categ_ids=fields.Many2many('pos.category',compute='_compute_selectable_categories')
    iface_display_categ_images=fields.Boolean(string='DisplayCategoryPictures',
        help="Theproductcategorieswillbedisplayedwithpictures.")
    restrict_price_control=fields.Boolean(string='RestrictPriceModificationstoManagers',
        help="OnlyuserswithManageraccessrightsforPoSappcanmodifytheproductpricesonorders.")
    cash_control=fields.Boolean(string='AdvancedCashControl',help="Checktheamountofthecashboxatopeningandclosing.")
    receipt_header=fields.Text(string='ReceiptHeader',help="Ashorttextthatwillbeinsertedasaheaderintheprintedreceipt.")
    receipt_footer=fields.Text(string='ReceiptFooter',help="Ashorttextthatwillbeinsertedasafooterintheprintedreceipt.")
    proxy_ip=fields.Char(string='IPAddress',size=45,
        help='Thehostnameoripaddressofthehardwareproxy,Willbeautodetectedifleftempty.')
    active=fields.Boolean(default=True)
    uuid=fields.Char(readonly=True,default=lambdaself:str(uuid4()),copy=False,
        help='Agloballyuniqueidentifierforthisposconfiguration,usedtopreventconflictsinclient-generateddata.')
    sequence_id=fields.Many2one('ir.sequence',string='OrderIDsSequence',readonly=True,
        help="ThissequenceisautomaticallycreatedbyFlectrabutyoucanchangeit"
        "tocustomizethereferencenumbersofyourorders.",copy=False,ondelete='restrict')
    sequence_line_id=fields.Many2one('ir.sequence',string='OrderLineIDsSequence',readonly=True,
        help="ThissequenceisautomaticallycreatedbyFlectrabutyoucanchangeit"
        "tocustomizethereferencenumbersofyourorderslines.",copy=False)
    session_ids=fields.One2many('pos.session','config_id',string='Sessions')
    current_session_id=fields.Many2one('pos.session',compute='_compute_current_session',string="CurrentSession")
    current_session_state=fields.Char(compute='_compute_current_session')
    last_session_closing_cash=fields.Float(compute='_compute_last_session')
    last_session_closing_date=fields.Date(compute='_compute_last_session')
    last_session_closing_cashbox=fields.Many2one('account.bank.statement.cashbox',compute='_compute_last_session')
    pos_session_username=fields.Char(compute='_compute_current_session_user')
    pos_session_state=fields.Char(compute='_compute_current_session_user')
    pos_session_duration=fields.Char(compute='_compute_current_session_user')
    pricelist_id=fields.Many2one('product.pricelist',string='DefaultPricelist',required=True,default=_default_pricelist,
        help="ThepricelistusedifnocustomerisselectedorifthecustomerhasnoSalePricelistconfigured.")
    available_pricelist_ids=fields.Many2many('product.pricelist',string='AvailablePricelists',default=_default_pricelist,
        help="MakeseveralpricelistsavailableinthePointofSale.Youcanalsoapplyapricelisttospecificcustomersfromtheircontactform(inSalestab).Tobevalid,thispricelistmustbelistedhereasanavailablepricelist.Otherwisethedefaultpricelistwillapply.")
    allowed_pricelist_ids=fields.Many2many(
        'product.pricelist',
        string='AllowedPricelists',
        compute='_compute_allowed_pricelist_ids',
        help='Thisisatechnicalfieldusedforthedomainofpricelist_id.',
    )
    company_id=fields.Many2one('res.company',string='Company',required=True,default=lambdaself:self.env.company)
    barcode_nomenclature_id=fields.Many2one('barcode.nomenclature',string='BarcodeNomenclature',
        help='Defineswhatkindofbarcodesareavailableandhowtheyareassignedtoproducts,customersandcashiers.',
        default=lambdaself:self.env.company.nomenclature_id,required=True)
    group_pos_manager_id=fields.Many2one('res.groups',string='PointofSaleManagerGroup',default=_get_group_pos_manager,
        help='Thisfieldistheretopasstheidoftheposmanagergrouptothepointofsaleclient.')
    group_pos_user_id=fields.Many2one('res.groups',string='PointofSaleUserGroup',default=_get_group_pos_user,
        help='Thisfieldistheretopasstheidoftheposusergrouptothepointofsaleclient.')
    iface_tipproduct=fields.Boolean(string="Producttips")
    tip_product_id=fields.Many2one('product.product',string='TipProduct',
        help="Thisproductisusedasreferenceoncustomerreceipts.")
    fiscal_position_ids=fields.Many2many('account.fiscal.position',string='FiscalPositions',help='Thisisusefulforrestaurantswithonsiteandtake-awayservicesthatimplyspecifictaxrates.')
    default_fiscal_position_id=fields.Many2one('account.fiscal.position',string='DefaultFiscalPosition')
    default_cashbox_id=fields.Many2one('account.bank.statement.cashbox',string='DefaultBalance')
    customer_facing_display_html=fields.Html(string='Customerfacingdisplaycontent',translate=True,compute=_compute_customer_html)
    use_pricelist=fields.Boolean("Useapricelist.")
    tax_regime=fields.Boolean("TaxRegime")
    tax_regime_selection=fields.Boolean("TaxRegimeSelectionvalue")
    start_category=fields.Boolean("StartCategory",default=False)
    limit_categories=fields.Boolean("RestrictProductCategories")
    module_account=fields.Boolean(string='Invoicing',default=True,help='EnablesinvoicegenerationfromthePointofSale.')
    module_pos_restaurant=fields.Boolean("IsaBar/Restaurant")
    module_pos_discount=fields.Boolean("GlobalDiscounts")
    module_pos_loyalty=fields.Boolean("LoyaltyProgram")
    module_pos_mercury=fields.Boolean(string="IntegratedCardPayments")
    manage_orders=fields.Boolean(string="ManageOrders")
    product_configurator=fields.Boolean(string="ProductConfigurator")
    is_posbox=fields.Boolean("PosBox")
    is_header_or_footer=fields.Boolean("Header&Footer")
    module_pos_hr=fields.Boolean(help="Showemployeeloginscreen")
    amount_authorized_diff=fields.Float('AmountAuthorizedDifference',
        help="Thisfielddepictsthemaximumdifferenceallowedbetweentheendingbalanceandthetheoreticalcashwhen"
             "closingasession,fornon-POSmanagers.Ifthismaximumisreached,theuserwillhaveanerrormessageat"
             "theclosingofhissessionsayingthatheneedstocontacthismanager.")
    payment_method_ids=fields.Many2many('pos.payment.method',string='PaymentMethods',default=lambdaself:self._default_payment_methods())
    company_has_template=fields.Boolean(string="Companyhaschartofaccounts",compute="_compute_company_has_template")
    current_user_id=fields.Many2one('res.users',string='CurrentSessionResponsible',compute='_compute_current_session_user')
    other_devices=fields.Boolean(string="OtherDevices",help="ConnectdevicestoyourPoSwithoutanIoTBox.")
    rounding_method=fields.Many2one('account.cash.rounding',string="Cashrounding")
    cash_rounding=fields.Boolean(string="CashRounding")
    only_round_cash_method=fields.Boolean(string="Onlyapplyroundingoncash")
    has_active_session=fields.Boolean(compute='_compute_current_session')
    show_allow_invoicing_alert=fields.Boolean(compute="_compute_show_allow_invoicing_alert")
    manual_discount=fields.Boolean(string="ManualDiscounts",default=True)

    @api.depends('use_pricelist','available_pricelist_ids')
    def_compute_allowed_pricelist_ids(self):
        forconfiginself:
            ifconfig.use_pricelist:
                config.allowed_pricelist_ids=config.available_pricelist_ids.ids
            else:
                config.allowed_pricelist_ids=self.env['product.pricelist'].search([]).ids

    @api.depends('company_id')
    def_compute_company_has_template(self):
        forconfiginself:
            config.company_has_template=self.env['account.chart.template'].existing_accounting(config.company_id)orconfig.company_id.chart_template_id

    def_compute_is_installed_account_accountant(self):
        account_accountant=self.env['ir.module.module'].sudo().search([('name','=','account_accountant'),('state','=','installed')])
        forpos_configinself:
            pos_config.is_installed_account_accountant=account_accountantandaccount_accountant.id

    @api.depends('journal_id.currency_id','journal_id.company_id.currency_id','company_id','company_id.currency_id')
    def_compute_currency(self):
        forpos_configinself:
            ifpos_config.journal_id:
                pos_config.currency_id=pos_config.journal_id.currency_id.idorpos_config.journal_id.company_id.currency_id.id
            else:
                pos_config.currency_id=pos_config.company_id.currency_id.id

    @api.depends('session_ids','session_ids.state')
    def_compute_current_session(self):
        """Ifthereisanopensession,storeittocurrent_session_id/current_session_State.
        """
        forpos_configinself:
            opened_sessions=pos_config.session_ids.filtered(lambdas:nots.state=='closed')
            session=pos_config.session_ids.filtered(lambdas:s.user_id.id==self.env.uidand\
                    nots.state=='closed'andnots.rescue)
            #sessionsorderedbyiddesc
            pos_config.has_active_session=opened_sessionsandTrueorFalse
            pos_config.current_session_id=sessionandsession[0].idorFalse
            pos_config.current_session_state=sessionandsession[0].stateorFalse

    @api.depends('module_account','manage_orders')
    def_compute_show_allow_invoicing_alert(self):
        forpos_configinself:
            ifnotpos_config.manage_orders:
                pos_config.show_allow_invoicing_alert=False
            else:
                pos_config.show_allow_invoicing_alert=notpos_config.module_account

    @api.depends('session_ids')
    def_compute_last_session(self):
        PosSession=self.env['pos.session']
        forpos_configinself:
            session=PosSession.search_read(
                [('config_id','=',pos_config.id),('state','=','closed')],
                ['cash_register_balance_end_real','stop_at','cash_register_id'],
                order="stop_atdesc",limit=1)
            ifsession:
                timezone=pytz.timezone(self._context.get('tz')orself.env.user.tzor'UTC')
                pos_config.last_session_closing_date=session[0]['stop_at'].astimezone(timezone).date()
                ifsession[0]['cash_register_id']:
                    pos_config.last_session_closing_cash=session[0]['cash_register_balance_end_real']
                    pos_config.last_session_closing_cashbox=self.env['account.bank.statement'].browse(session[0]['cash_register_id'][0]).cashbox_end_id
                else:
                    pos_config.last_session_closing_cash=0
                    pos_config.last_session_closing_cashbox=False
            else:
                pos_config.last_session_closing_cash=0
                pos_config.last_session_closing_date=False
                pos_config.last_session_closing_cashbox=False

    @api.depends('session_ids')
    def_compute_current_session_user(self):
        forpos_configinself:
            session=pos_config.session_ids.filtered(lambdas:s.statein['opening_control','opened','closing_control']andnots.rescue)
            ifsession:
                pos_config.pos_session_username=session[0].user_id.sudo().name
                pos_config.pos_session_state=session[0].state
                pos_config.pos_session_duration=(
                    datetime.now()-session[0].start_at
                ).daysifsession[0].start_atelse0
                pos_config.current_user_id=session[0].user_id
            else:
                pos_config.pos_session_username=False
                pos_config.pos_session_state=False
                pos_config.pos_session_duration=0
                pos_config.current_user_id=False

    @api.depends('iface_available_categ_ids')
    def_compute_selectable_categories(self):
        forconfiginself:
            ifconfig.iface_available_categ_ids:
                config.selectable_categ_ids=config.iface_available_categ_ids
            else:
                config.selectable_categ_ids=self.env['pos.category'].search([])

    @api.constrains('cash_control')
    def_check_session_state(self):
        open_session=self.env['pos.session'].search([('config_id','=',self.id),('state','!=','closed')])
        ifopen_session:
            raiseValidationError(_("Youarenotallowedtochangethecashcontrolstatuswhileasessionisalreadyopened."))

    @api.constrains('rounding_method')
    def_check_rounding_method_strategy(self):
        ifself.cash_roundingandself.rounding_method.strategy!='add_invoice_line':
            raiseValidationError(_("Cashroundingstrategymustbe:'Addaroundingline'"))

    @api.constrains('company_id','journal_id')
    def_check_company_journal(self):
        ifself.journal_idandself.journal_id.company_id.id!=self.company_id.id:
            raiseValidationError(_("Thesalesjournalandthepointofsalemustbelongtothesamecompany."))

    def_check_profit_loss_cash_journal(self):
        ifself.cash_controlandself.payment_method_ids:
            formethodinself.payment_method_ids:
                ifmethod.is_cash_countand(notmethod.cash_journal_id.loss_account_idornotmethod.cash_journal_id.profit_account_id):
                    raiseValidationError(_("Youneedalossandprofitaccountonyourcashjournal."))

    @api.constrains('company_id','invoice_journal_id')
    def_check_company_invoice_journal(self):
        ifself.invoice_journal_idandself.invoice_journal_id.company_id.id!=self.company_id.id:
            raiseValidationError(_("Theinvoicejournalandthepointofsalemustbelongtothesamecompany."))

    @api.constrains('company_id','payment_method_ids')
    def_check_company_payment(self):
        ifself.env['pos.payment.method'].search_count([('id','in',self.payment_method_ids.ids),('company_id','!=',self.company_id.id)]):
            raiseValidationError(_("Thepaymentmethodsandthepointofsalemustbelongtothesamecompany."))

    @api.constrains('pricelist_id','use_pricelist','available_pricelist_ids','journal_id','invoice_journal_id','payment_method_ids')
    def_check_currencies(self):
        forconfiginself:
            ifconfig.use_pricelistandconfig.pricelist_idnotinconfig.available_pricelist_ids:
                raiseValidationError(_("Thedefaultpricelistmustbeincludedintheavailablepricelists."))
        ifany(self.available_pricelist_ids.mapped(lambdapricelist:pricelist.currency_id!=self.currency_id)):
            raiseValidationError(_("Allavailablepricelistsmustbeinthesamecurrencyasthecompanyor"
                                    "astheSalesJournalsetonthispointofsaleifyouuse"
                                    "theAccountingapplication."))
        ifself.invoice_journal_id.currency_idandself.invoice_journal_id.currency_id!=self.currency_id:
            raiseValidationError(_("TheinvoicejournalmustbeinthesamecurrencyastheSalesJournalorthecompanycurrencyifthatisnotset."))
        ifany(
            self.payment_method_ids\
                .filtered(lambdapm:pm.is_cash_count)\
                .mapped(lambdapm:self.currency_idnotin(self.company_id.currency_id|pm.cash_journal_id.currency_id))
        ):
            raiseValidationError(_("AllpaymentmethodsmustbeinthesamecurrencyastheSalesJournalorthecompanycurrencyifthatisnotset."))

    @api.constrains('payment_method_ids')
    def_check_payment_method_receivable_accounts(self):
        #Thisisnormallynotsupposedtohappentohaveapaymentmethodwithoutareceivableaccountset,
        #asthisisarequiredfield.However,ithappensthereceivableaccountcannotbefoundduringupgrades
        #andthisisabommertoblocktheupgradeforthatpoint,giventheusercancorrectthisbyhimself,
        #withoutrequiringamanualinterventionfromourupgradesupport.
        #However,thismustbeensuredthisreceivableiswellsetbeforeopeningaPOSsession.
        invalid_payment_methods=self.payment_method_ids.filtered(lambdamethod:notmethod.receivable_account_id)
        ifinvalid_payment_methods:
            method_names=",".join(method.nameformethodininvalid_payment_methods)
            raiseValidationError(
                _("Youmustconfigureanintermediaryaccountforthepaymentmethods:%s.")%method_names
            )

    def_check_payment_method_ids(self):
        self.ensure_one()
        ifnotself.payment_method_ids:
            raiseValidationError(
                _("Youmusthaveatleastonepaymentmethodconfiguredtolaunchasession.")
            )

    @api.constrains('pricelist_id','available_pricelist_ids')
    def_check_pricelists(self):
        self._check_companies()
        self=self.sudo()
        ifself.pricelist_id.company_idandself.pricelist_id.company_id!=self.company_id:
            raiseValidationError(
                _("Thedefaultpricelistmustbelongtonocompanyorthecompanyofthepointofsale."))

    @api.constrains('company_id','available_pricelist_ids')
    def_check_companies(self):
        ifany(self.available_pricelist_ids.mapped(lambdapl:pl.company_id.idnotin(False,self.company_id.id))):
            raiseValidationError(_("Theselectedpricelistsmustbelongtonocompanyorthecompanyofthepointofsale."))

    @api.onchange('iface_tipproduct')
    def_onchange_tipproduct(self):
        ifself.iface_tipproduct:
            self.tip_product_id=self.env.ref('point_of_sale.product_product_tip',False)
        else:
            self.tip_product_id=False

    @api.onchange('iface_print_via_proxy')
    def_onchange_iface_print_via_proxy(self):
        self.iface_print_auto=self.iface_print_via_proxy
        ifnotself.iface_print_via_proxy:
            self.iface_cashdrawer=False

    @api.onchange('module_account')
    def_onchange_module_account(self):
        ifself.module_accountandnotself.invoice_journal_id:
            self.invoice_journal_id=self._default_invoice_journal()

    @api.onchange('use_pricelist')
    def_onchange_use_pricelist(self):
        """
        Ifthe'pricelist'boxisunchecked,weresetthepricelist_idtostop
        usingapricelistforthisiotbox.
        """
        ifnotself.use_pricelist:
            self.pricelist_id=self._default_pricelist()

    @api.onchange('available_pricelist_ids')
    def_onchange_available_pricelist_ids(self):
        ifself.pricelist_idnotinself.available_pricelist_ids._origin:
            self.pricelist_id=False

    @api.onchange('is_posbox')
    def_onchange_is_posbox(self):
        ifnotself.is_posbox:
            self.proxy_ip=False
            self.iface_scan_via_proxy=False
            self.iface_electronic_scale=False
            self.iface_cashdrawer=False
            self.iface_print_via_proxy=False
            self.iface_customer_facing_display=False

    @api.onchange('tax_regime')
    def_onchange_tax_regime(self):
        ifnotself.tax_regime:
            self.default_fiscal_position_id=False

    @api.onchange('tax_regime_selection')
    def_onchange_tax_regime_selection(self):
        ifnotself.tax_regime_selection:
            self.fiscal_position_ids=[(5,0,0)]

    @api.onchange('start_category')
    def_onchange_start_category(self):
        ifnotself.start_category:
            self.iface_start_categ_id=False

    @api.onchange('limit_categories','iface_available_categ_ids','iface_start_categ_id')
    def_onchange_limit_categories(self):
        res={}
        ifnotself.limit_categories:
            self.iface_available_categ_ids=False
        ifself.iface_available_categ_idsandself.iface_start_categ_id.idnotinself.iface_available_categ_ids.ids:
            self.iface_start_categ_id=False
        returnres

    @api.onchange('is_header_or_footer')
    def_onchange_header_footer(self):
        ifnotself.is_header_or_footer:
            self.receipt_header=False
            self.receipt_footer=False

    defname_get(self):
        result=[]
        forconfiginself:
            last_session=self.env['pos.session'].search([('config_id','=',config.id)],limit=1)
            if(notlast_session)or(last_session.state=='closed'):
                result.append((config.id,_("%(pos_name)s(notused)",pos_name=config.name)))
            else:
                result.append((config.id,"%s(%s)"%(config.name,last_session.user_id.name)))
        returnresult

    def_check_header_footer(self,values):
        ifnotself.env.is_admin()and{'is_header_or_footer','receipt_header','receipt_footer'}&values.keys():
            raiseAccessError(_('Onlyadministratorscaneditreceiptheadersandfooters'))

    @api.model
    defcreate(self,values):
        self._check_header_footer(values)
        IrSequence=self.env['ir.sequence'].sudo()
        val={
            'name':_('POSOrder%s',values['name']),
            'padding':4,
            'prefix':"%s/"%values['name'],
            'code':"pos.order",
            'company_id':values.get('company_id',False),
        }
        #forcesequence_idfieldtonewpos.ordersequence
        values['sequence_id']=IrSequence.create(val).id

        val.update(name=_('POSorderline%s',values['name']),code='pos.order.line')
        values['sequence_line_id']=IrSequence.create(val).id
        pos_config=super(PosConfig,self).create(values)
        pos_config.sudo()._check_modules_to_install()
        pos_config.sudo()._check_groups_implied()
        #Ifyouplantoaddsomethingafterthis,useanewenvironment.Theoneaboveisnolongervalidafterthemodulesinstall.
        returnpos_config

    defwrite(self,vals):
        self._check_header_footer(vals)
        opened_session=self.mapped('session_ids').filtered(lambdas:s.state!='closed')
        ifopened_session:
            forbidden_fields=[]
            forkeyinself._get_forbidden_change_fields():
                ifkeyinvals.keys():
                    field_name=self._fields[key].get_description(self.env)["string"]
                    forbidden_fields.append(field_name)
            iflen(forbidden_fields)>0:
                raiseUserError(_(
                    "UnabletomodifythisPoSConfigurationbecauseyoucan'tmodify%swhileasessionisopen.",
                    ",".join(forbidden_fields)
                ))
        result=super(PosConfig,self).write(vals)

        self.sudo()._set_fiscal_position()
        self.sudo()._check_modules_to_install()
        self.sudo()._check_groups_implied()
        returnresult

    def_get_forbidden_change_fields(self):
        forbidden_keys=['module_pos_hr','cash_control','module_pos_restaurant','available_pricelist_ids',
                          'limit_categories','iface_available_categ_ids','use_pricelist','module_pos_discount',
                          'payment_method_ids','iface_tipproduc']
        returnforbidden_keys

    defunlink(self):
        #Deletethepos.configrecordsfirstthendeletethesequenceslinkedtothem
        sequences_to_delete=self.sequence_id|self.sequence_line_id
        res=super(PosConfig,self).unlink()
        sequences_to_delete.unlink()
        returnres

    def_set_fiscal_position(self):
        forconfiginself:
            ifconfig.tax_regimeandconfig.default_fiscal_position_id.idnotinconfig.fiscal_position_ids.ids:
                config.fiscal_position_ids=[(4,config.default_fiscal_position_id.id)]
            elifnotconfig.tax_regime_selectionandnotconfig.tax_regimeandconfig.fiscal_position_ids.ids:
                config.fiscal_position_ids=[(5,0,0)]

    def_check_modules_to_install(self):
        #determinemodulestoinstall
        expected=[
            fname[7:]          #'module_account'->'account'
            forfnameinself.fields_get_keys()
            iffname.startswith('module_')
            ifany(pos_config[fname]forpos_configinself)
        ]
        ifexpected:
            STATES=('installed','toinstall','toupgrade')
            modules=self.env['ir.module.module'].sudo().search([('name','in',expected)])
            modules=modules.filtered(lambdamodule:module.statenotinSTATES)
            ifmodules:
                modules.button_immediate_install()
                #justincasewewanttodosomethingifweinstallamodule.(likearefresh...)
                returnTrue
        returnFalse

    def_check_groups_implied(self):
        forpos_configinself:
            forfield_namein[fforfinpos_config.fields_get_keys()iff.startswith('group_')]:
                field=pos_config._fields[field_name]
                iffield.typein('boolean','selection')andhasattr(field,'implied_group'):
                    field_group_xmlids=getattr(field,'group','base.group_user').split(',')
                    field_groups=self.env['res.groups'].concat(*(self.env.ref(it)foritinfield_group_xmlids))
                    field_groups.write({'implied_ids':[(4,self.env.ref(field.implied_group).id)]})


    defexecute(self):
        return{
             'type':'ir.actions.client',
             'tag':'reload',
             'params':{'wait':True}
         }

    def_force_http(self):
        enforce_https=self.env['ir.config_parameter'].sudo().get_param('point_of_sale.enforce_https')
        ifnotenforce_httpsandself.other_devices:
            returnTrue
        returnFalse

    def_get_pos_base_url(self):
        return'/pos/web'ifself._force_http()else'/pos/ui'

    #MethodstoopenthePOS
    defopen_ui(self):
        """Opentheposinterfacewithconfig_idasanextraargument.

        InvanillaPoSeachusercanonlyhaveoneactivesession,thereforeitwasnotneededtopasstheconfig_id
        onopeningasession.Itisalsopossibletologintosessionscreatedbyotherusers.

        :returns:dict
        """
        self.ensure_one()
        #checkallconstraints,raisesifanyisnotmet
        self._validate_fields(set(self._fields)-{"cash_control"})
        return{
            'type':'ir.actions.act_url',
            'url':self._get_pos_base_url()+'?config_id=%d'%self.id,
            'target':'self',
        }

    defopen_session_cb(self,check_coa=True):
        """newsessionbutton

        createoneifnoneexist
        accesscashcontrolinterfaceifenabledorstartasession
        """
        self.ensure_one()
        ifnotself.current_session_id:
            self._check_pricelists()
            self._check_company_journal()
            self._check_company_invoice_journal()
            self._check_company_payment()
            self._check_currencies()
            self._check_profit_loss_cash_journal()
            self._check_payment_method_ids()
            self._check_payment_method_receivable_accounts()
            self.env['pos.session'].create({
                'user_id':self.env.uid,
                'config_id':self.id
            })
        returnself.open_ui()

    defopen_existing_session_cb(self):
        """closesessionbutton

        accesssessionformtovalidateentries
        """
        self.ensure_one()
        returnself._open_session(self.current_session_id.id)

    def_open_session(self,session_id):
        self._check_pricelists() #Thepricelistcompanymighthavechangedafterthefirstopeningofthesession
        return{
            'name':_('Session'),
            'view_mode':'form,tree',
            'res_model':'pos.session',
            'res_id':session_id,
            'view_id':False,
            'type':'ir.actions.act_window',
        }

    #AllfollowingmethodsaremadetocreatedataneededinPOS,whenalocalisation
    #isinstalled,orifPOSisinstalledondatabasehavingcompaniesthatalreadyhave
    #alocalisationinstalled
    @api.model
    defpost_install_pos_localisation(self,companies=False):
        self=self.sudo()
        ifnotcompanies:
            companies=self.env['res.company'].search([])
        forcompanyincompanies.filtered('chart_template_id'):
            pos_configs=self.search([('company_id','=',company.id)])
            pos_configs.setup_defaults(company)

    defsetup_defaults(self,company):
        """Extendthismethodtocustomizetheexistingpos.configofthecompanyduringtheinstallation
        ofalocalisation.

        :paramselfpos.config:pos.configrecordspresentinthecompanyduringtheinstallationoflocalisation.
        :paramcompanyres.company:thesinglecompanywherethepos.configdefaultswillbesetup.
        """
        self.assign_payment_journals(company)
        self.generate_pos_journal(company)
        self.setup_invoice_journal(company)

    defassign_payment_journals(self,company):
        forpos_configinself:
            ifpos_config.payment_method_idsorpos_config.has_active_session:
                continue
            cash_journal=self.env['account.journal'].search([('company_id','=',company.id),('type','=','cash')],limit=1)
            pos_receivable_account=company.account_default_pos_receivable_account_id
            payment_methods=self.env['pos.payment.method']
            ifcash_journal:
                payment_methods|=payment_methods.create({
                    'name':_('Cash'),
                    'receivable_account_id':pos_receivable_account.id,
                    'is_cash_count':True,
                    'cash_journal_id':cash_journal.id,
                    'company_id':company.id,
                })
            payment_methods|=payment_methods.create({
                'name':_('Bank'),
                'receivable_account_id':pos_receivable_account.id,
                'is_cash_count':False,
                'company_id':company.id,
            })
            pos_config.write({'payment_method_ids':[(6,0,payment_methods.ids)]})

    defgenerate_pos_journal(self,company):
        forpos_configinself:
            ifpos_config.journal_id:
                continue
            pos_journal=self.env['account.journal'].search([('company_id','=',company.id),('code','=','POSS')])
            ifnotpos_journal:
                pos_journal=self.env['account.journal'].create({
                    'type':'sale',
                    'name':'PointofSale',
                    'code':'POSS',
                    'company_id':company.id,
                    'sequence':20
                })
            pos_config.write({'journal_id':pos_journal.id})

    defsetup_invoice_journal(self,company):
        forpos_configinself:
            invoice_journal_id=pos_config.invoice_journal_idorself.env['account.journal'].search([('type','=','sale'),('company_id','=',company.id)],limit=1)
            ifinvoice_journal_id:
                pos_config.write({'invoice_journal_id':invoice_journal_id.id})
            else:
                pos_config.write({'module_account':False})
