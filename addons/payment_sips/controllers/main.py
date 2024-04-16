#-*-coding:utf-8-*-

#Copyright2015Eezee-It

importjson
importlogging
importpprint
importwerkzeug

fromflectraimporthttp
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classSipsController(http.Controller):
    _notify_url='/payment/sips/ipn/'
    _return_url='/payment/sips/dpn/'

    defsips_validate_data(self,**post):
        sips=request.env['payment.acquirer'].search([('provider','=','sips')],limit=1)
        security=sips.sudo()._sips_generate_shasign(post)
        ifsecurity==post['Seal']:
            _logger.debug('Sips:validateddata')
            returnrequest.env['payment.transaction'].sudo().form_feedback(post,'sips')
        _logger.warning('Sips:dataarecorrupted')
        returnFalse

    @http.route('/payment/sips/ipn/',type='http',auth='public',methods=['POST'],csrf=False)
    defsips_ipn(self,**post):
        """SipsIPN."""
        _logger.info('BeginningSipsIPNform_feedbackwithpostdata%s',pprint.pformat(post)) #debug
        ifnotpost:
            #SIPSsometimessendsemptynotifications,thereasonwhyis
            #unclearbuttheytendtopollutelogsanddonotprovideany
            #meaningfulinformation;logasawarninginsteadofatraceback
            _logger.warning('Sips:receivedemptynotification;skip.')
        else:
            self.sips_validate_data(**post)
        return''

    @http.route('/payment/sips/dpn',type='http',auth="public",methods=['POST'],csrf=False,save_session=False)
    defsips_dpn(self,**post):
        """SipsDPN
        ThesessioncookiecreatedbyFlectrahasnottheattributeSameSite.Mostofbrowserswillforcethisattribute
        withthevalue'Lax'.Afterthepayment,SipswillperformaPOSTrequestonthisroute.Forallthesereasons,
        thecookiewon'tbeaddedtotherequest.Asaresult,ifwewanttosavethesession,theserverwillcreate
        anewsessioncookie.Therefore,theprevioussessionandallrelatedinformationwillbelost,soitwilllead
        toundesirablebehaviors.Thisisthereasonwhy`save_session=False`isneeded.
        """
        try:
            _logger.info('BeginningSipsDPNform_feedbackwithpostdata%s',pprint.pformat(post)) #debug
            self.sips_validate_data(**post)
        except:
            pass
        returnwerkzeug.utils.redirect('/payment/process')
