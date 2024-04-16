#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_
fromflectra.exceptionsimportUserError


classPosInvoiceReport(models.AbstractModel):
    _name='report.point_of_sale.report_invoice'
    _description='PointofSaleInvoiceReport'

    @api.model
    def_get_report_values(self,docids,data=None):
        PosOrder=self.env['pos.order']
        ids_to_print=[]
        invoiced_posorders_ids=[]
        selected_orders=PosOrder.browse(docids)
        fororderinselected_orders.filtered(lambdao:o.account_move):
            ids_to_print.append(order.account_move.id)
            invoiced_posorders_ids.append(order.id)
        not_invoiced_orders_ids=list(set(docids)-set(invoiced_posorders_ids))
        ifnot_invoiced_orders_ids:
            not_invoiced_posorders=PosOrder.browse(not_invoiced_orders_ids)
            not_invoiced_orders_names=[a.nameforainnot_invoiced_posorders]
            raiseUserError(_('Nolinktoaninvoicefor%s.')%','.join(not_invoiced_orders_names))

        return{
            'docs':self.env['account.move'].sudo().browse(ids_to_print),
            'qr_code_urls':self.env['report.account.report_invoice'].sudo()._get_report_values(ids_to_print)['qr_code_urls']
        }
