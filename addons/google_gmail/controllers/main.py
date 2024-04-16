#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importlogging
importwerkzeug

fromwerkzeug.exceptionsimportForbidden
fromwerkzeug.urlsimporturl_encode

fromflectraimport_,http
fromflectra.exceptionsimportUserError
fromflectra.httpimportrequest
fromflectra.toolsimportconsteq

_logger=logging.getLogger(__name__)


classGoogleGmailController(http.Controller):
    @http.route('/google_gmail/confirm',type='http',auth='user')
    defgoogle_gmail_callback(self,code=None,state=None,error=None,**kwargs):
        """CallbackURLduringtheOAuthprocess.

        Gmailredirectstheuserbrowsertothisendpointwiththeauthorizationcode.
        Wewillfetchtherefreshtokenandtheaccesstokenthankstothisauthorization
        codeandsavethosevaluesonthegivenmailserver.
        """
        ifnotrequest.env.user.has_group('base.group_system'):
            _logger.error('GoogleGmail:non-systemusertryingtolinkanGmailaccount.')
            raiseForbidden()

        iferror:
            return_('Anerroroccurduringtheauthenticationprocess.')

        try:
            state=json.loads(state)
            model_name=state['model']
            rec_id=state['id']
            csrf_token=state['csrf_token']
        exceptException:
            _logger.error('GoogleGmail:Wrongstatevalue%r.',state)
            raiseForbidden()

        model=request.env[model_name]

        ifnotisinstance(model,request.env.registry['google.gmail.mixin']):
            #Themodelmustinheritsfromthe"google.gmail.mixin"mixin
            raiseForbidden()

        record=model.browse(rec_id).exists()
        ifnotrecord:
            raiseForbidden()

        ifnotcsrf_tokenornotconsteq(csrf_token,record._get_gmail_csrf_token()):
            _logger.error('GoogleGmail:WrongCSRFtokenduringGmailauthentication.')
            raiseForbidden()

        try:
            refresh_token,access_token,expiration=record._fetch_gmail_refresh_token(code)
        exceptUserError:
            return_('Anerroroccurduringtheauthenticationprocess.')

        record.write({
            'google_gmail_access_token':access_token,
            'google_gmail_access_token_expiration':expiration,
            'google_gmail_authorization_code':code,
            'google_gmail_refresh_token':refresh_token,
        })

        url_params={
            'id':rec_id,
            'model':model_name,
            'view_type':'form'
        }
        url='/web?#'+url_encode(url_params)
        returnwerkzeug.utils.redirect(url,303)
