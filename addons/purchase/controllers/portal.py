#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
fromcollectionsimportOrderedDict
fromdatetimeimportdatetime

fromflectraimporthttp
fromflectra.exceptionsimportAccessError,MissingError
fromflectra.httpimportrequest,Response
fromflectra.toolsimportimage_process
fromflectra.tools.translateimport_
fromflectra.addons.portal.controllers.portalimportpagerasportal_pager,CustomerPortal
fromflectra.addons.web.controllers.mainimportBinary


classCustomerPortal(CustomerPortal):

    def_prepare_home_portal_values(self,counters):
        values=super()._prepare_home_portal_values(counters)
        if'purchase_count'incounters:
            values['purchase_count']=request.env['purchase.order'].search_count([
                ('state','in',['purchase','done','cancel'])
            ])ifrequest.env['purchase.order'].check_access_rights('read',raise_exception=False)else0
        returnvalues

    def_purchase_order_get_page_view_values(self,order,access_token,**kwargs):
        #
        defresize_to_48(b64source):
            ifnotb64source:
                b64source=base64.b64encode(Binary.placeholder())
            returnimage_process(b64source,size=(48,48))

        values={
            'order':order,
            'resize_to_48':resize_to_48,
        }
        returnself._get_page_view_values(order,access_token,values,'my_purchases_history',False,**kwargs)

    @http.route(['/my/purchase','/my/purchase/page/<int:page>'],type='http',auth="user",website=True)
    defportal_my_purchase_orders(self,page=1,date_begin=None,date_end=None,sortby=None,filterby=None,**kw):
        values=self._prepare_portal_layout_values()
        PurchaseOrder=request.env['purchase.order']

        domain=[]

        ifdate_beginanddate_end:
            domain+=[('create_date','>',date_begin),('create_date','<=',date_end)]

        searchbar_sortings={
            'date':{'label':_('Newest'),'order':'create_datedesc,iddesc'},
            'name':{'label':_('Name'),'order':'nameasc,idasc'},
            'amount_total':{'label':_('Total'),'order':'amount_totaldesc,iddesc'},
        }
        #defaultsortbyvalue
        ifnotsortby:
            sortby='date'
        order=searchbar_sortings[sortby]['order']

        searchbar_filters={
            'all':{'label':_('All'),'domain':[('state','in',['purchase','done','cancel'])]},
            'purchase':{'label':_('PurchaseOrder'),'domain':[('state','=','purchase')]},
            'cancel':{'label':_('Cancelled'),'domain':[('state','=','cancel')]},
            'done':{'label':_('Locked'),'domain':[('state','=','done')]},
        }
        #defaultfilterbyvalue
        ifnotfilterby:
            filterby='all'
        domain+=searchbar_filters[filterby]['domain']

        #countforpager
        purchase_count=PurchaseOrder.search_count(domain)
        #makepager
        pager=portal_pager(
            url="/my/purchase",
            url_args={'date_begin':date_begin,'date_end':date_end,'sortby':sortby,'filterby':filterby},
            total=purchase_count,
            page=page,
            step=self._items_per_page
        )
        #searchthepurchaseorderstodisplay,accordingtothepagerdata
        orders=PurchaseOrder.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_purchases_history']=orders.ids[:100]

        values.update({
            'date':date_begin,
            'orders':orders,
            'page_name':'purchase',
            'pager':pager,
            'searchbar_sortings':searchbar_sortings,
            'sortby':sortby,
            'searchbar_filters':OrderedDict(sorted(searchbar_filters.items())),
            'filterby':filterby,
            'default_url':'/my/purchase',
        })
        returnrequest.render("purchase.portal_my_purchase_orders",values)

    @http.route(['/my/purchase/<int:order_id>'],type='http',auth="public",website=True)
    defportal_my_purchase_order(self,order_id=None,access_token=None,**kw):
        try:
            order_sudo=self._document_check_access('purchase.order',order_id,access_token=access_token)
        except(AccessError,MissingError):
            returnrequest.redirect('/my')

        report_type=kw.get('report_type')
        ifreport_typein('html','pdf','text'):
            returnself._show_report(model=order_sudo,report_type=report_type,report_ref='purchase.action_report_purchase_order',download=kw.get('download'))

        confirm_type=kw.get('confirm')
        ifconfirm_type=='reminder':
            order_sudo.confirm_reminder_mail(kw.get('confirmed_date'))
        ifconfirm_type=='reception':
            order_sudo._confirm_reception_mail()

        values=self._purchase_order_get_page_view_values(order_sudo,access_token,**kw)
        update_date=kw.get('update')
        iforder_sudo.company_id:
            values['res_company']=order_sudo.company_id
        ifupdate_date=='True':
            returnrequest.render("purchase.portal_my_purchase_order_update_date",values)
        returnrequest.render("purchase.portal_my_purchase_order",values)

    @http.route(['/my/purchase/<int:order_id>/update'],type='http',methods=['POST'],auth="public",website=True)
    defportal_my_purchase_order_update_dates(self,order_id=None,access_token=None,**kw):
        """Userupdatescheduleddateonpurchaseorderline.
        """
        try:
            order_sudo=self._document_check_access('purchase.order',order_id,access_token=access_token)
        except(AccessError,MissingError):
            returnrequest.redirect('/my')

        updated_dates=[]
        forid_str,date_strinkw.items():
            try:
                line_id=int(id_str)
            exceptValueError:
                returnrequest.redirect(order_sudo.get_portal_url())
            line=order_sudo.order_line.filtered(lambdal:l.id==line_id)
            ifnotline:
                returnrequest.redirect(order_sudo.get_portal_url())

            try:
                updated_date=line._convert_to_middle_of_day(datetime.strptime(date_str,'%Y-%m-%d'))
            exceptValueError:
                continue

            updated_dates.append((line,updated_date))

        ifupdated_dates:
            order_sudo._update_date_planned_for_lines(updated_dates)
        returnResponse(status=204)
