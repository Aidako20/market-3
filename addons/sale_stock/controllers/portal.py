#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportexceptions,SUPERUSER_ID
fromflectra.addons.sale.controllers.portalimportCustomerPortal
fromflectra.httpimportrequest,route
fromflectra.toolsimportconsteq


classSaleStockPortal(CustomerPortal):

    def_stock_picking_check_access(self,picking_id,access_token=None):
        picking=request.env['stock.picking'].browse([picking_id])
        picking_sudo=picking.sudo()
        try:
            picking.check_access_rights('read')
            picking.check_access_rule('read')
        exceptexceptions.AccessError:
            ifnotaccess_tokenornotconsteq(picking_sudo.sale_id.access_token,access_token):
                raise
        returnpicking_sudo

    @route(['/my/picking/pdf/<int:picking_id>'],type='http',auth="public",website=True)
    defportal_my_picking_report(self,picking_id,access_token=None,**kw):
        """Printdeliveryslipforcustomer,usingeitheraccessrightsoraccesstoken
        tobesurecustomerhasaccess"""
        try:
            picking_sudo=self._stock_picking_check_access(picking_id,access_token=access_token)
        exceptexceptions.AccessError:
            returnrequest.redirect('/my')

        #printreportasSUPERUSER,sinceitrequireaccesstoproduct,taxes,paymenttermetc..andportaldoesnothavethoseaccessrights.
        pdf=request.env.ref('stock.action_report_delivery').with_user(SUPERUSER_ID)._render_qweb_pdf([picking_sudo.id])[0]
        pdfhttpheaders=[
            ('Content-Type','application/pdf'),
            ('Content-Length',len(pdf)),
        ]
        returnrequest.make_response(pdf,headers=pdfhttpheaders)
