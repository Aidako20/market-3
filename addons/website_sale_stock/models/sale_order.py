#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,api,fields
fromflectra.tools.translateimport_


classSaleOrder(models.Model):
    _inherit='sale.order'

    warning_stock=fields.Char('Warning')

    def_cart_update(self,product_id=None,line_id=None,add_qty=0,set_qty=0,**kwargs):
        values=super(SaleOrder,self)._cart_update(product_id,line_id,add_qty,set_qty,**kwargs)
        values=self._cart_lines_stock_update(values,**kwargs)
        returnvalues

    def_cart_lines_stock_update(self,values,**kwargs):
        line_id=values.get('line_id')
        forlineinself.order_line:
            ifline.product_id.type=='product'andline.product_id.inventory_availabilityin['always','threshold']:
                cart_qty=sum(self.order_line.filtered(lambdap:p.product_id.id==line.product_id.id).mapped('product_uom_qty'))
                if(line_id==line.id)andcart_qty>line.product_id.with_context(warehouse=self.warehouse_id.id).virtual_available:
                    qty=line.product_id.with_context(warehouse=self.warehouse_id.id).virtual_available-cart_qty
                    new_val=super(SaleOrder,self)._cart_update(line.product_id.id,line.id,qty,0,**kwargs)
                    values.update(new_val)

                    #Makesurelinestillexists,itmayhavebeendeletedinsuper()_cartupdatebecauseqtycanbe<=0
                    ifline.exists()andnew_val['quantity']:
                        line.warning_stock=_('Youaskfor%sproductsbutonly%sisavailable')%(cart_qty,new_val['quantity'])
                        values['warning']=line.warning_stock
                    else:
                        self.warning_stock=_("Someproductsbecameunavailableandyourcarthasbeenupdated.We'resorryfortheinconvenience.")
                        values['warning']=self.warning_stock
        returnvalues

    def_website_product_id_change(self,order_id,product_id,qty=0):
        res=super(SaleOrder,self)._website_product_id_change(order_id,product_id,qty=qty)
        product=self.env['product.product'].browse(product_id)
        res['customer_lead']=product.sale_delay
        returnres

    def_get_stock_warning(self,clear=True):
        self.ensure_one()
        warn=self.warning_stock
        ifclear:
            self.warning_stock=''
        returnwarn


classSaleOrderLine(models.Model):
    _inherit='sale.order.line'

    warning_stock=fields.Char('Warning')

    def_get_stock_warning(self,clear=True):
        self.ensure_one()
        warn=self.warning_stock
        ifclear:
            self.warning_stock=''
        returnwarn
