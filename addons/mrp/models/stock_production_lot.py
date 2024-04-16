#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_
fromflectra.exceptionsimportUserError


classStockProductionLot(models.Model):
    _inherit='stock.production.lot'

    def_check_create(self):
        active_mo_id=self.env.context.get('active_mo_id')
        ifactive_mo_id:
            active_mo=self.env['mrp.production'].browse(active_mo_id)
            ifnotactive_mo.picking_type_id.use_create_components_lots:
                raiseUserError(_('Youarenotallowedtocreateoreditalotorserialnumberforthecomponentswiththeoperationtype"Manufacturing".Tochangethis,goontheoperationtypeandtickthebox"CreateNewLots/SerialNumbersforComponents".'))
        returnsuper(StockProductionLot,self)._check_create()
