#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classSaleAdvancePaymentInv(models.TransientModel):
    _inherit="sale.advance.payment.inv"

    @api.model
    def_default_invoicing_timesheet_enabled(self):
        if'active_id'notinself._contextand'active_ids'notinself._context:
            returnFalse
        sale_orders=self.env['sale.order'].browse(self._context.get('active_id')orself._context.get('active_ids'))
        order_lines=sale_orders.mapped('order_line').filtered(lambdasol:sol.invoice_status=='toinvoice')
        product_ids=order_lines.mapped('product_id').filtered(lambdap:p._is_delivered_timesheet())
        returnbool(product_ids)

    date_start_invoice_timesheet=fields.Date(
        string='StartDate',
        help="Onlytimesheetsnotyetinvoiced(andvalidated,ifapplicable)fromthisperiodwillbeinvoiced.Iftheperiodisnotindicated,alltimesheetsnotyetinvoiced(andvalidated,ifapplicable)willbeinvoicedwithoutdistinction.")
    date_end_invoice_timesheet=fields.Date(
        string='EndDate',
        help="Onlytimesheetsnotyetinvoiced(andvalidated,ifapplicable)fromthisperiodwillbeinvoiced.Iftheperiodisnotindicated,alltimesheetsnotyetinvoiced(andvalidated,ifapplicable)willbeinvoicedwithoutdistinction.")
    invoicing_timesheet_enabled=fields.Boolean(default=_default_invoicing_timesheet_enabled)

    defcreate_invoices(self):
        """Overridemethodfromsale/wizard/sale_make_invoice_advance.py

            WhentheuserwanttoinvoicethetimesheetstotheSO
            uptoaspecificperiodthenweneedtorecomputethe
            qty_to_invoiceforeachproduct_idinsale.order.line,
            beforecreatingtheinvoice.
        """
        sale_orders=self.env['sale.order'].browse(
            self._context.get('active_ids',[])
        )

        ifself.advance_payment_method=='delivered'andself.invoicing_timesheet_enabled:
            ifself.date_start_invoice_timesheetorself.date_end_invoice_timesheet:
                sale_orders.mapped('order_line')._recompute_qty_to_invoice(self.date_start_invoice_timesheet,self.date_end_invoice_timesheet)

            sale_orders.with_context(
                timesheet_start_date=self.date_start_invoice_timesheet,
                timesheet_end_date=self.date_end_invoice_timesheet
            )._create_invoices(final=self.deduct_down_payments)

            ifself._context.get('open_invoices',False):
                returnsale_orders.action_view_invoice()
            return{'type':'ir.actions.act_window_close'}

        returnsuper(SaleAdvancePaymentInv,self).create_invoices()
