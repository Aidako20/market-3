#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classStockRule(models.Model):
    _inherit="stock.rule"

    def_push_prepare_move_copy_values(self,move_to_copy,new_date):
        new_move_vals=super(StockRule,self)._push_prepare_move_copy_values(move_to_copy,new_date)
        new_move_vals["is_subcontract"]=False
        returnnew_move_vals
