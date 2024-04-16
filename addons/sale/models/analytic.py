#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classAccountAnalyticLine(models.Model):
    _inherit="account.analytic.line"

    def_default_sale_line_domain(self):
        """ThisisonlyusedfordeliveredquantityofSOlinebasedonanalyticline,andtimesheet
            (seesale_timesheet).Thiscanbeoverridetoallowfurthercustomization.
        """
        return[('qty_delivered_method','=','analytic')]

    so_line=fields.Many2one('sale.order.line',string='SalesOrderItem',domain=lambdaself:self._default_sale_line_domain())
