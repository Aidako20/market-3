#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api
fromflectra.tools.translateimporthtml_translate


classProductTemplate(models.Model):
    _inherit="product.template"

    quotation_only_description=fields.Html('QuotationOnlyDescription',sanitize_attributes=False,
        translate=html_translate,help="Thequotationdescription(notusedoneCommerce)")

    quotation_description=fields.Html('QuotationDescription',compute='_compute_quotation_description',
        sanitize_attributes=False,help="ThisfieldusestheQuotationOnlyDescriptionifitisdefined,otherwiseitwilltrytoreadtheeCommerceDescription.")

    def_compute_quotation_description(self):
        forrecordinself:
            ifrecord.quotation_only_description:
                record.quotation_description=record.quotation_only_description
            elifhasattr(record,'website_description')andrecord.website_description:
                record.quotation_description=record.website_description
            else:
                record.quotation_description=''
