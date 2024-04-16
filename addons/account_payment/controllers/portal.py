#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.account.controllers.portalimportPortalAccount
fromflectra.httpimportrequest


classPortalAccount(PortalAccount):

    def_invoice_get_page_view_values(self,invoice,access_token,**kwargs):
        values=super(PortalAccount,self)._invoice_get_page_view_values(invoice,access_token,**kwargs)
        payment_inputs=request.env['payment.acquirer']._get_available_payment_input(partner=invoice.partner_id,company=invoice.company_id)
        #ifnotconnected(usingpublicuser),themethod_get_available_payment_inputwillreturnpublicusertokens
        is_public_user=request.env.user._is_public()
        ifis_public_user:
            #weshouldnotdisplaypaymenttokensownedbythepublicuser
            payment_inputs.pop('pms',None)
            token_count=request.env['payment.token'].sudo().search_count([('acquirer_id.company_id','=',invoice.company_id.id),
                                                                      ('partner_id','=',invoice.partner_id.id),
                                                                    ])
            values['existing_token']=token_count>0
        values.update(payment_inputs)
        #ifthecurrentuserisconnectedwesetpartner_idtohispartnerotherwisewesetitastheinvoicepartner
        #wedothistoforcethecreationofpaymenttokenstothecorrectpartnerandavoidtokenlinkedtothepublicuser
        values['partner_id']=invoice.partner_idifis_public_userelserequest.env.user.partner_id,
        returnvalues
