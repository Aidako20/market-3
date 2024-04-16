#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.osvimportexpression


classProductAttribute(models.Model):
    _name="product.attribute"
    _description="ProductAttribute"
    #ifyouchangethis_order,keepitinsyncwiththemethod
    #`_sort_key_attribute_value`in`product.template`
    _order='sequence,id'

    name=fields.Char('Attribute',required=True,translate=True)
    value_ids=fields.One2many('product.attribute.value','attribute_id','Values',copy=True)
    sequence=fields.Integer('Sequence',help="Determinethedisplayorder",index=True)
    attribute_line_ids=fields.One2many('product.template.attribute.line','attribute_id','Lines')
    create_variant=fields.Selection([
        ('always','Instantly'),
        ('dynamic','Dynamically'),
        ('no_variant','Never')],
        default='always',
        string="VariantsCreationMode",
        help="""-Instantly:Allpossiblevariantsarecreatedassoonastheattributeanditsvaluesareaddedtoaproduct.
        -Dynamically:Eachvariantiscreatedonlywhenitscorrespondingattributesandvaluesareaddedtoasalesorder.
        -Never:Variantsarenevercreatedfortheattribute.
        Note:thevariantscreationmodecannotbechangedoncetheattributeisusedonatleastoneproduct.""",
        required=True)
    is_used_on_products=fields.Boolean('UsedonProducts',compute='_compute_is_used_on_products')
    product_tmpl_ids=fields.Many2many('product.template',string="RelatedProducts",compute='_compute_products',store=True)
    display_type=fields.Selection([
        ('radio','Radio'),
        ('select','Select'),
        ('color','Color')],default='radio',required=True,help="ThedisplaytypeusedintheProductConfigurator.")

    @api.depends('product_tmpl_ids')
    def_compute_is_used_on_products(self):
        forpainself:
            pa.is_used_on_products=bool(pa.product_tmpl_ids)

    @api.depends('attribute_line_ids.active','attribute_line_ids.product_tmpl_id')
    def_compute_products(self):
        forpainself:
            pa.with_context(active_test=False).product_tmpl_ids=pa.attribute_line_ids.product_tmpl_id

    def_without_no_variant_attributes(self):
        returnself.filtered(lambdapa:pa.create_variant!='no_variant')

    defwrite(self,vals):
        """Overridetomakesureattributetypecan'tbechangedifit'susedon
        aproducttemplate.

        Thisisimportanttopreventbecausechangingthetypewouldmake
        existingcombinationsinvalidwithoutrecomputingthem,andrecomputing
        themmighttaketoolongandwedon'twanttochangeproductswithout
        theuserknowingaboutit."""
        if'create_variant'invals:
            forpainself:
                ifvals['create_variant']!=pa.create_variantandpa.is_used_on_products:
                    raiseUserError(
                        _("YoucannotchangetheVariantsCreationModeoftheattribute%sbecauseitisusedonthefollowingproducts:\n%s")%
                        (pa.display_name,",".join(pa.product_tmpl_ids.mapped('display_name')))
                    )
        invalidate_cache='sequence'invalsandany(record.sequence!=vals['sequence']forrecordinself)
        res=super(ProductAttribute,self).write(vals)
        ifinvalidate_cache:
            #prefetchedo2mhavetoberesequenced
            #(eg.product.template:attribute_line_ids)
            self.flush()
            self.invalidate_cache()
        returnres

    defunlink(self):
        forpainself:
            ifpa.is_used_on_products:
                raiseUserError(
                    _("Youcannotdeletetheattribute%sbecauseitisusedonthefollowingproducts:\n%s")%
                    (pa.display_name,",".join(pa.product_tmpl_ids.mapped('display_name')))
                )
        returnsuper(ProductAttribute,self).unlink()


classProductAttributeValue(models.Model):
    _name="product.attribute.value"
    #ifyouchangethis_order,keepitinsyncwiththemethod
    #`_sort_key_variant`in`product.template'
    _order='attribute_id,sequence,id'
    _description='AttributeValue'

    name=fields.Char(string='Value',required=True,translate=True)
    sequence=fields.Integer(string='Sequence',help="Determinethedisplayorder",index=True)
    attribute_id=fields.Many2one('product.attribute',string="Attribute",ondelete='cascade',required=True,index=True,
        help="Theattributecannotbechangedoncethevalueisusedonatleastoneproduct.")

    pav_attribute_line_ids=fields.Many2many('product.template.attribute.line',string="Lines",
        relation='product_attribute_value_product_template_attribute_line_rel',copy=False)
    is_used_on_products=fields.Boolean('UsedonProducts',compute='_compute_is_used_on_products')

    is_custom=fields.Boolean('Iscustomvalue',help="Allowuserstoinputcustomvaluesforthisattributevalue")
    html_color=fields.Char(
        string='Color',
        help="HereyoucansetaspecificHTMLcolorindex(e.g.#ff0000)todisplaythecoloriftheattributetypeis'Color'.")
    display_type=fields.Selection(related='attribute_id.display_type',readonly=True)

    _sql_constraints=[
        ('value_company_uniq','unique(name,attribute_id)',"Youcannotcreatetwovalueswiththesamenameforthesameattribute.")
    ]

    @api.depends('pav_attribute_line_ids')
    def_compute_is_used_on_products(self):
        forpavinself:
            pav.is_used_on_products=bool(pav.pav_attribute_line_ids)

    defname_get(self):
        """Overridebecauseingeneralthenameofthevalueisconfusingifit
        isdisplayedwithoutthenameofthecorrespondingattribute.
        Eg.onproductlist&kanbanviews,onBOMformview

        Howeverduringvariantsetup(ontheproducttemplateform)thenameof
        theattributeisalreadyoneachlinesothereisnoneedtorepeatit
        oneveryvalue.
        """
        ifnotself._context.get('show_attribute',True):
            returnsuper(ProductAttributeValue,self).name_get()
        return[(value.id,"%s:%s"%(value.attribute_id.name,value.name))forvalueinself]

    defwrite(self,values):
        if'attribute_id'invalues:
            forpavinself:
                ifpav.attribute_id.id!=values['attribute_id']andpav.is_used_on_products:
                    raiseUserError(
                        _("Youcannotchangetheattributeofthevalue%sbecauseitisusedonthefollowingproducts:%s")%
                        (pav.display_name,",".join(pav.pav_attribute_line_ids.product_tmpl_id.mapped('display_name')))
                    )

        invalidate_cache='sequence'invaluesandany(record.sequence!=values['sequence']forrecordinself)
        res=super(ProductAttributeValue,self).write(values)
        ifinvalidate_cache:
            #prefetchedo2mhavetoberesequenced
            #(eg.product.template.attribute.line:value_ids)
            self.flush()
            self.invalidate_cache()
        returnres

    defunlink(self):
        forpavinself:
            ifpav.is_used_on_products:
                raiseUserError(
                    _("Youcannotdeletethevalue%sbecauseitisusedonthefollowingproducts:\n%s\n"
                      "Ifthevaluehasbeenassociatedtoaproductinthepast,youwillnotbeabletodeleteit.")%
                    (pav.display_name,",".join(pav.pav_attribute_line_ids.product_tmpl_id.mapped('display_name')))
                )
            linked_products=pav.env['product.template.attribute.value'].search([('product_attribute_value_id','=',pav.id)]).with_context(active_test=False).ptav_product_variant_ids
            unlinkable_products=linked_products._filter_to_unlink()
            iflinked_products!=unlinkable_products:
                raiseUserError(_("Youcannotdeletevalue%sbecauseitwasusedinsomeproducts.",pav.display_name))
        returnsuper(ProductAttributeValue,self).unlink()

    def_without_no_variant_attributes(self):
        returnself.filtered(lambdapav:pav.attribute_id.create_variant!='no_variant')


classProductTemplateAttributeLine(models.Model):
    """Attributesavailableonproduct.templatewiththeirselectedvaluesinam2m.
    Usedasaconfigurationmodeltogeneratetheappropriateproduct.template.attribute.value"""

    _name="product.template.attribute.line"
    _rec_name='attribute_id'
    _description='ProductTemplateAttributeLine'
    _order='attribute_id,id'

    active=fields.Boolean(default=True)
    product_tmpl_id=fields.Many2one('product.template',string="ProductTemplate",ondelete='cascade',required=True,index=True)
    attribute_id=fields.Many2one('product.attribute',string="Attribute",ondelete='restrict',required=True,index=True)
    value_ids=fields.Many2many('product.attribute.value',string="Values",domain="[('attribute_id','=',attribute_id)]",
        relation='product_attribute_value_product_template_attribute_line_rel',ondelete='restrict')
    product_template_value_ids=fields.One2many('product.template.attribute.value','attribute_line_id',string="ProductAttributeValues")

    @api.onchange('attribute_id')
    def_onchange_attribute_id(self):
        self.value_ids=self.value_ids.filtered(lambdapav:pav.attribute_id==self.attribute_id)

    @api.constrains('active','value_ids','attribute_id')
    def_check_valid_values(self):
        forptalinself:
            ifptal.activeandnotptal.value_ids:
                raiseValidationError(
                    _("Theattribute%smusthaveatleastonevaluefortheproduct%s.")%
                    (ptal.attribute_id.display_name,ptal.product_tmpl_id.display_name)
                )
            forpavinptal.value_ids:
                ifpav.attribute_id!=ptal.attribute_id:
                    raiseValidationError(
                        _("Ontheproduct%syoucannotassociatethevalue%swiththeattribute%sbecausetheydonotmatch.")%
                        (ptal.product_tmpl_id.display_name,pav.display_name,ptal.attribute_id.display_name)
                    )
        returnTrue

    @api.model_create_multi
    defcreate(self,vals_list):
        """Overrideto:
        -Activatearchivedlineshavingthesameconfiguration(iftheyexist)
            insteadofcreatingnewlines.
        -Setuprelatedvaluesandrelatedvariants.

        Reactivatingexistinglinesallowstore-useexistingvariantswhen
        possible,keepingtheirconfigurationandavoidingduplication.
        """
        create_values=[]
        activated_lines=self.env['product.template.attribute.line']
        forvalueinvals_list:
            vals=dict(value,active=value.get('active',True))
            #Whilenotidealforpeformance,thissearchhastobedoneateach
            #steptoexcludethelinesthatmighthavebeenactivatedata
            #previousstep.Since`vals_list`willlikelybeasmalllistin
            #allusecases,thisisanacceptabletrade-off.
            archived_ptal=self.search([
                ('active','=',False),
                ('product_tmpl_id','=',vals.pop('product_tmpl_id',0)),
                ('attribute_id','=',vals.pop('attribute_id',0)),
            ],limit=1)
            ifarchived_ptal:
                #Writegiven`vals`inadditionof`active`toensure
                #`value_ids`orotherfieldspassedto`create`aresavedtoo,
                #butchangethecontexttoavoidupdatingthevaluesandthe
                #variantsuntilalltheexpectedlinesarecreated/updated.
                archived_ptal.with_context(update_product_template_attribute_values=False).write(vals)
                activated_lines+=archived_ptal
            else:
                create_values.append(value)
        res=activated_lines+super(ProductTemplateAttributeLine,self).create(create_values)
        res._update_product_template_attribute_values()
        returnres

    defwrite(self,values):
        """Overrideto:
        -Addconstraintstopreventdoingchangesthatarenotsupportedsuch
            asmodifyingthetemplateortheattributeofexistinglines.
        -Cleanuprelatedvaluesandrelatedvariantswhenarchivingorwhen
            updating`value_ids`.
        """
        if'product_tmpl_id'invalues:
            forptalinself:
                ifptal.product_tmpl_id.id!=values['product_tmpl_id']:
                    raiseUserError(
                        _("Youcannotmovetheattribute%sfromtheproduct%stotheproduct%s.")%
                        (ptal.attribute_id.display_name,ptal.product_tmpl_id.display_name,values['product_tmpl_id'])
                    )

        if'attribute_id'invalues:
            forptalinself:
                ifptal.attribute_id.id!=values['attribute_id']:
                    raiseUserError(
                        _("Ontheproduct%syoucannottransformtheattribute%sintotheattribute%s.")%
                        (ptal.product_tmpl_id.display_name,ptal.attribute_id.display_name,values['attribute_id'])
                    )
        #Removeallvalueswhilearchivingtomakesurethelineiscleanifit
        #iseveractivatedagain.
        ifnotvalues.get('active',True):
            values['value_ids']=[(5,0,0)]
        res=super(ProductTemplateAttributeLine,self).write(values)
        if'active'invalues:
            self.flush()
            self.env['product.template'].invalidate_cache(fnames=['attribute_line_ids'])
        #Ifcomingfrom`create`,noneedtoupdatethevaluesandthevariants
        #beforealllinesarecreated.
        ifself.env.context.get('update_product_template_attribute_values',True):
            self._update_product_template_attribute_values()
        returnres

    defunlink(self):
        """Overrideto:
        -Archivethelineifunlinkisnotpossible.
        -Cleanuprelatedvaluesandrelatedvariants.

        Archivingistypicallyneededwhenthelinehasvaluesthatcan'tbe
        deletedbecausetheyarereferencedelsewhere(onavariantthatcan't
        bedeleted,onasalesorderline,...).
        """
        #Trytoremovethevaluesfirsttoremovesomepotentiallyblocking
        #references,whichtypicallyworks:
        #-Forsinglevaluelinesbecausethevaluesaredirectlyremovedfrom
        #  thevariants.
        #-Forvaluesthatarepresentonvariantsthatcanbedeleted.
        self.product_template_value_ids._only_active().unlink()
        #Keepareferencetotherelatedtemplatesbeforethedeletion.
        templates=self.product_tmpl_id
        #Nowdeleteorarchivethelines.
        ptal_to_archive=self.env['product.template.attribute.line']
        forptalinself:
            try:
                withself.env.cr.savepoint(),tools.mute_logger('flectra.sql_db'):
                    super(ProductTemplateAttributeLine,ptal).unlink()
            exceptException:
                #Wecatchallkindofexceptionstobesurethattheoperation
                #doesn'tfail.
                ptal_to_archive+=ptal
        ptal_to_archive.write({'active':False})
        #Forarchivedlines`_update_product_template_attribute_values`is
        #implicitlycalledduringthe`write`above,butforproductsthatused
        #unlinkedlines`_create_variant_ids`hastobecalledmanually.
        (templates-ptal_to_archive.product_tmpl_id)._create_variant_ids()
        returnTrue

    def_update_product_template_attribute_values(self):
        """Createorunlink`product.template.attribute.value`foreachlinein
        `self`basedon`value_ids`.

        Thegoalistodeleteallvaluesthatarenotin`value_ids`,to
        activatethosein`value_ids`thatarecurrentlyarchived,andtocreate
        thosein`value_ids`thatdidn'texist.

        Thisisatrickfortheformviewandforperformanceingeneral,
        becausewedon'twanttogenerateinadvanceallpossiblevaluesforall
        templates,butonlythosethatwillbeselected.
        """
        ProductTemplateAttributeValue=self.env['product.template.attribute.value']
        ptav_to_create=[]
        ptav_to_unlink=ProductTemplateAttributeValue
        forptalinself:
            ptav_to_activate=ProductTemplateAttributeValue
            remaining_pav=ptal.value_ids
            forptavinptal.product_template_value_ids:
                ifptav.product_attribute_value_idnotinremaining_pav:
                    #Removevaluesthatexistedbutdon'texistanymore,but
                    #ignorethosethatarealreadyarchivedbecauseiftheyare
                    #archiveditmeanstheycouldnotbedeletedpreviously.
                    ifptav.ptav_active:
                        ptav_to_unlink+=ptav
                else:
                    #Activatecorrespondingvaluesthatarecurrentlyarchived.
                    remaining_pav-=ptav.product_attribute_value_id
                    ifnotptav.ptav_active:
                        ptav_to_activate+=ptav

            forpavinremaining_pav:
                #Thepreviousloopsearchedforarchivedvaluesthatbelongedto
                #thecurrentline,butifthelinewasdeletedandanotherline
                #wasrecreatedforthesameattribute,weneedtoexpandthe
                #searchtothosewithmatching`attribute_id`.
                #Whilenotidealforpeformance,thissearchhastobedoneat
                #eachsteptoexcludethevaluesthatmighthavebeenactivated
                #atapreviousstep.Since`remaining_pav`willlikelybea
                #smalllistinallusecases,thisisanacceptabletrade-off.
                ptav=ProductTemplateAttributeValue.search([
                    ('ptav_active','=',False),
                    ('product_tmpl_id','=',ptal.product_tmpl_id.id),
                    ('attribute_id','=',ptal.attribute_id.id),
                    ('product_attribute_value_id','=',pav.id),
                ],limit=1)
                ifptav:
                    ptav.write({'ptav_active':True,'attribute_line_id':ptal.id})
                    #Ifthevaluewasmarkedfordeletion,nowkeepit.
                    ptav_to_unlink-=ptav
                else:
                    #createvaluesthatdidn'texistyet
                    ptav_to_create.append({
                        'product_attribute_value_id':pav.id,
                        'attribute_line_id':ptal.id
                    })
            #Handleactiveateachstepincaseafollowinglinemightwantto
            #re-useavaluethatwasarchivedatapreviousstep.
            ptav_to_activate.write({'ptav_active':True})
            ptav_to_unlink.write({'ptav_active':False})
        ifptav_to_unlink:
            ptav_to_unlink.unlink()
        ProductTemplateAttributeValue.create(ptav_to_create)
        self.product_tmpl_id._create_variant_ids()

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        #TDEFIXME:currentlyoverridingthedomain;howeverasitincludesa
        #searchonam2oandoneonam2m,probablythiswillquicklybecome
        #difficulttocompute-checkifperformanceoptimizationisrequired
        ifnameandoperatorin('=','ilike','=ilike','like','=like'):
            args=argsor[]
            domain=['|',('attribute_id',operator,name),('value_ids',operator,name)]
            returnself._search(expression.AND([domain,args]),limit=limit,access_rights_uid=name_get_uid)
        returnsuper(ProductTemplateAttributeLine,self)._name_search(name=name,args=args,operator=operator,limit=limit,name_get_uid=name_get_uid)

    def_without_no_variant_attributes(self):
        returnself.filtered(lambdaptal:ptal.attribute_id.create_variant!='no_variant')


classProductTemplateAttributeValue(models.Model):
    """Materializedrelationshipbetweenattributevalues
    andproducttemplategeneratedbytheproduct.template.attribute.line"""

    _name="product.template.attribute.value"
    _description="ProductTemplateAttributeValue"
    _order='attribute_line_id,product_attribute_value_id,id'

    #Notjust`active`becausewealwayswanttoshowthevaluesexceptin
    #specificcase,asopposedto`active_test`.
    ptav_active=fields.Boolean("Active",default=True)
    name=fields.Char('Value',related="product_attribute_value_id.name")

    #definingfields:theproducttemplateattributelineandtheproductattributevalue
    product_attribute_value_id=fields.Many2one(
        'product.attribute.value',string='AttributeValue',
        required=True,ondelete='cascade',index=True)
    attribute_line_id=fields.Many2one('product.template.attribute.line',required=True,ondelete='cascade',index=True)

    #configurationfields:theprice_extraandtheexclusionrules
    price_extra=fields.Float(
        string="ValuePriceExtra",
        default=0.0,
        digits='ProductPrice',
        help="Extrapriceforthevariantwiththisattributevalueonsaleprice.eg.200priceextra,1000+200=1200.")
    currency_id=fields.Many2one(related='attribute_line_id.product_tmpl_id.currency_id')

    exclude_for=fields.One2many(
        'product.template.attribute.exclusion',
        'product_template_attribute_value_id',
        string="Excludefor",
        help="Makethisattributevaluenotcompatiblewith"
             "othervaluesoftheproductorsomeattributevaluesofoptionalandaccessoryproducts.")

    #relatedfields:producttemplateandproductattribute
    product_tmpl_id=fields.Many2one('product.template',string="ProductTemplate",related='attribute_line_id.product_tmpl_id',store=True,index=True)
    attribute_id=fields.Many2one('product.attribute',string="Attribute",related='attribute_line_id.attribute_id',store=True,index=True)
    ptav_product_variant_ids=fields.Many2many('product.product',relation='product_variant_combination',string="RelatedVariants",readonly=True)

    html_color=fields.Char('HTMLColorIndex',related="product_attribute_value_id.html_color")
    is_custom=fields.Boolean('Iscustomvalue',related="product_attribute_value_id.is_custom")
    display_type=fields.Selection(related='product_attribute_value_id.display_type',readonly=True)

    _sql_constraints=[
        ('attribute_value_unique','unique(attribute_line_id,product_attribute_value_id)',"Eachvalueshouldbedefinedonlyonceperattributeperproduct."),
    ]

    @api.constrains('attribute_line_id','product_attribute_value_id')
    def_check_valid_values(self):
        forptavinself:
            ifptav.product_attribute_value_idnotinptav.attribute_line_id.value_ids:
                raiseValidationError(
                    _("Thevalue%sisnotdefinedfortheattribute%sontheproduct%s.")%
                    (ptav.product_attribute_value_id.display_name,ptav.attribute_id.display_name,ptav.product_tmpl_id.display_name)
                )

    @api.model_create_multi
    defcreate(self,vals_list):
        ifany('ptav_product_variant_ids'invforvinvals_list):
            #Forcewriteonthisrelationfrom`product.product`toproperly
            #trigger`_compute_combination_indices`.
            raiseUserError(_("Youcannotupdaterelatedvariantsfromthevalues.Pleaseupdaterelatedvaluesfromthevariants."))
        returnsuper(ProductTemplateAttributeValue,self).create(vals_list)

    defwrite(self,values):
        if'ptav_product_variant_ids'invalues:
            #Forcewriteonthisrelationfrom`product.product`toproperly
            #trigger`_compute_combination_indices`.
            raiseUserError(_("Youcannotupdaterelatedvariantsfromthevalues.Pleaseupdaterelatedvaluesfromthevariants."))
        pav_in_values='product_attribute_value_id'invalues
        product_in_values='product_tmpl_id'invalues
        ifpav_in_valuesorproduct_in_values:
            forptavinself:
                ifpav_in_valuesandptav.product_attribute_value_id.id!=values['product_attribute_value_id']:
                    raiseUserError(
                        _("Youcannotchangethevalueofthevalue%ssetonproduct%s.")%
                        (ptav.display_name,ptav.product_tmpl_id.display_name)
                    )
                ifproduct_in_valuesandptav.product_tmpl_id.id!=values['product_tmpl_id']:
                    raiseUserError(
                        _("Youcannotchangetheproductofthevalue%ssetonproduct%s.")%
                        (ptav.display_name,ptav.product_tmpl_id.display_name)
                    )
        res=super(ProductTemplateAttributeValue,self).write(values)
        if'exclude_for'invalues:
            self.product_tmpl_id._create_variant_ids()
        returnres

    defunlink(self):
        """Overrideto:
        -Cleanupthevariantsthatuseanyofthevaluesinself:
            -Removethevaluefromthevariantifthevaluebelongedtoan
                attributelinewithonlyonevalue.
            -Unlinkorarchiveallrelatedvariants.
        -Archivethevalueifunlinkisnotpossible.

        Archivingistypicallyneededwhenthevalueisreferencedelsewhere
        (onavariantthatcan'tbedeleted,onasalesorderline,...).
        """
        #Directlyremovethevaluesfromthevariantsforlinesthathadsingle
        #value(countingalsothevaluesthatarearchived).
        single_values=self.filtered(lambdaptav:len(ptav.attribute_line_id.product_template_value_ids)==1)
        forptavinsingle_values:
            ptav.ptav_product_variant_ids.write({'product_template_attribute_value_ids':[(3,ptav.id,0)]})
        #Trytoremovethevariantsbeforedeletingtopotentiallyremovesome
        #blockingreferences.
        self.ptav_product_variant_ids._unlink_or_archive()
        #Nowdeleteorarchivethevalues.
        ptav_to_archive=self.env['product.template.attribute.value']
        forptavinself:
            try:
                withself.env.cr.savepoint(),tools.mute_logger('flectra.sql_db'):
                    super(ProductTemplateAttributeValue,ptav).unlink()
            exceptException:
                #Wecatchallkindofexceptionstobesurethattheoperation
                #doesn'tfail.
                ptav_to_archive+=ptav
        ptav_to_archive.write({'ptav_active':False})
        returnTrue

    defname_get(self):
        """Overridebecauseingeneralthenameofthevalueisconfusingifit
        isdisplayedwithoutthenameofthecorrespondingattribute.
        Eg.onexclusionrulesform
        """
        return[(value.id,"%s:%s"%(value.attribute_id.name,value.name))forvalueinself]

    def_only_active(self):
        returnself.filtered(lambdaptav:ptav.ptav_active)

    def_without_no_variant_attributes(self):
        returnself.filtered(lambdaptav:ptav.attribute_id.create_variant!='no_variant')

    def_ids2str(self):
        return','.join([str(i)foriinsorted(self.ids)])

    def_get_combination_name(self):
        """Excludevaluesfromsinglevaluelinesorfromno_variantattributes."""
        ptavs=self._without_no_variant_attributes().with_prefetch(self._prefetch_ids)
        ptavs=ptavs._filter_single_value_lines().with_prefetch(self._prefetch_ids)
        return",".join([ptav.nameforptavinptavs])

    def_filter_single_value_lines(self):
        """Return`self`withvaluesfromsinglevaluelinesfilteredout
        dependingontheactivestateofallthevaluesin`self`.

        Ifanyvaluein`self`isarchived,archivedvaluesarealsotakeninto
        accountwhencheckingforsinglevalues.
        Thisallowstodisplaythecorrectnameforarchivedvariants.

        Ifallvaluesin`self`areactive,onlyactivevaluesaretakeninto
        accountwhencheckingforsinglevalues.
        Thisallowstodisplaythecorrectnameforactivecombinations.
        """
        only_active=all(ptav.ptav_activeforptavinself)
        returnself.filtered(lambdaptav:notptav._is_from_single_value_line(only_active))

    def_is_from_single_value_line(self,only_active=True):
        """Returnwhether`self`isfromasinglevalueline,countingalso
        archivedvaluesif`only_active`isFalse.
        """
        self.ensure_one()
        all_values=self.attribute_line_id.product_template_value_ids
        ifonly_active:
            all_values=all_values._only_active()
        returnlen(all_values)==1


classProductTemplateAttributeExclusion(models.Model):
    _name="product.template.attribute.exclusion"
    _description='ProductTemplateAttributeExclusion'
    _order='product_tmpl_id,id'

    product_template_attribute_value_id=fields.Many2one(
        'product.template.attribute.value',string="AttributeValue",ondelete='cascade',index=True)
    product_tmpl_id=fields.Many2one(
        'product.template',string='ProductTemplate',ondelete='cascade',required=True,index=True)
    value_ids=fields.Many2many(
        'product.template.attribute.value',relation="product_attr_exclusion_value_ids_rel",
        string='AttributeValues',domain="[('product_tmpl_id','=',product_tmpl_id),('ptav_active','=',True)]")


classProductAttributeCustomValue(models.Model):
    _name="product.attribute.custom.value"
    _description='ProductAttributeCustomValue'
    _order='custom_product_template_attribute_value_id,id'

    name=fields.Char("Name",compute='_compute_name')
    custom_product_template_attribute_value_id=fields.Many2one('product.template.attribute.value',string="AttributeValue",required=True,ondelete='restrict')
    custom_value=fields.Char("CustomValue")

    @api.depends('custom_product_template_attribute_value_id.name','custom_value')
    def_compute_name(self):
        forrecordinself:
            name=(record.custom_valueor'').strip()
            ifrecord.custom_product_template_attribute_value_id.display_name:
                name="%s:%s"%(record.custom_product_template_attribute_value_id.display_name,name)
            record.name=name
