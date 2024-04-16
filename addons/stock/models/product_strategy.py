#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError


classRemovalStrategy(models.Model):
    _name='product.removal'
    _description='RemovalStrategy'

    name=fields.Char('Name',required=True)
    method=fields.Char("Method",required=True,help="FIFO,LIFO...")


classStockPutawayRule(models.Model):
    _name='stock.putaway.rule'
    _order='sequence,product_id'
    _description='PutawayRule'
    _check_company_auto=True

    def_default_category_id(self):
        ifself.env.context.get('active_model')=='product.category':
            returnself.env.context.get('active_id')

    def_default_location_id(self):
        ifself.env.context.get('active_model')=='stock.location':
            returnself.env.context.get('active_id')

    def_default_product_id(self):
        ifself.env.context.get('active_model')=='product.template'andself.env.context.get('active_id'):
            product_template=self.env['product.template'].browse(self.env.context.get('active_id'))
            product_template=product_template.exists()
            ifproduct_template.product_variant_count==1:
                returnproduct_template.product_variant_id
        elifself.env.context.get('active_model')=='product.product':
            returnself.env.context.get('active_id')

    def_domain_category_id(self):
        active_model=self.env.context.get('active_model')
        ifactive_modelin('product.template','product.product')andself.env.context.get('active_id'):
            product=self.env[active_model].browse(self.env.context.get('active_id'))
            product=product.exists()
            ifproduct:
                return[('id','=',product.categ_id.id)]
        return[]

    def_domain_product_id(self):
        domain="[('type','!=','service'),'|',('company_id','=',False),('company_id','=',company_id)]"
        ifself.env.context.get('active_model')=='product.template':
            return[('product_tmpl_id','=',self.env.context.get('active_id'))]
        returndomain

    product_id=fields.Many2one(
        'product.product','Product',check_company=True,
        default=_default_product_id,domain=_domain_product_id,ondelete='cascade')
    category_id=fields.Many2one('product.category','ProductCategory',
        default=_default_category_id,domain=_domain_category_id,ondelete='cascade')
    location_in_id=fields.Many2one(
        'stock.location','Whenproductarrivesin',check_company=True,
        domain="[('child_ids','!=',False),'|',('company_id','=',False),('company_id','=',company_id)]",
        default=_default_location_id,required=True,ondelete='cascade')
    location_out_id=fields.Many2one(
        'stock.location','Storeto',check_company=True,
        domain="[('id','child_of',location_in_id),('id','!=',location_in_id),'|',('company_id','=',False),('company_id','=',company_id)]",
        required=True,ondelete='cascade')
    sequence=fields.Integer('Priority',help="Givetothemorespecializedcategory,ahigherprioritytohavethemintopofthelist.")
    company_id=fields.Many2one(
        'res.company','Company',required=True,
        default=lambdas:s.env.company.id,index=True)

    @api.onchange('location_in_id')
    def_onchange_location_in(self):
        ifself.location_out_id:
            child_location_count=self.env['stock.location'].search_count([
                ('id','=',self.location_out_id.id),
                ('id','child_of',self.location_in_id.id),
                ('id','!=',self.location_in_id.id),
            ])
            ifnotchild_location_count:
                self.location_out_id=None

    defwrite(self,vals):
        if'company_id'invals:
            forruleinself:
                ifrule.company_id.id!=vals['company_id']:
                    raiseUserError(_("Changingthecompanyofthisrecordisforbiddenatthispoint,youshouldratherarchiveitandcreateanewone."))
        returnsuper(StockPutawayRule,self).write(vals)
