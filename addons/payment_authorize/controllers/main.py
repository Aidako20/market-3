#-*-coding:utf-8-*-
importpprint
importlogging
fromwerkzeugimporturls,utils

fromflectraimporthttp,_
fromflectra.httpimportrequest
fromflectra.exceptionsimportValidationError,UserError

_logger=logging.getLogger(__name__)


classAuthorizeController(http.Controller):
    _return_url='/payment/authorize/return/'
    _cancel_url='/payment/authorize/cancel/'

    @http.route([
        '/payment/authorize/return/',
        '/payment/authorize/cancel/',
    ],type='http',auth='public',csrf=False,save_session=False)
    defauthorize_form_feedback(self,**post):
        """ProcessthedatareturnedbyAuthorizeafterredirection.

        Therouteisflaggedwith`save_session=False`topreventFlectrafromassigninganewsession
        totheuseriftheyareredirectedtothisroutewithaPOSTrequest.Indeed,asthesession
        cookieiscreatedwithouta`SameSite`attribute,somebrowsersthatdon'timplementthe
        recommendeddefault`SameSite=Lax`behaviorwillnotincludethecookieintheredirection
        requestfromthepaymentprovidertoFlectra.Astheredirectiontothe'/payment/status'page
        willsatisfyanyspecificationofthe`SameSite`attribute,thesessionoftheuserwillbe
        retrievedandwithitthetransactionwhichwillbeimmediatelypost-processed.
        """
        _logger.info('Authorize:enteringform_feedbackwithpostdata%s',pprint.pformat(post))
        ifpost:
            request.env['payment.transaction'].sudo().form_feedback(post,'authorize')
        base_url=request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #Authorize.NetisexpectingaresponsetothePOSTsentbytheirserver.
        #ThisresponseisintheformofaURLthatAuthorize.Netwillpassontothe
        #client'sbrowsertoredirectthemtothedesiredlocationneedjavascript.
        returnrequest.render('payment_authorize.payment_authorize_redirect',{
            'return_url':urls.url_join(base_url,"/payment/process")
        })

    @http.route(['/payment/authorize/s2s/create_json_3ds'],type='json',auth='public',csrf=False)
    defauthorize_s2s_create_json_3ds(self,verify_validity=False,**kwargs):
        token=False
        acquirer=request.env['payment.acquirer'].browse(int(kwargs.get('acquirer_id')))

        try:
            ifnotkwargs.get('partner_id'):
                kwargs=dict(kwargs,partner_id=request.env.user.partner_id.id)
            token=acquirer.s2s_process(kwargs)
        exceptValidationErrorase:
            message=e.args[0]
            ifisinstance(message,dict)and'missing_fields'inmessage:
                ifrequest.env.user._is_public():
                    message=_("Pleasesignintocompletethepayment.")
                    #updatemessageifportalmode=b2b
                    ifrequest.env['ir.config_parameter'].sudo().get_param('auth_signup.allow_uninvited','False').lower()=='false':
                        message+=_("Ifyoudon'thaveanyaccount,askyoursalespersontograntyouaportalaccess.")
                else:
                    msg=_("Thetransactioncannotbeprocessedbecausesomecontactdetailsaremissingorinvalid:")
                    message=msg+','.join(message['missing_fields'])+'.'
                    message+=_("Pleasecompleteyourprofile.")

            return{
                'error':message
            }

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
            'verified':True,#Authorize.netdoesatransactiontypeofAuthorizationOnly
                              #AsAuthorize.netalreadyverifythiscard,wedonotverifythiscardagain.
        }
        #token.validate()don'tworkwithAuthorize.net.
        #PaymentsmadeviaAuthorize.netaresettledandallowedtoberefundedonlyonthenextday.
        #https://account.authorize.net/help/Miscellaneous/FAQ/Frequently_Asked_Questions.htm#Refund
        #<quote>TheoriginaltransactionthatyouwishtorefundmusthaveastatusofSettledSuccessfully.
        #Youcannotissuerefundsagainstunsettled,voided,declinedorerroredtransactions.</quote>
        returnres

    @http.route(['/payment/authorize/s2s/create'],type='http',auth='public',save_session=False)
    defauthorize_s2s_create(self,**post):
        acquirer_id=int(post.get('acquirer_id'))
        acquirer=request.env['payment.acquirer'].browse(acquirer_id)
        acquirer.s2s_process(post)
        returnutils.redirect("/payment/process")
