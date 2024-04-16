#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classMrpProduction(models.Model):
    _inherit='mrp.production'

    def_cal_price(self,consumed_moves):
        finished_move=self.move_finished_ids.filtered(lambdax:x.product_id==self.product_idandx.statenotin('done','cancel')andx.quantity_done>0)
        #Takethepriceunitofthereceptionmove
        last_done_receipt=finished_move.move_dest_ids.filtered(lambdam:m.state=='done')[-1:]
        iflast_done_receipt.is_subcontract:
            self.extra_cost=last_done_receipt._get_price_unit()
        returnsuper()._cal_price(consumed_moves=consumed_moves)
