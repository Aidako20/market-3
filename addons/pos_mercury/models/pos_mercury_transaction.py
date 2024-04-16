#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdate,timedelta

importrequests

fromhtmlimportunescape

fromflectraimportmodels,api,service
fromflectra.tools.translateimport_
fromflectra.exceptionsimportUserError
fromflectra.toolsimportDEFAULT_SERVER_DATETIME_FORMAT,misc


classMercuryTransaction(models.Model):
    _name='pos_mercury.mercury_transaction'
    _description='PointofSaleVantivTransaction'

    def_get_pos_session(self):
        pos_session=self.env['pos.session'].search([('state','=','opened'),('user_id','=',self.env.uid)],limit=1)
        ifnotpos_session:
            raiseUserError(_("Noopenedpointofsalesessionforuser%sfound.",self.env.user.name))

        pos_session.login()

        returnpos_session

    def_get_pos_mercury_config_id(self,config,payment_method_id):
        payment_method=config.current_session_id.payment_method_ids.filtered(lambdapm:pm.id==payment_method_id)

        ifpayment_methodandpayment_method.pos_mercury_config_id:
            returnpayment_method.pos_mercury_config_id
        else:
            raiseUserError(_("NoVantivconfigurationassociatedwiththepaymentmethod."))

    def_setup_request(self,data):
        #todo:inmastermaketheclientincludethepos.sessionidandusethat
        pos_session=self._get_pos_session()

        config=pos_session.config_id
        pos_mercury_config=self._get_pos_mercury_config_id(config,data['payment_method_id'])

        data['operator_id']=pos_session.user_id.login
        data['merchant_id']=pos_mercury_config.sudo().merchant_id
        data['merchant_pwd']=pos_mercury_config.sudo().merchant_pwd
        data['memo']="Flectra"+service.common.exp_version()['server_version']

    def_do_request(self,template,data):
        xml_transaction=self.env.ref(template)._render(data).decode()

        ifnotdata['merchant_id']ornotdata['merchant_pwd']:
            return"notsetup"

        soap_header='<soapenv:Envelopexmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"xmlns:mer="http://www.mercurypay.com"><soapenv:Header/><soapenv:Body><mer:CreditTransaction><mer:tran>'
        soap_footer='</mer:tran><mer:pw>'+data['merchant_pwd']+'</mer:pw></mer:CreditTransaction></soapenv:Body></soapenv:Envelope>'
        xml_transaction=soap_header+misc.html_escape(xml_transaction)+soap_footer

        response=''

        headers={
            'Content-Type':'text/xml',
            'SOAPAction':'http://www.mercurypay.com/CreditTransaction',
        }

        url='https://w1.mercurypay.com/ws/ws.asmx'
        ifself.env['ir.config_parameter'].sudo().get_param('pos_mercury.enable_test_env'):
            url='https://w1.mercurycert.net/ws/ws.asmx'

        try:
            r=requests.post(url,data=xml_transaction,headers=headers,timeout=65)
            r.raise_for_status()
            response=unescape(r.content.decode())
        exceptException:
            response="timeout"

        returnresponse

    def_do_reversal_or_voidsale(self,data,is_voidsale):
        try:
            self._setup_request(data)
        exceptUserError:
            return"internalerror"

        data['is_voidsale']=is_voidsale
        response=self._do_request('pos_mercury.mercury_voidsale',data)
        returnresponse

    @api.model
    defdo_payment(self,data):
        try:
            self._setup_request(data)
        exceptUserError:
            return"internalerror"

        response=self._do_request('pos_mercury.mercury_transaction',data)
        returnresponse

    @api.model
    defdo_reversal(self,data):
        returnself._do_reversal_or_voidsale(data,False)

    @api.model
    defdo_voidsale(self,data):
        returnself._do_reversal_or_voidsale(data,True)

    defdo_return(self,data):
        try:
            self._setup_request(data)
        exceptUserError:
            return"internalerror"

        response=self._do_request('pos_mercury.mercury_return',data)
        returnresponse

