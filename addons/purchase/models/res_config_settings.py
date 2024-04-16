#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    lock_confirmed_po=fields.Boolean("LockConfirmedOrders",default=lambdaself:self.env.company.po_lock=='lock')
    po_lock=fields.Selection(related='company_id.po_lock',string="PurchaseOrderModification*",readonly=False)
    po_order_approval=fields.Boolean("PurchaseOrderApproval",default=lambdaself:self.env.company.po_double_validation=='two_step')
    po_double_validation=fields.Selection(related='company_id.po_double_validation',string="LevelsofApprovals*",readonly=False)
    po_double_validation_amount=fields.Monetary(related='company_id.po_double_validation_amount',string="MinimumAmount",currency_field='company_currency_id',readonly=False)
    company_currency_id=fields.Many2one('res.currency',related='company_id.currency_id',string="CompanyCurrency",readonly=True,
        help='Utilityfieldtoexpressamountcurrency')
    default_purchase_method=fields.Selection([
        ('purchase','Orderedquantities'),
        ('receive','Receivedquantities'),
        ],string="BillControl",default_model="product.template",
        help="Thisdefaultvalueisappliedtoanynewproductcreated."
        "Thiscanbechangedintheproductdetailform.",default="receive")
    group_warning_purchase=fields.Boolean("PurchaseWarnings",implied_group='purchase.group_warning_purchase')
    module_account_3way_match=fields.Boolean("3-waymatching:purchases,receptionsandbills")
    module_purchase_requisition=fields.Boolean("PurchaseAgreements")
    module_purchase_product_matrix=fields.Boolean("PurchaseGridEntry")
    po_lead=fields.Float(related='company_id.po_lead',readonly=False)
    use_po_lead=fields.Boolean(
        string="SecurityLeadTimeforPurchase",
        config_parameter='purchase.use_po_lead',
        help="Marginoferrorforvendorleadtimes.WhenthesystemgeneratesPurchaseOrdersforreorderingproducts,theywillbescheduledthatmanydaysearliertocopewithunexpectedvendordelays.")

    group_send_reminder=fields.Boolean("ReceiptReminder",implied_group='purchase.group_send_reminder',default=True,
        help="Allowautomaticallysendemailtoremindyourvendorthereceiptdate")

    @api.onchange('use_po_lead')
    def_onchange_use_po_lead(self):
        ifnotself.use_po_lead:
            self.po_lead=0.0

    defset_values(self):
        super(ResConfigSettings,self).set_values()
        self.po_lock='lock'ifself.lock_confirmed_poelse'edit'
        self.po_double_validation='two_step'ifself.po_order_approvalelse'one_step'
