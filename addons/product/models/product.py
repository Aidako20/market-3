#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importre

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.osvimportexpression


fromflectra.toolsimportfloat_compare

_logger=logging.getLogger(__name__)



classProductCategory(models.Model):
    _name="product.category"
    _description="ProductCategory"
    _parent_name="parent_id"
    _parent_store=True
    _rec_name='complete_name'
    _order='complete_name'

    name=fields.Char('Name',index=True,required=True)
    complete_name=fields.Char(
        'CompleteName',compute='_compute_complete_name',
        store=True)
    parent_id=fields.Many2one('product.category','ParentCategory',index=True,ondelete='cascade')
    parent_path=fields.Char(index=True)
    child_id=fields.One2many('product.category','parent_id','ChildCategories')
    product_count=fields.Integer(
        '#Products',compute='_compute_product_count',
        help="Thenumberofproductsunderthiscategory(Doesnotconsiderthechildrencategories)")

    @api.depends('name','parent_id.complete_name')
    def_compute_complete_name(self):
        forcategoryinself:
            ifcategory.parent_id:
                category.complete_name='%s/%s'%(category.parent_id.complete_name,category.name)
            else:
                category.complete_name=category.name

    def_compute_product_count(self):
        read_group_res=self.env['product.template'].read_group([('categ_id','child_of',self.ids)],['categ_id'],['categ_id'])
        group_data=dict((data['categ_id'][0],data['categ_id_count'])fordatainread_group_res)
        forcateginself:
            product_count=0
            forsub_categ_idincateg.search([('id','child_of',categ.ids)]).ids:
                product_count+=group_data.get(sub_categ_id,0)
            categ.product_count=product_count

    @api.constrains('parent_id')
    def_check_category_recursion(self):
        ifnotself._check_recursion():
            raiseValidationError(_('Youcannotcreaterecursivecategories.'))
        returnTrue

    @api.model
    defname_create(self,name):
        returnself.create({'name':name}).name_get()[0]

    defunlink(self):
        main_category=self.env.ref('product.product_category_all')
        ifmain_categoryinself:
            raiseUserError(_("Youcannotdeletethisproductcategory,itisthedefaultgenericcategory."))
        returnsuper().unlink()


classProductProduct(models.Model):
    _name="product.product"
    _description="Product"
    _inherits={'product.template':'product_tmpl_id'}
    _inherit=['mail.thread','mail.activity.mixin']
    _order='default_code,name,id'

    #price:totalprice,contextdependent(partner,pricelist,quantity)
    price=fields.Float(
        'Price',compute='_compute_product_price',
        digits='ProductPrice',inverse='_set_product_price')
    #price_extra:catalogextravalueonly,sumofvariantextraattributes
    price_extra=fields.Float(
        'VariantPriceExtra',compute='_compute_product_price_extra',
        digits='ProductPrice',
        help="Thisisthesumoftheextrapriceofallattributes")
    #lst_price:catalogvalue+extra,contextdependent(uom)
    lst_price=fields.Float(
        'PublicPrice',compute='_compute_product_lst_price',
        digits='ProductPrice',inverse='_set_product_lst_price',
        help="Thesalepriceismanagedfromtheproducttemplate.Clickonthe'ConfigureVariants'buttontosettheextraattributeprices.")

    default_code=fields.Char('InternalReference',index=True)
    code=fields.Char('Reference',compute='_compute_product_code')
    partner_ref=fields.Char('CustomerRef',compute='_compute_partner_ref')

    active=fields.Boolean(
        'Active',default=True,
        help="Ifunchecked,itwillallowyoutohidetheproductwithoutremovingit.")
    product_tmpl_id=fields.Many2one(
        'product.template','ProductTemplate',
        auto_join=True,index=True,ondelete="cascade",required=True)
    barcode=fields.Char(
        'Barcode',copy=False,
        help="InternationalArticleNumberusedforproductidentification.")
    product_template_attribute_value_ids=fields.Many2many('product.template.attribute.value',relation='product_variant_combination',string="AttributeValues",ondelete='restrict')
    combination_indices=fields.Char(compute='_compute_combination_indices',store=True,index=True)
    is_product_variant=fields.Boolean(compute='_compute_is_product_variant')

    standard_price=fields.Float(
        'Cost',company_dependent=True,
        digits='ProductPrice',
        groups="base.group_user",
        help="""InStandardPrice&AVCO:valueoftheproduct(automaticallycomputedinAVCO).
        InFIFO:valueofthenextunitthatwillleavethestock(automaticallycomputed).
        Usedtovaluetheproductwhenthepurchasecostisnotknown(e.g.inventoryadjustment).
        Usedtocomputemarginsonsaleorders.""")
    volume=fields.Float('Volume',digits='Volume')
    weight=fields.Float('Weight',digits='StockWeight')

    pricelist_item_count=fields.Integer("Numberofpricerules",compute="_compute_variant_item_count")

    packaging_ids=fields.One2many(
        'product.packaging','product_id','ProductPackages',
        help="Givesthedifferentwaystopackagethesameproduct.")

    #allimagefieldsarebase64encodedandPIL-supported

    #allimage_variantfieldsaretechnicalandshouldnotbedisplayedtotheuser
    image_variant_1920=fields.Image("VariantImage",max_width=1920,max_height=1920)

    #resizedfieldsstored(asattachment)forperformance
    image_variant_1024=fields.Image("VariantImage1024",related="image_variant_1920",max_width=1024,max_height=1024,store=True)
    image_variant_512=fields.Image("VariantImage512",related="image_variant_1920",max_width=512,max_height=512,store=True)
    image_variant_256=fields.Image("VariantImage256",related="image_variant_1920",max_width=256,max_height=256,store=True)
    image_variant_128=fields.Image("VariantImage128",related="image_variant_1920",max_width=128,max_height=128,store=True)
    can_image_variant_1024_be_zoomed=fields.Boolean("CanVariantImage1024bezoomed",compute='_compute_can_image_variant_1024_be_zoomed',store=True)

    #Computedfieldsthatareusedtocreateafallbacktothetemplateif
    #necessary,it'srecommendedtodisplaythosefieldstotheuser.
    image_1920=fields.Image("Image",compute='_compute_image_1920',inverse='_set_image_1920')
    image_1024=fields.Image("Image1024",compute='_compute_image_1024')
    image_512=fields.Image("Image512",compute='_compute_image_512')
    image_256=fields.Image("Image256",compute='_compute_image_256')
    image_128=fields.Image("Image128",compute='_compute_image_128')
    can_image_1024_be_zoomed=fields.Boolean("CanImage1024bezoomed",compute='_compute_can_image_1024_be_zoomed')

    @api.depends('image_variant_1920','image_variant_1024')
    def_compute_can_image_variant_1024_be_zoomed(self):
        forrecordinself:
            record.can_image_variant_1024_be_zoomed=record.image_variant_1920andtools.is_image_size_above(record.image_variant_1920,record.image_variant_1024)

    def_compute_image_1920(self):
        """Gettheimagefromthetemplateifnoimageissetonthevariant."""
        forrecordinself:
            record.image_1920=record.image_variant_1920orrecord.product_tmpl_id.image_1920

    def_set_image_1920(self):
        forrecordinself:
            if(
                #Wearetryingtoremoveanimageeventhoughitisalready
                #notset,removeitfromthetemplateinstead.
                notrecord.image_1920andnotrecord.image_variant_1920or
                #Wearetryingtoaddanimage,butthetemplateimageis
                #notset,writeonthetemplateinstead.
                record.image_1920andnotrecord.product_tmpl_id.image_1920or
                #Thereisonlyonevariant,alwayswriteonthetemplate.
                self.search_count([
                    ('product_tmpl_id','=',record.product_tmpl_id.id),
                    ('active','=',True),
                ])<=1
            ):
                record.image_variant_1920=False
                record.product_tmpl_id.image_1920=record.image_1920
            else:
                record.image_variant_1920=record.image_1920

    @api.depends("create_date","write_date","product_tmpl_id.create_date","product_tmpl_id.write_date")
    defcompute_concurrency_field_with_access(self):
        #Intentionallynotcallingsuper()toinvolveallfieldsexplicitly
        forrecordinself:
            record[self.CONCURRENCY_CHECK_FIELD]=max(filter(None,(
                record.product_tmpl_id.write_dateorrecord.product_tmpl_id.create_date,
                record.write_dateorrecord.create_dateorfields.Datetime.now(),
            )))

    def_compute_image_1024(self):
        """Gettheimagefromthetemplateifnoimageissetonthevariant."""
        forrecordinself:
            record.image_1024=record.image_variant_1024orrecord.product_tmpl_id.image_1024

    def_compute_image_512(self):
        """Gettheimagefromthetemplateifnoimageissetonthevariant."""
        forrecordinself:
            record.image_512=record.image_variant_512orrecord.product_tmpl_id.image_512

    def_compute_image_256(self):
        """Gettheimagefromthetemplateifnoimageissetonthevariant."""
        forrecordinself:
            record.image_256=record.image_variant_256orrecord.product_tmpl_id.image_256

    def_compute_image_128(self):
        """Gettheimagefromthetemplateifnoimageissetonthevariant."""
        forrecordinself:
            record.image_128=record.image_variant_128orrecord.product_tmpl_id.image_128

    def_compute_can_image_1024_be_zoomed(self):
        """Gettheimagefromthetemplateifnoimageissetonthevariant."""
        forrecordinself:
            record.can_image_1024_be_zoomed=record.can_image_variant_1024_be_zoomedifrecord.image_variant_1920elserecord.product_tmpl_id.can_image_1024_be_zoomed

    definit(self):
        """Ensurethereisatmostoneactivevariantforeachcombination.

        Therecouldbenovariantforacombinationifusingdynamicattributes.
        """
        self.env.cr.execute("CREATEUNIQUEINDEXIFNOTEXISTSproduct_product_combination_uniqueON%s(product_tmpl_id,combination_indices)WHEREactiveistrue"
            %self._table)

    _sql_constraints=[
        ('barcode_uniq','unique(barcode)',"Abarcodecanonlybeassignedtooneproduct!"),
    ]

    def_get_invoice_policy(self):
        returnFalse

    @api.depends('product_template_attribute_value_ids')
    def_compute_combination_indices(self):
        forproductinself:
            product.combination_indices=product.product_template_attribute_value_ids._ids2str()

    def_compute_is_product_variant(self):
        self.is_product_variant=True

    @api.depends_context('pricelist','partner','quantity','uom','date','no_variant_attributes_price_extra')
    def_compute_product_price(self):
        prices={}
        pricelist_id_or_name=self._context.get('pricelist')
        ifpricelist_id_or_name:
            pricelist=None
            partner=self.env.context.get('partner',False)
            quantity=self.env.context.get('quantity',1.0)

            #Supportcontextpricelistsspecifiedaslist,display_nameorIDforcompatibility
            ifisinstance(pricelist_id_or_name,list):
                pricelist_id_or_name=pricelist_id_or_name[0]
            ifisinstance(pricelist_id_or_name,str):
                pricelist_name_search=self.env['product.pricelist'].name_search(pricelist_id_or_name,operator='=',limit=1)
                ifpricelist_name_search:
                    pricelist=self.env['product.pricelist'].browse([pricelist_name_search[0][0]])
            elifisinstance(pricelist_id_or_name,int):
                pricelist=self.env['product.pricelist'].browse(pricelist_id_or_name)

            ifpricelist:
                quantities=[quantity]*len(self)
                partners=[partner]*len(self)
                prices=pricelist.get_products_price(self,quantities,partners)

        forproductinself:
            product.price=prices.get(product.id,0.0)

    def_set_product_price(self):
        forproductinself:
            ifself._context.get('uom'):
                value=self.env['uom.uom'].browse(self._context['uom'])._compute_price(product.price,product.uom_id)
            else:
                value=product.price
            value-=product.price_extra
            product.write({'list_price':value})

    def_set_product_lst_price(self):
        forproductinself:
            ifself._context.get('uom'):
                value=self.env['uom.uom'].browse(self._context['uom'])._compute_price(product.lst_price,product.uom_id)
            else:
                value=product.lst_price
            value-=product.price_extra
            product.write({'list_price':value})

    def_compute_product_price_extra(self):
        forproductinself:
            product.price_extra=sum(product.product_template_attribute_value_ids.mapped('price_extra'))

    @api.depends('list_price','price_extra')
    @api.depends_context('uom')
    def_compute_product_lst_price(self):
        to_uom=None
        if'uom'inself._context:
            to_uom=self.env['uom.uom'].browse(self._context['uom'])

        forproductinself:
            ifto_uom:
                list_price=product.uom_id._compute_price(product.list_price,to_uom)
            else:
                list_price=product.list_price
            product.lst_price=list_price+product.price_extra

    @api.depends_context('partner_id')
    def_compute_product_code(self):
        forproductinself:
            forsupplier_infoinproduct.seller_ids:
                ifsupplier_info.name.id==product._context.get('partner_id'):
                    product.code=supplier_info.product_codeorproduct.default_code
                    break
            else:
                product.code=product.default_code

    @api.depends_context('partner_id')
    def_compute_partner_ref(self):
        forproductinself:
            forsupplier_infoinproduct.seller_ids:
                ifsupplier_info.name.id==product._context.get('partner_id'):
                    product_name=supplier_info.product_nameorproduct.default_codeorproduct.name
                    product.partner_ref='%s%s'%(product.codeand'[%s]'%product.codeor'',product_name)
                    break
            else:
                product.partner_ref=product.display_name

    def_compute_variant_item_count(self):
        forproductinself:
            domain=['|',
                '&',('product_tmpl_id','=',product.product_tmpl_id.id),('applied_on','=','1_product'),
                '&',('product_id','=',product.id),('applied_on','=','0_product_variant')]
            product.pricelist_item_count=self.env['product.pricelist.item'].search_count(domain)

    @api.onchange('uom_id')
    def_onchange_uom_id(self):
        ifself.uom_id:
            self.uom_po_id=self.uom_id.id

    @api.onchange('uom_po_id')
    def_onchange_uom(self):
        ifself.uom_idandself.uom_po_idandself.uom_id.category_id!=self.uom_po_id.category_id:
            self.uom_po_id=self.uom_id

    @api.model_create_multi
    defcreate(self,vals_list):
        products=super(ProductProduct,self.with_context(create_product_product=True)).create(vals_list)
        #`_get_variant_id_for_combination`dependsonexistingvariants
        self.clear_caches()
        returnproducts

    defwrite(self,values):
        res=super(ProductProduct,self).write(values)
        if'product_template_attribute_value_ids'invalues:
            #`_get_variant_id_for_combination`dependson`product_template_attribute_value_ids`
            self.clear_caches()
        elif'active'invalues:
            #`_get_first_possible_variant_id`dependsonvariantsactivestate
            self.clear_caches()
        returnres

    defunlink(self):
        unlink_products=self.env['product.product']
        unlink_templates=self.env['product.template']
        forproductinself:
            #Ifthereisanimagesetonthevariantandnoimagesetonthe
            #template,movetheimagetothetemplate.
            ifproduct.image_variant_1920andnotproduct.product_tmpl_id.image_1920:
                product.product_tmpl_id.image_1920=product.image_variant_1920
            #Checkifproductstillexists,incaseithasbeenunlinkedbyunlinkingitstemplate
            ifnotproduct.exists():
                continue
            #Checkiftheproductislastproductofthistemplate...
            other_products=self.search([('product_tmpl_id','=',product.product_tmpl_id.id),('id','!=',product.id)])
            #...anddonotdeleteproducttemplateifit'sconfiguredtobecreated"ondemand"
            ifnotother_productsandnotproduct.product_tmpl_id.has_dynamic_attributes():
                unlink_templates|=product.product_tmpl_id
            unlink_products|=product
        res=super(ProductProduct,unlink_products).unlink()
        #deletetemplatesaftercallingsuper,asdeletingtemplatecouldleadtodeleting
        #productsduetoondelete='cascade'
        unlink_templates.unlink()
        #`_get_variant_id_for_combination`dependsonexistingvariants
        self.clear_caches()
        returnres

    def_filter_to_unlink(self,check_access=True):
        returnself

    def_unlink_or_archive(self,check_access=True):
        """Unlinkorarchiveproducts.
        Tryinbatchasmuchaspossiblebecauseitismuchfaster.
        Usedichotomywhenanexceptionoccurs.
        """

        #Avoidaccesserrorsincasetheproductsissharedamongstcompanies
        #buttheunderlyingobjectsarenot.Ifunlinkfailsbecauseofan
        #AccessError(e.g.whilerecomputingfields),the'write'callwill
        #failaswellforthesamereasonsincethefieldhasbeensetto
        #recompute.
        ifcheck_access:
            self.check_access_rights('unlink')
            self.check_access_rule('unlink')
            self.check_access_rights('write')
            self.check_access_rule('write')
            self=self.sudo()
            to_unlink=self._filter_to_unlink()
            to_archive=self-to_unlink
            to_archive.write({'active':False})
            self=to_unlink

        try:
            withself.env.cr.savepoint(),tools.mute_logger('flectra.sql_db'):
                self.unlink()
        exceptException:
            #Wecatchallkindofexceptionstobesurethattheoperation
            #doesn'tfail.
            iflen(self)>1:
                self[:len(self)//2]._unlink_or_archive(check_access=False)
                self[len(self)//2:]._unlink_or_archive(check_access=False)
            else:
                ifself.active:
                    #Note:thiscanstillfailifsomethingispreventing
                    #fromarchiving.
                    #Thisisthecasefromexistingstockreorderingrules.
                    self.write({'active':False})

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        """Variantsaregenerateddependingontheconfigurationofattributes
        andvaluesonthetemplate,socopyingthemdoesnotmakesense.

        Forconveniencethetemplateiscopiedinsteadanditsfirstvariantis
        returned.
        """
        #copyvariantisdisabledinhttps://github.com/flectra/flectra/pull/38303
        #thisreturnsthefirstpossiblecombinationofvarianttomakeit
        #worksfornow,needtobefixedtoreturnproduct_variant_idifit's
        #possibleinthefuture
        template=self.product_tmpl_id.copy(default=default)
        returntemplate.product_variant_idortemplate._create_first_product_variant()

    @api.model
    def_search(self,args,offset=0,limit=None,order=None,count=False,access_rights_uid=None):
        #TDEFIXME:strange
        ifself._context.get('search_default_categ_id'):
            args.append((('categ_id','child_of',self._context['search_default_categ_id'])))
        returnsuper(ProductProduct,self)._search(args,offset=offset,limit=limit,order=order,count=count,access_rights_uid=access_rights_uid)

    @api.depends_context('display_default_code','seller_id')
    def_compute_display_name(self):
        #`display_name`iscalling`name_get()``whichisoveriddenonproduct
        #todependon`display_default_code`and`seller_id`
        returnsuper()._compute_display_name()

    defname_get(self):
        #TDE:thiscouldbecleanedabitIthink

        def_name_get(d):
            name=d.get('name','')
            code=self._context.get('display_default_code',True)andd.get('default_code',False)orFalse
            ifcode:
                name='[%s]%s'%(code,name)
            return(d['id'],name)

        partner_id=self._context.get('partner_id')
        ifpartner_id:
            partner_ids=[partner_id,self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids=[]
        company_id=self.env.context.get('company_id')

        #alluserdon'thaveaccesstosellerandpartner
        #checkaccessandusesuperuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result=[]

        #Prefetchthefieldsusedbythe`name_get`,so`browse`doesn'tfetchotherfields
        #Use`load=False`tonotcall`name_get`forthe`product_tmpl_id`
        self.sudo().read(['name','default_code','product_tmpl_id'],load=False)

        product_template_ids=self.sudo().mapped('product_tmpl_id').ids

        ifpartner_ids:
            supplier_info=self.env['product.supplierinfo'].sudo().search([
                ('product_tmpl_id','in',product_template_ids),
                ('name','in',partner_ids),
            ])
            #Prefetchthefieldsusedbythe`name_get`,so`browse`doesn'tfetchotherfields
            #Use`load=False`tonotcall`name_get`forthe`product_tmpl_id`and`product_id`
            supplier_info.sudo().read(['product_tmpl_id','product_id','product_name','product_code'],load=False)
            supplier_info_by_template={}
            forrinsupplier_info:
                supplier_info_by_template.setdefault(r.product_tmpl_id,[]).append(r)
        forproductinself.sudo():
            variant=product.product_template_attribute_value_ids._get_combination_name()

            name=variantand"%s(%s)"%(product.name,variant)orproduct.name
            sellers=self.env['product.supplierinfo'].sudo().browse(self.env.context.get('seller_id'))or[]
            ifnotsellersandpartner_ids:
                product_supplier_info=supplier_info_by_template.get(product.product_tmpl_id,[])
                sellers=[xforxinproduct_supplier_infoifx.product_idandx.product_id==product]
                ifnotsellers:
                    sellers=[xforxinproduct_supplier_infoifnotx.product_id]
                #Filteroutsellersbasedonthecompany.Thisisdoneafterwardsforabetter
                #codereadability.Atthispoint,onlyafewsellersshouldremain,soitshould
                #notbeaperformanceissue.
                ifcompany_id:
                    sellers=[xforxinsellersifx.company_id.idin[company_id,False]]
            ifsellers:
                forsinsellers:
                    seller_variant=s.product_nameand(
                        variantand"%s(%s)"%(s.product_name,variant)ors.product_name
                        )orFalse
                    mydict={
                              'id':product.id,
                              'name':seller_variantorname,
                              'default_code':s.product_codeorproduct.default_code,
                              }
                    temp=_name_get(mydict)
                    iftempnotinresult:
                        result.append(temp)
            else:
                mydict={
                          'id':product.id,
                          'name':name,
                          'default_code':product.default_code,
                          }
                result.append(_name_get(mydict))
        returnresult

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        ifnotargs:
            args=[]
        ifname:
            positive_operators=['=','ilike','=ilike','like','=like']
            product_ids=[]
            ifoperatorinpositive_operators:
                product_ids=list(self._search([('default_code','=',name)]+args,limit=limit,access_rights_uid=name_get_uid))
                ifnotproduct_ids:
                    product_ids=list(self._search([('barcode','=',name)]+args,limit=limit,access_rights_uid=name_get_uid))
            ifnotproduct_idsandoperatornotinexpression.NEGATIVE_TERM_OPERATORS:
                #Donotmergethe2nextlinesintoonesinglesearch,SQLsearchperformancewouldbeabysmal
                #onadatabasewiththousandsofmatchingproducts,duetothehugemerge+uniqueneededforthe
                #ORoperator(andgiventhefactthatthe'name'lookupresultscomefromtheir.translationtable
                #PerformingaquickmemorymergeofidsinPythonwillgivemuchbetterperformance
                product_ids=list(self._search(args+[('default_code',operator,name)],limit=limit))
                ifnotlimitorlen(product_ids)<limit:
                    #wemayunderrunthelimitbecauseofdupesintheresults,that'sfine
                    limit2=(limit-len(product_ids))iflimitelseFalse
                    product2_ids=self._search(args+[('name',operator,name),('id','notin',product_ids)],limit=limit2,access_rights_uid=name_get_uid)
                    product_ids.extend(product2_ids)
            elifnotproduct_idsandoperatorinexpression.NEGATIVE_TERM_OPERATORS:
                domain=expression.OR([
                    ['&',('default_code',operator,name),('name',operator,name)],
                    ['&',('default_code','=',False),('name',operator,name)],
                ])
                domain=expression.AND([args,domain])
                product_ids=list(self._search(domain,limit=limit,access_rights_uid=name_get_uid))
            ifnotproduct_idsandoperatorinpositive_operators:
                ptrn=re.compile('(\[(.*?)\])')
                res=ptrn.search(name)
                ifres:
                    product_ids=list(self._search([('default_code','=',res.group(2))]+args,limit=limit,access_rights_uid=name_get_uid))
            #stillnoresults,partnerincontext:searchonsupplierinfoaslasthopetofindsomething
            ifnotproduct_idsandself._context.get('partner_id'):
                suppliers_ids=self.env['product.supplierinfo']._search([
                    ('name','=',self._context.get('partner_id')),
                    '|',
                    ('product_code',operator,name),
                    ('product_name',operator,name)],access_rights_uid=name_get_uid)
                ifsuppliers_ids:
                    product_ids=self._search([('product_tmpl_id.seller_ids','in',suppliers_ids)],limit=limit,access_rights_uid=name_get_uid)
        else:
            product_ids=self._search(args,limit=limit,access_rights_uid=name_get_uid)
        returnproduct_ids

    @api.model
    defview_header_get(self,view_id,view_type):
        ifself._context.get('categ_id'):
            return_(
                'Products:%(category)s',
                category=self.env['product.category'].browse(self.env.context['categ_id']).name,
            )
        returnsuper().view_header_get(view_id,view_type)

    defopen_pricelist_rules(self):
        self.ensure_one()
        domain=['|',
            '&',('product_tmpl_id','=',self.product_tmpl_id.id),('applied_on','=','1_product'),
            '&',('product_id','=',self.id),('applied_on','=','0_product_variant')]
        return{
            'name':_('PriceRules'),
            'view_mode':'tree,form',
            'views':[(self.env.ref('product.product_pricelist_item_tree_view_from_product').id,'tree'),(False,'form')],
            'res_model':'product.pricelist.item',
            'type':'ir.actions.act_window',
            'target':'current',
            'domain':domain,
            'context':{
                'default_product_id':self.id,
                'default_applied_on':'0_product_variant',
            }
        }

    defopen_product_template(self):
        """Utilitymethodusedtoaddan"OpenTemplate"buttoninproductviews"""
        self.ensure_one()
        return{'type':'ir.actions.act_window',
                'res_model':'product.template',
                'view_mode':'form',
                'res_id':self.product_tmpl_id.id,
                'target':'new'}

    def_prepare_sellers(self,params=False):
        returnself.seller_ids.filtered(lambdas:s.name.active).sorted(lambdas:(s.sequence,-s.min_qty,s.price,s.id))

    def_select_seller(self,partner_id=False,quantity=0.0,date=None,uom_id=False,params=False):
        self.ensure_one()
        ifdateisNone:
            date=fields.Date.context_today(self)
        precision=self.env['decimal.precision'].precision_get('ProductUnitofMeasure')

        res=self.env['product.supplierinfo']
        sellers=self._prepare_sellers(params)
        sellers=sellers.filtered(lambdas:nots.company_idors.company_id.id==self.env.company.id)
        forsellerinsellers:
            #SetquantityinUoMofseller
            quantity_uom_seller=quantity
            ifquantity_uom_selleranduom_idanduom_id!=seller.product_uom:
                quantity_uom_seller=uom_id._compute_quantity(quantity_uom_seller,seller.product_uom)

            ifseller.date_startandseller.date_start>date:
                continue
            ifseller.date_endandseller.date_end<date:
                continue
            ifpartner_idandseller.namenotin[partner_id,partner_id.parent_id]:
                continue
            ifquantityisnotNoneandfloat_compare(quantity_uom_seller,seller.min_qty,precision_digits=precision)==-1:
                continue
            ifseller.product_idandseller.product_id!=self:
                continue
            ifnotresorres.name==seller.name:
                res|=seller
        returnres.sorted('price')[:1]

    defprice_compute(self,price_type,uom=False,currency=False,company=None):
        #TDEFIXME:delegatetotemplateornot?fieldsarereencodedhere...
        #compatibilityaboutcontextkeysusedabiteverywhereinthecode
        ifnotuomandself._context.get('uom'):
            uom=self.env['uom.uom'].browse(self._context['uom'])
        ifnotcurrencyandself._context.get('currency'):
            currency=self.env['res.currency'].browse(self._context['currency'])

        products=self
        ifprice_type=='standard_price':
            #standard_pricefieldcanonlybeseenbyusersinbase.group_user
            #Thus,inordertocomputethesalepricefromthecostforusersnotinthisgroup
            #Wefetchthestandardpriceasthesuperuser
            products=self.with_company(companyorself.env.company).sudo()

        prices=dict.fromkeys(self.ids,0.0)
        forproductinproducts:
            prices[product.id]=product[price_type]or0.0
            ifprice_type=='list_price':
                prices[product.id]+=product.price_extra
                #weneedtoaddthepricefromtheattributesthatdonotgeneratevariants
                #(seefieldproduct.attributecreate_variant)
                ifself._context.get('no_variant_attributes_price_extra'):
                    #wehavealistofprice_extrathatcomesfromtheattributevalues,weneedtosumallthat
                    prices[product.id]+=sum(self._context.get('no_variant_attributes_price_extra'))

            ifuom:
                prices[product.id]=product.uom_id._compute_price(prices[product.id],uom)

            #Convertfromcurrentusercompanycurrencytoaskedone
            #Thisisrightcauseafieldcannotbeinmorethanonecurrency
            ifcurrency:
                company=companyorself.env.company
                prices[product.id]=product.currency_id._convert(
                    prices[product.id],currency,company,fields.Date.today())

        returnprices

    @api.model
    defget_empty_list_help(self,help):
        self=self.with_context(
            empty_list_help_document_name=_("product"),
        )
        returnsuper(ProductProduct,self).get_empty_list_help(help)

    defget_product_multiline_description_sale(self):
        """Computeamultilinedescriptionofthisproduct,inthecontextofsales
                (donotuseforpurchasesorotherdisplayreasonsthatdon'tintendtouse"description_sale").
            Itwilloftenbeusedasthedefaultdescriptionofasaleorderlinereferencingthisproduct.
        """
        name=self.display_name
        ifself.description_sale:
            name+='\n'+self.description_sale

        returnname

    def_is_variant_possible(self,parent_combination=None):
        """Returnwhetherthevariantispossiblebasedonitsowncombination,
        andoptionallyaparentcombination.

        See`_is_combination_possible`formoreinformation.

        :paramparent_combination:combinationfromwhich`self`isan
            optionaloraccessoryproduct.
        :typeparent_combination:recordset`product.template.attribute.value`

        :return:ẁhetherthevariantispossiblebasedonitsowncombination
        :rtype:bool
        """
        self.ensure_one()
        returnself.product_tmpl_id._is_combination_possible(self.product_template_attribute_value_ids,parent_combination=parent_combination,ignore_no_variant=True)

    deftoggle_active(self):
        """Archivingrelatedproduct.templateifthereisnotanymoreactiveproduct.product
        (andviceversa,unarchivingtherelatedproducttemplateifthereisnowanactiveproduct.product)"""
        result=super().toggle_active()
        #Wedeactivateproducttemplateswhichareactivewithnoactivevariants.
        tmpl_to_deactivate=self.filtered(lambdaproduct:(product.product_tmpl_id.active
                                                            andnotproduct.product_tmpl_id.product_variant_ids)).mapped('product_tmpl_id')
        #Weactivateproducttemplateswhichareinactivewithactivevariants.
        tmpl_to_activate=self.filtered(lambdaproduct:(notproduct.product_tmpl_id.active
                                                          andproduct.product_tmpl_id.product_variant_ids)).mapped('product_tmpl_id')
        (tmpl_to_deactivate+tmpl_to_activate).toggle_active()
        returnresult


classProductPackaging(models.Model):
    _name="product.packaging"
    _description="ProductPackaging"
    _order='sequence'
    _check_company_auto=True

    name=fields.Char('PackageType',required=True)
    sequence=fields.Integer('Sequence',default=1,help="Thefirstinthesequenceisthedefaultone.")
    product_id=fields.Many2one('product.product',string='Product',check_company=True)
    qty=fields.Float('ContainedQuantity',digits='ProductUnitofMeasure',help="Quantityofproductscontainedinthepackaging.")
    barcode=fields.Char('Barcode',copy=False,help="Barcodeusedforpackagingidentification.ScanthispackagingbarcodefromatransferintheBarcodeapptomoveallthecontainedunits")
    product_uom_id=fields.Many2one('uom.uom',related='product_id.uom_id',readonly=True)
    company_id=fields.Many2one('res.company','Company',index=True)


classSupplierInfo(models.Model):
    _name="product.supplierinfo"
    _description="SupplierPricelist"
    _order='sequence,min_qtyDESC,price,id'

    name=fields.Many2one(
        'res.partner','Vendor',
        ondelete='cascade',required=True,
        help="Vendorofthisproduct",check_company=True)
    product_name=fields.Char(
        'VendorProductName',
        help="Thisvendor'sproductnamewillbeusedwhenprintingarequestforquotation.Keepemptytousetheinternalone.")
    product_code=fields.Char(
        'VendorProductCode',
        help="Thisvendor'sproductcodewillbeusedwhenprintingarequestforquotation.Keepemptytousetheinternalone.")
    sequence=fields.Integer(
        'Sequence',default=1,help="Assignstheprioritytothelistofproductvendor.")
    product_uom=fields.Many2one(
        'uom.uom','UnitofMeasure',
        related='product_tmpl_id.uom_po_id',
        help="Thiscomesfromtheproductform.")
    min_qty=fields.Float(
        'Quantity',default=0.0,required=True,digits="ProductUnitOfMeasure",
        help="Thequantitytopurchasefromthisvendortobenefitfromtheprice,expressedinthevendorProductUnitofMeasureifnotany,inthedefaultunitofmeasureoftheproductotherwise.")
    price=fields.Float(
        'Price',default=0.0,digits='ProductPrice',
        required=True,help="Thepricetopurchaseaproduct")
    company_id=fields.Many2one(
        'res.company','Company',
        default=lambdaself:self.env.company.id,index=1)
    currency_id=fields.Many2one(
        'res.currency','Currency',
        default=lambdaself:self.env.company.currency_id.id,
        required=True)
    date_start=fields.Date('StartDate',help="Startdateforthisvendorprice")
    date_end=fields.Date('EndDate',help="Enddateforthisvendorprice")
    product_id=fields.Many2one(
        'product.product','ProductVariant',check_company=True,
        help="Ifnotset,thevendorpricewillapplytoallvariantsofthisproduct.")
    product_tmpl_id=fields.Many2one(
        'product.template','ProductTemplate',check_company=True,
        index=True,ondelete='cascade')
    product_variant_count=fields.Integer('VariantCount',related='product_tmpl_id.product_variant_count')
    delay=fields.Integer(
        'DeliveryLeadTime',default=1,required=True,
        help="Leadtimeindaysbetweentheconfirmationofthepurchaseorderandthereceiptoftheproductsinyourwarehouse.Usedbytheschedulerforautomaticcomputationofthepurchaseorderplanning.")

    @api.model
    defget_import_templates(self):
        return[{
            'label':_('ImportTemplateforVendorPricelists'),
            'template':'/product/static/xls/product_supplierinfo.xls'
        }]

    @api.constrains('product_id','product_tmpl_id')
    def_check_product_variant(self):
        forsupplierinself:
            ifsupplier.product_idandsupplier.product_tmpl_idandsupplier.product_id.product_tmpl_id!=supplier.product_tmpl_id:
                raiseValidationError(_('Theproductvariantmustbeavariantoftheproducttemplate.'))
