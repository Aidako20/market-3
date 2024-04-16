#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importlogging
importpprint

fromflectraimporthttp
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classFlectraByAdyenController(http.Controller):
    _notification_url='/payment/flectra_adyen/notification'

    @http.route('/payment/flectra_adyen/notification',type='json',auth='public',csrf=False)
    defflectra_adyen_notification(self):
        data=json.loads(request.httprequest.data)
        _logger.info('BeginningFlectrabyAdyenform_feedbackwithdata%s',pprint.pformat(data))
        ifdata.get('authResult')notin['CANCELLED']:
            request.env['payment.transaction'].sudo().form_feedback(data,'flectra_adyen')
