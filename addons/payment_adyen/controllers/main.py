#-*-coding:utf-8-*-

importjson
importlogging
importpprint
importwerkzeug

fromflectraimporthttp
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classAdyenController(http.Controller):
    _return_url='/payment/adyen/return/'

    @http.route([
        '/payment/adyen/return',
    ],type='http',auth='public',csrf=False)
    defadyen_return(self,**post):
        _logger.info('BeginningAdyenform_feedbackwithpostdata%s',pprint.pformat(post)) #debug
        ifpost.get('authResult')notin['CANCELLED']:
            request.env['payment.transaction'].sudo().form_feedback(post,'adyen')
        returnwerkzeug.utils.redirect('/payment/process')

    @http.route([
        '/payment/adyen/notification',
    ],type='http',auth='public',methods=['POST'],csrf=False)
    defadyen_notification(self,**post):
        tx=post.get('merchantReference')andrequest.env['payment.transaction'].sudo().search([('reference','in',[post.get('merchantReference')])],limit=1)
        ifpost.get('eventCode')in['AUTHORISATION']andtx:
            states=(post.get('merchantReference'),post.get('success'),tx.state)
            if(post.get('success')=='true'andtx.state=='done')or(post.get('success')=='false'andtx.statein['cancel','error']):
                _logger.info('NotificationfromAdyenforthereference%s:received%s,stateis%s',states)
            else:
                _logger.warning('NotificationfromAdyenforthereference%s:received%sbutstateis%s',states)
        return'[accepted]'
