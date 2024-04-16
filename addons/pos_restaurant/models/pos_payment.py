#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classPosConfig(models.Model):
    _inherit='pos.payment'

    def_update_payment_line_for_tip(self,tip_amount):
        """Inheritthismethodtoperformreauthorizationorcaptureonelectronicpayment."""
        self.ensure_one()
        self.write({
            "amount":self.amount+tip_amount,
        })
