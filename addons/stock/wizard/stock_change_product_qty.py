#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError


classProductChangeQuantity(models.TransientModel):
    _name="stock.change.product.qty"
    _description="ChangeProductQuantity"

    product_id=fields.Many2one('product.product','Product',required=True)
    product_tmpl_id=fields.Many2one('product.template','Template',required=True)
    product_variant_count=fields.Integer('VariantCount',
        related='product_tmpl_id.product_variant_count',readonly=False)
    new_quantity=fields.Float(
        'NewQuantityonHand',default=1,
        digits='ProductUnitofMeasure',required=True,
        help='ThisquantityisexpressedintheDefaultUnitofMeasureoftheproduct.')

    @api.onchange('product_id')
    def_onchange_product_id(self):
        self.new_quantity=self.product_id.qty_available

    @api.constrains('new_quantity')
    defcheck_new_quantity(self):
        ifany(wizard.new_quantity<0forwizardinself):
            raiseUserError(_('Quantitycannotbenegative.'))

    defchange_product_qty(self):
        """ChangestheProductQuantitybycreating/editingcorrespondingquant.
        """
        warehouse=self.env['stock.warehouse'].search(
            [('company_id','=',self.env.company.id)],limit=1
        )
        #Beforecreatinganewquant,thequand`create`methodwillcheckif
        #itexistsalready.Ifitdoes,it'lleditits`inventory_quantity`
        #insteadofcreateanewone.
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id':self.product_id.id,
            'location_id':warehouse.lot_stock_id.id,
            'inventory_quantity':self.new_quantity,
        })
        return{'type':'ir.actions.act_window_close'}
