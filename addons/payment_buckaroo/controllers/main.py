#-*-coding:utf-8-*-

importlogging
importpprint
importwerkzeug

fromflectraimporthttp
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classBuckarooController(http.Controller):
    _return_url='/payment/buckaroo/return'
    _cancel_url='/payment/buckaroo/cancel'
    _exception_url='/payment/buckaroo/error'
    _reject_url='/payment/buckaroo/reject'

    @http.route([
        '/payment/buckaroo/return',
        '/payment/buckaroo/cancel',
        '/payment/buckaroo/error',
        '/payment/buckaroo/reject',
    ],type='http',auth='public',csrf=False)
    defbuckaroo_return(self,**post):
        """Buckaroo."""
        _logger.info('Buckaroo:enteringform_feedbackwithpostdata%s',pprint.pformat(post)) #debug
        request.env['payment.transaction'].sudo().form_feedback(post,'buckaroo')
        post={key.upper():valueforkey,valueinpost.items()}
        return_url=post.get('ADD_RETURNDATA')or'/'
        returnwerkzeug.utils.redirect('/payment/process')
