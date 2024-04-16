#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classPosOrder(models.Model):
    _inherit='pos.order'

    defaction_pos_order_paid(self):
        res=super(PosOrder,self).action_pos_order_paid()
        ifnotself.config_id.set_tip_after_payment:
            payment_lines=self.payment_ids.filtered(lambdaline:line.payment_method_id.use_payment_terminal=='adyen')
            forpayment_lineinpayment_lines:
                payment_line._adyen_capture()
        returnres
