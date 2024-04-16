#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromwerkzeug.urlsimporturl_encode

fromflectraimporthttp,_
fromflectra.addons.portal.controllers.portalimport_build_url_w_params
fromflectra.addons.payment.controllers.portalimportPaymentProcessing
fromflectra.httpimportrequest,route


classPaymentPortal(http.Controller):

    @route('/invoice/pay/<int:invoice_id>/form_tx',type='json',auth="public",website=True)
    definvoice_pay_form(self,acquirer_id,invoice_id,save_token=False,access_token=None,**kwargs):
        """Jsonmethodthatcreatesapayment.transaction,usedtocreatea
        transactionwhentheuserclickson'paynow'buttononthepayment
        form.

        :returnhtml:formcontainingallvaluesrelatedtotheacquirerto
                      redirectcustomerstotheacquirerwebsite"""
        invoice_sudo=request.env['account.move'].sudo().browse(invoice_id)
        ifnotinvoice_sudo:
            returnFalse

        try:
            acquirer_id=int(acquirer_id)
        except:
            returnFalse

        ifrequest.env.user._is_public():
            save_token=False#weavoidtocreateatokenforthepublicuser

        success_url=kwargs.get(
            'success_url',"%s?%s"%(invoice_sudo.access_url,url_encode({'access_token':access_token})ifaccess_tokenelse'')
        )
        vals={
            'acquirer_id':acquirer_id,
            'return_url':success_url,
        }

        ifsave_token:
            vals['type']='form_save'

        transaction=invoice_sudo._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(transaction)

        returntransaction.render_invoice_button(
            invoice_sudo,
            submit_txt=_('Pay&Confirm'),
            render_values={
                'type':'form_save'ifsave_tokenelse'form',
                'alias_usage':_('Ifwestoreyourpaymentinformationonourserver,subscriptionpaymentswillbemadeautomatically.'),
            }
        )

    @http.route('/invoice/pay/<int:invoice_id>/s2s_token_tx',type='http',auth='public',website=True)
    definvoice_pay_token(self,invoice_id,pm_id=None,**kwargs):
        """Useatokentoperformas2stransaction"""
        error_url=kwargs.get('error_url','/my')
        access_token=kwargs.get('access_token')
        params={}
        ifaccess_token:
            params['access_token']=access_token

        invoice_sudo=request.env['account.move'].sudo().browse(invoice_id).exists()
        ifnotinvoice_sudo:
            params['error']='pay_invoice_invalid_doc'
            returnrequest.redirect(_build_url_w_params(error_url,params))

        success_url=kwargs.get(
            'success_url',"%s?%s"%(invoice_sudo.access_url,url_encode({'access_token':access_token})ifaccess_tokenelse'')
        )
        try:
            token=request.env['payment.token'].sudo().browse(int(pm_id))
        except(ValueError,TypeError):
            token=False
        token_owner=invoice_sudo.partner_idifrequest.env.user._is_public()elserequest.env.user.partner_id
        ifnottokenortoken.partner_id!=token_owner:
            params['error']='pay_invoice_invalid_token'
            returnrequest.redirect(_build_url_w_params(error_url,params))

        vals={
            'payment_token_id':token.id,
            'type':'server2server',
            'return_url':_build_url_w_params(success_url,params),
        }

        tx=invoice_sudo._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(tx)

        params['success']='pay_invoice'
        returnrequest.redirect('/payment/process')
