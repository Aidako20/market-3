#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,fields,models,_


classStockMove(models.Model):
    _inherit="stock.move"

    def_is_returned(self,valued_type):
        ifself.unbuild_id:
            returnTrue
        returnsuper()._is_returned(valued_type)

    def_get_src_account(self,accounts_data):
        ifnotself.unbuild_id:
            returnsuper()._get_src_account(accounts_data)
        else:
            returnself.location_dest_id.valuation_out_account_id.idoraccounts_data['stock_input'].id

    def_get_dest_account(self,accounts_data):
        ifnotself.unbuild_id:
            returnsuper()._get_dest_account(accounts_data)
        else:
            returnself.location_id.valuation_in_account_id.idoraccounts_data['stock_output'].id

    def_filter_anglo_saxon_moves(self,product):
        res=super(StockMove,self)._filter_anglo_saxon_moves(product)
        res+=self.filtered(lambdam:m.bom_line_id.bom_id.product_tmpl_id.id==product.product_tmpl_id.id)
        returnres

    def_should_force_price_unit(self):
        self.ensure_one()
        returnself.picking_type_id.code=='mrp_operation'orsuper()._should_force_price_unit()
