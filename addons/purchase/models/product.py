#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.addons.base.models.res_partnerimportWARNING_MESSAGE,WARNING_HELP
fromflectra.tools.float_utilsimportfloat_round
fromdateutil.relativedeltaimportrelativedelta


classProductTemplate(models.Model):
    _name='product.template'
    _inherit='product.template'

    property_account_creditor_price_difference=fields.Many2one(
        'account.account',string="PriceDifferenceAccount",company_dependent=True,
        help="Thisaccountisusedinautomatedinventoryvaluationto"\
             "recordthepricedifferencebetweenapurchaseorderanditsrelatedvendorbillwhenvalidatingthisvendorbill.")
    purchased_product_qty=fields.Float(compute='_compute_purchased_product_qty',string='Purchased')
    purchase_method=fields.Selection([
        ('purchase','Onorderedquantities'),
        ('receive','Onreceivedquantities'),
    ],string="ControlPolicy",help="Onorderedquantities:Controlbillsbasedonorderedquantities.\n"
        "Onreceivedquantities:Controlbillsbasedonreceivedquantities.",default="receive")
    purchase_line_warn=fields.Selection(WARNING_MESSAGE,'PurchaseOrderLineWarning',help=WARNING_HELP,required=True,default="no-message")
    purchase_line_warn_msg=fields.Text('MessageforPurchaseOrderLine')

    def_compute_purchased_product_qty(self):
        fortemplateinself:
            template.purchased_product_qty=float_round(sum([p.purchased_product_qtyforpintemplate.product_variant_ids]),precision_rounding=template.uom_id.rounding)

    @api.model
    defget_import_templates(self):
        res=super(ProductTemplate,self).get_import_templates()
        ifself.env.context.get('purchase_product_template'):
            return[{
                'label':_('ImportTemplateforProducts'),
                'template':'/purchase/static/xls/product_purchase.xls'
            }]
        returnres

    defaction_view_po(self):
        action=self.env["ir.actions.actions"]._for_xml_id("purchase.action_purchase_order_report_all")
        action['domain']=['&',('state','in',['purchase','done']),('product_tmpl_id','in',self.ids)]
        action['context']={
            'graph_measure':'qty_ordered',
            'search_default_later_than_a_year_ago':True
        }
        returnaction


classProductProduct(models.Model):
    _name='product.product'
    _inherit='product.product'

    purchased_product_qty=fields.Float(compute='_compute_purchased_product_qty',string='Purchased')

    def_compute_purchased_product_qty(self):
        date_from=fields.Datetime.to_string(fields.Date.context_today(self)-relativedelta(years=1))
        domain=[
            ('order_id.state','in',['purchase','done']),
            ('product_id','in',self.ids),
            ('order_id.date_approve','>=',date_from)
        ]
        order_lines=self.env['purchase.order.line'].read_group(domain,['product_id','product_uom_qty'],['product_id'])
        purchased_data=dict([(data['product_id'][0],data['product_uom_qty'])fordatainorder_lines])
        forproductinself:
            ifnotproduct.id:
                product.purchased_product_qty=0.0
                continue
            product.purchased_product_qty=float_round(purchased_data.get(product.id,0),precision_rounding=product.uom_id.rounding)

    defaction_view_po(self):
        action=self.env["ir.actions.actions"]._for_xml_id("purchase.action_purchase_order_report_all")
        action['domain']=['&',('state','in',['purchase','done']),('product_id','in',self.ids)]
        action['context']={
            'graph_measure':'qty_ordered',
            'search_default_later_than_a_year_ago':True
        }
        returnaction


classProductCategory(models.Model):
    _inherit="product.category"

    property_account_creditor_price_difference_categ=fields.Many2one(
        'account.account',string="PriceDifferenceAccount",
        company_dependent=True,
        help="Thisaccountwillbeusedtovaluepricedifferencebetweenpurchasepriceandaccountingcost.")


classProductSupplierinfo(models.Model):
    _inherit="product.supplierinfo"

    @api.onchange('name')
    def_onchange_name(self):
        self.currency_id=self.name.property_purchase_currency_id.idorself.env.company.currency_id.id
