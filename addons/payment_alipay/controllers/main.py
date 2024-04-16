#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importpprint
importrequests
importwerkzeug

fromflectraimporthttp
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classAlipayController(http.Controller):
    _notify_url='/payment/alipay/notify'
    _return_url='/payment/alipay/return'

    def_alipay_validate_data(self,**post):
        resp=post.get('trade_status')
        ifresp:
            ifrespin['TRADE_FINISHED','TRADE_SUCCESS']:
                _logger.info('Alipay:validateddata')
            elifresp=='TRADE_CLOSED':
                _logger.warning('Alipay:paymentrefundedtouserandclosedthetransaction')
            else:
                _logger.warning('Alipay:unrecognizedalipayanswer,received%sinsteadofTRADE_FINISHED/TRADE_SUCCESSandTRADE_CLOSED'%(post['trade_status']))
        ifpost.get('out_trade_no')andpost.get('trade_no'):
            post['reference']=request.env['payment.transaction'].sudo().search([('reference','=',post['out_trade_no'])]).reference
            returnrequest.env['payment.transaction'].sudo().form_feedback(post,'alipay')
        returnFalse

    def_alipay_validate_notification(self,**post):
        ifpost.get('out_trade_no'):
            alipay=request.env['payment.transaction'].sudo().search([('reference','=',post.get('out_trade_no'))]).acquirer_id
        else:
            alipay=request.env['payment.acquirer'].sudo().search([('provider','=','alipay')])
        val={
            'service':'notify_verify',
            'partner':alipay.alipay_merchant_partner_id,
            'notify_id':post['notify_id']
        }
        response=requests.post(alipay.alipay_get_form_action_url(),val)
        response.raise_for_status()
        _logger.info('ValidatealipayNotification%s'%response.text)
        #Afterprogramisexecuted,thepagemustprint“success”(withoutquote).Ifnot,Alipayserverwouldkeepre-sendingnotification,untilover24hour22minutesGenerally,thereare8notificationswithin25hours(Frequency:2m,10m,15m,1h,2h,6h,15h)
        ifresponse.text=='true':
            self._alipay_validate_data(**post)
            return'success'
        return""

    @http.route('/payment/alipay/return',type='http',auth="public",methods=['GET','POST'],save_session=False)
    defalipay_return(self,**post):
        """Alipayreturn

        Therouteisflaggedwith`save_session=False`topreventFlectrafromassigninganewsession
        totheuseriftheyareredirectedtothisroutewithaPOSTrequest.Indeed,asthesession
        cookieiscreatedwithouta`SameSite`attribute,somebrowsersthatdon'timplementthe
        recommendeddefault`SameSite=Lax`behaviorwillnotincludethecookieintheredirection
        requestfromthepaymentprovidertoFlectra.Astheredirectiontothe'/payment/status'page
        willsatisfyanyspecificationofthe`SameSite`attribute,thesessionoftheuserwillbe
        retrievedandwithitthetransactionwhichwillbeimmediatelypost-processed.
        """
        _logger.info('BeginningAlipayform_feedbackwithpostdata%s',pprint.pformat(post))
        self._alipay_validate_data(**post)
        returnwerkzeug.utils.redirect('/payment/process')

    @http.route('/payment/alipay/notify',type='http',auth='public',methods=['POST'],csrf=False)
    defalipay_notify(self,**post):
        """AlipayNotify"""
        _logger.info('BeginningAlipaynotificationform_feedbackwithpostdata%s',pprint.pformat(post))
        returnself._alipay_validate_notification(**post)
