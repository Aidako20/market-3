#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.tools.translateimporthtml_translate


classSaleOrder(models.Model):
    _inherit='sale.order'

    website_description=fields.Html('WebsiteDescription',sanitize_attributes=False,translate=html_translate,sanitize_form=False)

    @api.onchange('partner_id')
    defonchange_update_description_lang(self):
        ifnotself.sale_order_template_id:
            return
        else:
            template=self.sale_order_template_id.with_context(lang=self.partner_id.lang)
            self.website_description=template.website_description

    def_compute_line_data_for_template_change(self,line):
        vals=super(SaleOrder,self)._compute_line_data_for_template_change(line)
        vals.update(website_description=line.website_description)
        returnvals

    def_compute_option_data_for_template_change(self,option):
        vals=super(SaleOrder,self)._compute_option_data_for_template_change(option)
        vals.update(website_description=option.website_description)
        returnvals

    @api.onchange('sale_order_template_id')
    defonchange_sale_order_template_id(self):
        ret=super(SaleOrder,self).onchange_sale_order_template_id()
        ifself.sale_order_template_id:
            template=self.sale_order_template_id.with_context(lang=self.partner_id.lang)
            self.website_description=template.website_description
        returnret


classSaleOrderLine(models.Model):
    _inherit="sale.order.line"

    website_description=fields.Html('WebsiteDescription',sanitize=False,translate=html_translate,sanitize_form=False)

    @api.model
    defcreate(self,values):
        values=self._inject_quotation_description(values)
        returnsuper(SaleOrderLine,self).create(values)

    defwrite(self,values):
        values=self._inject_quotation_description(values)
        returnsuper(SaleOrderLine,self).write(values)

    def_inject_quotation_description(self,values):
        values=dict(valuesor{})
        ifnotvalues.get('website_description')andvalues.get('product_id'):
            product=self.env['product.product'].browse(values['product_id'])
            values.update(website_description=product.quotation_description)
        returnvalues


classSaleOrderOption(models.Model):
    _inherit="sale.order.option"

    website_description=fields.Html('WebsiteDescription',sanitize_attributes=False,translate=html_translate)

    @api.onchange('product_id','uom_id')
    def_onchange_product_id(self):
        ret=super(SaleOrderOption,self)._onchange_product_id()
        ifself.product_id:
            product=self.product_id.with_context(lang=self.order_id.partner_id.lang)
            self.website_description=product.quotation_description
        returnret

    def_get_values_to_add_to_order(self):
        values=super(SaleOrderOption,self)._get_values_to_add_to_order()
        values.update(website_description=self.website_description)
        returnvalues
