#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classStockQuant(models.Model):
    _inherit='stock.quant'

    removal_date=fields.Datetime(related='lot_id.removal_date',store=True,readonly=False)
    use_expiration_date=fields.Boolean(related='product_id.use_expiration_date',readonly=True)

    @api.model
    def_get_inventory_fields_create(self):
        """Returnsalistoffieldsusercaneditwhenhewanttocreateaquantin`inventory_mode`.
        """
        res=super()._get_inventory_fields_create()
        res+=['removal_date']
        returnres

    @api.model
    def_get_inventory_fields_write(self):
        """Returnsalistoffieldsusercaneditwhenhewanttoeditaquantin`inventory_mode`.
        """
        res=super()._get_inventory_fields_write()
        res+=['removal_date']
        returnres

    @api.model
    def_get_removal_strategy_order(self,removal_strategy):
        ifremoval_strategy=='fefo':
            return'removal_date,in_date,id'
        returnsuper(StockQuant,self)._get_removal_strategy_order(removal_strategy)
