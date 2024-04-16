#-*-coding:utf-8-*-
importjson
importlogging
importpprint
importwerkzeug

fromflectraimporthttp
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classStripeController(http.Controller):
    _success_url='/payment/stripe/success'
    _cancel_url='/payment/stripe/cancel'

    @http.route(['/payment/stripe/success','/payment/stripe/cancel'],type='http',auth='public')
    defstripe_success(self,**kwargs):
        request.env['payment.transaction'].sudo().form_feedback(kwargs,'stripe')
        returnwerkzeug.utils.redirect('/payment/process')

    @http.route(['/payment/stripe/s2s/create_json_3ds'],type='json',auth='public',csrf=False)
    defstripe_s2s_create_json_3ds(self,verify_validity=False,**kwargs):
        ifnotkwargs.get('partner_id'):
            kwargs=dict(kwargs,partner_id=request.env.user.partner_id.id)
        token=request.env['payment.acquirer'].browse(int(kwargs.get('acquirer_id'))).with_context(stripe_manual_payment=True).s2s_process(kwargs)

        ifnottoken:
            res={
                'result':False,
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
            token.validate()
            res['verified']=token.verified

        returnres

    @http.route('/payment/stripe/s2s/create_setup_intent',type='json',auth='public',csrf=False)
    defstripe_s2s_create_setup_intent(self,acquirer_id,**kwargs):
        acquirer=request.env['payment.acquirer'].browse(int(acquirer_id))
        res=acquirer.with_context(stripe_manual_payment=True)._create_setup_intent(kwargs)
        returnres.get('client_secret')

    @http.route('/payment/stripe/s2s/process_payment_intent',type='json',auth='public',csrf=False)
    defstripe_s2s_process_payment_intent(self,**post):
        returnrequest.env['payment.transaction'].sudo().form_feedback(post,'stripe')

    @http.route('/payment/stripe/s2s/process_payment_error',type='json',auth='public',csrf=False)
    defstripe_s2s_process_payment_error(self,**post):
        transaction_sudo=request.env['payment.transaction'].sudo().search([('reference','=',post['reference']),
                                                                            ('provider','=','stripe'),
                                                                            ('stripe_payment_intent_secret','=',post['stripe_payment_intent_secret'])])
        transaction_sudo.write({'state':'error','state_message':post['error']})

    @http.route('/payment/stripe/webhook',type='json',auth='public',csrf=False)
    defstripe_webhook(self,**kwargs):
        data=json.loads(request.httprequest.data)
        request.env['payment.acquirer'].sudo()._handle_stripe_webhook(data)
        return'OK'