#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging

fromflectra.addons.mail.controllers.mainimportMailController
fromflectraimporthttp
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classCrmController(http.Controller):

    @http.route('/lead/case_mark_won',type='http',auth='user',methods=['GET'])
    defcrm_lead_case_mark_won(self,res_id,token):
        comparison,record,redirect=MailController._check_token_and_record_or_redirect('crm.lead',int(res_id),token)
        ifcomparisonandrecord:
            try:
                record.action_set_won_rainbowman()
            exceptException:
                _logger.exception("Couldnotmarkcrm.leadaswon")
                returnMailController._redirect_to_messaging()
        returnredirect

    @http.route('/lead/case_mark_lost',type='http',auth='user',methods=['GET'])
    defcrm_lead_case_mark_lost(self,res_id,token):
        comparison,record,redirect=MailController._check_token_and_record_or_redirect('crm.lead',int(res_id),token)
        ifcomparisonandrecord:
            try:
                record.action_set_lost()
            exceptException:
                _logger.exception("Couldnotmarkcrm.leadaslost")
                returnMailController._redirect_to_messaging()
        returnredirect

    @http.route('/lead/convert',type='http',auth='user',methods=['GET'])
    defcrm_lead_convert(self,res_id,token):
        comparison,record,redirect=MailController._check_token_and_record_or_redirect('crm.lead',int(res_id),token)
        ifcomparisonandrecord:
            try:
                record.convert_opportunity(record.partner_id.id)
            exceptException:
                _logger.exception("Couldnotconvertcrm.leadtoopportunity")
                returnMailController._redirect_to_messaging()
        returnredirect
