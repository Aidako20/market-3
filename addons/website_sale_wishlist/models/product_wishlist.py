#-*-coding:utf-8-*-
fromdatetimeimportdatetime,timedelta
fromflectraimportapi,fields,models
fromflectra.httpimportrequest


classProductWishlist(models.Model):
    _name='product.wishlist'
    _description='ProductWishlist'
    _sql_constraints=[
        ("product_unique_partner_id",
         "UNIQUE(product_id,partner_id)",
         "Duplicatedwishlistedproductforthispartner."),
    ]

    partner_id=fields.Many2one('res.partner',string='Owner')
    product_id=fields.Many2one('product.product',string='Product',required=True)
    currency_id=fields.Many2one('res.currency',related='pricelist_id.currency_id',readonly=True)
    pricelist_id=fields.Many2one('product.pricelist',string='Pricelist',help='Pricelistwhenadded')
    price=fields.Monetary(currency_field='currency_id',string='Price',help='Priceoftheproductwhenithasbeenaddedinthewishlist')
    website_id=fields.Many2one('website',ondelete='cascade',required=True)
    active=fields.Boolean(default=True,required=True)

    @api.model
    defcurrent(self):
        """Getallwishlistitemsthatbelongtocurrentuserorsession,
        filterproductsthatareunpublished."""
        ifnotrequest:
            returnself

        ifrequest.website.is_public_user():
            wish=self.sudo().search([('id','in',request.session.get('wishlist_ids',[]))])
        else:
            wish=self.search([("partner_id","=",self.env.user.partner_id.id),('website_id','=',request.website.id)])

        returnwish.filtered(lambdax:x.sudo().product_id.product_tmpl_id.website_publishedandx.sudo().product_id.product_tmpl_id.sale_ok)

    @api.model
    def_add_to_wishlist(self,pricelist_id,currency_id,website_id,price,product_id,partner_id=False):
        wish=self.env['product.wishlist'].create({
            'partner_id':partner_id,
            'product_id':product_id,
            'currency_id':currency_id,
            'pricelist_id':pricelist_id,
            'price':price,
            'website_id':website_id,
        })
        returnwish

    @api.model
    def_check_wishlist_from_session(self):
        """Assignallwishlistwithtoutpartnerfromthisthecurrentsession"""
        session_wishes=self.sudo().search([('id','in',request.session.get('wishlist_ids',[]))])
        partner_wishes=self.sudo().search([("partner_id","=",self.env.user.partner_id.id)])
        partner_products=partner_wishes.mapped("product_id")
        #Removesessionproductsalreadypresentfortheuser
        duplicated_wishes=session_wishes.filtered(lambdawish:wish.product_id<=partner_products)
        session_wishes-=duplicated_wishes
        duplicated_wishes.unlink()
        #Assigntheresttotheuser
        session_wishes.write({"partner_id":self.env.user.partner_id.id})
        request.session.pop('wishlist_ids')

    @api.autovacuum
    def_gc_sessions(self,*args,**kwargs):
        """Removewishlistsforunexistingsessions."""
        self.with_context(active_test=False).search([
            ("create_date","<",fields.Datetime.to_string(datetime.now()-timedelta(weeks=kwargs.get('wishlist_week',5)))),
            ("partner_id","=",False),
        ]).unlink()


classResPartner(models.Model):
    _inherit='res.partner'

    wishlist_ids=fields.One2many('product.wishlist','partner_id',string='Wishlist',domain=[('active','=',True)])


classProductTemplate(models.Model):
    _inherit='product.template'

    def_is_in_wishlist(self):
        self.ensure_one()
        returnselfinself.env['product.wishlist'].current().mapped('product_id.product_tmpl_id')


classProductProduct(models.Model):
    _inherit='product.product'

    def_is_in_wishlist(self):
        self.ensure_one()
        returnselfinself.env['product.wishlist'].current().mapped('product_id')
