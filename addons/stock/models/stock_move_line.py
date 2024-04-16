#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportCounter,defaultdict

fromflectraimport_,api,fields,tools,models
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.toolsimportOrderedSet
fromflectra.tools.float_utilsimportfloat_compare,float_is_zero,float_round


classStockMoveLine(models.Model):
    _name="stock.move.line"
    _description="ProductMoves(StockMoveLine)"
    _rec_name="product_id"
    _order="result_package_iddesc,id"

    picking_id=fields.Many2one(
        'stock.picking','Transfer',auto_join=True,
        check_company=True,
        index=True,
        help='Thestockoperationwherethepackinghasbeenmade')
    move_id=fields.Many2one(
        'stock.move','StockMove',
        check_company=True,
        help="Changetoabettername",index=True)
    company_id=fields.Many2one('res.company',string='Company',readonly=True,required=True,index=True)
    product_id=fields.Many2one('product.product','Product',ondelete="cascade",check_company=True,domain="[('type','!=','service'),'|',('company_id','=',False),('company_id','=',company_id)]",index=True)
    product_uom_id=fields.Many2one('uom.uom','UnitofMeasure',required=True,domain="[('category_id','=',product_uom_category_id)]")
    product_uom_category_id=fields.Many2one(related='product_id.uom_id.category_id')
    product_qty=fields.Float(
        'RealReservedQuantity',digits=0,copy=False,
        compute='_compute_product_qty',inverse='_set_product_qty',store=True)
    product_uom_qty=fields.Float(
        'Reserved',default=0.0,digits='ProductUnitofMeasure',required=True,copy=False)
    qty_done=fields.Float('Done',default=0.0,digits='ProductUnitofMeasure',copy=False)
    package_id=fields.Many2one(
        'stock.quant.package','SourcePackage',ondelete='restrict',
        check_company=True,
        domain="[('location_id','=',location_id)]")
    package_level_id=fields.Many2one('stock.package_level','PackageLevel',check_company=True)
    lot_id=fields.Many2one(
        'stock.production.lot','Lot/SerialNumber',
        domain="[('product_id','=',product_id),('company_id','=',company_id)]",check_company=True)
    lot_name=fields.Char('Lot/SerialNumberName')
    result_package_id=fields.Many2one(
        'stock.quant.package','DestinationPackage',
        ondelete='restrict',required=False,check_company=True,
        domain="['|','|',('location_id','=',False),('location_id','=',location_dest_id),('id','=',package_id)]",
        help="Ifset,theoperationsarepackedintothispackage")
    date=fields.Datetime('Date',default=fields.Datetime.now,required=True)
    owner_id=fields.Many2one(
        'res.partner','FromOwner',
        check_company=True,
        help="Whenvalidatingthetransfer,theproductswillbetakenfromthisowner.")
    location_id=fields.Many2one('stock.location','From',check_company=True,required=True)
    location_dest_id=fields.Many2one('stock.location','To',check_company=True,required=True)
    lots_visible=fields.Boolean(compute='_compute_lots_visible')
    picking_code=fields.Selection(related='picking_id.picking_type_id.code',readonly=True)
    picking_type_use_create_lots=fields.Boolean(related='picking_id.picking_type_id.use_create_lots',readonly=True)
    picking_type_use_existing_lots=fields.Boolean(related='picking_id.picking_type_id.use_existing_lots',readonly=True)
    state=fields.Selection(related='move_id.state',store=True,related_sudo=False)
    is_initial_demand_editable=fields.Boolean(related='move_id.is_initial_demand_editable',readonly=False)
    is_locked=fields.Boolean(related='move_id.is_locked',default=True,readonly=True)
    consume_line_ids=fields.Many2many('stock.move.line','stock_move_line_consume_rel','consume_line_id','produce_line_id',help="Technicallinktoseewhoconsumedwhat.")
    produce_line_ids=fields.Many2many('stock.move.line','stock_move_line_consume_rel','produce_line_id','consume_line_id',help="Technicallinktoseewhichlinewasproducedwiththis.")
    reference=fields.Char(related='move_id.reference',store=True,related_sudo=False,readonly=False)
    tracking=fields.Selection(related='product_id.tracking',readonly=True)
    origin=fields.Char(related='move_id.origin',string='Source')
    picking_type_entire_packs=fields.Boolean(related='picking_id.picking_type_id.show_entire_packs',readonly=True)
    description_picking=fields.Text(string="Descriptionpicking")

    @api.depends('picking_id.picking_type_id','product_id.tracking')
    def_compute_lots_visible(self):
        forlineinself:
            picking=line.picking_id
            ifpicking.picking_type_idandline.product_id.tracking!='none': #TDEFIXME:notsurecorrectlymigrated
                line.lots_visible=picking.picking_type_id.use_existing_lotsorpicking.picking_type_id.use_create_lots
            else:
                line.lots_visible=line.product_id.tracking!='none'

    @api.depends('product_id','product_id.uom_id','product_uom_id','product_uom_qty')
    def_compute_product_qty(self):
        forlineinself:
            line.product_qty=line.product_uom_id._compute_quantity(line.product_uom_qty,line.product_id.uom_id,rounding_method='HALF-UP')

    def_set_product_qty(self):
        """Themeaningofproduct_qtyfieldchangedlatelyandisnowafunctionalfieldcomputingthequantity
        inthedefaultproductUoM.Thiscodehasbeenaddedtoraiseanerrorifawriteismadegivenavalue
        for`product_qty`,wherethesamewriteshouldsetthe`product_uom_qty`fieldinstead,inorderto
        detecterrors."""
        raiseUserError(_('Therequestedoperationcannotbeprocessedbecauseofaprogrammingerrorsettingthe`product_qty`fieldinsteadofthe`product_uom_qty`.'))

    @api.constrains('lot_id','product_id')
    def_check_lot_product(self):
        forlineinself:
            ifline.lot_idandline.product_id!=line.lot_id.sudo().product_id:
                raiseValidationError(_(
                    'Thislot%(lot_name)sisincompatiblewiththisproduct%(product_name)s',
                    lot_name=line.lot_id.name,
                    product_name=line.product_id.display_name
                ))

    @api.constrains('product_uom_qty')
    def_check_reserved_done_quantity(self):
        formove_lineinself:
            ifmove_line.state=='done'andnotfloat_is_zero(move_line.product_uom_qty,precision_digits=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')):
                raiseValidationError(_('Adonemovelineshouldneverhaveareservedquantity.'))

    @api.constrains('qty_done')
    def_check_positive_qty_done(self):
        ifany([ml.qty_done<0formlinself]):
            raiseValidationError(_('Youcannotenternegativequantities.'))

    @api.onchange('product_id','product_uom_id')
    def_onchange_product_id(self):
        ifself.product_id:
            ifnotself.idandself.user_has_groups('stock.group_stock_multi_locations'):
                self.location_dest_id=self.location_dest_id._get_putaway_strategy(self.product_id)orself.location_dest_id
            ifself.picking_id:
                product=self.product_id.with_context(lang=self.picking_id.partner_id.langorself.env.user.lang)
                self.description_picking=product._get_description(self.picking_id.picking_type_id)
            self.lots_visible=self.product_id.tracking!='none'
            ifnotself.product_uom_idorself.product_uom_id.category_id!=self.product_id.uom_id.category_id:
                ifself.move_id.product_uom:
                    self.product_uom_id=self.move_id.product_uom.id
                else:
                    self.product_uom_id=self.product_id.uom_id.id

    @api.onchange('lot_name','lot_id')
    def_onchange_serial_number(self):
        """Whentheuserisencodingamovelineforatrackedproduct,weapplysomelogicto
        helphim.Thisincludes:
            -automaticallyswitch`qty_done`to1.0
            -warnifhehasalreadyencoded`lot_name`inanothermoveline
        """
        res={}
        ifself.product_id.tracking=='serial':
            ifnotself.qty_done:
                self.qty_done=1

            message=None
            ifself.lot_nameorself.lot_id:
                move_lines_to_check=self._get_similar_move_lines()-self
                ifself.lot_name:
                    counter=Counter([line.lot_nameforlineinmove_lines_to_check])
                    ifcounter.get(self.lot_name)andcounter[self.lot_name]>1:
                        message=_('Youcannotusethesameserialnumbertwice.Pleasecorrecttheserialnumbersencoded.')
                    elifnotself.lot_id:
                        counter=self.env['stock.production.lot'].search_count([
                            ('company_id','=',self.company_id.id),
                            ('product_id','=',self.product_id.id),
                            ('name','=',self.lot_name),
                        ])
                        ifcounter>0:
                            message=_('ExistingSerialnumber(%s).Pleasecorrecttheserialnumberencoded.')%self.lot_name
                elifself.lot_id:
                    counter=Counter([line.lot_id.idforlineinmove_lines_to_check])
                    ifcounter.get(self.lot_id.id)andcounter[self.lot_id.id]>1:
                        message=_('Youcannotusethesameserialnumbertwice.Pleasecorrecttheserialnumbersencoded.')
            ifmessage:
                res['warning']={'title':_('Warning'),'message':message}
        returnres

    @api.onchange('qty_done','product_uom_id')
    def_onchange_qty_done(self):
        """Whentheuserisencodingamovelineforatrackedproduct,weapplysomelogicto
        helphim.Thisonchangewillwarnhimifheset`qty_done`toanon-supportedvalue.
        """
        res={}
        ifself.qty_doneandself.product_id.tracking=='serial':
            qty_done=self.product_uom_id._compute_quantity(self.qty_done,self.product_id.uom_id)
            iffloat_compare(qty_done,1.0,precision_rounding=self.product_id.uom_id.rounding)!=0:
                message=_('Youcanonlyprocess1.0%sofproductswithuniqueserialnumber.',self.product_id.uom_id.name)
                res['warning']={'title':_('Warning'),'message':message}
        returnres

    definit(self):
        ifnottools.index_exists(self._cr,'stock_move_line_free_reservation_index'):
            self._cr.execute("""
                CREATEINDEXstock_move_line_free_reservation_index
                ON
                    stock_move_line(id,company_id,product_id,lot_id,location_id,owner_id,package_id)
                WHERE
                    (stateISNULLORstateNOTIN('cancel','done'))ANDproduct_qty>0""")

    @api.model_create_multi
    defcreate(self,vals_list):
        forvalsinvals_list:
            ifvals.get('move_id'):
                vals['company_id']=self.env['stock.move'].browse(vals['move_id']).company_id.id
            elifvals.get('picking_id'):
                vals['company_id']=self.env['stock.picking'].browse(vals['picking_id']).company_id.id

        mls=super().create(vals_list)

        defcreate_move(move_line):
            new_move=self.env['stock.move'].create(move_line._prepare_stock_move_vals())
            move_line.move_id=new_move.id

        #Ifthemovelineisdirectlycreateonthepickingview.
        #Ifthispickingisalreadydoneweshouldgeneratean
        #associateddonemove.
        formove_lineinmls:
            ifself.env.context.get('import_file')andmove_line.product_uom_qtyandnotmove_line._should_bypass_reservation(move_line.location_id):
                raiseUserError(_("Itisnotallowedtoimportreservedquantity,youhavetousethequantitydirectly."))
            ifmove_line.move_idornotmove_line.picking_id:
                continue
            ifmove_line.picking_id.state!='done':
                moves=move_line.picking_id.move_lines.filtered(lambdax:x.product_id==move_line.product_id)
                moves=sorted(moves,key=lambdam:m.quantity_done<m.product_qty,reverse=True)
                ifmoves:
                    move_line.move_id=moves[0].id
                else:
                    create_move(move_line)
            else:
                create_move(move_line)

        moves_to_update=mls.filtered(
            lambdaml:
            ml.move_idand
            ml.qty_doneand(
                ml.move_id.state=='done'or(
                    ml.move_id.picking_idand
                    ml.move_id.picking_id.immediate_transfer
                ))
        ).move_id
        formoveinmoves_to_update:
            move.product_uom_qty=move.quantity_done

        forml,valsinzip(mls,vals_list):
            ifml.state=='done':
                ifml.product_id.type=='product':
                    Quant=self.env['stock.quant']
                    quantity=ml.product_uom_id._compute_quantity(ml.qty_done,ml.move_id.product_id.uom_id,rounding_method='HALF-UP')
                    in_date=None
                    available_qty,in_date=Quant._update_available_quantity(ml.product_id,ml.location_id,-quantity,lot_id=ml.lot_id,package_id=ml.package_id,owner_id=ml.owner_id)
                    ifavailable_qty<0andml.lot_id:
                        #seeifwecancompensatethenegativequantswithsomeuntrackedquants
                        untracked_qty=Quant._get_available_quantity(ml.product_id,ml.location_id,lot_id=False,package_id=ml.package_id,owner_id=ml.owner_id,strict=True)
                        ifuntracked_qty:
                            taken_from_untracked_qty=min(untracked_qty,abs(quantity))
                            Quant._update_available_quantity(ml.product_id,ml.location_id,-taken_from_untracked_qty,lot_id=False,package_id=ml.package_id,owner_id=ml.owner_id)
                            Quant._update_available_quantity(ml.product_id,ml.location_id,taken_from_untracked_qty,lot_id=ml.lot_id,package_id=ml.package_id,owner_id=ml.owner_id)
                    Quant._update_available_quantity(ml.product_id,ml.location_dest_id,quantity,lot_id=ml.lot_id,package_id=ml.result_package_id,owner_id=ml.owner_id,in_date=in_date)
                next_moves=ml.move_id.move_dest_ids.filtered(lambdamove:move.statenotin('done','cancel'))
                next_moves._do_unreserve()
                next_moves._action_assign()
        returnmls

    defwrite(self,vals):
        ifself.env.context.get('bypass_reservation_update'):
            returnsuper(StockMoveLine,self).write(vals)

        if'product_id'invalsandany(vals.get('state',ml.state)!='draft'andvals['product_id']!=ml.product_id.idformlinself):
            raiseUserError(_("Changingtheproductisonlyallowedin'Draft'state."))

        moves_to_recompute_state=self.env['stock.move']
        Quant=self.env['stock.quant']
        precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
        triggers=[
            ('location_id','stock.location'),
            ('location_dest_id','stock.location'),
            ('lot_id','stock.production.lot'),
            ('package_id','stock.quant.package'),
            ('result_package_id','stock.quant.package'),
            ('owner_id','res.partner'),
            ('product_uom_id','uom.uom')
        ]
        updates={}
        forkey,modelintriggers:
            ifkeyinvals:
                updates[key]=self.env[model].browse(vals[key])

        if'result_package_id'inupdates:
            formlinself.filtered(lambdaml:ml.package_level_id):
                ifupdates.get('result_package_id'):
                    ml.package_level_id.package_id=updates.get('result_package_id')
                else:
                    #TODO:makepackagelevelslessofapainandfixthis
                    package_level=ml.package_level_id
                    ml.package_level_id=False
                    #Onlyneedtounlinkthepackagelevelifit'sempty.Otherwisewillunlinkittostillvalidmovelines.
                    ifnotpackage_level.move_line_ids:
                        package_level.unlink()

        #Whenwetrytowriteonareservedmovelineanyfieldsfrom`triggers`ordirectly
        #`product_uom_qty`(theactualreservedquantity),weneedtomakesuretheassociated
        #quantsarecorrectlyupdatedinordertonotmakethemoutofsync(i.e.thesumofthe
        #movelines`product_uom_qty`shouldalwaysbeequaltothesumof`reserved_quantity`on
        #thequants).Ifthenewcharateristicsarenotavailableonthequants,wechoseto
        #reservethemaximumpossible.
        ifupdatesor'product_uom_qty'invals:
            formlinself.filtered(lambdaml:ml.statein['partially_available','assigned']andml.product_id.type=='product'):

                if'product_uom_qty'invals:
                    new_product_uom_qty=ml.product_uom_id._compute_quantity(
                        vals['product_uom_qty'],ml.product_id.uom_id,rounding_method='HALF-UP')
                    #Makesure`product_uom_qty`isnotnegative.
                    iffloat_compare(new_product_uom_qty,0,precision_rounding=ml.product_id.uom_id.rounding)<0:
                        raiseUserError(_('Reservinganegativequantityisnotallowed.'))
                else:
                    new_product_uom_qty=ml.product_qty

                #Unreservetheoldcharateristicsofthemoveline.
                ifnotml._should_bypass_reservation(ml.location_id):
                    Quant._update_reserved_quantity(ml.product_id,ml.location_id,-ml.product_qty,lot_id=ml.lot_id,package_id=ml.package_id,owner_id=ml.owner_id,strict=True)

                #Reservethemaximumavailableofthenewcharateristicsofthemoveline.
                ifnotml._should_bypass_reservation(updates.get('location_id',ml.location_id)):
                    reserved_qty=0
                    try:
                        q=Quant._update_reserved_quantity(ml.product_id,updates.get('location_id',ml.location_id),new_product_uom_qty,lot_id=updates.get('lot_id',ml.lot_id),
                                                             package_id=updates.get('package_id',ml.package_id),owner_id=updates.get('owner_id',ml.owner_id),strict=True)
                        reserved_qty=sum([x[1]forxinq])
                    exceptUserError:
                        pass
                    ifreserved_qty!=new_product_uom_qty:
                        new_product_uom_qty=ml.product_id.uom_id._compute_quantity(reserved_qty,ml.product_uom_id,rounding_method='HALF-UP')
                        moves_to_recompute_state|=ml.move_id
                        ml.with_context(bypass_reservation_update=True).product_uom_qty=new_product_uom_qty
                        #wedon'twanttooverridethenewreservedquantity
                        vals.pop('product_uom_qty',None)

        #Wheneditingadonemoveline,thereservedavailabilityofapotentialchainedmoveisimpacted.Takecareofrunningagain`_action_assign`ontheconcernedmoves.
        ifupdatesor'qty_done'invals:
            next_moves=self.env['stock.move']
            mls=self.filtered(lambdaml:ml.move_id.state=='done'andml.product_id.type=='product')
            ifnotupdates: #wecanskipthosewhereqty_doneisalreadygooduptoUoMrounding
                mls=mls.filtered(lambdaml:notfloat_is_zero(ml.qty_done-vals['qty_done'],precision_rounding=ml.product_uom_id.rounding))
            formlinmls:
                #undotheoriginalmoveline
                qty_done_orig=ml.product_uom_id._compute_quantity(ml.qty_done,ml.move_id.product_id.uom_id,rounding_method='HALF-UP')
                in_date=Quant._update_available_quantity(ml.product_id,ml.location_dest_id,-qty_done_orig,lot_id=ml.lot_id,
                                                      package_id=ml.result_package_id,owner_id=ml.owner_id)[1]
                Quant._update_available_quantity(ml.product_id,ml.location_id,qty_done_orig,lot_id=ml.lot_id,
                                                      package_id=ml.package_id,owner_id=ml.owner_id,in_date=in_date)

                #movewhat'sbeenactuallydone
                product_id=ml.product_id
                location_id=updates.get('location_id',ml.location_id)
                location_dest_id=updates.get('location_dest_id',ml.location_dest_id)
                qty_done=vals.get('qty_done',ml.qty_done)
                lot_id=updates.get('lot_id',ml.lot_id)
                package_id=updates.get('package_id',ml.package_id)
                result_package_id=updates.get('result_package_id',ml.result_package_id)
                owner_id=updates.get('owner_id',ml.owner_id)
                product_uom_id=updates.get('product_uom_id',ml.product_uom_id)
                quantity=product_uom_id._compute_quantity(qty_done,ml.move_id.product_id.uom_id,rounding_method='HALF-UP')
                ifnotml._should_bypass_reservation(location_id):
                    ml._free_reservation(product_id,location_id,quantity,lot_id=lot_id,package_id=package_id,owner_id=owner_id)
                ifnotfloat_is_zero(quantity,precision_digits=precision):
                    available_qty,in_date=Quant._update_available_quantity(product_id,location_id,-quantity,lot_id=lot_id,package_id=package_id,owner_id=owner_id)
                    ifavailable_qty<0andlot_id:
                        #seeifwecancompensatethenegativequantswithsomeuntrackedquants
                        untracked_qty=Quant._get_available_quantity(product_id,location_id,lot_id=False,package_id=package_id,owner_id=owner_id,strict=True)
                        ifuntracked_qty:
                            taken_from_untracked_qty=min(untracked_qty,abs(available_qty))
                            Quant._update_available_quantity(product_id,location_id,-taken_from_untracked_qty,lot_id=False,package_id=package_id,owner_id=owner_id)
                            Quant._update_available_quantity(product_id,location_id,taken_from_untracked_qty,lot_id=lot_id,package_id=package_id,owner_id=owner_id)
                            ifnotml._should_bypass_reservation(location_id):
                                ml._free_reservation(ml.product_id,location_id,untracked_qty,lot_id=False,package_id=package_id,owner_id=owner_id)
                    Quant._update_available_quantity(product_id,location_dest_id,quantity,lot_id=lot_id,package_id=result_package_id,owner_id=owner_id,in_date=in_date)

                #Unreserveandreservefollowingmoveinordertohavetherealreservedquantityonmove_line.
                next_moves|=ml.move_id.move_dest_ids.filtered(lambdamove:move.statenotin('done','cancel'))

                #Loganote
                ifml.picking_id:
                    ml._log_message(ml.picking_id,ml,'stock.track_move_template',vals)

        res=super(StockMoveLine,self).write(vals)

        #Updatescrapobjectlinkedtomove_linestothenewquantity.
        if'qty_done'invals:
            formoveinself.mapped('move_id'):
                ifmove.scrapped:
                    move.scrap_ids.write({'scrap_qty':move.quantity_done})

        #Asstock_accountvaluesaccordingtoamove's`product_uom_qty`,weconsiderthatany
        #donestockmoveshouldhaveits`quantity_done`equalstoits`product_uom_qty`,and
        #thisiswhatmove's`action_done`willdo.So,wereplicatethebehaviorhere.
        ifupdatesor'qty_done'invals:
            moves=self.filtered(lambdaml:ml.move_id.state=='done').mapped('move_id')
            moves|=self.filtered(lambdaml:ml.move_id.statenotin('done','cancel')andml.move_id.picking_id.immediate_transferandnotml.product_uom_qty).mapped('move_id')
            formoveinmoves:
                move.product_uom_qty=move.quantity_done
            next_moves._do_unreserve()
            next_moves._action_assign()

        ifmoves_to_recompute_state:
            moves_to_recompute_state._recompute_state()

        returnres

    defunlink(self):
        precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
        formlinself:
            ifml.statein('done','cancel'):
                raiseUserError(_('Youcannotdeleteproductmovesifthepickingisdone.Youcanonlycorrectthedonequantities.'))
            #Unlinkingamovelineshouldunreserve.
            ifml.product_id.type=='product'andnotml._should_bypass_reservation(ml.location_id)andnotfloat_is_zero(ml.product_qty,precision_digits=precision):
                self.env['stock.quant']._update_reserved_quantity(ml.product_id,ml.location_id,-ml.product_qty,lot_id=ml.lot_id,package_id=ml.package_id,owner_id=ml.owner_id,strict=True)
        moves=self.mapped('move_id')
        res=super(StockMoveLine,self).unlink()
        ifmoves:
            #Addwith_prefetch()tosetthe_prefecht_ids=_ids
            #because_prefecht_idsgeneratorlooklazilyonthecacheofmove_id
            #whichisclearbytheunlinkofmoveline
            moves.with_prefetch()._recompute_state()
        returnres

    def_action_done(self):
        """Thismethodiscalledduringamove's`action_done`.It'llactuallymoveaquantfrom
        thesourcelocationtothedestinationlocation,andunreserveifneededinthesource
        location.

        Thismethodisintendedtobecalledonallthemovelinesofamove.Thismethodisnot
        intendedtobecalledwheneditinga`done`move(that'swhattheoverrideof`write`here
        isdone.
        """
        Quant=self.env['stock.quant']

        #First,weloopoverallthemovelinestodoapreliminarycheck:`qty_done`shouldnot
        #benegativeand,accordingtothepresenceofapickingtypeoralinkedinventory
        #adjustment,enforcesomerulesonthe`lot_id`field.If`qty_done`isnull,weunlink
        #theline.Itismandatoryinordertofreethereservationandcorrectlyapply
        #`action_done`onthenextmovelines.
        ml_ids_tracked_without_lot=OrderedSet()
        ml_ids_to_delete=OrderedSet()
        ml_ids_to_create_lot=OrderedSet()
        formlinself:
            #Checkhereif`ml.qty_done`respectstheroundingof`ml.product_uom_id`.
            uom_qty=float_round(ml.qty_done,precision_rounding=ml.product_uom_id.rounding,rounding_method='HALF-UP')
            precision_digits=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')
            qty_done=float_round(ml.qty_done,precision_digits=precision_digits,rounding_method='HALF-UP')
            iffloat_compare(uom_qty,qty_done,precision_digits=precision_digits)!=0:
                raiseUserError(_('Thequantitydonefortheproduct"%s"doesn\'trespecttheroundingprecision'
                                  'definedontheunitofmeasure"%s".Pleasechangethequantitydoneorthe'
                                  'roundingprecisionofyourunitofmeasure.')%(ml.product_id.display_name,ml.product_uom_id.name))

            qty_done_float_compared=float_compare(ml.qty_done,0,precision_rounding=ml.product_uom_id.rounding)
            ifqty_done_float_compared>0:
                ifml.product_id.tracking!='none':
                    picking_type_id=ml.move_id.picking_type_id
                    ifpicking_type_id:
                        ifpicking_type_id.use_create_lots:
                            #Ifapickingtypeislinked,wemayhavetocreateaproductionloton
                            #theflybeforeassigningittothemovelineiftheusercheckedboth
                            #`use_create_lots`and`use_existing_lots`.
                            ifml.lot_nameandnotml.lot_id:
                                lot=self.env['stock.production.lot'].search([
                                    ('company_id','=',ml.company_id.id),
                                    ('product_id','=',ml.product_id.id),
                                    ('name','=',ml.lot_name),
                                ],limit=1)
                                iflot:
                                    ml.lot_id=lot.id
                                else:
                                    ml_ids_to_create_lot.add(ml.id)
                        elifnotpicking_type_id.use_create_lotsandnotpicking_type_id.use_existing_lots:
                            #Iftheuserdisabledboth`use_create_lots`and`use_existing_lots`
                            #checkboxesonthepickingtype,he'sallowedtoentertracked
                            #productswithouta`lot_id`.
                            continue
                    elifml.move_id.inventory_id:
                        #Ifaninventoryadjustmentislinked,theuserisallowedtoenter
                        #trackedproductswithouta`lot_id`.
                        continue

                    ifnotml.lot_idandml.idnotinml_ids_to_create_lot:
                        ml_ids_tracked_without_lot.add(ml.id)
            elifqty_done_float_compared<0:
                raiseUserError(_('Nonegativequantitiesallowed'))
            else:
                ml_ids_to_delete.add(ml.id)

        ifml_ids_tracked_without_lot:
            mls_tracked_without_lot=self.env['stock.move.line'].browse(ml_ids_tracked_without_lot)
            raiseUserError(_('YouneedtosupplyaLot/SerialNumberforproduct:\n-')+
                              '\n-'.join(mls_tracked_without_lot.mapped('product_id.display_name')))
        ml_to_create_lot=self.env['stock.move.line'].browse(ml_ids_to_create_lot)
        ml_to_create_lot._create_and_assign_production_lot()

        mls_to_delete=self.env['stock.move.line'].browse(ml_ids_to_delete)
        mls_to_delete.unlink()

        mls_todo=(self-mls_to_delete)
        mls_todo._check_company()

        #Now,wecanactuallymovethequant.
        ml_ids_to_ignore=OrderedSet()
        formlinmls_todo:
            ifml.product_id.type=='product':
                rounding=ml.product_uom_id.rounding

                #ifthismovelineisforceassigned,unreserveelsewhereifneeded
                ifnotml._should_bypass_reservation(ml.location_id)andfloat_compare(ml.qty_done,ml.product_uom_qty,precision_rounding=rounding)>0:
                    qty_done_product_uom=ml.product_uom_id._compute_quantity(ml.qty_done,ml.product_id.uom_id,rounding_method='HALF-UP')
                    extra_qty=qty_done_product_uom-ml.product_qty
                    ml_to_ignore=self.env['stock.move.line'].browse(ml_ids_to_ignore)
                    ml._free_reservation(ml.product_id,ml.location_id,extra_qty,lot_id=ml.lot_id,package_id=ml.package_id,owner_id=ml.owner_id,ml_to_ignore=ml_to_ignore)
                #unreservewhat'sbeenreserved
                ifnotml._should_bypass_reservation(ml.location_id)andml.product_id.type=='product'andml.product_qty:
                    Quant._update_reserved_quantity(ml.product_id,ml.location_id,-ml.product_qty,lot_id=ml.lot_id,package_id=ml.package_id,owner_id=ml.owner_id,strict=True)

                #movewhat'sbeenactuallydone
                quantity=ml.product_uom_id._compute_quantity(ml.qty_done,ml.move_id.product_id.uom_id,rounding_method='HALF-UP')
                available_qty,in_date=Quant._update_available_quantity(ml.product_id,ml.location_id,-quantity,lot_id=ml.lot_id,package_id=ml.package_id,owner_id=ml.owner_id)
                ifavailable_qty<0andml.lot_id:
                    #seeifwecancompensatethenegativequantswithsomeuntrackedquants
                    untracked_qty=Quant._get_available_quantity(ml.product_id,ml.location_id,lot_id=False,package_id=ml.package_id,owner_id=ml.owner_id,strict=True)
                    ifuntracked_qty:
                        taken_from_untracked_qty=min(untracked_qty,abs(quantity))
                        Quant._update_available_quantity(ml.product_id,ml.location_id,-taken_from_untracked_qty,lot_id=False,package_id=ml.package_id,owner_id=ml.owner_id)
                        Quant._update_available_quantity(ml.product_id,ml.location_id,taken_from_untracked_qty,lot_id=ml.lot_id,package_id=ml.package_id,owner_id=ml.owner_id)
                Quant._update_available_quantity(ml.product_id,ml.location_dest_id,quantity,lot_id=ml.lot_id,package_id=ml.result_package_id,owner_id=ml.owner_id,in_date=in_date)
            ml_ids_to_ignore.add(ml.id)
        #Resetthereservedquantityaswejustmovedittothedestinationlocation.
        mls_todo.with_context(bypass_reservation_update=True).write({
            'product_uom_qty':0.00,
            'date':fields.Datetime.now(),
        })

    def_get_similar_move_lines(self):
        self.ensure_one()
        lines=self.env['stock.move.line']
        picking_id=self.move_id.picking_idifself.move_idelseself.picking_id
        ifpicking_id:
            lines|=picking_id.move_line_ids.filtered(lambdaml:ml.product_id==self.product_idand(ml.lot_idorml.lot_name))
        returnlines

    def_get_value_production_lot(self):
        self.ensure_one()
        return{
            'company_id':self.company_id.id,
            'name':self.lot_name,
            'product_id':self.product_id.id
        }

    def_create_and_assign_production_lot(self):
        """Createsandassignnewproductionlotsformovelines."""
        lot_vals=[]
        #Itispossibletohavemultipletimethesamelottocreate&assign,
        #sowehandlethecasewith2dictionaries.
        key_to_index={} #keytoindexofthelot
        key_to_mls=defaultdict(lambda:self.env['stock.move.line']) #keytoallmls
        formlinself:
            key=(ml.company_id.id,ml.product_id.id,ml.lot_name)
            key_to_mls[key]|=ml
            ifml.tracking!='lot'orkeynotinkey_to_index:
                key_to_index[key]=len(lot_vals)
                lot_vals.append(ml._get_value_production_lot())

        lots=self.env['stock.production.lot'].create(lot_vals)
        forkey,mlsinkey_to_mls.items():
            mls._assign_production_lot(lots[key_to_index[key]].with_prefetch(lots._ids)) #Withprefetchtoreconstructtheonesbrokebyaccessingbyindex

    def_assign_production_lot(self,lot):
        self.write({'lot_id':lot.id})

    def_reservation_is_updatable(self,quantity,reserved_quant):
        self.ensure_one()
        if(self.product_id.tracking!='serial'and
                self.location_id.id==reserved_quant.location_id.idand
                self.lot_id.id==reserved_quant.lot_id.idand
                self.package_id.id==reserved_quant.package_id.idand
                self.owner_id.id==reserved_quant.owner_id.id):
            returnTrue
        returnFalse

    def_log_message(self,record,move,template,vals):
        data=vals.copy()
        if'lot_id'invalsandvals['lot_id']!=move.lot_id.id:
            data['lot_name']=self.env['stock.production.lot'].browse(vals.get('lot_id')).name
        if'location_id'invals:
            data['location_name']=self.env['stock.location'].browse(vals.get('location_id')).name
        if'location_dest_id'invals:
            data['location_dest_name']=self.env['stock.location'].browse(vals.get('location_dest_id')).name
        if'package_id'invalsandvals['package_id']!=move.package_id.id:
            data['package_name']=self.env['stock.quant.package'].browse(vals.get('package_id')).name
        if'package_result_id'invalsandvals['package_result_id']!=move.package_result_id.id:
            data['result_package_name']=self.env['stock.quant.package'].browse(vals.get('result_package_id')).name
        if'owner_id'invalsandvals['owner_id']!=move.owner_id.id:
            data['owner_name']=self.env['res.partner'].browse(vals.get('owner_id')).name
        record.message_post_with_view(template,values={'move':move,'vals':dict(vals,**data)},subtype_id=self.env.ref('mail.mt_note').id)

    def_free_reservation(self,product_id,location_id,quantity,lot_id=None,package_id=None,owner_id=None,ml_to_ignore=None):
        """Wheneditingadonemovelineorvalidatingonewithsomeforcedquantities,itis
        possibletoimpactquantsthatwerenotreserved.Itisthereforenecessarytoeditor
        unlinkthemovelinesthatreservedaquantitynowunavailable.

        :paramml_to_ignore:recordsetof`stock.move.line`thatshouldNOTbeunreserved
        """
        self.ensure_one()

        ifml_to_ignoreisNone:
            ml_to_ignore=self.env['stock.move.line']
        ml_to_ignore|=self

        #Checktheavailablequantity,withthe`strict`kwsetto`True`.Iftheavailable
        #quantityisgreatherthanthequantitynowunavailable,thereisnothingtodo.
        available_quantity=self.env['stock.quant']._get_available_quantity(
            product_id,location_id,lot_id=lot_id,package_id=package_id,owner_id=owner_id,strict=True
        )
        ifquantity>available_quantity:
            quantity=quantity-available_quantity
            #Wenowhavetofindthemovelinesthatreservedournowunavailablequantity.We
            #takecaretoexcludeourselvesandthemovelineswereworkhadalreadybeendone.
            outdated_move_lines_domain=[
                ('state','notin',['done','cancel']),
                ('product_id','=',product_id.id),
                ('lot_id','=',lot_id.idiflot_idelseFalse),
                ('location_id','=',location_id.id),
                ('owner_id','=',owner_id.idifowner_idelseFalse),
                ('package_id','=',package_id.idifpackage_idelseFalse),
                ('product_qty','>',0.0),
                ('id','notin',ml_to_ignore.ids),
            ]
            #Wetakethecurrentpickingfirst,thenthepickingswiththelatestscheduleddate
            current_picking_first=lambdacand:(
                cand.picking_id!=self.move_id.picking_id,
                -(cand.picking_id.scheduled_dateorcand.move_id.date).timestamp()
                ifcand.picking_idorcand.move_id
                else-cand.id,
            )
            outdated_candidates=self.env['stock.move.line'].search(outdated_move_lines_domain).sorted(current_picking_first)

            #Asthemove'sstateisnotcomputedoverthemovelines,we'llhavetomanually
            #recomputethemoveswhichweadaptedtheirlines.
            move_to_recompute_state=self.env['stock.move']
            to_unlink_candidate_ids=set()

            rounding=self.product_uom_id.rounding
            forcandidateinoutdated_candidates:
                iffloat_compare(candidate.product_qty,quantity,precision_rounding=rounding)<=0:
                    quantity-=candidate.product_qty
                    ifcandidate.qty_done:
                        move_to_recompute_state|=candidate.move_id
                        candidate.product_uom_qty=0.0
                    else:
                        to_unlink_candidate_ids.add(candidate.id)
                    iffloat_is_zero(quantity,precision_rounding=rounding):
                        break
                else:
                    #splitthismovelineandassignthenewparttoourextramove
                    quantity_split=float_round(
                        candidate.product_qty-quantity,
                        precision_rounding=self.product_uom_id.rounding,
                        rounding_method='UP')
                    candidate.product_uom_qty=self.product_id.uom_id._compute_quantity(quantity_split,candidate.product_uom_id,rounding_method='HALF-UP')
                    move_to_recompute_state|=candidate.move_id
                    break
            self.env['stock.move.line'].browse(to_unlink_candidate_ids).unlink()
            move_to_recompute_state._recompute_state()

    def_should_bypass_reservation(self,location):
        self.ensure_one()
        returnlocation.should_bypass_reservation()orself.product_id.type!='product'

    def_get_aggregated_product_quantities(self,**kwargs):
        """Returnsadictionaryofproducts(key=id+name+description+uom)andcorrespondingvaluesofinterest.

        Allowsaggregationofdataacrossseparatemovelinesforthesameproduct.Thisisexpectedtobeuseful
        inthingssuchasdeliveryreports.Dictkeyismadeasacombinationofvaluesweexpecttowanttogroup
        theproductsby(i.e.sodataisnotlost).Thisfunctionpurposelyignoreslots/SNsbecausetheseare
        expectedtoalreadybeproperlygroupedbyline.

        returns:dictionary{product_id+name+description+uom:{product,name,description,qty_done,product_uom},...}
        """
        aggregated_move_lines={}
        formove_lineinself:
            name=move_line.product_id.display_name
            description=move_line.move_id.description_picking
            ifdescription==nameordescription==move_line.product_id.name:
                description=False
            uom=move_line.product_uom_id
            line_key=str(move_line.product_id.id)+"_"+name+(descriptionor"")+"uom"+str(uom.id)

            ifline_keynotinaggregated_move_lines:
                aggregated_move_lines[line_key]={'name':name,
                                                   'description':description,
                                                   'qty_done':move_line.qty_done,
                                                   'product_uom':uom.name,
                                                   'product_uom_rec':uom,
                                                   'product':move_line.product_id}
            else:
                aggregated_move_lines[line_key]['qty_done']+=move_line.qty_done
        returnaggregated_move_lines

    def_compute_sale_price(self):
        #ToOverride
        pass

    @api.model
    def_prepare_stock_move_vals(self):
        self.ensure_one()
        return{
            'name':_('NewMove:')+self.product_id.display_name,
            'product_id':self.product_id.id,
            'product_uom_qty':0ifself.picking_idandself.picking_id.state!='done'elseself.qty_done,
            'product_uom':self.product_uom_id.id,
            'description_picking':self.description_picking,
            'location_id':self.picking_id.location_id.id,
            'location_dest_id':self.picking_id.location_dest_id.id,
            'picking_id':self.picking_id.id,
            'state':self.picking_id.state,
            'picking_type_id':self.picking_id.picking_type_id.id,
            'restrict_partner_id':self.picking_id.owner_id.id,
            'company_id':self.picking_id.company_id.id,
        }
