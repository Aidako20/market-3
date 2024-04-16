#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classStockWarnInsufficientQty(models.AbstractModel):
    _name='stock.warn.insufficient.qty'
    _description='WarnInsufficientQuantity'

    product_id=fields.Many2one('product.product','Product',required=True)
    location_id=fields.Many2one('stock.location','Location',domain="[('usage','=','internal')]",required=True)
    quant_ids=fields.Many2many('stock.quant',compute='_compute_quant_ids')
    quantity=fields.Float(string="Quantity",required=True)
    product_uom_name=fields.Char("UnitofMeasure",required=True)

    def_get_reference_document_company_id(self):
        raiseNotImplementedError()

    @api.depends('product_id')
    def_compute_quant_ids(self):
        forquantityinself:
            quantity.quant_ids=self.env['stock.quant'].search([
                ('product_id','=',quantity.product_id.id),
                ('location_id.usage','=','internal'),
                ('company_id','=',quantity._get_reference_document_company_id().id)
            ])

    defaction_done(self):
        raiseNotImplementedError()


classStockWarnInsufficientQtyScrap(models.TransientModel):
    _name='stock.warn.insufficient.qty.scrap'
    _inherit='stock.warn.insufficient.qty'
    _description='WarnInsufficientScrapQuantity'

    scrap_id=fields.Many2one('stock.scrap','Scrap')

    def_get_reference_document_company_id(self):
        returnself.scrap_id.company_id

    defaction_done(self):
        returnself.scrap_id.do_scrap()

    defaction_cancel(self):
        #FIXMEinmaster:weshouldnothavecreatedthescrapinafirstplace
        ifself.env.context.get('not_unlink_on_discard'):
            returnTrue
        else:
            returnself.scrap_id.sudo().unlink()
