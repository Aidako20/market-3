#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classProductTemplate(models.Model):
    _inherit='product.template'

    available_in_pos=fields.Boolean(string='AvailableinPOS',help='CheckifyouwantthisproducttoappearinthePointofSale.',default=False)
    to_weight=fields.Boolean(string='ToWeighWithScale',help="Checkiftheproductshouldbeweightedusingthehardwarescaleintegration.")
    pos_categ_id=fields.Many2one(
        'pos.category',string='PointofSaleCategory',
        help="CategoryusedinthePointofSale.")

    defunlink(self):
        product_ctx=dict(self.env.contextor{},active_test=False)
        ifself.with_context(product_ctx).search_count([('id','in',self.ids),('available_in_pos','=',True)]):
            ifself.env['pos.session'].sudo().search_count([('state','!=','closed')]):
                raiseUserError(_('Youcannotdeleteaproductsaleableinpointofsalewhileasessionisstillopened.'))
        returnsuper(ProductTemplate,self).unlink()

    @api.onchange('sale_ok')
    def_onchange_sale_ok(self):
        ifnotself.sale_ok:
            self.available_in_pos=False


classProductProduct(models.Model):
    _inherit='product.product'

    defunlink(self):
        product_ctx=dict(self.env.contextor{},active_test=False)
        ifself.env['pos.session'].sudo().search_count([('state','!=','closed')]):
            ifself.with_context(product_ctx).search_count([('id','in',self.ids),('product_tmpl_id.available_in_pos','=',True)]):
                raiseUserError(_('Youcannotdeleteaproductsaleableinpointofsalewhileasessionisstillopened.'))
        returnsuper(ProductProduct,self).unlink()


classUomCateg(models.Model):
    _inherit='uom.category'

    is_pos_groupable=fields.Boolean(string='GroupProductsinPOS',
        help="Checkifyouwanttogroupproductsofthiscategoryinpointofsaleorders")


classUom(models.Model):
    _inherit='uom.uom'

    is_pos_groupable=fields.Boolean(related='category_id.is_pos_groupable',readonly=False)
