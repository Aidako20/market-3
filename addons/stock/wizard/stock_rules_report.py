#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classStockRulesReport(models.TransientModel):
    _name='stock.rules.report'
    _description='StockRulesreport'

    product_id=fields.Many2one('product.product',string='Product',required=True)
    product_tmpl_id=fields.Many2one('product.template',string='ProductTemplate',required=True)
    warehouse_ids=fields.Many2many('stock.warehouse',string='Warehouses',required=True,
        help="Showtheroutesthatapplyonselectedwarehouses.")
    product_has_variants=fields.Boolean('Hasvariants',default=False,required=True)

    @api.model
    defdefault_get(self,fields):
        res=super(StockRulesReport,self).default_get(fields)
        product_tmpl_id=self.env['product.template']
        if'product_id'infields:
            ifself.env.context.get('default_product_id'):
                product_id=self.env['product.product'].browse(self.env.context['default_product_id'])
                product_tmpl_id=product_id.product_tmpl_id
                res['product_tmpl_id']=product_id.product_tmpl_id.id
                res['product_id']=product_id.id
            elifself.env.context.get('default_product_tmpl_id'):
                product_tmpl_id=self.env['product.template'].browse(self.env.context['default_product_tmpl_id'])
                res['product_tmpl_id']=product_tmpl_id.id
                res['product_id']=product_tmpl_id.product_variant_id.id
                iflen(product_tmpl_id.product_variant_ids)>1:
                    res['product_has_variants']=True
        if'warehouse_ids'infields:
            company=product_tmpl_id.company_idorself.env.company
            warehouse_id=self.env['stock.warehouse'].search([('company_id','=',company.id)],limit=1).id
            res['warehouse_ids']=[(6,0,[warehouse_id])]
        returnres

    def_prepare_report_data(self):
        data={
            'product_id':self.product_id.id,
            'warehouse_ids':self.warehouse_ids.ids,
        }
        returndata

    defprint_report(self):
        self.ensure_one()
        data=self._prepare_report_data()
        returnself.env.ref('stock.action_report_stock_rule').report_action(None,data=data)

