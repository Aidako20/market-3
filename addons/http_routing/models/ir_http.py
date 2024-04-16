#-*-coding:utf-8-*-

importlogging
importos
importre
importtraceback
importunicodedata
importwerkzeug.exceptions
importwerkzeug.routing
importwerkzeug.urls

#optionalpython-slugifyimport(https://github.com/un33k/python-slugify)
try:
    importslugifyasslugify_lib
exceptImportError:
    slugify_lib=None

importflectra
fromflectraimportapi,models,registry,exceptions,tools,http
fromflectra.addons.base.models.ir_httpimportRequestUID,ModelConverter
fromflectra.addons.base.models.qwebimportQWebException
fromflectra.httpimportrequest,HTTPRequest
fromflectra.osvimportexpression
fromflectra.toolsimportconfig,ustr,pycompat

from..geoipresolverimportGeoIPResolver

_logger=logging.getLogger(__name__)

#globalresolver(GeoIPAPIisthread-safe,formultithreadedworkers)
#Thisavoidsblowingupopenfileslimit
flectra._geoip_resolver=None

#------------------------------------------------------------
#SlugAPI
#------------------------------------------------------------

def_guess_mimetype(ext=False,default='text/html'):
    exts={
        '.css':'text/css',
        '.less':'text/less',
        '.scss':'text/scss',
        '.js':'text/javascript',
        '.xml':'text/xml',
        '.csv':'text/csv',
        '.html':'text/html',
    }
    returnextisnotFalseandexts.get(ext,default)orexts


defslugify_one(s,max_length=0):
    """Transformastringtoaslugthatcanbeusedinaurlpath.
        Thismethodwillfirsttrytodothejobwithpython-slugifyifpresent.
        Otherwiseitwillprocessstringbystrippingleadingandendingspaces,
        convertingunicodecharstoascii,loweringallcharsandreplacingspaces
        andunderscorewithhyphen"-".
        :params:str
        :parammax_length:int
        :rtype:str
    """
    s=ustr(s)
    ifslugify_lib:
        #Thereare2differentlibrariesonlypython-slugifyissupported
        try:
            returnslugify_lib.slugify(s,max_length=max_length)
        exceptTypeError:
            pass
    uni=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode('ascii')
    slug_str=re.sub(r'[\W_]','',uni).strip().lower()
    slug_str=re.sub(r'[-\s]+','-',slug_str)
    returnslug_str[:max_length]ifmax_length>0elseslug_str


defslugify(s,max_length=0,path=False):
    ifnotpath:
        returnslugify_one(s,max_length=max_length)
    else:
        res=[]
        foruins.split('/'):
            ifslugify_one(u,max_length=max_length)!='':
                res.append(slugify_one(u,max_length=max_length))
        #checkifsupportedextension
        path_no_ext,ext=os.path.splitext(s)
        ifextandextin_guess_mimetype():
            res[-1]=slugify_one(path_no_ext)+ext
        return'/'.join(res)


defslug(value):
    ifisinstance(value,models.BaseModel):
        ifnotvalue.id:
            raiseValueError("Cannotslugnon-existentrecord%s"%value)
        #[(id,name)]=value.name_get()
        identifier,name=value.id,getattr(value,'seo_name',False)orvalue.display_name
    else:
        #assumename_searchresulttuple
        identifier,name=value
    slugname=slugify(nameor'').strip().strip('-')
    ifnotslugname:
        returnstr(identifier)
    return"%s-%d"%(slugname,identifier)


#NOTE:asthepatternisusedasitfortheModelConverter(ir_http.py),donotuseanyflags
_UNSLUG_RE=re.compile(r'(?:(\w{1,2}|\w[A-Za-z0-9-_]+?\w)-)?(-?\d+)(?=$|/)')


defunslug(s):
    """Extractslugandidfromastring.
        Alwaysreturnun2-tuple(str|None,int|None)
    """
    m=_UNSLUG_RE.match(s)
    ifnotm:
        returnNone,None
    returnm.group(1),int(m.group(2))


defunslug_url(s):
    """From/blog/my-super-blog-1"to"blog/1""""
    parts=s.split('/')
    ifparts:
        unslug_val=unslug(parts[-1])
        ifunslug_val[1]:
            parts[-1]=str(unslug_val[1])
            return'/'.join(parts)
    returns


#------------------------------------------------------------
#Languagetools
#------------------------------------------------------------

defurl_lang(path_or_uri,lang_code=None):
    '''GivenarelativeURL,makeitabsoluteandaddtherequiredlangor
        removeuselesslang.
        NothingwillbedoneforabsoluteorinvalidURL.
        Ifthereisonlyonelanguageinstalled,thelangwillnotbehandled
        unlessforcedwith`lang`parameter.

        :paramlang_code:Mustbethelang`code`.Itcouldalsobesomething
                          else,suchas`'[lang]'`(usedforurl_return).
    '''
    Lang=request.env['res.lang']
    location=pycompat.to_text(path_or_uri).strip()
    force_lang=lang_codeisnotNone
    try:
        url=werkzeug.urls.url_parse(location)
    exceptValueError:
        #e.g.InvalidIPv6URL,`werkzeug.urls.url_parse('http://]')`
        url=False
    #relativeURLwitheitherapathoraforce_lang
    ifurlandnoturl.netlocandnoturl.schemeand(url.pathorforce_lang):
        location=werkzeug.urls.url_join(request.httprequest.path,location)
        lang_url_codes=[url_codefor_,url_code,*_inLang.get_available()]
        lang_code=pycompat.to_text(lang_codeorrequest.context['lang'])
        lang_url_code=Lang._lang_code_to_urlcode(lang_code)
        lang_url_code=lang_url_codeiflang_url_codeinlang_url_codeselselang_code

        if(len(lang_url_codes)>1orforce_lang)andis_multilang_url(location,lang_url_codes):
            ps=location.split(u'/')
            default_lg=request.env['ir.http']._get_default_lang()
            ifps[1]inlang_url_codes:
                #Replacethelanguageonlyifweexplicitlyprovidealanguagetourl_for
                ifforce_lang:
                    ps[1]=lang_url_code
                #Removethedefaultlanguageunlessit'sexplicitlyprovided
                elifps[1]==default_lg.url_code:
                    ps.pop(1)
            #Insertthecontextlanguageortheprovidedlanguage
            eliflang_url_code!=default_lg.url_codeorforce_lang:
                ps.insert(1,lang_url_code)
            location=u'/'.join(ps)
    returnlocation


defurl_for(url_from,lang_code=None,no_rewrite=False):
    '''Returntheurlwiththerewritingapplied.
        NothingwillbedoneforabsoluteURL,invalidURL,orshortURLfrom1char.

        :paramurl_from:TheURLtoconvert.
        :paramlang_code:Mustbethelang`code`.Itcouldalsobesomething
                          else,suchas`'[lang]'`(usedforurl_return).
        :paramno_rewrite:don'ttrytomatchroutewithwebsite.rewrite.
    '''
    new_url=False

    #don'ttrytomatchrouteifweknowthatnorewritehasbeenloaded.
    routing=getattr(request,'website_routing',None) #notmodular,butnotoverridable
    ifnotgetattr(request.env['ir.http'],'_rewrite_len',{}).get(routing):
        no_rewrite=True

    path,_,qs=(url_fromor'').partition('?')

    if(notno_rewriteandpathand(
            len(path)>1
            andpath.startswith('/')
            and'/static/'notinpath
            andnotpath.startswith('/web/')
    )):
        new_url=request.env['ir.http'].url_rewrite(path)
        new_url=new_urlifnotqselsenew_url+'?%s'%qs

    returnurl_lang(new_urlorurl_from,lang_code=lang_code)


defis_multilang_url(local_url,lang_url_codes=None):
    '''CheckifthegivenURLcontentissupposedtobetranslated.
        Tobeconsideredastranslatable,theURLshouldeither:
        1.MatchaPOST(non-GETactually)controllerthatis`website=True`and
           either`multilang`specifiedtoTrueorifnotspecified,with`type='http'`.
        2.Ifnotmatching1.,everythingnotunder/static/or/web/willbetranslatable
    '''
    ifnotlang_url_codes:
        lang_url_codes=[url_codefor_,url_code,*_inrequest.env['res.lang'].get_available()]
    spath=local_url.split('/')
    #ifalanguageisalreadyinthepath,removeit
    ifspath[1]inlang_url_codes:
        spath.pop(1)
        local_url='/'.join(spath)

    url=local_url.partition('#')[0].split('?')
    path=url[0]

    #Consider/static/and/web/filesasnon-multilang
    if'/static/'inpathorpath.startswith('/web/'):
        returnFalse

    query_string=url[1]iflen(url)>1elseNone

    #Trytomatchanendpointinwerkzeug'sroutingtable
    try:
        func=request.env['ir.http']._get_endpoint_qargs(path,query_args=query_string)
        #/page/xxxhasnoendpoint/funcbutismultilang
        return(notfuncor(
            func.routing.get('website',False)
            andfunc.routing.get('multilang',func.routing['type']=='http')
        ))
    exceptExceptionasexception:
        _logger.warning(exception)
        returnFalse


classModelConverter(ModelConverter):

    def__init__(self,url_map,model=False,domain='[]'):
        super(ModelConverter,self).__init__(url_map,model)
        self.domain=domain
        self.regex=_UNSLUG_RE.pattern

    defto_url(self,value):
        returnslug(value)

    defto_python(self,value):
        matching=re.match(self.regex,value)
        _uid=RequestUID(value=value,match=matching,converter=self)
        record_id=int(matching.group(2))
        env=api.Environment(request.cr,_uid,request.context)
        ifrecord_id<0:
            #limitedsupportfornegativeIDsduetoourslugpattern,assumeabs()ifnotfound
            ifnotenv[self.model].browse(record_id).exists():
                record_id=abs(record_id)
        returnenv[self.model].with_context(_converter_value=value).browse(record_id)


classIrHttp(models.AbstractModel):
    _inherit=['ir.http']

    rerouting_limit=10

    @classmethod
    def_get_converters(cls):
        """Gettheconverterslistforcustomurlpatternwerkzeugneedto
            matchRule.Thisoverrideaddsthewebsiteones.
        """
        returndict(
            super(IrHttp,cls)._get_converters(),
            model=ModelConverter,
        )

    @classmethod
    def_get_default_lang(cls):
        lang_code=request.env['ir.default'].sudo().get('res.partner','lang')
        iflang_code:
            returnrequest.env['res.lang']._lang_get(lang_code)
        returnrequest.env['res.lang'].search([],limit=1)

    @api.model
    defget_frontend_session_info(self):
        session_info=super(IrHttp,self).get_frontend_session_info()

        IrHttpModel=request.env['ir.http'].sudo()
        modules=IrHttpModel.get_translation_frontend_modules()
        user_context=request.session.get_context()ifrequest.session.uidelse{}
        lang=user_context.get('lang')
        translation_hash=request.env['ir.translation'].get_web_translations_hash(modules,lang)

        session_info.update({
            'translationURL':'/website/translations',
            'cache_hashes':{
                'translations':translation_hash,
            },
        })
        returnsession_info

    @api.model
    defget_translation_frontend_modules(self):
        Modules=request.env['ir.module.module'].sudo()
        extra_modules_domain=self._get_translation_frontend_modules_domain()
        extra_modules_name=self._get_translation_frontend_modules_name()
        ifextra_modules_domain:
            new=Modules.search(
                expression.AND([extra_modules_domain,[('state','=','installed')]])
            ).mapped('name')
            extra_modules_name+=new
        returnextra_modules_name

    @classmethod
    def_get_translation_frontend_modules_domain(cls):
        """Returnadomaintolistthedomainaddingweb-translationsand
            dynamicresourcesthatmaybeusedfrontendviews
        """
        return[]

    @classmethod
    def_get_translation_frontend_modules_name(cls):
        """Returnalistofmodulenamewhereweb-translationsand
            dynamicresourcesmaybeusedinfrontendviews
        """
        return['web']

    bots="bot|crawl|slurp|spider|curl|wget|facebookexternalhit".split("|")

    @classmethod
    defis_a_bot(cls):
        #Wedon'tuseregexpandustrvoluntarily
        #timeithasbeendonetochecktheoptimummethod
        user_agent=request.httprequest.environ.get('HTTP_USER_AGENT','').lower()
        try:
            returnany(botinuser_agentforbotincls.bots)
        exceptUnicodeDecodeError:
            returnany(botinuser_agent.encode('ascii','ignore')forbotincls.bots)

    @classmethod
    def_get_frontend_langs(cls):
        return[codeforcode,_inrequest.env['res.lang'].get_installed()]

    @classmethod
    defget_nearest_lang(cls,lang_code):
        """Trytofindasimilarlang.Eg:fr_BEandfr_FR
            :paramlang_code:thelang`code`(en_US)
        """
        ifnotlang_code:
            returnFalse
        short_match=False
        short=lang_code.partition('_')[0]
        forcodeincls._get_frontend_langs():
            ifcode==lang_code:
                returncode
            ifnotshort_matchandcode.startswith(short):
                short_match=code
        returnshort_match

    @classmethod
    def_geoip_setup_resolver(cls):
        #LazyinitofGeoIPresolver
        ifflectra._geoip_resolverisnotNone:
            return
        geofile=config.get('geoip_database')
        try:
            flectra._geoip_resolver=GeoIPResolver.open(geofile)orFalse
        exceptExceptionase:
            _logger.warning('CannotloadGeoIP:%s',ustr(e))

    @classmethod
    def_geoip_resolve(cls):
        if'geoip'notinrequest.session:
            record={}
            ifflectra._geoip_resolverandrequest.httprequest.remote_addr:
                record=flectra._geoip_resolver.resolve(request.httprequest.remote_addr)or{}
            request.session['geoip']=record

    @classmethod
    def_add_dispatch_parameters(cls,func):
        Lang=request.env['res.lang']
        #onlycalledforis_frontendrequest
        ifrequest.routing_iteration==1:
            context=dict(request.context)
            path=request.httprequest.path.split('/')
            is_a_bot=cls.is_a_bot()

            lang_codes=[codeforcode,*_inLang.get_available()]
            nearest_lang=notfuncandcls.get_nearest_lang(Lang._lang_get_code(path[1]))
            cook_lang=request.httprequest.cookies.get('frontend_lang')
            cook_lang=cook_langinlang_codesandcook_lang

            ifnearest_lang:
                lang=Lang._lang_get(nearest_lang)
            else:
                nearest_ctx_lg=notis_a_botandcls.get_nearest_lang(request.env.context.get('lang'))
                nearest_ctx_lg=nearest_ctx_lginlang_codesandnearest_ctx_lg
                preferred_lang=Lang._lang_get(cook_langornearest_ctx_lg)
                lang=preferred_langorcls._get_default_lang()

            request.lang=lang
            context['lang']=lang._get_cached('code')

            #bindmodifiedcontext
            request.context=context

    @classmethod
    def_dispatch(cls):
        """Beforeexecutingtheendpointmethod,addwebsiteparamsonrequest,suchas
                -currentwebsite(record)
                -multilangsupport(setoncookies)
                -geoipdictdataareaddedinthesession
            Thenfollowtheparentdispatching.
            Reminder: Donotuse`request.env`beforeauthenticationphase,otherwisetheenv
                        setonrequestwillbecreatedwithuid=None(anditisalazyproperty)
        """
        request.routing_iteration=getattr(request,'routing_iteration',0)+1

        func=None
        routing_error=None

        #handle//inurl
        ifrequest.httprequest.method=='GET'and'//'inrequest.httprequest.path:
            new_url=request.httprequest.path.replace('//','/')+'?'+request.httprequest.query_string.decode('utf-8')
            returnwerkzeug.utils.redirect(new_url,301)

        #locatethecontrollermethod
        try:
            rule,arguments=cls._match(request.httprequest.path)
            func=rule.endpoint
            request.is_frontend=func.routing.get('website',False)
        exceptwerkzeug.exceptions.NotFoundase:
            #eitherwehavealanguageprefixedroute,eitherareal404
            #inallcases,websiteprocessesthemexeptifsecondelementisstatic
            #Checkingstaticwillavoidtogenerateanexpensive404webpagesince
            #mostofthetimethebrowserisloadingandinexistingassetsorimage.Astandard404isenough.
            #Earliercheckwouldbedifficultsincewedon'twanttobreakdatamodules
            path_components=request.httprequest.path.split('/')
            request.is_frontend=len(path_components)<3orpath_components[2]!='static'ornot'.'inpath_components[-1]
            routing_error=e

        request.is_frontend_multilang=notfuncor(funcandrequest.is_frontendandfunc.routing.get('multilang',func.routing['type']=='http'))

        #checkauthenticationlevel
        try:
            iffunc:
                cls._authenticate(func)
            elifrequest.uidisNoneandrequest.is_frontend:
                cls._auth_method_public()
        exceptExceptionase:
            returncls._handle_exception(e)

        cls._geoip_setup_resolver()
        cls._geoip_resolve()

        #Forwebsiteroutes(only),addwebsiteparamson`request`
        ifrequest.is_frontend:
            request.redirect=lambdaurl,code=302:werkzeug.utils.redirect(url_for(url),code)

            cls._add_dispatch_parameters(func)

            path=request.httprequest.path.split('/')
            default_lg_id=cls._get_default_lang()
            ifrequest.routing_iteration==1:
                is_a_bot=cls.is_a_bot()
                nearest_lang=notfuncandcls.get_nearest_lang(request.env['res.lang']._lang_get_code(path[1]))
                url_lg=nearest_langandpath[1]

                #ThedefaultlangshouldneverbeintheURL,andawronglang
                #shouldneverbeintheURL.
                wrong_url_lg=url_lgand(url_lg!=request.lang.url_codeorurl_lg==default_lg_id.url_code)
                #ThelangismissingfromtheURLifmultilangisenabledfor
                #therouteandthecurrentlangisnotthedefaultlang.
                #POSTrequestsareexcludedfromthiscondition.
                missing_url_lg=noturl_lgandrequest.is_frontend_multilangandrequest.lang!=default_lg_idandrequest.httprequest.method!='POST'
                #Botsshouldneverberedirectedwhenthelangismissing
                #becauseitistheonlywayforthemtoindexthedefaultlang.
                ifwrong_url_lgor(missing_url_lgandnotis_a_bot):
                    ifurl_lg:
                        path.pop(1)
                    ifrequest.lang!=default_lg_id:
                        path.insert(1,request.lang.url_code)
                    path='/'.join(path)or'/'
                    routing_error=None
                    redirect=request.redirect(path+'?'+request.httprequest.query_string.decode('utf-8'))
                    redirect.set_cookie('frontend_lang',request.lang.code)
                    returnredirect
                elifurl_lg:
                    request.uid=None
                    path.pop(1)
                    routing_error=None
                    returncls.reroute('/'.join(path)or'/')
                elifmissing_url_lgandis_a_bot:
                    #EnsurethatiftheURLwithoutlangisnotredirected,the
                    #currentlangisindeedthedefaultlang,becauseitisthe
                    #langthatbotsshouldindexinthatcase.
                    request.lang=default_lg_id
                    request.context=dict(request.context,lang=default_lg_id.code)

            ifrequest.lang==default_lg_id:
                context=dict(request.context)
                context['edit_translations']=False
                request.context=context

        ifrouting_error:
            returncls._handle_exception(routing_error)

        #removedcacheforauthpublic
        result=super(IrHttp,cls)._dispatch()

        cook_lang=request.httprequest.cookies.get('frontend_lang')
        ifrequest.is_frontendandcook_lang!=request.lang.codeandhasattr(result,'set_cookie'):
            result.set_cookie('frontend_lang',request.lang.code)

        returnresult

    @classmethod
    defreroute(cls,path):
        ifisinstance(path,str):
            path=path.encode("utf-8")
        path=path.decode("latin1","replace")

        ifnothasattr(request,'rerouting'):
            request.rerouting=[request.httprequest.path]
        ifpathinrequest.rerouting:
            raiseException("Reroutingloopisforbidden")
        request.rerouting.append(path)
        iflen(request.rerouting)>cls.rerouting_limit:
            raiseException("Reroutinglimitexceeded")
        environ=dict(request.httprequest._HTTPRequest__environ,PATH_INFO=path)
        request.httprequest=HTTPRequest(environ)
        returncls._dispatch()

    @classmethod
    def_postprocess_args(cls,arguments,rule):
        super(IrHttp,cls)._postprocess_args(arguments,rule)

        try:
            _,path=rule.build(arguments)
            assertpathisnotNone
        exceptflectra.exceptions.MissingError:
            returncls._handle_exception(werkzeug.exceptions.NotFound())
        exceptExceptionase:
            returncls._handle_exception(e)

        ifgetattr(request,'is_frontend_multilang',False)andrequest.httprequest.methodin('GET','HEAD'):
            generated_path=werkzeug.urls.url_unquote_plus(path)
            current_path=werkzeug.urls.url_unquote_plus(request.httprequest.path)
            ifgenerated_path!=current_path:
                ifrequest.lang!=cls._get_default_lang():
                    path='/'+request.lang.url_code+path
                ifrequest.httprequest.query_string:
                    path+='?'+request.httprequest.query_string.decode('utf-8')
                returnwerkzeug.utils.redirect(path,code=301)

    @classmethod
    def_get_exception_code_values(cls,exception):
        """Returnatuplewiththeerrorcodefollowingbythevaluesmatchingtheexception"""
        code=500 #defaultcode
        values=dict(
            exception=exception,
            traceback=traceback.format_exc(),
        )
        ifisinstance(exception,exceptions.UserError):
            values['error_message']=exception.args[0]
            code=400
            ifisinstance(exception,exceptions.AccessError):
                code=403

        elifisinstance(exception,QWebException):
            values.update(qweb_exception=exception)

            ifisinstance(exception.error,exceptions.AccessError):
                code=403

        elifisinstance(exception,werkzeug.exceptions.HTTPException):
            code=exception.code

        values.update(
            status_message=werkzeug.http.HTTP_STATUS_CODES.get(code,''),
            status_code=code,
        )

        return(code,values)

    @classmethod
    def_get_values_500_error(cls,env,values,exception):
        values['view']=env["ir.ui.view"]
        returnvalues

    @classmethod
    def_get_error_html(cls,env,code,values):
        returncode,env['ir.ui.view']._render_template('http_routing.%s'%code,values)

    @classmethod
    def_handle_exception(cls,exception):
        is_frontend_request=bool(getattr(request,'is_frontend',False))
        ifnotis_frontend_request:
            #Don'ttouchnonfrontendrequestsexceptionhandling
            returnsuper(IrHttp,cls)._handle_exception(exception)
        try:
            response=super(IrHttp,cls)._handle_exception(exception)

            ifisinstance(response,Exception):
                exception=response
            else:
                #ifparentexcplicitelyreturnsaplainresponse,thenwedon'ttouchit
                returnresponse
        exceptExceptionase:
            if'werkzeug'inconfig['dev_mode']:
                raisee
            exception=e

        code,values=cls._get_exception_code_values(exception)

        ifcodeisNone:
            #Hand-craftedHTTPExceptionlikelycomingfromabort(),
            #usuallyforaredirectresponse->returnitdirectly
            returnexception

        ifnotrequest.uid:
            cls._auth_method_public()

        #Werollbackthecurrenttransactionbeforeinitializinganew
        #cursortoavoidpotentialdeadlocks.

        #Ifthecurrent(failed)transactionwasholdingalock,thenew
        #cursormighthavetowaitforthislocktobereleasedfurther
        #downtheline.However,thiswillonlyhappenafterthe
        #requestisdone(andinfactitwon'thappen).Asaresult,the
        #currentthread/workerisfrozenuntilitstimeoutisreached.

        #Sorollingbackthetransactionwillreleaseanypotentiallock
        #and,sinceweareinacasewhereanexceptionwasraised,the
        #transactionshouldn'tbecommittedinthefirstplace.
        request.env.cr.rollback()

        withregistry(request.env.cr.dbname).cursor()ascr:
            env=api.Environment(cr,request.uid,request.env.context)
            ifcode==500:
                _logger.error("500InternalServerError:\n\n%s",values['traceback'])
                values=cls._get_values_500_error(env,values,exception)
            elifcode==403:
                _logger.warning("403Forbidden:\n\n%s",values['traceback'])
            elifcode==400:
                _logger.warning("400BadRequest:\n\n%s",values['traceback'])
            try:
                code,html=cls._get_error_html(env,code,values)
            exceptException:
                code,html=418,env['ir.ui.view']._render_template('http_routing.http_error',values)

        returnwerkzeug.wrappers.Response(html,status=code,content_type='text/html;charset=utf-8')

    @api.model
    @tools.ormcache('path')
    defurl_rewrite(self,path):
        new_url=False
        router=http.root.get_db_router(request.db).bind('')
        try:
            _=router.match(path,method='POST')
        exceptwerkzeug.exceptions.MethodNotAllowed:
            _=router.match(path,method='GET')
        exceptwerkzeug.routing.RequestRedirectase:
            #getpathfromhttp://{path}?{currentquerystring}
            new_url=e.new_url.split('?')[0][7:]
        exceptwerkzeug.exceptions.NotFound:
            new_url=path
        exceptExceptionase:
            raisee

        returnnew_urlorpath

    #mergewithdefurl_rewriteinmaster/14.1
    @api.model
    @tools.cache('path','query_args')
    def_get_endpoint_qargs(self,path,query_args=None):
        router=http.root.get_db_router(request.db).bind('')
        endpoint=False
        try:
            endpoint=router.match(path,method='POST',query_args=query_args)
        exceptwerkzeug.exceptions.MethodNotAllowed:
            endpoint=router.match(path,method='GET',query_args=query_args)
        exceptwerkzeug.routing.RequestRedirectase:
            new_url=e.new_url[7:] #removescheme
            assertnew_url!=path
            endpoint=self._get_endpoint_qargs(new_url,query_args)
            endpoint=endpointand[endpoint]
        exceptwerkzeug.exceptions.NotFound:
            pass#endpoint=False
        returnendpointandendpoint[0]
