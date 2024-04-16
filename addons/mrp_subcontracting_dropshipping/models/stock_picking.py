#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.toolsimportfloat_compare


classStockPicking(models.Model):
    _inherit='stock.picking'

    def_action_done(self):
        """Ifneeded,createacompensationlayer,soweaddtheMOcost
        tothedropshipone
        """
        res=super()._action_done()
        formoveinself.move_lines:
            ifnot(move.is_subcontractandmove._is_dropshipped()andmove.state=='done'):
                continue

            dropship_svls=move.stock_valuation_layer_ids
            ifnotdropship_svls:
                continue

            subcontract_svls=move.move_orig_ids.stock_valuation_layer_ids
            subcontract_value=sum(subcontract_svls.mapped('value'))
            dropship_value=abs(sum(dropship_svls.mapped('value')))
            diff=subcontract_value-dropship_value
            iffloat_compare(diff,0,precision_rounding=move.company_id.currency_id.rounding)<=0:
                continue

            svl_vals=move._prepare_common_svl_vals()
            svl_vals.update({
                'remaining_value':0,
                'remaining_qty':0,
                'value':-diff,
                'quantity':0,
                'unit_cost':0,
                'stock_valuation_layer_id':dropship_svls[0].id,
                'stock_move_id':False,
            })
            svl=self.env['stock.valuation.layer'].create(svl_vals)

            move=move.with_company(move.company_id)
            ifmove.product_id.valuation!='real_time':
                continue
            move._account_entry_move(svl.quantity,svl.description,svl.id,svl.value)

        returnres

    def_get_warehouse(self,subcontract_move):
        ifsubcontract_move.sale_line_id:
            returnsubcontract_move.sale_line_id.order_id.warehouse_id
        returnsuper(StockPicking,self)._get_warehouse(subcontract_move)

    def_prepare_subcontract_mo_vals(self,subcontract_move,bom):
        res=super()._prepare_subcontract_mo_vals(subcontract_move,bom)
        ifnotres.get('picking_type_id')and(
                subcontract_move.location_dest_id.usage=='customer'
                orsubcontract_move.partner_id.property_stock_subcontractor.parent_pathinsubcontract_move.location_dest_id.parent_path
        ):
            #Iftheif-conditionisrespected,itmeansthat`subcontract_move`isnot
            #relatedtoaspecificwarehouse.Thiscanhappenif,forinstance,theuser
            #confirmsaPOwithasubcontractedproductthatshouldbedeliveredtoa
            #customer(dropshipping).Inthatcase,wecanuseadefaultwarehouseto
            #getthepickingtype
            default_warehouse=self.env['stock.warehouse'].search([('company_id','=',subcontract_move.company_id.id)],limit=1)
            res['picking_type_id']=default_warehouse.subcontracting_type_id.id,
        returnres
