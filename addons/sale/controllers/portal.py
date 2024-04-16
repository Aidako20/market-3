#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbinascii

fromflectraimportfields,http,SUPERUSER_ID,_
fromflectra.exceptionsimportAccessError,MissingError
fromflectra.httpimportrequest
fromflectra.addons.payment.controllers.portalimportPaymentProcessing
fromflectra.addons.portal.controllers.mailimport_message_post_helper
fromflectra.addons.portal.controllers.portalimportCustomerPortal,pagerasportal_pager,get_records_pager
fromflectra.osvimportexpression


classCustomerPortal(CustomerPortal):

    def_prepare_home_portal_values(self,counters):
        values=super()._prepare_home_portal_values(counters)
        partner=request.env.user.partner_id

        SaleOrder=request.env['sale.order']
        if'quotation_count'incounters:
            values['quotation_count']=SaleOrder.search_count(self._prepare_quotations_domain(partner))\
                ifSaleOrder.check_access_rights('read',raise_exception=False)else0
        if'order_count'incounters:
            values['order_count']=SaleOrder.search_count(self._prepare_orders_domain(partner))\
                ifSaleOrder.check_access_rights('read',raise_exception=False)else0

        returnvalues

    def_prepare_quotations_domain(self,partner):
        return[
            ('message_partner_ids','child_of',[partner.commercial_partner_id.id]),
            ('state','in',['sent','cancel'])
        ]

    def_prepare_orders_domain(self,partner):
        return[
            ('message_partner_ids','child_of',[partner.commercial_partner_id.id]),
            ('state','in',['sale','done'])
        ]

    def_order_get_page_view_values(self,order,access_token,**kwargs):
        values={
            'sale_order':order,
            'token':access_token,
            'return_url':'/shop/payment/validate',
            'bootstrap_formatting':True,
            'partner_id':order.partner_id.id,
            'report_type':'html',
            'action':order._get_portal_return_action(),
        }
        iforder.company_id:
            values['res_company']=order.company_id

        iforder.has_to_be_paid():
            domain=expression.AND([
                ['&',('state','in',['enabled','test']),('company_id','=',order.company_id.id)],
                ['|',('country_ids','=',False),('country_ids','in',[order.partner_id.country_id.id])]
            ])
            acquirers=request.env['payment.acquirer'].sudo().search(domain)

            values['acquirers']=acquirers.filtered(lambdaacq:(acq.payment_flow=='form'andacq.view_template_id)or
                                                     (acq.payment_flow=='s2s'andacq.registration_view_template_id))
            values['pms']=request.env['payment.token'].search([('partner_id','=',order.partner_id.id)])
            values['acq_extra_fees']=acquirers.get_acquirer_extra_fees(order.amount_total,order.currency_id,order.partner_id.country_id.id)

        iforder.statein('draft','sent','cancel'):
            history=request.session.get('my_quotations_history',[])
        else:
            history=request.session.get('my_orders_history',[])
        values.update(get_records_pager(history,order))

        returnvalues

    def_get_sale_searchbar_sortings(self):
        return{
            'date':{'label':_('OrderDate'),'order':'date_orderdesc'},
            'name':{'label':_('Reference'),'order':'name'},
            'stage':{'label':_('Stage'),'order':'state'},
        }

    #
    #QuotationsandSalesOrders
    #

    @http.route(['/my/quotes','/my/quotes/page/<int:page>'],type='http',auth="user",website=True)
    defportal_my_quotes(self,page=1,date_begin=None,date_end=None,sortby=None,**kw):
        values=self._prepare_portal_layout_values()
        partner=request.env.user.partner_id
        SaleOrder=request.env['sale.order']

        domain=self._prepare_quotations_domain(partner)

        searchbar_sortings=self._get_sale_searchbar_sortings()

        #defaultsortbyorder
        ifnotsortby:
            sortby='date'
        sort_order=searchbar_sortings[sortby]['order']

        ifdate_beginanddate_end:
            domain+=[('create_date','>',date_begin),('create_date','<=',date_end)]

        #countforpager
        quotation_count=SaleOrder.search_count(domain)
        #makepager
        pager=portal_pager(
            url="/my/quotes",
            url_args={'date_begin':date_begin,'date_end':date_end,'sortby':sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        #searchthecounttodisplay,accordingtothepagerdata
        quotations=SaleOrder.search(domain,order=sort_order,limit=self._items_per_page,offset=pager['offset'])
        request.session['my_quotations_history']=quotations.ids[:100]

        values.update({
            'date':date_begin,
            'quotations':quotations.sudo(),
            'page_name':'quote',
            'pager':pager,
            'default_url':'/my/quotes',
            'searchbar_sortings':searchbar_sortings,
            'sortby':sortby,
        })
        returnrequest.render("sale.portal_my_quotations",values)

    @http.route(['/my/orders','/my/orders/page/<int:page>'],type='http',auth="user",website=True)
    defportal_my_orders(self,page=1,date_begin=None,date_end=None,sortby=None,**kw):
        values=self._prepare_portal_layout_values()
        partner=request.env.user.partner_id
        SaleOrder=request.env['sale.order']

        domain=self._prepare_orders_domain(partner)

        searchbar_sortings=self._get_sale_searchbar_sortings()

        #defaultsortbyorder
        ifnotsortby:
            sortby='date'
        sort_order=searchbar_sortings[sortby]['order']

        ifdate_beginanddate_end:
            domain+=[('create_date','>',date_begin),('create_date','<=',date_end)]

        #countforpager
        order_count=SaleOrder.search_count(domain)
        #pager
        pager=portal_pager(
            url="/my/orders",
            url_args={'date_begin':date_begin,'date_end':date_end,'sortby':sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        #contentaccordingtopager
        orders=SaleOrder.search(domain,order=sort_order,limit=self._items_per_page,offset=pager['offset'])
        request.session['my_orders_history']=orders.ids[:100]

        values.update({
            'date':date_begin,
            'orders':orders.sudo(),
            'page_name':'order',
            'pager':pager,
            'default_url':'/my/orders',
            'searchbar_sortings':searchbar_sortings,
            'sortby':sortby,
        })
        returnrequest.render("sale.portal_my_orders",values)

    @http.route(['/my/orders/<int:order_id>'],type='http',auth="public",website=True)
    defportal_order_page(self,order_id,report_type=None,access_token=None,message=False,download=False,**kw):
        try:
            order_sudo=self._document_check_access('sale.order',order_id,access_token=access_token)
        except(AccessError,MissingError):
            returnrequest.redirect('/my')

        ifreport_typein('html','pdf','text'):
            returnself._show_report(model=order_sudo,report_type=report_type,report_ref='sale.action_report_saleorder',download=download)

        #usesudotoallowaccessing/viewingordersforpublicuser
        #onlyifheknowstheprivatetoken
        #Logonlyonceaday
        iforder_sudo:
            #storethedateasastringinthesessiontoallowserialization
            now=fields.Date.today().isoformat()
            session_obj_date=request.session.get('view_quote_%s'%order_sudo.id)
            ifsession_obj_date!=nowandrequest.env.user.shareandaccess_token:
                request.session['view_quote_%s'%order_sudo.id]=now
                body=_('Quotationviewedbycustomer%s',order_sudo.partner_id.nameifrequest.env.user._is_public()elserequest.env.user.partner_id.name)
                _message_post_helper(
                    "sale.order",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

        values=self._order_get_page_view_values(order_sudo,access_token,**kw)
        values['message']=message

        returnrequest.render('sale.sale_order_portal_template',values)

    @http.route(['/my/orders/<int:order_id>/accept'],type='json',auth="public",website=True)
    defportal_quote_accept(self,order_id,access_token=None,name=None,signature=None):
        #getfromquerystringifnotonjsonparam
        access_token=access_tokenorrequest.httprequest.args.get('access_token')
        try:
            order_sudo=self._document_check_access('sale.order',order_id,access_token=access_token)
        except(AccessError,MissingError):
            return{'error':_('Invalidorder.')}

        ifnotorder_sudo.has_to_be_signed():
            return{'error':_('Theorderisnotinastaterequiringcustomersignature.')}
        ifnotsignature:
            return{'error':_('Signatureismissing.')}

        try:
            order_sudo.write({
                'signed_by':name,
                'signed_on':fields.Datetime.now(),
                'signature':signature,
            })
            request.env.cr.commit()
        except(TypeError,binascii.Error)ase:
            return{'error':_('Invalidsignaturedata.')}

        ifnotorder_sudo.has_to_be_paid():
            order_sudo.action_confirm()
            order_sudo._send_order_confirmation_mail()

        pdf=request.env.ref('sale.action_report_saleorder').with_user(SUPERUSER_ID)._render_qweb_pdf([order_sudo.id])[0]

        _message_post_helper(
            'sale.order',order_sudo.id,_('Ordersignedby%s')%(name,),
            attachments=[('%s.pdf'%order_sudo.name,pdf)],
            **({'token':access_token}ifaccess_tokenelse{}))

        query_string='&message=sign_ok'
        iforder_sudo.has_to_be_paid(True):
            query_string+='#allow_payment=yes'
        return{
            'force_refresh':True,
            'redirect_url':order_sudo.get_portal_url(query_string=query_string),
        }

    @http.route(['/my/orders/<int:order_id>/decline'],type='http',auth="public",methods=['POST'],website=True)
    defdecline(self,order_id,access_token=None,**post):
        try:
            order_sudo=self._document_check_access('sale.order',order_id,access_token=access_token)
        except(AccessError,MissingError):
            returnrequest.redirect('/my')

        message=post.get('decline_message')

        query_string=False
        iforder_sudo.has_to_be_signed()andmessage:
            order_sudo.action_cancel()
            _message_post_helper('sale.order',order_id,message,**{'token':access_token}ifaccess_tokenelse{})
        else:
            query_string="&message=cant_reject"

        returnrequest.redirect(order_sudo.get_portal_url(query_string=query_string))

    #note:website_salecode
    @http.route(['/my/orders/<int:order_id>/transaction/'],type='json',auth="public",website=True)
    defpayment_transaction_token(self,acquirer_id,order_id,save_token=False,access_token=None,**kwargs):
        """Jsonmethodthatcreatesapayment.transaction,usedtocreatea
        transactionwhentheuserclickson'paynow'button.Afterhaving
        createdthetransaction,theeventcontinuesandtheuserisredirected
        totheacquirerwebsite.

        :paramintacquirer_id:idofapayment.acquirerrecord.Ifnotsetthe
                                userisredirectedtothecheckoutpage
        """
        #Ensureapaymentacquirerisselected
        ifnotacquirer_id:
            returnFalse

        try:
            acquirer_id=int(acquirer_id)
        except:
            returnFalse

        order=request.env['sale.order'].sudo().browse(order_id)
        ifnotorderornotorder.order_lineornotorder.has_to_be_paid():
            returnFalse

        #Createtransaction
        vals={
            'acquirer_id':acquirer_id,
            'type':order._get_payment_type(save_token),
            'return_url':order.get_portal_url(),
        }

        transaction=order._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(transaction)
        returntransaction.render_sale_button(
            order,
            submit_txt=_('Pay&Confirm'),
            render_values={
                'type':order._get_payment_type(save_token),
                'alias_usage':_('Ifwestoreyourpaymentinformationonourserver,subscriptionpaymentswillbemadeautomatically.'),
            }
        )

    @http.route('/my/orders/<int:order_id>/transaction/token',type='http',auth='public',website=True)
    defpayment_token(self,order_id,pm_id=None,**kwargs):

        order=request.env['sale.order'].sudo().browse(order_id)
        ifnotorder:
            returnrequest.redirect("/my/orders")
        ifnotorder.order_lineorpm_idisNoneornotorder.has_to_be_paid():
            returnrequest.redirect(order.get_portal_url())

        #trytoconvertpm_idintoaninteger,ifitdoesn'tworkredirecttheusertothequote
        try:
            pm_id=int(pm_id)
        exceptValueError:
            returnrequest.redirect(order.get_portal_url())

        #Createtransaction
        vals={
            'payment_token_id':pm_id,
            'type':'server2server',
            'return_url':order.get_portal_url(),
        }

        tx=order._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(tx)
        returnrequest.redirect('/payment/process')
