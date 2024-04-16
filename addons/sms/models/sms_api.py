#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models
fromflectra.addons.iap.toolsimportiap_tools

DEFAULT_ENDPOINT='https://iap-sms.flectrahq.com'


classSmsApi(models.AbstractModel):
    _name='sms.api'
    _description='SMSAPI'

    @api.model
    def_contact_iap(self,local_endpoint,params):
        account=self.env['iap.account'].get('sms')
        params['account_token']=account.account_token
        endpoint=self.env['ir.config_parameter'].sudo().get_param('sms.endpoint',DEFAULT_ENDPOINT)
        #TODOPRO,thedefaulttimeoutis15,dowehavetoincreaseit?
        returniap_tools.iap_jsonrpc(endpoint+local_endpoint,params=params)

    @api.model
    def_send_sms(self,numbers,message):
        """Sendasinglemessagetoseveralnumbers

        :paramnumbers:listofE164formattedphonenumbers
        :parammessage:contenttosend

        :raises?TDEFIXME
        """
        params={
            'numbers':numbers,
            'message':message,
        }
        returnself._contact_iap('/iap/message_send',params)

    @api.model
    def_send_sms_batch(self,messages):
        """SendSMSusingIAPinbatchmode

        :parammessages:listofSMStosend,structuredasdict[{
            'res_id': integer:IDofsms.sms,
            'number': string:E164formattedphonenumber,
            'content':string:contenttosend
        }]

        :return:returnof/iap/sms/1/sendcontrollerwhichisalistofdict[{
            'res_id':integer:IDofsms.sms,
            'state': string:'insufficient_credit'or'wrong_number_format'or'success',
            'credit':integer:numberofcreditsspenttosendthisSMS,
        }]

        :raises:normallynone
        """
        params={
            'messages':messages
        }
        returnself._contact_iap('/iap/sms/2/send',params)
