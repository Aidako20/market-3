#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging
fromlxmlimportetree
importos
importunittest
importtime

importpytz
importwerkzeug
importwerkzeug.routing
importwerkzeug.utils

fromfunctoolsimportpartial

importflectra
fromflectraimportapi,models
fromflectraimportregistry,SUPERUSER_ID
fromflectra.httpimportrequest
fromflectra.tools.safe_evalimportsafe_eval
fromflectra.osv.expressionimportFALSE_DOMAIN
fromflectra.addons.http_routing.models.ir_httpimportModelConverter,_guess_mimetype
fromflectra.addons.portal.controllers.portalimport_build_url_w_params

logger=logging.getLogger(__name__)


defsitemap_qs2dom(qs,route,field='name'):
    """Convertaquery_string(cancontainsapath)toadomain"""
    dom=[]
    ifqsandqs.lower()notinroute:
        needles=qs.strip('/').split('/')
        #needleswillbealteredandkeeponlyelementwhichoneisnotinroute
        #diff(from=['shop','product'],to=['shop','product','product'])=>to=['product']
        unittest.util.unorderable_list_difference(route.strip('/').split('/'),needles)
        iflen(needles)==1:
            dom=[(field,'ilike',needles[0])]
        else:
            dom=list(FALSE_DOMAIN)
    returndom


defget_request_website():
    """Returnthewebsiteseton`request`ifcalledinafrontendcontext
    (website=Trueonroute).
    Thismethodcantypicallybeusedtocheckifweareinthefrontend.

    Thismethodiseasytomockduringpythonteststosimulatefrontend
    context,ratherthanmockingeverymethodaccessingrequest.website.

    Don'timportdirectlythemethodoritwon'tbemockedduringtests,do:
    ```
    fromflectra.addons.website.modelsimportir_http
    my_var=ir_http.get_request_website()
    ```
    """
    returnrequestandgetattr(request,'website',False)orFalse


classHttp(models.AbstractModel):
    _inherit='ir.http'

    @classmethod
    defrouting_map(cls,key=None):
        key=keyor(requestandrequest.website_routing)
        returnsuper(Http,cls).routing_map(key=key)

    @classmethod
    defclear_caches(cls):
        super(Http,cls)._clear_routing_map()
        returnsuper(Http,cls).clear_caches()

    @classmethod
    def_slug_matching(cls,adapter,endpoint,**kw):
        forarginkw:
            ifisinstance(kw[arg],models.BaseModel):
                kw[arg]=kw[arg].with_context(slug_matching=True)
        qs=request.httprequest.query_string.decode('utf-8')
        try:
            returnadapter.build(endpoint,kw)+(qsand'?%s'%qsor'')
        exceptflectra.exceptions.MissingError:
            raisewerkzeug.exceptions.NotFound()

    @classmethod
    def_match(cls,path_info,key=None):
        key=keyor(requestandrequest.website_routing)
        returnsuper(Http,cls)._match(path_info,key=key)

    @classmethod
    def_generate_routing_rules(cls,modules,converters):
        website_id=request.website_routing
        logger.debug("_generate_routing_rulesforwebsite:%s",website_id)
        domain=[('redirect_type','in',('308','404')),'|',('website_id','=',False),('website_id','=',website_id)]

        rewrites=dict([(x.url_from,x)forxinrequest.env['website.rewrite'].sudo().search(domain)])
        cls._rewrite_len[website_id]=len(rewrites)

        forurl,endpoint,routinginsuper(Http,cls)._generate_routing_rules(modules,converters):
            routing=dict(routing)
            ifurlinrewrites:
                rewrite=rewrites[url]
                url_to=rewrite.url_to
                ifrewrite.redirect_type=='308':
                    logger.debug('Addrule%sfor%s'%(url_to,website_id))
                    yieldurl_to,endpoint,routing #yieldnewurl

                    ifurl!=url_to:
                        logger.debug('Redirectfrom%sto%sforwebsite%s'%(url,url_to,website_id))
                        _slug_matching=partial(cls._slug_matching,endpoint=endpoint)
                        routing['redirect_to']=_slug_matching
                        yieldurl,endpoint,routing #yieldoriginalredirectedtonewurl
                elifrewrite.redirect_type=='404':
                    logger.debug('Return404for%sforwebsite%s'%(url,website_id))
                    continue
            else:
                yieldurl,endpoint,routing

    @classmethod
    def_get_converters(cls):
        """Gettheconverterslistforcustomurlpatternwerkzeugneedto
            matchRule.Thisoverrideaddsthewebsiteones.
        """
        returndict(
            super(Http,cls)._get_converters(),
            model=ModelConverter,
        )

    @classmethod
    def_auth_method_public(cls):
        """Ifnouserlogged,setthepublicuserofcurrentwebsite,ordefault
            publicuserasrequestuid.
            Afterthismethod`request.env`canbecalled,sincethe`request.uid`is
            set.The`env`lazypropertyof`request`willbecorrect.
        """
        ifnotrequest.session.uid:
            env=api.Environment(request.cr,SUPERUSER_ID,request.context)
            website=env['website'].get_current_website()
            request.uid=websiteandwebsite._get_cached('user_id')

        ifnotrequest.uid:
            super(Http,cls)._auth_method_public()

    @classmethod
    def_register_website_track(cls,response):
        ifgetattr(response,'status_code',0)!=200:
            returnFalse

        template=False
        ifhasattr(response,'qcontext'): #classicresponse
            main_object=response.qcontext.get('main_object')
            website_page=getattr(main_object,'_name',False)=='website.page'andmain_object
            template=response.qcontext.get('response_template')
        elifhasattr(response,'_cached_page'):
            website_page,template=response._cached_page,response._cached_template

        view=templateandrequest.env['website'].get_template(template)
        ifviewandview.track:
            request.env['website.visitor']._handle_webpage_dispatch(response,website_page)

        returnFalse

    @classmethod
    def_dispatch(cls):
        """
        Incaseofreroutingfortranslate(e.g.whenvisitingflectrahq.com/fr_BE/),
        _dispatchcallsreroute()thatreturns_dispatchwithalteredrequestproperties.
        Thesecond_dispatchwillcontinueuntilendofprocess.Whensecond_dispatchisfinished,thefirst_dispatch
        callreceivethenewalteredrequestandcontinue.
        Attheend,2callsof_dispatch(andthisoverride)aremadewithexactsamerequestproperties,insteadofone.
        Astheresponsehasnotbeensentbacktotheclient,thevisitorcookiedoesnotexistyetwhensecond_dispatchcall
        istreatedin_handle_webpage_dispatch,leadingtocreate2visitorswithexactsameproperties.
        Toavoidthis,wecheckif,!!!beforecallingsuper!!!,weareinareroutingrequest.Ifnot,itmeansthatweare
        handlingtheoriginalrequest,inwhichweshouldcreatethevisitor.Weignoreeveryotherreroutingrequests.
        """
        is_rerouting=hasattr(request,'routing_iteration')

        ifrequest.session.db:
            reg=registry(request.session.db)
            withreg.cursor()ascr:
                env=api.Environment(cr,SUPERUSER_ID,{})
                request.website_routing=env['website'].get_current_website().id

        response=super(Http,cls)._dispatch()

        ifnotis_rerouting:
            cls._register_website_track(response)
        returnresponse

    @classmethod
    def_add_dispatch_parameters(cls,func):

        #DEPRECATEDfor/website/force/<website_id>-removemeinmaster~saas-14.4
        #Forcewebsitewithquerystringparamater,typicallysetfromwebsiteselectorinfrontendnavbarandinsidetests
        force_website_id=request.httprequest.args.get('fw')
        if(force_website_idandrequest.session.get('force_website_id')!=force_website_id
                andrequest.env.user.has_group('website.group_multi_website')
                andrequest.env.user.has_group('website.group_website_publisher')):
            request.env['website']._force_website(request.httprequest.args.get('fw'))

        context={}
        ifnotrequest.context.get('tz'):
            context['tz']=request.session.get('geoip',{}).get('time_zone')
            try:
                pytz.timezone(context['tz']or'')
            exceptpytz.UnknownTimeZoneError:
                context.pop('tz')

        request.website=request.env['website'].get_current_website() #canuse`request.env`sinceauthmethodsarecalled
        context['website_id']=request.website.id
        #Thisismainlytoavoidaccesserrorsinwebsitecontrollerswherethereisno
        #context(eg:/shop),andit'snotgoingtopropagatetotheglobalcontextofthetab
        #Ifthecompanyofthewebsiteisnotintheallowedcompaniesoftheuser,setthemain
        #companyoftheuser.
        website_company_id=request.website._get_cached('company_id')
        ifwebsite_company_idinrequest.env.user.company_ids.ids:
            context['allowed_company_ids']=[website_company_id]
        else:
            context['allowed_company_ids']=request.env.user.company_id.ids

        #modifyboundcontext
        request.context=dict(request.context,**context)

        super(Http,cls)._add_dispatch_parameters(func)

        ifrequest.routing_iteration==1:
            request.website=request.website.with_context(request.context)

    @classmethod
    def_get_frontend_langs(cls):
        ifget_request_website():
            return[codeforcode,*_inrequest.env['res.lang'].get_available()]
        else:
            returnsuper()._get_frontend_langs()

    @classmethod
    def_get_default_lang(cls):
        ifgetattr(request,'website',False):
            returnrequest.env['res.lang'].browse(request.website._get_cached('default_lang_id'))
        returnsuper(Http,cls)._get_default_lang()

    @classmethod
    def_get_translation_frontend_modules_name(cls):
        mods=super(Http,cls)._get_translation_frontend_modules_name()
        installed=request.registry._init_modules|set(flectra.conf.server_wide_modules)
        returnmods+[modformodininstalledifmod.startswith('website')]

    @classmethod
    def_serve_page(cls):
        req_page=request.httprequest.path

        def_search_page(comparator='='):
            page_domain=[('url',comparator,req_page)]+request.website.website_domain()
            returnrequest.env['website.page'].sudo().search(page_domain,order='website_idasc',limit=1)

        #specificpagefirst
        page=_search_page()

        #caseinsensitivesearch
        ifnotpage:
            page=_search_page('=ilike')
            ifpage:
                logger.info("Page%rnotfound,redirectingtoexistingpage%r",req_page,page.url)
                returnrequest.redirect(page.url)

        #redirectwithouttrailing/
        ifnotpageandreq_page!="/"andreq_page.endswith("/"):
            returnrequest.redirect(req_page[:-1])

        ifpage:
            #prefetchallmenus(itwillprefetchwebsite.pagetoo)
            request.website.menu_id

        ifpageand(request.website.is_publisher()orpage.is_visible):
            need_to_cache=False
            cache_key=page._get_cache_key(request)
            if(
                page.cache_time #cache>0
                andrequest.httprequest.method=="GET"
                andrequest.env.user._is_public()   #onlycacheforunloggeduser
                and'nocache'notinrequest.params #allowbypasscache/debug
                andnotrequest.session.debug
                andlen(cache_key)andcache_key[-1]isnotNone #nocacheviaexpr
            ):
                need_to_cache=True
                try:
                    r=page._get_cache_response(cache_key)
                    ifr['time']+page.cache_time>time.time():
                        response=werkzeug.Response(r['content'],mimetype=r['contenttype'])
                        response._cached_template=r['template']
                        response._cached_page=page
                        returnresponse
                exceptKeyError:
                    pass

            _,ext=os.path.splitext(req_page)
            response=request.render(page.view_id.id,{
                'deletable':True,
                'main_object':page,
            },mimetype=_guess_mimetype(ext))

            ifneed_to_cacheandresponse.status_code==200:
                r=response.render()
                page._set_cache_response(cache_key,{
                    'content':r,
                    'contenttype':response.headers['Content-Type'],
                    'time':time.time(),
                    'template':getattr(response,'qcontext',{}).get('response_template')
                })
            returnresponse
        returnFalse

    @classmethod
    def_serve_redirect(cls):
        req_page=request.httprequest.path
        domain=[
            ('redirect_type','in',('301','302')),
            #trailing/couldhavebeenremovedbyserver_page
            '|',('url_from','=',req_page.rstrip('/')),('url_from','=',req_page+'/')
        ]
        domain+=request.website.website_domain()
        returnrequest.env['website.rewrite'].sudo().search(domain,limit=1)

    @classmethod
    def_serve_fallback(cls,exception):
        #serveattachmentbefore
        parent=super(Http,cls)._serve_fallback(exception)
        ifparent: #attachment
            returnparent
        ifnotrequest.is_frontend:
            returnFalse
        website_page=cls._serve_page()
        ifwebsite_page:
            returnwebsite_page

        redirect=cls._serve_redirect()
        ifredirect:
            returnrequest.redirect(_build_url_w_params(redirect.url_to,request.params),code=redirect.redirect_type)

        returnFalse

    @classmethod
    def_get_exception_code_values(cls,exception):
        code,values=super(Http,cls)._get_exception_code_values(exception)
        ifisinstance(exception,werkzeug.exceptions.NotFound)andrequest.website.is_publisher():
            code='page_404'
            values['path']=request.httprequest.path[1:]
        ifisinstance(exception,werkzeug.exceptions.Forbidden)and\
           exception.description=="website_visibility_password_required":
            code='protected_403'
            values['path']=request.httprequest.path
        return(code,values)

    @classmethod
    def_get_values_500_error(cls,env,values,exception):
        View=env["ir.ui.view"]
        values=super(Http,cls)._get_values_500_error(env,values,exception)
        if'qweb_exception'invalues:
            try:
                #exception.namemightbeint,string
                exception_template=int(exception.name)
            exceptValueError:
                exception_template=exception.name
            view=View._view_obj(exception_template)
            ifexception.htmlandexception.htmlinview.arch:
                values['view']=view
            else:
                #Theremightbe2caseswheretheexceptioncodecan'tbefound
                #intheview,eithertheerrorisinachildvieworthecode
                #containsbranding(<divt-att-data="request.browse('ok')"/>).
                et=etree.fromstring(view.with_context(inherit_branding=False).read_combined(['arch'])['arch'])
                node=et.xpath(exception.path)
                line=nodeisnotNoneandetree.tostring(node[0],encoding='unicode')
                ifline:
                    values['view']=View._views_get(exception_template).filtered(
                        lambdav:lineinv.arch
                    )
                    values['view']=values['view']andvalues['view'][0]
        #Neededtoshowresettemplateontranslatedpages(`_prepare_qcontext`willsetitformainlang)
        values['editable']=request.uidandrequest.website.is_publisher()
        returnvalues

    @classmethod
    def_get_error_html(cls,env,code,values):
        ifcodein('page_404','protected_403'):
            returncode.split('_')[1],env['ir.ui.view']._render_template('website.%s'%code,values)
        returnsuper(Http,cls)._get_error_html(env,code,values)

    defbinary_content(self,xmlid=None,model='ir.attachment',id=None,field='datas',
                       unique=False,filename=None,filename_field='name',download=False,
                       mimetype=None,default_mimetype='application/octet-stream',
                       access_token=None):
        obj=None
        ifxmlid:
            obj=self._xmlid_to_obj(self.env,xmlid)
        elifidandmodelinself.env:
            obj=self.env[model].browse(int(id))
        ifobjand'website_published'inobj._fields:
            ifself.env[obj._name].sudo().search([('id','=',obj.id),('website_published','=',True)]):
                self=self.sudo()
        returnsuper(Http,self).binary_content(
            xmlid=xmlid,model=model,id=id,field=field,unique=unique,filename=filename,
            filename_field=filename_field,download=download,mimetype=mimetype,
            default_mimetype=default_mimetype,access_token=access_token)

    @classmethod
    def_xmlid_to_obj(cls,env,xmlid):
        website_id=env['website'].get_current_website()
        ifwebsite_idandwebsite_id.theme_id:
            domain=[('key','=',xmlid),('website_id','=',website_id.id)]
            Attachment=env['ir.attachment']
            ifrequest.env.user.share:
                domain.append(('public','=',True))
                Attachment=Attachment.sudo()
            obj=Attachment.search(domain)
            ifobj:
                returnobj[0]

        returnsuper(Http,cls)._xmlid_to_obj(env,xmlid)

    @api.model
    defget_frontend_session_info(self):
        session_info=super(Http,self).get_frontend_session_info()
        session_info.update({
            'is_website_user':request.env.user.id==request.website.user_id.id,
            'lang_url_code':request.lang._get_cached('url_code'),
        })
        ifrequest.env.user.has_group('website.group_website_publisher'):
            session_info.update({
                'website_id':request.website.id,
                'website_company_id':request.website._get_cached('company_id'),
            })
        returnsession_info


classModelConverter(ModelConverter):

    defto_url(self,value):
        ifvalue.env.context.get('slug_matching'):
            returnvalue.env.context.get('_converter_value',str(value.id))
        returnsuper().to_url(value)

    defgenerate(self,uid,dom=None,args=None):
        Model=request.env[self.model].with_user(uid)
        #Allowtocurrent_website_iddirectlyinroutedomain
        args.update(current_website_id=request.env['website'].get_current_website().id)
        domain=safe_eval(self.domain,(argsor{}).copy())
        ifdom:
            domain+=dom
        forrecordinModel.search(domain):
            #returnrecordsoURLwillbetherealendpointURLastherecordwillgothrough`slug()`
            #thesamewayasendpointURLisretrievedduringdispatch(301redirect),see`to_url()`fromModelConverter
            yieldrecord
