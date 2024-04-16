#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,api


classResCompany(models.Model):
    _inherit='res.company'

    @api.model
    def_set_default_sale_order_template_id_if_empty(self):
        template=self.env.ref('sale_quotation_builder.sale_order_template_default',raise_if_not_found=False)
        ifnottemplate:
            return
        companies=self.sudo().search([])
        forcompanyincompanies:
            company.sale_order_template_id=company.sale_order_template_idortemplate
