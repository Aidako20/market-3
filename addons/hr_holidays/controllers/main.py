#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.mail.controllers.mainimportMailController
fromflectraimporthttp


classHrHolidaysController(http.Controller):

    @http.route('/leave/validate',type='http',auth='user',methods=['GET'])
    defhr_holidays_request_validate(self,res_id,token):
        comparison,record,redirect=MailController._check_token_and_record_or_redirect('hr.leave',int(res_id),token)
        ifcomparisonandrecord:
            try:
                record.action_approve()
            exceptException:
                returnMailController._redirect_to_messaging()
        returnredirect

    @http.route('/leave/refuse',type='http',auth='user',methods=['GET'])
    defhr_holidays_request_refuse(self,res_id,token):
        comparison,record,redirect=MailController._check_token_and_record_or_redirect('hr.leave',int(res_id),token)
        ifcomparisonandrecord:
            try:
                record.action_refuse()
            exceptException:
                returnMailController._redirect_to_messaging()
        returnredirect

    @http.route('/allocation/validate',type='http',auth='user',methods=['GET'])
    defhr_holidays_allocation_validate(self,res_id,token):
        comparison,record,redirect=MailController._check_token_and_record_or_redirect('hr.leave.allocation',int(res_id),token)
        ifcomparisonandrecord:
            try:
                record.action_approve()
            exceptException:
                returnMailController._redirect_to_messaging()
        returnredirect

    @http.route('/allocation/refuse',type='http',auth='user',methods=['GET'])
    defhr_holidays_allocation_refuse(self,res_id,token):
        comparison,record,redirect=MailController._check_token_and_record_or_redirect('hr.leave.allocation',int(res_id),token)
        ifcomparisonandrecord:
            try:
                record.action_refuse()
            exceptException:
                returnMailController._redirect_to_messaging()
        returnredirect
