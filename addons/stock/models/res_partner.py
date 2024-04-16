#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models
fromflectra.addons.base.models.res_partnerimportWARNING_HELP,WARNING_MESSAGE


classPartner(models.Model):
    _inherit='res.partner'
    _check_company_auto=True

    property_stock_customer=fields.Many2one(
        'stock.location',string="CustomerLocation",company_dependent=True,check_company=True,
        domain="['|',('company_id','=',False),('company_id','=',allowed_company_ids[0])]",
        help="Thestocklocationusedasdestinationwhensendinggoodstothiscontact.")
    property_stock_supplier=fields.Many2one(
        'stock.location',string="VendorLocation",company_dependent=True,check_company=True,
        domain="['|',('company_id','=',False),('company_id','=',allowed_company_ids[0])]",
        help="Thestocklocationusedassourcewhenreceivinggoodsfromthiscontact.")
    picking_warn=fields.Selection(WARNING_MESSAGE,'StockPicking',help=WARNING_HELP,default='no-message')
    picking_warn_msg=fields.Text('MessageforStockPicking')
