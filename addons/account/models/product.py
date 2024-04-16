#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError

ACCOUNT_DOMAIN="[('deprecated','=',False),('internal_type','=','other'),('company_id','=',current_company_id),('is_off_balance','=',False)]"

classProductCategory(models.Model):
    _inherit="product.category"

    property_account_income_categ_id=fields.Many2one('account.account',company_dependent=True,
        string="IncomeAccount",
        domain=ACCOUNT_DOMAIN,
        help="Thisaccountwillbeusedwhenvalidatingacustomerinvoice.")
    property_account_expense_categ_id=fields.Many2one('account.account',company_dependent=True,
        string="ExpenseAccount",
        domain=ACCOUNT_DOMAIN,
        help="Theexpenseisaccountedforwhenavendorbillisvalidated,exceptinanglo-saxonaccountingwithperpetualinventoryvaluationinwhichcasetheexpense(CostofGoodsSoldaccount)isrecognizedatthecustomerinvoicevalidation.")

#----------------------------------------------------------
#Products
#----------------------------------------------------------
classProductTemplate(models.Model):
    _inherit="product.template"

    taxes_id=fields.Many2many('account.tax','product_taxes_rel','prod_id','tax_id',help="Defaulttaxesusedwhensellingtheproduct.",string='CustomerTaxes',
        domain=[('type_tax_use','=','sale')],default=lambdaself:self.env.company.account_sale_tax_id)
    supplier_taxes_id=fields.Many2many('account.tax','product_supplier_taxes_rel','prod_id','tax_id',string='VendorTaxes',help='Defaulttaxesusedwhenbuyingtheproduct.',
        domain=[('type_tax_use','=','purchase')],default=lambdaself:self.env.company.account_purchase_tax_id)
    property_account_income_id=fields.Many2one('account.account',company_dependent=True,
        string="IncomeAccount",
        domain=ACCOUNT_DOMAIN,
        help="Keepthisfieldemptytousethedefaultvaluefromtheproductcategory.")
    property_account_expense_id=fields.Many2one('account.account',company_dependent=True,
        string="ExpenseAccount",
        domain=ACCOUNT_DOMAIN,
        help="Keepthisfieldemptytousethedefaultvaluefromtheproductcategory.Ifanglo-saxonaccountingwithautomatedvaluationmethodisconfigured,theexpenseaccountontheproductcategorywillbeused.")

    def_get_product_accounts(self):
        return{
            'income':self.property_account_income_idorself.categ_id.property_account_income_categ_id,
            'expense':self.property_account_expense_idorself.categ_id.property_account_expense_categ_id
        }

    def_get_asset_accounts(self):
        res={}
        res['stock_input']=False
        res['stock_output']=False
        returnres

    defget_product_accounts(self,fiscal_pos=None):
        accounts=self._get_product_accounts()
        ifnotfiscal_pos:
            fiscal_pos=self.env['account.fiscal.position']
        returnfiscal_pos.map_accounts(accounts)

    @api.constrains('uom_id')
    def_check_uom_not_in_invoice(self):
        self.env['product.template'].flush(['uom_id'])
        self._cr.execute("""
            SELECTprod_template.id
              FROMaccount_move_lineline
              JOINproduct_productprod_variantONline.product_id=prod_variant.id
              JOINproduct_templateprod_templateONprod_variant.product_tmpl_id=prod_template.id
              JOINuom_uomtemplate_uomONprod_template.uom_id=template_uom.id
              JOINuom_categorytemplate_uom_catONtemplate_uom.category_id=template_uom_cat.id
              JOINuom_uomline_uomONline.product_uom_id=line_uom.id
              JOINuom_categoryline_uom_catONline_uom.category_id=line_uom_cat.id
             WHEREprod_template.idIN%s
               ANDline.parent_state='posted'
               ANDtemplate_uom_cat.id!=line_uom_cat.id
             LIMIT1
        """,[tuple(self.ids)])
        ifself._cr.fetchall():
            raiseValidationError(_(
                "ThisproductisalreadybeingusedinpostedJournalEntries.\n"
                "IfyouwanttochangeitsUnitofMeasure,pleasearchivethisproductandcreateanewone."
            ))


classProductProduct(models.Model):
    _inherit="product.product"

    def_get_product_accounts(self):
        returnself.product_tmpl_id._get_product_accounts()

    @api.model
    def_get_tax_included_unit_price(self,company,currency,document_date,document_type,
            is_refund_document=False,product_uom=None,product_currency=None,
            product_price_unit=None,product_taxes=None,fiscal_position=None
        ):
        """Helpertogetthepriceunitfromdifferentmodels.
            Thisisneededtocomputethesameunitpriceindifferentmodels(saleorder,accountmove,etc.)withsameparameters.
        """

        product=self

        assertdocument_type

        ifproduct_uomisNone:
            product_uom=product.uom_id
        ifnotproduct_currency:
            ifdocument_type=='sale':
                product_currency=product.currency_id
            elifdocument_type=='purchase':
                product_currency=company.currency_id
        ifproduct_price_unitisNone:
            ifdocument_type=='sale':
                product_price_unit=product.with_company(company).lst_price
            elifdocument_type=='purchase':
                product_price_unit=product.with_company(company).standard_price
            else:
                return0.0
        ifproduct_taxesisNone:
            ifdocument_type=='sale':
                product_taxes=product.taxes_id.filtered(lambdax:x.company_id==company)
            elifdocument_type=='purchase':
                product_taxes=product.supplier_taxes_id.filtered(lambdax:x.company_id==company)
        #Applyunitofmeasure.
        ifproduct_uomandproduct.uom_id!=product_uom:
            product_price_unit=product.uom_id._compute_price(product_price_unit,product_uom)

        #Applyfiscalposition.
        ifproduct_taxesandfiscal_position:
            product_taxes_after_fp=fiscal_position.map_tax(product_taxes)
            flattened_taxes_after_fp=product_taxes_after_fp._origin.flatten_taxes_hierarchy()
            flattened_taxes_before_fp=product_taxes._origin.flatten_taxes_hierarchy()
            taxes_before_included=all(tax.price_includefortaxinflattened_taxes_before_fp)

            ifset(product_taxes.ids)!=set(product_taxes_after_fp.ids)andtaxes_before_included:
                taxes_res=flattened_taxes_before_fp.compute_all(
                    product_price_unit,
                    quantity=1.0,
                    currency=currency,
                    product=product,
                    is_refund=is_refund_document,
                )
                product_price_unit=taxes_res['total_excluded']

                ifany(tax.price_includefortaxinflattened_taxes_after_fp):
                    taxes_res=flattened_taxes_after_fp.compute_all(
                        product_price_unit,
                        quantity=1.0,
                        currency=currency,
                        product=product,
                        is_refund=is_refund_document,
                        handle_price_include=False,
                    )
                    fortax_resintaxes_res['taxes']:
                        tax=self.env['account.tax'].browse(tax_res['id'])
                        iftax.price_include:
                            product_price_unit+=tax_res['amount']

        #Applycurrencyrate.
        ifcurrency!=product_currency:
            product_price_unit=product_currency._convert(product_price_unit,currency,company,document_date)

        returnproduct_price_unit
