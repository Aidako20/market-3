#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    module_stock_landed_costs=fields.Boolean("LandedCosts",
        help="Affectlandedcostsonreceptionoperationsandsplitthemamongproductstoupdatetheircostprice.")
