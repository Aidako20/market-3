#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classPartner(models.Model):
    _name='res.partner'
    _inherit='res.partner'

    #NOTAREALPROPERTY!!!!
    property_product_pricelist=fields.Many2one(
        'product.pricelist','Pricelist',compute='_compute_product_pricelist',
        inverse="_inverse_product_pricelist",company_dependent=False,
        domain=lambdaself:[('company_id','in',(self.env.company.id,False))],
        help="Thispricelistwillbeused,insteadofthedefaultone,forsalestothecurrentpartner")

    @api.depends('country_id')
    @api.depends_context('company')
    def_compute_product_pricelist(self):
        company=self.env.company.id
        res=self.env['product.pricelist']._get_partner_pricelist_multi(self.ids,company_id=company)
        forpinself:
            p.property_product_pricelist=res.get(p.id)

    def_inverse_product_pricelist(self):
        forpartnerinself:
            pls=self.env['product.pricelist'].search(
                [('country_group_ids.country_ids.code','=',partner.country_idandpartner.country_id.codeorFalse)],
                limit=1
            )
            default_for_country=plsandpls[0]
            actual=self.env['ir.property']._get('property_product_pricelist','res.partner','res.partner,%s'%partner.id)
            #updateateachchangecountry,andsoeraseoldpricelist
            ifpartner.property_product_pricelistor(actualanddefault_for_countryanddefault_for_country.id!=actual.id):
                #keepthecompanyofthecurrentuserbeforesudo
                self.env['ir.property']._set_multi(
                    'property_product_pricelist',
                    partner._name,
                    {partner.id:partner.property_product_pricelistordefault_for_country.id},
                    default_value=default_for_country.id
                )

    def_commercial_fields(self):
        returnsuper(Partner,self)._commercial_fields()+['property_product_pricelist']
