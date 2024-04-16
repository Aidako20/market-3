#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp,_
fromflectra.addons.portal.controllers.portalimportCustomerPortal,pagerasportal_pager
fromflectra.exceptionsimportAccessError,MissingError
fromcollectionsimportOrderedDict
fromflectra.httpimportrequest


classPortalAccount(CustomerPortal):

    def_prepare_home_portal_values(self,counters):
        values=super()._prepare_home_portal_values(counters)
        if'invoice_count'incounters:
            invoice_count=request.env['account.move'].search_count(self._get_invoices_domain())\
                ifrequest.env['account.move'].check_access_rights('read',raise_exception=False)else0
            values['invoice_count']=invoice_count
        returnvalues

    #------------------------------------------------------------
    #MyInvoices
    #------------------------------------------------------------

    def_invoice_get_page_view_values(self,invoice,access_token,**kwargs):
        values={
            'page_name':'invoice',
            'invoice':invoice,
        }
        returnself._get_page_view_values(invoice,access_token,values,'my_invoices_history',False,**kwargs)

    def_get_invoices_domain(self):
        return[('state','notin',('cancel','draft')),('move_type','in',('out_invoice','out_refund','in_invoice','in_refund','out_receipt','in_receipt'))]

    @http.route(['/my/invoices','/my/invoices/page/<int:page>'],type='http',auth="user",website=True)
    defportal_my_invoices(self,page=1,date_begin=None,date_end=None,sortby=None,filterby=None,**kw):
        values=self._prepare_portal_layout_values()
        AccountInvoice=request.env['account.move']

        domain=self._get_invoices_domain()

        searchbar_sortings={
            'date':{'label':_('Date'),'order':'invoice_datedesc'},
            'duedate':{'label':_('DueDate'),'order':'invoice_date_duedesc'},
            'name':{'label':_('Reference'),'order':'namedesc'},
            'state':{'label':_('Status'),'order':'state'},
        }
        #defaultsortbyorder
        ifnotsortby:
            sortby='date'
        order=searchbar_sortings[sortby]['order']

        searchbar_filters={
            'all':{'label':_('All'),'domain':[]},
            'invoices':{'label':_('Invoices'),'domain':[('move_type','in',('out_invoice','out_refund'))]},
            'bills':{'label':_('Bills'),'domain':[('move_type','in',('in_invoice','in_refund'))]},
        }
        #defaultfilterbyvalue
        ifnotfilterby:
            filterby='all'
        domain+=searchbar_filters[filterby]['domain']

        ifdate_beginanddate_end:
            domain+=[('create_date','>',date_begin),('create_date','<=',date_end)]

        #countforpager
        invoice_count=AccountInvoice.search_count(domain)
        #pager
        pager=portal_pager(
            url="/my/invoices",
            url_args={'date_begin':date_begin,'date_end':date_end,'sortby':sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        #contentaccordingtopagerandarchiveselected
        invoices=AccountInvoice.search(domain,order=order,limit=self._items_per_page,offset=pager['offset'])
        request.session['my_invoices_history']=invoices.ids[:100]

        values.update({
            'date':date_begin,
            'invoices':invoices,
            'page_name':'invoice',
            'pager':pager,
            'default_url':'/my/invoices',
            'searchbar_sortings':searchbar_sortings,
            'sortby':sortby,
            'searchbar_filters':OrderedDict(sorted(searchbar_filters.items())),
            'filterby':filterby,
        })
        returnrequest.render("account.portal_my_invoices",values)

    @http.route(['/my/invoices/<int:invoice_id>'],type='http',auth="public",website=True)
    defportal_my_invoice_detail(self,invoice_id,access_token=None,report_type=None,download=False,**kw):
        try:
            invoice_sudo=self._document_check_access('account.move',invoice_id,access_token)
        except(AccessError,MissingError):
            returnrequest.redirect('/my')

        ifreport_typein('html','pdf','text'):
            returnself._show_report(model=invoice_sudo,report_type=report_type,report_ref='account.account_invoices',download=download)

        values=self._invoice_get_page_view_values(invoice_sudo,access_token,**kw)
        acquirers=values.get('acquirers')
        ifacquirers:
            country_id=values.get('partner_id')andvalues.get('partner_id')[0].country_id.id
            values['acq_extra_fees']=acquirers.get_acquirer_extra_fees(invoice_sudo.amount_residual,invoice_sudo.currency_id,country_id)

        returnrequest.render("account.portal_invoice_page",values)

    #------------------------------------------------------------
    #MyHome
    #------------------------------------------------------------

    defdetails_form_validate(self,data):
        error,error_message=super(PortalAccount,self).details_form_validate(data)
        #preventVAT/namechangeifinvoicesexist
        partner=request.env['res.users'].browse(request.uid).partner_id
        ifnotpartner.can_edit_vat():
            if'vat'indataand(data['vat']orFalse)!=(partner.vatorFalse):
                error['vat']='error'
                error_message.append(_('ChangingVATnumberisnotallowedonceinvoiceshavebeenissuedforyouraccount.Pleasecontactusdirectlyforthisoperation.'))
            if'name'indataand(data['name']orFalse)!=(partner.nameorFalse):
                error['name']='error'
                error_message.append(_('Changingyournameisnotallowedonceinvoiceshavebeenissuedforyouraccount.Pleasecontactusdirectlyforthisoperation.'))
            if'company_name'indataand(data['company_name']orFalse)!=(partner.company_nameorFalse):
                error['company_name']='error'
                error_message.append(_('Changingyourcompanynameisnotallowedonceinvoiceshavebeenissuedforyouraccount.Pleasecontactusdirectlyforthisoperation.'))
        returnerror,error_message
