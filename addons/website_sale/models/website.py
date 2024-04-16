#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportapi,fields,models,tools,SUPERUSER_ID,_

fromflectra.httpimportrequest
fromflectra.addons.website.modelsimportir_http
fromflectra.addons.http_routing.models.ir_httpimporturl_for

_logger=logging.getLogger(__name__)


classWebsite(models.Model):
    _inherit='website'

    pricelist_id=fields.Many2one('product.pricelist',compute='_compute_pricelist_id',string='DefaultPricelist')
    currency_id=fields.Many2one('res.currency',
        related='pricelist_id.currency_id',depends=(),related_sudo=False,
        string='DefaultCurrency',readonly=False)
    salesperson_id=fields.Many2one('res.users',string='Salesperson')

    def_get_default_website_team(self):
        try:
            team=self.env.ref('sales_team.salesteam_website_sales')
            returnteamifteam.activeelseNone
        exceptValueError:
            returnNone

    salesteam_id=fields.Many2one('crm.team',
        string='SalesTeam',
        default=_get_default_website_team)
    pricelist_ids=fields.One2many('product.pricelist',compute="_compute_pricelist_ids",
                                    string='PricelistavailableforthisEcommerce/Website')
    all_pricelist_ids=fields.One2many('product.pricelist','website_id',string='Allpricelists',
                                        help='Technical:Usedtorecomputepricelist_ids')

    def_default_recovery_mail_template(self):
        try:
            returnself.env.ref('website_sale.mail_template_sale_cart_recovery').id
        exceptValueError:
            returnFalse

    cart_recovery_mail_template_id=fields.Many2one('mail.template',string='CartRecoveryEmail',default=_default_recovery_mail_template,domain="[('model','=','sale.order')]")
    cart_abandoned_delay=fields.Float("AbandonedDelay",default=1.0)

    shop_ppg=fields.Integer(default=20,string="Numberofproductsinthegridontheshop")
    shop_ppr=fields.Integer(default=4,string="Numberofgridcolumnsontheshop")

    shop_extra_field_ids=fields.One2many('website.sale.extra.field','website_id',string='E-CommerceExtraFields')

    @api.depends('all_pricelist_ids')
    def_compute_pricelist_ids(self):
        Pricelist=self.env['product.pricelist']
        forwebsiteinself:
            website.pricelist_ids=Pricelist.search(
                Pricelist._get_website_pricelists_domain(website.id)
            )

    def_compute_pricelist_id(self):
        forwebsiteinself:
            website.pricelist_id=website.with_context(website_id=website.id).get_current_pricelist()

    #Thismethodiscached,mustnotreturnrecords!Seealso#8795
    @tools.ormcache('self.env.uid','country_code','show_visible','website_pl','current_pl','all_pl','partner_pl','order_pl')
    def_get_pl_partner_order(self,country_code,show_visible,website_pl,current_pl,all_pl,partner_pl=False,order_pl=False):
        """Returnthelistofpriceliststhatcanbeusedonwebsiteforthecurrentuser.
        :paramstrcountry_code:codeisoorFalse,Ifset,wesearchonlypricelistavailableforthiscountry
        :paramboolshow_visible:ifTrue,wedon'tdisplaypricelistwhereselectableisFalse(Eg:Codepromo)
        :paramintwebsite_pl:Thedefaultpricelistusedonthiswebsite
        :paramintcurrent_pl:Thecurrentpricelistusedonthewebsite
                               (Ifnotselectablebutthecurrentpricelistwehadthispricelistanyway)
        :paramlistall_pl:Listofallpricelistavailableforthiswebsite
        :paramintpartner_pl:thepartnerpricelist
        :paramintorder_pl:thecurrentcartpricelist
        :returns:listofpricelistids
        """
        def_check_show_visible(pl):
            """If`show_visible`isTrue,wewillonlyshowthepricelistif
            oneofthisconditionismet:
            -Thepricelistis`selectable`.
            -Thepricelistiseitherthecurrentlyusedpricelistorthe
            currentcartpricelist,weshouldconsideritasavailableevenif
            itmightnotbewebsitecompliant(eg:itisnotselectableanymore,
            itisabackendpricelist,itisnotactiveanymore..).
            """
            return(notshow_visibleorpl.selectableorpl.idin(current_pl,order_pl))

        #Note:1.pricelistsfromall_plarealreadywebsitecompliant(wentthrough
        #         `_get_website_pricelists_domain`)
        #      2.donotread`property_product_pricelist`hereas`_get_pl_partner_order`
        #         iscachedandtheresultofthismethodwillbeimpactedbythatfieldvalue.
        #         Passitthrough`partner_pl`parameterinsteadtoinvalidatethecache.

        #IfthereisaGeoIPcountry,findapricelistforit
        self.ensure_one()
        pricelists=self.env['product.pricelist']
        ifcountry_code:
            forcgroupinself.env['res.country.group'].search([('country_ids.code','=',country_code)]):
                pricelists|=cgroup.pricelist_ids.filtered(
                    lambdapl:pl._is_available_on_website(self.id)and_check_show_visible(pl)
                )

        #noGeoIPornopricelistforthiscountry
        ifnotcountry_codeornotpricelists:
            pricelists|=all_pl.filtered(lambdapl:_check_show_visible(pl))

        #ifloggedin,addpartnerpl(whichis`property_product_pricelist`,mightnotbewebsitecompliant)
        is_public=self.user_id.id==self.env.user.id
        ifnotis_public:
            #keeppartner_plonlyifwebsitecompliant
            partner_pl=pricelists.browse(partner_pl).filtered(lambdapl:pl._is_available_on_website(self.id)and_check_show_visible(pl))
            ifcountry_code:
                #keeppartner_plonlyifGeoIPcompliantincaseofGeoIPenabled
                partner_pl=partner_pl.filtered(
                    lambdapl:pl.country_group_idsandcountry_codeinpl.country_group_ids.mapped('country_ids.code')ornotpl.country_group_ids
                )
            pricelists|=partner_pl

        #Thismethodiscached,mustnotreturnrecords!Seealso#8795
        returnpricelists.ids

    def_get_pricelist_available(self,req,show_visible=False):
        """Returnthelistofpriceliststhatcanbeusedonwebsiteforthecurrentuser.
        CountryrestrictionswillbedetectedwithGeoIP(ifinstalled).
        :paramboolshow_visible:ifTrue,wedon'tdisplaypricelistwhereselectableisFalse(Eg:Codepromo)
        :returns:pricelistrecordset
        """
        website=ir_http.get_request_website()
        ifnotwebsite:
            ifself.env.context.get('website_id'):
                website=self.browse(self.env.context['website_id'])
            else:
                #Intheweirdcasewearecomingfromthebackend(https://github.com/flectra/flectra/issues/20245)
                website=len(self)==1andselforself.search([],limit=1)
        isocountry=reqandreq.session.geoipandreq.session.geoip.get('country_code')orFalse
        partner=self.env.user.partner_id
        last_order_pl=partner.last_website_so_id.pricelist_id
        partner_pl=partner.property_product_pricelist
        pricelists=website._get_pl_partner_order(isocountry,show_visible,
                                                   website.user_id.sudo().partner_id.property_product_pricelist.id,
                                                   reqandreq.session.get('website_sale_current_pl')orNone,
                                                   website.pricelist_ids,
                                                   partner_pl=partner_plandpartner_pl.idorNone,
                                                   order_pl=last_order_plandlast_order_pl.idorNone)
        returnself.env['product.pricelist'].browse(pricelists)

    defget_pricelist_available(self,show_visible=False):
        returnself._get_pricelist_available(request,show_visible)

    defis_pricelist_available(self,pl_id):
        """Returnabooleantospecifyifaspecificpricelistcanbemanuallysetonthewebsite.
        Warning:Itcheckonlyifpricelistisinthe'selectable'pricelistsorthecurrentpricelist.
        :paramintpl_id:Thepricelistidtocheck
        :returns:Boolean,Trueifvalid/available
        """
        returnpl_idinself.get_pricelist_available(show_visible=False).ids

    defget_current_pricelist(self):
        """
        :returns:Thecurrentpricelistrecord
        """
        #Thelistofavailablepricelistsforthisuser.
        #Iftheuserissignedin,andhasapricelistsetdifferentthanthepublicuserpricelist
        #thenthispricelistwillalwaysbeconsideredasavailable
        available_pricelists=self.get_pricelist_available()
        pl=None
        partner=self.env.user.partner_id
        ifrequestandrequest.session.get('website_sale_current_pl'):
            #`website_sale_current_pl`issetonlyiftheuserspecificallychoseit:
            # -Either,hechoseitfromthepricelistselection
            # -Either,heenteredacouponcode
            pl=self.env['product.pricelist'].browse(request.session['website_sale_current_pl'])
            ifplnotinavailable_pricelists:
                pl=None
                request.session.pop('website_sale_current_pl')
        ifnotpl:
            #Iftheuserhasasavedcart,ittakethepricelistofthislastunconfirmedcart
            pl=partner.last_website_so_id.pricelist_id
            ifnotpl:
                #Thepricelistoftheusersetonitspartnerform.
                #Iftheuserisnotsignedin,it'sthepublicuserpricelist
                pl=partner.property_product_pricelist
            ifavailable_pricelistsandplnotinavailable_pricelists:
                #Ifthereisatleastonepricelistintheavailablepricelists
                #andthechosenpricelistisnotwithinthem
                #itthenchoosethefirstavailablepricelist.
                #Thiscanonlyhappenwhenthepricelististhepublicuserpricelistandthispricelistisnotintheavailablepricelistforthislocalization
                #Iftheuserissignedin,andhasaspecialpricelist(differentthanthepublicuserpricelist),
                #thenthisspecialpricelistisamongstheseavailablepricelists,andthereforeitwon'tfallinthiscase.
                pl=available_pricelists[0]

        ifnotpl:
            _logger.error('Failtofindpricelistforpartner"%s"(id%s)',partner.name,partner.id)
        returnpl

    defsale_product_domain(self):
        return[("sale_ok","=",True)]+self.get_current_website().website_domain()

    @api.model
    defsale_get_payment_term(self,partner):
        pt=self.env.ref('account.account_payment_term_immediate',False).sudo()
        ifpt:
            pt=(notpt.company_id.idorself.company_id.id==pt.company_id.id)andpt
        return(
            partner.property_payment_term_idor
            ptor
            self.env['account.payment.term'].sudo().search([('company_id','=',self.company_id.id)],limit=1)
        ).id

    def_prepare_sale_order_values(self,partner,pricelist):
        self.ensure_one()
        affiliate_id=request.session.get('affiliate_id')
        salesperson_id=affiliate_idifself.env['res.users'].sudo().browse(affiliate_id).exists()elserequest.website.salesperson_id.id
        addr=partner.address_get(['delivery'])
        ifnotrequest.website.is_public_user():
            last_sale_order=self.env['sale.order'].sudo().search([('partner_id','=',partner.id)],limit=1,order="date_orderdesc,iddesc")
            iflast_sale_orderandlast_sale_order.partner_shipping_id.active: #first=me
                addr['delivery']=last_sale_order.partner_shipping_id.id
        default_user_id=partner.parent_id.user_id.idorpartner.user_id.id
        values={
            'partner_id':partner.id,
            'pricelist_id':pricelist.id,
            'payment_term_id':self.sale_get_payment_term(partner),
            'team_id':self.salesteam_id.idorpartner.parent_id.team_id.idorpartner.team_id.id,
            'partner_invoice_id':partner.id,
            'partner_shipping_id':addr['delivery'],
            'user_id':salesperson_idorself.salesperson_id.idordefault_user_id,
            'website_id':self._context.get('website_id'),
        }
        company=self.company_idorpricelist.company_id
        ifcompany:
            values['company_id']=company.id
        returnvalues

    defsale_get_order(self,force_create=False,code=None,update_pricelist=False,force_pricelist=False):
        """Returnthecurrentsalesorderaftermoficationsspecifiedbyparams.
        :paramboolforce_create:Createsalesorderifnotalreadyexisting
        :paramstrcode:Codetoforceapricelist(promocode)
                         Ifempty,it'saspecialcasetoresetthepricelistwiththefirstavailableelsethedefault.
        :paramboolupdate_pricelist:Forcetorecomputeallthelinesfromsalesordertoadaptthepricewiththecurrentpricelist.
        :paramintforce_pricelist:pricelist_id-ifset, wechangethepricelistwiththisone
        :returns:browserecordforthecurrentsalesorder
        """
        self.ensure_one()
        partner=self.env.user.partner_id
        sale_order_id=request.session.get('sale_order_id')
        check_fpos=False
        ifnotsale_order_idandnotself.env.user._is_public():
            last_order=partner.last_website_so_id
            iflast_order:
                available_pricelists=self.get_pricelist_available()
                #Donotreloadthecartofthisuserlastvisitifthecartusesapricelistnolongeravailable.
                sale_order_id=last_order.pricelist_idinavailable_pricelistsandlast_order.id
                check_fpos=True

        #Testvalidityofthesale_order_id
        sale_order=self.env['sale.order'].with_company(request.website.company_id.id).sudo().browse(sale_order_id).exists()ifsale_order_idelseNone

        #Ignorethecurrentorderifapaymenthasbeeninitiated.Wedon'twanttoretrievethe
        #cartandallowtheusertoupdateitwhenthepaymentisabouttoconfirmit.
        ifsale_orderandsale_order.get_portal_last_transaction().statein('pending','authorized','done'):
            sale_order=None

        #DonotreloadthecartofthisuserlastvisitiftheFiscalPositionhaschanged.
        ifcheck_fposandsale_order:
            fpos_id=(
                self.env['account.fiscal.position'].sudo()
                .with_company(sale_order.company_id.id)
                .get_fiscal_position(sale_order.partner_id.id,delivery_id=sale_order.partner_shipping_id.id)
            ).id
            ifsale_order.fiscal_position_id.id!=fpos_id:
                sale_order=None

        ifnot(sale_orderorforce_createorcode):
            ifrequest.session.get('sale_order_id'):
                request.session['sale_order_id']=None
            returnself.env['sale.order']

        ifself.env['product.pricelist'].browse(force_pricelist).exists():
            pricelist_id=force_pricelist
            request.session['website_sale_current_pl']=pricelist_id
            update_pricelist=True
        else:
            pricelist_id=request.session.get('website_sale_current_pl')orself.get_current_pricelist().id

        ifnotself._context.get('pricelist'):
            self=self.with_context(pricelist=pricelist_id)

        #cartcreationwasrequested(eitherexplicitlyortoconfigureapromocode)
        ifnotsale_order:
            #TODOcachepartner_idsession
            pricelist=self.env['product.pricelist'].browse(pricelist_id).sudo()
            so_data=self._prepare_sale_order_values(partner,pricelist)
            sale_order=self.env['sale.order'].with_company(request.website.company_id.id).with_user(SUPERUSER_ID).create(so_data)

            #setfiscalposition
            ifrequest.website.partner_id.id!=partner.id:
                sale_order.onchange_partner_shipping_id()
            else:#Forpublicuser,fiscalpositionbasedongeolocation
                country_code=request.session['geoip'].get('country_code')
                ifcountry_code:
                    country_id=request.env['res.country'].search([('code','=',country_code)],limit=1).id
                    sale_order.fiscal_position_id=request.env['account.fiscal.position'].sudo().with_company(request.website.company_id.id)._get_fpos_by_region(country_id)
                else:
                    #ifnogeolocation,usethepublicuserfp
                    sale_order.onchange_partner_shipping_id()

            request.session['sale_order_id']=sale_order.id

            #TheorderwascreatedwithSUPERUSER_ID,revertbacktorequestuser.
            sale_order=sale_order.with_user(self.env.user).sudo()

        #casewhenuseremptiedthecart
        ifnotrequest.session.get('sale_order_id'):
            request.session['sale_order_id']=sale_order.id

        #checkforchangeofpricelistwithacoupon
        pricelist_id=pricelist_idorpartner.property_product_pricelist.id

        #checkforchangeofpartner_idieaftersignup
        ifsale_order.partner_id.id!=partner.idandrequest.website.partner_id.id!=partner.id:
            flag_pricelist=False
            ifpricelist_id!=sale_order.pricelist_id.id:
                flag_pricelist=True
            fiscal_position=sale_order.fiscal_position_id.id

            #changethepartner,andtriggertheonchange
            sale_order.write({'partner_id':partner.id})
            sale_order.with_context(not_self_saleperson=True).onchange_partner_id()
            sale_order.write({'partner_invoice_id':partner.id})
            sale_order.onchange_partner_shipping_id()#fiscalposition
            sale_order['payment_term_id']=self.sale_get_payment_term(partner)

            #checkthepricelist:updateitifthepricelistisnotthe'forced'one
            values={}
            ifsale_order.pricelist_id:
                ifsale_order.pricelist_id.id!=pricelist_id:
                    values['pricelist_id']=pricelist_id
                    update_pricelist=True

            #iffiscalposition,updatetheorderlinestaxes
            ifsale_order.fiscal_position_id:
                sale_order._compute_tax_id()

            #ifvalues,thenmaketheSOupdate
            ifvalues:
                sale_order.write(values)

            #checkifthefiscalpositionhaschangedwiththepartner_idupdate
            recent_fiscal_position=sale_order.fiscal_position_id.id
            #whenbuyingafreeproductwithpublicuserandtryingtologin,SOstateisnotdraft
            if(flag_pricelistorrecent_fiscal_position!=fiscal_position)andsale_order.state=='draft':
                update_pricelist=True

        ifcodeandcode!=sale_order.pricelist_id.code:
            code_pricelist=self.env['product.pricelist'].sudo().search([('code','=',code)],limit=1)
            ifcode_pricelist:
                pricelist_id=code_pricelist.id
                update_pricelist=True
        elifcodeisnotNoneandsale_order.pricelist_id.codeandcode!=sale_order.pricelist_id.code:
            #codeisnotNonewhenuserremovescodeandclickon"Apply"
            pricelist_id=partner.property_product_pricelist.id
            update_pricelist=True

        #updatethepricelist
        ifupdate_pricelist:
            request.session['website_sale_current_pl']=pricelist_id
            values={'pricelist_id':pricelist_id}
            sale_order.write(values)
            forlineinsale_order.order_line:
                ifline.exists():
                    sale_order._cart_update(product_id=line.product_id.id,line_id=line.id,add_qty=0)

        returnsale_order

    defsale_reset(self):
        request.session.update({
            'sale_order_id':False,
            'website_sale_current_pl':False,
        })

    @api.model
    defaction_dashboard_redirect(self):
        ifself.env.user.has_group('sales_team.group_sale_salesman'):
            returnself.env["ir.actions.actions"]._for_xml_id("website.backend_dashboard")
        returnsuper(Website,self).action_dashboard_redirect()

    defget_suggested_controllers(self):
        suggested_controllers=super(Website,self).get_suggested_controllers()
        suggested_controllers.append((_('eCommerce'),url_for('/shop'),'website_sale'))
        returnsuggested_controllers

    def_bootstrap_snippet_filters(self):
        super(Website,self)._bootstrap_snippet_filters()
        #Thesamebehaviorisdoneinthepost_inithook
        action=self.env.ref('website_sale.dynamic_snippet_products_action',raise_if_not_found=False)
        ifaction:
            self.env['website.snippet.filter'].create({
                'action_server_id':action.id,
                'field_names':'display_name,description_sale,image_512,list_price',
                'limit':16,
                'name':_('Products'),
                'website_id':self.id,
            })


classWebsiteSaleExtraField(models.Model):
    _name='website.sale.extra.field'
    _description='E-CommerceExtraInfoShownonproductpage'
    _order='sequence'

    website_id=fields.Many2one('website')
    sequence=fields.Integer(default=10)
    field_id=fields.Many2one(
        'ir.model.fields',
        domain=[('model_id.model','=','product.template'),('ttype','in',['char','binary'])]
    )
    label=fields.Char(related='field_id.field_description')
    name=fields.Char(related='field_id.name')
