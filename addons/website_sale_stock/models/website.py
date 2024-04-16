#-*-coding:utf-8-*-
fromflectraimportapi,fields,models


classWebsite(models.Model):
    _inherit='website'

    warehouse_id=fields.Many2one('stock.warehouse',string='Warehouse')

    def_prepare_sale_order_values(self,partner,pricelist):
        self.ensure_one()
        values=super(Website,self)._prepare_sale_order_values(partner,pricelist)
        ifvalues['company_id']:
            warehouse_id=self._get_warehouse_available()
            ifwarehouse_id:
                values['warehouse_id']=warehouse_id
        returnvalues

    def_get_warehouse_available(self):
        return(
            self.warehouse_idandself.warehouse_id.idor
            self.env['ir.default'].get('sale.order','warehouse_id',company_id=self.company_id.id)or
            self.env['ir.default'].get('sale.order','warehouse_id')or
            self.env['stock.warehouse'].sudo().search([('company_id','=',self.company_id.id)],limit=1).id
        )

    defsale_get_order(self,force_create=False,code=None,update_pricelist=False,force_pricelist=False):
        so=super().sale_get_order(force_create=force_create,code=code,update_pricelist=update_pricelist,force_pricelist=force_pricelist)
        returnso.with_context(warehouse=so.warehouse_id.id)ifsoelseso
