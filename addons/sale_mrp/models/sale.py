#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.toolsimportfloat_compare


classSaleOrder(models.Model):
    _inherit='sale.order'

    mrp_production_count=fields.Integer(
        "CountofMOgenerated",
        compute='_compute_mrp_production_count',
        groups='mrp.group_mrp_user')

    @api.depends('procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids')
    def_compute_mrp_production_count(self):
        data=self.env['procurement.group'].read_group([('sale_id','in',self.ids)],['ids:array_agg(id)'],['sale_id'])
        mrp_count=dict()
        foritemindata:
            procurement_groups=self.env['procurement.group'].browse(item['ids'])
            mrp_count[item['sale_id'][0]]=len(
                set(procurement_groups.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids)|
                set(procurement_groups.mrp_production_ids.ids))
        forsaleinself:
            sale.mrp_production_count=mrp_count.get(sale.id)

    defaction_view_mrp_production(self):
        self.ensure_one()
        procurement_groups=self.env['procurement.group'].search([('sale_id','in',self.ids)])
        mrp_production_ids=set(procurement_groups.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids)|\
            set(procurement_groups.mrp_production_ids.ids)
        action={
            'res_model':'mrp.production',
            'type':'ir.actions.act_window',
        }
        iflen(mrp_production_ids)==1:
            action.update({
                'view_mode':'form',
                'res_id':mrp_production_ids.pop(),
            })
        else:
            action.update({
                'name':_("ManufacturingOrdersGeneratedby%s",self.name),
                'domain':[('id','in',list(mrp_production_ids))],
                'view_mode':'tree,form',
            })
        returnaction


classSaleOrderLine(models.Model):
    _inherit='sale.order.line'

    @api.depends('product_uom_qty','qty_delivered','product_id','state')
    def_compute_qty_to_deliver(self):
        """Theinventorywidgetshouldnowbevisibleinmorecasesiftheproductisconsumable."""
        super(SaleOrderLine,self)._compute_qty_to_deliver()
        forlineinself:
            #Hidethewidgetforkitssinceforecastdoesn'tsupportthem.
            boms=self.env['mrp.bom']
            ifline.state=='sale':
                boms=line.move_ids.mapped('bom_line_id.bom_id')
            elifline.statein['draft','sent']andline.product_id:
                boms=boms._bom_find(product=line.product_id,company_id=line.company_id.id,bom_type='phantom')
            relevant_bom=boms.filtered(lambdab:b.type=='phantom'and
                    (b.product_id==line.product_idor
                    (b.product_tmpl_id==line.product_id.product_tmpl_idandnotb.product_id)))
            ifrelevant_bom:
                line.display_qty_widget=False
                continue
            ifline.state=='draft'andline.product_type=='consu':
                components=line.product_id.get_components()
                ifcomponentsandcomponents!=[line.product_id.id]:
                    line.display_qty_widget=True

    def_compute_qty_delivered(self):
        super(SaleOrderLine,self)._compute_qty_delivered()
        fororder_lineinself:
            iforder_line.qty_delivered_method=='stock_move':
                boms=order_line.move_ids.filtered(lambdam:m.state!='cancel').mapped('bom_line_id.bom_id')
                dropship=any(m._is_dropshipped()forminorder_line.move_ids)
                ifnotbomsanddropship:
                    boms=boms._bom_find(product=order_line.product_id,company_id=order_line.company_id.id,bom_type='phantom')
                #WefetchtheBoMsoftypekitslinkedtotheorder_line,
                #thewekeeponlytheonerelatedtothefinishedprodust.
                #Thisbomshoudbetheonlyonesincebom_line_idwaswrittenonthemoves
                relevant_bom=boms.filtered(lambdab:b.type=='phantom'and
                        (b.product_id==order_line.product_idor
                        (b.product_tmpl_id==order_line.product_id.product_tmpl_idandnotb.product_id)))
                ifrelevant_bom:
                    #Incaseofdropship,weusea'allornothing'policysince'bom_line_id'was
                    #notwrittenonamovecomingfromaPO:allmoves(tocustomer)mustbedone
                    #andthereturnsmustbedeliveredbacktothecustomer
                    #FIXME:ifthecomponentsofakithavedifferentsuppliers,multiplePO
                    #aregenerated.IfonePOisconfirmedandalltheothersareindraft,receiving
                    #theproductsforthisPOwillsettheqty_delivered.Wemightneedtocheckthe
                    #stateofallPOaswell...butsale_mrpdoesn'tdependonpurchase.
                    ifdropship:
                        moves=order_line.move_ids.filtered(lambdam:m.state!='cancel')
                        ifany((m.location_dest_id.usage=='customer'andm.state!='done')
                               or(m.location_dest_id.usage!='customer'
                               andm.state=='done'
                               andfloat_compare(m.quantity_done,
                                                 sum(sub_m.product_uom._compute_quantity(sub_m.quantity_done,m.product_uom)forsub_minm.returned_move_idsifsub_m.state=='done'),
                                                 precision_rounding=m.product_uom.rounding)>0)
                               forminmoves)ornotmoves:
                            order_line.qty_delivered=0
                        else:
                            order_line.qty_delivered=order_line.product_uom_qty
                        continue
                    moves=order_line.move_ids.filtered(lambdam:m.state=='done'andnotm.scrapped)
                    filters={
                        'incoming_moves':lambdam:m.location_dest_id.usage=='customer'and(notm.origin_returned_move_idor(m.origin_returned_move_idandm.to_refund)),
                        'outgoing_moves':lambdam:m.location_dest_id.usage!='customer'andm.to_refund
                    }
                    order_qty=order_line.product_uom._compute_quantity(order_line.product_uom_qty,relevant_bom.product_uom_id)
                    qty_delivered=moves._compute_kit_quantities(order_line.product_id,order_qty,relevant_bom,filters)
                    order_line.qty_delivered=relevant_bom.product_uom_id._compute_quantity(qty_delivered,order_line.product_uom)

                #IfnorelevantBOMisfound,fallbackontheall-or-nothingpolicy.Thishappens
                #whentheproductsoldismadeonlyofkits.Inthiscase,theBOMofthestockmoves
                #donotcorrespondtotheproductsold=>norelevantBOM.
                elifboms:
                    #ifthemoveisingoing,theproduct**sold**hasdeliveredqty0
                    ifall(m.state=='done'andm.location_dest_id.usage=='customer'forminorder_line.move_ids):
                        order_line.qty_delivered=order_line.product_uom_qty
                    else:
                        order_line.qty_delivered=0.0

    def_get_bom_component_qty(self,bom):
        bom_quantity=self.product_id.uom_id._compute_quantity(1,bom.product_uom_id,rounding_method='HALF-UP')
        boms,lines=bom.explode(self.product_id,bom_quantity)
        components={}
        forline,line_datainlines:
            product=line.product_id.id
            uom=line.product_uom_id
            qty=line_data['qty']
            ifcomponents.get(product,False):
                ifuom.id!=components[product]['uom']:
                    from_uom=uom
                    to_uom=self.env['uom.uom'].browse(components[product]['uom'])
                    qty=from_uom._compute_quantity(qty,to_uom)
                components[product]['qty']+=qty
            else:
                #Tobeintheuomreferenceoftheproduct
                to_uom=self.env['product.product'].browse(product).uom_id
                ifuom.id!=to_uom.id:
                    from_uom=uom
                    qty=from_uom._compute_quantity(qty,to_uom)
                components[product]={'qty':qty,'uom':to_uom.id}
        returncomponents

    def_get_qty_procurement(self,previous_product_uom_qty=False):
        self.ensure_one()
        #SpecificcasewhenwechangetheqtyonaSOforakitproduct.
        #Wedon'ttrytobetoosmartandkeepasimpleapproach:weusethequantityofentire
        #kitsthatarecurrentlyindelivery
        bom=self.env['mrp.bom']._bom_find(product=self.product_id,bom_type='phantom')
        ifbom:
            moves=self.move_ids.filtered(lambdar:r.state!='cancel'andnotr.scrapped)
            filters={
                'incoming_moves':lambdam:m.location_dest_id.usage=='customer'and(notm.origin_returned_move_idor(m.origin_returned_move_idandm.to_refund)),
                'outgoing_moves':lambdam:m.location_dest_id.usage!='customer'andm.to_refund
            }
            order_qty=self.product_uom._compute_quantity(self.product_uom_qty,bom.product_uom_id)
            qty=moves._compute_kit_quantities(self.product_id,order_qty,bom,filters)
            returnbom.product_uom_id._compute_quantity(qty,self.product_uom)
        returnsuper(SaleOrderLine,self)._get_qty_procurement(previous_product_uom_qty=previous_product_uom_qty)
