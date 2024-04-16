#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.tools.sqlimportcolumn_exists,create_column


classStockMove(models.Model):
    _inherit='stock.move'

    def_auto_init(self):
        ifnotcolumn_exists(self.env.cr,"stock_move","weight"):
            #Incaseofabigdatabasewithalotofstockmoves,theRAMgetsexhausted
            #TopreventaprocessfrombeingkilledWecreatethecolumn'weight'manually
            #Thenwedothecomputationinaquerybymultiplyingproductweightwithqty
            create_column(self.env.cr,"stock_move","weight","numeric")
            self.env.cr.execute("""
                UPDATEstock_movemove
                SETweight=move.product_qty*product.weight
                FROMproduct_productproduct
                WHEREmove.product_id=product.id
                ANDmove.state!='cancel'
                """)
        returnsuper()._auto_init()

    weight=fields.Float(compute='_cal_move_weight',digits='StockWeight',store=True,compute_sudo=True)

    @api.depends('product_id','product_uom_qty','product_uom')
    def_cal_move_weight(self):
        moves_with_weight=self.filtered(lambdamoves:moves.product_id.weight>0.00)
        formoveinmoves_with_weight:
            move.weight=(move.product_qty*move.product_id.weight)
        (self-moves_with_weight).weight=0

    def_get_new_picking_values(self):
        vals=super(StockMove,self)._get_new_picking_values()
        vals['carrier_id']=self.mapped('sale_line_id.order_id.carrier_id').id
        returnvals

    def_key_assign_picking(self):
        keys=super(StockMove,self)._key_assign_picking()
        returnkeys+(self.sale_line_id.order_id.carrier_id,)

classStockMoveLine(models.Model):
    _inherit='stock.move.line'

    sale_price=fields.Float(compute='_compute_sale_price')

    @api.depends('qty_done','product_uom_id','product_id','move_id.sale_line_id','move_id.sale_line_id.price_reduce_taxinc','move_id.sale_line_id.product_uom')
    def_compute_sale_price(self):
        formove_lineinself:
            ifmove_line.move_id.sale_line_id:
                unit_price=move_line.move_id.sale_line_id.price_reduce_taxinc
                qty=move_line.product_uom_id._compute_quantity(move_line.qty_done,move_line.move_id.sale_line_id.product_uom)
            else:
                unit_price=move_line.product_id.list_price
                qty=move_line.product_uom_id._compute_quantity(move_line.qty_done,move_line.product_id.uom_id)
            move_line.sale_price=unit_price*qty
        super(StockMoveLine,self)._compute_sale_price()

    def_get_aggregated_product_quantities(self,**kwargs):
        """Returnsdictionaryofproductsandcorrespondingvaluesofinterest+hs_code

        Unfortunatelybecauseweareworkingwithaggregateddata,wehavetoloopthroughthe
        aggregationtoaddmorevaluestoeachdatum.Thisextensionaddsonthehs_codevalue.

        returns:dictionary{same_key_as_super:{same_values_as_super,hs_code},...}
        """
        aggregated_move_lines=super()._get_aggregated_product_quantities(**kwargs)
        foraggregated_move_lineinaggregated_move_lines:
            hs_code=aggregated_move_lines[aggregated_move_line]['product'].product_tmpl_id.hs_code
            aggregated_move_lines[aggregated_move_line]['hs_code']=hs_code
        returnaggregated_move_lines
