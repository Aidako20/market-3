#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError
fromflectra.osvimportexpression


classLocation(models.Model):
    _name="stock.location"
    _description="InventoryLocations"
    _parent_name="location_id"
    _parent_store=True
    _order='complete_name,id'
    _rec_name='complete_name'
    _check_company_auto=True

    @api.model
    defdefault_get(self,fields):
        res=super(Location,self).default_get(fields)
        if'barcode'infieldsand'barcode'notinresandres.get('complete_name'):
            res['barcode']=res['complete_name']
        returnres

    name=fields.Char('LocationName',required=True)
    complete_name=fields.Char("FullLocationName",compute='_compute_complete_name',store=True)
    active=fields.Boolean('Active',default=True,help="Byuncheckingtheactivefield,youmayhidealocationwithoutdeletingit.")
    usage=fields.Selection([
        ('supplier','VendorLocation'),
        ('view','View'),
        ('internal','InternalLocation'),
        ('customer','CustomerLocation'),
        ('inventory','InventoryLoss'),
        ('production','Production'),
        ('transit','TransitLocation')],string='LocationType',
        default='internal',index=True,required=True,
        help="*VendorLocation:Virtuallocationrepresentingthesourcelocationforproductscomingfromyourvendors"
             "\n*View:Virtuallocationusedtocreateahierarchicalstructuresforyourwarehouse,aggregatingitschildlocations;can'tdirectlycontainproducts"
             "\n*InternalLocation:Physicallocationsinsideyourownwarehouses,"
             "\n*CustomerLocation:Virtuallocationrepresentingthedestinationlocationforproductssenttoyourcustomers"
             "\n*InventoryLoss:Virtuallocationservingascounterpartforinventoryoperationsusedtocorrectstocklevels(Physicalinventories)"
             "\n*Production:Virtualcounterpartlocationforproductionoperations:thislocationconsumesthecomponentsandproducesfinishedproducts"
             "\n*TransitLocation:Counterpartlocationthatshouldbeusedininter-companyorinter-warehousesoperations")
    location_id=fields.Many2one(
        'stock.location','ParentLocation',index=True,ondelete='cascade',check_company=True,
        help="Theparentlocationthatincludesthislocation.Example:The'DispatchZone'isthe'Gate1'parentlocation.")
    child_ids=fields.One2many('stock.location','location_id','Contains')
    comment=fields.Text('AdditionalInformation')
    posx=fields.Integer('Corridor(X)',default=0,help="Optionallocalizationdetails,forinformationpurposeonly")
    posy=fields.Integer('Shelves(Y)',default=0,help="Optionallocalizationdetails,forinformationpurposeonly")
    posz=fields.Integer('Height(Z)',default=0,help="Optionallocalizationdetails,forinformationpurposeonly")
    parent_path=fields.Char(index=True)
    company_id=fields.Many2one(
        'res.company','Company',
        default=lambdaself:self.env.company,index=True,
        help='Letthisfieldemptyifthislocationissharedbetweencompanies')
    scrap_location=fields.Boolean('IsaScrapLocation?',default=False,help='Checkthisboxtoallowusingthislocationtoputscrapped/damagedgoods.')
    return_location=fields.Boolean('IsaReturnLocation?',help='Checkthisboxtoallowusingthislocationasareturnlocation.')
    removal_strategy_id=fields.Many2one('product.removal','RemovalStrategy',help="Definesthedefaultmethodusedforsuggestingtheexactlocation(shelf)wheretotaketheproductsfrom,whichlotetc.forthislocation.Thismethodcanbeenforcedattheproductcategorylevel,andafallbackismadeontheparentlocationsifnoneissethere.")
    putaway_rule_ids=fields.One2many('stock.putaway.rule','location_in_id','PutawayRules')
    barcode=fields.Char('Barcode',copy=False)
    quant_ids=fields.One2many('stock.quant','location_id')

    _sql_constraints=[('barcode_company_uniq','unique(barcode,company_id)','Thebarcodeforalocationmustbeuniquepercompany!')]

    @api.depends('name','location_id.complete_name','usage')
    def_compute_complete_name(self):
        forlocationinself:
            iflocation.location_idandlocation.usage!='view':
                location.complete_name='%s/%s'%(location.location_id.complete_name,location.name)
            else:
                location.complete_name=location.name

    @api.onchange('usage')
    def_onchange_usage(self):
        ifself.usagenotin('internal','inventory'):
            self.scrap_location=False

    defwrite(self,values):
        if'company_id'invalues:
            forlocationinself:
                iflocation.company_id.id!=values['company_id']:
                    raiseUserError(_("Changingthecompanyofthisrecordisforbiddenatthispoint,youshouldratherarchiveitandcreateanewone."))
        if'usage'invaluesandvalues['usage']=='view':
            ifself.mapped('quant_ids'):
                raiseUserError(_("Thislocation'susagecannotbechangedtoviewasitcontainsproducts."))
        if'usage'invaluesor'scrap_location'invalues:
            modified_locations=self.filtered(
                lambdal:any(l[f]!=values[f]iffinvalueselseFalse
                              forfin{'usage','scrap_location'}))
            reserved_quantities=self.env['stock.move.line'].search_count([
                ('location_id','in',modified_locations.ids),
                ('product_qty','>',0),
            ])
            ifreserved_quantities:
                raiseUserError(_(
                    "Youcannotchangethelocationtypeoritsuseasascrap"
                    "locationasthereareproductsreservedinthislocation."
                    "Pleaseunreservetheproductsfirst."
                ))
        if'active'invalues:
            ifvalues['active']==False:
                forlocationinself:
                    warehouses=self.env['stock.warehouse'].search([('active','=',True),'|',('lot_stock_id','=',location.id),('view_location_id','=',location.id)])
                    ifwarehouses:
                        raiseUserError(_("Youcannotarchivethelocation%sasitis"
                        "usedbyyourwarehouse%s")%(location.display_name,warehouses[0].display_name))

            ifnotself.env.context.get('do_not_check_quant'):
                children_location=self.env['stock.location'].with_context(active_test=False).search([('id','child_of',self.ids)])
                internal_children_locations=children_location.filtered(lambdal:l.usage=='internal')
                children_quants=self.env['stock.quant'].search(['&','|',('quantity','!=',0),('reserved_quantity','!=',0),('location_id','in',internal_children_locations.ids)])
                ifchildren_quantsandvalues['active']==False:
                    raiseUserError(_('Youstillhavesomeproductinlocations%s')%
                        (','.join(children_quants.mapped('location_id.display_name'))))
                else:
                    super(Location,children_location-self).with_context(do_not_check_quant=True).write({
                        'active':values['active'],
                    })

        returnsuper(Location,self).write(values)

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        """searchfullnameandbarcode"""
        args=argsor[]
        ifoperator=='ilike'andnot(nameor'').strip():
            domain=[]
        elifoperatorinexpression.NEGATIVE_TERM_OPERATORS:
            domain=[('barcode',operator,name),('complete_name',operator,name)]
        else:
            domain=['|',('barcode',operator,name),('complete_name',operator,name)]
        returnself._search(expression.AND([domain,args]),limit=limit,access_rights_uid=name_get_uid)

    def_get_putaway_strategy(self,product):
        '''Returnsthelocationwheretheproducthastobeput,ifanycompliantputawaystrategyisfound.OtherwisereturnsNone.'''
        current_location=self
        putaway_location=self.env['stock.location']
        whilecurrent_locationandnotputaway_location:
            #Lookingforaputawayabouttheproduct.
            putaway_rules=current_location.putaway_rule_ids.filtered(lambdax:x.product_id==product)
            ifputaway_rules:
                putaway_location=putaway_rules[0].location_out_id
            #Ifnotproductputawayfound,we'relookingwithcategoryso.
            else:
                categ=product.categ_id
                whilecateg:
                    putaway_rules=current_location.putaway_rule_ids.filtered(lambdax:x.category_id==categ)
                    ifputaway_rules:
                        putaway_location=putaway_rules[0].location_out_id
                        break
                    categ=categ.parent_id
            current_location=current_location.location_id
        returnputaway_location

    @api.returns('stock.warehouse',lambdavalue:value.id)
    defget_warehouse(self):
        """Returnswarehouseidofwarehousethatcontainslocation"""
        domain=[('view_location_id','parent_of',self.ids)]
        returnself.env['stock.warehouse'].search(domain,limit=1)

    defshould_bypass_reservation(self):
        self.ensure_one()
        returnself.usagein('supplier','customer','inventory','production')orself.scrap_locationor(self.usage=='transit'andnotself.company_id)


classRoute(models.Model):
    _name='stock.location.route'
    _description="InventoryRoutes"
    _order='sequence'
    _check_company_auto=True

    name=fields.Char('Route',required=True,translate=True)
    active=fields.Boolean('Active',default=True,help="IftheactivefieldissettoFalse,itwillallowyoutohidetheroutewithoutremovingit.")
    sequence=fields.Integer('Sequence',default=0)
    rule_ids=fields.One2many('stock.rule','route_id','Rules',copy=True)
    product_selectable=fields.Boolean('ApplicableonProduct',default=True,help="Whenchecked,theroutewillbeselectableintheInventorytaboftheProductform.")
    product_categ_selectable=fields.Boolean('ApplicableonProductCategory',help="Whenchecked,theroutewillbeselectableontheProductCategory.")
    warehouse_selectable=fields.Boolean('ApplicableonWarehouse',help="Whenawarehouseisselectedforthisroute,thisrouteshouldbeseenasthedefaultroutewhenproductspassthroughthiswarehouse.")
    supplied_wh_id=fields.Many2one('stock.warehouse','SuppliedWarehouse')
    supplier_wh_id=fields.Many2one('stock.warehouse','SupplyingWarehouse')
    company_id=fields.Many2one(
        'res.company','Company',
        default=lambdaself:self.env.company,index=True,
        help='Leavethisfieldemptyifthisrouteissharedbetweenallcompanies')
    product_ids=fields.Many2many(
        'product.template','stock_route_product','route_id','product_id',
        'Products',copy=False,check_company=True)
    categ_ids=fields.Many2many('product.category','stock_location_route_categ','route_id','categ_id','ProductCategories',copy=False)
    warehouse_domain_ids=fields.One2many('stock.warehouse',compute='_compute_warehouses')
    warehouse_ids=fields.Many2many(
        'stock.warehouse','stock_route_warehouse','route_id','warehouse_id',
        'Warehouses',copy=False,domain="[('id','in',warehouse_domain_ids)]")

    @api.depends('company_id')
    def_compute_warehouses(self):
        forlocinself:
            domain=[('company_id','=',loc.company_id.id)]ifloc.company_idelse[]
            loc.warehouse_domain_ids=self.env['stock.warehouse'].search(domain)

    @api.onchange('company_id')
    def_onchange_company(self):
        ifself.company_id:
            self.warehouse_ids=self.warehouse_ids.filtered(lambdaw:w.company_id==self.company_id)

    @api.onchange('warehouse_selectable')
    def_onchange_warehouse_selectable(self):
        ifnotself.warehouse_selectable:
            self.warehouse_ids=[(5,0,0)]

    deftoggle_active(self):
        forrouteinself:
            route.with_context(active_test=False).rule_ids.filtered(lambdaru:ru.active==route.active).toggle_active()
        super(Route,self).toggle_active()
