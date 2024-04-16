#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.addons.base.models.res_partnerimportWARNING_MESSAGE,WARNING_HELP


classres_partner(models.Model):
    _name='res.partner'
    _inherit='res.partner'

    def_compute_purchase_order_count(self):
        #retrieveallchildrenpartnersandprefetch'parent_id'onthem
        all_partners=self.with_context(active_test=False).search([('id','child_of',self.ids)])
        all_partners.read(['parent_id'])

        purchase_order_groups=self.env['purchase.order'].read_group(
            domain=[('partner_id','in',all_partners.ids)],
            fields=['partner_id'],groupby=['partner_id']
        )
        partners=self.browse()
        forgroupinpurchase_order_groups:
            partner=self.browse(group['partner_id'][0])
            whilepartner:
                ifpartnerinself:
                    partner.purchase_order_count+=group['partner_id_count']
                    partners|=partner
                partner=partner.parent_id
        (self-partners).purchase_order_count=0

    def_compute_supplier_invoice_count(self):
        #retrieveallchildrenpartnersandprefetch'parent_id'onthem
        all_partners=self.with_context(active_test=False).search([('id','child_of',self.ids)])
        all_partners.read(['parent_id'])

        supplier_invoice_groups=self.env['account.move'].read_group(
            domain=[('partner_id','in',all_partners.ids),
                    ('move_type','in',('in_invoice','in_refund'))],
            fields=['partner_id'],groupby=['partner_id']
        )
        partners=self.browse()
        forgroupinsupplier_invoice_groups:
            partner=self.browse(group['partner_id'][0])
            whilepartner:
                ifpartnerinself:
                    partner.supplier_invoice_count+=group['partner_id_count']
                    partners|=partner
                partner=partner.parent_id
        (self-partners).supplier_invoice_count=0

    @api.model
    def_commercial_fields(self):
        returnsuper(res_partner,self)._commercial_fields()

    property_purchase_currency_id=fields.Many2one(
        'res.currency',string="SupplierCurrency",company_dependent=True,
        help="Thiscurrencywillbeused,insteadofthedefaultone,forpurchasesfromthecurrentpartner")
    purchase_order_count=fields.Integer(compute='_compute_purchase_order_count',string='PurchaseOrderCount')
    supplier_invoice_count=fields.Integer(compute='_compute_supplier_invoice_count',string='#VendorBills')
    purchase_warn=fields.Selection(WARNING_MESSAGE,'PurchaseOrder',help=WARNING_HELP,default="no-message")
    purchase_warn_msg=fields.Text('MessageforPurchaseOrder')

    receipt_reminder_email=fields.Boolean('ReceiptReminder',default=False,company_dependent=True,
        help="AutomaticallysendaconfirmationemailtothevendorXdaysbeforetheexpectedreceiptdate,askinghimtoconfirmtheexactdate.")
    reminder_date_before_receipt=fields.Integer('DaysBeforeReceipt',default=1,company_dependent=True,
        help="Numberofdaystosendreminderemailbeforethepromisedreceiptdate")
