#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importpprint
importwerkzeug

fromflectraimporthttp
fromflectra.exceptionsimportValidationError
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classPayuLatamController(http.Controller):

    @http.route('/payment/payulatam/response',type='http',auth='public',csrf=False)
    defpayulatam_response(self,**post):
        """PayUlatam."""
        _logger.info('PayULatam:enteringform_feedbackwithpostresponsedata%s',pprint.pformat(post))
        ifpost:
            request.env['payment.transaction'].sudo().form_feedback(post,'payulatam')
        returnwerkzeug.utils.redirect('/payment/process')

    @http.route('/payment/payulatam/webhook',type='http',auth='public',methods=['POST'],csrf=False)
    defpayulatam_webhook(self,**data):
        _logger.info("handlingconfirmationfromPayULatamwithdata:\n%s",pprint.pformat(data))
        state_pol=data.get('state_pol')
        ifstate_pol=='4':
            lapTransactionState='APPROVED'
        elifstate_pol=='6':
            lapTransactionState='DECLINED'
        elifstate_pol=='5':
            lapTransactionState='EXPIRED'
        else:
            lapTransactionState=f'INVALIDstate_pol{state_pol}'

        data={
            'signature':data.get('sign'),
            'TX_VALUE':data.get('value'),
            'currency':data.get('currency'),
            'referenceCode':data.get('reference_sale'),
            'transactionId':data.get('transaction_id'),
            'transactionState':data.get('state_pol'),
            'message':data.get('response_message_pol'),
            'lapTransactionState':lapTransactionState,
            'merchantId':data.get('merchant_id'),
        }

        try:
            request.env['payment.transaction'].sudo().with_context(
                payulatam_is_confirmation_page=True
            ).form_feedback(data,'payulatam')
        exceptValidationError:
            _logger.exception(
                'AnerroroccurredwhilehandlingtheconfirmationfromPayUwithdata:\n%s',
                pprint.pformat(data))
        returnhttp.Response(status=200)
