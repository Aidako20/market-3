#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.tools.float_utilsimportfloat_compare


classChooseDeliveryPackage(models.TransientModel):
    _name='choose.delivery.package'
    _description='DeliveryPackageSelectionWizard'

    @api.model
    defdefault_get(self,fields_list):
        defaults=super().default_get(fields_list)
        if'shipping_weight'infields_list:
            picking=self.env['stock.picking'].browse(defaults.get('picking_id'))
            move_line_ids=picking.move_line_ids.filtered(lambdam:
                float_compare(m.qty_done,0.0,precision_rounding=m.product_uom_id.rounding)>0
                andnotm.result_package_id
            )
            total_weight=0.0
            formlinmove_line_ids:
                qty=ml.product_uom_id._compute_quantity(ml.qty_done,ml.product_id.uom_id)
                total_weight+=qty*ml.product_id.weight
            defaults['shipping_weight']=total_weight
        returndefaults

    picking_id=fields.Many2one('stock.picking','Picking')
    delivery_packaging_id=fields.Many2one('product.packaging','DeliveryPackaging',check_company=True)
    shipping_weight=fields.Float('ShippingWeight')
    weight_uom_name=fields.Char(string='Weightunitofmeasurelabel',compute='_compute_weight_uom_name')
    company_id=fields.Many2one(related='picking_id.company_id')

    @api.depends('delivery_packaging_id')
    def_compute_weight_uom_name(self):
        weight_uom_id=self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        forpackageinself:
            package.weight_uom_name=weight_uom_id.name

    @api.onchange('delivery_packaging_id','shipping_weight')
    def_onchange_packaging_weight(self):
        ifself.delivery_packaging_id.max_weightandself.shipping_weight>self.delivery_packaging_id.max_weight:
            warning_mess={
                'title':_('Packagetooheavy!'),
                'message':_('Theweightofyourpackageishigherthanthemaximumweightauthorizedforthispackagetype.Pleasechooseanotherpackagetype.')
            }
            return{'warning':warning_mess}

    defaction_put_in_pack(self):
        picking_move_lines=self.picking_id.move_line_ids
        ifnotself.picking_id.picking_type_id.show_reservedandnotself.env.context.get('barcode_view'):
            picking_move_lines=self.picking_id.move_line_nosuggest_ids

        move_line_ids=picking_move_lines.filtered(lambdaml:
            float_compare(ml.qty_done,0.0,precision_rounding=ml.product_uom_id.rounding)>0
            andnotml.result_package_id
        )
        ifnotmove_line_ids:
            move_line_ids=picking_move_lines.filtered(lambdaml:float_compare(ml.product_uom_qty,0.0,
                                 precision_rounding=ml.product_uom_id.rounding)>0andfloat_compare(ml.qty_done,0.0,
                                 precision_rounding=ml.product_uom_id.rounding)==0)

        delivery_package=self.picking_id._put_in_pack(move_line_ids)
        #writeshippingweightandproduct_packagingon'stock_quant_package'ifneeded
        ifself.delivery_packaging_id:
            delivery_package.packaging_id=self.delivery_packaging_id
        ifself.shipping_weight:
            delivery_package.shipping_weight=self.shipping_weight
