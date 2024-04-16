#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importjson
importlogging
fromdatetimeimportdatetime
fromwerkzeug.exceptionsimportForbidden,NotFound

fromflectraimportfields,http,SUPERUSER_ID,tools,_
fromflectra.httpimportrequest
fromflectra.addons.base.models.ir_qweb_fieldsimportnl2br
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.addons.payment.controllers.portalimportPaymentProcessing
fromflectra.addons.website.controllers.mainimportQueryURL
fromflectra.addons.website.models.ir_httpimportsitemap_qs2dom
fromflectra.exceptionsimportValidationError
fromflectra.addons.portal.controllers.portalimport_build_url_w_params
fromflectra.addons.website.controllers.mainimportWebsite
fromflectra.addons.website_form.controllers.mainimportWebsiteForm
fromflectra.osvimportexpression
_logger=logging.getLogger(__name__)


classTableCompute(object):

    def__init__(self):
        self.table={}

    def_check_place(self,posx,posy,sizex,sizey,ppr):
        res=True
        foryinrange(sizey):
            forxinrange(sizex):
                ifposx+x>=ppr:
                    res=False
                    break
                row=self.table.setdefault(posy+y,{})
                ifrow.setdefault(posx+x)isnotNone:
                    res=False
                    break
            forxinrange(ppr):
                self.table[posy+y].setdefault(x,None)
        returnres

    defprocess(self,products,ppg=20,ppr=4):
        #Computeproductspositionsonthegrid
        minpos=0
        index=0
        maxy=0
        x=0
        forpinproducts:
            x=min(max(p.website_size_x,1),ppr)
            y=min(max(p.website_size_y,1),ppr)
            ifindex>=ppg:
                x=y=1

            pos=minpos
            whilenotself._check_place(pos%ppr,pos//ppr,x,y,ppr):
                pos+=1
            #if21stproducts(index20)andthelastlineisfull(pprproductsinit),break
            #(pos+1.0)/ppristhelinewheretheproductwouldbeinserted
            #maxyisthenumberofexistinglines
            #+1.0isbecauseposbeginsat0,thuspos20isactuallythe21stblock
            #andtoforcepythontonotroundthedivisionoperation
            ifindex>=ppgand((pos+1.0)//ppr)>maxy:
                break

            ifx==1andy==1:  #simpleheuristicforCPUoptimization
                minpos=pos//ppr

            fory2inrange(y):
                forx2inrange(x):
                    self.table[(pos//ppr)+y2][(pos%ppr)+x2]=False
            self.table[pos//ppr][pos%ppr]={
                'product':p,'x':x,'y':y,
                'ribbon':p.website_ribbon_id,
            }
            ifindex<=ppg:
                maxy=max(maxy,y+(pos//ppr))
            index+=1

        #FormattableaccordingtoHTMLneeds
        rows=sorted(self.table.items())
        rows=[r[1]forrinrows]
        forcolinrange(len(rows)):
            cols=sorted(rows[col].items())
            x+=len(cols)
            rows[col]=[r[1]forrincolsifr[1]]

        returnrows


classWebsiteSaleForm(WebsiteForm):

    @http.route('/website_form/shop.sale.order',type='http',auth="public",methods=['POST'],website=True)
    defwebsite_form_saleorder(self,**kwargs):
        model_record=request.env.ref('sale.model_sale_order')
        try:
            data=self.extract_data(model_record,kwargs)
        exceptValidationErrorase:
            returnjson.dumps({'error_fields':e.args[0]})

        order=request.website.sale_get_order()
        ifdata['record']:
            order.write(data['record'])

        ifdata['custom']:
            values={
                'body':nl2br(data['custom']),
                'model':'sale.order',
                'message_type':'comment',
                'no_auto_thread':False,
                'res_id':order.id,
            }
            request.env['mail.message'].with_user(SUPERUSER_ID).create(values)

        ifdata['attachments']:
            self.insert_attachment(model_record,order.id,data['attachments'])

        returnjson.dumps({'id':order.id})


classWebsite(Website):
    @http.route()
    defget_switchable_related_views(self,key):
        views=super(Website,self).get_switchable_related_views(key)
        ifkey=='website_sale.product':
            ifnotrequest.env.user.has_group('product.group_product_variant'):
                view_product_variants=request.website.viewref('website_sale.product_variants')
                views=[vforvinviewsifv['id']!=view_product_variants.id]
        returnviews

    @http.route()
    deftoggle_switchable_view(self,view_key):
        super(Website,self).toggle_switchable_view(view_key)
        ifview_keyin('website_sale.products_list_view','website_sale.add_grid_or_list_option'):
            request.session.pop('website_sale_shop_layout_mode',None)


classWebsiteSale(http.Controller):

    def_get_pricelist_context(self):
        pricelist_context=dict(request.env.context)
        pricelist=False
        ifnotpricelist_context.get('pricelist'):
            pricelist=request.website.get_current_pricelist()
            pricelist_context['pricelist']=pricelist.id
        else:
            pricelist=request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        returnpricelist_context,pricelist

    def_get_search_order(self,post):
        #OrderBywillbeparsedinormandsonodirectsqlinjection
        #idisaddedtobesurethatorderisauniquesortkey
        order=post.get('order')or'website_sequenceASC'
        return'is_publisheddesc,%s,iddesc'%order

    def_get_search_domain(self,search,category,attrib_values,search_in_description=True):
        domains=[request.website.sale_product_domain()]
        ifsearch:
            forsrchinsearch.split(""):
                subdomains=[
                    [('name','ilike',srch)],
                    [('product_variant_ids.default_code','ilike',srch)]
                ]
                ifsearch_in_description:
                    subdomains.append([('description','ilike',srch)])
                    subdomains.append([('description_sale','ilike',srch)])
                domains.append(expression.OR(subdomains))

        ifcategory:
            domains.append([('public_categ_ids','child_of',int(category))])

        ifattrib_values:
            attrib=None
            ids=[]
            forvalueinattrib_values:
                ifnotattrib:
                    attrib=value[0]
                    ids.append(value[1])
                elifvalue[0]==attrib:
                    ids.append(value[1])
                else:
                    domains.append([('attribute_line_ids.value_ids','in',ids)])
                    attrib=value[0]
                    ids=[value[1]]
            ifattrib:
                domains.append([('attribute_line_ids.value_ids','in',ids)])

        returnexpression.AND(domains)

    defsitemap_shop(env,rule,qs):
        ifnotqsorqs.lower()in'/shop':
            yield{'loc':'/shop'}

        Category=env['product.public.category']
        dom=sitemap_qs2dom(qs,'/shop/category',Category._rec_name)
        dom+=env['website'].get_current_website().website_domain()
        forcatinCategory.search(dom):
            loc='/shop/category/%s'%slug(cat)
            ifnotqsorqs.lower()inloc:
                yield{'loc':loc}

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ],type='http',auth="public",website=True,sitemap=sitemap_shop)
    defshop(self,page=0,category=None,search='',ppg=False,**post):
        add_qty=int(post.get('add_qty',1))
        Category=request.env['product.public.category']
        ifcategory:
            category=Category.search([('id','=',int(category))],limit=1)
            ifnotcategoryornotcategory.can_access_from_current_website():
                raiseNotFound()
        else:
            category=Category

        ifppg:
            try:
                ppg=int(ppg)
                post['ppg']=ppg
            exceptValueError:
                ppg=False
        ifnotppg:
            ppg=request.env['website'].get_current_website().shop_ppgor20

        ppr=request.env['website'].get_current_website().shop_ppror4

        attrib_list=request.httprequest.args.getlist('attrib')
        attrib_values=[[int(x)forxinv.split("-")]forvinattrib_listifv]
        attributes_ids={v[0]forvinattrib_values}
        attrib_set={v[1]forvinattrib_values}

        domain=self._get_search_domain(search,category,attrib_values)

        keep=QueryURL('/shop',category=categoryandint(category),search=search,attrib=attrib_list,order=post.get('order'))

        pricelist_context,pricelist=self._get_pricelist_context()

        request.context=dict(request.context,pricelist=pricelist.id,partner=request.env.user.partner_id)

        url="/shop"
        ifsearch:
            post["search"]=search
        ifattrib_list:
            post['attrib']=attrib_list

        Product=request.env['product.template'].with_context(bin_size=True)

        search_product=Product.search(domain,order=self._get_search_order(post))
        website_domain=request.website.website_domain()
        categs_domain=[('parent_id','=',False)]+website_domain
        ifsearch:
            search_categories=Category.search([('product_tmpl_ids','in',search_product.ids)]+website_domain).parents_and_self
            categs_domain.append(('id','in',search_categories.ids))
        else:
            search_categories=Category
        categs=Category.search(categs_domain)

        ifcategory:
            url="/shop/category/%s"%slug(category)

        product_count=len(search_product)
        pager=request.website.pager(url=url,total=product_count,page=page,step=ppg,scope=5,url_args=post)
        offset=pager['offset']
        products=search_product[offset:offset+ppg]

        ProductAttribute=request.env['product.attribute']
        ifproducts:
            #getallproductswithoutlimit
            attributes=ProductAttribute.search([('product_tmpl_ids','in',search_product.ids)])
        else:
            attributes=ProductAttribute.browse(attributes_ids)

        layout_mode=request.session.get('website_sale_shop_layout_mode')
        ifnotlayout_mode:
            ifrequest.website.viewref('website_sale.products_list_view').active:
                layout_mode='list'
            else:
                layout_mode='grid'

        values={
            'search':search,
            'order':post.get('order',''),
            'category':category,
            'attrib_values':attrib_values,
            'attrib_set':attrib_set,
            'pager':pager,
            'pricelist':pricelist,
            'add_qty':add_qty,
            'products':products,
            'search_count':product_count, #commonforallsearchbox
            'bins':TableCompute().process(products,ppg,ppr),
            'ppg':ppg,
            'ppr':ppr,
            'categories':categs,
            'attributes':attributes,
            'keep':keep,
            'search_categories_ids':search_categories.ids,
            'layout_mode':layout_mode,
        }
        ifcategory:
            values['main_object']=category
        returnrequest.render("website_sale.products",values)

    @http.route(['/shop/<model("product.template"):product>'],type='http',auth="public",website=True,sitemap=True)
    defproduct(self,product,category='',search='',**kwargs):
        ifnotproduct.can_access_from_current_website():
            raiseNotFound()

        returnrequest.render("website_sale.product",self._prepare_product_values(product,category,search,**kwargs))

    @http.route(['/shop/product/<model("product.template"):product>'],type='http',auth="public",website=True,sitemap=False)
    defold_product(self,product,category='',search='',**kwargs):
        #Compatibilitypre-v14
        returnrequest.redirect(_build_url_w_params("/shop/%s"%slug(product),request.params),code=301)

    def_prepare_product_values(self,product,category,search,**kwargs):
        add_qty=int(kwargs.get('add_qty',1))

        product_context=dict(request.env.context,quantity=add_qty,
                               active_id=product.id,
                               partner=request.env.user.partner_id)
        ProductCategory=request.env['product.public.category']

        ifcategory:
            category=ProductCategory.browse(int(category)).exists()

        attrib_list=request.httprequest.args.getlist('attrib')
        attrib_values=[[int(x)forxinv.split("-")]forvinattrib_listifv]
        attrib_set={v[1]forvinattrib_values}

        keep=QueryURL('/shop',category=categoryandcategory.id,search=search,attrib=attrib_list)

        categs=ProductCategory.search([('parent_id','=',False)])

        pricelist=request.website.get_current_pricelist()

        ifnotproduct_context.get('pricelist'):
            product_context['pricelist']=pricelist.id
            product=product.with_context(product_context)

        #Neededtotriggertherecentlyviewedproductrpc
        view_track=request.website.viewref("website_sale.product").track

        return{
            'search':search,
            'category':category,
            'pricelist':pricelist,
            'attrib_values':attrib_values,
            'attrib_set':attrib_set,
            'keep':keep,
            'categories':categs,
            'main_object':product,
            'product':product,
            'add_qty':add_qty,
            'view_track':view_track,
        }

    @http.route(['/shop/change_pricelist/<model("product.pricelist"):pl_id>'],type='http',auth="public",website=True,sitemap=False)
    defpricelist_change(self,pl_id,**post):
        if(pl_id.selectableorpl_id==request.env.user.partner_id.property_product_pricelist)\
                andrequest.website.is_pricelist_available(pl_id.id):
            request.session['website_sale_current_pl']=pl_id.id
            request.website.sale_get_order(force_pricelist=pl_id.id)
        returnrequest.redirect(request.httprequest.referreror'/shop')

    @http.route(['/shop/pricelist'],type='http',auth="public",website=True,sitemap=False)
    defpricelist(self,promo,**post):
        redirect=post.get('r','/shop/cart')
        #emptypromocodeisusedtoreset/removepricelist(see`sale_get_order()`)
        ifpromo:
            pricelist=request.env['product.pricelist'].sudo().search([('code','=',promo)],limit=1)
            if(notpricelistor(pricelistandnotrequest.website.is_pricelist_available(pricelist.id))):
                returnrequest.redirect("%s?code_not_available=1"%redirect)

        request.website.sale_get_order(code=promo)
        returnrequest.redirect(redirect)

    @http.route(['/shop/cart'],type='http',auth="public",website=True,sitemap=False)
    defcart(self,access_token=None,revive='',**post):
        """
        Maincartmanagement+abandonedcartrevival
        access_token:AbandonedcartSOaccesstoken
        revive:Revivalmethodwhenabandonedcart.Canbe'merge'or'squash'
        """
        order=request.website.sale_get_order()
        iforderandorder.state!='draft':
            request.session['sale_order_id']=None
            order=request.website.sale_get_order()
        values={}
        ifaccess_token:
            abandoned_order=request.env['sale.order'].sudo().search([('access_token','=',access_token)],limit=1)
            ifnotabandoned_order: #wrongtoken(orSOhasbeendeleted)
                raiseNotFound()
            ifabandoned_order.state!='draft': #abandonedcartalreadyfinished
                values.update({'abandoned_proceed':True})
            elifrevive=='squash'or(revive=='merge'andnotrequest.session.get('sale_order_id')): #restoreoldcartormergewithunexistant
                request.session['sale_order_id']=abandoned_order.id
                returnrequest.redirect('/shop/cart')
            elifrevive=='merge':
                abandoned_order.order_line.write({'order_id':request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elifabandoned_order.id!=request.session.get('sale_order_id'): #abandonedcartfound,userhavetochoosewhattodo
                values.update({'access_token':abandoned_order.access_token})

        values.update({
            'website_sale_order':order,
            'date':fields.Date.today(),
            'suggested_products':[],
        })
        iforder:
            order.order_line.filtered(lambdal:notl.product_id.active).unlink()
            _order=order
            ifnotrequest.env.context.get('pricelist'):
                _order=order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products']=_order._cart_accessories()

        ifpost.get('type')=='popover':
            #forceno-cachesoIE11doesn'tcachethisXHR
            returnrequest.render("website_sale.cart_popover",values,headers={'Cache-Control':'no-cache'})

        returnrequest.render("website_sale.cart",values)

    @http.route(['/shop/cart/update'],type='http',auth="public",methods=['POST'],website=True)
    defcart_update(self,product_id,add_qty=1,set_qty=0,**kw):
        """Thisrouteiscalledwhenaddingaproducttocart(nooptions)."""
        sale_order=request.website.sale_get_order(force_create=True)
        ifsale_order.state!='draft':
            request.session['sale_order_id']=None
            sale_order=request.website.sale_get_order(force_create=True)

        product_custom_attribute_values=None
        ifkw.get('product_custom_attribute_values'):
            product_custom_attribute_values=json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values=None
        ifkw.get('no_variant_attribute_values'):
            no_variant_attribute_values=json.loads(kw.get('no_variant_attribute_values'))

        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )

        ifkw.get('express'):
            returnrequest.redirect("/shop/checkout?express=1")

        returnrequest.redirect("/shop/cart")

    @http.route(['/shop/cart/update_json'],type='json',auth="public",methods=['POST'],website=True,csrf=False)
    defcart_update_json(self,product_id,line_id=None,add_qty=None,set_qty=None,display=True):
        """Thisrouteiscalledwhenchangingquantityfromthecartoradding
        aproductfromthewishlist."""
        order=request.website.sale_get_order(force_create=1)
        iforder.state!='draft':
            request.website.sale_reset()
            return{}

        value=order._cart_update(product_id=product_id,line_id=line_id,add_qty=add_qty,set_qty=set_qty)

        ifnotorder.cart_quantity:
            request.website.sale_reset()
            returnvalue

        order=request.website.sale_get_order()
        value['cart_quantity']=order.cart_quantity

        ifnotdisplay:
            returnvalue

        value['website_sale.cart_lines']=request.env['ir.ui.view']._render_template("website_sale.cart_lines",{
            'website_sale_order':order,
            'date':fields.Date.today(),
            'suggested_products':order._cart_accessories()
        })
        value['website_sale.short_cart_summary']=request.env['ir.ui.view']._render_template("website_sale.short_cart_summary",{
            'website_sale_order':order,
        })
        returnvalue

    @http.route('/shop/save_shop_layout_mode',type='json',auth='public',website=True)
    defsave_shop_layout_mode(self,layout_mode):
        assertlayout_modein('grid','list'),"Invalidshoplayoutmode"
        request.session['website_sale_shop_layout_mode']=layout_mode

    #------------------------------------------------------
    #Checkout
    #------------------------------------------------------

    defcheckout_check_address(self,order):
        billing_fields_required=self._get_mandatory_fields_billing(order.partner_id.country_id.id)
        ifnotall(order.partner_id.read(billing_fields_required)[0].values()):
            returnrequest.redirect('/shop/address?partner_id=%d'%order.partner_id.id)

        shipping_fields_required=self._get_mandatory_fields_shipping(order.partner_shipping_id.country_id.id)
        ifnotall(order.partner_shipping_id.read(shipping_fields_required)[0].values()):
            returnrequest.redirect('/shop/address?partner_id=%d'%order.partner_shipping_id.id)

    defcheckout_redirection(self,order):
        #musthaveadraftsalesorderwithlinesatthispoint,otherwisereset
        ifnotorderororder.state!='draft':
            request.session['sale_order_id']=None
            request.session['sale_transaction_id']=None
            returnrequest.redirect('/shop')

        iforderandnotorder.order_line:
            returnrequest.redirect('/shop/cart')

        #iftransactionpending/done:redirecttoconfirmation
        tx=request.env.context.get('website_sale_transaction')
        iftxandtx.state!='draft':
            returnrequest.redirect('/shop/payment/confirmation/%s'%order.id)

    defcheckout_values(self,**kw):
        order=request.website.sale_get_order(force_create=1)
        shippings=[]
        iforder.partner_id!=request.website.user_id.sudo().partner_id:
            Partner=order.partner_id.with_context(show_address=1).sudo()
            shippings=Partner.search([
                ("id","child_of",order.partner_id.commercial_partner_id.ids),
                '|',("type","in",["delivery","other"]),("id","=",order.partner_id.commercial_partner_id.id)
            ],order='iddesc')
            ifshippings:
                ifkw.get('partner_id')or'use_billing'inkw:
                    if'use_billing'inkw:
                        partner_id=order.partner_id.id
                    else:
                        partner_id=int(kw.get('partner_id'))
                    ifpartner_idinshippings.mapped('id'):
                        order.partner_shipping_id=partner_id

        values={
            'order':order,
            'shippings':shippings,
            'only_services':orderandorder.only_servicesorFalse
        }
        returnvalues

    def_get_mandatory_billing_fields(self):
        #deprecatedfor_get_mandatory_fields_billingwhichhandlezip/staterequired
        return["name","email","street","city","country_id"]

    def_get_mandatory_shipping_fields(self):
        #deprecatedfor_get_mandatory_fields_shippingwhichhandlezip/staterequired
        return["name","street","city","country_id"]

    def_get_mandatory_fields_billing(self,country_id=False):
        req=self._get_mandatory_billing_fields()
        ifcountry_id:
            country=request.env['res.country'].browse(country_id)
            ifcountry.state_required:
                req+=['state_id']
            ifcountry.zip_required:
                req+=['zip']
        returnreq

    def_get_mandatory_fields_shipping(self,country_id=False):
        req=self._get_mandatory_shipping_fields()
        ifcountry_id:
            country=request.env['res.country'].browse(country_id)
            ifcountry.state_required:
                req+=['state_id']
            ifcountry.zip_required:
                req+=['zip']
        returnreq

    defcheckout_form_validate(self,mode,all_form_values,data):
        #mode:tuple('new|edit','billing|shipping')
        #all_form_values:allvaluesbeforepreprocess
        #data:valuesafterpreprocess
        error=dict()
        error_message=[]

        ifdata.get('partner_id'):
            partner_su=request.env['res.partner'].sudo().browse(int(data['partner_id'])).exists()
            name_change=partner_suand'name'indataanddata['name']!=partner_su.name
            email_change=partner_suand'email'indataanddata['email']!=partner_su.email

            #Preventchangingthebillingpartnernameifinvoiceshavebeenissued.
            ifmode[1]=='billing'andname_changeandnotpartner_su.can_edit_vat():
                error['name']='error'
                error_message.append(_(
                    "Changingyournameisnotallowedoncedocumentshavebeenissuedforyour"
                    "account.Pleasecontactusdirectlyforthisoperation."
                ))

            #Preventchangethepartnernameoremailifitisaninternaluser.
            if(name_changeoremail_change)andnotall(partner_su.user_ids.mapped('share')):
                error.update({
                    'name':'error'ifname_changeelseNone,
                    'email':'error'ifemail_changeelseNone,
                })
                error_message.append(_(
                    "Ifyouareorderingforanexternalperson,pleaseplaceyourorderviathe"
                    "backend.Ifyouwishtochangeyournameoremailaddress,pleasedosoin"
                    "theaccountsettingsorcontactyouradministrator."
                ))

        #Requiredfieldsfromform
        required_fields=[fforfin(all_form_values.get('field_required')or'').split(',')iff]

        #Requiredfieldsfrommandatoryfieldfunction
        country_id=int(data.get('country_id',False))
        required_fields+=mode[1]=='shipping'andself._get_mandatory_fields_shipping(country_id)orself._get_mandatory_fields_billing(country_id)

        #errormessageforemptyrequiredfields
        forfield_nameinrequired_fields:
            ifnotdata.get(field_name):
                error[field_name]='missing'

        #emailvalidation
        ifdata.get('email')andnottools.single_email_re.match(data.get('email')):
            error["email"]='error'
            error_message.append(_('InvalidEmail!Pleaseenteravalidemailaddress.'))

        #vatvalidation
        Partner=request.env['res.partner']
        ifdata.get("vat")andhasattr(Partner,"check_vat"):
            ifcountry_id:
                data["vat"]=Partner.fix_eu_vat_number(country_id,data.get("vat"))
            partner_dummy=Partner.new(self._get_vat_validation_fields(data))
            try:
                partner_dummy.check_vat()
            exceptValidationErrorasexception:
                error["vat"]='error'
                error_message.append(exception.args[0])

        if[errforerrinerror.values()iferr=='missing']:
            error_message.append(_('Somerequiredfieldsareempty.'))

        returnerror,error_message

    def_get_vat_validation_fields(self,data):
        return{
            'vat':data['vat'],
            'country_id':int(data['country_id'])ifdata.get('country_id')elseFalse,
        }

    def_checkout_form_save(self,mode,checkout,all_values):
        Partner=request.env['res.partner']
        ifmode[0]=='new':
            partner_id=Partner.sudo().with_context(tracking_disable=True).create(checkout).id
        elifmode[0]=='edit':
            partner_id=int(all_values.get('partner_id',0))
            ifpartner_id:
                #doublecheck
                order=request.website.sale_get_order()
                shippings=Partner.sudo().search([("id","child_of",order.partner_id.commercial_partner_id.ids)])
                ifpartner_idnotinshippings.mapped('id')andpartner_id!=order.partner_id.id:
                    returnForbidden()
                Partner.browse(partner_id).sudo().write(checkout)
        returnpartner_id

    defvalues_preprocess(self,order,mode,values):
        new_values=dict()
        partner_fields=request.env['res.partner']._fields

        fork,vinvalues.items():
            #Convertthevaluesformany2onefieldstointegersincetheyareusedasIDs
            ifkinpartner_fieldsandpartner_fields[k].type=='many2one':
                new_values[k]=bool(v)andint(v)
            #Storeemptyfieldsas`False`insteadofemptystrings`''`forconsistencywithotherapplicationslike
            #Contacts.
            elifv=='':
                new_values[k]=False
            else:
                new_values[k]=v

        returnnew_values

    defvalues_postprocess(self,order,mode,values,errors,error_msg):
        new_values={}
        authorized_fields=request.env['ir.model']._get('res.partner')._get_form_writable_fields()
        fork,vinvalues.items():
            #don'tdropemptyvalue,itcouldbeafieldtoreset
            ifkinauthorized_fieldsandvisnotNone:
                new_values[k]=v
            else: #DEBUGONLY
                ifknotin('field_required','partner_id','callback','submitted'):#classiccase
                    _logger.debug("website_salepostprocess:%svaluehasbeendropped(emptyornotwritable)"%k)

        ifrequest.website.specific_user_account:
            new_values['website_id']=request.website.id

        ifmode[0]=='new':
            new_values['company_id']=request.website.company_id.id
            new_values['team_id']=request.website.salesteam_idandrequest.website.salesteam_id.id
            new_values['user_id']=request.website.salesperson_id.id

        lang=request.lang.codeifrequest.lang.codeinrequest.website.mapped('language_ids.code')elseNone
        iflang:
            new_values['lang']=lang
        ifmode==('edit','billing')andorder.partner_id.type=='contact':
            new_values['type']='other'
        ifmode[1]=='shipping':
            new_values['parent_id']=order.partner_id.commercial_partner_id.id
            new_values['type']='delivery'

        returnnew_values,errors,error_msg

    @http.route(['/shop/address'],type='http',methods=['GET','POST'],auth="public",website=True,sitemap=False)
    defaddress(self,**kw):
        Partner=request.env['res.partner'].with_context(show_address=1).sudo()
        order=request.website.sale_get_order()

        redirection=self.checkout_redirection(order)
        ifredirection:
            returnredirection

        mode=(False,False)
        can_edit_vat=False
        values,errors={},{}

        partner_id=int(kw.get('partner_id',-1))

        #IFPUBLICORDER
        iforder.partner_id.id==request.website.user_id.sudo().partner_id.id:
            mode=('new','billing')
            can_edit_vat=True
        #IFORDERLINKEDTOAPARTNER
        else:
            ifpartner_id>0:
                ifpartner_id==order.partner_id.id:
                    mode=('edit','billing')
                    can_edit_vat=order.partner_id.can_edit_vat()
                else:
                    shippings=Partner.search([('id','child_of',order.partner_id.commercial_partner_id.ids)])
                    iforder.partner_id.commercial_partner_id.id==partner_id:
                        mode=('new','shipping')
                        partner_id=-1
                    elifpartner_idinshippings.mapped('id'):
                        mode=('edit','shipping')
                    else:
                        returnForbidden()
                ifmodeandpartner_id!=-1:
                    values=Partner.browse(partner_id)
            elifpartner_id==-1:
                mode=('new','shipping')
            else:#nomode-refreshwithoutpost?
                returnrequest.redirect('/shop/checkout')

        #IFPOSTED
        if'submitted'inkwandrequest.httprequest.method=="POST":
            pre_values=self.values_preprocess(order,mode,kw)
            errors,error_msg=self.checkout_form_validate(mode,kw,pre_values)
            post,errors,error_msg=self.values_postprocess(order,mode,pre_values,errors,error_msg)

            iferrors:
                errors['error_message']=error_msg
                values=kw
            else:
                partner_id=self._checkout_form_save(mode,post,kw)
                #Weneedtovalidate_checkout_form_savereturn,becausewhenpartner_idnotinshippings
                #itreturnsForbidden()insteadthepartner_id
                ifisinstance(partner_id,Forbidden):
                    returnpartner_id
                ifmode[1]=='billing':
                    order.partner_id=partner_id
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                    #Thisisthe*only*thingthatthefrontenduserwillsee/editanywaywhenchoosingbillingaddress
                    order.partner_invoice_id=partner_id
                    ifnotkw.get('use_same'):
                        kw['callback']=kw.get('callback')or\
                            (notorder.only_servicesand(mode[0]=='edit'and'/shop/checkout'or'/shop/address'))
                    #Weneedtoupdatethepricelist(bytheoneselectedbythecustomer),becauseonchange_partnerresetit
                    #Weonlyneedtoupdatethepricelistwhenitisnotredirectedto/confirm_order
                    ifkw.get('callback',False)!='/shop/confirm_order':
                        request.website.sale_get_order(update_pricelist=True)
                elifmode[1]=='shipping':
                    order.partner_shipping_id=partner_id

                #TDEFIXME:don'teverdothis
                order.message_partner_ids=[(4,partner_id),(3,request.website.partner_id.id)]
                ifnoterrors:
                    returnrequest.redirect(kw.get('callback')or'/shop/confirm_order')

        render_values={
            'website_sale_order':order,
            'partner_id':partner_id,
            'mode':mode,
            'checkout':values,
            'can_edit_vat':can_edit_vat,
            'error':errors,
            'callback':kw.get('callback'),
            'only_services':orderandorder.only_services,
        }
        render_values.update(self._get_country_related_render_values(kw,render_values))
        returnrequest.render("website_sale.address",render_values)

    def_get_country_related_render_values(self,kw,render_values):
        '''
        Thismethodprovidesfieldsrelatedtothecountrytorenderthewebsitesaleform
        '''
        values=render_values['checkout']
        mode=render_values['mode']
        order=render_values['website_sale_order']

        def_country_id=order.partner_id.country_id
        #IFPUBLICORDER
        iforder.partner_id.id==request.website.user_id.sudo().partner_id.id:
            country_code=request.session['geoip'].get('country_code')
            ifcountry_code:
                def_country_id=request.env['res.country'].search([('code','=',country_code)],limit=1)
            else:
                def_country_id=request.website.user_id.sudo().country_id

        country='country_id'invaluesandvalues['country_id']!=''andrequest.env['res.country'].browse(int(values['country_id']))
        country=countryandcountry.exists()ordef_country_id

        res={
            'country':country,
            'country_states':country.get_website_sale_states(mode=mode[1]),
            'countries':country.get_website_sale_countries(mode=mode[1]),
        }
        returnres

    @http.route(['/shop/checkout'],type='http',auth="public",website=True,sitemap=False)
    defcheckout(self,**post):
        order=request.website.sale_get_order()

        redirection=self.checkout_redirection(order)
        ifredirection:
            returnredirection

        iforder.partner_id.id==request.website.user_id.sudo().partner_id.id:
            returnrequest.redirect('/shop/address')

        redirection=self.checkout_check_address(order)
        ifredirection:
            returnredirection

        values=self.checkout_values(**post)

        ifpost.get('express'):
            returnrequest.redirect('/shop/confirm_order')

        values.update({'website_sale_order':order})

        #Avoiduselessrenderingifcalledinajax
        ifpost.get('xhr'):
            return'ok'
        returnrequest.render("website_sale.checkout",values)

    @http.route(['/shop/confirm_order'],type='http',auth="public",website=True,sitemap=False)
    defconfirm_order(self,**post):
        order=request.website.sale_get_order()

        redirection=self.checkout_redirection(order)orself.checkout_check_address(order)
        ifredirection:
            returnredirection

        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id']=order.id
        request.website.sale_get_order(update_pricelist=True)
        extra_step=request.website.viewref('website_sale.extra_info_option')
        ifextra_step.active:
            returnrequest.redirect("/shop/extra_info")

        returnrequest.redirect("/shop/payment")

    #------------------------------------------------------
    #Extrastep
    #------------------------------------------------------
    @http.route(['/shop/extra_info'],type='http',auth="public",website=True,sitemap=False)
    defextra_info(self,**post):
        #Checkthatthisoptionisactivated
        extra_step=request.website.viewref('website_sale.extra_info_option')
        ifnotextra_step.active:
            returnrequest.redirect("/shop/payment")

        #checkthatcartisvalid
        order=request.website.sale_get_order()
        redirection=self.checkout_redirection(order)
        ifredirection:
            returnredirection

        #ifformposted
        if'post_values'inpost:
            values={}
            forfield_name,field_valueinpost.items():
                iffield_nameinrequest.env['sale.order']._fieldsandfield_name.startswith('x_'):
                    values[field_name]=field_value
            ifvalues:
                order.write(values)
            returnrequest.redirect("/shop/payment")

        values={
            'website_sale_order':order,
            'post':post,
            'escape':lambdax:x.replace("'",r"\'"),
            'partner':order.partner_id.id,
            'order':order,
        }

        returnrequest.render("website_sale.extra_info",values)

    #------------------------------------------------------
    #Payment
    #------------------------------------------------------

    def_get_shop_payment_values(self,order,**kwargs):
        values=dict(
            website_sale_order=order,
            errors=[],
            partner=order.partner_id.id,
            order=order,
            payment_action_id=request.env.ref('payment.action_payment_acquirer').id,
            return_url='/shop/payment/validate',
            bootstrap_formatting=True
        )
        iforder.partner_id.company_idandorder.partner_id.company_id.id!=order.company_id.id:
            values['errors'].append(
                (_('Sorry,weareunabletofindaPaymentMethod'),
                 _('Nopaymentmethodisavailableforyourcurrentorder.'
                   'Pleasecontactusformoreinformation.')))
            returnvalues

        domain=expression.AND([
            ['&',('state','in',['enabled','test']),('company_id','=',order.company_id.id)],
            ['|',('website_id','=',False),('website_id','=',request.website.id)],
            ['|',('country_ids','=',False),('country_ids','in',[order.partner_id.country_id.id])]
        ])
        acquirers=request.env['payment.acquirer'].search(domain)

        values['access_token']=order.access_token
        values['acquirers']=[acqforacqinacquirersif(acq.payment_flow=='form'andacq.view_template_id)or
                                    (acq.payment_flow=='s2s'andacq.registration_view_template_id)]
        values['tokens']=request.env['payment.token'].search([
            ('acquirer_id','in',acquirers.ids),
            ('partner_id','child_of',order.partner_id.commercial_partner_id.id)])

        iforder:
            values['acq_extra_fees']=acquirers.get_acquirer_extra_fees(order.amount_total,order.currency_id,order.partner_id.country_id.id)
        returnvalues

    @http.route(['/shop/payment'],type='http',auth="public",website=True,sitemap=False)
    defpayment(self,**post):
        """Paymentstep.Thispageproposesseveralpaymentmeansbasedonavailable
        payment.acquirer.Stateatthispoint:

         -adraftsalesorderwithlines;otherwise,cleancontext/sessionand
           backtotheshop
         -notransactionincontext/session,oronlyadraftone,ifthecustomer
           didgotoapayment.acquirerwebsitebutclosedthetabwithout
           paying/canceling
        """
        order=request.website.sale_get_order()
        redirection=self.checkout_redirection(order)orself.checkout_check_address(order)
        ifredirection:
            returnredirection

        render_values=self._get_shop_payment_values(order,**post)
        render_values['only_services']=orderandorder.only_servicesorFalse

        ifrender_values['errors']:
            render_values.pop('acquirers','')
            render_values.pop('tokens','')

        returnrequest.render("website_sale.payment",render_values)

    @http.route(['/shop/payment/transaction/',
        '/shop/payment/transaction/<int:so_id>',
        '/shop/payment/transaction/<int:so_id>/<string:access_token>'],type='json',auth="public",website=True)
    defpayment_transaction(self,acquirer_id,save_token=False,so_id=None,access_token=None,token=None,**kwargs):
        """Jsonmethodthatcreatesapayment.transaction,usedtocreatea
        transactionwhentheuserclickson'paynow'button.Afterhaving
        createdthetransaction,theeventcontinuesandtheuserisredirected
        totheacquirerwebsite.

        :paramintacquirer_id:idofapayment.acquirerrecord.Ifnotsetthe
                                userisredirectedtothecheckoutpage
        """
        #Ensureapaymentacquirerisselected
        ifnotacquirer_id:
            returnFalse

        try:
            acquirer_id=int(acquirer_id)
        except:
            returnFalse

        #Retrievethesaleorder
        ifso_id:
            env=request.env['sale.order']
            domain=[('id','=',so_id)]
            ifaccess_token:
                env=env.sudo()
                domain.append(('access_token','=',access_token))
            order=env.search(domain,limit=1)
        else:
            order=request.website.sale_get_order()

        #Ensurethereissomethingtoproceed
        ifnotorderor(orderandnotorder.order_line):
            returnFalse

        assertorder.partner_id.id!=request.website.partner_id.id

        #Createtransaction
        vals={'acquirer_id':acquirer_id,
                'return_url':'/shop/payment/validate'}

        ifsave_token:
            vals['type']='form_save'
        iftoken:
            vals['payment_token_id']=int(token)

        transaction=order._create_payment_transaction(vals)

        #storethenewtransactionintothetransactionlistandifthere'sanoldone,weremoveit
        #untilthedaytheecommercesupportsmultipleordersatthesametime
        last_tx_id=request.session.get('__website_sale_last_tx_id')
        last_tx=request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        iflast_tx:
            PaymentProcessing.remove_payment_transaction(last_tx)
        PaymentProcessing.add_payment_transaction(transaction)
        request.session['__website_sale_last_tx_id']=transaction.id
        returntransaction.render_sale_button(order)

    @http.route('/shop/payment/token',type='http',auth='public',website=True,sitemap=False)
    defpayment_token(self,pm_id=None,**kwargs):
        """Methodthathandlespaymentusingsavedtokens

        :paramintpm_id:idofthepayment.tokenthatwewanttousetopay.
        """
        order=request.website.sale_get_order()
        #donotcrashiftheuserhasalreadypaidandtrytopayagain
        ifnotorder:
            returnrequest.redirect('/shop/?error=no_order')

        assertorder.partner_id.id!=request.website.partner_id.id

        try:
            pm_id=int(pm_id)
        exceptValueError:
            returnrequest.redirect('/shop/?error=invalid_token_id')

        #Weretrievethetokentheuserwanttousetopay
        ifnotrequest.env['payment.token'].sudo().search_count([('id','=',pm_id)]):
            returnrequest.redirect('/shop/?error=token_not_found')

        #Createtransaction
        vals={'payment_token_id':pm_id,'return_url':'/shop/payment/validate'}

        tx=order._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(tx)
        returnrequest.redirect('/payment/process')

    @http.route('/shop/payment/get_status/<int:sale_order_id>',type='json',auth="public",website=True)
    defpayment_get_status(self,sale_order_id,**post):
        order=request.env['sale.order'].sudo().browse(sale_order_id).exists()
        iforder.id!=request.session.get('sale_last_order_id'):
            #eithersomethingwentwrongorthesessionisunbound
            #preventrecallingevery3rdofasecondintheJSwidget
            return{}

        return{
            'recall':order.get_portal_last_transaction().state=='pending',
            'message':request.env['ir.ui.view']._render_template("website_sale.payment_confirmation_status",{
                'order':order
            })
        }

    @http.route('/shop/payment/validate',type='http',auth="public",website=True,sitemap=False)
    defpayment_validate(self,transaction_id=None,sale_order_id=None,**post):
        """Methodthatshouldbecalledbytheserverwhenreceivinganupdate
        foratransaction.Stateatthispoint:

         -UDPATEME
        """
        ifsale_order_idisNone:
            order=request.website.sale_get_order()
            ifnotorderand'sale_last_order_id'inrequest.session:
                #Retrievethelastknownorderfromthesessionifthesessionkey`sale_order_id`
                #wasprematurelycleared.Thisisdonetopreventtheuserfromupdatingtheircart
                #afterpaymentincasetheydon'treturnfrompaymentthroughthisroute.
                last_order_id=request.session['sale_last_order_id']
                order=request.env['sale.order'].sudo().browse(last_order_id).exists()
        else:
            order=request.env['sale.order'].sudo().browse(sale_order_id)
            assertorder.id==request.session.get('sale_last_order_id')

        iftransaction_id:
            tx=request.env['payment.transaction'].sudo().browse(transaction_id)
            asserttxinorder.transaction_ids()
        eliforder:
            tx=order.get_portal_last_transaction()
        else:
            tx=None

        ifnotorderor(order.amount_totalandnottx):
            returnrequest.redirect('/shop')

        iforderandnotorder.amount_totalandnottx:
            order.with_context(send_email=True).action_confirm()
            returnrequest.redirect(order.get_portal_url())

        #cleancontextandsession,thenredirecttotheconfirmationpage
        request.website.sale_reset()
        iftxandtx.state=='draft':
            returnrequest.redirect('/shop')

        PaymentProcessing.remove_payment_transaction(tx)
        returnrequest.redirect('/shop/confirmation')

    @http.route(['/shop/terms'],type='http',auth="public",website=True,sitemap=True)
    defterms(self,**kw):
        returnrequest.render("website_sale.terms")

    @http.route(['/shop/confirmation'],type='http',auth="public",website=True,sitemap=False)
    defpayment_confirmation(self,**post):
        """Endofcheckoutprocesscontroller.Confirmationisbasicallyseing
        thestatusofasale.order.Stateatthispoint:

         -shouldnothaveanycontext/sessioninfo:cleanthem
         -takeasale.orderid,becausewerequestasale.orderandarenot
           sessiondependantanymore
        """
        sale_order_id=request.session.get('sale_last_order_id')
        ifsale_order_id:
            order=request.env['sale.order'].sudo().browse(sale_order_id)
            returnrequest.render("website_sale.confirmation",{'order':order})
        else:
            returnrequest.redirect('/shop')

    @http.route(['/shop/print'],type='http',auth="public",website=True,sitemap=False)
    defprint_saleorder(self,**kwargs):
        sale_order_id=request.session.get('sale_last_order_id')
        ifsale_order_id:
            pdf,_=request.env.ref('sale.action_report_saleorder').with_user(SUPERUSER_ID)._render_qweb_pdf([sale_order_id])
            pdfhttpheaders=[('Content-Type','application/pdf'),('Content-Length',u'%s'%len(pdf))]
            returnrequest.make_response(pdf,headers=pdfhttpheaders)
        else:
            returnrequest.redirect('/shop')

    @http.route(['/shop/tracking_last_order'],type='json',auth="public")
    deftracking_cart(self,**post):
        """returndataaboutorderinJSONneededforgoogleanalytics"""
        ret={}
        sale_order_id=request.session.get('sale_last_order_id')
        ifsale_order_id:
            order=request.env['sale.order'].sudo().browse(sale_order_id)
            ret=self.order_2_return_dict(order)
        returnret

    #------------------------------------------------------
    #Edit
    #------------------------------------------------------

    @http.route(['/shop/add_product'],type='json',auth="user",methods=['POST'],website=True)
    defadd_product(self,name=None,category=None,**post):
        product=request.env['product.product'].create({
            'name':nameor_("NewProduct"),
            'public_categ_ids':category,
            'website_id':request.website.id,
        })
        return"%s?enable_editor=1"%product.product_tmpl_id.website_url

    @http.route(['/shop/change_sequence'],type='json',auth='user')
    defchange_sequence(self,id,sequence):
        product_tmpl=request.env['product.template'].browse(id)
        ifsequence=="top":
            product_tmpl.set_sequence_top()
        elifsequence=="bottom":
            product_tmpl.set_sequence_bottom()
        elifsequence=="up":
            product_tmpl.set_sequence_up()
        elifsequence=="down":
            product_tmpl.set_sequence_down()

    @http.route(['/shop/change_size'],type='json',auth='user')
    defchange_size(self,id,x,y):
        product=request.env['product.template'].browse(id)
        returnproduct.write({'website_size_x':x,'website_size_y':y})

    @http.route(['/shop/change_ppg'],type='json',auth='user')
    defchange_ppg(self,ppg):
        request.env['website'].get_current_website().shop_ppg=ppg

    @http.route(['/shop/change_ppr'],type='json',auth='user')
    defchange_ppr(self,ppr):
        request.env['website'].get_current_website().shop_ppr=ppr

    deforder_lines_2_google_api(self,order_lines):
        """Transformsalistoforderlinesintoadictforgoogleanalytics"""
        ret=[]
        forlineinorder_lines:
            product=line.product_id
            ret.append({
                'id':line.order_id.id,
                'sku':product.barcodeorproduct.id,
                'name':product.nameor'-',
                'category':product.categ_id.nameor'-',
                'price':line.price_unit,
                'quantity':line.product_uom_qty,
            })
        returnret

    deforder_2_return_dict(self,order):
        """Returnsthetracking_cartdictoftheorderforGoogleanalyticsbasicallydefinedtobeinherited"""
        return{
            'transaction':{
                'id':order.id,
                'affiliation':order.company_id.name,
                'revenue':order.amount_total,
                'tax':order.amount_tax,
                'currency':order.currency_id.name
            },
            'lines':self.order_lines_2_google_api(order.order_line)
        }

    @http.route(['/shop/country_infos/<model("res.country"):country>'],type='json',auth="public",methods=['POST'],website=True)
    defcountry_infos(self,country,mode,**kw):
        returndict(
            fields=country.get_address_fields(),
            states=[(st.id,st.name,st.code)forstincountry.get_website_sale_states(mode=mode)],
            phone_code=country.phone_code,
            zip_required=country.zip_required,
            state_required=country.state_required,
        )

    #--------------------------------------------------------------------------
    #ProductsSearchBar
    #--------------------------------------------------------------------------

    @http.route('/shop/products/autocomplete',type='json',auth='public',website=True)
    defproducts_autocomplete(self,term,options={},**kwargs):
        """
        Returnslistofproductsaccordingtothetermandproductoptions

        Params:
            term(str):searchtermwrittenbytheuser
            options(dict)
                -'limit'(int),defaultto5:numberofproductstoconsider
                -'display_description'(bool),defaulttoTrue
                -'display_price'(bool),defaulttoTrue
                -'order'(str)
                -'max_nb_chars'(int):maxnumberofcharactersforthe
                                        descriptionifreturned

        Returns:
            dict(orFalseifnoresult)
                -'products'(list):products(onlytheirneededfieldvalues)
                        note:thepriceswillbestringsproperlyformattedand
                        alreadycontainingthecurrency
                -'products_count'(int):thenumberofproductsinthedatabase
                        thatmatchedthesearchquery
        """
        ProductTemplate=request.env['product.template']

        display_description=options.get('display_description',True)
        display_price=options.get('display_price',True)
        order=self._get_search_order(options)
        max_nb_chars=options.get('max_nb_chars',999)

        category=options.get('category')
        attrib_values=options.get('attrib_values')

        domain=self._get_search_domain(term,category,attrib_values,display_description)
        products=ProductTemplate.search(
            domain,
            limit=min(20,options.get('limit',5)),
            order=order
        )

        fields=['id','name','website_url']
        ifdisplay_description:
            fields.append('description_sale')

        res={
            'products':products.read(fields),
            'products_count':ProductTemplate.search_count(domain),
        }

        ifdisplay_description:
            forres_productinres['products']:
                desc=res_product['description_sale']
                ifdescandlen(desc)>max_nb_chars:
                    res_product['description_sale']="%s..."%desc[:(max_nb_chars-3)]

        ifdisplay_price:
            FieldMonetary=request.env['ir.qweb.field.monetary']
            monetary_options={
                'display_currency':request.website.get_current_pricelist().currency_id,
            }
            forres_product,productinzip(res['products'],products):
                combination_info=product._get_combination_info(only_template=True)
                res_product.update(combination_info)
                res_product['list_price']=FieldMonetary.value_to_html(res_product['list_price'],monetary_options)
                res_product['price']=FieldMonetary.value_to_html(res_product['price'],monetary_options)

        returnres

    #--------------------------------------------------------------------------
    #ProductsRecentlyViewed
    #--------------------------------------------------------------------------
    @http.route('/shop/products/recently_viewed',type='json',auth='public',website=True)
    defproducts_recently_viewed(self,**kwargs):
        returnself._get_products_recently_viewed()

    def_get_products_recently_viewed(self):
        """
        Returnslistofrecentlyviewedproductsaccordingtocurrentuser
        """
        max_number_of_product_for_carousel=12
        visitor=request.env['website.visitor']._get_visitor_from_request()
        ifvisitor:
            excluded_products=request.website.sale_get_order().mapped('order_line.product_id.id')
            products=request.env['website.track'].sudo().read_group(
                [('visitor_id','=',visitor.id),('product_id','!=',False),('product_id.website_published','=',True),('product_id','notin',excluded_products)],
                ['product_id','visit_datetime:max'],['product_id'],limit=max_number_of_product_for_carousel,orderby='visit_datetimeDESC')
            products_ids=[product['product_id'][0]forproductinproducts]
            ifproducts_ids:
                viewed_products=request.env['product.product'].with_context(display_default_code=False).search([('id','in',products_ids)])

                FieldMonetary=request.env['ir.qweb.field.monetary']
                monetary_options={
                    'display_currency':request.website.get_current_pricelist().currency_id,
                }
                rating=request.website.viewref('website_sale.product_comment').active
                res={'products':[]}
                forproductinviewed_products:
                    combination_info=product._get_combination_info_variant()
                    res_product=product.read(['id','name','website_url'])[0]
                    res_product.update(combination_info)
                    res_product['price']=FieldMonetary.value_to_html(res_product['price'],monetary_options)
                    ifrating:
                        res_product['rating']=request.env["ir.ui.view"]._render_template('portal_rating.rating_widget_stars_static',values={
                            'rating_avg':product.rating_avg,
                            'rating_count':product.rating_count,
                        })
                    res['products'].append(res_product)

                returnres
        return{}

    @http.route('/shop/products/recently_viewed_update',type='json',auth='public',website=True)
    defproducts_recently_viewed_update(self,product_id,**kwargs):
        res={}
        visitor_sudo=request.env['website.visitor']._get_visitor_from_request(force_create=True)
        ifvisitor_sudo:
            ifrequest.httprequest.cookies.get('visitor_uuid','')!=visitor_sudo.access_token:
                res['visitor_uuid']=visitor_sudo.access_token
            visitor_sudo._add_viewed_product(product_id)
        returnres

    @http.route('/shop/products/recently_viewed_delete',type='json',auth='public',website=True)
    defproducts_recently_viewed_delete(self,product_id,**kwargs):
        visitor_sudo=request.env['website.visitor']._get_visitor_from_request()
        ifvisitor_sudo:
            request.env['website.track'].sudo().search([('visitor_id','=',visitor_sudo.id),('product_id','=',product_id)]).unlink()
        returnself._get_products_recently_viewed()

    #--------------------------------------------------------------------------
    #WebsiteSnippetFilters
    #--------------------------------------------------------------------------

    @http.route('/website_sale/snippet/options_filters',type='json',auth='user',website=True)
    defget_dynamic_snippet_filters(self):
        domain=expression.AND([
            request.website.website_domain(),
            ['|',('filter_id.model_id','=','product.product'),('action_server_id.model_id.model','=','product.product')]
        ])
        filters=request.env['website.snippet.filter'].sudo().search_read(
            domain,['id']
        )
        returnfilters
