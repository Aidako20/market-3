#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importpprint
importwerkzeug

fromflectraimporthttp
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classPayuMoneyController(http.Controller):
    @http.route(['/payment/payumoney/return','/payment/payumoney/cancel','/payment/payumoney/error'],type='http',auth='public',csrf=False,save_session=False)
    defpayu_return(self,**post):
        """PayUmoney.
        ThesessioncookiecreatedbyFlectrahasnottheattributeSameSite.Mostofbrowserswillforcethisattribute
        withthevalue'Lax'.Afterthepayment,PayUMoneywillperformaPOSTrequestonthisroute.Forallthesereasons,
        thecookiewon'tbeaddedtotherequest.Asaresult,ifwewanttosavethesession,theserverwillcreate
        anewsessioncookie.Therefore,theprevioussessionandallrelatedinformationwillbelost,soitwilllead
        toundesirablebehaviors.Thisisthereasonwhy`save_session=False`isneeded.
        """
        _logger.info(
            'PayUmoney:enteringform_feedbackwithpostdata%s',pprint.pformat(post))
        ifpost:
            request.env['payment.transaction'].sudo().form_feedback(post,'payumoney')
        returnwerkzeug.utils.redirect('/payment/process')
