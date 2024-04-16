#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classResCompany(models.Model):
    _inherit='res.company'

    subcontracting_location_id=fields.Many2one('stock.location')

    @api.model
    defcreate_missing_subcontracting_location(self):
        company_without_subcontracting_loc=self.env['res.company'].search(
            [('subcontracting_location_id','=',False)])
        company_without_subcontracting_loc._create_subcontracting_location()

    def_create_per_company_locations(self):
        super(ResCompany,self)._create_per_company_locations()
        self._create_subcontracting_location()

    def_create_subcontracting_location(self):
        parent_location=self.env.ref('stock.stock_location_locations',raise_if_not_found=False)
        forcompanyinself:
            subcontracting_location=self.env['stock.location'].create({
                'name':_('SubcontractingLocation'),
                'usage':'internal',
                'location_id':parent_location.id,
                'company_id':company.id,
            })
            self.env['ir.property']._set_default(
                "property_stock_subcontractor",
                "res.partner",
                subcontracting_location,
                company,
            )
            company.subcontracting_location_id=subcontracting_location
