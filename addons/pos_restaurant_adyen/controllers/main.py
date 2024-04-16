#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.addons.payment_adyen.controllers.mainimportAdyenController

_logger=logging.getLogger(__name__)


classPosRestaurantAdyenController(AdyenController):

    @http.route()
    defadyen_notification(self,**post):
        ifpost.get('eventCode')in['CAPTURE','AUTHORISATION_ADJUSTMENT']andpost.get('success')!='true':
                _logger.warning('%sfortransaction_id%sfailed',post.get('eventCode'),post.get('originalReference'))
        returnsuper(PosRestaurantAdyenController,self).adyen_notification(**post)
