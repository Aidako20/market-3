#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.modules.moduleimportget_module_resource
fromflectra.toolsimportformatLang


classLunchProductCategory(models.Model):
    """Categoryoftheproductsuchaspizza,sandwich,pasta,chinese,burger..."""
    _name='lunch.product.category'
    _inherit='image.mixin'
    _description='LunchProductCategory'

    @api.model
    def_default_image(self):
        image_path=get_module_resource('lunch','static/img','lunch.png')
        returnbase64.b64encode(open(image_path,'rb').read())

    name=fields.Char('ProductCategory',required=True,translate=True)
    company_id=fields.Many2one('res.company')
    currency_id=fields.Many2one('res.currency',related='company_id.currency_id')
    topping_label_1=fields.Char('Extra1Label',required=True,default='Extras')
    topping_label_2=fields.Char('Extra2Label',required=True,default='Beverages')
    topping_label_3=fields.Char('Extra3Label',required=True,default='ExtraLabel3')
    topping_ids_1=fields.One2many('lunch.topping','category_id',domain=[('topping_category','=',1)])
    topping_ids_2=fields.One2many('lunch.topping','category_id',domain=[('topping_category','=',2)])
    topping_ids_3=fields.One2many('lunch.topping','category_id',domain=[('topping_category','=',3)])
    topping_quantity_1=fields.Selection([
        ('0_more','NoneorMore'),
        ('1_more','OneorMore'),
        ('1','OnlyOne')],'Extra1Quantity',default='0_more',required=True)
    topping_quantity_2=fields.Selection([
        ('0_more','NoneorMore'),
        ('1_more','OneorMore'),
        ('1','OnlyOne')],'Extra2Quantity',default='0_more',required=True)
    topping_quantity_3=fields.Selection([
        ('0_more','NoneorMore'),
        ('1_more','OneorMore'),
        ('1','OnlyOne')],'Extra3Quantity',default='0_more',required=True)
    product_count=fields.Integer(compute='_compute_product_count',help="Thenumberofproductsrelatedtothiscategory")
    active=fields.Boolean(string='Active',default=True)
    image_1920=fields.Image(default=_default_image)

    def_compute_product_count(self):
        product_data=self.env['lunch.product'].read_group([('category_id','in',self.ids)],['category_id'],['category_id'])
        data={product['category_id'][0]:product['category_id_count']forproductinproduct_data}
        forcategoryinself:
            category.product_count=data.get(category.id,0)

    @api.model
    defcreate(self,vals):
        fortoppinginvals.get('topping_ids_2',[]):
            topping[2].update({'topping_category':2})
        fortoppinginvals.get('topping_ids_3',[]):
            topping[2].update({'topping_category':3})
        returnsuper(LunchProductCategory,self).create(vals)

    defwrite(self,vals):
        fortoppinginvals.get('topping_ids_2',[]):
            topping_values=topping[2]
            iftopping_values:
                topping_values.update({'topping_category':2})
        fortoppinginvals.get('topping_ids_3',[]):
            topping_values=topping[2]
            iftopping_values:
                topping_values.update({'topping_category':3})
        returnsuper(LunchProductCategory,self).write(vals)

    deftoggle_active(self):
        """Archivingrelatedlunchproduct"""
        res=super().toggle_active()
        Product=self.env['lunch.product'].with_context(active_test=False)
        all_products=Product.search([('category_id','in',self.ids)])
        all_products._sync_active_from_related()
        returnres

classLunchTopping(models.Model):
    """"""
    _name='lunch.topping'
    _description='LunchExtras'

    name=fields.Char('Name',required=True)
    company_id=fields.Many2one('res.company',default=lambdaself:self.env.company)
    currency_id=fields.Many2one('res.currency',related='company_id.currency_id')
    price=fields.Float('Price',digits='Account',required=True)
    category_id=fields.Many2one('lunch.product.category',ondelete='cascade')
    topping_category=fields.Integer('ToppingCategory',help="Thisfieldisatechnicalfield",required=True,default=1)

    defname_get(self):
        currency_id=self.env.company.currency_id
        res=dict(super(LunchTopping,self).name_get())
        fortoppinginself:
            price=formatLang(self.env,topping.price,currency_obj=currency_id)
            res[topping.id]='%s%s'%(topping.name,price)
        returnlist(res.items())


classLunchProduct(models.Model):
    """Productsavailabletoorder.Aproductislinkedtoaspecificvendor."""
    _name='lunch.product'
    _description='LunchProduct'
    _inherit='image.mixin'
    _order='name'
    _check_company_auto=True

    name=fields.Char('ProductName',required=True,translate=True)
    category_id=fields.Many2one('lunch.product.category','ProductCategory',check_company=True,required=True)
    description=fields.Text('Description',translate=True)
    price=fields.Float('Price',digits='Account',required=True)
    supplier_id=fields.Many2one('lunch.supplier','Vendor',check_company=True,required=True)
    active=fields.Boolean(default=True)

    company_id=fields.Many2one('res.company',related='supplier_id.company_id',readonly=False,store=True)
    currency_id=fields.Many2one('res.currency',related='company_id.currency_id')

    new_until=fields.Date('NewUntil')
    favorite_user_ids=fields.Many2many('res.users','lunch_product_favorite_user_rel','product_id','user_id',check_company=True)

    def_sync_active_from_related(self):
        """Archive/unarchiveproductafterrelatedfieldisarchived/unarchived"""
        returnself.filtered(lambdap:(p.category_id.activeandp.supplier_id.active)!=p.active).toggle_active()

    deftoggle_active(self):
        ifself.filtered(lambdaproduct:notproduct.activeandnotproduct.category_id.active):
            raiseUserError(_("Theproductcategoryisarchived.Theuserhavetounarchivethecategoryorchangethecategoryoftheproduct."))
        ifself.filtered(lambdaproduct:notproduct.activeandnotproduct.supplier_id.active):
            raiseUserError(_("Theproductsupplierisarchived.Theuserhavetounarchivethesupplierorchangethesupplieroftheproduct."))
        returnsuper().toggle_active()
