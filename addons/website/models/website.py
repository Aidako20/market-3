#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importinspect
importlogging
importhashlib
importre


fromwerkzeugimporturls
fromwerkzeug.datastructuresimportOrderedMultiDict
fromwerkzeug.exceptionsimportNotFound

fromflectraimportapi,fields,models,tools,http
fromflectra.addons.base.models.ir_modelimportMODULE_UNINSTALL_FLAG
fromflectra.addons.http_routing.models.ir_httpimportslugify,_guess_mimetype,url_for
fromflectra.addons.website.models.ir_httpimportsitemap_qs2dom
fromflectra.addons.portal.controllers.portalimportpager
fromflectra.exceptionsimportUserError
fromflectra.httpimportrequest
fromflectra.modules.moduleimportget_resource_path
fromflectra.osv.expressionimportFALSE_DOMAIN
fromflectra.tools.translateimport_

logger=logging.getLogger(__name__)


DEFAULT_CDN_FILTERS=[
    "^/[^/]+/static/",
    "^/web/(css|js)/",
    "^/web/image",
    "^/web/content",
    #retrocompatibility
    "^/website/image/",
]


classWebsite(models.Model):

    _name="website"
    _description="Website"

    @api.model
    defwebsite_domain(self,website_id=False):
        return[('website_id','in',(False,website_idorself.id))]

    def_active_languages(self):
        returnself.env['res.lang'].search([]).ids

    def_default_language(self):
        lang_code=self.env['ir.default'].get('res.partner','lang')
        def_lang_id=self.env['res.lang']._lang_get_id(lang_code)
        returndef_lang_idorself._active_languages()[0]

    name=fields.Char('WebsiteName',required=True)
    domain=fields.Char('WebsiteDomain',
        help='WillbeprefixedbyhttpincanonicalURLsifnoschemeisspecified')
    country_group_ids=fields.Many2many('res.country.group','website_country_group_rel','website_id','country_group_id',
                                         string='CountryGroups',help='Usedwhenmultiplewebsiteshavethesamedomain.')
    company_id=fields.Many2one('res.company',string="Company",default=lambdaself:self.env.company,required=True)
    language_ids=fields.Many2many('res.lang','website_lang_rel','website_id','lang_id','Languages',default=_active_languages)
    default_lang_id=fields.Many2one('res.lang',string="DefaultLanguage",default=_default_language,required=True)
    auto_redirect_lang=fields.Boolean('AutoredirectLanguage',default=True,help="Shouldusersberedirectedtotheirbrowser'slanguage")
    cookies_bar=fields.Boolean('CookiesBar',help="Displayacustomizablecookiesbaronyourwebsite.")

    def_default_social_facebook(self):
        returnself.env.ref('base.main_company').social_facebook

    def_default_social_github(self):
        returnself.env.ref('base.main_company').social_github

    def_default_social_linkedin(self):
        returnself.env.ref('base.main_company').social_linkedin

    def_default_social_youtube(self):
        returnself.env.ref('base.main_company').social_youtube

    def_default_social_instagram(self):
        returnself.env.ref('base.main_company').social_instagram

    def_default_social_twitter(self):
        returnself.env.ref('base.main_company').social_twitter

    def_default_logo(self):
        image_path=get_resource_path('website','static/src/img','website_logo.png')
        withtools.file_open(image_path,'rb')asf:
            returnbase64.b64encode(f.read())

    logo=fields.Binary('WebsiteLogo',default=_default_logo,help="Displaythislogoonthewebsite.")
    social_twitter=fields.Char('TwitterAccount',default=_default_social_twitter)
    social_facebook=fields.Char('FacebookAccount',default=_default_social_facebook)
    social_github=fields.Char('GitHubAccount',default=_default_social_github)
    social_linkedin=fields.Char('LinkedInAccount',default=_default_social_linkedin)
    social_youtube=fields.Char('YoutubeAccount',default=_default_social_youtube)
    social_instagram=fields.Char('InstagramAccount',default=_default_social_instagram)
    social_default_image=fields.Binary(string="DefaultSocialShareImage",help="Ifset,replacesthewebsitelogoasthedefaultsocialshareimage.")
    has_social_default_image=fields.Boolean(compute='_compute_has_social_default_image',store=True)

    google_analytics_key=fields.Char('GoogleAnalyticsKey')
    google_management_client_id=fields.Char('GoogleClientID')
    google_management_client_secret=fields.Char('GoogleClientSecret')
    google_search_console=fields.Char(help='Googlekey,orEnabletoaccessfirstreply')

    google_maps_api_key=fields.Char('GoogleMapsAPIKey')

    user_id=fields.Many2one('res.users',string='PublicUser',required=True)
    cdn_activated=fields.Boolean('ContentDeliveryNetwork(CDN)')
    cdn_url=fields.Char('CDNBaseURL',default='')
    cdn_filters=fields.Text('CDNFilters',default=lambdas:'\n'.join(DEFAULT_CDN_FILTERS),help="URLmatchingthosefilterswillberewrittenusingtheCDNBaseURL")
    partner_id=fields.Many2one(related='user_id.partner_id',string='PublicPartner',readonly=False)
    menu_id=fields.Many2one('website.menu',compute='_compute_menu',string='MainMenu')
    homepage_id=fields.Many2one('website.page',string='Homepage')
    custom_code_head=fields.Text('Custom<head>code')
    custom_code_footer=fields.Text('Customendof<body>code')

    robots_txt=fields.Text('Robots.txt',translate=False,groups='website.group_website_designer')

    def_default_favicon(self):
        img_path=get_resource_path('web','static/src/img/favicon.ico')
        withtools.file_open(img_path,'rb')asf:
            returnbase64.b64encode(f.read())

    favicon=fields.Binary(string="WebsiteFavicon",help="Thisfieldholdstheimageusedtodisplayafavicononthewebsite.",default=_default_favicon)
    theme_id=fields.Many2one('ir.module.module',help='Installedtheme')

    specific_user_account=fields.Boolean('SpecificUserAccount',help='IfTrue,newaccountswillbeassociatedtothecurrentwebsite')
    auth_signup_uninvited=fields.Selection([
        ('b2b','Oninvitation'),
        ('b2c','Freesignup'),
    ],string='CustomerAccount',default='b2b')

    @api.onchange('language_ids')
    def_onchange_language_ids(self):
        language_ids=self.language_ids._origin
        iflanguage_idsandself.default_lang_idnotinlanguage_ids:
            self.default_lang_id=language_ids[0]

    @api.depends('social_default_image')
    def_compute_has_social_default_image(self):
        forwebsiteinself:
            website.has_social_default_image=bool(website.social_default_image)

    def_compute_menu(self):
        forwebsiteinself:
            menus=self.env['website.menu'].browse(website._get_menu_ids())

            #usefieldparent_id(1query)todeterminefieldchild_id(2queriesbylevel)"
            formenuinmenus:
                menu._cache['child_id']=()
            formenuinmenus:
                #don'taddchildmenuifparentisforbidden
                ifmenu.parent_idandmenu.parent_idinmenus:
                    menu.parent_id._cache['child_id']+=(menu.id,)

            #prefetcheverywebsite.pageandir.ui.viewatonce
            menus.mapped('is_visible')

            top_menus=menus.filtered(lambdam:notm.parent_id)
            website.menu_id=top_menusandtop_menus[0].idorFalse

    #self.env.uidforir.rulegroupsonmenu
    @tools.ormcache('self.env.uid','self.id')
    def_get_menu_ids(self):
        returnself.env['website.menu'].search([('website_id','=',self.id)]).ids

    def_bootstrap_snippet_filters(self):
        ir_filter=self.env.ref('website.dynamic_snippet_country_filter',raise_if_not_found=False)
        ifir_filter:
            self.env['website.snippet.filter'].create({
                'field_names':'name,code,image_url:image,phone_code:char',
                'filter_id':ir_filter.id,
                'limit':16,
                'name':_('Countries'),
                'website_id':self.id,
            })

    @api.model
    defcreate(self,vals):
        self._handle_favicon(vals)

        if'user_id'notinvals:
            company=self.env['res.company'].browse(vals.get('company_id'))
            vals['user_id']=company._get_public_user().idifcompanyelseself.env.ref('base.public_user').id

        res=super(Website,self).create(vals)
        res._bootstrap_homepage()
        res._bootstrap_snippet_filters()

        ifnotself.env.user.has_group('website.group_multi_website')andself.search_count([])>1:
            all_user_groups='base.group_portal,base.group_user,base.group_public'
            groups=self.env['res.groups'].concat(*(self.env.ref(it)foritinall_user_groups.split(',')))
            groups.write({'implied_ids':[(4,self.env.ref('website.group_multi_website').id)]})

        returnres

    defwrite(self,values):
        public_user_to_change_websites=self.env['website']
        self._handle_favicon(values)

        self.clear_caches()

        if'company_id'invaluesand'user_id'notinvalues:
            public_user_to_change_websites=self.filtered(lambdaw:w.sudo().user_id.company_id.id!=values['company_id'])
            ifpublic_user_to_change_websites:
                company=self.env['res.company'].browse(values['company_id'])
                super(Website,public_user_to_change_websites).write(dict(values,user_id=companyandcompany._get_public_user().id))

        result=super(Website,self-public_user_to_change_websites).write(values)
        if'cdn_activated'invaluesor'cdn_url'invaluesor'cdn_filters'invalues:
            #invalidatethecachesfromstaticnodeatcompiletime
            self.env['ir.qweb'].clear_caches()

        if'cookies_bar'invalues:
            existing_policy_page=self.env['website.page'].search([
                ('website_id','=',self.id),
                ('url','=','/cookie-policy'),
            ])
            ifnotvalues['cookies_bar']:
                existing_policy_page.unlink()
            elifnotexisting_policy_page:
                cookies_view=self.env.ref('website.cookie_policy',raise_if_not_found=False)
                ifcookies_view:
                    cookies_view.with_context(website_id=self.id).write({'website_id':self.id})
                    specific_cook_view=self.with_context(website_id=self.id).viewref('website.cookie_policy')
                    self.env['website.page'].create({
                        'is_published':True,
                        'website_indexed':False,
                        'url':'/cookie-policy',
                        'website_id':self.id,
                        'view_id':specific_cook_view.id,
                    })

        returnresult

    @api.model
    def_handle_favicon(self,vals):
        if'favicon'invals:
            vals['favicon']=tools.image_process(vals['favicon'],size=(256,256),crop='center',output_format='ICO')

    defunlink(self):
        ifnotself.env.context.get(MODULE_UNINSTALL_FLAG,False):
            website=self.search([('id','notin',self.ids)],limit=1)
            ifnotwebsite:
                raiseUserError(_('Youmustkeepatleastonewebsite.'))

        self._remove_attachments_on_website_unlink()

        returnsuper().unlink()

    def_remove_attachments_on_website_unlink(self):
        #Donotdeleteinvoices,deletewhat'sstrictlynecessary
        attachments_to_unlink=self.env['ir.attachment'].search([
            ('website_id','in',self.ids),
            '|','|',
            ('key','!=',False), #themeattachment
            ('url','ilike','.custom.'), #customizedthemeattachment
            ('url','ilike','.assets\\_'),
        ])
        attachments_to_unlink.unlink()

    defcreate_and_redirect_to_theme(self):
        self._force()
        action=self.env.ref('website.theme_install_kanban_action')
        returnaction.read()[0]

    #----------------------------------------------------------
    #PageManagement
    #----------------------------------------------------------
    def_bootstrap_homepage(self):
        Page=self.env['website.page']
        standard_homepage=self.env.ref('website.homepage',raise_if_not_found=False)
        ifnotstandard_homepage:
            return

        new_homepage_view='''<tname="Homepage"t-name="website.homepage%s">
        <tt-call="website.layout">
            <tt-set="pageName"t-value="'homepage'"/>
            <divid="wrap"class="oe_structureoe_empty"/>
            </t>
        </t>'''%(self.id)
        standard_homepage.with_context(website_id=self.id).arch_db=new_homepage_view

        homepage_page=Page.search([
            ('website_id','=',self.id),
            ('key','=',standard_homepage.key),
        ],limit=1)
        ifnothomepage_page:
            homepage_page=Page.create({
                'website_published':True,
                'url':'/',
                'view_id':self.with_context(website_id=self.id).viewref('website.homepage').id,
            })
        #prevent/-1ashomepageURL
        homepage_page.url='/'
        self.homepage_id=homepage_page

        #Bootstrapdefaultmenuhierarchy,createanewminimalistoneifnodefault
        default_menu=self.env.ref('website.main_menu')
        self.copy_menu_hierarchy(default_menu)
        home_menu=self.env['website.menu'].search([('website_id','=',self.id),('url','=','/')])
        home_menu.page_id=self.homepage_id

    defcopy_menu_hierarchy(self,top_menu):
        defcopy_menu(menu,t_menu):
            new_menu=menu.copy({
                'parent_id':t_menu.id,
                'website_id':self.id,
            })
            forsubmenuinmenu.child_id:
                copy_menu(submenu,new_menu)
        forwebsiteinself:
            new_top_menu=top_menu.copy({
                'name':_('TopMenuforWebsite%s',website.id),
                'website_id':website.id,
            })
            forsubmenuintop_menu.child_id:
                copy_menu(submenu,new_top_menu)

    @api.model
    defnew_page(self,name=False,add_menu=False,template='website.default_page',ispage=True,namespace=None):
        """Createanewwebsitepage,andassignitaxmlidbasedonthegivenone
            :paramname:thenameofthepage
            :paramtemplate:potentialxml_idofthepagetocreate
            :paramnamespace:modulepartofthexml_idifnone,thetemplatemodulenameisused
        """
        ifnamespace:
            template_module=namespace
        else:
            template_module,_=template.split('.')
        page_url='/'+slugify(name,max_length=1024,path=True)
        page_url=self.get_unique_path(page_url)
        page_key=slugify(name)
        result=dict({'url':page_url,'view_id':False})

        ifnotname:
            name='Home'
            page_key='home'

        template_record=self.env.ref(template)
        website_id=self._context.get('website_id')
        key=self.get_unique_key(page_key,template_module)
        view=template_record.copy({'website_id':website_id,'key':key})

        view.with_context(lang=None).write({
            'arch':template_record.arch.replace(template,key),
            'name':name,
        })

        ifview.arch_fs:
            view.arch_fs=False

        website=self.get_current_website()
        ifispage:
            page=self.env['website.page'].create({
                'url':page_url,
                'website_id':website.id, #removeitifonlyonewebsiteornot?
                'view_id':view.id,
                'track':True,
            })
            result['view_id']=view.id
        ifadd_menu:
            self.env['website.menu'].create({
                'name':name,
                'url':page_url,
                'parent_id':website.menu_id.id,
                'page_id':page.id,
                'website_id':website.id,
            })
        returnresult

    @api.model
    defguess_mimetype(self):
        return_guess_mimetype()

    defget_unique_path(self,page_url):
        """Givenanurl,returnthaturlsuffixedbycounterifitalreadyexists
            :parampage_url:theurltobecheckedforuniqueness
        """
        inc=0
        #weonlywantaunique_pathforwebsitespecific.
        #weneedtobeabletohave/urlforwebsite=False,and/urlforwebsite=1
        #incaseofduplicate,pagemanagerwillallowyoutomanagethiscase
        domain_static=[('website_id','=',self.get_current_website().id)] #.website_domain()
        page_temp=page_url
        whileself.env['website.page'].with_context(active_test=False).sudo().search([('url','=',page_temp)]+domain_static):
            inc+=1
            page_temp=page_url+(incand"-%s"%incor"")
        returnpage_temp

    defget_unique_key(self,string,template_module=False):
        """Givenastring,returnanuniquekeyincludingmoduleprefix.
            Itwillbesuffixedbyacounterifitalreadyexiststogaranteeuniqueness.
            :paramstring:thekeytobecheckedforuniqueness,youcanpassitwith'website.'ornot
            :paramtemplate_module:themoduletobeprefixedonthekey,ifnotset,wewillusewebsite
        """
        iftemplate_module:
            string=template_module+'.'+string
        else:
            ifnotstring.startswith('website.'):
                string='website.'+string

        #Lookforuniquekey
        key_copy=string
        inc=0
        domain_static=self.get_current_website().website_domain()
        whileself.env['ir.ui.view'].with_context(active_test=False).sudo().search([('key','=',key_copy)]+domain_static):
            inc+=1
            key_copy=string+(incand"-%s"%incor"")
        returnkey_copy

    @api.model
    defpage_search_dependencies(self,page_id=False):
        """Searchdependenciesjustforinformation.Itwillnotcatch100%
            ofdependenciesandFalsepositiveismorethanpossible
            Eachmodulecouldadddependencesinthisdict
            :returnsadictionnarywherekeyisthe'categorie'ofobjectrelatedtothegiven
                view,andthevalueisthelistoftextandlinktotheresourceusinggivenpage
        """
        dependencies={}
        ifnotpage_id:
            returndependencies

        page=self.env['website.page'].browse(int(page_id))
        website=self.env['website'].browse(self._context.get('website_id'))
        url=page.url

        #searchforwebsite_pagewithlink
        website_page_search_dom=[('view_id.arch_db','ilike',url)]+website.website_domain()
        pages=self.env['website.page'].search(website_page_search_dom)
        page_key=_('Page')
        iflen(pages)>1:
            page_key=_('Pages')
        page_view_ids=[]
        forpageinpages:
            dependencies.setdefault(page_key,[])
            dependencies[page_key].append({
                'text':_('Page<b>%s</b>containsalinktothispage',page.url),
                'item':page.name,
                'link':page.url,
            })
            page_view_ids.append(page.view_id.id)

        #searchforir_ui_view(notfromawebsite_page)withlink
        page_search_dom=[('arch_db','ilike',url),('id','notin',page_view_ids)]+website.website_domain()
        views=self.env['ir.ui.view'].search(page_search_dom)
        view_key=_('Template')
        iflen(views)>1:
            view_key=_('Templates')
        forviewinviews:
            dependencies.setdefault(view_key,[])
            dependencies[view_key].append({
                'text':_('Template<b>%s(id:%s)</b>containsalinktothispage')%(view.keyorview.name,view.id),
                'link':'/web#id=%s&view_type=form&model=ir.ui.view'%view.id,
                'item':_('%s(id:%s)')%(view.keyorview.name,view.id),
            })
        #searchformenuwithlink
        menu_search_dom=[('url','ilike','%s'%url)]+website.website_domain()

        menus=self.env['website.menu'].search(menu_search_dom)
        menu_key=_('Menu')
        iflen(menus)>1:
            menu_key=_('Menus')
        formenuinmenus:
            dependencies.setdefault(menu_key,[]).append({
                'text':_('Thispageisinthemenu<b>%s</b>',menu.name),
                'link':'/web#id=%s&view_type=form&model=website.menu'%menu.id,
                'item':menu.name,
            })

        returndependencies

    @api.model
    defpage_search_key_dependencies(self,page_id=False):
        """Searchdependenciesjustforinformation.Itwillnotcatch100%
            ofdependenciesandFalsepositiveismorethanpossible
            Eachmodulecouldadddependencesinthisdict
            :returnsadictionnarywherekeyisthe'categorie'ofobjectrelatedtothegiven
                view,andthevalueisthelistoftextandlinktotheresourceusinggivenpage
        """
        dependencies={}
        ifnotpage_id:
            returndependencies

        page=self.env['website.page'].browse(int(page_id))
        website=self.env['website'].browse(self._context.get('website_id'))
        key=page.key

        #searchforwebsite_pagewithlink
        website_page_search_dom=[
            ('view_id.arch_db','ilike',key),
            ('id','!=',page.id)
        ]+website.website_domain()
        pages=self.env['website.page'].search(website_page_search_dom)
        page_key=_('Page')
        iflen(pages)>1:
            page_key=_('Pages')
        page_view_ids=[]
        forpinpages:
            dependencies.setdefault(page_key,[])
            dependencies[page_key].append({
                'text':_('Page<b>%s</b>iscallingthisfile',p.url),
                'item':p.name,
                'link':p.url,
            })
            page_view_ids.append(p.view_id.id)

        #searchforir_ui_view(notfromawebsite_page)withlink
        page_search_dom=[
            ('arch_db','ilike',key),('id','notin',page_view_ids),
            ('id','!=',page.view_id.id),
        ]+website.website_domain()
        views=self.env['ir.ui.view'].search(page_search_dom)
        view_key=_('Template')
        iflen(views)>1:
            view_key=_('Templates')
        forviewinviews:
            dependencies.setdefault(view_key,[])
            dependencies[view_key].append({
                'text':_('Template<b>%s(id:%s)</b>iscallingthisfile')%(view.keyorview.name,view.id),
                'item':_('%s(id:%s)')%(view.keyorview.name,view.id),
                'link':'/web#id=%s&view_type=form&model=ir.ui.view'%view.id,
            })

        returndependencies

    #----------------------------------------------------------
    #Languages
    #----------------------------------------------------------

    def_get_alternate_languages(self,canonical_params):
        self.ensure_one()

        ifnotself._is_canonical_url(canonical_params=canonical_params):
            #nohreflangonnon-canonicalpages
            return[]

        languages=self.language_ids
        iflen(languages)<=1:
            #nohreflangifnoalternatelanguage
            return[]

        langs=[]
        shorts=[]

        forlginlanguages:
            lg_codes=lg.code.split('_')
            short=lg_codes[0]
            shorts.append(short)
            langs.append({
                'hreflang':('-'.join(lg_codes)).lower(),
                'short':short,
                'href':self._get_canonical_url_localized(lang=lg,canonical_params=canonical_params),
            })

        #ifthereisonlyoneregionforalanguage,useonlythelanguagecode
        forlanginlangs:
            ifshorts.count(lang['short'])==1:
                lang['hreflang']=lang['short']

        #addthedefault
        langs.append({
            'hreflang':'x-default',
            'href':self._get_canonical_url_localized(lang=self.default_lang_id,canonical_params=canonical_params),
        })

        returnlangs

    #----------------------------------------------------------
    #Utilities
    #----------------------------------------------------------

    @api.model
    defget_current_website(self,fallback=True):
        ifrequestandrequest.session.get('force_website_id'):
            website_id=self.browse(request.session['force_website_id']).exists()
            ifnotwebsite_id:
                #Don'tcrashissessionwebsitegotdeleted
                request.session.pop('force_website_id')
            else:
                returnwebsite_id

        website_id=self.env.context.get('website_id')
        ifwebsite_id:
            returnself.browse(website_id)

        #Theformatof`httprequest.host`is`domain:port`
        domain_name=requestandrequest.httprequest.hostor''

        country=request.session.geoip.get('country_code')ifrequestandrequest.session.geoipelseFalse
        country_id=False
        ifcountry:
            country_id=self.env['res.country'].search([('code','=',country)],limit=1).id

        website_id=self._get_current_website_id(domain_name,country_id,fallback=fallback)
        returnself.browse(website_id)

    @tools.cache('domain_name','country_id','fallback')
    @api.model
    def_get_current_website_id(self,domain_name,country_id,fallback=True):
        """Getthecurrentwebsiteid.

        Firstfindallthewebsitesforwhichtheconfigured`domain`(after
        ignoringapotentialscheme)isequaltothegiven
        `domain_name`.Ifthereisonlyoneresult,returnitimmediately.

        Iftherearenowebsitefoundforthegiven`domain_name`,either
        fallbacktothefirstfoundwebsite(nomatterits`domain`)orreturn
        Falsedependingonthe`fallback`parameter.

        Iftherearemultiplewebsitesforthesame`domain_name`,weneedto
        filterthemoutbycountry.Wereturnthefirstfoundwebsitematching
        thegiven`country_id`.Ifnofoundwebsitematching`domain_name`
        correspondstothegiven`country_id`,thefirstfoundwebsitefor
        `domain_name`willbereturned(nomatteritscountry).

        :paramdomain_name:thedomainforwhichwewantthewebsite.
            Inregardtothe`url_parse`method,onlythe`netloc`partshould
            begivenhere,no`scheme`.
        :typedomain_name:string

        :paramcountry_id:idofthecountryforwhichwewantthewebsite
        :typecountry_id:int

        :paramfallback:ifTrueandnowebsiteisfoundforthespecificed
            `domain_name`,returnthefirstwebsite(withoutfilteringthem)
        :typefallback:bool

        :return:idofthefoundwebsite,orFalseifnowebsiteisfoundand
            `fallback`isFalse
        :rtype:intorFalse

        :raises:if`fallback`isTruebutnowebsiteatallisfound
        """
        def_remove_port(domain_name):
            return(domain_nameor'').split(':')[0]

        def_filter_domain(website,domain_name,ignore_port=False):
            """Ignore`scheme`fromthe`domain`,justmatchthe`netloc`which
            ishost:portintheversionof`url_parse`weuse."""
            #Hereweaddhttp://tothedomainifit'snotsetbecause
            #`url_parse`expectsittobesettocorrectlyreturnthe`netloc`.
            website_domain=urls.url_parse(website._get_http_domain()).netloc
            ifignore_port:
                website_domain=_remove_port(website_domain)
                domain_name=_remove_port(domain_name)
            returnwebsite_domain.lower()==(domain_nameor'').lower()

        #Sortoncountry_group_idssothatwefallbackonagenericwebsite:
        #websiteswithemptycountry_group_idswillbefirst.
        found_websites=self.search([('domain','ilike',_remove_port(domain_name))]).sorted('country_group_ids')
        #Filterfortheexactdomain(tofilteroutpotentialsubdomains)due
        #totheuseofilike.
        websites=found_websites.filtered(lambdaw:_filter_domain(w,domain_name))
        #Ifthereisnodomainmatchingforthegivenport,ignoretheport.
        websites=websitesorfound_websites.filtered(lambdaw:_filter_domain(w,domain_name,ignore_port=True))

        ifnotwebsites:
            ifnotfallback:
                returnFalse
            returnself.search([],limit=1).id
        eliflen(websites)==1:
            returnwebsites.id
        else: #>1websitewiththesamedomain
            country_specific_websites=websites.filtered(lambdawebsite:country_idinwebsite.country_group_ids.mapped('country_ids').ids)
            returncountry_specific_websites[0].idifcountry_specific_websiteselsewebsites[0].id

    def_force(self):
        self._force_website(self.id)

    def_force_website(self,website_id):
        ifrequest:
            request.session['force_website_id']=website_idandstr(website_id).isdigit()andint(website_id)

    @api.model
    defis_publisher(self):
        returnself.env['ir.model.access'].check('ir.ui.view','write',False)

    @api.model
    defis_user(self):
        returnself.env['ir.model.access'].check('ir.ui.menu','read',False)

    @api.model
    defis_public_user(self):
        returnrequest.env.user.id==request.website._get_cached('user_id')

    @api.model
    defviewref(self,view_id,raise_if_not_found=True):
        '''Givenanxml_idoraview_id,returnthecorrespondingviewrecord.
            Incaseofwebsitecontext,returnthemostspecificone.

            Ifnowebsite_idisinthecontext,itwillreturnthegenericview,
            insteadofarandomonelike`get_view_id`.

            Lookalsoforarchivedviews,nomatterthecontext.

            :paramview_id:eitherastringxml_idoranintegerview_id
            :paramraise_if_not_found:shouldthemethodraiseanerrorifnoviewfound
            :return:Theviewrecordoremptyrecordset
        '''
        View=self.env['ir.ui.view'].sudo()
        view=View
        ifisinstance(view_id,str):
            if'website_id'inself._context:
                domain=[('key','=',view_id)]+self.env['website'].website_domain(self._context.get('website_id'))
                order='website_id'
            else:
                domain=[('key','=',view_id)]
                order=View._order
            views=View.with_context(active_test=False).search(domain,order=order)
            ifviews:
                view=views.filter_duplicate()
            else:
                #wehandletheraisebelow
                view=self.env.ref(view_id,raise_if_not_found=False)
                #self.env.refmightreturnsomethingelsethananir.ui.view(eg:atheme.ir.ui.view)
                ifnotvieworview._name!='ir.ui.view':
                    #makesurewealwaysreturnarecordset
                    view=View
        elifisinstance(view_id,int):
            view=View.browse(view_id)
        else:
            raiseValueError('Expectingastringoraninteger,nota%s.'%(type(view_id)))

        ifnotviewandraise_if_not_found:
            raiseValueError('NorecordfoundforuniqueID%s.Itmayhavebeendeleted.'%(view_id))
        returnview

    @tools.ormcache_context(keys=('website_id',))
    def_cache_customize_show_views(self):
        views=self.env['ir.ui.view'].with_context(active_test=False).sudo().search([('customize_show','=',True)])
        views=views.filter_duplicate()
        return{v.key:v.activeforvinviews}

    @tools.ormcache_context('key',keys=('website_id',))
    defis_view_active(self,key,raise_if_not_found=False):
        """
            ReturnTrueifactive,Falseifnotactive,Noneifnotfoundornotacustomize_showview
        """
        views=self._cache_customize_show_views()
        view=keyinviewsandviews[key]
        ifviewisNoneandraise_if_not_found:
            raiseValueError('Noviewoftypecustomize_showfoundforkey%s'%key)
        returnview

    @api.model
    defget_template(self,template):
        View=self.env['ir.ui.view']
        ifisinstance(template,int):
            view_id=template
        else:
            if'.'notintemplate:
                template='website.%s'%template
            view_id=View.get_view_id(template)
        ifnotview_id:
            raiseNotFound
        returnView.sudo().browse(view_id)

    @api.model
    defpager(self,url,total,page=1,step=30,scope=5,url_args=None):
        returnpager(url,total,page=page,step=step,scope=scope,url_args=url_args)

    defrule_is_enumerable(self,rule):
        """ChecksthatitispossibletogeneratesensibleGETqueriesfor
            agivenrule(iftheendpointmatchesitsownrequirements)
            :typerule:werkzeug.routing.Rule
            :rtype:bool
        """
        endpoint=rule.endpoint
        methods=endpoint.routing.get('methods')or['GET']

        converters=list(rule._converters.values())
        ifnot('GET'inmethodsand
                endpoint.routing['type']=='http'and
                endpoint.routing['auth']in('none','public')and
                endpoint.routing.get('website',False)and
                all(hasattr(converter,'generate')forconverterinconverters)):
                returnFalse

        #dont'tlistrouteswithoutargumenthavingnodefaultvalueorconverter
        sign=inspect.signature(endpoint.method.original_func)
        params=list(sign.parameters.values())[1:] #skipself
        supported_kinds=(inspect.Parameter.POSITIONAL_ONLY,
                           inspect.Parameter.POSITIONAL_OR_KEYWORD)
        has_no_default=lambdap:p.defaultisinspect.Parameter.empty

        #checkthatallargshaveaconverter
        returnall(p.nameinrule._convertersforpinparams
                   ifp.kindinsupported_kindsandhas_no_default(p))

    def_enumerate_pages(self,query_string=None,force=False):
        """Availablepagesinthewebsite/CMS.Thisismostlyusedforlinks
            generationandcanbeoverriddenbymodulessettingupnewHTML
            controllersfordynamicpages(e.g.blog).
            Bydefault,returnstemplateviewsmarkedaspages.
            :paramstrquery_string:a(user-provided)string,fetchespages
                                     matchingthestring
            :returns:alistofmappingswithtwokeys:``name``isthedisplayable
                      nameoftheresource(page),``url``istheabsoluteURL
                      ofthesame.
            :rtype:list({name:str,url:str})
        """

        router=http.root.get_db_router(request.db)
        url_set=set()

        sitemap_endpoint_done=set()

        forruleinrouter.iter_rules():
            if'sitemap'inrule.endpoint.routingandrule.endpoint.routing['sitemap']isnotTrue:
                ifrule.endpointinsitemap_endpoint_done:
                    continue
                sitemap_endpoint_done.add(rule.endpoint)

                func=rule.endpoint.routing['sitemap']
                iffuncisFalse:
                    continue
                forlocinfunc(self.env,rule,query_string):
                    yieldloc
                continue

            ifnotself.rule_is_enumerable(rule):
                continue

            if'sitemap'notinrule.endpoint.routing:
                logger.warning('NoSitemapvalueprovidedforcontroller%s(%s)'%
                               (rule.endpoint.method,','.join(rule.endpoint.routing['routes'])))

            converters=rule._convertersor{}
            ifquery_stringandnotconvertersand(query_stringnotinrule.build({},append_unknown=False)[1]):
                continue

            values=[{}]
            #converterswithadomainareprocessedaftertheotherones
            convitems=sorted(
                converters.items(),
                key=lambdax:(hasattr(x[1],'domain')and(x[1].domain!='[]'),rule._trace.index((True,x[0]))))

            for(i,(name,converter))inenumerate(convitems):
                if'website_id'inself.env[converter.model]._fieldsand(notconverter.domainorconverter.domain=='[]'):
                    converter.domain="[('website_id','in',(False,current_website_id))]"

                newval=[]
                forvalinvalues:
                    query=i==len(convitems)-1andquery_string
                    ifquery:
                        r="".join([x[1]forxinrule._trace[1:]ifnotx[0]]) #removemodelconverterfromroute
                        query=sitemap_qs2dom(query,r,self.env[converter.model]._rec_name)
                        ifquery==FALSE_DOMAIN:
                            continue

                    forrecinconverter.generate(uid=self.env.uid,dom=query,args=val):
                        newval.append(val.copy())
                        newval[-1].update({name:rec})
                values=newval

            forvalueinvalues:
                domain_part,url=rule.build(value,append_unknown=False)
                ifnotquery_stringorquery_string.lower()inurl.lower():
                    page={'loc':url}
                    ifurlinurl_set:
                        continue
                    url_set.add(url)

                    yieldpage

        #'/'alreadyhasahttp.route&isintherouting_mapsoitwillalreadyhaveanentryinthexml
        domain=[('url','!=','/')]
        ifnotforce:
            domain+=[('website_indexed','=',True),('visibility','=',False)]
            #is_visible
            domain+=[
                ('website_published','=',True),('visibility','=',False),
                '|',('date_publish','=',False),('date_publish','<=',fields.Datetime.now())
            ]

        ifquery_string:
            domain+=[('url','like',query_string)]

        pages=self._get_website_pages(domain)

        forpageinpages:
            record={'loc':page['url'],'id':page['id'],'name':page['name']}
            ifpage.view_idandpage.view_id.priority!=16:
                record['priority']=min(round(page.view_id.priority/32.0,1),1)
            ifpage['write_date']:
                record['lastmod']=page['write_date'].date()
            yieldrecord

    def_get_website_pages(self,domain=None,order='name',limit=None):
        ifdomainisNone:
            domain=[]
        domain+=self.get_current_website().website_domain()
        pages=self.env['website.page'].sudo().search(domain,order=order,limit=limit)
        #TODOIn16.0removeconditionon_filter_duplicate_pages.
        ifself.env.context.get('_filter_duplicate_pages'):
            pages=pages.filtered(pages._is_most_specific_page)
        returnpages

    defsearch_pages(self,needle=None,limit=None):
        name=slugify(needle,max_length=50,path=True)
        res=[]
        forpageinself._enumerate_pages(query_string=name,force=True):
            res.append(page)
            iflen(res)==limit:
                break
        returnres

    defget_suggested_controllers(self):
        """
            Returnsatuple(name,url,icon).
            Whereiconcanbeamodulename,orapath
        """
        suggested_controllers=[
            (_('Homepage'),url_for('/'),'website'),
            (_('ContactUs'),url_for('/contactus'),'website_crm'),
        ]
        returnsuggested_controllers

    @api.model
    defimage_url(self,record,field,size=None):
        """Returnsalocalurlthatpointstotheimagefieldofagivenbrowserecord."""
        sudo_record=record.sudo()
        sha=hashlib.sha512(str(getattr(sudo_record,'__last_update')).encode('utf-8')).hexdigest()[:7]
        size=''ifsizeisNoneelse'/%s'%size
        return'/web/image/%s/%s/%s%s?unique=%s'%(record._name,record.id,field,size,sha)

    defget_cdn_url(self,uri):
        self.ensure_one()
        ifnoturi:
            return''
        cdn_url=self.cdn_url
        cdn_filters=(self.cdn_filtersor'').splitlines()
        forfltincdn_filters:
            iffltandre.match(flt,uri):
                returnurls.url_join(cdn_url,uri)
        returnuri

    @api.model
    defaction_dashboard_redirect(self):
        ifself.env.user.has_group('base.group_system')orself.env.user.has_group('website.group_website_designer'):
            returnself.env["ir.actions.actions"]._for_xml_id("website.backend_dashboard")
        returnself.env["ir.actions.actions"]._for_xml_id("website.action_website")

    defbutton_go_website(self,path='/',mode_edit=False):
        self._force()
        ifmode_edit:
            #Iftheusergetsonatranslatedpage(e.g/fr)theeditorwill
            #neverstart.Forcingthedefaultlanguagefixesthisissue.
            path=url_for(path,self.default_lang_id.url_code)
            path+='?enable_editor=1'
        return{
            'type':'ir.actions.act_url',
            'url':path,
            'target':'self',
        }

    def_get_http_domain(self):
        """Getthedomainofthecurrentwebsite,prefixedbyhttpifno
        schemeisspecifiedandwithtouttrailing/.

        Emptystringifnodomainisspecifiedonthewebsite.
        """
        self.ensure_one()
        ifnotself.domain:
            return''

        domain=self.domain
        ifnotself.domain.startswith('http'):
            domain='http://%s'%domain

        returndomain.rstrip('/')

    defget_base_url(self):
        self.ensure_one()
        returnself._get_http_domain()orsuper(BaseModel,self).get_base_url()

    def_get_canonical_url_localized(self,lang,canonical_params):
        """ReturnsthecanonicalURLforthecurrentrequestwithtranslatable
        elementsappropriatelytranslatedin`lang`.

        If`request.endpoint`isnottrue,returnsthecurrent`path`instead.

        `url_quote_plus`isappliedonthereturnedpath.
        """
        self.ensure_one()
        ifrequest.endpoint:
            router=http.root.get_db_router(request.db).bind('')
            arguments=dict(request.endpoint_arguments)
            forkey,valinlist(arguments.items()):
                ifisinstance(val,models.BaseModel):
                    ifval.env.context.get('lang')!=lang.code:
                        arguments[key]=val.with_context(lang=lang.code)
            path=router.build(request.endpoint,arguments)
        else:
            #ThebuildmethodreturnsaquotedURLsoconvertinthiscaseforconsistency.
            path=urls.url_quote_plus(request.httprequest.path,safe='/')
        lang_path=('/'+lang.url_code)iflang!=self.default_lang_idelse''
        canonical_query_string='?%s'%urls.url_encode(canonical_params)ifcanonical_paramselse''

        iflang_pathandpath=='/':
            #Wewant`/fr_BE`not`/fr_BE/`forcorrectcanonicalonhomepage
            localized_path=lang_path
        else:
            localized_path=lang_path+path

        returnself.get_base_url()+localized_path+canonical_query_string

    def_get_canonical_url(self,canonical_params):
        """ReturnsthecanonicalURLforthecurrentrequest."""
        self.ensure_one()
        returnself._get_canonical_url_localized(lang=request.lang,canonical_params=canonical_params)

    def_is_canonical_url(self,canonical_params):
        """ReturnswhetherthecurrentrequestURLiscanonical."""
        self.ensure_one()
        #CompareOrderedMultiDictbecausetheorderisimportant,theremustbe
        #onlyonecanonicalandnotparamspermutations.
        params=request.httprequest.args
        canonical_params=canonical_paramsorOrderedMultiDict()
        ifparams!=canonical_params:
            returnFalse
        #CompareURLatthefirstreroutingiteration(ifavailable)because
        #it'stheonewiththelanguageinthepath.
        #ItisimportanttoalsotestthedomainofthecurrentURL.
        current_url=request.httprequest.url_root[:-1]+(hasattr(request,'rerouting')andrequest.rerouting[0]orrequest.httprequest.path)
        canonical_url=self._get_canonical_url_localized(lang=request.lang,canonical_params=None)
        #Arequestpathwithquotablecharacters(suchas",")isnever
        #canonicalbecauserequest.httprequest.base_urlisalwaysunquoted,
        #andcanonicalurlisalwaysquoted,soitisneverpossibletotell
        #ifthecurrentURLisindeedcanonicalornot.
        returncurrent_url==canonical_url

    @tools.ormcache('self.id')
    def_get_cached_values(self):
        self.ensure_one()
        return{
            'user_id':self.user_id.id,
            'company_id':self.company_id.id,
            'default_lang_id':self.default_lang_id.id,
        }

    def_get_cached(self,field):
        returnself._get_cached_values()[field]

    def_get_relative_url(self,url):
        returnurls.url_parse(url).replace(scheme='',netloc='').to_url()


classBaseModel(models.AbstractModel):
    _inherit='base'

    defget_base_url(self):
        """
        Returnsbaseurlaboutonegivenrecord.
        Ifawebsite_idfieldexistsinthecurrentrecordweusetheurl
        fromthiswebsiteasbaseurl.

        :return:thebaseurlforthisrecord
        :rtype:string

        """
        self.ensure_one()
        if'website_id'inselfandself.website_id.domain:
            returnself.website_id._get_http_domain()
        else:
            returnsuper(BaseModel,self).get_base_url()

    defget_website_meta(self):
        #dummyversionof'get_website_meta'above;thisisagracefulfallback
        #formodelsthatdon'tinheritfrom'website.seo.metadata'
        return{}
