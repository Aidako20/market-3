#-*-coding:utf-8-*-
importlogging
importpprint
importwerkzeug

fromflectraimporthttp
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classTransferController(http.Controller):
    _accept_url='/payment/transfer/feedback'

    @http.route([
        '/payment/transfer/feedback',
    ],type='http',auth='public',csrf=False)
    deftransfer_form_feedback(self,**post):
        _logger.info('Beginningform_feedbackwithpostdata%s',pprint.pformat(post)) #debug
        request.env['payment.transaction'].sudo().form_feedback(post,'transfer')
        returnwerkzeug.utils.redirect('/payment/process')
