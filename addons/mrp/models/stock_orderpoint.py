#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.tools.float_utilsimportfloat_is_zero
fromflectra.osv.expressionimportAND

classStockWarehouseOrderpoint(models.Model):
    _inherit='stock.warehouse.orderpoint'

    show_bom=fields.Boolean('ShowBoMcolumn',compute='_compute_show_bom')
    bom_id=fields.Many2one(
        'mrp.bom',string='BillofMaterials',check_company=True,
        domain="[('type','=','normal'),'&','|',('company_id','=',company_id),('company_id','=',False),'|',('product_id','=',product_id),'&',('product_id','=',False),('product_tmpl_id','=',product_tmpl_id)]")

    def_get_replenishment_order_notification(self):
        self.ensure_one()
        domain=[('orderpoint_id','in',self.ids)]
        ifself.env.context.get('written_after'):
            domain=AND([domain,[('write_date','>',self.env.context.get('written_after'))]])
        production=self.env['mrp.production'].search(domain,limit=1)
        ifproduction:
            action=self.env.ref('mrp.action_mrp_production_form')
            return{
                'type':'ir.actions.client',
                'tag':'display_notification',
                'params':{
                    'title':_('Thefollowingreplenishmentorderhasbeengenerated'),
                    'message':'%s',
                    'links':[{
                        'label':production.name,
                        'url':f'#action={action.id}&id={production.id}&model=mrp.production'
                    }],
                    'sticky':False,
                }
            }
        returnsuper()._get_replenishment_order_notification()

    @api.depends('route_id')
    def_compute_show_bom(self):
        manufacture_route=[]
        forresinself.env['stock.rule'].search_read([('action','=','manufacture')],['route_id']):
            manufacture_route.append(res['route_id'][0])
        fororderpointinself:
            orderpoint.show_bom=orderpoint.route_id.idinmanufacture_route

    def_quantity_in_progress(self):
        bom_manufacture=self.env['mrp.bom']
        bom_kit_orderpoints={}
        fororderpointinself:
            bom=self.env['mrp.bom']._bom_find(product=orderpoint.product_id)
            ifbom.type=='phantom':
                bom_kit_orderpoints[orderpoint]=bom
            elifbom.type=='normal':
                bom_manufacture|=bom

        orderpoints_without_kit=self-self.env['stock.warehouse.orderpoint'].concat(*bom_kit_orderpoints.keys())
        res=super(StockWarehouseOrderpoint,orderpoints_without_kit)._quantity_in_progress()
        fororderpointinbom_kit_orderpoints:
            boms,bom_sub_lines=bom_kit_orderpoints[orderpoint].explode(orderpoint.product_id,1)
            ratios_qty_available=[]
            #total=qty_available+in_progress
            ratios_total=[]
            forbom_line,bom_line_datainbom_sub_lines:
                component=bom_line.product_id
                ifcomponent.type!='product'orfloat_is_zero(bom_line_data['qty'],precision_rounding=bom_line.product_uom_id.rounding):
                    continue
                uom_qty_per_kit=bom_line_data['qty']/bom_line_data['original_qty']
                qty_per_kit=bom_line.product_uom_id._compute_quantity(uom_qty_per_kit,bom_line.product_id.uom_id,raise_if_failure=False)
                ifnotqty_per_kit:
                    continue
                qty_by_product_location,dummy=component._get_quantity_in_progress(orderpoint.location_id.ids)
                qty_in_progress=qty_by_product_location.get((component.id,orderpoint.location_id.id),0.0)
                qty_available=component.qty_available/qty_per_kit
                ratios_qty_available.append(qty_available)
                ratios_total.append(qty_available+(qty_in_progress/qty_per_kit))
            #Forakit,thequantityinprogressis:
            # (thequantityifwehavereceivedallin-progresscomponents)-(thequantityusingonlyavailablecomponents)
            product_qty=min(ratios_totalor[0])-min(ratios_qty_availableor[0])
            res[orderpoint.id]=orderpoint.product_id.uom_id._compute_quantity(product_qty,orderpoint.product_uom,round=False)

        productions_group=self.env['mrp.production'].read_group(
            [('bom_id','in',bom_manufacture.ids),('state','=','draft'),('orderpoint_id','in',orderpoints_without_kit.ids)],
            ['orderpoint_id','product_qty','product_uom_id'],
            ['orderpoint_id','product_uom_id'],lazy=False)
        forpinproductions_group:
            uom=self.env['uom.uom'].browse(p['product_uom_id'][0])
            orderpoint=self.env['stock.warehouse.orderpoint'].browse(p['orderpoint_id'][0])
            res[orderpoint.id]+=uom._compute_quantity(
                p['product_qty'],orderpoint.product_uom,round=False)
        returnres

    def_set_default_route_id(self):
        route_id=self.env['stock.rule'].search([
            ('action','=','manufacture')
        ]).route_id
        orderpoint_wh_bom=self.filtered(lambdao:o.product_id.bom_ids)
        ifroute_idandorderpoint_wh_bom:
            orderpoint_wh_bom.route_id=route_id[0].id
        returnsuper()._set_default_route_id()

    def_prepare_procurement_values(self,date=False,group=False):
        values=super()._prepare_procurement_values(date=date,group=group)
        values['bom_id']=self.bom_id
        returnvalues

    def_post_process_scheduler(self):
        """Confirmtheproductionsonlyafteralltheorderpointshaveruntheir
        procurementtoavoidthenewprocurementcreatedfromtheproductionconflict
        withthem."""
        self.env['mrp.production'].sudo().search([
            ('orderpoint_id','in',self.ids),
            ('move_raw_ids','!=',False),
            ('state','=','draft'),
        ]).action_confirm()
        returnsuper()._post_process_scheduler()
