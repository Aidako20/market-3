#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromitertoolsimportchain

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.tools.miscimportformatLang,get_lang


classPricelist(models.Model):
    _name="product.pricelist"
    _description="Pricelist"
    _order="sequenceasc,iddesc"

    def_get_default_currency_id(self):
        returnself.env.company.currency_id.id

    name=fields.Char('PricelistName',required=True,translate=True)
    active=fields.Boolean('Active',default=True,help="Ifunchecked,itwillallowyoutohidethepricelistwithoutremovingit.")
    item_ids=fields.One2many(
        'product.pricelist.item','pricelist_id','PricelistItems',
        copy=True)
    currency_id=fields.Many2one('res.currency','Currency',default=_get_default_currency_id,required=True)
    company_id=fields.Many2one('res.company','Company')

    sequence=fields.Integer(default=16)
    country_group_ids=fields.Many2many('res.country.group','res_country_group_pricelist_rel',
                                         'pricelist_id','res_country_group_id',string='CountryGroups')

    discount_policy=fields.Selection([
        ('with_discount','Discountincludedintheprice'),
        ('without_discount','Showpublicprice&discounttothecustomer')],
        default='with_discount',required=True)

    defname_get(self):
        return[(pricelist.id,'%s(%s)'%(pricelist.name,pricelist.currency_id.name))forpricelistinself]

    @api.model
    def_name_search(self,name,args=None,operator='ilike',limit=100,name_get_uid=None):
        ifnameandoperator=='='andnotargs:
            #searchonthenameofthepricelistanditscurrency,oppositeofname_get(),
            #Usedbythemagiccontextfilterintheproductsearchview.
            query_args={'name':name,'limit':limit,'lang':get_lang(self.env).code}
            query="""SELECTp.id
                       FROM((
                                SELECTpr.id,pr.name
                                FROMproduct_pricelistprJOIN
                                     res_currencycurON
                                         (pr.currency_id=cur.id)
                                WHEREpr.name||'('||cur.name||')'=%(name)s
                            )
                            UNION(
                                SELECTtr.res_idasid,tr.valueasname
                                FROMir_translationtrJOIN
                                     product_pricelistprON(
                                        pr.id=tr.res_idAND
                                        tr.type='model'AND
                                        tr.name='product.pricelist,name'AND
                                        tr.lang=%(lang)s
                                     )JOIN
                                     res_currencycurON
                                         (pr.currency_id=cur.id)
                                WHEREtr.value||'('||cur.name||')'=%(name)s
                            )
                        )p
                       ORDERBYp.name"""
            iflimit:
                query+="LIMIT%(limit)s"
            self._cr.execute(query,query_args)
            ids=[r[0]forrinself._cr.fetchall()]
            #regularsearch()toapplyACLs-maylimitresultsbelowlimitinsomecases
            pricelist_ids=self._search([('id','in',ids)],limit=limit,access_rights_uid=name_get_uid)
            ifpricelist_ids:
                returnpricelist_ids
        returnsuper(Pricelist,self)._name_search(name,args,operator=operator,limit=limit,name_get_uid=name_get_uid)

    def_compute_price_rule_multi(self,products_qty_partner,date=False,uom_id=False):
        """Low-levelmethod-Multipricelist,multiproducts
        Returns:dict{product_id:dict{pricelist_id:(price,suitable_rule)}}"""
        ifnotself.ids:
            pricelists=self.search([])
        else:
            pricelists=self
        results={}
        forpricelistinpricelists:
            subres=pricelist._compute_price_rule(products_qty_partner,date=date,uom_id=uom_id)
            forproduct_id,priceinsubres.items():
                results.setdefault(product_id,{})
                results[product_id][pricelist.id]=price
        returnresults

    def_compute_price_rule_get_items(self,products_qty_partner,date,uom_id,prod_tmpl_ids,prod_ids,categ_ids):
        self.ensure_one()
        #Loadallrules
        self.env['product.pricelist.item'].flush(['price','currency_id','company_id','active'])
        self.env.cr.execute(
            """
            SELECT
                item.id
            FROM
                product_pricelist_itemASitem
            LEFTJOINproduct_categoryAScategONitem.categ_id=categ.id
            WHERE
                (item.product_tmpl_idISNULLORitem.product_tmpl_id=any(%s))
                AND(item.product_idISNULLORitem.product_id=any(%s))
                AND(item.categ_idISNULLORitem.categ_id=any(%s))
                AND(item.pricelist_id=%s)
                AND(item.date_startISNULLORitem.date_start<=%s)
                AND(item.date_endISNULLORitem.date_end>=%s)
                AND(item.active=TRUE)
            ORDERBY
                item.applied_on,item.min_quantitydesc,categ.complete_namedesc,item.iddesc
            """,
            (prod_tmpl_ids,prod_ids,categ_ids,self.id,date,date))
        #NOTE:ifyouchange`orderby`onthatquery,makesureitmatches
        #_orderfrommodeltoavoidinconstenciesandundeterministicissues.

        item_ids=[x[0]forxinself.env.cr.fetchall()]
        returnself.env['product.pricelist.item'].browse(item_ids)

    def_compute_price_rule(self,products_qty_partner,date=False,uom_id=False):
        """Low-levelmethod-Monopricelist,multiproducts
        Returns:dict{product_id:(price,suitable_rule)forthegivenpricelist}

        Dateincontextcanbeadate,datetime,...

            :paramproducts_qty_partner:listoftyplesproducts,quantity,partner
            :paramdatetimedate:validitydate
            :paramIDuom_id:intermediateunitofmeasure
        """
        self.ensure_one()
        ifnotdate:
            date=self._context.get('date')orfields.Datetime.now()
        ifnotuom_idandself._context.get('uom'):
            uom_id=self._context['uom']
        ifuom_id:
            #rebrowsewithuomifgiven
            products=[item[0].with_context(uom=uom_id)foriteminproducts_qty_partner]
            products_qty_partner=[(products[index],data_struct[1],data_struct[2])forindex,data_structinenumerate(products_qty_partner)]
        else:
            products=[item[0]foriteminproducts_qty_partner]

        ifnotproducts:
            return{}

        categ_ids={}
        forpinproducts:
            categ=p.categ_id
            whilecateg:
                categ_ids[categ.id]=True
                categ=categ.parent_id
        categ_ids=list(categ_ids)

        is_product_template=products[0]._name=="product.template"
        ifis_product_template:
            prod_tmpl_ids=[tmpl.idfortmplinproducts]
            #allvariantsofallproducts
            prod_ids=[p.idforpin
                        list(chain.from_iterable([t.product_variant_idsfortinproducts]))]
        else:
            prod_ids=[product.idforproductinproducts]
            prod_tmpl_ids=[product.product_tmpl_id.idforproductinproducts]

        items=self._compute_price_rule_get_items(products_qty_partner,date,uom_id,prod_tmpl_ids,prod_ids,categ_ids)

        results={}
        forproduct,qty,partnerinproducts_qty_partner:
            results[product.id]=0.0
            suitable_rule=False

            #Finalunitpriceiscomputedaccordingto`qty`inthe`qty_uom_id`UoM.
            #AnintermediaryunitpricemaybecomputedaccordingtoadifferentUoM,in
            #whichcasetheprice_uom_idcontainsthatUoM.
            #Thefinalpricewillbeconvertedtomatch`qty_uom_id`.
            qty_uom_id=self._context.get('uom')orproduct.uom_id.id
            qty_in_product_uom=qty
            ifqty_uom_id!=product.uom_id.id:
                try:
                    qty_in_product_uom=self.env['uom.uom'].browse([self._context['uom']])._compute_quantity(qty,product.uom_id)
                exceptUserError:
                    #Ignored-incompatibleUoMincontext,usedefaultproductUoM
                    pass

            #ifPublicusertrytoaccessstandardpricefromwebsitesale,needtocallprice_compute.
            #TDESURPRISE:productcanactuallybeatemplate
            price=product.price_compute('list_price')[product.id]

            price_uom=self.env['uom.uom'].browse([qty_uom_id])
            forruleinitems:
                ifrule.min_quantityandqty_in_product_uom<rule.min_quantity:
                    continue
                ifis_product_template:
                    ifrule.product_tmpl_idandproduct.id!=rule.product_tmpl_id.id:
                        continue
                    ifrule.product_idandnot(product.product_variant_count==1andproduct.product_variant_id.id==rule.product_id.id):
                        #productruleacceptableontemplateifhasonlyonevariant
                        continue
                else:
                    ifrule.product_tmpl_idandproduct.product_tmpl_id.id!=rule.product_tmpl_id.id:
                        continue
                    ifrule.product_idandproduct.id!=rule.product_id.id:
                        continue

                ifrule.categ_id:
                    cat=product.categ_id
                    whilecat:
                        ifcat.id==rule.categ_id.id:
                            break
                        cat=cat.parent_id
                    ifnotcat:
                        continue

                ifrule.base=='pricelist'andrule.base_pricelist_id:
                    price=rule.base_pricelist_id._compute_price_rule([(product,qty,partner)],date,uom_id)[product.id][0] #TDE:0=price,1=rule
                    src_currency=rule.base_pricelist_id.currency_id
                else:
                    #ifbaseoptionispublicpricetakesalepriceelsecostpriceofproduct
                    #price_computereturnsthepriceinthecontextUoM,i.e.qty_uom_id
                    price=product.price_compute(rule.base)[product.id]
                    ifrule.base=='standard_price':
                        src_currency=product.cost_currency_id
                    else:
                        src_currency=product.currency_id

                ifsrc_currency!=self.currency_id:
                    price=src_currency._convert(
                        price,self.currency_id,self.env.company,date,round=False)

                ifpriceisnotFalse:
                    price=rule._compute_price(price,price_uom,product,quantity=qty,partner=partner)
                    suitable_rule=rule
                break

            ifnotsuitable_rule:
                cur=product.currency_id
                price=cur._convert(price,self.currency_id,self.env.company,date,round=False)

            results[product.id]=(price,suitable_ruleandsuitable_rule.idorFalse)

        returnresults

    #Newmethods:productbased
    defget_products_price(self,products,quantities,partners,date=False,uom_id=False):
        """Foragivenpricelist,returnpriceforproducts
        Returns:dict{product_id:productprice},inthegivenpricelist"""
        self.ensure_one()
        return{
            product_id:res_tuple[0]
            forproduct_id,res_tupleinself._compute_price_rule(
                list(zip(products,quantities,partners)),
                date=date,
                uom_id=uom_id
            ).items()
        }

    defget_product_price(self,product,quantity,partner,date=False,uom_id=False):
        """Foragivenpricelist,returnpriceforagivenproduct"""
        self.ensure_one()
        returnself._compute_price_rule([(product,quantity,partner)],date=date,uom_id=uom_id)[product.id][0]

    defget_product_price_rule(self,product,quantity,partner,date=False,uom_id=False):
        """Foragivenpricelist,returnpriceandruleforagivenproduct"""
        self.ensure_one()
        returnself._compute_price_rule([(product,quantity,partner)],date=date,uom_id=uom_id)[product.id]

    defprice_get(self,prod_id,qty,partner=None):
        """Multipricelist,monoproduct-returnspriceperpricelist"""
        return{key:price[0]forkey,priceinself.price_rule_get(prod_id,qty,partner=partner).items()}

    defprice_rule_get_multi(self,products_by_qty_by_partner):
        """Multipricelist,multiproduct -returntuple"""
        returnself._compute_price_rule_multi(products_by_qty_by_partner)

    defprice_rule_get(self,prod_id,qty,partner=None):
        """Multipricelist,monoproduct-returntuple"""
        product=self.env['product.product'].browse([prod_id])
        returnself._compute_price_rule_multi([(product,qty,partner)])[prod_id]

    @api.model
    def_price_get_multi(self,pricelist,products_by_qty_by_partner):
        """Monopricelist,multiproduct-returnpriceperproduct"""
        returnpricelist.get_products_price(
            list(zip(**products_by_qty_by_partner)))

    def_get_partner_pricelist_multi_search_domain_hook(self,company_id):
        return[
            ('active','=',True),
            ('company_id','in',[company_id,False]),
        ]

    def_get_partner_pricelist_multi_filter_hook(self):
        returnself.filtered('active')

    def_get_partner_pricelist_multi(self,partner_ids,company_id=None):
        """Retrievetheapplicablepricelistforgivenpartnersinagivencompany.

            Itwillreturnthefirstfoundpricelistinthisorder:
            First,thepricelistofthespecificproperty(res_idset),thisone
                   iscreatedwhensavingapricelistonthepartnerformview.
            Else,itwillreturnthepricelistofthepartnercountrygroup
            Else,itwillreturnthegenericproperty(res_idnotset),thisone
                  iscreatedonthecompanycreation.
            Else,itwillreturnthefirstavailablepricelist

            :paramcompany_id:ifpassed,usedforlookingupproperties,
                insteadofcurrentuser'scompany
            :return:adict{partner_id:pricelist}
        """
        #`partner_ids`mightbeIDfrominactiveuers.Weshoulduseactive_test
        #aswewilldoasearch()later(realcaseforwebsitepublicuser).
        Partner=self.env['res.partner'].with_context(active_test=False)
        company_id=company_idorself.env.company.id

        Property=self.env['ir.property'].with_company(company_id)
        Pricelist=self.env['product.pricelist']
        pl_domain=self._get_partner_pricelist_multi_search_domain_hook(company_id)

        #ifnospecificproperty,trytofindafittingpricelist
        result=Property._get_multi('property_product_pricelist',Partner._name,partner_ids)

        remaining_partner_ids=[pidforpid,valinresult.items()ifnotvalor
                                 notval._get_partner_pricelist_multi_filter_hook()]
        ifremaining_partner_ids:
            #getfallbackpricelistwhennopricelistforagivencountry
            pl_fallback=(
                Pricelist.search(pl_domain+[('country_group_ids','=',False)],limit=1)or
                Property._get('property_product_pricelist','res.partner')or
                Pricelist.search(pl_domain,limit=1)
            )
            #grouppartnersbycountry,andfindapricelistforeachcountry
            domain=[('id','in',remaining_partner_ids)]
            groups=Partner.read_group(domain,['country_id'],['country_id'])
            forgroupingroups:
                country_id=group['country_id']andgroup['country_id'][0]
                pl=Pricelist.search(pl_domain+[('country_group_ids.country_ids','=',country_id)],limit=1)
                pl=plorpl_fallback
                forpidinPartner.search(group['__domain']).ids:
                    result[pid]=pl

        returnresult

    @api.model
    defget_import_templates(self):
        return[{
            'label':_('ImportTemplateforPricelists'),
            'template':'/product/static/xls/product_pricelist.xls'
        }]
    
    defunlink(self):
        forpricelistinself:
            linked_items=self.env['product.pricelist.item'].sudo().with_context(active_test=False).search(
                [('base','=','pricelist'),('base_pricelist_id','=',pricelist.id),('pricelist_id','notin',self.ids)])
            iflinked_items:
                raiseUserError(_('Youcannotdeletethispricelist(%s),itisusedinotherpricelist(s):\n%s',
                    pricelist.display_name,'\n'.join(linked_items.pricelist_id.mapped('display_name'))))
        returnsuper().unlink()


classResCountryGroup(models.Model):
    _inherit='res.country.group'

    pricelist_ids=fields.Many2many('product.pricelist','res_country_group_pricelist_rel',
                                     'res_country_group_id','pricelist_id',string='Pricelists')


classPricelistItem(models.Model):
    _name="product.pricelist.item"
    _description="PricelistRule"
    _order="applied_on,min_quantitydesc,categ_iddesc,iddesc"
    _check_company_auto=True
    #NOTE:ifyouchange_orderonthismodel,makesureitmatchestheSQL
    #querybuiltin_compute_price_rule()aboveinthisfiletoavoid
    #inconstenciesandundeterministicissues.

    def_default_pricelist_id(self):
        returnself.env['product.pricelist'].search([
            '|',('company_id','=',False),
            ('company_id','=',self.env.company.id)],limit=1)

    product_tmpl_id=fields.Many2one(
        'product.template','Product',ondelete='cascade',check_company=True,
        help="Specifyatemplateifthisruleonlyappliestooneproducttemplate.Keepemptyotherwise.")
    product_id=fields.Many2one(
        'product.product','ProductVariant',ondelete='cascade',check_company=True,
        help="Specifyaproductifthisruleonlyappliestooneproduct.Keepemptyotherwise.")
    categ_id=fields.Many2one(
        'product.category','ProductCategory',ondelete='cascade',
        help="Specifyaproductcategoryifthisruleonlyappliestoproductsbelongingtothiscategoryoritschildrencategories.Keepemptyotherwise.")
    min_quantity=fields.Float(
        'Min.Quantity',default=0,digits="ProductUnitOfMeasure",
        help="Fortheruletoapply,bought/soldquantitymustbegreater"
             "thanorequaltotheminimumquantityspecifiedinthisfield.\n"
             "Expressedinthedefaultunitofmeasureoftheproduct.")
    applied_on=fields.Selection([
        ('3_global','AllProducts'),
        ('2_product_category','ProductCategory'),
        ('1_product','Product'),
        ('0_product_variant','ProductVariant')],"ApplyOn",
        default='3_global',required=True,
        help='PricelistItemapplicableonselectedoption')
    base=fields.Selection([
        ('list_price','SalesPrice'),
        ('standard_price','Cost'),
        ('pricelist','OtherPricelist')],"Basedon",
        default='list_price',required=True,
        help='Basepriceforcomputation.\n'
             'SalesPrice:ThebasepricewillbetheSalesPrice.\n'
             'CostPrice:Thebasepricewillbethecostprice.\n'
             'OtherPricelist:ComputationofthebasepricebasedonanotherPricelist.')
    base_pricelist_id=fields.Many2one('product.pricelist','OtherPricelist',check_company=True)
    pricelist_id=fields.Many2one('product.pricelist','Pricelist',index=True,ondelete='cascade',required=True,default=_default_pricelist_id)
    price_surcharge=fields.Float(
        'PriceSurcharge',digits='ProductPrice',
        help='Specifythefixedamounttoaddorsubtract(ifnegative)totheamountcalculatedwiththediscount.')
    price_discount=fields.Float('PriceDiscount',default=0,digits=(16,2))
    price_round=fields.Float(
        'PriceRounding',digits='ProductPrice',
        help="Setsthepricesothatitisamultipleofthisvalue.\n"
             "Roundingisappliedafterthediscountandbeforethesurcharge.\n"
             "Tohavepricesthatendin9.99,setrounding10,surcharge-0.01")
    price_min_margin=fields.Float(
        'Min.PriceMargin',digits='ProductPrice',
        help='Specifytheminimumamountofmarginoverthebaseprice.')
    price_max_margin=fields.Float(
        'Max.PriceMargin',digits='ProductPrice',
        help='Specifythemaximumamountofmarginoverthebaseprice.')
    company_id=fields.Many2one(
        'res.company','Company',
        readonly=True,related='pricelist_id.company_id',store=True)
    currency_id=fields.Many2one(
        'res.currency','Currency',
        readonly=True,related='pricelist_id.currency_id',store=True)
    active=fields.Boolean(
        readonly=True,related="pricelist_id.active",store=True)
    date_start=fields.Datetime('StartDate',help="Startingdatetimeforthepricelistitemvalidation\n"
                                                "Thedisplayedvaluedependsonthetimezonesetinyourpreferences.")
    date_end=fields.Datetime('EndDate',help="Endingdatetimeforthepricelistitemvalidation\n"
                                                "Thedisplayedvaluedependsonthetimezonesetinyourpreferences.")
    compute_price=fields.Selection([
        ('fixed','FixedPrice'),
        ('percentage','Percentage(discount)'),
        ('formula','Formula')],index=True,default='fixed',required=True)
    fixed_price=fields.Float('FixedPrice',digits='ProductPrice')
    percent_price=fields.Float('PercentagePrice')
    #functionalfieldsusedforusabilitypurposes
    name=fields.Char(
        'Name',compute='_get_pricelist_item_name_price',
        help="Explicitrulenameforthispricelistline.")
    price=fields.Char(
        'Price',compute='_get_pricelist_item_name_price',
        help="Explicitrulenameforthispricelistline.")

    @api.constrains('base_pricelist_id','pricelist_id','base')
    def_check_recursion(self):
        ifany(item.base=='pricelist'anditem.pricelist_idanditem.pricelist_id==item.base_pricelist_idforiteminself):
            raiseValidationError(_('YoucannotassigntheMainPricelistasOtherPricelistinPriceListItem'))
        returnTrue

    @api.constrains('price_min_margin','price_max_margin')
    def_check_margin(self):
        ifany(item.price_min_margin>item.price_max_marginforiteminself):
            raiseValidationError(_('Theminimummarginshouldbelowerthanthemaximummargin.'))
        returnTrue

    @api.constrains('product_id','product_tmpl_id','categ_id')
    def_check_product_consistency(self):
        foriteminself:
            ifitem.applied_on=="2_product_category"andnotitem.categ_id:
                raiseValidationError(_("Pleasespecifythecategoryforwhichthisruleshouldbeapplied"))
            elifitem.applied_on=="1_product"andnotitem.product_tmpl_id:
                raiseValidationError(_("Pleasespecifytheproductforwhichthisruleshouldbeapplied"))
            elifitem.applied_on=="0_product_variant"andnotitem.product_id:
                raiseValidationError(_("Pleasespecifytheproductvariantforwhichthisruleshouldbeapplied"))

    @api.depends('applied_on','categ_id','product_tmpl_id','product_id','compute_price','fixed_price',\
        'pricelist_id','percent_price','price_discount','price_surcharge')
    def_get_pricelist_item_name_price(self):
        foriteminself:
            ifitem.categ_idanditem.applied_on=='2_product_category':
                item.name=_("Category:%s")%(item.categ_id.display_name)
            elifitem.product_tmpl_idanditem.applied_on=='1_product':
                item.name=_("Product:%s")%(item.product_tmpl_id.display_name)
            elifitem.product_idanditem.applied_on=='0_product_variant':
                item.name=_("Variant:%s")%(item.product_id.with_context(display_default_code=False).display_name)
            else:
                item.name=_("AllProducts")

            ifitem.compute_price=='fixed':
                item.price=formatLang(item.env,item.fixed_price,monetary=True,dp="ProductPrice",currency_obj=item.currency_id)
            elifitem.compute_price=='percentage':
                item.price=_("%s%%discount",item.percent_price)
            else:
                item.price=_("%(percentage)s%%discountand%(price)ssurcharge",percentage=item.price_discount,price=item.price_surcharge)

    @api.onchange('compute_price')
    def_onchange_compute_price(self):
        ifself.compute_price!='fixed':
            self.fixed_price=0.0
        ifself.compute_price!='percentage':
            self.percent_price=0.0
        ifself.compute_price!='formula':
            self.update({
                'base':'list_price',
                'price_discount':0.0,
                'price_surcharge':0.0,
                'price_round':0.0,
                'price_min_margin':0.0,
                'price_max_margin':0.0,
            })

    @api.onchange('product_id')
    def_onchange_product_id(self):
        has_product_id=self.filtered('product_id')
        foriteminhas_product_id:
            item.product_tmpl_id=item.product_id.product_tmpl_id
        ifself.env.context.get('default_applied_on',False)=='1_product':
            #Ifaproductvariantisspecified,applyonvariantsinstead
            #Resetifproductvariantisremoved
            has_product_id.update({'applied_on':'0_product_variant'})
            (self-has_product_id).update({'applied_on':'1_product'})

    @api.onchange('product_tmpl_id')
    def_onchange_product_tmpl_id(self):
        has_tmpl_id=self.filtered('product_tmpl_id')
        foriteminhas_tmpl_id:
            ifitem.product_idanditem.product_id.product_tmpl_id!=item.product_tmpl_id:
                item.product_id=None

    @api.onchange('product_id','product_tmpl_id','categ_id')
    def_onchane_rule_content(self):
        ifnotself.user_has_groups('product.group_sale_pricelist')andnotself.env.context.get('default_applied_on',False):
            #Ifadvancedpricelistsaredisabled(applied_onfieldisnotvisible)
            #ANDwearen'tcomingfromaspecificproducttemplate/variant.
            variants_rules=self.filtered('product_id')
            template_rules=(self-variants_rules).filtered('product_tmpl_id')
            variants_rules.update({'applied_on':'0_product_variant'})
            template_rules.update({'applied_on':'1_product'})
            (self-variants_rules-template_rules).update({'applied_on':'3_global'})

    @api.model_create_multi
    defcreate(self,vals_list):
        forvaluesinvals_list:
            ifvalues.get('applied_on',False):
                #Ensureitemconsistencyforlatersearches.
                applied_on=values['applied_on']
                ifapplied_on=='3_global':
                    values.update(dict(product_id=None,product_tmpl_id=None,categ_id=None))
                elifapplied_on=='2_product_category':
                    values.update(dict(product_id=None,product_tmpl_id=None))
                elifapplied_on=='1_product':
                    values.update(dict(product_id=None,categ_id=None))
                elifapplied_on=='0_product_variant':
                    values.update(dict(categ_id=None))
        returnsuper(PricelistItem,self).create(vals_list)

    defwrite(self,values):
        ifvalues.get('applied_on',False):
            #Ensureitemconsistencyforlatersearches.
            applied_on=values['applied_on']
            ifapplied_on=='3_global':
                values.update(dict(product_id=None,product_tmpl_id=None,categ_id=None))
            elifapplied_on=='2_product_category':
                values.update(dict(product_id=None,product_tmpl_id=None))
            elifapplied_on=='1_product':
                values.update(dict(product_id=None,categ_id=None))
            elifapplied_on=='0_product_variant':
                values.update(dict(categ_id=None))
        res=super(PricelistItem,self).write(values)
        #Whenthepricelistchangesweneedtheproduct.templateprice
        #tobeinvalidedandrecomputed.
        self.env['product.template'].invalidate_cache(['price'])
        self.env['product.product'].invalidate_cache(['price'])
        returnres

    deftoggle_active(self):
        raiseValidationError(_("Youcannotdisableapricelistrule,pleasedeleteitorarchiveitspricelistinstead."))

    def_compute_price(self,price,price_uom,product,quantity=1.0,partner=False):
        """Computetheunitpriceofaproductinthecontextofapricelistapplication.
           Theunusedparametersaretheretomakethefullcontextavailableforoverrides.
        """
        self.ensure_one()
        convert_to_price_uom=(lambdaprice:product.uom_id._compute_price(price,price_uom))
        ifself.compute_price=='fixed':
            price=convert_to_price_uom(self.fixed_price)
        elifself.compute_price=='percentage':
            price=(price-(price*(self.percent_price/100)))or0.0
        else:
            #completeformula
            price_limit=price
            price=(price-(price*(self.price_discount/100)))or0.0

            ifself.price_round:
                price=tools.float_round(price,precision_rounding=self.price_round)

            ifself.price_surcharge:
                price+=convert_to_price_uom(self.price_surcharge)

            ifself.price_min_margin:
                price_min_margin=convert_to_price_uom(self.price_min_margin)
                price=max(price,price_limit+price_min_margin)

            ifself.price_max_margin:
                price_max_margin=convert_to_price_uom(self.price_max_margin)
                price=min(price,price_limit+price_max_margin)

        returnprice
