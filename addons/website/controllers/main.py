#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64
importdatetime
importjson
importos
importlogging
importpytz
importrequests
importwerkzeug.urls
importwerkzeug.utils
importwerkzeug.wrappers

fromitertoolsimportislice
fromwerkzeugimporturls
fromxml.etreeimportElementTreeasET

importflectra

fromflectraimporthttp,models,fields,_
fromflectra.httpimportrequest
fromflectra.toolsimportOrderedSet
fromflectra.addons.http_routing.models.ir_httpimportslug,slugify,_guess_mimetype
fromflectra.addons.web.controllers.mainimportBinary
fromflectra.addons.portal.controllers.portalimportpagerasportal_pager
fromflectra.addons.portal.controllers.webimportHome

logger=logging.getLogger(__name__)

#Completelyarbitrarylimits
MAX_IMAGE_WIDTH,MAX_IMAGE_HEIGHT=IMAGE_LIMITS=(1024,768)
LOC_PER_SITEMAP=45000
SITEMAP_CACHE_TIME=datetime.timedelta(hours=12)


classQueryURL(object):
    def__init__(self,path='',path_args=None,**args):
        self.path=path
        self.args=args
        self.path_args=OrderedSet(path_argsor[])

    def__call__(self,path=None,path_args=None,**kw):
        path=pathorself.path
        forkey,valueinself.args.items():
            kw.setdefault(key,value)
        path_args=OrderedSet(path_argsor[])|self.path_args
        paths,fragments={},[]
        forkey,valueinkw.items():
            ifvalueandkeyinpath_args:
                ifisinstance(value,models.BaseModel):
                    paths[key]=slug(value)
                else:
                    paths[key]=u"%s"%value
            elifvalue:
                ifisinstance(value,list)orisinstance(value,set):
                    fragments.append(werkzeug.urls.url_encode([(key,item)foriteminvalue]))
                else:
                    fragments.append(werkzeug.urls.url_encode([(key,value)]))
        forkeyinpath_args:
            value=paths.get(key)
            ifvalueisnotNone:
                path+='/'+key+'/'+value
        iffragments:
            path+='?'+'&'.join(fragments)
        returnpath


classWebsite(Home):

    @http.route('/',type='http',auth="public",website=True,sitemap=True)
    defindex(self,**kw):
        #prefetchallmenus(itwillprefetchwebsite.pagetoo)
        top_menu=request.website.menu_id

        homepage=request.website.homepage_id
        ifhomepageand(homepage.sudo().is_visibleorrequest.env.user.has_group('base.group_user'))andhomepage.url!='/':
            returnrequest.env['ir.http'].reroute(homepage.url)

        website_page=request.env['ir.http']._serve_page()
        ifwebsite_page:
            returnwebsite_page
        else:
            first_menu=top_menuandtop_menu.child_idandtop_menu.child_id.filtered(lambdamenu:menu.is_visible)
            iffirst_menuandfirst_menu[0].urlnotin('/','','#')and(not(first_menu[0].url.startswith(('/?','/#','')))):
                returnrequest.redirect(first_menu[0].url)

        raiserequest.not_found()

    @http.route('/website/force/<int:website_id>',type='http',auth="user",website=True,sitemap=False,multilang=False)
    defwebsite_force(self,website_id,path='/',isredir=False,**kw):
        """Toswitchfromawebsitetoanother,weneedtoforcethewebsitein
        session,AFTERlandingonthatwebsitedomain(ifset)asthiswillbea
        differentsession.
        """
        parse=werkzeug.urls.url_parse
        safe_path=parse(path).path

        ifnot(request.env.user.has_group('website.group_multi_website')
           andrequest.env.user.has_group('website.group_website_publisher')):
            #Theusermightnotbeloggedinontheforcedwebsite,sohewon't
            #haverights.Wejustredirecttothepathastheuserisalready
            #onthedomain(basicallyano-opasitwon'tchangedomainor
            #forcewebsite).
            #Website1:127.0.0.1(admin)
            #Website2:127.0.0.2(notloggedin)
            #Clickon"Website2"fromWebsite1
            returnrequest.redirect(safe_path)

        website=request.env['website'].browse(website_id)

        ifnotisredirandwebsite.domain:
            domain_from=request.httprequest.environ.get('HTTP_HOST','')
            domain_to=parse(website._get_http_domain()).netloc
            ifdomain_from!=domain_to:
                #redirecttocorrectdomainforacorrectroutingmap
                url_to=urls.url_join(website._get_http_domain(),'/website/force/%s?isredir=1&path=%s'%(website.id,safe_path))
                returnrequest.redirect(url_to)
        website._force()
        returnrequest.redirect(safe_path)

    #------------------------------------------------------
    #Login-overwriteofthewebloginsothatregularusersareredirectedtothebackend
    #whileportalusersareredirectedtothefrontendbydefault
    #------------------------------------------------------

    def_login_redirect(self,uid,redirect=None):
        """Redirectregularusers(employees)tothebackend)andothersto
        thefrontend
        """
        ifnotredirectandrequest.params.get('login_success'):
            ifrequest.env['res.users'].browse(uid).has_group('base.group_user'):
                redirect='/web?'+request.httprequest.query_string.decode()
            else:
                redirect='/my'
        returnsuper()._login_redirect(uid,redirect=redirect)

    #Forcewebsite=True+auth='public',requiredforloginformlayout
    @http.route(website=True,auth="public",sitemap=False)
    defweb_login(self,*args,**kw):
        returnsuper().web_login(*args,**kw)

    #------------------------------------------------------
    #Business
    #------------------------------------------------------

    @http.route('/website/get_languages',type='json',auth="user",website=True)
    defwebsite_languages(self,**kwargs):
        return[(lg.code,lg.url_code,lg.name)forlginrequest.website.language_ids]

    @http.route('/website/lang/<lang>',type='http',auth="public",website=True,multilang=False)
    defchange_lang(self,lang,r='/',**kwargs):
        """:paramlang:supposedtobevalueof`url_code`field"""
        r=request.website._get_relative_url(r)
        iflang=='default':
            lang=request.website.default_lang_id.url_code
            r='/%s%s'%(lang,ror'/')
        redirect=werkzeug.utils.redirect(ror('/%s'%lang),303)
        lang_code=request.env['res.lang']._lang_get_code(lang)
        redirect.set_cookie('frontend_lang',lang_code)
        returnredirect

    @http.route(['/website/country_infos/<model("res.country"):country>'],type='json',auth="public",methods=['POST'],website=True)
    defcountry_infos(self,country,**kw):
        fields=country.get_address_fields()
        returndict(fields=fields,states=[(st.id,st.name,st.code)forstincountry.state_ids],phone_code=country.phone_code)

    @http.route(['/robots.txt'],type='http',auth="public",website=True,sitemap=False)
    defrobots(self,**kwargs):
        returnrequest.render('website.robots',{'url_root':request.httprequest.url_root},mimetype='text/plain')

    @http.route('/sitemap.xml',type='http',auth="public",website=True,multilang=False,sitemap=False)
    defsitemap_xml_index(self,**kwargs):
        current_website=request.website
        Attachment=request.env['ir.attachment'].sudo()
        View=request.env['ir.ui.view'].sudo()
        mimetype='application/xml;charset=utf-8'
        content=None

        defcreate_sitemap(url,content):
            returnAttachment.create({
                'datas':base64.b64encode(content),
                'mimetype':mimetype,
                'type':'binary',
                'name':url,
                'url':url,
            })
        dom=[('url','=','/sitemap-%d.xml'%current_website.id),('type','=','binary')]
        sitemap=Attachment.search(dom,limit=1)
        ifsitemap:
            #Checkifstoredversionisstillvalid
            create_date=fields.Datetime.from_string(sitemap.create_date)
            delta=datetime.datetime.now()-create_date
            ifdelta<SITEMAP_CACHE_TIME:
                content=base64.b64decode(sitemap.datas)

        ifnotcontent:
            #Removeallsitemapsinir.attachmentsaswe'regoingtoregeneratedthem
            dom=[('type','=','binary'),'|',('url','=like','/sitemap-%d-%%.xml'%current_website.id),
                   ('url','=','/sitemap-%d.xml'%current_website.id)]
            sitemaps=Attachment.search(dom)
            sitemaps.unlink()

            pages=0
            locs=request.website.with_context(_filter_duplicate_pages=True).with_user(request.website.user_id)._enumerate_pages()
            whileTrue:
                values={
                    'locs':islice(locs,0,LOC_PER_SITEMAP),
                    'url_root':request.httprequest.url_root[:-1],
                }
                urls=View._render_template('website.sitemap_locs',values)
                ifurls.strip():
                    content=View._render_template('website.sitemap_xml',{'content':urls})
                    pages+=1
                    last_sitemap=create_sitemap('/sitemap-%d-%d.xml'%(current_website.id,pages),content)
                else:
                    break

            ifnotpages:
                returnrequest.not_found()
            elifpages==1:
                #renamethe-id-page.xml=>-id.xml
                last_sitemap.write({
                    'url':"/sitemap-%d.xml"%current_website.id,
                    'name':"/sitemap-%d.xml"%current_website.id,
                })
            else:
                #TODO:inmaster/saas-15,movecurrent_website_idintemplatedirectly
                pages_with_website=["%d-%d"%(current_website.id,p)forpinrange(1,pages+1)]

                #Sitemapsmustbesplitinseveralsmallerfileswithasitemapindex
                content=View._render_template('website.sitemap_index_xml',{
                    'pages':pages_with_website,
                    'url_root':request.httprequest.url_root,
                })
                create_sitemap('/sitemap-%d.xml'%current_website.id,content)

        returnrequest.make_response(content,[('Content-Type',mimetype)])

    defsitemap_website_info(env,rule,qs):
        website=env['website'].get_current_website()
        ifnot(
            website.viewref('website.website_info',False).active
            andwebsite.viewref('website.show_website_info',False).active
        ):
            #avoid404orblankpageinsitemap
            returnFalse

        ifnotqsorqs.lower()in'/website/info':
            yield{'loc':'/website/info'}

    @http.route('/website/info',type='http',auth="public",website=True,sitemap=sitemap_website_info)
    defwebsite_info(self,**kwargs):
        ifnotrequest.website.viewref('website.website_info',False).active:
            #Deletedorarchivedview(throughmanualoperationinbackend).
            #Don'tcheck`show_website_info`view:stillneedtoaccessif
            #disabledtobeabletoenableitthroughthecustomizeshow.
            raiserequest.not_found()

        Module=request.env['ir.module.module'].sudo()
        apps=Module.search([('state','=','installed'),('application','=',True)])
        l10n=Module.search([('state','=','installed'),('name','=like','l10n_%')])
        values={
            'apps':apps,
            'l10n':l10n,
            'version':flectra.service.common.exp_version()
        }
        returnrequest.render('website.website_info',values)

    @http.route(['/website/social/<string:social>'],type='http',auth="public",website=True,sitemap=False)
    defsocial(self,social,**kwargs):
        url=getattr(request.website,'social_%s'%social,False)
        ifnoturl:
            raisewerkzeug.exceptions.NotFound()
        returnrequest.redirect(url)

    @http.route('/website/get_suggested_links',type='json',auth="user",website=True)
    defget_suggested_link(self,needle,limit=10):
        current_website=request.website

        matching_pages=[]
        forpageincurrent_website.with_context(_filter_duplicate_pages=True).search_pages(needle,limit=int(limit)):
            matching_pages.append({
                'value':page['loc'],
                'label':'name'inpageand'%s(%s)'%(page['loc'],page['name'])orpage['loc'],
            })
        matching_urls=set(map(lambdamatch:match['value'],matching_pages))

        matching_last_modified=[]
        last_modified_pages=current_website.with_context(_filter_duplicate_pages=True)._get_website_pages(order='write_datedesc',limit=5)
        forurl,nameinlast_modified_pages.mapped(lambdap:(p.url,p.name)):
            ifneedle.lower()inname.lower()orneedle.lower()inurl.lower()andurlnotinmatching_urls:
                matching_last_modified.append({
                    'value':url,
                    'label':'%s(%s)'%(url,name),
                })

        suggested_controllers=[]
        forname,url,modincurrent_website.get_suggested_controllers():
            ifneedle.lower()inname.lower()orneedle.lower()inurl.lower():
                module_sudo=modandrequest.env.ref('base.module_%s'%mod,False).sudo()
                icon=modand"<imgsrc='%s'width='24px'height='24px'class='mr-2rounded'/>"%(module_sudoandmodule_sudo.iconormod)or''
                suggested_controllers.append({
                    'value':url,
                    'label':'%s%s(%s)'%(icon,url,name),
                })

        return{
            'matching_pages':sorted(matching_pages,key=lambdao:o['label']),
            'others':[
                dict(title=_('Lastmodifiedpages'),values=matching_last_modified),
                dict(title=_('Appsurl'),values=suggested_controllers),
            ]
        }

    @http.route('/website/snippet/filters',type='json',auth='public',website=True)
    defget_dynamic_filter(self,filter_id,template_key,limit=None,search_domain=None):
        dynamic_filter=request.env['website.snippet.filter'].sudo().search(
            [('id','=',filter_id)]+request.website.website_domain()
        )
        returndynamic_filteranddynamic_filter.render(template_key,limit,search_domain)or''

    @http.route('/website/snippet/options_filters',type='json',auth='user',website=True)
    defget_dynamic_snippet_filters(self):
        dynamic_filter=request.env['website.snippet.filter'].sudo().search_read(
            request.website.website_domain(),['id','name','limit']
        )
        returndynamic_filter

    @http.route('/website/snippet/filter_templates',type='json',auth='public',website=True)
    defget_dynamic_snippet_templates(self,filter_id=False):
        #todo:iffilter_id.model->filtertemplate
        templates=request.env['ir.ui.view'].sudo().search_read(
            [['key','ilike','.dynamic_filter_template_'],['type','=','qweb']],['key','name']
        )
        returntemplates

    #------------------------------------------------------
    #Edit
    #------------------------------------------------------

    @http.route(['/website/pages','/website/pages/page/<int:page>'],type='http',auth="user",website=True)
    defpages_management(self,page=1,sortby='url',search='',**kw):
        #onlywebsite_designershouldaccessthepageManagement
        ifnotrequest.env.user.has_group('website.group_website_designer'):
            raisewerkzeug.exceptions.NotFound()

        Page=request.env['website.page']
        searchbar_sortings={
            'url':{'label':_('SortbyUrl'),'order':'url'},
            'name':{'label':_('SortbyName'),'order':'name'},
        }
        #defaultsortbyorder
        sort_order=searchbar_sortings.get(sortby,'url')['order']+',website_iddesc,id'

        domain=request.website.website_domain()
        ifsearch:
            domain+=['|',('name','ilike',search),('url','ilike',search)]

        pages=Page.search(domain,order=sort_order)
        ifsortby!='url'ornotrequest.env.user.has_group('website.group_multi_website'):
            pages=pages.filtered(pages._is_most_specific_page)
        pages_count=len(pages)

        step=50
        pager=portal_pager(
            url="/website/pages",
            url_args={'sortby':sortby},
            total=pages_count,
            page=page,
            step=step
        )

        pages=pages[(page-1)*step:page*step]

        values={
            'pager':pager,
            'pages':pages,
            'search':search,
            'sortby':sortby,
            'searchbar_sortings':searchbar_sortings,
        }
        returnrequest.render("website.list_website_pages",values)

    @http.route(['/website/add/','/website/add/<path:path>'],type='http',auth="user",website=True,methods=['POST'])
    defpagenew(self,path="",noredirect=False,add_menu=False,template=False,**kwargs):
        #forsupportedmimetype,getcorrectdefaulttemplate
        _,ext=os.path.splitext(path)
        ext_special_case=extandextin_guess_mimetype()andext!='.html'

        ifnottemplateandext_special_case:
            default_templ='website.default_%s'%ext.lstrip('.')
            ifrequest.env.ref(default_templ,False):
                template=default_templ

        template=templateanddict(template=template)or{}
        page=request.env['website'].new_page(path,add_menu=add_menu,**template)
        url=page['url']
        ifnoredirect:
            returnwerkzeug.wrappers.Response(url,mimetype='text/plain')

        ifext_special_case: #redirectnonhtmlpagestobackendtoedit
            returnwerkzeug.utils.redirect('/web#id='+str(page.get('view_id'))+'&view_type=form&model=ir.ui.view')
        returnwerkzeug.utils.redirect(url+"?enable_editor=1")

    @http.route("/website/get_switchable_related_views",type="json",auth="user",website=True)
    defget_switchable_related_views(self,key):
        views=request.env["ir.ui.view"].get_related_views(key,bundles=False).filtered(lambdav:v.customize_show)
        views=views.sorted(key=lambdav:(v.inherit_id.id,v.name))
        returnviews.with_context(display_website=False).read(['name','id','key','xml_id','active','inherit_id'])

    @http.route('/website/toggle_switchable_view',type='json',auth='user',website=True)
    deftoggle_switchable_view(self,view_key):
        ifrequest.website.user_has_groups('website.group_website_designer'):
            request.website.viewref(view_key).toggle_active()
        else:
            returnwerkzeug.exceptions.Forbidden()

    @http.route('/website/reset_template',type='http',auth='user',methods=['POST'],website=True,csrf=False)
    defreset_template(self,view_id,mode='soft',redirect='/',**kwargs):
        """Thismethodwilltrytoresetabrokenview.
        Giventhemode,theviewcaneitherbe:
        -Softreset:restoretopreviousarchiteture.
        -Hardreset:itwillreadtheoriginal`arch`fromtheXMLfileifthe
        viewcomesfromanXMLfile(arch_fs).
        """
        view=request.env['ir.ui.view'].browse(int(view_id))
        #DeactivateCOWtonotfixagenericviewbycreatingaspecific
        view.with_context(website_id=None).reset_arch(mode)
        returnrequest.redirect(redirect)

    @http.route(['/website/publish'],type='json',auth="user",website=True)
    defpublish(self,id,object):
        Model=request.env[object]
        record=Model.browse(int(id))

        values={}
        if'website_published'inModel._fields:
            values['website_published']=notrecord.website_published
            record.write(values)
            returnbool(record.website_published)
        returnFalse

    @http.route(['/website/seo_suggest'],type='json',auth="user",website=True)
    defseo_suggest(self,keywords=None,lang=None):
        language=lang.split("_")
        url="http://google.com/complete/search"
        try:
            req=requests.get(url,params={
                'ie':'utf8','oe':'utf8','output':'toolbar','q':keywords,'hl':language[0],'gl':language[1]})
            req.raise_for_status()
            response=req.content
        exceptIOError:
            return[]
        xmlroot=ET.fromstring(response)
        returnjson.dumps([sugg[0].attrib['data']forsugginxmlrootiflen(sugg)andsugg[0].attrib['data']])

    @http.route(['/website/get_seo_data'],type='json',auth="user",website=True)
    defget_seo_data(self,res_id,res_model):
        ifnotrequest.env.user.has_group('website.group_website_publisher'):
            raisewerkzeug.exceptions.Forbidden()

        fields=['website_meta_title','website_meta_description','website_meta_keywords','website_meta_og_img']
        ifres_model=='website.page':
            fields.extend(['website_indexed','website_id'])

        record=request.env[res_model].browse(res_id)
        res=record._read_format(fields)[0]
        res['has_social_default_image']=request.website.has_social_default_image

        ifres_modelnotin('website.page','ir.ui.view')and'seo_name'inrecord: #allowcustomslugify
            res['seo_name_default']=slugify(record.display_name) #defaultslug,ifseo_namebecomeempty
            res['seo_name']=record.seo_nameandslugify(record.seo_name)or''
        returnres

    @http.route(['/google<string(length=16):key>.html'],type='http',auth="public",website=True,sitemap=False)
    defgoogle_console_search(self,key,**kwargs):
        ifnotrequest.website.google_search_console:
            logger.warning('GoogleSearchConsolenotenable')
            raisewerkzeug.exceptions.NotFound()

        trusted=request.website.google_search_console.lstrip('google').rstrip('.html')
        ifkey!=trusted:
            ifkey.startswith(trusted):
                request.website.sudo().google_search_console="google%s.html"%key
            else:
                logger.warning('GoogleSearchConsole%snotrecognize'%key)
                raisewerkzeug.exceptions.NotFound()

        returnrequest.make_response("google-site-verification:%s"%request.website.google_search_console)

    @http.route('/website/google_maps_api_key',type='json',auth='public',website=True)
    defgoogle_maps_api_key(self):
        returnjson.dumps({
            'google_maps_api_key':request.website.google_maps_api_keyor''
        })

    #------------------------------------------------------
    #Themes
    #------------------------------------------------------

    def_get_customize_views(self,xml_ids):
        View=request.env["ir.ui.view"].with_context(active_test=False)
        ifnotxml_ids:
            returnView
        domain=[("key","in",xml_ids)]+request.website.website_domain()
        returnView.search(domain).filter_duplicate()

    @http.route(['/website/theme_customize_get'],type='json',auth='user',website=True)
    deftheme_customize_get(self,xml_ids):
        views=self._get_customize_views(xml_ids)
        returnviews.filtered('active').mapped('key')

    @http.route(['/website/theme_customize'],type='json',auth='user',website=True)
    deftheme_customize(self,enable=None,disable=None):
        """
        Enablesand/ordisablesviewsaccordingtolistofkeys.

        :paramenable:listofviews'keystoenable
        :paramdisable:listofviews'keystodisable
        """
        self._get_customize_views(disable).filtered('active').write({'active':False})
        self._get_customize_views(enable).filtered(lambdax:notx.active).write({'active':True})

    @http.route(['/website/theme_customize_bundle_reload'],type='json',auth='user',website=True)
    deftheme_customize_bundle_reload(self):
        """
        ReloadsassetbundlesandreturnstheiruniqueURLs.
        """
        context=dict(request.context)
        return{
            'web.assets_common':request.env['ir.qweb']._get_asset_link_urls('web.assets_common',options=context),
            'web.assets_frontend':request.env['ir.qweb']._get_asset_link_urls('web.assets_frontend',options=context),
            'website.assets_editor':request.env['ir.qweb']._get_asset_link_urls('website.assets_editor',options=context),
        }

    @http.route(['/website/make_scss_custo'],type='json',auth='user',website=True)
    defmake_scss_custo(self,url,values):
        """
        Params:
            url(str):
                theURLofthescssfiletocustomize(supposedtobeavariable
                filewhichwillappearintheassets_commonbundle)

            values(dict):
                key,valuemappingtointegrateinthefile'smap(containingthe
                wordhook).Ifakeyisalreadyinthefile'smap,itsvalueis
                overridden.

        Returns:
            boolean
        """
        request.env['web_editor.assets'].make_scss_customization(url,values)
        returnTrue

    #------------------------------------------------------
    #Serveractions
    #------------------------------------------------------

    @http.route([
        '/website/action/<path_or_xml_id_or_id>',
        '/website/action/<path_or_xml_id_or_id>/<path:path>',
    ],type='http',auth="public",website=True)
    defactions_server(self,path_or_xml_id_or_id,**post):
        ServerActions=request.env['ir.actions.server']
        action=action_id=None

        #findtheaction_id:eitheranxml_id,thepath,oranID
        ifisinstance(path_or_xml_id_or_id,str)and'.'inpath_or_xml_id_or_id:
            action=request.env.ref(path_or_xml_id_or_id,raise_if_not_found=False).sudo()
        ifnotaction:
            action=ServerActions.sudo().search(
                [('website_path','=',path_or_xml_id_or_id),('website_published','=',True)],limit=1)
        ifnotaction:
            try:
                action_id=int(path_or_xml_id_or_id)
                action=ServerActions.sudo().browse(action_id).exists()
            exceptValueError:
                pass

        #runit,returnonlyifwegotaResponseobject
        ifaction:
            ifaction.state=='code'andaction.website_published:
                #usemainsessionenvforexecution
                action_res=ServerActions.browse(action.id).run()
                ifisinstance(action_res,werkzeug.wrappers.Response):
                    returnaction_res

        returnrequest.redirect('/')


#------------------------------------------------------
#Retrocompatibilityroutes
#------------------------------------------------------
classWebsiteBinary(http.Controller):

    @http.route([
        '/website/image',
        '/website/image/<xmlid>',
        '/website/image/<xmlid>/<int:width>x<int:height>',
        '/website/image/<xmlid>/<field>',
        '/website/image/<xmlid>/<field>/<int:width>x<int:height>',
        '/website/image/<model>/<id>/<field>',
        '/website/image/<model>/<id>/<field>/<int:width>x<int:height>'
    ],type='http',auth="public",website=False,multilang=False)
    defcontent_image(self,id=None,max_width=0,max_height=0,**kw):
        ifmax_width:
            kw['width']=max_width
        ifmax_height:
            kw['height']=max_height
        ifid:
            id,_,unique=id.partition('_')
            kw['id']=int(id)
            ifunique:
                kw['unique']=unique
        returnBinary().content_image(**kw)

    #ifnoticonprovidedinDOM,browsertriestoaccess/favicon.ico,egwhenopeninganorderpdf
    @http.route(['/favicon.ico'],type='http',auth='public',website=True,multilang=False,sitemap=False)
    deffavicon(self,**kw):
        website=request.website
        response=request.redirect(website.image_url(website,'favicon'),code=301)
        response.headers['Cache-Control']='public,max-age=%s'%http.STATIC_CACHE_LONG
        returnresponse
