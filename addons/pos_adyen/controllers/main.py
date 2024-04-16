#coding:utf-8
importlogging
importpprint
importjson
fromflectraimportfields,http
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classPosAdyenController(http.Controller):
    @http.route('/pos_adyen/notification',type='json',methods=['POST'],auth='none',csrf=False)
    defnotification(self):
        data=json.loads(request.httprequest.data)

        #ignoreifit'snotaresponsetoasalesrequest
        ifnotdata.get('SaleToPOIResponse'):
            return

        _logger.info('notificationreceivedfromadyen:\n%s',pprint.pformat(data))
        terminal_identifier=data['SaleToPOIResponse']['MessageHeader']['POIID']
        payment_method=request.env['pos.payment.method'].sudo().search([('adyen_terminal_identifier','=',terminal_identifier)],limit=1)

        ifpayment_method:
            #Theseareonlyusedtoseeiftheterminalisreachable,
            #storethemostrecentIDwereceived.
            ifdata['SaleToPOIResponse'].get('DiagnosisResponse'):
                payment_method.adyen_latest_diagnosis=data['SaleToPOIResponse']['MessageHeader']['ServiceID']
            else:
                payment_method.adyen_latest_response=json.dumps(data)
            _logger.info('notificationwritedfromadyen\n%s',data)
        else:
            _logger.error('receivedamessageforaterminalnotregisteredinFlectra:%s',terminal_identifier)
