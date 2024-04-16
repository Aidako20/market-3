#coding:utf-8
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classPosPaymentMethod(models.Model):
    _inherit='pos.payment.method'

    adyen_merchant_account=fields.Char(help='ThePOSmerchantaccountcodeusedinAdyen')

    def_get_adyen_endpoints(self):
        return{
            **super(PosPaymentMethod,self)._get_adyen_endpoints(),
            'adjust':'https://pal-%s.adyen.com/pal/servlet/Payment/v52/adjustAuthorisation',
            'capture':'https://pal-%s.adyen.com/pal/servlet/Payment/v52/capture',
        }
