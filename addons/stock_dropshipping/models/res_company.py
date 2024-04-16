#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classResCompany(models.Model):
    _inherit='res.company'

    #-------------------------------------------------------------------------
    #Sequences
    #-------------------------------------------------------------------------
    def_create_dropship_sequence(self):
        dropship_vals=[]
        forcompanyinself:
            dropship_vals.append({
                'name':'Dropship(%s)'%company.name,
                'code':'stock.dropshipping',
                'company_id':company.id,
                'prefix':'DS/',
                'padding':5,
            })
        ifdropship_vals:
            self.env['ir.sequence'].create(dropship_vals)

    @api.model
    defcreate_missing_dropship_sequence(self):
        company_ids=self.env['res.company'].search([])
        company_has_dropship_seq=self.env['ir.sequence'].search([('code','=','stock.dropshipping')]).mapped('company_id')
        company_todo_sequence=company_ids-company_has_dropship_seq
        company_todo_sequence._create_dropship_sequence()

    def_create_per_company_sequences(self):
        super(ResCompany,self)._create_per_company_sequences()
        self._create_dropship_sequence()

    #-------------------------------------------------------------------------
    #Pickingtypes
    #-------------------------------------------------------------------------
    def_create_dropship_picking_type(self):
        dropship_vals=[]
        forcompanyinself:
            sequence=self.env['ir.sequence'].search([
                ('code','=','stock.dropshipping'),
                ('company_id','=',company.id),
            ])
            dropship_vals.append({
                'name':'Dropship',
                'company_id':company.id,
                'warehouse_id':False,
                'sequence_id':sequence.id,
                'code':'incoming',
                'default_location_src_id':self.env.ref('stock.stock_location_suppliers').id,
                'default_location_dest_id':self.env.ref('stock.stock_location_customers').id,
                'sequence_code':'DS',
            })
        ifdropship_vals:
            self.env['stock.picking.type'].create(dropship_vals)

    @api.model
    defcreate_missing_dropship_picking_type(self):
        company_ids=self.env['res.company'].search([])
        company_has_dropship_picking_type=(
            self.env['stock.picking.type']
            .search([
                ('default_location_src_id.usage','=','supplier'),
                ('default_location_dest_id.usage','=','customer'),
            ])
            .mapped('company_id')
        )
        company_todo_picking_type=company_ids-company_has_dropship_picking_type
        company_todo_picking_type._create_dropship_picking_type()

    def_create_per_company_picking_types(self):
        super(ResCompany,self)._create_per_company_picking_types()
        self._create_dropship_picking_type()

    #-------------------------------------------------------------------------
    #Stockrules
    #-------------------------------------------------------------------------
    def_create_dropship_rule(self):
        dropship_route=self.env.ref('stock_dropshipping.route_drop_shipping')
        supplier_location=self.env.ref('stock.stock_location_suppliers')
        customer_location=self.env.ref('stock.stock_location_customers')

        dropship_vals=[]
        forcompanyinself:
            dropship_picking_type=self.env['stock.picking.type'].search([
                ('company_id','=',company.id),
                ('default_location_src_id.usage','=','supplier'),
                ('default_location_dest_id.usage','=','customer'),
            ],limit=1,order='sequence')
            ifnotdropship_picking_type:
                continue
            dropship_vals.append({
                'name':'%s→%s'%(supplier_location.name,customer_location.name),
                'action':'buy',
                'location_id':customer_location.id,
                'location_src_id':supplier_location.id,
                'procure_method':'make_to_stock',
                'route_id':dropship_route.id,
                'picking_type_id':dropship_picking_type.id,
                'company_id':company.id,
            })
        ifdropship_vals:
            self.env['stock.rule'].create(dropship_vals)

    @api.model
    defcreate_missing_dropship_rule(self):
        dropship_route=self.env.ref('stock_dropshipping.route_drop_shipping')

        company_ids=self.env['res.company'].search([])
        company_has_dropship_rule=self.env['stock.rule'].search([('route_id','=',dropship_route.id)]).mapped('company_id')
        company_todo_rule=company_ids-company_has_dropship_rule
        company_todo_rule._create_dropship_rule()

    def_create_per_company_rules(self):
        super(ResCompany,self)._create_per_company_rules()
        self._create_dropship_rule()
