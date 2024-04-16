#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    group_sale_order_template=fields.Boolean(
        "QuotationTemplates",implied_group='sale_management.group_sale_order_template')
    company_so_template_id=fields.Many2one(
        related="company_id.sale_order_template_id",string="DefaultTemplate",readonly=False,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    module_sale_quotation_builder=fields.Boolean("QuotationBuilder")

    @api.onchange('group_sale_order_template')
    def_onchange_group_sale_order_template(self):
        ifnotself.group_sale_order_template:
            self.module_sale_quotation_builder=False

    defset_values(self):
        ifnotself.group_sale_order_template:
            self.company_so_template_id=None
            self.env['res.company'].sudo().search([]).write({
                'sale_order_template_id':False,
            })
        returnsuper(ResConfigSettings,self).set_values()
