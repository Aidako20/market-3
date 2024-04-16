#-*-coding:utf-8-*-

fromflectraimportmodels,fields,api

fromfunctoolsimportlru_cache


classAccountInvoiceReport(models.Model):
    _name="account.invoice.report"
    _description="InvoicesStatistics"
    _auto=False
    _rec_name='invoice_date'
    _order='invoice_datedesc'

    #====Invoicefields====
    move_id=fields.Many2one('account.move',readonly=True)
    journal_id=fields.Many2one('account.journal',string='Journal',readonly=True)
    company_id=fields.Many2one('res.company',string='Company',readonly=True)
    company_currency_id=fields.Many2one('res.currency',string='CompanyCurrency',readonly=True)
    partner_id=fields.Many2one('res.partner',string='Partner',readonly=True)
    commercial_partner_id=fields.Many2one('res.partner',string='PartnerCompany',help="CommercialEntity")
    country_id=fields.Many2one('res.country',string="Country")
    invoice_user_id=fields.Many2one('res.users',string='Salesperson',readonly=True)
    move_type=fields.Selection([
        ('out_invoice','CustomerInvoice'),
        ('in_invoice','VendorBill'),
        ('out_refund','CustomerCreditNote'),
        ('in_refund','VendorCreditNote'),
        ],readonly=True)
    state=fields.Selection([
        ('draft','Draft'),
        ('posted','Open'),
        ('cancel','Cancelled')
        ],string='InvoiceStatus',readonly=True)
    payment_state=fields.Selection(selection=[
        ('not_paid','NotPaid'),
        ('in_payment','InPayment'),
        ('paid','paid')
    ],string='PaymentStatus',readonly=True)
    fiscal_position_id=fields.Many2one('account.fiscal.position',string='FiscalPosition',readonly=True)
    invoice_date=fields.Date(readonly=True,string="InvoiceDate")

    #====Invoicelinefields====
    quantity=fields.Float(string='ProductQuantity',readonly=True)
    product_id=fields.Many2one('product.product',string='Product',readonly=True)
    product_uom_id=fields.Many2one('uom.uom',string='UnitofMeasure',readonly=True)
    product_categ_id=fields.Many2one('product.category',string='ProductCategory',readonly=True)
    invoice_date_due=fields.Date(string='DueDate',readonly=True)
    account_id=fields.Many2one('account.account',string='Revenue/ExpenseAccount',readonly=True,domain=[('deprecated','=',False)])
    analytic_account_id=fields.Many2one('account.analytic.account',string='AnalyticAccount',groups="analytic.group_analytic_accounting")
    price_subtotal=fields.Float(string='UntaxedTotal',readonly=True)
    price_average=fields.Float(string='AveragePrice',readonly=True,group_operator="avg")

    _depends={
        'account.move':[
            'name','state','move_type','partner_id','invoice_user_id','fiscal_position_id',
            'invoice_date','invoice_date_due','invoice_payment_term_id','partner_bank_id',
        ],
        'account.move.line':[
            'quantity','price_subtotal','amount_residual','balance','amount_currency',
            'move_id','product_id','product_uom_id','account_id','analytic_account_id',
            'journal_id','company_id','currency_id','partner_id',
        ],
        'product.product':['product_tmpl_id'],
        'product.template':['categ_id'],
        'uom.uom':['category_id','factor','name','uom_type'],
        'res.currency.rate':['currency_id','name'],
        'res.partner':['country_id'],
    }

    @property
    def_table_query(self):
        return'%s%s%s'%(self._select(),self._from(),self._where())

    @api.model
    def_select(self):
        return'''
            SELECT
                line.id,
                line.move_id,
                line.product_id,
                line.account_id,
                line.analytic_account_id,
                line.journal_id,
                line.company_id,
                line.company_currency_id,
                line.partner_idAScommercial_partner_id,
                move.state,
                move.move_type,
                move.partner_id,
                move.invoice_user_id,
                move.fiscal_position_id,
                move.payment_state,
                move.invoice_date,
                move.invoice_date_due,
                uom_template.id                                            ASproduct_uom_id,
                template.categ_id                                          ASproduct_categ_id,
                line.quantity/NULLIF(COALESCE(uom_line.factor,1)/COALESCE(uom_template.factor,1),0.0)*(CASEWHENmove.move_typeIN('in_invoice','out_refund','in_receipt')THEN-1ELSE1END)
                                                                            ASquantity,
                -line.balance*currency_table.rate                        ASprice_subtotal,
                -COALESCE(
                   --Averagelineprice
                   (line.balance/NULLIF(line.quantity,0.0))*(CASEWHENmove.move_typeIN('in_invoice','out_refund','in_receipt')THEN-1ELSE1END)
                   --converttotemplateuom
                   *(NULLIF(COALESCE(uom_line.factor,1),0.0)/NULLIF(COALESCE(uom_template.factor,1),0.0)),
                   0.0)*currency_table.rate                              ASprice_average,
                COALESCE(partner.country_id,commercial_partner.country_id)AScountry_id
        '''

    @api.model
    def_from(self):
        return'''
            FROMaccount_move_lineline
                LEFTJOINres_partnerpartnerONpartner.id=line.partner_id
                LEFTJOINproduct_productproductONproduct.id=line.product_id
                LEFTJOINaccount_accountaccountONaccount.id=line.account_id
                LEFTJOINaccount_account_typeuser_typeONuser_type.id=account.user_type_id
                LEFTJOINproduct_templatetemplateONtemplate.id=product.product_tmpl_id
                LEFTJOINuom_uomuom_lineONuom_line.id=line.product_uom_id
                LEFTJOINuom_uomuom_templateONuom_template.id=template.uom_id
                INNERJOINaccount_movemoveONmove.id=line.move_id
                LEFTJOINres_partnercommercial_partnerONcommercial_partner.id=move.commercial_partner_id
                JOIN{currency_table}ONcurrency_table.company_id=line.company_id
        '''.format(
            currency_table=self.env['res.currency']._get_query_currency_table({'multi_company':True,'date':{'date_to':fields.Date.today()}}),
        )

    @api.model
    def_where(self):
        return'''
            WHEREmove.move_typeIN('out_invoice','out_refund','in_invoice','in_refund','out_receipt','in_receipt')
                ANDline.account_idISNOTNULL
                ANDNOTline.exclude_from_invoice_tab
        '''


classReportInvoiceWithoutPayment(models.AbstractModel):
    _name='report.account.report_invoice'
    _description='Accountreportwithoutpaymentlines'

    @api.model
    def_get_report_values(self,docids,data=None):
        docs=self.env['account.move'].browse(docids)

        qr_code_urls={}
        forinvoiceindocs:
            ifinvoice.display_qr_code:
                new_code_url=invoice.generate_qr_code()
                ifnew_code_url:
                    qr_code_urls[invoice.id]=new_code_url

        return{
            'doc_ids':docids,
            'doc_model':'account.move',
            'docs':docs,
            'qr_code_urls':qr_code_urls,
        }

classReportInvoiceWithPayment(models.AbstractModel):
    _name='report.account.report_invoice_with_payments'
    _description='Accountreportwithpaymentlines'
    _inherit='report.account.report_invoice'

    @api.model
    def_get_report_values(self,docids,data=None):
        rslt=super()._get_report_values(docids,data)
        rslt['report_type']=data.get('report_type')ifdataelse''
        returnrslt
