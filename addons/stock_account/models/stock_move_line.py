#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models
fromflectra.toolsimportfloat_is_zero


classStockMoveLine(models.Model):
    _inherit='stock.move.line'

    #-------------------------------------------------------------------------
    #CRUD
    #-------------------------------------------------------------------------
    @api.model_create_multi
    defcreate(self,vals_list):
        move_lines=super(StockMoveLine,self).create(vals_list)
        formove_lineinmove_lines:
            ifmove_line.state!='done':
                continue
            move=move_line.move_id
            rounding=move.product_id.uom_id.rounding
            diff=move.product_uom._compute_quantity(move_line.qty_done,move.product_id.uom_id)
            iffloat_is_zero(diff,precision_rounding=rounding):
                continue
            self._create_correction_svl(move,diff)
        returnmove_lines

    defwrite(self,vals):
        if'qty_done'invals:
            formove_lineinself:
                ifmove_line.state!='done':
                    continue
                move=move_line.move_id
                rounding=move.product_id.uom_id.rounding
                diff=move.product_uom._compute_quantity(vals['qty_done']-move_line.qty_done,move.product_id.uom_id)
                iffloat_is_zero(diff,precision_rounding=rounding):
                    continue
                self._create_correction_svl(move,diff)
        returnsuper(StockMoveLine,self).write(vals)

    #-------------------------------------------------------------------------
    #SVLcreationhelpers
    #-------------------------------------------------------------------------
    @api.model
    def_create_correction_svl(self,move,diff):
        stock_valuation_layers=self.env['stock.valuation.layer']
        ifmove._is_in()anddiff>0ormove._is_out()anddiff<0:
            move.product_price_update_before_done(forced_qty=diff)
            stock_valuation_layers|=move._create_in_svl(forced_quantity=abs(diff))
            ifmove.product_id.cost_methodin('average','fifo'):
                move.product_id._run_fifo_vacuum(move.company_id)
        elifmove._is_in()anddiff<0ormove._is_out()anddiff>0:
            stock_valuation_layers|=move._create_out_svl(forced_quantity=abs(diff))
        elifmove._is_dropshipped()anddiff>0ormove._is_dropshipped_returned()anddiff<0:
            stock_valuation_layers|=move._create_dropshipped_svl(forced_quantity=abs(diff))
        elifmove._is_dropshipped()anddiff<0ormove._is_dropshipped_returned()anddiff>0:
            stock_valuation_layers|=move._create_dropshipped_returned_svl(forced_quantity=abs(diff))

        forsvlinstock_valuation_layers:
            ifnotsvl.product_id.valuation=='real_time':
                continue
            svl.stock_move_id._account_entry_move(svl.quantity,svl.description,svl.id,svl.value)
