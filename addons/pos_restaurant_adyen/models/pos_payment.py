#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importrequests

fromflectraimportmodels

TIMEOUT=10


classPosPayment(models.Model):
    _inherit='pos.payment'

    def_update_payment_line_for_tip(self,tip_amount):
        """Capturethepaymentwhenatipisset."""
        res=super(PosPayment,self)._update_payment_line_for_tip(tip_amount)
        ifself.payment_method_id.use_payment_terminal=='adyen':
            self._adyen_capture()
        returnres

    def_adyen_capture(self):
        data={
            'originalReference':self.transaction_id,
            'modificationAmount':{
                'value':int(self.amount*10**self.currency_id.decimal_places),
                'currency':self.currency_id.name,
            },
            'merchantAccount':self.payment_method_id.adyen_merchant_account,
        }

        returnself.payment_method_id.proxy_adyen_request(data,'capture')
