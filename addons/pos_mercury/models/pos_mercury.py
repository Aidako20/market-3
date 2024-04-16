#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportmodels,fields,api,_
fromflectra.tools.float_utilsimportfloat_compare

_logger=logging.getLogger(__name__)


classBarcodeRule(models.Model):
    _inherit='barcode.rule'

    type=fields.Selection(selection_add=[
        ('credit','CreditCard')
    ],ondelete={'credit':'setdefault'})


classPosMercuryConfiguration(models.Model):
    _name='pos_mercury.configuration'
    _description='PointofSaleVantivConfiguration'

    name=fields.Char(required=True,help='NameofthisVantivconfiguration')
    merchant_id=fields.Char(string='MerchantID',required=True,help='IDofthemerchanttoauthenticatehimonthepaymentproviderserver')
    merchant_pwd=fields.Char(string='MerchantPassword',required=True,help='Passwordofthemerchanttoauthenticatehimonthepaymentproviderserver')


classPoSPayment(models.Model):
    _inherit="pos.payment"

    mercury_card_number=fields.Char(string='CardNumber',help='Thelast4numbersofthecardusedtopay')
    mercury_prefixed_card_number=fields.Char(string='CardNumberPrefix',compute='_compute_prefixed_card_number',help='Thecardnumberusedforthepayment.')
    mercury_card_brand=fields.Char(string='CardBrand',help='Thebrandofthepaymentcard(e.g.Visa,AMEX,...)')
    mercury_card_owner_name=fields.Char(string='CardOwnerName',help='Thenameofthecardowner')
    mercury_ref_no=fields.Char(string='Vantivreferencenumber',help='PaymentreferencenumberfromVantivPay')
    mercury_record_no=fields.Char(string='Vantivrecordnumber',help='PaymentrecordnumberfromVantivPay')
    mercury_invoice_no=fields.Char(string='Vantivinvoicenumber',help='InvoicenumberfromVantivPay')

    def_compute_prefixed_card_number(self):
        forlineinself:
            ifline.mercury_card_number:
                line.mercury_prefixed_card_number="********"+line.mercury_card_number
            else:
                line.mercury_prefixed_card_number=""


classPoSPaymentMethod(models.Model):
    _inherit='pos.payment.method'

    pos_mercury_config_id=fields.Many2one('pos_mercury.configuration',string='VantivCredentials',help='TheconfigurationofVantivusedforthisjournal')

    def_get_payment_terminal_selection(self):
        returnsuper(PoSPaymentMethod,self)._get_payment_terminal_selection()+[('mercury','Vantiv')]

    @api.onchange('use_payment_terminal')
    def_onchange_use_payment_terminal(self):
        super(PoSPaymentMethod,self)._onchange_use_payment_terminal()
        ifself.use_payment_terminal!='mercury':
            self.pos_mercury_config_id=False

classPosOrder(models.Model):
    _inherit="pos.order"

    @api.model
    def_payment_fields(self,order,ui_paymentline):
        fields=super(PosOrder,self)._payment_fields(order,ui_paymentline)

        fields.update({
            'mercury_card_number':ui_paymentline.get('mercury_card_number'),
            'mercury_card_brand':ui_paymentline.get('mercury_card_brand'),
            'mercury_card_owner_name':ui_paymentline.get('mercury_card_owner_name'),
            'mercury_ref_no':ui_paymentline.get('mercury_ref_no'),
            'mercury_record_no':ui_paymentline.get('mercury_record_no'),
            'mercury_invoice_no':ui_paymentline.get('mercury_invoice_no')
        })

        returnfields
