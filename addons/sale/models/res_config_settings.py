#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    group_auto_done_setting=fields.Boolean("LockConfirmedSales",implied_group='sale.group_auto_done_setting')
    module_sale_margin=fields.Boolean("Margins")
    quotation_validity_days=fields.Integer(related='company_id.quotation_validity_days',string="DefaultQuotationValidity(Days)",readonly=False)
    use_quotation_validity_days=fields.Boolean("DefaultQuotationValidity",config_parameter='sale.use_quotation_validity_days')
    group_warning_sale=fields.Boolean("SaleOrderWarnings",implied_group='sale.group_warning_sale')
    portal_confirmation_sign=fields.Boolean(related='company_id.portal_confirmation_sign',string='OnlineSignature',readonly=False)
    portal_confirmation_pay=fields.Boolean(related='company_id.portal_confirmation_pay',string='OnlinePayment',readonly=False)
    group_sale_delivery_address=fields.Boolean("CustomerAddresses",implied_group='sale.group_delivery_invoice_address')
    group_proforma_sales=fields.Boolean(string="Pro-FormaInvoice",implied_group='sale.group_proforma_sales',
        help="Allowsyoutosendpro-formainvoice.")
    default_invoice_policy=fields.Selection([
        ('order','Invoicewhatisordered'),
        ('delivery','Invoicewhatisdelivered')
        ],'InvoicingPolicy',
        default='delivery',
        default_model='product.template')
    deposit_default_product_id=fields.Many2one(
        'product.product',
        'DepositProduct',
        domain="[('type','=','service')]",
        config_parameter='sale.default_deposit_product_id',
        help='Defaultproductusedforpaymentadvances')

    auth_signup_uninvited=fields.Selection([
        ('b2b','Oninvitation'),
        ('b2c','Freesignup'),
    ],string='CustomerAccount',default='b2b',config_parameter='auth_signup.invitation_scope')

    module_delivery=fields.Boolean("DeliveryMethods")
    module_delivery_dhl=fields.Boolean("DHLExpressConnector")
    module_delivery_fedex=fields.Boolean("FedExConnector")
    module_delivery_ups=fields.Boolean("UPSConnector")
    module_delivery_usps=fields.Boolean("USPSConnector")
    module_delivery_bpost=fields.Boolean("bpostConnector")
    module_delivery_easypost=fields.Boolean("EasypostConnector")

    module_product_email_template=fields.Boolean("SpecificEmail")
    module_sale_coupon=fields.Boolean("Coupons&Promotions")
    module_sale_amazon=fields.Boolean("AmazonSync")

    automatic_invoice=fields.Boolean("AutomaticInvoice",
                                       help="Theinvoiceisgeneratedautomaticallyandavailableinthecustomerportal"
                                            "whenthetransactionisconfirmedbythepaymentacquirer.\n"
                                            "Theinvoiceismarkedaspaidandthepaymentisregisteredinthepaymentjournal"
                                            "definedintheconfigurationofthepaymentacquirer.\n"
                                            "Thismodeisadvisedifyouissuethefinalinvoiceattheorderandnotafterthedelivery.",
                                       config_parameter='sale.automatic_invoice')
    template_id=fields.Many2one('mail.template','EmailTemplate',
                                  domain="[('model','=','account.move')]",
                                  config_parameter='sale.default_email_template',
                                  default=lambdaself:self.env.ref('account.email_template_edi_invoice',False))
    confirmation_template_id=fields.Many2one('mail.template',string='ConfirmationEmail',
                                               domain="[('model','=','sale.order')]",
                                               config_parameter='sale.default_confirmation_template',
                                               help="Emailsenttothecustomeroncetheorderispaid.")

    defset_values(self):
        super(ResConfigSettings,self).set_values()
        ifself.default_invoice_policy!='order':
            self.env['ir.config_parameter'].set_param('sale.automatic_invoice',False)

    @api.onchange('use_quotation_validity_days')
    def_onchange_use_quotation_validity_days(self):
        ifself.quotation_validity_days<=0:
            self.quotation_validity_days=self.env['res.company'].default_get(['quotation_validity_days'])['quotation_validity_days']

    @api.onchange('quotation_validity_days')
    def_onchange_quotation_validity_days(self):
        ifself.quotation_validity_days<=0:
            self.quotation_validity_days=self.env['res.company'].default_get(['quotation_validity_days'])['quotation_validity_days']
            return{
                'warning':{'title':"Warning",'message':"QuotationValidityisrequiredandmustbegreaterthan0."},
            }
