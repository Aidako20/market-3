#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models


classCompany(models.Model):
    _inherit="res.company"
    _check_company_auto=True

    def_default_confirmation_mail_template(self):
        try:
            returnself.env.ref('stock.mail_template_data_delivery_confirmation').id
        exceptValueError:
            returnFalse

    internal_transit_location_id=fields.Many2one(
        'stock.location','InternalTransitLocation',ondelete="restrict",check_company=True,
        help="Technicalfieldusedforresupplyroutesbetweenwarehousesthatbelongtothiscompany")
    stock_move_email_validation=fields.Boolean("EmailConfirmationpicking",default=False)
    stock_mail_confirmation_template_id=fields.Many2one('mail.template',string="EmailTemplateconfirmationpicking",
        domain="[('model','=','stock.picking')]",
        default=_default_confirmation_mail_template,
        help="Emailsenttothecustomeroncetheorderisdone.")

    def_create_transit_location(self):
        '''Createatransitlocationwithcompany_idbeingthegivencompany_id.Thisisneeded
           incaseofresuplyroutesbetweenwarehousesbelongingtothesamecompany,because
           wedon'twanttocreateaccountingentriesatthattime.
        '''
        parent_location=self.env.ref('stock.stock_location_locations',raise_if_not_found=False)
        forcompanyinself:
            location=self.env['stock.location'].create({
                'name':_('Inter-warehousetransit'),
                'usage':'transit',
                'location_id':parent_locationandparent_location.idorFalse,
                'company_id':company.id,
                'active':False
            })

            company.write({'internal_transit_location_id':location.id})

            company.partner_id.with_company(company).write({
                'property_stock_customer':location.id,
                'property_stock_supplier':location.id,
            })

    def_create_inventory_loss_location(self):
        parent_location=self.env.ref('stock.stock_location_locations_virtual',raise_if_not_found=False)
        forcompanyinself:
            inventory_loss_location=self.env['stock.location'].create({
                'name':'Inventoryadjustment',
                'usage':'inventory',
                'location_id':parent_location.id,
                'company_id':company.id,
            })
            self.env['ir.property']._set_default(
                "property_stock_inventory",
                "product.template",
                inventory_loss_location,
                company.id,
            )

    def_create_production_location(self):
        parent_location=self.env.ref('stock.stock_location_locations_virtual',raise_if_not_found=False)
        forcompanyinself:
            production_location=self.env['stock.location'].create({
                'name':'Production',
                'usage':'production',
                'location_id':parent_location.id,
                'company_id':company.id,
            })
            self.env['ir.property']._set_default(
                "property_stock_production",
                "product.template",
                production_location,
                company.id,
            )


    def_create_scrap_location(self):
        parent_location=self.env.ref('stock.stock_location_locations_virtual',raise_if_not_found=False)
        forcompanyinself:
            scrap_location=self.env['stock.location'].create({
                'name':'Scrap',
                'usage':'inventory',
                'location_id':parent_location.id,
                'company_id':company.id,
                'scrap_location':True,
            })

    def_create_scrap_sequence(self):
        scrap_vals=[]
        forcompanyinself:
            scrap_vals.append({
                'name':'%sSequencescrap'%company.name,
                'code':'stock.scrap',
                'company_id':company.id,
                'prefix':'SP/',
                'padding':5,
                'number_next':1,
                'number_increment':1
            })
        ifscrap_vals:
            self.env['ir.sequence'].create(scrap_vals)

    @api.model
    defcreate_missing_warehouse(self):
        """Thishookisusedtoaddawarehouseonexistingcompanies
        whenmodulestockisinstalled.
        """
        company_ids =self.env['res.company'].search([])
        company_with_warehouse=self.env['stock.warehouse'].with_context(active_test=False).search([]).mapped('company_id')
        company_without_warehouse=company_ids-company_with_warehouse
        forcompanyincompany_without_warehouse:
            self.env['stock.warehouse'].create({
                'name':company.name,
                'code':company.name[:5],
                'company_id':company.id,
                'partner_id':company.partner_id.id,
            })

    @api.model
    defcreate_missing_transit_location(self):
        company_without_transit=self.env['res.company'].search([('internal_transit_location_id','=',False)])
        company_without_transit._create_transit_location()

    @api.model
    defcreate_missing_inventory_loss_location(self):
        company_ids =self.env['res.company'].search([])
        inventory_loss_product_template_field=self.env['ir.model.fields']._get('product.template','property_stock_inventory')
        companies_having_property=self.env['ir.property'].sudo().search([('fields_id','=',inventory_loss_product_template_field.id),('res_id','=',False)]).mapped('company_id')
        company_without_property=company_ids-companies_having_property
        company_without_property._create_inventory_loss_location()

    @api.model
    defcreate_missing_production_location(self):
        company_ids =self.env['res.company'].search([])
        production_product_template_field=self.env['ir.model.fields']._get('product.template','property_stock_production')
        companies_having_property=self.env['ir.property'].sudo().search([('fields_id','=',production_product_template_field.id),('res_id','=',False)]).mapped('company_id')
        company_without_property=company_ids-companies_having_property
        company_without_property._create_production_location()

    @api.model
    defcreate_missing_scrap_location(self):
        company_ids =self.env['res.company'].search([])
        companies_having_scrap_loc=self.env['stock.location'].search([('scrap_location','=',True)]).mapped('company_id')
        company_without_property=company_ids-companies_having_scrap_loc
        company_without_property._create_scrap_location()

    @api.model
    defcreate_missing_scrap_sequence(self):
        company_ids =self.env['res.company'].search([])
        company_has_scrap_seq=self.env['ir.sequence'].search([('code','=','stock.scrap')]).mapped('company_id')
        company_todo_sequence=company_ids-company_has_scrap_seq
        company_todo_sequence._create_scrap_sequence()

    def_create_per_company_locations(self):
        self.ensure_one()
        self._create_transit_location()
        self._create_inventory_loss_location()
        self._create_production_location()
        self._create_scrap_location()

    def_create_per_company_sequences(self):
        self.ensure_one()
        self._create_scrap_sequence()

    def_create_per_company_picking_types(self):
        self.ensure_one()

    def_create_per_company_rules(self):
        self.ensure_one()

    @api.model
    defcreate(self,vals):
        company=super(Company,self).create(vals)
        company.sudo()._create_per_company_locations()
        company.sudo()._create_per_company_sequences()
        company.sudo()._create_per_company_picking_types()
        company.sudo()._create_per_company_rules()
        self.env['stock.warehouse'].sudo().create({
            'name':company.name,
            'code':self.env.context.get('default_code')orcompany.name[:5],
            'company_id':company.id,
            'partner_id':company.partner_id.id
        })
        returncompany
