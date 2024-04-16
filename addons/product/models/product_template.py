#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importitertools
importlogging
fromcollectionsimportdefaultdict

fromflectraimportapi,fields,models,tools,_,SUPERUSER_ID
fromflectra.exceptionsimportValidationError,RedirectWarning,UserError
fromflectra.osvimportexpression

_logger=logging.getLogger(__name__)


classProductTemplate(models.Model):
    _name="product.template"
    _inherit=['mail.thread','mail.activity.mixin','image.mixin']
    _description="ProductTemplate"
    _order="name"

    @tools.ormcache()
    def_get_default_category_id(self):
        #Deletionforbidden(atleastthroughunlink)
        returnself.env.ref('product.product_category_all')

    @tools.ormcache()
    def_get_default_uom_id(self):
        #Deletionforbidden(atleastthroughunlink)
        returnself.env.ref('uom.product_uom_unit')

    def_get_default_uom_po_id(self):
        returnself.default_get(['uom_id']).get('uom_id')orself._get_default_uom_id()

    def_read_group_categ_id(self,categories,domain,order):
        category_ids=self.env.context.get('default_categ_id')
        ifnotcategory_idsandself.env.context.get('group_expand'):
            category_ids=categories._search([],order=order,access_rights_uid=SUPERUSER_ID)
        returncategories.browse(category_ids)

    name=fields.Char('Name',index=True,required=True,translate=True)
    sequence=fields.Integer('Sequence',default=1,help='Givesthesequenceorderwhendisplayingaproductlist')
    description=fields.Text(
        'Description',translate=True)
    description_purchase=fields.Text(
        'PurchaseDescription',translate=True)
    description_sale=fields.Text(
        'SalesDescription',translate=True,
        help="AdescriptionoftheProductthatyouwanttocommunicatetoyourcustomers."
             "ThisdescriptionwillbecopiedtoeverySalesOrder,DeliveryOrderandCustomerInvoice/CreditNote")
    type=fields.Selection([
        ('consu','Consumable'),
        ('service','Service')],string='ProductType',default='consu',required=True,
        help='Astorableproductisaproductforwhichyoumanagestock.TheInventoryapphastobeinstalled.\n'
             'Aconsumableproductisaproductforwhichstockisnotmanaged.\n'
             'Aserviceisanon-materialproductyouprovide.')
    categ_id=fields.Many2one(
        'product.category','ProductCategory',
        change_default=True,default=_get_default_category_id,group_expand='_read_group_categ_id',
        required=True,help="Selectcategoryforthecurrentproduct")

    currency_id=fields.Many2one(
        'res.currency','Currency',compute='_compute_currency_id')
    cost_currency_id=fields.Many2one(
        'res.currency','CostCurrency',compute='_compute_cost_currency_id')

    #pricefields
    #price:totaltemplateprice,contextdependent(partner,pricelist,quantity)
    price=fields.Float(
        'Price',compute='_compute_template_price',inverse='_set_template_price',
        digits='ProductPrice')
    #list_price:catalogprice,userdefined
    list_price=fields.Float(
        'SalesPrice',default=1.0,
        digits='ProductPrice',
        help="Priceatwhichtheproductissoldtocustomers.")
    #lst_price:catalogpricefortemplate,butincludingextraforvariants
    lst_price=fields.Float(
        'PublicPrice',related='list_price',readonly=False,
        digits='ProductPrice')
    standard_price=fields.Float(
        'Cost',compute='_compute_standard_price',
        inverse='_set_standard_price',search='_search_standard_price',
        digits='ProductPrice',groups="base.group_user",
        help="""InStandardPrice&AVCO:valueoftheproduct(automaticallycomputedinAVCO).
        InFIFO:valueofthenextunitthatwillleavethestock(automaticallycomputed).
        Usedtovaluetheproductwhenthepurchasecostisnotknown(e.g.inventoryadjustment).
        Usedtocomputemarginsonsaleorders.""")

    volume=fields.Float(
        'Volume',compute='_compute_volume',inverse='_set_volume',digits='Volume',store=True)
    volume_uom_name=fields.Char(string='Volumeunitofmeasurelabel',compute='_compute_volume_uom_name')
    weight=fields.Float(
        'Weight',compute='_compute_weight',digits='StockWeight',
        inverse='_set_weight',store=True)
    weight_uom_name=fields.Char(string='Weightunitofmeasurelabel',compute='_compute_weight_uom_name')

    sale_ok=fields.Boolean('CanbeSold',default=True)
    purchase_ok=fields.Boolean('CanbePurchased',default=True)
    pricelist_id=fields.Many2one(
        'product.pricelist','Pricelist',store=False,
        help='Technicalfield.Usedforsearchingonpricelists,notstoredindatabase.')
    uom_id=fields.Many2one(
        'uom.uom','UnitofMeasure',
        default=_get_default_uom_id,required=True,
        help="Defaultunitofmeasureusedforallstockoperations.")
    uom_name=fields.Char(string='UnitofMeasureName',related='uom_id.name',readonly=True)
    uom_po_id=fields.Many2one(
        'uom.uom','PurchaseUnitofMeasure',
        default=_get_default_uom_po_id,required=True,
        help="Defaultunitofmeasureusedforpurchaseorders.Itmustbeinthesamecategoryasthedefaultunitofmeasure.")
    company_id=fields.Many2one(
        'res.company','Company',index=1)
    packaging_ids=fields.One2many(
        'product.packaging',string="ProductPackages",compute="_compute_packaging_ids",inverse="_set_packaging_ids",
        help="Givesthedifferentwaystopackagethesameproduct.")
    seller_ids=fields.One2many('product.supplierinfo','product_tmpl_id','Vendors',depends_context=('company',),help="Definevendorpricelists.")
    variant_seller_ids=fields.One2many('product.supplierinfo','product_tmpl_id')

    active=fields.Boolean('Active',default=True,help="Ifunchecked,itwillallowyoutohidetheproductwithoutremovingit.")
    color=fields.Integer('ColorIndex')

    is_product_variant=fields.Boolean(string='Isaproductvariant',compute='_compute_is_product_variant')
    attribute_line_ids=fields.One2many('product.template.attribute.line','product_tmpl_id','ProductAttributes',copy=True)

    valid_product_template_attribute_line_ids=fields.Many2many('product.template.attribute.line',
        compute="_compute_valid_product_template_attribute_line_ids",string='ValidProductAttributeLines',help="Technicalcompute")

    product_variant_ids=fields.One2many('product.product','product_tmpl_id','Products',required=True)
    #performance:product_variant_idprovidesprefetchingonthefirstproductvariantonly
    product_variant_id=fields.Many2one('product.product','Product',compute='_compute_product_variant_id')

    product_variant_count=fields.Integer(
        '#ProductVariants',compute='_compute_product_variant_count')

    #relatedtodisplayproductproductinformationifis_product_variant
    barcode=fields.Char('Barcode',compute='_compute_barcode',inverse='_set_barcode',search='_search_barcode')
    default_code=fields.Char(
        'InternalReference',compute='_compute_default_code',
        inverse='_set_default_code',store=True)

    pricelist_item_count=fields.Integer("Numberofpricerules",compute="_compute_item_count")

    can_image_1024_be_zoomed=fields.Boolean("CanImage1024bezoomed",compute='_compute_can_image_1024_be_zoomed',store=True)
    has_configurable_attributes=fields.Boolean("Isaconfigurableproduct",compute='_compute_has_configurable_attributes',store=True)

    def_compute_item_count(self):
        fortemplateinself:
            #Pricelistitemcountcountstherulesapplicableoncurrenttemplateoronitsvariants.
            template.pricelist_item_count=template.env['product.pricelist.item'].search_count([
                '|',('product_tmpl_id','=',template.id),('product_id','in',template.product_variant_ids.ids)])

    @api.depends('image_1920','image_1024')
    def_compute_can_image_1024_be_zoomed(self):
        fortemplateinself:
            template.can_image_1024_be_zoomed=template.image_1920andtools.is_image_size_above(template.image_1920,template.image_1024)

    @api.depends('attribute_line_ids','attribute_line_ids.value_ids','attribute_line_ids.attribute_id.create_variant')
    def_compute_has_configurable_attributes(self):
        """Aproductisconsideredconfigurableif:
        -Ithasdynamicattributes
        -Ithasanyattributelinewithatleast2attributevaluesconfigured
        """
        forproductinself:
            product.has_configurable_attributes=product.has_dynamic_attributes()orany(len(ptal.value_ids)>=2forptalinproduct.attribute_line_ids)

    @api.depends('product_variant_ids')
    def_compute_product_variant_id(self):
        forpinself:
            p.product_variant_id=p.product_variant_ids[:1].id

    @api.depends('company_id')
    def_compute_currency_id(self):
        main_company=self.env['res.company']._get_main_company()
        fortemplateinself:
            template.currency_id=template.company_id.sudo().currency_id.idormain_company.currency_id.id

    @api.depends_context('company')
    def_compute_cost_currency_id(self):
        self.cost_currency_id=self.env.company.currency_id.id

    def_compute_template_price(self):
        prices=self._compute_template_price_no_inverse()
        fortemplateinself:
            template.price=prices.get(template.id,0.0)

    def_compute_template_price_no_inverse(self):
        """The_compute_template_pricewritesthe'list_price'fieldwithaninversemethod
        Thismethodallowscomputingthepricewithoutwritingthe'list_price'
        """
        prices={}
        pricelist_id_or_name=self._context.get('pricelist')
        ifpricelist_id_or_name:
            pricelist=None
            partner=self.env.context.get('partner')
            quantity=self.env.context.get('quantity',1.0)

            #Supportcontextpricelistsspecifiedaslist,display_nameorIDforcompatibility
            ifisinstance(pricelist_id_or_name,list):
                pricelist_id_or_name=pricelist_id_or_name[0]
            ifisinstance(pricelist_id_or_name,str):
                pricelist_data=self.env['product.pricelist'].name_search(pricelist_id_or_name,operator='=',limit=1)
                ifpricelist_data:
                    pricelist=self.env['product.pricelist'].browse(pricelist_data[0][0])
            elifisinstance(pricelist_id_or_name,int):
                pricelist=self.env['product.pricelist'].browse(pricelist_id_or_name)

            ifpricelist:
                quantities=[quantity]*len(self)
                partners=[partner]*len(self)
                prices=pricelist.get_products_price(self,quantities,partners)

        returnprices

    def_set_template_price(self):
        ifself._context.get('uom'):
            fortemplateinself:
                value=self.env['uom.uom'].browse(self._context['uom'])._compute_price(template.price,template.uom_id)
                template.write({'list_price':value})
        else:
            self.write({'list_price':self.price})

    @api.depends_context('company')
    @api.depends('product_variant_ids','product_variant_ids.standard_price')
    def_compute_standard_price(self):
        #Dependsonforce_companycontextbecausestandard_priceiscompany_dependent
        #ontheproduct_product
        unique_variants=self.filtered(lambdatemplate:len(template.product_variant_ids)==1)
        fortemplateinunique_variants:
            template.standard_price=template.product_variant_ids.standard_price
        fortemplatein(self-unique_variants):
            template.standard_price=0.0

    def_set_standard_price(self):
        fortemplateinself:
            iflen(template.product_variant_ids)==1:
                template.product_variant_ids.standard_price=template.standard_price

    def_search_standard_price(self,operator,value):
        products=self.env['product.product'].search([('standard_price',operator,value)],limit=None)
        return[('id','in',products.mapped('product_tmpl_id').ids)]

    @api.depends('product_variant_ids','product_variant_ids.volume')
    def_compute_volume(self):
        unique_variants=self.filtered(lambdatemplate:len(template.product_variant_ids)==1)
        fortemplateinunique_variants:
            template.volume=template.product_variant_ids.volume
        fortemplatein(self-unique_variants):
            template.volume=0.0

    def_set_volume(self):
        fortemplateinself:
            iflen(template.product_variant_ids)==1:
                template.product_variant_ids.volume=template.volume

    @api.depends('product_variant_ids','product_variant_ids.weight')
    def_compute_weight(self):
        unique_variants=self.filtered(lambdatemplate:len(template.product_variant_ids)==1)
        fortemplateinunique_variants:
            template.weight=template.product_variant_ids.weight
        fortemplatein(self-unique_variants):
            template.weight=0.0

    def_compute_is_product_variant(self):
        self.is_product_variant=False

    @api.depends('product_variant_ids.barcode')
    def_compute_barcode(self):
        self.barcode=False
        fortemplateinself:
            #TODOmaster:updateproduct_variant_countdependsanduseitinstead
            variant_count=len(template.product_variant_ids)
            ifvariant_count==1:
                template.barcode=template.product_variant_ids.barcode
            elifvariant_count==0:
                archived_variants=template.with_context(active_test=False).product_variant_ids
                iflen(archived_variants)==1:
                    template.barcode=archived_variants.barcode

    def_search_barcode(self,operator,value):
        query=self.with_context(active_test=False)._search([('product_variant_ids.barcode',operator,value)])
        return[('id','in',query)]

    def_set_barcode(self):
        variant_count=len(self.product_variant_ids)
        ifvariant_count==1:
            self.product_variant_ids.barcode=self.barcode
        elifvariant_count==0:
            archived_variants=self.with_context(active_test=False).product_variant_ids
            iflen(archived_variants)==1:
                archived_variants.barcode=self.barcode

    @api.model
    def_get_weight_uom_id_from_ir_config_parameter(self):
        """Gettheunitofmeasuretointerpretthe`weight`field.Bydefault,weconsiderer
        thatweightsareexpressedinkilograms.Userscanconfiguretoexpresstheminpounds
        byaddinganir.config_parameterrecordwith"product.product_weight_in_lbs"askey
        and"1"asvalue.
        """
        product_weight_in_lbs_param=self.env['ir.config_parameter'].sudo().get_param('product.weight_in_lbs')
        ifproduct_weight_in_lbs_param=='1':
            returnself.env.ref('uom.product_uom_lb')
        else:
            returnself.env.ref('uom.product_uom_kgm')

    @api.model
    def_get_length_uom_id_from_ir_config_parameter(self):
        """Gettheunitofmeasuretointerpretthe`length`,'width','height'field.
        Bydefault,weconsidererthatlengthareexpressedinmeters.Userscanconfigure
        toexpresstheminfeetbyaddinganir.config_parameterrecordwith"product.volume_in_cubic_feet"
        askeyand"1"asvalue.
        """
        product_length_in_feet_param=self.env['ir.config_parameter'].sudo().get_param('product.volume_in_cubic_feet')
        ifproduct_length_in_feet_param=='1':
            returnself.env.ref('uom.product_uom_foot')
        else:
            returnself.env.ref('uom.product_uom_meter')

    @api.model
    def_get_volume_uom_id_from_ir_config_parameter(self):
        """Gettheunitofmeasuretointerpretthe`volume`field.Bydefault,weconsider
        thatvolumesareexpressedincubicmeters.Userscanconfiguretoexpressthemincubicfeet
        byaddinganir.config_parameterrecordwith"product.volume_in_cubic_feet"askey
        and"1"asvalue.
        """
        product_length_in_feet_param=self.env['ir.config_parameter'].sudo().get_param('product.volume_in_cubic_feet')
        ifproduct_length_in_feet_param=='1':
            returnself.env.ref('uom.product_uom_cubic_foot')
        else:
            returnself.env.ref('uom.product_uom_cubic_meter')

    @api.model
    def_get_weight_uom_name_from_ir_config_parameter(self):
        returnself._get_weight_uom_id_from_ir_config_parameter().display_name

    @api.model
    def_get_length_uom_name_from_ir_config_parameter(self):
        returnself._get_length_uom_id_from_ir_config_parameter().display_name

    @api.model
    def_get_volume_uom_name_from_ir_config_parameter(self):
        returnself._get_volume_uom_id_from_ir_config_parameter().display_name

    def_compute_weight_uom_name(self):
        self.weight_uom_name=self._get_weight_uom_name_from_ir_config_parameter()

    def_compute_volume_uom_name(self):
        self.volume_uom_name=self._get_volume_uom_name_from_ir_config_parameter()

    def_set_weight(self):
        fortemplateinself:
            iflen(template.product_variant_ids)==1:
                template.product_variant_ids.weight=template.weight

    @api.depends('product_variant_ids.product_tmpl_id')
    def_compute_product_variant_count(self):
        fortemplateinself:
            #donotpollutevariantstobeprefetchedwhencountingvariants
            template.product_variant_count=len(template.with_prefetch().product_variant_ids)

    @api.depends('product_variant_ids','product_variant_ids.default_code')
    def_compute_default_code(self):
        unique_variants=self.filtered(lambdatemplate:len(template.product_variant_ids)==1)
        fortemplateinunique_variants:
            template.default_code=template.product_variant_ids.default_code
        fortemplatein(self-unique_variants):
            template.default_code=False

    def_set_default_code(self):
        fortemplateinself:
            iflen(template.product_variant_ids)==1:
                template.product_variant_ids.default_code=template.default_code

    @api.depends('product_variant_ids','product_variant_ids.packaging_ids')
    def_compute_packaging_ids(self):
        forpinself:
            iflen(p.product_variant_ids)==1:
                p.packaging_ids=p.product_variant_ids.packaging_ids
            else:
                p.packaging_ids=False

    def_set_packaging_ids(self):
        forpinself:
            iflen(p.product_variant_ids)==1:
                p.product_variant_ids.packaging_ids=p.packaging_ids

    @api.constrains('uom_id','uom_po_id')
    def_check_uom(self):
        ifany(template.uom_idandtemplate.uom_po_idandtemplate.uom_id.category_id!=template.uom_po_id.category_idfortemplateinself):
            raiseValidationError(_('ThedefaultUnitofMeasureandthepurchaseUnitofMeasuremustbeinthesamecategory.'))
        returnTrue

    @api.onchange('uom_id')
    def_onchange_uom_id(self):
        ifself.uom_id:
            self.uom_po_id=self.uom_id.id

    @api.onchange('uom_po_id')
    def_onchange_uom(self):
        ifself.uom_idandself.uom_po_idandself.uom_id.category_id!=self.uom_po_id.category_id:
            self.uom_po_id=self.uom_id

    @api.onchange('type')
    def_onchange_type(self):
        #Donothingbutneededforinheritance
        return{}

    @api.model_create_multi
    defcreate(self,vals_list):
        '''Storetheinitialstandardpriceinordertobeabletoretrievethecostofaproducttemplateforagivendate'''
        templates=super(ProductTemplate,self).create(vals_list)
        if"create_product_product"notinself._context:
            templates._create_variant_ids()

        #Thisisneededtosetgivenvaluestofirstvariantaftercreation
        fortemplate,valsinzip(templates,vals_list):
            related_vals={}
            ifvals.get('barcode'):
                related_vals['barcode']=vals['barcode']
            ifvals.get('default_code'):
                related_vals['default_code']=vals['default_code']
            ifvals.get('standard_price'):
                related_vals['standard_price']=vals['standard_price']
            ifvals.get('volume'):
                related_vals['volume']=vals['volume']
            ifvals.get('weight'):
                related_vals['weight']=vals['weight']
            #Pleasedoforwardport
            ifvals.get('packaging_ids'):
                related_vals['packaging_ids']=vals['packaging_ids']
            ifrelated_vals:
                template.write(related_vals)

        returntemplates

    defwrite(self,vals):
        if'uom_id'invalsor'uom_po_id'invals:
            uom_id=self.env['uom.uom'].browse(vals.get('uom_id'))orself.uom_id
            uom_po_id=self.env['uom.uom'].browse(vals.get('uom_po_id'))orself.uom_po_id
            ifuom_idanduom_po_idanduom_id.category_id!=uom_po_id.category_id:
                vals['uom_po_id']=uom_id.id
        res=super(ProductTemplate,self).write(vals)
        if'attribute_line_ids'invalsor(vals.get('active')andlen(self.product_variant_ids)==0):
            self._create_variant_ids()
        if'active'invalsandnotvals.get('active'):
            self.with_context(active_test=False).mapped('product_variant_ids').write({'active':vals.get('active')})
        if'image_1920'invals:
            self.env['product.product'].invalidate_cache(fnames=[
                'image_1920',
                'image_1024',
                'image_512',
                'image_256',
                'image_128',
                'can_image_1024_be_zoomed',
            ])
        returnres

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        #TDEFIXME:shouldprobablybecopy_data
        self.ensure_one()
        ifdefaultisNone:
            default={}
        if'name'notindefault:
            default['name']=_("%s(copy)",self.name)
        returnsuper(ProductTemplate,self).copy(default=default)

    defname_get(self):
        #Prefetchthefieldsusedbythe`name_get`,so`browse`doesn'tfetchotherfields
        self.browse(self.ids).read(['name','default_code'])
        return[(template.id,'%s%s'%(template.default_codeand'[%s]'%template.default_codeor'',template.name))
                fortemplateinself]

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        #Onlyusetheproduct.productheuristicsifthereisasearchtermandthedomain
        #doesnotspecifyamatchon`product.template`IDs.
        ifnotnameorany(term[0]=='id'fortermin(argsor[])):
            returnsuper(ProductTemplate,self)._name_search(name=name,args=args,operator=operator,limit=limit,name_get_uid=name_get_uid)

        Product=self.env['product.product']
        templates=self.browse([])
        whileTrue:
            domain=templatesand[('product_tmpl_id','notin',templates.ids)]or[]
            args=argsifargsisnotNoneelse[]
            #Product._name_searchhasdefaultvaluelimit=100
            #So,weeitherusethatvalueoroverrideittoNonetofetchallproductsatonce
            kwargs={}iflimitelse{'limit':None}
            products_ids=Product._name_search(name,args+domain,operator=operator,name_get_uid=name_get_uid,**kwargs)
            products=Product.browse(products_ids)
            new_templates=products.mapped('product_tmpl_id')
            ifnew_templates&templates:
                """Product._name_searchcanbypassthedomainwepassed(searchonsupplierinfo).
                   Ifthishappens,aninfiniteloopwilloccur."""
                break
            templates|=new_templates
            if(notproducts)or(limitand(len(templates)>limit)):
                break

        searched_ids=set(templates.ids)
        #someproduct.templatesdonothaveproduct.productsyet(dynamicvariantsconfiguration),
        #weneedtoaddthebase_name_searchtotheresults
        #FIXMEawa:thisisreallynotperformantatallbutafterdiscussingwiththeteam
        #wedon'tseeanotherwaytodoit
        tmpl_without_variant_ids=[]
        ifnotlimitorlen(searched_ids)<limit:
            tmpl_without_variant_ids=self.env['product.template'].search(
                [('id','notin',self.env['product.template']._search([('product_variant_ids.active','=',True)]))]
            )
        iftmpl_without_variant_ids:
            domain=expression.AND([argsor[],[('id','in',tmpl_without_variant_ids.ids)]])
            searched_ids|=set(super(ProductTemplate,self)._name_search(
                    name,
                    args=domain,
                    operator=operator,
                    limit=limit,
                    name_get_uid=name_get_uid))

        #re-applyproduct.templateorder+name_get
        returnsuper(ProductTemplate,self)._name_search(
            '',args=[('id','in',list(searched_ids))],
            operator='ilike',limit=limit,name_get_uid=name_get_uid)

    defopen_pricelist_rules(self):
        self.ensure_one()
        domain=['|',
            ('product_tmpl_id','=',self.id),
            ('product_id','in',self.product_variant_ids.ids)]
        return{
            'name':_('PriceRules'),
            'view_mode':'tree,form',
            'views':[(self.env.ref('product.product_pricelist_item_tree_view_from_product').id,'tree'),(False,'form')],
            'res_model':'product.pricelist.item',
            'type':'ir.actions.act_window',
            'target':'current',
            'domain':domain,
            'context':{
                'default_product_tmpl_id':self.id,
                'default_applied_on':'1_product',
                'product_without_variants':self.product_variant_count==1,
            },
        }

    defprice_compute(self,price_type,uom=False,currency=False,company=None):
        #TDEFIXME:delegatetotemplateornot?fieldsarereencodedhere...
        #compatibilityaboutcontextkeysusedabiteverywhereinthecode
        ifnotuomandself._context.get('uom'):
            uom=self.env['uom.uom'].browse(self._context['uom'])
        ifnotcurrencyandself._context.get('currency'):
            currency=self.env['res.currency'].browse(self._context['currency'])

        templates=self
        ifprice_type=='standard_price':
            #standard_pricefieldcanonlybeseenbyusersinbase.group_user
            #Thus,inordertocomputethesalepricefromthecostforusersnotinthisgroup
            #Wefetchthestandardpriceasthesuperuser
            templates=self.with_company(company).sudo()
        ifnotcompany:
            company=self.env.company
        date=self.env.context.get('date')orfields.Date.today()

        prices=dict.fromkeys(self.ids,0.0)
        fortemplateintemplates:
            prices[template.id]=template[price_type]or0.0
            #yes,therecanbeattributevaluesforproducttemplateifit'snotavariantYET
            #(seefieldproduct.attributecreate_variant)
            ifprice_type=='list_price'andself._context.get('current_attributes_price_extra'):
                #wehavealistofprice_extrathatcomesfromtheattributevalues,weneedtosumallthat
                prices[template.id]+=sum(self._context.get('current_attributes_price_extra'))

            ifuom:
                prices[template.id]=template.uom_id._compute_price(prices[template.id],uom)

            #Convertfromcurrentusercompanycurrencytoaskedone
            #Thisisrightcauseafieldcannotbeinmorethanonecurrency
            ifcurrency:
                prices[template.id]=template.currency_id._convert(prices[template.id],currency,company,date)

        returnprices

    def_create_variant_ids(self):
        self.flush()
        Product=self.env["product.product"]

        variants_to_create=[]
        variants_to_activate=Product
        variants_to_unlink=Product

        fortmpl_idinself:
            lines_without_no_variants=tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes()

            all_variants=tmpl_id.with_context(active_test=False).product_variant_ids.sorted(lambdap:(p.active,-p.id))

            current_variants_to_create=[]
            current_variants_to_activate=Product

            #addinganattributewithonlyonevalueshouldnotrecreateproduct
            #writethisattributeoneveryproducttomakesurewedon'tlosethem
            single_value_lines=lines_without_no_variants.filtered(lambdaptal:len(ptal.product_template_value_ids._only_active())==1)
            ifsingle_value_lines:
                forvariantinall_variants:
                    combination=variant.product_template_attribute_value_ids|single_value_lines.product_template_value_ids._only_active()
                    #Donotaddsinglevalueiftheresultingcombinationwould
                    #beinvalidanyway.
                    if(
                        len(combination)==len(lines_without_no_variants)and
                        combination.attribute_line_id==lines_without_no_variants
                    ):
                        variant.product_template_attribute_value_ids=combination

            #Setcontainingexisting`product.template.attribute.value`combination
            existing_variants={
                variant.product_template_attribute_value_ids:variantforvariantinall_variants
            }

            #Determinewhichproductvariantsneedtobecreatedbasedontheattribute
            #configuration.Ifanyattributeissettogeneratevariantsdynamically,skipthe
            #process.
            #Technicalnote:ifthereisnoattribute,avariantisstillcreatedbecause
            #'notany([])'and'set([])notinset([])'areTrue.
            ifnottmpl_id.has_dynamic_attributes():
                #Iteratorcontainingallpossible`product.template.attribute.value`combination
                #TheiteratorisusedtoavoidMemoryErrorincaseofahugenumberofcombination.
                all_combinations=itertools.product(*[
                    ptal.product_template_value_ids._only_active()forptalinlines_without_no_variants
                ])
                #Foreachpossiblevariant,createifitdoesn'texistyet.
                forcombination_tupleinall_combinations:
                    combination=self.env['product.template.attribute.value'].concat(*combination_tuple)
                    is_combination_possible=tmpl_id._is_combination_possible_by_config(combination,ignore_no_variant=True)
                    ifnotis_combination_possible:
                        continue
                    ifcombinationinexisting_variants:
                        current_variants_to_activate+=existing_variants[combination]
                    else:
                        current_variants_to_create.append({
                            'product_tmpl_id':tmpl_id.id,
                            'product_template_attribute_value_ids':[(6,0,combination.ids)],
                            'active':tmpl_id.active,
                        })
                        iflen(current_variants_to_create)>1000:
                            raiseUserError(_(
                                'Thenumberofvariantstogenerateistoohigh.'
                                'Youshouldeithernotgeneratevariantsforeachcombinationorgeneratethemondemandfromthesalesorder.'
                                'Todoso,opentheformviewofattributesandchangethemodeof*CreateVariants*.'))
                variants_to_create+=current_variants_to_create
                variants_to_activate+=current_variants_to_activate

            else:
                forvariantinexisting_variants.values():
                    is_combination_possible=self._is_combination_possible_by_config(
                        combination=variant.product_template_attribute_value_ids,
                        ignore_no_variant=True,
                    )
                    ifis_combination_possible:
                        current_variants_to_activate+=variant
                variants_to_activate+=current_variants_to_activate

            variants_to_unlink+=all_variants-current_variants_to_activate

        ifvariants_to_activate:
            variants_to_activate.write({'active':True})
        ifvariants_to_create:
            Product.create(variants_to_create)
        ifvariants_to_unlink:
            variants_to_unlink._unlink_or_archive()
            #preventchangeifexclusiondeletedtemplatebydeletinglastvariant
            ifself.exists()!=self:
                raiseUserError(_("Thisconfigurationofproductattributes,values,andexclusionswouldleadtonopossiblevariant.Pleasearchiveordeleteyourproductdirectlyifintended."))

        #prefetchedo2mhavetobereloaded(becauseofactive_test)
        #(eg.product.template:product_variant_ids)
        #Wecan'trelyonexistinginvalidate_cachebecauseofthesavepoint
        #in_unlink_or_archive.
        self.flush()
        self.invalidate_cache()
        returnTrue

    defhas_dynamic_attributes(self):
        """Returnwhetherthis`product.template`hasatleastonedynamic
        attribute.

        :return:Trueifatleastonedynamicattribute,Falseotherwise
        :rtype:bool
        """
        self.ensure_one()
        returnany(a.create_variant=='dynamic'forainself.valid_product_template_attribute_line_ids.attribute_id)

    @api.depends('attribute_line_ids.value_ids')
    def_compute_valid_product_template_attribute_line_ids(self):
        """Aproducttemplateattributelineisconsideredvalidifithasat
        leastonepossiblevalue.

        Thosewithonlyonevalueareconsideredvalid,eventhoughtheyshould
        notappearontheconfiguratoritself(unlesstheyhaveanis_custom
        valuetoinput),indeedsinglevalueattributescanbeusedtofilter
        productsamongothersbasedonthatattribute/value.
        """
        forrecordinself:
            record.valid_product_template_attribute_line_ids=record.attribute_line_ids.filtered(lambdaptal:ptal.value_ids)

    def_get_possible_variants(self,parent_combination=None):
        """Returntheexistingvariantsthatarepossible.

        Fordynamicattributes,itwillonlyreturnthevariantsthathavebeen
        createdalready.

        Iftherearealotofvariants,thismethodmightbeslow.Evenifthere
        aren'ttoomanyvariants,forperformancereasons,donotcallthis
        methodinaloopovertheproducttemplates.

        Thereforethismethodhasaveryrestrictedreasonableusecaseandyou
        shouldstronglyconsiderdoingthingsdifferentlyifyouconsiderusing
        thismethod.

        :paramparent_combination:combinationfromwhich`self`isan
            optionaloraccessoryproduct.
        :typeparent_combination:recordset`product.template.attribute.value`

        :return:theexistingvariantsthatarepossible.
        :rtype:recordsetof`product.product`
        """
        self.ensure_one()
        returnself.product_variant_ids.filtered(lambdap:p._is_variant_possible(parent_combination))

    def_get_attribute_exclusions(self,parent_combination=None,parent_name=None):
        """Returnthelistofattributeexclusionsofaproduct.

        :paramparent_combination:thecombinationfromwhich
            `self`isanoptionaloraccessoryproduct.Indeedexclusions
            rulesononeproductcanconcernanotherproduct.
        :typeparent_combination:recordset`product.template.attribute.value`
        :paramparent_name:thenameoftheparentproductcombination.
        :typeparent_name:str

        :return:dictofexclusions
            -exclusions:fromthisproductitself
            -parent_combination:idsofthegivenparent_combination
            -parent_exclusions:fromtheparent_combination
           -parent_product_name:thenameoftheparentproductifany,usedintheinterface
               toexplainwhysomecombinationsarenotavailable.
               (e.g:NotavailablewithCustomizableDesk(Legs:Steel))
           -mapped_attribute_names:thenameofeveryattributevaluesbasedontheirid,
               usedtoexplainintheinterfacewhythatcombinationisnotavailable
               (e.g:NotavailablewithColor:Black)
        """
        self.ensure_one()
        parent_combination=parent_combinationorself.env['product.template.attribute.value']
        return{
            'exclusions':self._complete_inverse_exclusions(self._get_own_attribute_exclusions()),
            'parent_exclusions':self._get_parent_attribute_exclusions(parent_combination),
            'parent_combination':parent_combination.ids,
            'parent_product_name':parent_name,
            'mapped_attribute_names':self._get_mapped_attribute_names(parent_combination),
        }

    @api.model
    def_complete_inverse_exclusions(self,exclusions):
        """Willcompletethedictionnaryofexclusionswiththeirrespectiveinverse
        e.g:BlackexcludesXLandL
        ->XLexcludesBlack
        ->LexcludesBlack"""
        result=dict(exclusions)
        forkey,valueinexclusions.items():
            forexclusioninvalue:
                ifexclusioninresultandkeynotinresult[exclusion]:
                    result[exclusion].append(key)
                else:
                    result[exclusion]=[key]

        returnresult

    def_get_own_attribute_exclusions(self):
        """Getexclusionscomingfromthecurrenttemplate.

        Dictionnary,eachproducttemplateattributevalueisakey,andforeachofthem
        thevalueisanarraywiththeotherptavthattheyexclude(emptyifnoexclusion).
        """
        self.ensure_one()
        product_template_attribute_values=self.valid_product_template_attribute_line_ids.product_template_value_ids
        return{
            ptav.id:[
                value_id
                forfilter_lineinptav.exclude_for.filtered(
                    lambdafilter_line:filter_line.product_tmpl_id==self
                )forvalue_idinfilter_line.value_ids.ids
            ]
            forptavinproduct_template_attribute_values
        }

    def_get_parent_attribute_exclusions(self,parent_combination):
        """Getexclusionscomingfromtheparentcombination.

        Dictionnary,eachparent'sptavisakey,andforeachofthemthevalueis
        anarraywiththeotherptavthatareexcludedbecauseoftheparent.
        """
        self.ensure_one()
        ifnotparent_combination:
            return{}

        result={}
        forproduct_attribute_valueinparent_combination:
            forfilter_lineinproduct_attribute_value.exclude_for.filtered(
                lambdafilter_line:filter_line.product_tmpl_id==self
            ):
                #Someexclusionsdon'thaveattributevalue.Thismeansthatthetemplateisnot
                #compatiblewiththeparentcombination.Ifsuchanexclusionisfound,itmeansthatall
                #attributevaluesareexcluded.
                iffilter_line.value_ids:
                    result[product_attribute_value.id]=filter_line.value_ids.ids
                else:
                    result[product_attribute_value.id]=filter_line.product_tmpl_id.mapped('attribute_line_ids.product_template_value_ids').ids

        returnresult

    def_get_mapped_attribute_names(self,parent_combination=None):
        """Thenameofeveryattributevaluesbasedontheirid,
        usedtoexplainintheinterfacewhythatcombinationisnotavailable
        (e.g:NotavailablewithColor:Black).

        Itcontainsbothattributevaluenamesfromthisproductandfrom
        theparentcombinationifprovided.
        """
        self.ensure_one()
        all_product_attribute_values=self.valid_product_template_attribute_line_ids.product_template_value_ids
        ifparent_combination:
            all_product_attribute_values|=parent_combination

        return{
            attribute_value.id:attribute_value.display_name
            forattribute_valueinall_product_attribute_values
        }

    def_is_combination_possible_by_config(self,combination,ignore_no_variant=False):
        """Returnwhetherthegivencombinationispossibleaccordingtotheconfigofattributesonthetemplate

        :paramcombination:thecombinationtocheckforpossibility
        :typecombination:recordset`product.template.attribute.value`

        :paramignore_no_variant:whetherno_variantattributesshouldbeignored
        :typeignore_no_variant:bool

        :return:wetherthegivencombinationispossibleaccordingtotheconfigofattributesonthetemplate
        :rtype:bool
        """
        self.ensure_one()

        attribute_lines=self.valid_product_template_attribute_line_ids

        ifignore_no_variant:
            attribute_lines=attribute_lines._without_no_variant_attributes()

        iflen(combination)!=len(attribute_lines):
            #numberofattributevaluespassedisdifferentthanthe
            #configurationofattributesonthetemplate
            returnFalse

        ifattribute_lines!=combination.attribute_line_id:
            #combinationhasdifferentattributesthantheonesconfiguredonthetemplate
            returnFalse

        ifnot(attribute_lines.product_template_value_ids._only_active()>=combination):
            #combinationhasdifferentvaluesthantheonesconfiguredonthetemplate
            returnFalse

        exclusions=self._get_own_attribute_exclusions()
        ifexclusions:
            #excludeifthecurrentvalueisinanexclusion,
            #andthevalueexcludingitisalsointhecombination
            forptavincombination:
                forexclusioninexclusions.get(ptav.id):
                    ifexclusionincombination.ids:
                        returnFalse

        returnTrue

    def_is_combination_possible(self,combination,parent_combination=None,ignore_no_variant=False):
        """
        Thecombinationispossibleifitisnotexcludedbyanyrule
        comingfromthecurrenttemplate,notexcludedbyanyrulefromthe
        parent_combination(ifgiven),andthereshouldnotbeanyarchived
        variantwiththeexactsamecombination.

        Ifthetemplatedoesnothaveanydynamicattribute,thecombination
        isalsonotpossibleifthematchingvarianthasbeendeleted.

        Moreovertheattributesofthecombinationmustexcatlymatchthe
        attributesallowedonthetemplate.

        :paramcombination:thecombinationtocheckforpossibility
        :typecombination:recordset`product.template.attribute.value`

        :paramignore_no_variant:whetherno_variantattributesshouldbeignored
        :typeignore_no_variant:bool

        :paramparent_combination:combinationfromwhich`self`isan
            optionaloraccessoryproduct.
        :typeparent_combination:recordset`product.template.attribute.value`

        :return:whetherthecombinationispossible
        :rtype:bool
        """
        self.ensure_one()

        ifnotself._is_combination_possible_by_config(combination,ignore_no_variant):
            returnFalse

        variant=self._get_variant_for_combination(combination)

        ifself.has_dynamic_attributes():
            ifvariantandnotvariant.active:
                #dynamicandthevarianthasbeenarchived
                returnFalse
        else:
            ifnotvariantornotvariant.active:
                #notdynamic,thevarianthasbeenarchivedordeleted
                returnFalse

        parent_exclusions=self._get_parent_attribute_exclusions(parent_combination)
        ifparent_exclusions:
            #parent_exclusionaremappedbyptavbutherewedon'tneedtoknow
            #wheretheexclusioncomesfromsoweloopdirectlyonthedictvalues
            forexclusions_valuesinparent_exclusions.values():
                forexclusioninexclusions_values:
                    ifexclusionincombination.ids:
                        returnFalse

        returnTrue

    def_get_variant_for_combination(self,combination):
        """Getthevariantmatchingthecombination.

        Allofthevaluesincombinationmustbepresentinthevariant,andthe
        variantshouldnothavemoreattributes.Ignoretheattributesthatare
        notsupposedtocreatevariants.

        :paramcombination:recordsetof`product.template.attribute.value`

        :return:thevariantiffound,elseempty
        :rtype:recordset`product.product`
        """
        self.ensure_one()
        filtered_combination=combination._without_no_variant_attributes()
        returnself.env['product.product'].browse(self._get_variant_id_for_combination(filtered_combination))

    def_create_product_variant(self,combination,log_warning=False):
        """Createifnecessaryandpossibleandreturntheproductvariant
        matchingthegivencombinationforthistemplate.

        Itispossibletocreateonlyifthetemplatehasdynamicattributes
        andthecombinationitselfispossible.
        Ifweareinthiscaseandthevariantalreadyexistsbutitis
        archived,itisactivatedinsteadofbeingcreatedagain.

        :paramcombination:thecombinationforwhichtogetorcreatevariant.
            Thecombinationmustcontainallnecessaryattributes,including
            thoseoftypeno_variant.Indeedeventhoughthoseattributeswon't
            beincludedinthevariantifnewlycreated,theyareneededwhen
            checkingifthecombinationispossible.
        :typecombination:recordsetof`product.template.attribute.value`

        :paramlog_warning:whetherawarningshouldbeloggedonfail
        :typelog_warning:bool

        :return:theproductvariantmatchingthecombinationornone
        :rtype:recordsetof`product.product`
        """
        self.ensure_one()

        Product=self.env['product.product']

        product_variant=self._get_variant_for_combination(combination)
        ifproduct_variant:
            ifnotproduct_variant.activeandself.has_dynamic_attributes()andself._is_combination_possible(combination):
                product_variant.active=True
            returnproduct_variant

        ifnotself.has_dynamic_attributes():
            iflog_warning:
                _logger.warning('Theuser#%striedtocreateavariantforthenon-dynamicproduct%s.'%(self.env.user.id,self.id))
            returnProduct

        ifnotself._is_combination_possible(combination):
            iflog_warning:
                _logger.warning('Theuser#%striedtocreateaninvalidvariantfortheproduct%s.'%(self.env.user.id,self.id))
            returnProduct

        returnProduct.sudo().create({
            'product_tmpl_id':self.id,
            'product_template_attribute_value_ids':[(6,0,combination._without_no_variant_attributes().ids)]
        })

    def_create_first_product_variant(self,log_warning=False):
        """Createifnecessaryandpossibleandreturnthefirstproduct
        variantforthistemplate.

        :paramlog_warning:whetherawarningshouldbeloggedonfail
        :typelog_warning:bool

        :return:thefirstproductvariantornone
        :rtype:recordsetof`product.product`
        """
        returnself._create_product_variant(self._get_first_possible_combination(),log_warning)

    @tools.ormcache('self.id','frozenset(filtered_combination.ids)')
    def_get_variant_id_for_combination(self,filtered_combination):
        """See`_get_variant_for_combination`.ThismethodreturnsanID
        soitcanbecached.

        Usesudobecausethesameresultshouldbecachedforallusers.
        """
        self.ensure_one()
        domain=[('product_tmpl_id','=',self.id)]
        combination_indices_ids=filtered_combination._ids2str()

        ifcombination_indices_ids:
            domain=expression.AND([domain,[('combination_indices','=',combination_indices_ids)]])
        else:
            domain=expression.AND([domain,[('combination_indices','in',['',False])]])

        returnself.env['product.product'].sudo().with_context(active_test=False).search(domain,order='activeDESC',limit=1).id

    @tools.ormcache('self.id')
    def_get_first_possible_variant_id(self):
        """See`_create_first_product_variant`.ThismethodreturnsanID
        soitcanbecached."""
        self.ensure_one()
        returnself._create_first_product_variant().id

    def_get_first_possible_combination(self,parent_combination=None,necessary_values=None):
        """See`_get_possible_combinations`(oneiteration).

        Thismethodreturnthesameresult(emptyrecordset)ifno
        combinationispossibleatallwhichwouldbeconsideredanegative
        result,oriftherearenoattributelinesonthetemplateinwhich
        casethe"emptycombination"isactuallyapossiblecombination.
        Thereforetheresultofthismethodwhenemptyshouldbetested
        with`_is_combination_possible`ifit'simportanttoknowifthe
        resultingemptycombinationisactuallypossibleornot.
        """
        returnnext(self._get_possible_combinations(parent_combination,necessary_values),self.env['product.template.attribute.value'])

    def_cartesian_product(self,product_template_attribute_values_per_line,parent_combination):
        """
        Generateallpossiblecombinationforattributesvalues(akacartesianproduct).
        Itisequivalenttoitertools.productexceptitskipsinvalidpartialcombinationsbeforetheyarecomplete.

        Imaginethecartesianproductof'A','CD'andrange(1_000_000)andlet'ssaythat'A'and'C'areincompatible.
        Ifyouuseitertools.productoranynormalcartesianproduct,you'llneedtofilteroutofthefinalresult
        the1_000_000combinationsthatstartwith'A'and'C'.Instead,Thisimplementationwilltestif'A'and'C'are
        compatiblebeforeevenconsideringrange(1_000_000),skipitandandcontinuewithcombinationsthatstart
        with'A'and'D'.

        It'snecessaryforperformancereasonbecausefilteringoutinvalidcombinationsfromstandardCartesianproduct
        canbeextremelyslow

        :paramproduct_template_attribute_values_per_line:thevalueswewantallthepossiblescombinationsof.
        Onelistofvaluesbyattributeline
        :return:ageneratorofproducttemplateattributevalue
        """
        ifnotproduct_template_attribute_values_per_line:
            return

        all_exclusions={self.env['product.template.attribute.value'].browse(k):
                          self.env['product.template.attribute.value'].browse(v)fork,vin
                          self._get_own_attribute_exclusions().items()}
        #Thefollowingdictusesproducttemplateattributevaluesaskeys
        #0meansthevalueisacceptable,greaterthan0meansit'srejected,itcannotbenegative
        #Bearinmindthatseveralvaluescanrejectthesamevalueandthelattercanonlybeincludedinthe
        # consideredcombinationifnovaluerejectsit.
        #Thisdictionarycountshowmanytimeseachvalueisrejected.
        #Eachtimeavalueisincludedintheconsideredcombination,thevaluesitrejectsareincremented
        #Whenavalueisdiscardedfromtheconsideredcombination,thevaluesitrejectsaredecremented
        current_exclusions=defaultdict(int)
        forexclusioninself._get_parent_attribute_exclusions(parent_combination):
            current_exclusions[self.env['product.template.attribute.value'].browse(exclusion)]+=1
        partial_combination=self.env['product.template.attribute.value']

        #Thefollowinglistreflectsproduct_template_attribute_values_per_line
        #Foreachline,insteadofalistofvalues,itcontainstheindexoftheselectedvalue
        #-1meansnovaluehasbeenpickedforthelineinthecurrent(partial)combination
        value_index_per_line=[-1]*len(product_template_attribute_values_per_line)
        #determineswhichlinelinewe'reworkingon
        line_index=0

        whileTrue:
            current_line_values=product_template_attribute_values_per_line[line_index]
            current_ptav_index=value_index_per_line[line_index]
            current_ptav=current_line_values[current_ptav_index]

            #removingexclusionsfromcurrent_ptavaswe'reremovingitfrompartial_combination
            ifcurrent_ptav_index>=0:
                forptav_to_include_backinall_exclusions[current_ptav]:
                    current_exclusions[ptav_to_include_back]-=1
                partial_combination-=current_ptav

            ifcurrent_ptav_index<len(current_line_values)-1:
                #gotonextvalueofcurrentline
                value_index_per_line[line_index]+=1
                current_line_values=product_template_attribute_values_per_line[line_index]
                current_ptav_index=value_index_per_line[line_index]
                current_ptav=current_line_values[current_ptav_index]
            elifline_index!=0:
                #resetcurrentline,andthengotopreviousline
                value_index_per_line[line_index]=-1
                line_index-=1
                continue
            else:
                #we'redoneifwemustresetfirstline
                break

            #addingexclusionsfromcurrent_ptavaswe'reincorporatingitinpartial_combination
            forptav_to_excludeinall_exclusions[current_ptav]:
                current_exclusions[ptav_to_exclude]+=1
            partial_combination+=current_ptav

            #testifincludedvaluesexcludescurrentvalueorifcurrentvalueexcludeincludedvalues
            ifcurrent_exclusions[current_ptav]or\
                    any(intersectioninpartial_combinationforintersectioninall_exclusions[current_ptav]):
                continue

            ifline_index==len(product_template_attribute_values_per_line)-1:
                #submitcombinationifwe'reonthelastline
                yieldpartial_combination
            else:
                #elsewegotothenextline
                line_index+=1

    def_get_possible_combinations(self,parent_combination=None,necessary_values=None):
        """Generatorreturningcombinationsthatarepossible,followingthe
        sequenceofattributesandvalues.

        See`_is_combination_possible`forwhatisapossiblecombination.

        Whenencounteringanimpossiblecombination,trytochangethevalue
        ofattributesbystartingwiththefurtherregardingtheirsequences.

        Ignoreattributesthathavenovalues.

        :paramparent_combination:combinationfromwhich`self`isan
            optionaloraccessoryproduct.
        :typeparent_combination:recordset`product.template.attribute.value`

        :paramnecessary_values:valuesthatmustbeinthereturnedcombination
        :typenecessary_values:recordsetof`product.template.attribute.value`

        :return:thepossiblecombinations
        :rtype:generatorofrecordsetof`product.template.attribute.value`
        """
        self.ensure_one()

        ifnotself.active:
            return_("Theproducttemplateisarchivedsonocombinationispossible.")

        necessary_values=necessary_valuesorself.env['product.template.attribute.value']
        necessary_attribute_lines=necessary_values.mapped('attribute_line_id')
        attribute_lines=self.valid_product_template_attribute_line_ids.filtered(lambdaptal:ptalnotinnecessary_attribute_lines)

        ifnotattribute_linesandself._is_combination_possible(necessary_values,parent_combination):
            yieldnecessary_values

        product_template_attribute_values_per_line=[
            ptal.product_template_value_ids._only_active()
            forptalinattribute_lines
        ]

        forpartial_combinationinself._cartesian_product(product_template_attribute_values_per_line,parent_combination):
            combination=partial_combination+necessary_values
            ifself._is_combination_possible(combination,parent_combination):
                yieldcombination

        return_("Therearenoremainingpossiblecombination.")

    def_get_closest_possible_combination(self,combination):
        """See`_get_closest_possible_combinations`(oneiteration).

        Thismethodreturnthesameresult(emptyrecordset)ifno
        combinationispossibleatallwhichwouldbeconsideredanegative
        result,oriftherearenoattributelinesonthetemplateinwhich
        casethe"emptycombination"isactuallyapossiblecombination.
        Thereforetheresultofthismethodwhenemptyshouldbetested
        with`_is_combination_possible`ifit'simportanttoknowifthe
        resultingemptycombinationisactuallypossibleornot.
        """
        returnnext(self._get_closest_possible_combinations(combination),self.env['product.template.attribute.value'])

    def_get_closest_possible_combinations(self,combination):
        """Generatorreturningthepossiblecombinationsthataretheclosestto
        thegivencombination.

        Ifthegivencombinationisincomplete,trytocompleteit.

        Ifthegivencombinationisinvalid,trytoremovevaluesfromitbefore
        completingit.

        :paramcombination:thevaluestoincludeiftheyarepossible
        :typecombination:recordset`product.template.attribute.value`

        :return:thepossiblecombinationsthatareincludingasmuch
            elementsaspossiblefromthegivencombination.
        :rtype:generatorofrecordsetofproduct.template.attribute.value
        """
        whileTrue:
            res=self._get_possible_combinations(necessary_values=combination)
            try:
                #Ifthereisatleastoneresultforthegivencombination
                #weconsiderthatcombinationset,andweyieldallthe
                #possiblecombinationsforit.
                yield(next(res))
                forcurinres:
                    yield(cur)
                return_("Therearenoremainingclosestcombination.")
            exceptStopIteration:
                #Therearenoresultsforthegivencombination,wetryto
                #progressivelyremovevaluesfromit.
                ifnotcombination:
                    return_("Therearenopossiblecombination.")
                combination=combination[:-1]

    def_get_current_company(self,**kwargs):
        """Getthemostappropriatecompanyforthisproduct.

        Ifthecompanyissetontheproduct,directlyreturnit.Otherwise,
        fallbacktoacontextualcompany.

        :paramkwargs:kwargsforwardedtothefallbackmethod.

        :return:themostappropriatecompanyforthisproduct
        :rtype:recordsetofone`res.company`
        """
        self.ensure_one()
        returnself.company_idorself._get_current_company_fallback(**kwargs)

    def_get_current_company_fallback(self,**kwargs):
        """Fallbacktogetthemostappropriatecompanyforthisproduct.

        Thisshouldonlybecalledfrom`_get_current_company`butisdefined
        separatelytoallowoverride.

        Thefinalfallbackwillbethecurrentuser'scompany.

        :return:thefallbackcompanyforthisproduct
        :rtype:recordsetofone`res.company`
        """
        self.ensure_one()
        returnself.env.company

    defget_single_product_variant(self):
        """Methodusedbytheproductconfiguratortocheckiftheproductisconfigurableornot.

        Weneedtoopentheproductconfiguratoriftheproduct:
        -isconfigurable(seehas_configurable_attributes)
        -hasoptionalproducts(methodisextendedinsaletoreturnoptionalproductsinfo)
        """
        self.ensure_one()
        ifself.product_variant_count==1andnotself.has_configurable_attributes:
            return{
                'product_id':self.product_variant_id.id,
            }
        return{}

    @api.model
    defget_empty_list_help(self,help):
        self=self.with_context(
            empty_list_help_document_name=_("product"),
        )
        returnsuper(ProductTemplate,self).get_empty_list_help(help)

    @api.model
    defget_import_templates(self):
        return[{
            'label':_('ImportTemplateforProducts'),
            'template':'/product/static/xls/product_template.xls'
        }]
