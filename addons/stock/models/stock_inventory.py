#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.addons.base.models.ir_modelimportMODULE_UNINSTALL_FLAG
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.osvimportexpression
fromflectra.toolsimportfloat_compare,float_is_zero
fromflectra.tools.miscimportOrderedSet


classInventory(models.Model):
    _name="stock.inventory"
    _description="Inventory"
    _order="datedesc,iddesc"
    _inherit=['mail.thread','mail.activity.mixin']

    name=fields.Char(
        'InventoryReference',default="Inventory",
        readonly=True,required=True,
        states={'draft':[('readonly',False)]})
    date=fields.Datetime(
        'InventoryDate',
        readonly=True,required=True,
        default=fields.Datetime.now,
        help="Iftheinventoryadjustmentisnotvalidated,dateatwhichthetheoriticalquantitieshavebeenchecked.\n"
             "Iftheinventoryadjustmentisvalidated,dateatwhichtheinventoryadjustmenthasbeenvalidated.")
    line_ids=fields.One2many(
        'stock.inventory.line','inventory_id',string='Inventories',
        copy=False,readonly=False,
        states={'done':[('readonly',True)]})
    move_ids=fields.One2many(
        'stock.move','inventory_id',string='CreatedMoves',
        states={'done':[('readonly',True)]})
    state=fields.Selection(string='Status',selection=[
        ('draft','Draft'),
        ('cancel','Cancelled'),
        ('confirm','InProgress'),
        ('done','Validated')],
        copy=False,index=True,readonly=True,tracking=True,
        default='draft')
    company_id=fields.Many2one(
        'res.company','Company',
        readonly=True,index=True,required=True,
        states={'draft':[('readonly',False)]},
        default=lambdaself:self.env.company)
    location_ids=fields.Many2many(
        'stock.location',string='Locations',
        readonly=True,check_company=True,
        states={'draft':[('readonly',False)]},
        domain="[('company_id','=',company_id),('usage','in',['internal','transit'])]")
    product_ids=fields.Many2many(
        'product.product',string='Products',check_company=True,
        domain="[('type','=','product'),'|',('company_id','=',False),('company_id','=',company_id)]",readonly=True,
        states={'draft':[('readonly',False)]},
        help="SpecifyProductstofocusyourinventoryonparticularProducts.")
    start_empty=fields.Boolean('EmptyInventory',
        help="Allowstostartwithanemptyinventory.")
    prefill_counted_quantity=fields.Selection(string='CountedQuantities',
        help="Allowstostartwithapre-filledcountedquantityforeachlinesor"
        "withallcountedquantitiessettozero.",default='counted',
        selection=[('counted','Defaulttostockonhand'),('zero','Defaulttozero')])
    exhausted=fields.Boolean(
        'IncludeExhaustedProducts',readonly=True,
        states={'draft':[('readonly',False)]},
        help="Includealsoproductswithquantityof0")

    @api.onchange('company_id')
    def_onchange_company_id(self):
        #Ifthemultilocationgroupisnotactive,defaultthelocationtotheoneofthemain
        #warehouse.
        ifnotself.user_has_groups('stock.group_stock_multi_locations'):
            warehouse=self.env['stock.warehouse'].search([('company_id','=',self.company_id.id)],limit=1)
            ifwarehouse:
                self.location_ids=warehouse.lot_stock_id

    defcopy_data(self,default=None):
        name=_("%s(copy)")%(self.name)
        default=dict(defaultor{},name=name)
        returnsuper(Inventory,self).copy_data(default)

    defunlink(self):
        forinventoryinself:
            if(inventory.statenotin('draft','cancel')
               andnotself.env.context.get(MODULE_UNINSTALL_FLAG,False)):
                raiseUserError(_('Youcanonlydeleteadraftinventoryadjustment.Iftheinventoryadjustmentisnotdone,youcancancelit.'))
        returnsuper(Inventory,self).unlink()

    defaction_validate(self):
        ifnotself.exists():
            return
        self.ensure_one()
        ifnotself.user_has_groups('stock.group_stock_manager'):
            raiseUserError(_("Onlyastockmanagercanvalidateaninventoryadjustment."))
        ifself.state!='confirm':
            raiseUserError(_(
                "Youcan'tvalidatetheinventory'%s',maybethisinventory"
                "hasbeenalreadyvalidatedorisn'tready.",self.name))
        inventory_lines=self.line_ids.filtered(lambdal:l.product_id.trackingin['lot','serial']andnotl.prod_lot_idandl.theoretical_qty!=l.product_qty)
        lines=self.line_ids.filtered(lambdal:float_compare(l.product_qty,1,precision_rounding=l.product_uom_id.rounding)>0andl.product_id.tracking=='serial'andl.prod_lot_id)
        ifinventory_linesandnotlines:
            wiz_lines=[(0,0,{'product_id':product.id,'tracking':product.tracking})forproductininventory_lines.mapped('product_id')]
            wiz=self.env['stock.track.confirmation'].create({'inventory_id':self.id,'tracking_line_ids':wiz_lines})
            return{
                'name':_('TrackedProductsinInventoryAdjustment'),
                'type':'ir.actions.act_window',
                'view_mode':'form',
                'views':[(False,'form')],
                'res_model':'stock.track.confirmation',
                'target':'new',
                'res_id':wiz.id,
            }
        self._action_done()
        self.line_ids._check_company()
        self._check_company()
        returnTrue

    def_action_done(self):
        negative=next((lineforlineinself.mapped('line_ids')ifline.product_qty<0andline.product_qty!=line.theoretical_qty),False)
        ifnegative:
            raiseUserError(_(
                'Youcannotsetanegativeproductquantityinaninventoryline:\n\t%s-qty:%s',
                negative.product_id.display_name,
                negative.product_qty
            ))
        self.action_check()
        self.write({'state':'done','date':fields.Datetime.now()})
        self.post_inventory()
        returnTrue

    defpost_inventory(self):
        #Theinventoryispostedasasinglestepwhichmeansquantscannotbemovedfromaninternallocationtoanotherusinganinventory
        #astheywillbemovedtoinventoryloss,andotherquantswillbecreatedtotheencodedquantlocation.Thisisanormalbehavior
        #asquantscannotbereusefrominventorylocation(userscanstillmanuallymovetheproductsbefore/aftertheinventoryiftheywant).
        self.mapped('move_ids').filtered(lambdamove:move.state!='done')._action_done()
        returnTrue

    defaction_check(self):
        """Checkstheinventoryandcomputesthestockmovetodo"""
        #tdetodo:cleanafter_generate_moves
        forinventoryinself.filtered(lambdax:x.statenotin('done','cancel')):
            #firstremovetheexistingstockmoveslinkedtothisinventory
            inventory.with_context(prefetch_fields=False).mapped('move_ids').unlink()
            inventory.line_ids._generate_moves()

    defaction_cancel_draft(self):
        self.mapped('move_ids')._action_cancel()
        self.line_ids.unlink()
        self.write({'state':'draft'})

    defaction_start(self):
        self.ensure_one()
        self._action_start()
        self._check_company()
        returnself.action_open_inventory_lines()

    def_action_start(self):
        """ConfirmstheInventoryAdjustmentandgeneratesitsinventorylines
        ifitsstateisdraftanddon'thavealreadyinventorylines(canhappen
        withdemodataortests).
        """
        forinventoryinself:
            ifinventory.state!='draft':
                continue
            vals={
                'state':'confirm',
                'date':fields.Datetime.now()
            }
            ifnotinventory.line_idsandnotinventory.start_empty:
                self.env['stock.inventory.line'].create(inventory._get_inventory_lines_values())
            inventory.write(vals)

    defaction_open_inventory_lines(self):
        self.ensure_one()
        action={
            'type':'ir.actions.act_window',
            'view_mode':'tree',
            'name':_('InventoryLines'),
            'res_model':'stock.inventory.line',
        }
        context={
            'default_is_editable':True,
            'default_inventory_id':self.id,
            'default_company_id':self.company_id.id,
        }
        #Definedomainsandcontext
        domain=[
            ('inventory_id','=',self.id),
            ('location_id.usage','in',['internal','transit'])
        ]
        ifself.location_ids:
            context['default_location_id']=self.location_ids[0].id
            iflen(self.location_ids)==1:
                ifnotself.location_ids[0].child_ids:
                    context['readonly_location_id']=True

        ifself.product_ids:
            #no_createonproduct_idfield
            action['view_id']=self.env.ref('stock.stock_inventory_line_tree_no_product_create').id
            iflen(self.product_ids)==1:
                context['default_product_id']=self.product_ids[0].id
        else:
            #noproduct_ids=>we'reallowedtocreatenewproductsintree
            action['view_id']=self.env.ref('stock.stock_inventory_line_tree').id

        action['context']=context
        action['domain']=domain
        returnaction

    defaction_view_related_move_lines(self):
        self.ensure_one()
        domain=[('move_id','in',self.move_ids.ids)]
        action={
            'name':_('ProductMoves'),
            'type':'ir.actions.act_window',
            'res_model':'stock.move.line',
            'view_type':'list',
            'view_mode':'list,form',
            'domain':domain,
        }
        returnaction

    defaction_print(self):
        returnself.env.ref('stock.action_report_inventory').report_action(self)

    def_get_quantities(self):
        """Returnquantitiesgroupbyproduct_id,location_id,lot_id,package_idandowner_id

        :return:adictwithkeysastupleofgroupbyandquantityasvalue
        :rtype:dict
        """
        self.ensure_one()
        ifself.location_ids:
            domain_loc=[('id','child_of',self.location_ids.ids)]
        else:
            domain_loc=[('company_id','=',self.company_id.id),('usage','in',['internal','transit'])]
        locations_ids=[l['id']forlinself.env['stock.location'].search_read(domain_loc,['id'])]

        domain=[('company_id','=',self.company_id.id),
                  ('quantity','!=','0'),
                  ('location_id','in',locations_ids)]
        ifself.prefill_counted_quantity=='zero':
            domain.append(('product_id.active','=',True))

        ifself.product_ids:
            domain=expression.AND([domain,[('product_id','in',self.product_ids.ids)]])

        fields=['product_id','location_id','lot_id','package_id','owner_id','quantity:sum']
        group_by=['product_id','location_id','lot_id','package_id','owner_id']

        quants=self.env['stock.quant'].read_group(domain,fields,group_by,lazy=False)
        return{(
            quant['product_id']andquant['product_id'][0]orFalse,
            quant['location_id']andquant['location_id'][0]orFalse,
            quant['lot_id']andquant['lot_id'][0]orFalse,
            quant['package_id']andquant['package_id'][0]orFalse,
            quant['owner_id']andquant['owner_id'][0]orFalse):
            quant['quantity']forquantinquants
        }

    def_get_exhausted_inventory_lines_vals(self,non_exhausted_set):
        """Returnthevaluesoftheinventorylinestocreateiftheuser
        wantstoincludeexhaustedproducts.Exhaustedproductsareproducts
        withoutquantitiesorquantityequalto0.

        :paramnon_exhausted_set:setoftuple(product_id,location_id)ofnonexhaustedproduct-location
        :return:alistcontainingthe`stock.inventory.line`valuestocreate
        :rtype:list
        """
        self.ensure_one()
        ifself.product_ids:
            product_ids=self.product_ids.ids
        else:
            product_ids=self.env['product.product'].search_read([
                '|',('company_id','=',self.company_id.id),('company_id','=',False),
                ('type','=','product'),
                ('active','=',True)],['id'])
            product_ids=[p['id']forpinproduct_ids]

        ifself.location_ids:
            location_ids=self.location_ids.ids
        else:
            location_ids=self.env['stock.warehouse'].search([('company_id','=',self.company_id.id)]).lot_stock_id.ids

        vals=[]
        forproduct_idinproduct_ids:
            forlocation_idinlocation_ids:
                if((product_id,location_id)notinnon_exhausted_set):
                    vals.append({
                        'inventory_id':self.id,
                        'product_id':product_id,
                        'location_id':location_id,
                        'theoretical_qty':0
                    })
        returnvals

    def_get_inventory_lines_values(self):
        """Returnthevaluesoftheinventorylinestocreateforthisinventory.

        :return:alistcontainingthe`stock.inventory.line`valuestocreate
        :rtype:list
        """
        self.ensure_one()
        quants_groups=self._get_quantities()
        vals=[]
        product_ids=OrderedSet()
        for(product_id,location_id,lot_id,package_id,owner_id),quantityinquants_groups.items():
            line_values={
                'inventory_id':self.id,
                'product_qty':0ifself.prefill_counted_quantity=="zero"elsequantity,
                'theoretical_qty':quantity,
                'prod_lot_id':lot_id,
                'partner_id':owner_id,
                'product_id':product_id,
                'location_id':location_id,
                'package_id':package_id
            }
            product_ids.add(product_id)
            vals.append(line_values)
        product_id_to_product=dict(zip(product_ids,self.env['product.product'].browse(product_ids)))
        forvalinvals:
            val['product_uom_id']=product_id_to_product[val['product_id']].product_tmpl_id.uom_id.id
        ifself.exhausted:
            vals+=self._get_exhausted_inventory_lines_vals({(l['product_id'],l['location_id'])forlinvals})
        returnvals


classInventoryLine(models.Model):
    _name="stock.inventory.line"
    _description="InventoryLine"
    _order="product_id,inventory_id,location_id,prod_lot_id"

    @api.model
    def_domain_location_id(self):
        ifself.env.context.get('active_model')=='stock.inventory':
            inventory=self.env['stock.inventory'].browse(self.env.context.get('active_id'))
            ifinventory.exists()andinventory.location_ids:
                return"[('company_id','=',company_id),('usage','in',['internal','transit']),('id','child_of',%s)]"%inventory.location_ids.ids
        return"[('company_id','=',company_id),('usage','in',['internal','transit'])]"

    @api.model
    def_domain_product_id(self):
        ifself.env.context.get('active_model')=='stock.inventory':
            inventory=self.env['stock.inventory'].browse(self.env.context.get('active_id'))
            ifinventory.exists()andlen(inventory.product_ids)>1:
                return"[('type','=','product'),'|',('company_id','=',False),('company_id','=',company_id),('id','in',%s)]"%inventory.product_ids.ids
        return"[('type','=','product'),'|',('company_id','=',False),('company_id','=',company_id)]"

    is_editable=fields.Boolean(help="Technicalfieldtorestrictediting.")
    inventory_id=fields.Many2one(
        'stock.inventory','Inventory',check_company=True,
        index=True,ondelete='cascade')
    partner_id=fields.Many2one('res.partner','Owner',check_company=True)
    product_id=fields.Many2one(
        'product.product','Product',check_company=True,
        domain=lambdaself:self._domain_product_id(),
        index=True,required=True)
    product_uom_id=fields.Many2one(
        'uom.uom','ProductUnitofMeasure',
        required=True,readonly=True)
    product_qty=fields.Float(
        'CountedQuantity',
        readonly=True,states={'confirm':[('readonly',False)]},
        digits='ProductUnitofMeasure',default=0)
    categ_id=fields.Many2one(related='product_id.categ_id',store=True)
    location_id=fields.Many2one(
        'stock.location','Location',check_company=True,
        domain=lambdaself:self._domain_location_id(),
        index=True,required=True)
    package_id=fields.Many2one(
        'stock.quant.package','Pack',index=True,check_company=True,
        domain="[('location_id','=',location_id)]",
    )
    prod_lot_id=fields.Many2one(
        'stock.production.lot','Lot/SerialNumber',check_company=True,
        domain="[('product_id','=',product_id),('company_id','=',company_id)]")
    company_id=fields.Many2one(
        'res.company','Company',related='inventory_id.company_id',
        index=True,readonly=True,store=True)
    state=fields.Selection(string='Status',related='inventory_id.state')
    theoretical_qty=fields.Float(
        'TheoreticalQuantity',
        digits='ProductUnitofMeasure',readonly=True)
    difference_qty=fields.Float('Difference',compute='_compute_difference',
        help="Indicatesthegapbetweentheproduct'stheoreticalquantityanditsnewestquantity.",
        readonly=True,digits='ProductUnitofMeasure',search="_search_difference_qty")
    inventory_date=fields.Datetime('InventoryDate',readonly=True,
        default=fields.Datetime.now,
        help="LastdateatwhichtheOnHandQuantityhasbeencomputed.")
    outdated=fields.Boolean(string='Quantityoutdated',
        compute='_compute_outdated',search='_search_outdated')
    product_tracking=fields.Selection(string='Tracking',related='product_id.tracking',readonly=True)

    @api.depends('product_qty','theoretical_qty')
    def_compute_difference(self):
        forlineinself:
            line.difference_qty=line.product_qty-line.theoretical_qty

    @api.depends('inventory_date','product_id.stock_move_ids','theoretical_qty','product_uom_id.rounding')
    def_compute_outdated(self):
        quants_by_inventory={inventory:inventory._get_quantities()forinventoryinself.inventory_id}
        forlineinself:
            quants=quants_by_inventory[line.inventory_id]
            ifline.state=='done'ornotline.id:
                line.outdated=False
                continue
            qty=quants.get((
                line.product_id.id,
                line.location_id.id,
                line.prod_lot_id.id,
                line.package_id.id,
                line.partner_id.id),0
            )
            iffloat_compare(qty,line.theoretical_qty,precision_rounding=line.product_uom_id.rounding)!=0:
                line.outdated=True
            else:
                line.outdated=False

    @api.onchange('product_id','location_id','product_uom_id','prod_lot_id','partner_id','package_id')
    def_onchange_quantity_context(self):
        ifself.product_id:
            self.product_uom_id=self.product_id.uom_id
        ifself.product_idandself.location_idandself.product_id.uom_id.category_id==self.product_uom_id.category_id: #TDEFIXME:lastpartaddedbecausecrash
            theoretical_qty=self.product_id.get_theoretical_quantity(
                self.product_id.id,
                self.location_id.id,
                lot_id=self.prod_lot_id.id,
                package_id=self.package_id.id,
                owner_id=self.partner_id.id,
                to_uom=self.product_uom_id.id,
            )
        else:
            theoretical_qty=0
        #Sanitycheckonthelot.
        ifself.prod_lot_id:
            ifself.product_id.tracking=='none'orself.product_id!=self.prod_lot_id.product_id:
                self.prod_lot_id=False

        ifself.prod_lot_idandself.product_id.tracking=='serial':
            #Weforce`product_qty`to1forSNtrackedproductbecauseit's
            #theonlyrelevantvalueaside0forthiskindofproduct.
            self.product_qty=1
        elifself.product_idandfloat_compare(self.product_qty,self.theoretical_qty,precision_rounding=self.product_uom_id.rounding)==0:
            #Weupdate`product_qty`onlyifitequalsto`theoretical_qty`to
            #avoidtoresetquantitywhenusermanuallysetit.
            self.product_qty=theoretical_qty
        self.theoretical_qty=theoretical_qty

    @api.model_create_multi
    defcreate(self,vals_list):
        """Overridetohandlethecasewecreateinventorylinewithout
        `theoretical_qty`becausethisfieldisusuallycomputed,butinsome
        case(typicalyintests),wecreateinventorylinewithouttriggerthe
        onchange,sointhiscase,weset`theoretical_qty`dependingofthe
        product'stheoreticalquantity.
        Handlesthesameproblemwith`product_uom_id`asthisfieldisnormally
        setinanonchangeof`product_id`.
        Finally,thisoverridecheckswedon'ttrytocreateaduplicatedline.
        """
        products=self.env['product.product'].browse([vals.get('product_id')forvalsinvals_list])
        forproduct,valuesinzip(products,vals_list):
            if'theoretical_qty'notinvalues:
                theoretical_qty=self.env['product.product'].get_theoretical_quantity(
                    values['product_id'],
                    values['location_id'],
                    lot_id=values.get('prod_lot_id'),
                    package_id=values.get('package_id'),
                    owner_id=values.get('partner_id'),
                    to_uom=values.get('product_uom_id'),
                )
                values['theoretical_qty']=theoretical_qty
            if'product_id'invaluesand'product_uom_id'notinvalues:
                values['product_uom_id']=product.product_tmpl_id.uom_id.id
        res=super(InventoryLine,self).create(vals_list)
        res._check_no_duplicate_line()
        returnres

    defwrite(self,vals):
        res=super(InventoryLine,self).write(vals)
        self._check_no_duplicate_line()
        returnres

    def_check_no_duplicate_line(self):
        domain=[
            ('product_id','in',self.product_id.ids),
            ('location_id','in',self.location_id.ids),
            '|',('partner_id','in',self.partner_id.ids),('partner_id','=',None),
            '|',('package_id','in',self.package_id.ids),('package_id','=',None),
            '|',('prod_lot_id','in',self.prod_lot_id.ids),('prod_lot_id','=',None),
            '|',('inventory_id','in',self.inventory_id.ids),('inventory_id','=',None),
        ]
        groupby_fields=['product_id','location_id','partner_id','package_id','prod_lot_id','inventory_id']
        lines_count={}
        forgroupinself.read_group(domain,['product_id'],groupby_fields,lazy=False):
            key=tuple([group[field]andgroup[field][0]forfieldingroupby_fields])
            lines_count[key]=group['__count']
        forlineinself:
            key=(line.product_id.id,line.location_id.id,line.partner_id.id,line.package_id.id,line.prod_lot_id.id,line.inventory_id.id)
            iflines_count[key]>1:
                raiseUserError(_("Thereisalreadyoneinventoryadjustmentlineforthisproduct,"
                                  "youshouldrathermodifythisoneinsteadofcreatinganewone."))

    @api.constrains('product_id')
    def_check_product_id(self):
        """Asnoquantsarecreatedforconsumableproducts,itshouldnotbepossibledoadjust
        theirquantity.
        """
        forlineinself:
            ifline.product_id.type!='product':
                raiseValidationError(_("Youcanonlyadjuststorableproducts.")+'\n\n%s->%s'%(line.product_id.display_name,line.product_id.type))

    def_get_move_values(self,qty,location_id,location_dest_id,out):
        self.ensure_one()
        return{
            'name':_('INV:')+(self.inventory_id.nameor''),
            'product_id':self.product_id.id,
            'product_uom':self.product_uom_id.id,
            'product_uom_qty':qty,
            'date':self.inventory_id.date,
            'company_id':self.inventory_id.company_id.id,
            'inventory_id':self.inventory_id.id,
            'state':'confirmed',
            'restrict_partner_id':self.partner_id.id,
            'location_id':location_id,
            'location_dest_id':location_dest_id,
            'move_line_ids':[(0,0,{
                'product_id':self.product_id.id,
                'lot_id':self.prod_lot_id.id,
                'product_uom_qty':0, #bypassreservationhere
                'product_uom_id':self.product_uom_id.id,
                'qty_done':qty,
                'package_id':outandself.package_id.idorFalse,
                'result_package_id':(notout)andself.package_id.idorFalse,
                'location_id':location_id,
                'location_dest_id':location_dest_id,
                'owner_id':self.partner_id.id,
            })]
        }

    def_get_virtual_location(self):
        returnself.product_id.with_company(self.company_id).property_stock_inventory

    def_generate_moves(self):
        vals_list=[]
        forlineinself:
            virtual_location=line._get_virtual_location()
            rounding=line.product_id.uom_id.rounding
            iffloat_is_zero(line.difference_qty,precision_rounding=rounding):
                continue
            ifline.difference_qty>0: #foundmorethanexpected
                vals=line._get_move_values(line.difference_qty,virtual_location.id,line.location_id.id,False)
            else:
                vals=line._get_move_values(abs(line.difference_qty),line.location_id.id,virtual_location.id,True)
            vals_list.append(vals)
        returnself.env['stock.move'].create(vals_list)

    defaction_refresh_quantity(self):
        filtered_lines=self.filtered(lambdal:l.state!='done')
        forlineinfiltered_lines:
            ifline.outdated:
                quants=self.env['stock.quant']._gather(line.product_id,line.location_id,lot_id=line.prod_lot_id,package_id=line.package_id,owner_id=line.partner_id,strict=True)
                ifquants.exists():
                    quantity=sum(quants.mapped('quantity'))
                    ifline.theoretical_qty!=quantity:
                        line.theoretical_qty=quantity
                else:
                    line.theoretical_qty=0
                line.inventory_date=fields.Datetime.now()

    defaction_reset_product_qty(self):
        """Write`product_qty`tozeroontheselectedrecords."""
        impacted_lines=self.env['stock.inventory.line']
        forlineinself:
            ifline.state=='done':
                continue
            impacted_lines|=line
        impacted_lines.write({'product_qty':0})

    def_search_difference_qty(self,operator,value):
        ifoperator=='=':
            result=True
        elifoperator=='!=':
            result=False
        else:
            raiseNotImplementedError()
        ifnotself.env.context.get('default_inventory_id'):
            raiseNotImplementedError(_('Unsupportedsearchon%soutsideofanInventoryAdjustment','difference_qty'))
        lines=self.search([('inventory_id','=',self.env.context.get('default_inventory_id'))])
        line_ids=lines.filtered(lambdaline:float_is_zero(line.difference_qty,precision_rounding=line.product_id.uom_id.rounding)==result).ids
        return[('id','in',line_ids)]

    def_search_outdated(self,operator,value):
        ifoperator!='=':
            ifoperator=='!='andisinstance(value,bool):
                value=notvalue
            else:
                raiseNotImplementedError()
        ifnotself.env.context.get('default_inventory_id'):
            raiseNotImplementedError(_('Unsupportedsearchon%soutsideofanInventoryAdjustment','outdated'))
        lines=self.search([('inventory_id','=',self.env.context.get('default_inventory_id'))])
        line_ids=lines.filtered(lambdaline:line.outdated==value).ids
        return[('id','in',line_ids)]
