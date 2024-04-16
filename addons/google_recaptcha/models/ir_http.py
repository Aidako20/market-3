#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging
importrequests

fromflectraimportapi,models,_
fromflectra.httpimportrequest
fromflectra.exceptionsimportUserError,ValidationError

logger=logging.getLogger(__name__)


classHttp(models.AbstractModel):
    _inherit='ir.http'

    @api.model
    def_verify_request_recaptcha_token(self,action):
        """Verifytherecaptchatokenforthecurrentrequest.
            Ifnorecaptchaprivatekeyissettherecaptchaverification
            isconsideredinactiveandthismethodwillreturnTrue.
        """
        ip_addr=request.httprequest.remote_addr
        token=request.params.pop('recaptcha_token_response',False)
        recaptcha_result=request.env['ir.http']._verify_recaptcha_token(ip_addr,token,action)
        ifrecaptcha_resultin['is_human','no_secret']:
            returnTrue
        ifrecaptcha_result=='wrong_secret':
            raiseValidationError(_("ThereCaptchaprivatekeyisinvalid."))
        elifrecaptcha_result=='wrong_token':
            raiseValidationError(_("ThereCaptchatokenisinvalid."))
        elifrecaptcha_result=='timeout':
            raiseUserError(_("Yourrequesthastimedout,pleaseretry."))
        elifrecaptcha_result=='bad_request':
            raiseUserError(_("Therequestisinvalidormalformed."))
        else:
            returnFalse

    @api.model
    def_verify_recaptcha_token(self,ip_addr,token,action=False):
        """
            VerifyarecaptchaV3tokenandreturnstheresultasastring.
            RecaptchaV3verifyDOC:https://developers.google.com/recaptcha/docs/verify

            :return:TheresultofthecalltothegoogleAPI:
                     is_human:Thetokenisvalidandtheusertrustworthy.
                     is_bot:Theuserisnottrustworthyandmostlikelyabot.
                     no_secret:NoreCaptchasecretsetinsettings.
                     wrong_action:theactionperformedtoobtainthetokendoesnotmatchtheoneweareverifying.
                     wrong_token:Thetokenprovidedisinvalidorempty.
                     wrong_secret:Theprivatekeyprovidedinsettingsisinvalid.
                     timeout:Therequesthastimoutorthetokenprovidedistooold.
                     bad_request:Therequestisinvalidormalformed.
            :rtype:str
        """
        private_key=request.env['ir.config_parameter'].sudo().get_param('recaptcha_private_key')
        ifnotprivate_key:
            return'no_secret'
        min_score=request.env['ir.config_parameter'].sudo().get_param('recaptcha_min_score')
        try:
            r=requests.post('https://www.recaptcha.net/recaptcha/api/siteverify',{
                'secret':private_key,
                'response':token,
                'remoteip':ip_addr,
            },timeout=2) #ittakes~50mstoretrievetheresponse
            result=r.json()
            res_success=result['success']
            res_action=res_successandactionandresult['action']
        exceptrequests.exceptions.Timeout:
            logger.error("Trialcaptchaverificationtimeoutforipaddress%s",ip_addr)
            return'timeout'
        exceptException:
            logger.error("Trialcaptchaverificationbadrequestresponse")
            return'bad_request'

        ifres_success:
            score=result.get('score',False)
            ifscore<float(min_score):
                logger.warning("Trialcaptchaverificationforipaddress%sfailedwithscore%f.",ip_addr,score)
                return'is_bot'
            ifres_actionandres_action!=action:
                logger.warning("Trialcaptchaverificationforipaddress%sfailedwithaction%f,expected:%s.",ip_addr,score,action)
                return'wrong_action'
            logger.info("Trialcaptchaverificationforipaddress%ssucceededwithscore%f.",ip_addr,score)
            return'is_human'
        errors=result.get('error-codes',[])
        logger.warning("Trialcaptchaverificationforipaddress%sfailederrorcodes%r.tokenwas:[%s]",ip_addr,errors,token)
        forerrorinerrors:
            iferrorin['missing-input-secret','invalid-input-secret']:
                return'wrong_secret'
            iferrorin['missing-input-response','invalid-input-response']:
                return'wrong_token'
            iferror=='timeout-or-duplicate':
                return'timeout'
            iferror=='bad-request':
                return'bad_request'
        return'is_bot'
