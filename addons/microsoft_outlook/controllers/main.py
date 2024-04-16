#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importlogging
importwerkzeug

fromwerkzeug.exceptionsimportForbidden

fromflectraimporthttp
fromflectra.exceptionsimportUserError
fromflectra.httpimportrequest
fromflectra.toolsimportconsteq

_logger=logging.getLogger(__name__)


classMicrosoftOutlookController(http.Controller):
    @http.route('/microsoft_outlook/confirm',type='http',auth='user')
    defmicrosoft_outlook_callback(self,code=None,state=None,error_description=None,**kwargs):
        """CallbackURLduringtheOAuthprocess.

        Outlookredirectstheuserbrowsertothisendpointwiththeauthorizationcode.
        Wewillfetchtherefreshtokenandtheaccesstokenthankstothisauthorization
        codeandsavethosevaluesonthegivenmailserver.
        """
        ifnotrequest.env.user.has_group('base.group_system'):
            _logger.error('MicrosoftOutlook:NonsystemusertrytolinkanOutlookaccount.')
            raiseForbidden()

        try:
            state=json.loads(state)
            model_name=state['model']
            rec_id=state['id']
            csrf_token=state['csrf_token']
        exceptException:
            _logger.error('MicrosoftOutlook:Wrongstatevalue%r.',state)
            raiseForbidden()

        iferror_description:
            returnrequest.render('microsoft_outlook.microsoft_outlook_oauth_error',{
                'error':error_description,
                'model_name':model_name,
                'rec_id':rec_id,
            })

        model=request.env[model_name]

        ifnotisinstance(model,request.env.registry['microsoft.outlook.mixin']):
            #Themodelmustinheritsfromthe"microsoft.outlook.mixin"mixin
            raiseForbidden()

        record=model.browse(rec_id).exists()
        ifnotrecord:
            raiseForbidden()

        ifnotcsrf_tokenornotconsteq(csrf_token,record._get_outlook_csrf_token()):
            _logger.error('MicrosoftOutlook:WrongCSRFtokenduringOutlookauthentication.')
            raiseForbidden()

        try:
            refresh_token,access_token,expiration=record._fetch_outlook_refresh_token(code)
        exceptUserErrorase:
            returnrequest.render('microsoft_outlook.microsoft_outlook_oauth_error',{
                'error':str(e.name),
                'model_name':model_name,
                'rec_id':rec_id,
            })

        record.write({
            'microsoft_outlook_refresh_token':refresh_token,
            'microsoft_outlook_access_token':access_token,
            'microsoft_outlook_access_token_expiration':expiration,
        })

        returnwerkzeug.utils.redirect(f'/web?#id={rec_id}&model={model_name}&view_type=form',303)
