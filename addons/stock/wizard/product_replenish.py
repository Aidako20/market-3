#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError
fromflectra.tools.miscimportclean_context


classProductReplenish(models.TransientModel):
    _name='product.replenish'
    _description='ProductReplenish'

    product_id=fields.Many2one('product.product',string='Product',required=True)
    product_tmpl_id=fields.Many2one('product.template',string='ProductTemplate',required=True)
    product_has_variants=fields.Boolean('Hasvariants',default=False,required=True)
    product_uom_category_id=fields.Many2one('uom.category',related='product_id.uom_id.category_id',readonly=True,required=True)
    product_uom_id=fields.Many2one('uom.uom',string='Unitofmeasure',required=True)
    quantity=fields.Float('Quantity',default=1,required=True)
    date_planned=fields.Datetime('ScheduledDate',required=True,help="Dateatwhichthereplenishmentshouldtakeplace.")
    warehouse_id=fields.Many2one(
        'stock.warehouse',string='Warehouse',required=True,
        domain="[('company_id','=',company_id)]")
    route_ids=fields.Many2many(
        'stock.location.route',string='PreferredRoutes',
        help="Applyspecificroute(s)forthereplenishmentinsteadofproduct'sdefaultroutes.",
        domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    company_id=fields.Many2one('res.company')

    @api.model
    defdefault_get(self,fields):
        res=super(ProductReplenish,self).default_get(fields)
        product_tmpl_id=self.env['product.template']
        if'product_id'infields:
            ifself.env.context.get('default_product_id'):
                product_id=self.env['product.product'].browse(self.env.context['default_product_id'])
                product_tmpl_id=product_id.product_tmpl_id
                res['product_tmpl_id']=product_id.product_tmpl_id.id
                res['product_id']=product_id.id
            elifself.env.context.get('default_product_tmpl_id'):
                product_tmpl_id=self.env['product.template'].browse(self.env.context['default_product_tmpl_id'])
                res['product_tmpl_id']=product_tmpl_id.id
                res['product_id']=product_tmpl_id.product_variant_id.id
                iflen(product_tmpl_id.product_variant_ids)>1:
                    res['product_has_variants']=True
        company=product_tmpl_id.company_idorself.env.company
        if'product_uom_id'infields:
            res['product_uom_id']=product_tmpl_id.uom_id.id
        if'company_id'infields:
            res['company_id']=company.id
        if'warehouse_id'infieldsand'warehouse_id'notinres:
            warehouse=self.env['stock.warehouse'].search([('company_id','=',company.id)],limit=1)
            res['warehouse_id']=warehouse.id
        if'date_planned'infields:
            res['date_planned']=datetime.datetime.now()
        returnres

    deflaunch_replenishment(self):
        uom_reference=self.product_id.uom_id
        self.quantity=self.product_uom_id._compute_quantity(self.quantity,uom_reference)
        try:
            self.env['procurement.group'].with_context(clean_context(self.env.context)).run([
                self.env['procurement.group'].Procurement(
                    self.product_id,
                    self.quantity,
                    uom_reference,
                    self.warehouse_id.lot_stock_id, #Location
                    _("ManualReplenishment"), #Name
                    _("ManualReplenishment"), #Origin
                    self.warehouse_id.company_id,
                    self._prepare_run_values() #Values
                )
            ])
        exceptUserErroraserror:
            raiseUserError(error)

    def_prepare_run_values(self):
        replenishment=self.env['procurement.group'].create({
            'partner_id':self.product_id.with_company(self.company_id).responsible_id.partner_id.id,
        })

        values={
            'warehouse_id':self.warehouse_id,
            'route_ids':self.route_ids,
            'date_planned':self.date_planned,
            'group_id':replenishment,
        }
        returnvalues
