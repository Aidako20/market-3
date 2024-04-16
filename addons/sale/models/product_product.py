#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimporttimedelta,time
fromflectraimportapi,fields,models,_
fromflectra.tools.float_utilsimportfloat_round


classProductProduct(models.Model):
    _inherit='product.product'

    sales_count=fields.Float(compute='_compute_sales_count',string='Sold')

    def_compute_sales_count(self):
        r={}
        self.sales_count=0
        ifnotself.user_has_groups('sales_team.group_sale_salesman'):
            returnr
        date_from=fields.Datetime.to_string(fields.datetime.combine(fields.datetime.now()-timedelta(days=365),
                                                                      time.min))

        done_states=self.env['sale.report']._get_done_states()

        domain=[
            ('state','in',done_states),
            ('product_id','in',self.ids),
            ('date','>=',date_from),
        ]
        forgroupinself.env['sale.report'].read_group(domain,['product_id','product_uom_qty'],['product_id']):
            r[group['product_id'][0]]=group['product_uom_qty']
        forproductinself:
            ifnotproduct.id:
                product.sales_count=0.0
                continue
            product.sales_count=float_round(r.get(product.id,0),precision_rounding=product.uom_id.rounding)
        returnr

    @api.onchange('type')
    def_onchange_type(self):
        ifself._originandself.sales_count>0:
            return{'warning':{
                'title':_("Warning"),
                'message':_("Youcannotchangetheproduct'stypebecauseitisalreadyusedinsalesorders.")
            }}

    defaction_view_sales(self):
        action=self.env["ir.actions.actions"]._for_xml_id("sale.report_all_channels_sales_action")
        action['domain']=[('product_id','in',self.ids)]
        action['context']={
            'pivot_measures':['product_uom_qty'],
            'active_id':self._context.get('active_id'),
            'search_default_Sales':1,
            'active_model':'sale.report',
            'search_default_filter_order_date':1,
        }
        returnaction

    def_get_invoice_policy(self):
        returnself.invoice_policy

    def_get_combination_info_variant(self,add_qty=1,pricelist=False,parent_combination=False):
        """Returnthevariantinfobasedonitscombination.
        See`_get_combination_info`formoreinformation.
        """
        self.ensure_one()
        returnself.product_tmpl_id._get_combination_info(self.product_template_attribute_value_ids,self.id,add_qty,pricelist,parent_combination)

    def_filter_to_unlink(self):
        domain=[('product_id','in',self.ids)]
        lines=self.env['sale.order.line'].read_group(domain,['product_id'],['product_id'])
        linked_product_ids=[group['product_id'][0]forgroupinlines]
        returnsuper(ProductProduct,self-self.browse(linked_product_ids))._filter_to_unlink()


classProductAttributeCustomValue(models.Model):
    _inherit="product.attribute.custom.value"

    sale_order_line_id=fields.Many2one('sale.order.line',string="SalesOrderLine",required=True,ondelete='cascade')

    _sql_constraints=[
        ('sol_custom_value_unique','unique(custom_product_template_attribute_value_id,sale_order_line_id)',"OnlyoneCustomValueisallowedperAttributeValueperSalesOrderLine.")
    ]
