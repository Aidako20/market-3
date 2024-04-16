#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
fromcollectionsimportdefaultdict

fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportUserError
fromflectra.tools.sqlimportcolumn_exists,create_column


classStockQuantPackage(models.Model):
    _inherit="stock.quant.package"

    @api.depends('quant_ids')
    def_compute_weight(self):
        ifself.env.context.get('picking_id'):
            package_weights=defaultdict(float)
            #Orderingbyqty_donepreventsthedefaultorderingbygroupbyfieldsthatcaninjectmultipleLeftJoinsintheresultingquery.
            res_groups=self.env['stock.move.line'].read_group(
                [('result_package_id','in',self.ids),('product_id','!=',False),('picking_id','=',self.env.context['picking_id'])],
                ['id:count'],
                ['result_package_id','product_id','product_uom_id','qty_done'],
                lazy=False,orderby='qty_doneasc'
            )
            forres_groupinres_groups:
                product_id=self.env['product.product'].browse(res_group['product_id'][0])
                product_uom_id=self.env['uom.uom'].browse(res_group['product_uom_id'][0])
                package_weights[res_group['result_package_id'][0]]+=(
                    res_group['__count']
                    *product_uom_id._compute_quantity(res_group['qty_done'],product_id.uom_id)
                    *product_id.weight
                )
        forpackageinself:
            ifself.env.context.get('picking_id'):
                package.weight=package_weights[package.id]
            else:
                weight=0.0
                forquantinpackage.quant_ids:
                    weight+=quant.quantity*quant.product_id.weight
                package.weight=weight

    def_get_default_weight_uom(self):
        returnself.env['product.template']._get_weight_uom_name_from_ir_config_parameter()

    def_compute_weight_uom_name(self):
        forpackageinself:
            package.weight_uom_name=self.env['product.template']._get_weight_uom_name_from_ir_config_parameter()

    weight=fields.Float(compute='_compute_weight',help="Totalweightofalltheproductscontainedinthepackage.")
    weight_uom_name=fields.Char(string='Weightunitofmeasurelabel',compute='_compute_weight_uom_name',readonly=True,default=_get_default_weight_uom)
    shipping_weight=fields.Float(string='ShippingWeight',help="Totalweightofthepackage.")


classStockPicking(models.Model):
    _inherit='stock.picking'

    def_auto_init(self):
        ifnotcolumn_exists(self.env.cr,"stock_picking","weight"):
            #Inordertospeedupmoduleinstallationwhendealingwithheftydata
            #Wecreatethecolumnweightmanually,butthecomputationwillbeskipped
            #Thereforewedothecomputationinaquerybygettingweightsumfromstockmoves
            create_column(self.env.cr,"stock_picking","weight","numeric")
            self.env.cr.execute("""
                WITHcomputed_weightAS(
                    SELECTSUM(weight)ASweight_sum,picking_id
                    FROMstock_move
                    WHEREpicking_idISNOTNULL
                    GROUPBYpicking_id
                )
                UPDATEstock_picking
                SETweight=weight_sum
                FROMcomputed_weight
                WHEREstock_picking.id=computed_weight.picking_id;
            """)
        returnsuper()._auto_init()

    @api.depends('move_line_ids','move_line_ids.result_package_id')
    def_compute_packages(self):
        packages={
            res["picking_id"][0]:set(res["result_package_id"])
            forresinself.env["stock.move.line"].read_group(
                [("picking_id","in",self.ids),("result_package_id","!=",False)],
                ["result_package_id:array_agg"],
                ["picking_id"],
                lazy=False,orderby="picking_idasc",
            )
        }
        forpickinginself:
            picking.package_ids=list(packages.get(picking.id,[]))

    @api.depends('move_line_ids','move_line_ids.result_package_id','move_line_ids.product_uom_id','move_line_ids.qty_done')
    def_compute_bulk_weight(self):
        picking_weights=defaultdict(float)
        #Orderingbyqty_donepreventsthedefaultorderingbygroupbyfieldsthatcaninjectmultipleLeftJoinsintheresultingquery.
        res_groups=self.env['stock.move.line'].read_group(
            [('picking_id','in',self.ids),('product_id','!=',False),('result_package_id','=',False)],
            ['id:count'],
            ['picking_id','product_id','product_uom_id','qty_done'],
            lazy=False,orderby='qty_doneasc'
        )
        products_by_id={
            product_res['id']:(product_res['uom_id'][0],product_res['weight'])
            forproduct_resin
            self.env['product.product'].with_context(active_test=False).search_read(
                [('id','in',list(set(grp["product_id"][0]forgrpinres_groups)))],['uom_id','weight'])
        }
        forres_groupinres_groups:
            uom_id,weight=products_by_id[res_group['product_id'][0]]
            uom=self.env['uom.uom'].browse(uom_id)
            product_uom_id=self.env['uom.uom'].browse(res_group['product_uom_id'][0])
            picking_weights[res_group['picking_id'][0]]+=(
                res_group['__count']
                *product_uom_id._compute_quantity(res_group['qty_done'],uom)
                *weight
            )
        forpickinginself:
            picking.weight_bulk=picking_weights[picking.id]

    @api.depends('move_line_ids.result_package_id','move_line_ids.result_package_id.shipping_weight','weight_bulk')
    def_compute_shipping_weight(self):
        forpickinginself:
            #ifshippingweightisnotassigned=>defaulttocalculatedproductweight
            picking.shipping_weight=picking.weight_bulk+sum([pack.shipping_weightorpack.weightforpackinpicking.package_ids])

    def_get_default_weight_uom(self):
        returnself.env['product.template']._get_weight_uom_name_from_ir_config_parameter()

    def_compute_weight_uom_name(self):
        forpackageinself:
            package.weight_uom_name=self.env['product.template']._get_weight_uom_name_from_ir_config_parameter()

    carrier_price=fields.Float(string="ShippingCost")
    delivery_type=fields.Selection(related='carrier_id.delivery_type',readonly=True)
    carrier_id=fields.Many2one("delivery.carrier",string="Carrier",check_company=True)
    weight=fields.Float(compute='_cal_weight',digits='StockWeight',store=True,help="Totalweightoftheproductsinthepicking.",compute_sudo=True)
    carrier_tracking_ref=fields.Char(string='TrackingReference',copy=False)
    carrier_tracking_url=fields.Char(string='TrackingURL',compute='_compute_carrier_tracking_url')
    weight_uom_name=fields.Char(string='Weightunitofmeasurelabel',compute='_compute_weight_uom_name',readonly=True,default=_get_default_weight_uom)
    package_ids=fields.Many2many('stock.quant.package',compute='_compute_packages',string='Packages')
    weight_bulk=fields.Float('BulkWeight',compute='_compute_bulk_weight',help="Totalweightofproductswhicharenotinapackage.")
    shipping_weight=fields.Float("WeightforShipping",compute='_compute_shipping_weight',
        help="Totalweightofpackagesandproductsnotinapackage.Packageswithnoshippingweightspecifiedwilldefaulttotheirproducts'totalweight.Thisistheweightusedtocomputethecostoftheshipping.")
    is_return_picking=fields.Boolean(compute='_compute_return_picking')
    return_label_ids=fields.One2many('ir.attachment',compute='_compute_return_label')

    @api.depends('carrier_id','carrier_tracking_ref')
    def_compute_carrier_tracking_url(self):
        forpickinginself:
            picking.carrier_tracking_url=picking.carrier_id.get_tracking_link(picking)ifpicking.carrier_idandpicking.carrier_tracking_refelseFalse

    @api.depends('carrier_id','move_ids_without_package')
    def_compute_return_picking(self):
        forpickinginself:
            ifpicking.carrier_idandpicking.carrier_id.can_generate_return:
                picking.is_return_picking=any(m.origin_returned_move_idforminpicking.move_ids_without_package)
            else:
                picking.is_return_picking=False

    def_compute_return_label(self):
        forpickinginself:
            ifpicking.carrier_id:
                picking.return_label_ids=self.env['ir.attachment'].search([('res_model','=','stock.picking'),('res_id','=',picking.id),('name','like','%s%%'%picking.carrier_id.get_return_label_prefix())])
            else:
                picking.return_label_ids=False

    defget_multiple_carrier_tracking(self):
        self.ensure_one()
        try:
            returnjson.loads(self.carrier_tracking_url)
        except(ValueError,TypeError):
            returnFalse

    @api.depends('move_lines')
    def_cal_weight(self):
        forpickinginself:
            picking.weight=sum(move.weightformoveinpicking.move_linesifmove.state!='cancel')

    def_send_confirmation_email(self):
        forpickinself:
            ifpick.carrier_id:
                ifpick.carrier_id.integration_level=='rate_and_ship'andpick.picking_type_code!='incoming':
                    pick.sudo().send_to_shipper()
            pick._check_carrier_details_compliance()
        returnsuper(StockPicking,self)._send_confirmation_email()

    def_pre_put_in_pack_hook(self,move_line_ids):
        res=super(StockPicking,self)._pre_put_in_pack_hook(move_line_ids)
        ifnotres:
            ifself.carrier_id:
                returnself._set_delivery_packaging()
        else:
            returnres

    def_set_delivery_packaging(self):
        """Thismethodreturnsanactionallowingtosettheproductpackagingandtheshippingweight
         onthestock.quant.package.
        """
        self.ensure_one()
        view_id=self.env.ref('delivery.choose_delivery_package_view_form').id
        context=dict(
            self.env.context,
            current_package_carrier_type=self.carrier_id.delivery_type,
            default_picking_id=self.id
        )
        #Aswepassthe`delivery_type`('fixed'or'base_on_rule'bydefault)inakeywho
        #correspondtothe`package_carrier_type`('none'todefault),wemakeaconversion.
        #Noneedconversionforothercarriersasthe`delivery_type`and
        #`package_carrier_type`willbethesameinthesecases.
        ifcontext['current_package_carrier_type']in['fixed','base_on_rule']:
            context['current_package_carrier_type']='none'
        return{
            'name':_('PackageDetails'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'choose.delivery.package',
            'view_id':view_id,
            'views':[(view_id,'form')],
            'target':'new',
            'context':context,
        }

    defsend_to_shipper(self):
        self.ensure_one()
        res=self.carrier_id.send_shipping(self)[0]
        ifself.carrier_id.free_overandself.sale_idandself.sale_id._compute_amount_total_without_delivery()>=self.carrier_id.amount:
            res['exact_price']=0.0
        self.carrier_price=res['exact_price']*(1.0+(self.carrier_id.margin/100.0))
        ifres['tracking_number']:
            self.carrier_tracking_ref=res['tracking_number']
        order_currency=self.sale_id.currency_idorself.company_id.currency_id
        msg=_(
            "Shipmentsenttocarrier%(carrier_name)sforshippingwithtrackingnumber%(ref)s<br/>Cost:%(price).2f%(currency)s",
            carrier_name=self.carrier_id.name,
            ref=self.carrier_tracking_ref,
            price=self.carrier_price,
            currency=order_currency.name
        )
        self.message_post(body=msg)
        self._add_delivery_cost_to_so()

    def_check_carrier_details_compliance(self):
        """Hooktocheckifadeliveryiscompliantinregardofthecarrier.
        """
        pass

    defprint_return_label(self):
        self.ensure_one()
        self.carrier_id.get_return_label(self)

    def_add_delivery_cost_to_so(self):
        self.ensure_one()
        sale_order=self.sale_id
        ifsale_orderandself.carrier_id.invoice_policy=='real'andself.carrier_price:
            delivery_lines=sale_order.order_line.filtered(lambdal:l.is_deliveryandl.currency_id.is_zero(l.price_unit)andl.product_id==self.carrier_id.product_id)
            ifnotdelivery_lines:
                delivery_lines=[sale_order._create_delivery_line(self.carrier_id,self.carrier_price)]
            delivery_line=delivery_lines[0]
            delivery_line[0].write({
                'price_unit':self.carrier_price,
                #removetheestimatedpricefromthedescription
                'name':self.carrier_id.with_context(lang=self.partner_id.lang).name,
            })

    defopen_website_url(self):
        self.ensure_one()
        ifnotself.carrier_tracking_url:
            raiseUserError(_("Yourdeliverymethodhasnoredirectoncourierprovider'swebsitetotrackthisorder."))

        carrier_trackers=[]
        try:
            carrier_trackers=json.loads(self.carrier_tracking_url)
        exceptValueError:
            carrier_trackers=self.carrier_tracking_url
        else:
            msg="Trackinglinksforshipment:<br/>"
            fortrackerincarrier_trackers:
                msg+='<ahref='+tracker[1]+'>'+tracker[0]+'</a><br/>'
            self.message_post(body=msg)
            returnself.env["ir.actions.actions"]._for_xml_id("delivery.act_delivery_trackers_url")

        client_action={
            'type':'ir.actions.act_url',
            'name':"ShipmentTrackingPage",
            'target':'new',
            'url':self.carrier_tracking_url,
        }
        returnclient_action

    defcancel_shipment(self):
        forpickinginself:
            picking.carrier_id.cancel_shipment(self)
            msg="Shipment%scancelled"%picking.carrier_tracking_ref
            picking.message_post(body=msg)
            picking.carrier_tracking_ref=False

    def_get_estimated_weight(self):
        self.ensure_one()
        weight=0.0
        formoveinself.move_lines:
            weight+=move.product_qty*move.product_id.weight
        returnweight

    def_should_generate_commercial_invoice(self):
        self.ensure_one()
        returnself.picking_type_id.warehouse_id.partner_id.country_id!=self.partner_id.country_id


classStockReturnPicking(models.TransientModel):
    _inherit='stock.return.picking'

    def_create_returns(self):
        #Preventcopyofthecarrierandcarrierpricewhengeneratingreturnpicking
        #(wehavenointegrationofreturnsfornow)
        new_picking,pick_type_id=super(StockReturnPicking,self)._create_returns()
        picking=self.env['stock.picking'].browse(new_picking)
        picking.write({'carrier_id':False,
                       'carrier_price':0.0})
        returnnew_picking,pick_type_id
