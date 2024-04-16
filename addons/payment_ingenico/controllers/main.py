#-*-coding:utf-8-*-
importlogging
importpprint
importwerkzeug
fromwerkzeug.urlsimporturl_unquote_plus

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.addons.payment.models.payment_acquirerimportValidationError
fromflectra.addons.payment.controllers.portalimportPaymentProcessing

_logger=logging.getLogger(__name__)


classOgoneController(http.Controller):
    _accept_url='/payment/ogone/test/accept'
    _decline_url='/payment/ogone/test/decline'
    _exception_url='/payment/ogone/test/exception'
    _cancel_url='/payment/ogone/test/cancel'

    @http.route([
        '/payment/ogone/accept','/payment/ogone/test/accept',
        '/payment/ogone/decline','/payment/ogone/test/decline',
        '/payment/ogone/exception','/payment/ogone/test/exception',
        '/payment/ogone/cancel','/payment/ogone/test/cancel',
    ],type='http',auth='public',csrf=False)
    defogone_form_feedback(self,**post):
        """HandlebothredirectionfromIngenico(GET)ands2snotification(POST/GET)"""
        _logger.info('Ogone:enteringform_feedbackwithpostdata%s',pprint.pformat(post)) #debug
        request.env['payment.transaction'].sudo().form_feedback(post,'ogone')
        returnwerkzeug.utils.redirect("/payment/process")

    @http.route(['/payment/ogone/s2s/create_json'],type='json',auth='public',csrf=False)
    defogone_s2s_create_json(self,**kwargs):
        ifnotkwargs.get('partner_id'):
            kwargs=dict(kwargs,partner_id=request.env.user.partner_id.id)
        new_id=request.env['payment.acquirer'].browse(int(kwargs.get('acquirer_id'))).s2s_process(kwargs)
        returnnew_id.id

    @http.route(['/payment/ogone/s2s/create_json_3ds'],type='json',auth='public',csrf=False)
    defogone_s2s_create_json_3ds(self,verify_validity=False,**kwargs):
        ifnotkwargs.get('partner_id'):
            kwargs=dict(kwargs,partner_id=request.env.user.partner_id.id)
        token=False
        error=None

        try:
            token=request.env['payment.acquirer'].browse(int(kwargs.get('acquirer_id'))).s2s_process(kwargs)
        exceptExceptionase:
            error=str(e)

        ifnottoken:
            res={
                'result':False,
                'error':error,
            }
            returnres

        res={
            'result':True,
            'id':token.id,
            'short_name':token.short_name,
            '3d_secure':False,
            'verified':False,
        }

        ifverify_validity!=False:
            baseurl=request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            params={
                'accept_url':baseurl+'/payment/ogone/validate/accept',
                'decline_url':baseurl+'/payment/ogone/validate/decline',
                'exception_url':baseurl+'/payment/ogone/validate/exception',
                'return_url':kwargs.get('return_url',baseurl)
                }
            tx=token.validate(**params)
            res['verified']=token.verified

            iftxandtx.html_3ds:
                res['3d_secure']=tx.html_3ds

        returnres

    @http.route(['/payment/ogone/s2s/create'],type='http',auth='public',methods=["POST"],csrf=False)
    defogone_s2s_create(self,**post):
        error=''
        acq=request.env['payment.acquirer'].browse(int(post.get('acquirer_id')))
        try:
            token=acq.s2s_process(post)
        exceptExceptionase:
            #synthaxerror:'CHECKERROR:|Notavaliddate\n\n50001111:None'
            token=False
            error=str(e).splitlines()[0].split('|')[-1]or''

        iftokenandpost.get('verify_validity'):
            baseurl=request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            params={
                'accept_url':baseurl+'/payment/ogone/validate/accept',
                'decline_url':baseurl+'/payment/ogone/validate/decline',
                'exception_url':baseurl+'/payment/ogone/validate/exception',
                'return_url':post.get('return_url',baseurl)
                }
            tx=token.validate(**params)
            iftxandtx.html_3ds:
                returntx.html_3ds
            #addthepaymenttransactionintothesessiontoletthepage/payment/processtohandleit
            PaymentProcessing.add_payment_transaction(tx)
        returnwerkzeug.utils.redirect("/payment/process")

    @http.route([
        '/payment/ogone/validate/accept',
        '/payment/ogone/validate/decline',
        '/payment/ogone/validate/exception',
    ],type='http',auth='public')
    defogone_validation_form_feedback(self,**post):
        """Feedbackfrom3dsecureforabankcardvalidation"""
        request.env['payment.transaction'].sudo().form_feedback(post,'ogone')
        returnwerkzeug.utils.redirect("/payment/process")

    @http.route(['/payment/ogone/s2s/feedback'],auth='public',csrf=False)
    deffeedback(self,**kwargs):
        try:
            tx=request.env['payment.transaction'].sudo()._ogone_form_get_tx_from_data(kwargs)
            tx._ogone_s2s_validate_tree(kwargs)
        exceptValidationError:
            return'ko'
        return'ok'
