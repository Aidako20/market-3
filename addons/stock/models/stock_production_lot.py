#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError,ValidationError


classProductionLot(models.Model):
    _name='stock.production.lot'
    _inherit=['mail.thread','mail.activity.mixin']
    _description='Lot/Serial'
    _check_company_auto=True
    _order='name,id'

    name=fields.Char(
        'Lot/SerialNumber',default=lambdaself:self.env['ir.sequence'].next_by_code('stock.lot.serial'),
        required=True,help="UniqueLot/SerialNumber")
    ref=fields.Char('InternalReference',help="Internalreferencenumberincaseitdiffersfromthemanufacturer'slot/serialnumber")
    product_id=fields.Many2one(
        'product.product','Product',
        domain=lambdaself:self._domain_product_id(),required=True,check_company=True)
    product_uom_id=fields.Many2one(
        'uom.uom','UnitofMeasure',
        related='product_id.uom_id',store=True,readonly=False)
    quant_ids=fields.One2many('stock.quant','lot_id','Quants',readonly=True)
    product_qty=fields.Float('Quantity',compute='_product_qty')
    note=fields.Html(string='Description')
    display_complete=fields.Boolean(compute='_compute_display_complete')
    company_id=fields.Many2one('res.company','Company',required=True,store=True,index=True,default=lambdaself:self.env.company.id)

    @api.constrains('name','product_id','company_id')
    def_check_unique_lot(self):
        domain=[('product_id','in',self.product_id.ids),
                  ('company_id','in',self.company_id.ids),
                  ('name','in',self.mapped('name'))]
        fields=['company_id','product_id','name']
        groupby=['company_id','product_id','name']
        records=self.read_group(domain,fields,groupby,lazy=False)
        error_message_lines=[]
        forrecinrecords:
            ifrec['__count']!=1:
                product_name=self.env['product.product'].browse(rec['product_id'][0]).display_name
                error_message_lines.append(_("-Product:%s,SerialNumber:%s",product_name,rec['name']))
        iferror_message_lines:
            raiseValidationError(_('Thecombinationofserialnumberandproductmustbeuniqueacrossacompany.\nFollowingcombinationcontainsduplicates:\n')+'\n'.join(error_message_lines))

    def_domain_product_id(self):
        domain=[
            "('tracking','!=','none')",
            "('type','=','product')",
            "'|'",
                "('company_id','=',False)",
                "('company_id','=',company_id)"
        ]
        ifself.env.context.get('default_product_tmpl_id'):
            domain.insert(0,
                ("('product_tmpl_id','=',%s)"%self.env.context['default_product_tmpl_id'])
            )
        return'['+','.join(domain)+']'

    def_check_create(self):
        active_picking_id=self.env.context.get('active_picking_id',False)
        ifactive_picking_id:
            picking_id=self.env['stock.picking'].browse(active_picking_id)
            ifpicking_idandnotpicking_id.picking_type_id.use_create_lots:
                raiseUserError(_('Youarenotallowedtocreatealotorserialnumberwiththisoperationtype.Tochangethis,goontheoperationtypeandtickthebox"CreateNewLots/SerialNumbers".'))

    @api.depends('name')
    def_compute_display_complete(self):
        """Definesifwewanttodisplayallfieldsinthestock.production.lotformview.
        Itwilliftherecordexists(`id`set)orifwepreciseditintothecontext.
        Thiscomputedependsonfield`name`becauseasithasalwaysadefaultvalue,it'llbe
        alwaystriggered.
        """
        forprod_lotinself:
            prod_lot.display_complete=prod_lot.idorself._context.get('display_complete')

    @api.model_create_multi
    defcreate(self,vals_list):
        self._check_create()
        returnsuper(ProductionLot,self.with_context(mail_create_nosubscribe=True)).create(vals_list)

    defwrite(self,vals):
        if'company_id'invals:
            forlotinself:
                iflot.company_id.id!=vals['company_id']:
                    raiseUserError(_("Changingthecompanyofthisrecordisforbiddenatthispoint,youshouldratherarchiveitandcreateanewone."))
        if'product_id'invalsandany(vals['product_id']!=lot.product_id.idforlotinself):
            move_lines=self.env['stock.move.line'].search([('lot_id','in',self.ids),('product_id','!=',vals['product_id'])])
            ifmove_lines:
                raiseUserError(_(
                    'Youarenotallowedtochangetheproductlinkedtoaserialorlotnumber'
                    'ifsomestockmoveshavealreadybeencreatedwiththatnumber.'
                    'Thiswouldleadtoinconsistenciesinyourstock.'
                ))
        returnsuper(ProductionLot,self).write(vals)

    @api.depends('quant_ids','quant_ids.quantity')
    def_product_qty(self):
        forlotinself:
            #Weonlycareforthequantsininternalortransitlocations.
            quants=lot.quant_ids.filtered(lambdaq:q.location_id.usage=='internal'or(q.location_id.usage=='transit'andq.location_id.company_id))
            lot.product_qty=sum(quants.mapped('quantity'))

    defaction_lot_open_quants(self):
        self=self.with_context(search_default_lot_id=self.id,create=False)
        ifself.user_has_groups('stock.group_stock_manager'):
            self=self.with_context(inventory_mode=True)
        returnself.env['stock.quant']._get_quants_action()
