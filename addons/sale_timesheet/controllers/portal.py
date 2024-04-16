#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp,_
fromflectra.httpimportrequest
fromflectra.osvimportexpression

fromflectra.addons.account.controllersimportportal
fromflectra.addons.hr_timesheet.controllers.portalimportTimesheetCustomerPortal


classPortalAccount(portal.PortalAccount):

    def_invoice_get_page_view_values(self,invoice,access_token,**kwargs):
        values=super(PortalAccount,self)._invoice_get_page_view_values(invoice,access_token,**kwargs)
        domain=request.env['account.analytic.line']._timesheet_get_portal_domain()
        domain=expression.AND([
            domain,
            request.env['account.analytic.line']._timesheet_get_sale_domain(
                invoice.mapped('line_ids.sale_line_ids'),
                request.env['account.move'].browse([invoice.id])
            )
        ])
        values['timesheets']=request.env['account.analytic.line'].sudo().search(domain)
        values['is_uom_day']=request.env['account.analytic.line'].sudo()._is_timesheet_encode_uom_day()
        returnvalues


classCustomerPortal(portal.CustomerPortal):
    def_order_get_page_view_values(self,order,access_token,**kwargs):
        values=super(CustomerPortal,self)._order_get_page_view_values(order,access_token,**kwargs)
        domain=request.env['account.analytic.line']._timesheet_get_portal_domain()
        domain=expression.AND([
            domain,
            request.env['account.analytic.line']._timesheet_get_sale_domain(
                order.mapped('order_line'),
                order.invoice_ids
            )
        ])
        values['timesheets']=request.env['account.analytic.line'].sudo().search(domain)
        values['is_uom_day']=request.env['account.analytic.line'].sudo()._is_timesheet_encode_uom_day()
        returnvalues


classSaleTimesheetCustomerPortal(TimesheetCustomerPortal):

    def_get_searchbar_inputs(self):
        searchbar_inputs=super()._get_searchbar_inputs()
        searchbar_inputs.update(
            sol={'input':'sol','label':_('SearchinSalesOrderItem')},
            sol_id={'input':'sol_id','label':_('SearchinSalesOrderItemID')},
            invoice={'input':'invoice_id','label':_('SearchinInvoiceID')})
        returnsearchbar_inputs

    def_get_searchbar_groupby(self):
        searchbar_groupby=super()._get_searchbar_groupby()
        searchbar_groupby.update(sol={'input':'sol','label':_('SalesOrderItem')})
        returnsearchbar_groupby

    def_get_search_domain(self,search_in,search):
        search_domain=super()._get_search_domain(search_in,search)
        ifsearch_inin('sol','all'):
            search_domain=expression.OR([search_domain,[('so_line','ilike',search)]])
        ifsearch_inin('sol_id','invoice_id'):
            search=int(search)ifsearch.isdigit()else0
        ifsearch_in=='sol_id':
            search_domain=expression.OR([search_domain,[('so_line.id','=',search)]])
        ifsearch_in=='invoice_id':
            invoice=request.env['account.move'].browse(search)
            domain=request.env['account.analytic.line']._timesheet_get_sale_domain(invoice.mapped('invoice_line_ids.sale_line_ids'),invoice)
            search_domain=expression.OR([search_domain,domain])
        returnsearch_domain

    def_get_groupby_mapping(self):
        groupby_mapping=super()._get_groupby_mapping()
        groupby_mapping.update(sol='so_line')
        returngroupby_mapping

    @http.route(['/my/timesheets','/my/timesheets/page/<int:page>'],type='http',auth="user",website=True)
    defportal_my_timesheets(self,page=1,sortby=None,filterby=None,search=None,search_in='all',groupby='sol',**kw):
        ifsearchandsearch_inandsearch_inin('sol_id','invoice_id')andnotsearch.isdigit():
            search='0'
        returnsuper().portal_my_timesheets(page,sortby,filterby,search,search_in,groupby,**kw)
