#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.addons.http_routing.models.ir_httpimportunslug
fromflectra.addons.portal.controllers.portalimportCustomerPortal


classCustomerPortal(CustomerPortal):

    @http.route(["/sale_quotation_builder/template/<string:template_id>"],type='http',auth="user",website=True)
    defsale_quotation_builder_template_view(self,template_id,**post):
        template_id=unslug(template_id)[-1]
        template=request.env['sale.order.template'].browse(template_id).with_context(
            allowed_company_ids=request.env.user.company_ids.ids,
        )
        values={'template':template}
        returnrequest.render('sale_quotation_builder.so_template',values)
