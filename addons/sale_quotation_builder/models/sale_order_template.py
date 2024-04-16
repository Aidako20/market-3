#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.tools.translateimporthtml_translate


classSaleOrderTemplate(models.Model):
    _inherit="sale.order.template"

    website_description=fields.Html('WebsiteDescription',translate=html_translate,sanitize_attributes=False,sanitize_form=False)

    defopen_template(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_url',
            'target':'self',
            'url':'/sale_quotation_builder/template/%d'%self.id
        }


classSaleOrderTemplateLine(models.Model):
    _inherit="sale.order.template.line"

    website_description=fields.Html('WebsiteDescription',related='product_id.product_tmpl_id.quotation_only_description',translate=html_translate,readonly=False,sanitize_form=False)

    @api.onchange('product_id')
    def_onchange_product_id(self):
        ret=super(SaleOrderTemplateLine,self)._onchange_product_id()
        ifself.product_id:
            self.website_description=self.product_id.quotation_description
        returnret

    @api.model
    defcreate(self,values):
        values=self._inject_quotation_description(values)
        returnsuper(SaleOrderTemplateLine,self).create(values)

    defwrite(self,values):
        values=self._inject_quotation_description(values)
        returnsuper(SaleOrderTemplateLine,self).write(values)

    def_inject_quotation_description(self,values):
        values=dict(valuesor{})
        ifnotvalues.get('website_description')andvalues.get('product_id'):
            product=self.env['product.product'].browse(values['product_id'])
            values['website_description']=product.quotation_description
        returnvalues


classSaleOrderTemplateOption(models.Model):
    _inherit="sale.order.template.option"

    website_description=fields.Html('WebsiteDescription',translate=html_translate,sanitize_attributes=False)

    @api.onchange('product_id')
    def_onchange_product_id(self):
        ret=super(SaleOrderTemplateOption,self)._onchange_product_id()
        ifself.product_id:
            self.website_description=self.product_id.quotation_description
        returnret
