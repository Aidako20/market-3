#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_
fromflectra.exceptionsimportUserError
fromflectra.toolsimportgroupby


classProductTemplate(models.Model):
    _name='product.template'
    _inherit='product.template'

    defaction_bom_cost(self):
        templates=self.filtered(lambdat:t.product_variant_count==1andt.bom_count>0)
        iftemplates:
            returntemplates.mapped('product_variant_id').action_bom_cost()

    defbutton_bom_cost(self):
        templates=self.filtered(lambdat:t.product_variant_count==1andt.bom_count>0)
        iftemplates:
            returntemplates.mapped('product_variant_id').button_bom_cost()


classProductProduct(models.Model):
    _name='product.product'
    _inherit='product.product'
    _description='Product'

    defbutton_bom_cost(self):
        self.ensure_one()
        self._set_price_from_bom()

    defaction_bom_cost(self):
        boms_to_recompute=self.env['mrp.bom'].search(['|',('product_id','in',self.ids),'&',('product_id','=',False),('product_tmpl_id','in',self.mapped('product_tmpl_id').ids)])
        forproductinself:
            product._set_price_from_bom(boms_to_recompute)

    def_set_price_from_bom(self,boms_to_recompute=False):
        self.ensure_one()
        bom=self.env['mrp.bom']._bom_find(product=self)
        ifbom:
            self.standard_price=self._compute_bom_price(bom,boms_to_recompute=boms_to_recompute)

    def_compute_average_price(self,qty_invoiced,qty_to_invoice,stock_moves):
        self.ensure_one()
        ifstock_moves.product_id==self:
            returnsuper()._compute_average_price(qty_invoiced,qty_to_invoice,stock_moves)
        bom=self.env['mrp.bom']._bom_find(product=self,company_id=stock_moves.company_id.id,bom_type='phantom')
        ifnotbom:
            returnsuper()._compute_average_price(qty_invoiced,qty_to_invoice,stock_moves)
        value=0
        dummy,bom_lines=bom.explode(self,1)
        bom_lines={line:dataforline,datainbom_lines}
        forbom_line,moves_listingroupby(stock_moves.filtered(lambdasm:sm.state!='cancel'),lambdasm:sm.bom_line_id):
            ifbom_linenotinbom_lines:
                formoveinmoves_list:
                    value+=move.product_qty*move.product_id._compute_average_price(qty_invoiced*move.product_qty,qty_to_invoice*move.product_qty,move)
                continue
            line_qty=bom_line.product_uom_id._compute_quantity(bom_lines[bom_line]['qty'],bom_line.product_id.uom_id)
            moves=self.env['stock.move'].concat(*moves_list)
            value+=line_qty*bom_line.product_id._compute_average_price(qty_invoiced*line_qty,qty_to_invoice*line_qty,moves)
        returnvalue

    def_compute_bom_price(self,bom,boms_to_recompute=False):
        self.ensure_one()
        ifnotbom:
            return0
        ifnotboms_to_recompute:
            boms_to_recompute=[]
        total=0
        foroptinbom.operation_ids:
            duration_expected=(
                opt.workcenter_id.time_start+
                opt.workcenter_id.time_stop+
                opt.time_cycle*100/opt.workcenter_id.time_efficiency)
            total+=(duration_expected/60)*opt.workcenter_id.costs_hour
        forlineinbom.bom_line_ids:
            ifline._skip_bom_line(self):
                continue

            #Computerecursiveiflinehas`child_line_ids`
            ifline.child_bom_idandline.child_bom_idinboms_to_recompute:
                child_total=line.product_id._compute_bom_price(line.child_bom_id,boms_to_recompute=boms_to_recompute)
                total+=line.product_id.uom_id._compute_price(child_total,line.product_uom_id)*line.product_qty
            else:
                total+=line.product_id.uom_id._compute_price(line.product_id.standard_price,line.product_uom_id)*line.product_qty
        returnbom.product_uom_id._compute_price(total/bom.product_qty,self.uom_id)
