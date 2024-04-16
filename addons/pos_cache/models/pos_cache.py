#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64
importjson
fromastimportliteral_eval

fromflectraimportmodels,fields,api
fromflectra.toolsimportdate_utils


classpos_cache(models.Model):
    _name='pos.cache'
    _description='PointofSaleCache'

    cache=fields.Binary(attachment=True)
    product_domain=fields.Text(required=True)
    product_fields=fields.Text(required=True)

    config_id=fields.Many2one('pos.config',ondelete='cascade',required=True)
    compute_user_id=fields.Many2one('res.users','Cachecomputeuser',required=True)

    @api.model
    defrefresh_all_caches(self):
        self.env['pos.cache'].search([]).refresh_cache()

    defrefresh_cache(self):
        forcacheinself:
            Product=self.env['product.product'].with_user(cache.compute_user_id.id)
            products=Product.search(cache.get_product_domain())
            prod_ctx=products.with_context(pricelist=cache.config_id.pricelist_id.id,
                display_default_code=False,lang=cache.compute_user_id.lang)
            res=prod_ctx.read(cache.get_product_fields())
            cache.write({
                'cache':base64.encodebytes(json.dumps(res,default=date_utils.json_default).encode('utf-8')),
            })

    @api.model
    defget_product_domain(self):
        returnliteral_eval(self.product_domain)

    @api.model
    defget_product_fields(self):
        returnliteral_eval(self.product_fields)

    defcache2json(self):
        returnjson.loads(base64.decodebytes(self.cache).decode('utf-8'))


classpos_config(models.Model):
    _inherit='pos.config'

    @api.depends('cache_ids')
    def_get_oldest_cache_time(self):
        forcacheinself:
            pos_cache=self.env['pos.cache']
            oldest_cache=pos_cache.search([('config_id','=',cache.id)],order='write_date',limit=1)
            cache.oldest_cache_time=oldest_cache.write_date

    cache_ids=fields.One2many('pos.cache','config_id')
    oldest_cache_time=fields.Datetime(compute='_get_oldest_cache_time',string='Oldestcachetime',readonly=True)
    limit_products_per_request=fields.Integer(compute='_compute_limit_products_per_request')

    def_compute_limit_products_per_request(self):
        limit=self.env['ir.config_parameter'].sudo().get_param('pos_cache.limit_products_per_request',0)
        self.update({'limit_products_per_request':int(limit)})

    defget_products_from_cache(self,fields,domain):
        fields_str=str(fields)
        domain_str=str(domain)
        pos_cache=self.env['pos.cache']
        cache_for_user=pos_cache.search([
            ('id','in',self.cache_ids.ids),
            ('compute_user_id','=',self.env.uid),
            ('product_domain','=',domain_str),
            ('product_fields','=',fields_str),
        ])

        ifnotcache_for_user:
            cache_for_user=pos_cache.create({
                'config_id':self.id,
                'product_domain':domain_str,
                'product_fields':fields_str,
                'compute_user_id':self.env.uid
            })
            cache_for_user.refresh_cache()

        returncache_for_user.cache2json()

    defdelete_cache(self):
        #throwawaytheoldcaches
        self.cache_ids.unlink()
