#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models
fromflectra.addons.stock_landed_costs.models.stock_landed_costimportSPLIT_METHOD
fromflectra.exceptionsimportUserError
fromflectraimport_


classProductTemplate(models.Model):
    _inherit="product.template"

    landed_cost_ok=fields.Boolean('IsaLandedCost',help='Indicateswhethertheproductisalandedcost.')
    split_method_landed_cost=fields.Selection(SPLIT_METHOD,string="DefaultSplitMethod",
                                                help="DefaultSplitMethodwhenusedforLandedCost")

    defwrite(self,vals):
        forproductinself:
            if(('type'invalsandvals['type']!='service')or('landed_cost_ok'invalsandnotvals['landed_cost_ok']))andproduct.type=='service'andproduct.landed_cost_ok:
                ifself.env['account.move.line'].search_count([('product_id','in',product.product_variant_ids.ids),('is_landed_costs_line','=',True)]):
                    raiseUserError(_("Youcannotchangetheproducttypeordisablelandedcostoptionbecausetheproductisusedinanaccountmoveline."))
                vals['landed_cost_ok']=False

        returnsuper().write(vals)
