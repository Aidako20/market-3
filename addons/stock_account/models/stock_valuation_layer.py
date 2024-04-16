#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,tools
fromflectra.toolsimportfloat_compare,float_is_zero


classStockValuationLayer(models.Model):
    """StockValuationLayer"""

    _name='stock.valuation.layer'
    _description='StockValuationLayer'
    _order='create_date,id'

    _rec_name='product_id'

    company_id=fields.Many2one('res.company','Company',readonly=True,required=True)
    product_id=fields.Many2one('product.product','Product',readonly=True,required=True,check_company=True,auto_join=True)
    categ_id=fields.Many2one('product.category',related='product_id.categ_id')
    product_tmpl_id=fields.Many2one('product.template',related='product_id.product_tmpl_id')
    quantity=fields.Float('Quantity',digits=0,help='Quantity',readonly=True)
    uom_id=fields.Many2one(related='product_id.uom_id',readonly=True,required=True)
    currency_id=fields.Many2one('res.currency','Currency',related='company_id.currency_id',readonly=True,required=True)
    unit_cost=fields.Monetary('UnitValue',readonly=True)
    value=fields.Monetary('TotalValue',readonly=True)
    remaining_qty=fields.Float(digits=0,readonly=True)
    remaining_value=fields.Monetary('RemainingValue',readonly=True)
    description=fields.Char('Description',readonly=True)
    stock_valuation_layer_id=fields.Many2one('stock.valuation.layer','LinkedTo',readonly=True,check_company=True)
    stock_valuation_layer_ids=fields.One2many('stock.valuation.layer','stock_valuation_layer_id')
    stock_move_id=fields.Many2one('stock.move','StockMove',readonly=True,check_company=True,index=True)
    account_move_id=fields.Many2one('account.move','JournalEntry',readonly=True,check_company=True,index=True)

    definit(self):
        tools.create_index(
            self._cr,'stock_valuation_layer_index',
            self._table,['product_id','remaining_qty','stock_move_id','company_id','create_date']
        )

    def_consume_specific_qty(self,qty_valued,qty_to_value):
        """
        IterateontheSVLtofirstskiptheqtyalreadyvalued.Then,keep
        iteratingtoconsume`qty_to_value`andstop
        Themethodreturnsthevaluedquantityanditsvaluation
        """
        ifnotself:
            return0,0

        rounding=self.product_id.uom_id.rounding
        qty_to_take_on_candidates=qty_to_value
        tmp_value=0 #toaccumulatethevaluetakenonthecandidates
        forcandidateinself:
            iffloat_is_zero(candidate.quantity,precision_rounding=rounding):
                continue
            candidate_quantity=abs(candidate.quantity)
            returned_qty=sum([sm.product_uom._compute_quantity(sm.quantity_done,self.uom_id)
                                forsmincandidate.stock_move_id.returned_move_idsifsm.state=='done'])
            candidate_quantity-=returned_qty
            iffloat_is_zero(candidate_quantity,precision_rounding=rounding):
                continue
            ifnotfloat_is_zero(qty_valued,precision_rounding=rounding):
                qty_ignored=min(qty_valued,candidate_quantity)
                qty_valued-=qty_ignored
                candidate_quantity-=qty_ignored
                iffloat_is_zero(candidate_quantity,precision_rounding=rounding):
                    continue
            qty_taken_on_candidate=min(qty_to_take_on_candidates,candidate_quantity)

            qty_to_take_on_candidates-=qty_taken_on_candidate
            tmp_value+=qty_taken_on_candidate*((candidate.value+sum(candidate.stock_valuation_layer_ids.mapped('value')))/candidate.quantity)
            iffloat_is_zero(qty_to_take_on_candidates,precision_rounding=rounding):
                break

        returnqty_to_value-qty_to_take_on_candidates,tmp_value

    def_consume_all(self,qty_valued,valued,qty_to_value):
        """
        Themethodconsumesallsvltogetthetotalqty/value.Thenitdeducts
        thealreadyconsumedqty/value.Finally,ittriestoconsumethe`qty_to_value`
        Themethodreturnsthevaluedquantityanditsvaluation
        """
        ifnotself:
            return0,0

        rounding=self.product_id.uom_id.rounding
        qty_total=-qty_valued
        value_total=-valued
        new_valued_qty=0
        new_valuation=0

        forsvlinself:
            iffloat_is_zero(svl.quantity,precision_rounding=rounding):
                continue
            relevant_qty=abs(svl.quantity)
            returned_qty=sum([sm.product_uom._compute_quantity(sm.quantity_done,self.uom_id)
                                forsminsvl.stock_move_id.returned_move_idsifsm.state=='done'])
            relevant_qty-=returned_qty
            iffloat_is_zero(relevant_qty,precision_rounding=rounding):
                continue
            qty_total+=relevant_qty
            value_total+=relevant_qty*((svl.value+sum(svl.stock_valuation_layer_ids.mapped('value')))/svl.quantity)

        iffloat_compare(qty_total,0,precision_rounding=rounding)>0:
            unit_cost=value_total/qty_total
            new_valued_qty=min(qty_total,qty_to_value)
            new_valuation=unit_cost*new_valued_qty

        returnnew_valued_qty,new_valuation
