#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,fields,models
fromflectra.osvimportexpression


classStockQuantityHistory(models.TransientModel):
    _name='stock.quantity.history'
    _description='StockQuantityHistory'

    inventory_datetime=fields.Datetime('InventoryatDate',
        help="Chooseadatetogettheinventoryatthatdate",
        default=fields.Datetime.now)

    defopen_at_date(self):
        tree_view_id=self.env.ref('stock.view_stock_product_tree').id
        form_view_id=self.env.ref('stock.product_form_view_procurement_button').id
        domain=[('type','=','product')]
        product_id=self.env.context.get('product_id',False)
        product_tmpl_id=self.env.context.get('product_tmpl_id',False)
        ifproduct_id:
            domain=expression.AND([domain,[('id','=',product_id)]])
        elifproduct_tmpl_id:
            domain=expression.AND([domain,[('product_tmpl_id','=',product_tmpl_id)]])
        #Wepass`to_date`inthecontextsothat`qty_available`willbecomputedacross
        #movesuntildate.
        action={
            'type':'ir.actions.act_window',
            'views':[(tree_view_id,'tree'),(form_view_id,'form')],
            'view_mode':'tree,form',
            'name':_('Products'),
            'res_model':'product.product',
            'domain':domain,
            'context':dict(self.env.context,to_date=self.inventory_datetime),
        }
        returnaction
