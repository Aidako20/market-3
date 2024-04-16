#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classStockMove(models.Model):
    _inherit="stock.move"

    def_is_purchase_return(self):
        res=super()._is_purchase_return()
        returnresorself._is_dropshipped_returned()

    def_is_dropshipped(self):
        res=super()._is_dropshipped()
        returnresor(
                self.partner_id.property_stock_subcontractor.parent_path
                andself.partner_id.property_stock_subcontractor.parent_pathinself.location_id.parent_path
                andself.location_dest_id.usage=='customer'
        )

    def_is_dropshipped_returned(self):
        res=super()._is_dropshipped_returned()
        returnresor(
                self.location_id.usage=='customer'
                andself.partner_id.property_stock_subcontractor.parent_path
                andself.partner_id.property_stock_subcontractor.parent_pathinself.location_dest_id.parent_path
        )
