#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportValidationError,UserError
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.addons.website.modelsimportir_http
fromflectra.tools.translateimporthtml_translate
fromflectra.osvimportexpression
frompsycopg2.extrasimportexecute_values

_logger=logging.getLogger(__name__)


classProductRibbon(models.Model):
    _name="product.ribbon"
    _description='Productribbon'

    defname_get(self):
        return[(ribbon.id,'%s(#%d)'%(tools.html2plaintext(ribbon.html),ribbon.id))forribboninself]

    html=fields.Char(string='Ribbonhtml',required=True,translate=True)
    bg_color=fields.Char(string='Ribbonbackgroundcolor',required=False)
    text_color=fields.Char(string='Ribbontextcolor',required=False)
    html_class=fields.Char(string='Ribbonclass',required=True,default='')


classProductPricelist(models.Model):
    _inherit="product.pricelist"

    def_default_website(self):
        """Findthefirstcompany'swebsite,ifthereisone."""
        company_id=self.env.company.id

        ifself._context.get('default_company_id'):
            company_id=self._context.get('default_company_id')

        domain=[('company_id','=',company_id)]
        returnself.env['website'].search(domain,limit=1)

    website_id=fields.Many2one('website',string="Website",ondelete='restrict',default=_default_website,domain="[('company_id','=?',company_id)]")
    code=fields.Char(string='E-commercePromotionalCode',groups="base.group_user")
    selectable=fields.Boolean(help="Allowtheendusertochoosethispricelist")

    defclear_cache(self):
        #website._get_pl_partner_order()iscachedtoavoidtorecomputeateachrequestthe
        #listofavailablepricelists.So,weneedtoinvalidatethecachewhen
        #wechangetheconfigofwebsitepricelisttoforcetorecompute.
        website=self.env['website']
        website._get_pl_partner_order.clear_cache(website)

    @api.model
    defcreate(self,data):
        ifdata.get('company_id')andnotdata.get('website_id'):
            #l10nmodulesinstallwillchangethecompanycurrency,creatinga
            #pricelistforthatcurrency.Donotuseuser'scompanyinthat
            #caseasmoduleinstallaredonewithFlectraBot(company1)
            self=self.with_context(default_company_id=data['company_id'])
        res=super(ProductPricelist,self).create(data)
        self.clear_cache()
        returnres

    defwrite(self,data):
        res=super(ProductPricelist,self).write(data)
        ifdata.keys()&{'code','active','website_id','selectable','company_id'}:
            self._check_website_pricelist()
        self.clear_cache()
        returnres

    defunlink(self):
        res=super(ProductPricelist,self).unlink()
        self._check_website_pricelist()
        self.clear_cache()
        returnres

    def_get_partner_pricelist_multi_search_domain_hook(self,company_id):
        domain=super(ProductPricelist,self)._get_partner_pricelist_multi_search_domain_hook(company_id)
        website=ir_http.get_request_website()
        ifwebsite:
            domain+=self._get_website_pricelists_domain(website.id)
        returndomain

    def_get_partner_pricelist_multi_filter_hook(self):
        res=super(ProductPricelist,self)._get_partner_pricelist_multi_filter_hook()
        website=ir_http.get_request_website()
        ifwebsite:
            res=res.filtered(lambdapl:pl._is_available_on_website(website.id))
        returnres

    def_check_website_pricelist(self):
        forwebsiteinself.env['website'].search([]):
            #sudo()tobeabletoreadpricelists/websitefromanothercompany
            ifnotwebsite.sudo().pricelist_ids:
                raiseUserError(_("Withthisaction,'%s'websitewouldnothaveanypricelistavailable.")%(website.name))

    def_is_available_on_website(self,website_id):
        """Tobeabletobeusedonawebsite,apricelistshouldeither:
        -Haveits`website_id`settocurrentwebsite(specificpricelist).
        -Haveno`website_id`setandshouldbe`selectable`(genericpricelist)
          orshouldhavea`code`(genericpromotion).
        -Haveno`company_id`ora`company_id`matchingitswebsiteone.

        Note:Apricelistwithoutawebsite_id,notselectableandwithouta
              codeisabackendpricelist.

        Changeinthismethodshouldbereflectedin`_get_website_pricelists_domain`.
        """
        self.ensure_one()
        ifself.company_idandself.company_id!=self.env["website"].browse(website_id).company_id:
            returnFalse
        returnself.website_id.id==website_idor(notself.website_idand(self.selectableorself.sudo().code))

    def_get_website_pricelists_domain(self,website_id):
        '''Checkabove`_is_available_on_website`forexplanation.
        Changeinthismethodshouldbereflectedin`_is_available_on_website`.
        '''
        company_id=self.env["website"].browse(website_id).company_id.id
        return[
            '&',('company_id','in',[False,company_id]),
            '|',('website_id','=',website_id),
            '&',('website_id','=',False),
            '|',('selectable','=',True),('code','!=',False),
        ]

    def_get_partner_pricelist_multi(self,partner_ids,company_id=None):
        '''If`property_product_pricelist`isreadfromwebsite,weshoulduse
            thewebsite'scompanyandnottheuser'sone.
            Passinga`company_id`tosuperwillavoidusingthecurrentuser's
            company.
        '''
        website=ir_http.get_request_website()
        ifnotcompany_idandwebsite:
            company_id=website.company_id.id
        returnsuper(ProductPricelist,self)._get_partner_pricelist_multi(partner_ids,company_id)

    @api.constrains('company_id','website_id')
    def_check_websites_in_company(self):
        '''Preventmisconfigurationmulti-website/multi-companies.
           Iftherecordhasacompany,thewebsiteshouldbefromthatcompany.
        '''
        forrecordinself.filtered(lambdapl:pl.website_idandpl.company_id):
            ifrecord.website_id.company_id!=record.company_id:
                raiseValidationError(_("""Onlythecompany'swebsitesareallowed.\nLeavetheCompanyfieldemptyorselectawebsitefromthatcompany."""))


classProductPublicCategory(models.Model):
    _name="product.public.category"
    _inherit=["website.seo.metadata","website.multi.mixin",'image.mixin']
    _description="WebsiteProductCategory"
    _parent_store=True
    _order="sequence,name,id"

    def_default_sequence(self):
        cat=self.search([],limit=1,order="sequenceDESC")
        ifcat:
            returncat.sequence+5
        return10000

    name=fields.Char(required=True,translate=True)
    parent_id=fields.Many2one('product.public.category',string='ParentCategory',index=True,ondelete="cascade")
    parent_path=fields.Char(index=True)
    child_id=fields.One2many('product.public.category','parent_id',string='ChildrenCategories')
    parents_and_self=fields.Many2many('product.public.category',compute='_compute_parents_and_self')
    sequence=fields.Integer(help="Givesthesequenceorderwhendisplayingalistofproductcategories.",index=True,default=_default_sequence)
    website_description=fields.Html('CategoryDescription',sanitize_attributes=False,translate=html_translate,sanitize_form=False)
    product_tmpl_ids=fields.Many2many('product.template',relation='product_public_category_product_template_rel')

    @api.constrains('parent_id')
    defcheck_parent_id(self):
        ifnotself._check_recursion():
            raiseValueError(_('Error!Youcannotcreaterecursivecategories.'))

    defname_get(self):
        res=[]
        forcategoryinself:
            res.append((category.id,"/".join(category.parents_and_self.mapped('name'))))
        returnres

    def_compute_parents_and_self(self):
        forcategoryinself:
            ifcategory.parent_path:
                category.parents_and_self=self.env['product.public.category'].browse([int(p)forpincategory.parent_path.split('/')[:-1]])
            else:
                category.parents_and_self=category


classProductTemplate(models.Model):
    _inherit=["product.template","website.seo.metadata",'website.published.multi.mixin','rating.mixin']
    _name='product.template'
    _mail_post_access='read'
    _check_company_auto=True

    website_description=fields.Html('Descriptionforthewebsite',sanitize_attributes=False,translate=html_translate,sanitize_form=False)
    alternative_product_ids=fields.Many2many(
        'product.template','product_alternative_rel','src_id','dest_id',check_company=True,
        string='AlternativeProducts',help='Suggestalternativestoyourcustomer(upsellstrategy).'
                                            'Thoseproductsshowupontheproductpage.')
    accessory_product_ids=fields.Many2many(
        'product.product','product_accessory_rel','src_id','dest_id',string='AccessoryProducts',check_company=True,
        help='Accessoriesshowupwhenthecustomerreviewsthecartbeforepayment(cross-sellstrategy).')
    website_size_x=fields.Integer('SizeX',default=1)
    website_size_y=fields.Integer('SizeY',default=1)
    website_ribbon_id=fields.Many2one('product.ribbon',string='Ribbon')
    website_sequence=fields.Integer('WebsiteSequence',help="DeterminethedisplayorderintheWebsiteE-commerce",
                                      default=lambdaself:self._default_website_sequence(),copy=False)
    public_categ_ids=fields.Many2many(
        'product.public.category',relation='product_public_category_product_template_rel',
        string='WebsiteProductCategory',
        help="TheproductwillbeavailableineachmentionedeCommercecategory.GotoShop>"
             "Customizeandenable'eCommercecategories'toviewalleCommercecategories.")

    product_template_image_ids=fields.One2many('product.image','product_tmpl_id',string="ExtraProductMedia",copy=True)

    def_has_no_variant_attributes(self):
        """Returnwhetherthis`product.template`hasatleastoneno_variant
        attribute.

        :return:Trueifatleastoneno_variantattribute,Falseotherwise
        :rtype:bool
        """
        self.ensure_one()
        returnany(a.create_variant=='no_variant'forainself.valid_product_template_attribute_line_ids.attribute_id)

    def_has_is_custom_values(self):
        self.ensure_one()
        """Returnwhetherthis`product.template`hasatleastoneis_custom
        attributevalue.

        :return:Trueifatleastoneis_customattributevalue,Falseotherwise
        :rtype:bool
        """
        returnany(v.is_customforvinself.valid_product_template_attribute_line_ids.product_template_value_ids._only_active())

    def_get_possible_variants_sorted(self,parent_combination=None):
        """Returnthesortedrecordsetofvariantsthatarepossible.

        Theorderisbasedontheorderoftheattributesandtheirvalues.

        See`_get_possible_variants`forthelimitationsofthismethodwith
        dynamicorno_variantattributes,andalsoforawarningabout
        performances.

        :paramparent_combination:combinationfromwhich`self`isan
            optionaloraccessoryproduct
        :typeparent_combination:recordset`product.template.attribute.value`

        :return:thesortedvariantsthatarepossible
        :rtype:recordsetof`product.product`
        """
        self.ensure_one()

        def_sort_key_attribute_value(value):
            #ifyouchangethisorder,keepitinsyncwith_orderfrom`product.attribute`
            return(value.attribute_id.sequence,value.attribute_id.id)

        def_sort_key_variant(variant):
            """
                Weassumeallvariantswillhavethesameattributes,withonlyonevalueforeach.
                    -firstlevelsort:sameas"product.attribute"._order
                    -secondlevelsort:sameas"product.attribute.value"._order
            """
            keys=[]
            forattributeinvariant.product_template_attribute_value_ids.sorted(_sort_key_attribute_value):
                #ifyouchangethisorder,keepitinsyncwith_orderfrom`product.attribute.value`
                keys.append(attribute.product_attribute_value_id.sequence)
                keys.append(attribute.id)
            returnkeys

        returnself._get_possible_variants(parent_combination).sorted(_sort_key_variant)

    def_get_combination_info(self,combination=False,product_id=False,add_qty=1,pricelist=False,parent_combination=False,only_template=False):
        """Overrideforwebsite,wherewewantto:
            -takethewebsitepricelistifnopricelistisset
            -applytheb2b/b2csettingtotheresult

        Thiswillworkwhenaddingwebsite_idtothecontext,whichisdone
        automaticallywhencalledfromrouteswithwebsite=True.
        """
        self.ensure_one()

        current_website=False

        ifself.env.context.get('website_id'):
            current_website=self.env['website'].get_current_website()
            ifnotpricelist:
                pricelist=current_website.get_current_pricelist()

        combination_info=super(ProductTemplate,self)._get_combination_info(
            combination=combination,product_id=product_id,add_qty=add_qty,pricelist=pricelist,
            parent_combination=parent_combination,only_template=only_template)

        ifself.env.context.get('website_id'):
            partner=self.env.user.partner_id
            company_id=current_website.company_id
            product=self.env['product.product'].browse(combination_info['product_id'])orself

            tax_display=self.user_has_groups('account.group_show_line_subtotals_tax_excluded')and'total_excluded'or'total_included'
            fpos=self.env['account.fiscal.position'].sudo().get_fiscal_position(partner.id)
            taxes=fpos.map_tax(product.sudo().taxes_id.filtered(lambdax:x.company_id==company_id),product,partner)

            #Thelist_priceisalwaysthepriceofone.
            quantity_1=1
            combination_info['price']=self.env['account.tax']._fix_tax_included_price_company(combination_info['price'],product.sudo().taxes_id,taxes,company_id)
            price=taxes.compute_all(combination_info['price'],pricelist.currency_id,quantity_1,product,partner)[tax_display]
            ifpricelist.discount_policy=='without_discount':
                combination_info['list_price']=self.env['account.tax']._fix_tax_included_price_company(combination_info['list_price'],product.sudo().taxes_id,taxes,company_id)
                list_price=taxes.compute_all(combination_info['list_price'],pricelist.currency_id,quantity_1,product,partner)[tax_display]
            else:
                list_price=price
            combination_info['price_extra']=self.env['account.tax']._fix_tax_included_price_company(combination_info['price_extra'],product.sudo().taxes_id,taxes,company_id)
            price_extra=taxes.compute_all(combination_info['price_extra'],pricelist.currency_id,quantity_1,product,partner)[tax_display]
            has_discounted_price=pricelist.currency_id.compare_amounts(list_price,price)==1

            combination_info.update(
                price=price,
                list_price=list_price,
                price_extra=price_extra,
                has_discounted_price=has_discounted_price,
            )

        returncombination_info

    def_get_image_holder(self):
        """Returnstheholderoftheimagetouseasdefaultrepresentation.
        Iftheproducttemplatehasanimageitistheproducttemplate,
        otherwiseiftheproducthasvariantsitisthefirstvariant

        :return:thisproducttemplateorthefirstproductvariant
        :rtype:recordsetof'product.template'orrecordsetof'product.product'
        """
        self.ensure_one()
        ifself.image_128:
            returnself
        variant=self.env['product.product'].browse(self._get_first_possible_variant_id())
        #ifthevarianthasnoimageanyway,sparesomequeriesbyusingtemplate
        returnvariantifvariant.image_variant_128elseself

    def_get_current_company_fallback(self,**kwargs):
        """Override:ifawebsiteissetontheproductorgiven,fallbackto
        thecompanyofthewebsite.Otherwiseusetheonefromparentmethod."""
        res=super(ProductTemplate,self)._get_current_company_fallback(**kwargs)
        website=self.website_idorkwargs.get('website')
        returnwebsiteandwebsite.company_idorres

    def_init_column(self,column_name):
        #toavoidgeneratingasingledefaultwebsite_sequencewheninstallingthemodule,
        #weneedtosetthedefaultrowbyrowforthiscolumn
        ifcolumn_name=="website_sequence":
            _logger.debug("Table'%s':settingdefaultvalueofnewcolumn%stouniquevaluesforeachrow",self._table,column_name)
            self.env.cr.execute("SELECTidFROM%sWHEREwebsite_sequenceISNULL"%self._table)
            prod_tmpl_ids=self.env.cr.dictfetchall()
            max_seq=self._default_website_sequence()
            query="""
                UPDATE{table}
                SETwebsite_sequence=p.web_seq
                FROM(VALUES%s)ASp(p_id,web_seq)
                WHEREid=p.p_id
            """.format(table=self._table)
            values_args=[(prod_tmpl['id'],max_seq+i*5)fori,prod_tmplinenumerate(prod_tmpl_ids)]
            execute_values(self.env.cr._obj,query,values_args)
        else:
            super(ProductTemplate,self)._init_column(column_name)

    def_default_website_sequence(self):
        '''Wewantnewproducttobethelast(highestseq).
        Everyproductshouldideallyhaveanuniquesequence.
        Defaultsequence(10000)shouldonlybeusedforDBfirstproduct.
        Aswedon'tresequencethewholetree(as`sequence`does),thisfield
        mighthavenegativevalue.
        '''
        self._cr.execute("SELECTMAX(website_sequence)FROM%s"%self._table)
        max_sequence=self._cr.fetchone()[0]
        ifmax_sequenceisNone:
            return10000
        returnmax_sequence+5

    defset_sequence_top(self):
        min_sequence=self.sudo().search([],order='website_sequenceASC',limit=1)
        self.website_sequence=min_sequence.website_sequence-5

    defset_sequence_bottom(self):
        max_sequence=self.sudo().search([],order='website_sequenceDESC',limit=1)
        self.website_sequence=max_sequence.website_sequence+5

    defset_sequence_up(self):
        previous_product_tmpl=self.sudo().search([
            ('website_sequence','<',self.website_sequence),
            ('website_published','=',self.website_published),
        ],order='website_sequenceDESC',limit=1)
        ifprevious_product_tmpl:
            previous_product_tmpl.website_sequence,self.website_sequence=self.website_sequence,previous_product_tmpl.website_sequence
        else:
            self.set_sequence_top()

    defset_sequence_down(self):
        next_prodcut_tmpl=self.search([
            ('website_sequence','>',self.website_sequence),
            ('website_published','=',self.website_published),
        ],order='website_sequenceASC',limit=1)
        ifnext_prodcut_tmpl:
            next_prodcut_tmpl.website_sequence,self.website_sequence=self.website_sequence,next_prodcut_tmpl.website_sequence
        else:
            returnself.set_sequence_bottom()

    def_default_website_meta(self):
        res=super(ProductTemplate,self)._default_website_meta()
        res['default_opengraph']['og:description']=res['default_twitter']['twitter:description']=self.description_sale
        res['default_opengraph']['og:title']=res['default_twitter']['twitter:title']=self.name
        res['default_opengraph']['og:image']=res['default_twitter']['twitter:image']=self.env['website'].image_url(self,'image_1024')
        res['default_meta_description']=self.description_sale
        returnres

    def_compute_website_url(self):
        super(ProductTemplate,self)._compute_website_url()
        forproductinself:
            ifproduct.id:
                product.website_url="/shop/%s"%slug(product)

    #---------------------------------------------------------
    #RatingMixinAPI
    #---------------------------------------------------------

    def_rating_domain(self):
        """Onlytakethepublishedratingintoaccounttocomputeavgandcount"""
        domain=super(ProductTemplate,self)._rating_domain()
        returnexpression.AND([domain,[('is_internal','=',False)]])

    def_get_images(self):
        """Returnalistofrecordsimplementing`image.mixin`to
        displayonthecarouselonthewebsiteforthistemplate.

        Thisreturnsalistandnotarecordsetbecausetherecordsmightbe
        fromdifferentmodels(templateandimage).

        Itcontainsinthisorder:themainimageofthetemplateandthe
        TemplateExtraImages.
        """
        self.ensure_one()
        return[self]+list(self.product_template_image_ids)


classProduct(models.Model):
    _inherit="product.product"

    website_id=fields.Many2one(related='product_tmpl_id.website_id',readonly=False)

    product_variant_image_ids=fields.One2many('product.image','product_variant_id',string="ExtraVariantImages")

    website_url=fields.Char('WebsiteURL',compute='_compute_product_website_url',help='ThefullURLtoaccessthedocumentthroughthewebsite.')

    @api.depends_context('lang')
    @api.depends('product_tmpl_id.website_url','product_template_attribute_value_ids')
    def_compute_product_website_url(self):
        forproductinself:
            attributes=','.join(str(x)forxinproduct.product_template_attribute_value_ids.ids)
            product.website_url="%s#attr=%s"%(product.product_tmpl_id.website_url,attributes)

    defwebsite_publish_button(self):
        self.ensure_one()
        returnself.product_tmpl_id.website_publish_button()

    defopen_website_url(self):
        self.ensure_one()
        res=self.product_tmpl_id.open_website_url()
        res['url']=self.website_url
        returnres

    def_get_images(self):
        """Returnalistofrecordsimplementing`image.mixin`to
        displayonthecarouselonthewebsiteforthisvariant.

        Thisreturnsalistandnotarecordsetbecausetherecordsmightbe
        fromdifferentmodels(template,variantandimage).

        Itcontainsinthisorder:themainimageofthevariant(ifset),the
        VariantExtraImages,andtheTemplateExtraImages.
        """
        self.ensure_one()
        variant_images=list(self.product_variant_image_ids)
        ifself.image_variant_1920:
            #ifthemainvariantimageisset,displayitfirst
            variant_images=[self]+variant_images
        else:
            #Ifthemainvariantimageisempty,itwillfallbacktotemplate
            #image,inthiscaseinsertitaftertheothervariantimages,so
            #thatallvariantimagesarefirstandalltemplateimageslast.
            variant_images=variant_images+[self]
        #[1:]toremovethemainimagefromthetemplate,weonlydisplay
        #thetemplateextraimageshere
        returnvariant_images+self.product_tmpl_id._get_images()[1:]

    def_is_add_to_cart_allowed(self):
        self.ensure_one()
        returnself.user_has_groups('base.group_system')or(self.sale_okandself.website_published)
