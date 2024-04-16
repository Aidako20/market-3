#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbabel.messages.pofile
importbase64
importcopy
importdatetime
importfunctools
importglob
importhashlib
importio
importitertools
importjinja2
importjson
importlogging
importoperator
importos
importre
importsys
importtempfile

importwerkzeug
importwerkzeug.exceptions
importwerkzeug.utils
importwerkzeug.wrappers
importwerkzeug.wsgi
fromcollectionsimportOrderedDict,defaultdict,Counter
fromwerkzeug.urlsimporturl_encode,url_decode,iri_to_uri
fromlxmlimportetree
importunicodedata


importflectra
importflectra.modules.registry
fromflectra.apiimportcall_kw,Environment
fromflectra.modulesimportget_module_path,get_resource_path
fromflectra.toolsimportimage_process,topological_sort,html_escape,pycompat,ustr,apply_inheritance_specs,lazy_property
fromflectra.tools.mimetypesimportguess_mimetype
fromflectra.tools.translateimport_
fromflectra.tools.miscimportstr2bool,xlsxwriter,file_open
fromflectra.tools.safe_evalimportsafe_eval,time
fromflectraimporthttp,tools
fromflectra.httpimportcontent_disposition,dispatch_rpc,request,serialize_exceptionas_serialize_exception,Response
fromflectra.exceptionsimportAccessError,UserError,AccessDenied
fromflectra.modelsimportcheck_method_name
fromflectra.serviceimportdb,security

_logger=logging.getLogger(__name__)

ifhasattr(sys,'frozen'):
    #Whenrunningoncompiledwindowsbinary,wedon'thaveaccesstopackageloader.
    path=os.path.realpath(os.path.join(os.path.dirname(__file__),'..','views'))
    loader=jinja2.FileSystemLoader(path)
else:
    loader=jinja2.PackageLoader('flectra.addons.web',"views")

env=jinja2.Environment(loader=loader,autoescape=True)
env.filters["json"]=json.dumps

CONTENT_MAXAGE=http.STATIC_CACHE_LONG #menus,translations,staticqweb

DBNAME_PATTERN='^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'

COMMENT_PATTERN=r'Modifiedby[\s\w\-.]+from[\s\w\-.]+'


defnone_values_filtered(func):
    @functools.wraps(func)
    defwrap(iterable):
        returnfunc(vforviniterableifvisnotNone)
    returnwrap

defallow_empty_iterable(func):
    """
    Somefunctionsdonotacceptemptyiterables(e.g.max,minwithnodefaultvalue)
    Thisreturnsthefunction`func`suchthatitreturnsNoneiftheiterable
    isemptyinsteadofraisingaValueError.
    """
    @functools.wraps(func)
    defwrap(iterable):
        iterator=iter(iterable)
        try:
            value=next(iterator)
            returnfunc(itertools.chain([value],iterator))
        exceptStopIteration:
            returnNone
    returnwrap

OPERATOR_MAPPING={
    'max':none_values_filtered(allow_empty_iterable(max)),
    'min':none_values_filtered(allow_empty_iterable(min)),
    'sum':sum,
    'bool_and':all,
    'bool_or':any,
}

#----------------------------------------------------------
#FlectraWebhelpers
#----------------------------------------------------------

db_list=http.db_list

db_monodb=http.db_monodb

defclean(name):returnname.replace('\x3c','')
defserialize_exception(f):
    @functools.wraps(f)
    defwrap(*args,**kwargs):
        try:
            returnf(*args,**kwargs)
        exceptExceptionase:
            _logger.exception("Anexceptionoccuredduringanhttprequest")
            se=_serialize_exception(e)
            error={
                'code':200,
                'message':"FlectraServerError",
                'data':se
            }
            returnwerkzeug.exceptions.InternalServerError(json.dumps(error))
    returnwrap

defredirect_with_hash(*args,**kw):
    """
        ..deprecated::8.0

        Usethe``http.redirect_with_hash()``functioninstead.
    """
    returnhttp.redirect_with_hash(*args,**kw)

defabort_and_redirect(url):
    response=werkzeug.utils.redirect(url,302)
    response=http.root.get_response(request.httprequest,response,explicit_session=False)
    werkzeug.exceptions.abort(response)

defensure_db(redirect='/web/database/selector'):
    #Thishelpershouldbeusedinwebclientauth="none"routes
    #ifthoseroutesneedsadbtoworkwith.
    #Iftheheuristicsdoesnotfindanydatabase,thentheuserswillbe
    #redirectedtodbselectororanyurlspecifiedby`redirect`argument.
    #Ifthedbistakenoutofaqueryparameter,itwillbecheckedagainst
    #`http.db_filter()`inordertoensureit'slegitandthusavoiddb
    #forgeringthatcouldleadtoxssattacks.
    db=request.params.get('db')andrequest.params.get('db').strip()

    #Ensuredbislegit
    ifdbanddbnotinhttp.db_filter([db]):
        db=None

    ifdbandnotrequest.session.db:
        #Useraskedaspecificdatabaseonanewsession.
        #Thatmeanthenodbrouterhasbeenusedtofindtheroute
        #Dependingoninstalledmoduleinthedatabase,therenderingofthepage
        #maydependondatainjectedbythedatabaseroutedispatcher.
        #Thus,weredirecttheusertothesamepagebutwiththesessioncookieset.
        #Thiswillforceusingthedatabaseroutedispatcher...
        r=request.httprequest
        url_redirect=werkzeug.urls.url_parse(r.base_url)
        ifr.query_string:
            #inP3,request.query_stringisbytes,therestistext,can'tmixthem
            query_string=iri_to_uri(r.query_string)
            url_redirect=url_redirect.replace(query=query_string)
        request.session.db=db
        abort_and_redirect(url_redirect.to_url())

    #ifdbnotprovided,usethesessionone
    ifnotdbandrequest.session.dbandhttp.db_filter([request.session.db]):
        db=request.session.db

    #ifnodatabaseprovidedandnodatabaseinsession,usemonodb
    ifnotdb:
        db=db_monodb(request.httprequest)

    #ifnodbcanbefoundtilhere,sendtothedatabaseselector
    #thedatabaseselectorwillredirecttodatabasemanagerifneeded
    ifnotdb:
        werkzeug.exceptions.abort(werkzeug.utils.redirect(redirect,303))

    #alwaysswitchthesessiontothecomputeddb
    ifdb!=request.session.db:
        request.session.logout()
        abort_and_redirect(request.httprequest.url)

    request.session.db=db

defmodule_installed(environment):
    #Candidatesmodulethecurrentheuristicisthe/staticdir
    loadable=list(http.addons_manifest)

    #Retrievedatabaseinstalledmodules
    #TODOThefollowingcodeshouldmovetoir.module.module.list_installed_modules()
    Modules=environment['ir.module.module']
    domain=[('state','=','installed'),('name','in',loadable)]
    modules=OrderedDict(
        (module.name,module.dependencies_id.mapped('name'))
        formoduleinModules.search(domain)
    )

    sorted_modules=topological_sort(modules)
    returnsorted_modules

defmodule_installed_bypass_session(dbname):
    try:
        registry=flectra.registry(dbname)
        withregistry.cursor()ascr:
            returnmodule_installed(
                environment=Environment(cr,flectra.SUPERUSER_ID,{}))
    exceptException:
        pass
    return{}

defmodule_boot(db=None):
    server_wide_modules=flectra.conf.server_wide_modulesor[]
    serverside=['base','web']
    dbside=[]
    foriinserver_wide_modules:
        ifiinhttp.addons_manifestandinotinserverside:
            serverside.append(i)
    monodb=dbordb_monodb()
    ifmonodb:
        dbside=module_installed_bypass_session(monodb)
        dbside=[iforiindbsideifinotinserverside]
    addons=serverside+dbside
    returnaddons


deffs2web(path):
    """convertFSpathintowebpath"""
    return'/'.join(path.split(os.path.sep))

defmanifest_glob(extension,addons=None,db=None,include_remotes=False):
    ifaddonsisNone:
        addons=module_boot(db=db)

    r=[]
    foraddoninaddons:
        manifest=http.addons_manifest.get(addon,None)
        ifnotmanifest:
            continue
        #ensuredoesnotendswith/
        addons_path=os.path.join(manifest['addons_path'],'')[:-1]
        globlist=manifest.get(extension,[])
        forpatterningloblist:
            ifpattern.startswith(('http://','https://','//')):
                ifinclude_remotes:
                    r.append((None,pattern,addon))
            else:
                forpathinglob.glob(os.path.normpath(os.path.join(addons_path,addon,pattern))):
                    r.append((path,fs2web(path[len(addons_path):]),addon))
    returnr


defmanifest_list(extension,mods=None,db=None,debug=None):
    """listresourcestoloadspecifyingeither:
    mods:acommaseparatedstringlistingmodules
    db:adatabasename(returnallinstalledmodulesinthatdatabase)
    """
    ifdebugisnotNone:
        _logger.warning("flectra.addons.web.main.manifest_list():debugparameterisdeprecated")
    mods=mods.split(',')
    files=manifest_glob(extension,addons=mods,db=db,include_remotes=True)
    return[wpfor_fp,wp,addoninfiles]

defget_last_modified(files):
    """Returnsthemodificationtimeofthemostrecentlymodified
    fileprovided

    :paramlist(str)files:namesoffilestocheck
    :return:mostrecentmodificationtimeamongstthefileset
    :rtype:datetime.datetime
    """
    files=list(files)
    iffiles:
        returnmax(datetime.datetime.fromtimestamp(os.path.getmtime(f))
                   forfinfiles)
    returndatetime.datetime(1970,1,1)

defmake_conditional(response,last_modified=None,etag=None,max_age=0):
    """Makestheprovidedresponseconditionalbasedupontherequest,
    andmandatesrevalidationfromclients

    UsesWerkzeug'sown:meth:`ETagResponseMixin.make_conditional`,after
    setting``last_modified``and``etag``correctlyontheresponseobject

    :paramresponse:Werkzeugresponse
    :typeresponse:werkzeug.wrappers.Response
    :paramdatetime.datetimelast_modified:lastmodificationdateoftheresponsecontent
    :paramstretag:somesortofchecksumofthecontent(deepetag)
    :return:theresponseobjectprovided
    :rtype:werkzeug.wrappers.Response
    """
    response.cache_control.must_revalidate=True
    response.cache_control.max_age=max_age
    iflast_modified:
        response.last_modified=last_modified
    ifetag:
        response.set_etag(etag)
    returnresponse.make_conditional(request.httprequest)

def_get_login_redirect_url(uid,redirect=None):
    """Decideifuserrequiresaspecificpost-loginredirect,e.g.for2FA,oriftheyare
    fullyloggedandcanproceedtotherequestedURL
    """
    ifrequest.session.uid:#fullylogged
        returnredirector'/web'

    #partialsession(MFA)
    url=request.env(user=uid)['res.users'].browse(uid)._mfa_url()
    ifnotredirect:
        returnurl

    parsed=werkzeug.urls.url_parse(url)
    qs=parsed.decode_query()
    qs['redirect']=redirect
    returnparsed.replace(query=werkzeug.urls.url_encode(qs)).to_url()

deflogin_and_redirect(db,login,key,redirect_url='/web'):
    uid=request.session.authenticate(db,login,key)
    redirect_url=_get_login_redirect_url(uid,redirect_url)
    returnset_cookie_and_redirect(redirect_url)

defset_cookie_and_redirect(redirect_url):
    redirect=werkzeug.utils.redirect(redirect_url,303)
    redirect.autocorrect_location_header=False
    returnredirect

defclean_action(action,env):
    action_type=action.setdefault('type','ir.actions.act_window_close')
    ifaction_type=='ir.actions.act_window':
        action=fix_view_modes(action)

    #Whenreturninganaction,keeponlyrelevantfields/properties
    readable_fields=env[action['type']]._get_readable_fields()
    action_type_fields=env[action['type']]._fields.keys()

    cleaned_action={
        field:value
        forfield,valueinaction.items()
        #keepallowedfieldsandcustompropertiesfields
        iffieldinreadable_fieldsorfieldnotinaction_type_fields
    }

    #Warnaboutcustompropertiesfields,becauseuseisdiscouraged
    action_name=action.get('name')oraction
    custom_properties=action.keys()-readable_fields-action_type_fields
    ifcustom_properties:
        _logger.warning("Action%rcontainscustomproperties%s.Passingthem"
            "viathe`params`or`context`propertiesisrecommendedinstead",
            action_name,','.join(map(repr,custom_properties)))

    returncleaned_action

#Ithinkgenerate_views,fix_view_modesshouldgointojsActionManager
defgenerate_views(action):
    """
    Whiletheservergeneratesasequencecalled"views"computingdependencies
    betweenabunchofstuffforviewscomingdirectlyfromthedatabase
    (the``ir.actions.act_windowmodel``),it'salsopossiblefore.g.buttons
    toreturncustomviewdictionariesgeneratedonthefly.

    Inthatcase,thereisno``views``keyavailableontheaction.

    Sincethewebclientrelieson``action['views']``,generateitherefrom
    ``view_mode``and``view_id``.

    Currentlyhandlestwodifferentcases:

    *noview_id,multipleview_mode
    *singleview_id,singleview_mode

    :paramdictaction:actiondescriptordictionarytogenerateaviewskeyfor
    """
    view_id=action.get('view_id')orFalse
    ifisinstance(view_id,(list,tuple)):
        view_id=view_id[0]

    #providingatleastoneviewmodeisarequirement,notanoption
    view_modes=action['view_mode'].split(',')

    iflen(view_modes)>1:
        ifview_id:
            raiseValueError('Non-dbactiondictionariesshouldprovide'
                             'eithermultipleviewmodesorasingleview'
                             'modeandanoptionalviewid.\n\nGotview'
                             'modes%randviewid%rforaction%r'%(
                view_modes,view_id,action))
        action['views']=[(False,mode)formodeinview_modes]
        return
    action['views']=[(view_id,view_modes[0])]

deffix_view_modes(action):
    """Forhistoricalreasons,Flectrahasweirddealingsinrelationto
    view_modeandtheview_typeattribute(onwindowactions):

    *oneoftheviewmodesis``tree``,whichstandsforbothlistviews
      andtreeviews
    *thechoiceismadebychecking``view_type``,whichiseither
      ``form``foralistviewor``tree``foranactualtreeview

    Thismethodssimplyfoldstheview_typeintoview_modebyaddinga
    newviewmode``list``whichistheresultofthe``tree``view_mode
    inconjunctionwiththe``form``view_type.

    TODO:thisshouldgointothedoc,somekindof"peculiarities"section

    :paramdictaction:anactiondescriptor
    :returns:nothing,theactionismodifiedinplace
    """
    ifnotaction.get('views'):
        generate_views(action)

    ifaction.pop('view_type','form')!='form':
        returnaction

    if'view_mode'inaction:
        action['view_mode']=','.join(
            modeifmode!='tree'else'list'
            formodeinaction['view_mode'].split(','))
    action['views']=[
        [id,modeifmode!='tree'else'list']
        forid,modeinaction['views']
    ]

    returnaction

def_local_web_translations(trans_file):
    messages=[]
    try:
        withopen(trans_file)ast_file:
            po=babel.messages.pofile.read_po(t_file)
    exceptException:
        return
    forxinpo:
        ifx.idandx.stringand"openerp-web"inx.auto_comments:
            messages.append({'id':x.id,'string':x.string})
    returnmessages

defxml2json_from_elementtree(el,preserve_whitespaces=False):
    """xml2json-direct
    SimpleandstraightforwardXML-to-JSONconverterinPython
    NewBSDLicensed
    http://code.google.com/p/xml2json-direct/
    """
    res={}
    ifel.tag[0]=="{":
        ns,name=el.tag.rsplit("}",1)
        res["tag"]=name
        res["namespace"]=ns[1:]
    else:
        res["tag"]=el.tag
    res["attrs"]={}
    fork,vinel.items():
        res["attrs"][k]=v
    kids=[]
    ifel.textand(preserve_whitespacesorel.text.strip()!=''):
        kids.append(el.text)
    forkidinel:
        kids.append(xml2json_from_elementtree(kid,preserve_whitespaces))
        ifkid.tailand(preserve_whitespacesorkid.tail.strip()!=''):
            kids.append(kid.tail)
    res["children"]=kids
    returnres

classHomeStaticTemplateHelpers(object):
    """
    HelperClassthatwrapsthereadingofstaticqwebtemplatesfiles
    andxpathinheritanceappliedtothosetemplates
    /!\Templateinheritanceorderisdefinedbyir.module.modulenaturalorder
        whichis"sequence,name"
        Thenatopologicalsortisapplied,whichjustputsdependencies
        ofamodulebeforethatmodule
    """
    NAME_TEMPLATE_DIRECTIVE='t-name'
    STATIC_INHERIT_DIRECTIVE='t-inherit'
    STATIC_INHERIT_MODE_DIRECTIVE='t-inherit-mode'
    PRIMARY_MODE='primary'
    EXTENSION_MODE='extension'
    DEFAULT_MODE=PRIMARY_MODE

    def__init__(self,addons,db,checksum_only=False,debug=False):
        '''
        :paramstr|listaddons:plainlistorcommaseparatedlistofaddons
        :paramstrdb:thecurrentdbweareworkingon
        :paramboolchecksum_only:onlycomputesthechecksumofallfilesforaddons
        :paramstrdebug:thedebugmodeofthesession
        '''
        super(HomeStaticTemplateHelpers,self).__init__()
        self.addons=addons.split(',')ifisinstance(addons,str)elseaddons
        self.db=db
        self.debug=debug
        self.checksum_only=checksum_only
        self.template_dict=OrderedDict()

    def_get_parent_template(self,addon,template):
        """Computestherealaddonnameandthetemplatename
        oftheparenttemplate(theonethatisinheritedfrom)

        :paramstraddon:theaddonthetemplateisdeclaredin
        :parametreetemplate:thecurrenttemplatewearearehandling
        :returns:(str,str)
        """
        original_template_name=template.attrib[self.STATIC_INHERIT_DIRECTIVE]
        split_name_attempt=original_template_name.split('.',1)
        parent_addon,parent_name=tuple(split_name_attempt)iflen(split_name_attempt)==2else(addon,original_template_name)
        ifparent_addonnotinself.template_dict:
            iforiginal_template_nameinself.template_dict[addon]:
                parent_addon=addon
                parent_name=original_template_name
            else:
                raiseValueError(_('Module%snotloadedorinexistent,ortemplatesofaddonbeingloaded(%s)aremisordered')%(parent_addon,addon))

        ifparent_namenotinself.template_dict[parent_addon]:
            raiseValueError(_("Notemplatefoundtoinheritfrom.Module%sandtemplatename%s")%(parent_addon,parent_name))

        returnparent_addon,parent_name

    def_compute_xml_tree(self,addon,file_name,source):
        """Computesthexmltreethat'source'contains
        Appliesinheritancespecsintheprocess

        :paramstraddon:thecurrentaddonwearereadingfilesfor
        :paramstrfile_name:thecurrentnameofthefilewearereading
        :paramstrsource:thecontentofthefile
        :returns:etree
        """
        try:
            all_templates_tree=etree.parse(io.BytesIO(source),parser=etree.XMLParser(remove_comments=True)).getroot()
        exceptetree.ParseErrorase:
            _logger.error("Couldnotparsefile%s:%s"%(file_name,e.msg))
            raisee

        self.template_dict.setdefault(addon,OrderedDict())
        fortemplate_treeinlist(all_templates_tree):
            ifself.NAME_TEMPLATE_DIRECTIVEintemplate_tree.attrib:
                template_name=template_tree.attrib[self.NAME_TEMPLATE_DIRECTIVE]
                dotted_names=template_name.split('.',1)
                iflen(dotted_names)>1anddotted_names[0]==addon:
                    template_name=dotted_names[1]
            else:
                #self.template_dict[addon]growsafterprocessingeachtemplate
                template_name='anonymous_template_%s'%len(self.template_dict[addon])
            ifself.STATIC_INHERIT_DIRECTIVEintemplate_tree.attrib:
                inherit_mode=template_tree.attrib.get(self.STATIC_INHERIT_MODE_DIRECTIVE,self.DEFAULT_MODE)
                ifinherit_modenotin[self.PRIMARY_MODE,self.EXTENSION_MODE]:
                    raiseValueError(_("Invalidinheritmode.Module%sandtemplatename%s")%(addon,template_name))

                parent_addon,parent_name=self._get_parent_template(addon,template_tree)

                #Afterseveralperformancetests,wefoundoutthatdeepcopyisthemostefficient
                #solutioninthiscase(comparedwithcopy,xpathwith'.'andstringifying).
                parent_tree=copy.deepcopy(self.template_dict[parent_addon][parent_name])

                xpaths=list(template_tree)
                ifself.debugandinherit_mode==self.EXTENSION_MODE:
                    forxpathinxpaths:
                        xpath.insert(0,etree.Comment("Modifiedby%sfrom%s"%(template_name,addon)))
                elifinherit_mode==self.PRIMARY_MODE:
                    parent_tree.tag=template_tree.tag
                inherited_template=apply_inheritance_specs(parent_tree,xpaths)

                ifinherit_mode==self.PRIMARY_MODE: #Newtemplate_tree:A'=B(A)
                    forattr_name,attr_valintemplate_tree.attrib.items():
                        ifattr_namenotin('t-inherit','t-inherit-mode'):
                            inherited_template.set(attr_name,attr_val)
                    ifself.debug:
                        self._remove_inheritance_comments(inherited_template)
                    self.template_dict[addon][template_name]=inherited_template

                else: #Modifiesoriginal:A=B(A)
                    self.template_dict[parent_addon][parent_name]=inherited_template
            else:
                iftemplate_nameinself.template_dict[addon]:
                    raiseValueError(_("Template%salreadyexistsinmodule%s")%(template_name,addon))
                self.template_dict[addon][template_name]=template_tree
        returnall_templates_tree

    def_remove_inheritance_comments(self,inherited_template):
        '''Removethecommentsaddedinthetemplatealready,theycomefromothertemplatesextending
        thebaseofthisinheritance

        :paraminherited_template:
        '''
        forcommentininherited_template.xpath('//comment()'):
            ifre.match(COMMENT_PATTERN,comment.text.strip()):
                comment.getparent().remove(comment)

    def_manifest_glob(self):
        '''Proxyformanifest_glob
        Usefulltomake'self'testable'''
        returnmanifest_glob('qweb',self.addons,self.db)

    def_read_addon_file(self,file_path):
        """Readsthecontentofafilegivenbyfile_path
        Usefulltomake'self'testable
        :paramstrfile_path:
        :returns:str
        """
        withopen(file_path,'rb')asfp:
            contents=fp.read()
        returncontents

    def_concat_xml(self,file_dict):
        """Concatenatexmlfiles

        :paramdict(list)file_dict:
            key:addonname
            value:listoffilesforanaddon
        :returns:(concatenation_result,checksum)
        :rtype:(bytes,str)
        """
        checksum=hashlib.new('sha512') #sha512/256
        ifnotfile_dict:
            returnb'',checksum.hexdigest()

        root=None
        foraddon,fnamesinfile_dict.items():
            forfnameinfnames:
                contents=self._read_addon_file(fname)
                checksum.update(contents)
                ifnotself.checksum_only:
                    xml=self._compute_xml_tree(addon,fname,contents)

                    ifrootisNone:
                        root=etree.Element(xml.tag)

        foraddoninself.template_dict.values():
            fortemplateinaddon.values():
                root.append(template)

        returnetree.tostring(root,encoding='utf-8')ifrootisnotNoneelseb'',checksum.hexdigest()[:64]

    def_get_qweb_templates(self):
        """Oneandonlyentrypointthatgetsandevaluatesstaticqwebtemplates

        :rtype:(str,str)
        """
        files=OrderedDict([(addon,list())foraddoninself.addons])
        [files[f[2]].append(f[0])forfinself._manifest_glob()]
        content,checksum=self._concat_xml(files)
        returncontent,checksum

    @classmethod
    defget_qweb_templates_checksum(cls,addons,db=None,debug=False):
        returncls(addons,db,checksum_only=True,debug=debug)._get_qweb_templates()[1]

    @classmethod
    defget_qweb_templates(cls,addons,db=None,debug=False):
        returncls(addons,db,debug=debug)._get_qweb_templates()[0]

#Sharedparametersforalllogin/signupflows
SIGN_UP_REQUEST_PARAMS={'db','login','debug','token','message','error','scope','mode',
                          'redirect','redirect_hostname','email','name','partner_id',
                          'password','confirm_password','city','country_id','lang'}

classGroupsTreeNode:
    """
    Thisclassbuildsanorderedtreeofgroupsfromtheresultofa`read_group(lazy=False)`.
    The`read_group`returnsalistofdictionnariesandeachdictionnaryisusedto
    buildaleaf.Theentiretreeisbuiltbyinsertingallleaves.
    """

    def__init__(self,model,fields,groupby,groupby_type,root=None):
        self._model=model
        self._export_field_names=fields #exportedfieldnames(e.g.'journal_id','account_id/name',...)
        self._groupby=groupby
        self._groupby_type=groupby_type

        self.count=0 #Totalnumberofrecordsinthesubtree
        self.children=OrderedDict()
        self.data=[] #Onlyleafnodeshavedata

        ifroot:
            self.insert_leaf(root)

    def_get_aggregate(self,field_name,data,group_operator):
        #Whenexportingone2manyfields,multipledatalinesmightbeexportedforonerecord.
        #Blankcellsofadditionnallinesarefilledwithanemptystring.Thiscouldleadto''being
        #aggregatedwithanintegerorfloat.
        data=(valueforvalueindataifvalue!='')

        ifgroup_operator=='avg':
            returnself._get_avg_aggregate(field_name,data)

        aggregate_func=OPERATOR_MAPPING.get(group_operator)
        ifnotaggregate_func:
            _logger.warning("Unsupportedexportofgroup_operator'%s'forfield%sonmodel%s"%(group_operator,field_name,self._model._name))
            return

        ifself.data:
            returnaggregate_func(data)
        returnaggregate_func((child.aggregated_values.get(field_name)forchildinself.children.values()))

    def_get_avg_aggregate(self,field_name,data):
        aggregate_func=OPERATOR_MAPPING.get('sum')
        ifself.data:
            returnaggregate_func(data)/self.count
        children_sums=(child.aggregated_values.get(field_name)*child.countforchildinself.children.values())
        returnaggregate_func(children_sums)/self.count

    def_get_aggregated_field_names(self):
        """Returnfieldnamesofexportedfieldhavingagroupoperator"""
        aggregated_field_names=[]
        forfield_nameinself._export_field_names:
            iffield_name=='.id':
                field_name='id'
            if'/'infield_name:
                #Currentlynosupportofaggregatedvaluefornestedrecordfields
                #e.g.line_ids/analytic_line_ids/amount
                continue
            field=self._model._fields[field_name]
            iffield.group_operator:
                aggregated_field_names.append(field_name)
        returnaggregated_field_names

    #Lazypropertytomemoizeaggregatedvaluesofchildrennodestoavoiduselessrecomputations
    @lazy_property
    defaggregated_values(self):

        aggregated_values={}

        #Transposethedatamatrixtogroupallvaluesofeachfieldinoneiterable
        field_values=zip(*self.data)
        forfield_nameinself._export_field_names:
            field_data=self.dataandnext(field_values)or[]

            iffield_nameinself._get_aggregated_field_names():
                field=self._model._fields[field_name]
                aggregated_values[field_name]=self._get_aggregate(field_name,field_data,field.group_operator)

        returnaggregated_values

    defchild(self,key):
        """
        Returnthechildidentifiedby`key`.
        Ifitdoesn'texistsinsertsadefaultnodeandreturnsit.
        :paramkey:childkeyidentifier(groupbyvalueasreturnedbyread_group,
                    usually(id,display_name))
        :return:thechildnode
        """
        ifkeynotinself.children:
            self.children[key]=GroupsTreeNode(self._model,self._export_field_names,self._groupby,self._groupby_type)
        returnself.children[key]

    definsert_leaf(self,group):
        """
        Buildaleaffrom`group`andinsertitinthetree.
        :paramgroup:dictasreturnedby`read_group(lazy=False)`
        """
        leaf_path=[group.get(groupby_field)forgroupby_fieldinself._groupby]
        domain=group.pop('__domain')
        count=group.pop('__count')

        records=self._model.search(domain,offset=0,limit=False,order=False)

        #Followthepathfromthetoplevelgrouptothedeepest
        #groupwhichactuallycontainstherecords'data.
        node=self#root
        node.count+=count
        fornode_keyinleaf_path:
            #Godowntothenextnodeorcreateoneifitdoesnotexistyet.
            node=node.child(node_key)
            #Updatecountvalueandaggregatedvalue.
            node.count+=count

        node.data=records.export_data(self._export_field_names).get('datas',[])


classExportXlsxWriter:

    def__init__(self,field_names,row_count=0):
        self.field_names=field_names
        self.output=io.BytesIO()
        self.workbook=xlsxwriter.Workbook(self.output,{'in_memory':True})
        self.base_style=self.workbook.add_format({'text_wrap':True})
        self.header_style=self.workbook.add_format({'bold':True})
        self.header_bold_style=self.workbook.add_format({'text_wrap':True,'bold':True,'bg_color':'#e9ecef'})
        self.date_style=self.workbook.add_format({'text_wrap':True,'num_format':'yyyy-mm-dd'})
        self.datetime_style=self.workbook.add_format({'text_wrap':True,'num_format':'yyyy-mm-ddhh:mm:ss'})
        self.worksheet=self.workbook.add_worksheet()
        self.value=False
        self.float_format='#,##0.00'
        decimal_places=[res['decimal_places']forresinrequest.env['res.currency'].search_read([],['decimal_places'])]
        self.monetary_format=f'#,##0.{max(decimal_placesor[2])*"0"}'

        ifrow_count>self.worksheet.xls_rowmax:
            raiseUserError(_('Therearetoomanyrows(%srows,limit:%s)toexportasExcel2007-2013(.xlsx)format.Considersplittingtheexport.')%(row_count,self.worksheet.xls_rowmax))

    def__enter__(self):
        self.write_header()
        returnself

    def__exit__(self,exc_type,exc_value,exc_traceback):
        self.close()

    defwrite_header(self):
        #Writemainheader
        fori,fieldnameinenumerate(self.field_names):
            self.write(0,i,fieldname,self.header_style)
        self.worksheet.set_column(0,i,30)#around220pixels

    defclose(self):
        self.workbook.close()
        withself.output:
            self.value=self.output.getvalue()

    defwrite(self,row,column,cell_value,style=None):
        self.worksheet.write(row,column,cell_value,style)

    defwrite_cell(self,row,column,cell_value):
        cell_style=self.base_style

        ifisinstance(cell_value,bytes):
            try:
                #becausexlsxusesrawexport,wecangetabytesobject
                #here.xlsxwriterdoesnotsupportbytesvaluesinPython3->
                #assumethisisbase64anddecodetoastring,ifthis
                #failsnotethatyoucan'texport
                cell_value=pycompat.to_text(cell_value)
            exceptUnicodeDecodeError:
                raiseUserError(_("BinaryfieldscannotbeexportedtoExcelunlesstheircontentisbase64-encoded.Thatdoesnotseemtobethecasefor%s.",self.field_names)[column])

        ifisinstance(cell_value,str):
            iflen(cell_value)>self.worksheet.xls_strmax:
                cell_value=_("ThecontentofthiscellistoolongforanXLSXfile(morethan%scharacters).PleaseusetheCSVformatforthisexport.",self.worksheet.xls_strmax)
            else:
                cell_value=cell_value.replace("\r","")
        elifisinstance(cell_value,datetime.datetime):
            cell_style=self.datetime_style
        elifisinstance(cell_value,datetime.date):
            cell_style=self.date_style
        elifisinstance(cell_value,float):
            cell_style.set_num_format(self.float_format)
        elifisinstance(cell_value,(list,tuple)):
            cell_value=pycompat.to_text(cell_value)
        self.write(row,column,cell_value,cell_style)

classGroupExportXlsxWriter(ExportXlsxWriter):

    def__init__(self,fields,row_count=0):
        super().__init__([f['label'].strip()forfinfields],row_count)
        self.fields=fields

    defwrite_group(self,row,column,group_name,group,group_depth=0):
        group_name=group_name[1]ifisinstance(group_name,tuple)andlen(group_name)>1elsegroup_name
        ifgroup._groupby_type[group_depth]!='boolean':
            group_name=group_nameor_("Undefined")
        row,column=self._write_group_header(row,column,group_name,group,group_depth)

        #Recursivelywritesub-groups
        forchild_group_name,child_groupingroup.children.items():
            row,column=self.write_group(row,column,child_group_name,child_group,group_depth+1)

        forrecordingroup.data:
            row,column=self._write_row(row,column,record)
        returnrow,column

    def_write_row(self,row,column,data):
        forvalueindata:
            self.write_cell(row,column,value)
            column+=1
        returnrow+1,0

    def_write_group_header(self,row,column,label,group,group_depth=0):
        aggregates=group.aggregated_values

        label='%s%s(%s)'%('   '*group_depth,label,group.count)
        self.write(row,column,label,self.header_bold_style)
        forfieldinself.fields[1:]:#Noaggregatesallowedinthefirstcolumnbecauseofthegrouptitle
            column+=1
            aggregated_value=aggregates.get(field['name'])
            iffield.get('type')=='monetary':
                self.header_bold_style.set_num_format(self.monetary_format)
            eliffield.get('type')=='float':
                self.header_bold_style.set_num_format(self.float_format)
            else:
                aggregated_value=str(aggregated_valueifaggregated_valueisnotNoneelse'')
            self.write(row,column,aggregated_value,self.header_bold_style)
        returnrow+1,0


#----------------------------------------------------------
#FlectraWebwebControllers
#----------------------------------------------------------
classHome(http.Controller):

    @http.route('/',type='http',auth="none")
    defindex(self,s_action=None,db=None,**kw):
        returnhttp.local_redirect('/web',query=request.params,keep_hash=True)

    #ideally,thisrouteshouldbe`auth="user"`butthatdon'tworkinnon-monodbmode.
    @http.route('/web',type='http',auth="none")
    defweb_client(self,s_action=None,**kw):
        ensure_db()
        ifnotrequest.session.uid:
            returnwerkzeug.utils.redirect('/web/login',303)
        ifkw.get('redirect'):
            returnwerkzeug.utils.redirect(kw.get('redirect'),303)

        request.uid=request.session.uid
        try:
            context=request.env['ir.http'].webclient_rendering_context()
            response=request.render('web.webclient_bootstrap',qcontext=context)
            response.headers['X-Frame-Options']='DENY'
            returnresponse
        exceptAccessError:
            returnwerkzeug.utils.redirect('/web/login?error=access')

    @http.route('/web/webclient/load_menus/<string:unique>',type='http',auth='user',methods=['GET'])
    defweb_load_menus(self,unique):
        """
        Loadsthemenusforthewebclient
        :paramunique:thisparametersisnotused,butmandatory:itisusedbytheHTTPstacktomakeauniquerequest
        :return:themenus(includingtheimagesinBase64)
        """
        menus=request.env["ir.ui.menu"].load_menus(request.session.debug)
        body=json.dumps(menus,default=ustr)
        response=request.make_response(body,[
            #thismethodmustspecifyacontent-typeapplication/jsoninsteadofusingthedefaulttext/htmlsetbecause
            #thetypeoftherouteissettoHTTP,buttherpcismadewithagetandexpectsJSON
            ('Content-Type','application/json'),
            ('Cache-Control','public,max-age='+str(CONTENT_MAXAGE)),
        ])
        returnresponse

    def_login_redirect(self,uid,redirect=None):
        return_get_login_redirect_url(uid,redirect)

    @http.route('/web/login',type='http',auth="none")
    defweb_login(self,redirect=None,**kw):
        ensure_db()
        request.params['login_success']=False
        ifrequest.httprequest.method=='GET'andredirectandrequest.session.uid:
            returnhttp.redirect_with_hash(redirect)

        ifnotrequest.uid:
            request.uid=flectra.SUPERUSER_ID

        values={k:vfork,vinrequest.params.items()ifkinSIGN_UP_REQUEST_PARAMS}
        try:
            values['databases']=http.db_list()
        exceptflectra.exceptions.AccessDenied:
            values['databases']=None

        ifrequest.httprequest.method=='POST':
            old_uid=request.uid
            try:
                uid=request.session.authenticate(request.session.db,request.params['login'],request.params['password'])
                request.params['login_success']=True
                returnhttp.redirect_with_hash(self._login_redirect(uid,redirect=redirect))
            exceptflectra.exceptions.AccessDeniedase:
                request.uid=old_uid
                ife.args==flectra.exceptions.AccessDenied().args:
                    values['error']=_("Wronglogin/password")
                else:
                    values['error']=e.args[0]
        else:
            if'error'inrequest.paramsandrequest.params.get('error')=='access':
                values['error']=_('Onlyemployeescanaccessthisdatabase.Pleasecontacttheadministrator.')

        if'login'notinvaluesandrequest.session.get('auth_login'):
            values['login']=request.session.get('auth_login')

        ifnotflectra.tools.config['list_db']:
            values['disable_database_manager']=True

        response=request.render('web.login',values)
        response.headers['X-Frame-Options']='DENY'
        returnresponse

    @http.route('/web/become',type='http',auth='user',sitemap=False)
    defswitch_to_admin(self):
        uid=request.env.user.id
        ifrequest.env.user._is_system():
            uid=request.session.uid=flectra.SUPERUSER_ID
            #invalidatesessiontokencacheaswe'vechangedtheuid
            request.env['res.users'].clear_caches()
            request.session.session_token=security.compute_session_token(request.session,request.env)

        returnhttp.local_redirect(self._login_redirect(uid),keep_hash=True)

classWebClient(http.Controller):

    @http.route('/web/webclient/csslist',type='json',auth="none")
    defcsslist(self,mods=None):
        returnmanifest_list('css',mods=mods)

    @http.route('/web/webclient/jslist',type='json',auth="none")
    defjslist(self,mods=None):
        returnmanifest_list('js',mods=mods)

    @http.route('/web/webclient/locale/<string:lang>',type='http',auth="none")
    defload_locale(self,lang):
        magic_file_finding=[lang.replace("_",'-').lower(),lang.split('_')[0]]
        forcodeinmagic_file_finding:
            try:
                returnhttp.Response(
                    werkzeug.wsgi.wrap_file(
                        request.httprequest.environ,
                        file_open('web/static/lib/moment/locale/%s.js'%code,'rb')
                    ),
                    content_type='application/javascript;charset=utf-8',
                    headers=[('Cache-Control','max-age=%s'%http.STATIC_CACHE)],
                    direct_passthrough=True,
                )
            exceptIOError:
                _logger.debug("Nomomentlocaleforcode%s",code)

        returnrequest.make_response("",headers=[
            ('Content-Type','application/javascript'),
            ('Cache-Control','max-age=%s'%http.STATIC_CACHE),
        ])

    @http.route('/web/webclient/qweb/<string:unique>',type='http',auth="none",cors="*")
    defqweb(self,unique,mods=None,db=None):
        content=HomeStaticTemplateHelpers.get_qweb_templates(mods,db,debug=request.session.debug)

        returnrequest.make_response(content,[
                ('Content-Type','text/xml'),
                ('Cache-Control','public,max-age='+str(CONTENT_MAXAGE))
            ])

    @http.route('/web/webclient/bootstrap_translations',type='json',auth="none")
    defbootstrap_translations(self,mods):
        """Loadlocaltranslationsfrom*.pofiles,asatemporarysolution
            untilwehaveestablishedavalidsession.Thisismeantonly
            fortranslatingtheloginpageanddbmanagementchrome,using
            thebrowser'slanguage."""
        #Forperformancereasonsweonlyloadasingletranslation,sofor
        #sub-languages(thatshouldonlybepartiallytranslated)weloadthe
        #mainlanguagePOinstead-thatshouldbeenoughfortheloginscreen.
        context=dict(request.context)
        request.session._fix_lang(context)
        lang=context['lang'].split('_')[0]

        translations_per_module={}
        foraddon_nameinmods:
            ifhttp.addons_manifest[addon_name].get('bootstrap'):
                addons_path=http.addons_manifest[addon_name]['addons_path']
                f_name=os.path.join(addons_path,addon_name,"i18n",lang+".po")
                ifnotos.path.exists(f_name):
                    continue
                translations_per_module[addon_name]={'messages':_local_web_translations(f_name)}

        return{"modules":translations_per_module,
                "lang_parameters":None}

    @http.route('/web/webclient/translations/<string:unique>',type='http',auth="public")
    deftranslations(self,unique,mods=None,lang=None):
        """
        Loadthetranslationsforthespecifiedlanguageandmodules

        :paramunique:thisparametersisnotused,butmandatory:itisusedbytheHTTPstacktomakeauniquerequest
        :parammods:themodules,acommaseparatedlist
        :paramlang:thelanguageoftheuser
        :return:
        """

        ifmods:
            mods=mods.split(',')
        translations_per_module,lang_params=request.env["ir.translation"].get_translations_for_webclient(mods,lang)

        body=json.dumps({
            'lang':lang,
            'lang_parameters':lang_params,
            'modules':translations_per_module,
            'multi_lang':len(request.env['res.lang'].sudo().get_installed())>1,
        })
        response=request.make_response(body,[
            #thismethodmustspecifyacontent-typeapplication/jsoninsteadofusingthedefaulttext/htmlsetbecause
            #thetypeoftherouteissettoHTTP,buttherpcismadewithagetandexpectsJSON
            ('Content-Type','application/json'),
            ('Cache-Control','public,max-age='+str(CONTENT_MAXAGE)),
        ])
        returnresponse

    @http.route('/web/webclient/version_info',type='json',auth="none")
    defversion_info(self):
        returnflectra.service.common.exp_version()

    @http.route('/web/tests',type='http',auth="user")
    deftest_suite(self,mod=None,**kwargs):
        returnrequest.render('web.qunit_suite')

    @http.route('/web/tests/mobile',type='http',auth="none")
    deftest_mobile_suite(self,mod=None,**kwargs):
        returnrequest.render('web.qunit_mobile_suite')

    @http.route('/web/benchmarks',type='http',auth="none")
    defbenchmarks(self,mod=None,**kwargs):
        returnrequest.render('web.benchmark_suite')


classDatabase(http.Controller):

    def_render_template(self,**d):
        d.setdefault('manage',True)
        d['insecure']=flectra.tools.config.verify_admin_password('admin')
        d['list_db']=flectra.tools.config['list_db']
        d['langs']=flectra.service.db.exp_list_lang()
        d['countries']=flectra.service.db.exp_list_countries()
        d['pattern']=DBNAME_PATTERN
        #databaseslist
        d['databases']=[]
        try:
            d['databases']=http.db_list()
            d['incompatible_databases']=flectra.service.db.list_db_incompatible(d['databases'])
        exceptflectra.exceptions.AccessDenied:
            monodb=db_monodb()
            ifmonodb:
                d['databases']=[monodb]
        returnenv.get_template("database_manager.html").render(d)

    @http.route('/web/database/selector',type='http',auth="none")
    defselector(self,**kw):
        request._cr=None
        returnself._render_template(manage=False)

    @http.route('/web/database/manager',type='http',auth="none")
    defmanager(self,**kw):
        request._cr=None
        returnself._render_template()

    @http.route('/web/database/create',type='http',auth="none",methods=['POST'],csrf=False)
    defcreate(self,master_pwd,name,lang,password,**post):
        insecure=flectra.tools.config.verify_admin_password('admin')
        ifinsecureandmaster_pwd:
            dispatch_rpc('db','change_admin_password',["admin",master_pwd])
        try:
            ifnotre.match(DBNAME_PATTERN,name):
                raiseException(_('Invaliddatabasename.Onlyalphanumericalcharacters,underscore,hyphenanddotareallowed.'))
            #countrycodecouldbe="False"whichisactuallyTrueinpython
            country_code=post.get('country_code')orFalse
            dispatch_rpc('db','create_database',[master_pwd,name,bool(post.get('demo')),lang,password,post['login'],country_code,post['phone']])
            request.session.authenticate(name,post['login'],password)
            returnhttp.local_redirect('/web/')
        exceptExceptionase:
            error="Databasecreationerror:%s"%(str(e)orrepr(e))
        returnself._render_template(error=error)

    @http.route('/web/database/duplicate',type='http',auth="none",methods=['POST'],csrf=False)
    defduplicate(self,master_pwd,name,new_name):
        insecure=flectra.tools.config.verify_admin_password('admin')
        ifinsecureandmaster_pwd:
            dispatch_rpc('db','change_admin_password',["admin",master_pwd])
        try:
            ifnotre.match(DBNAME_PATTERN,new_name):
                raiseException(_('Invaliddatabasename.Onlyalphanumericalcharacters,underscore,hyphenanddotareallowed.'))
            dispatch_rpc('db','duplicate_database',[master_pwd,name,new_name])
            request._cr=None #duplicatingadatabaseleadstoanunusablecursor
            returnhttp.local_redirect('/web/database/manager')
        exceptExceptionase:
            error="Databaseduplicationerror:%s"%(str(e)orrepr(e))
            returnself._render_template(error=error)

    @http.route('/web/database/drop',type='http',auth="none",methods=['POST'],csrf=False)
    defdrop(self,master_pwd,name):
        insecure=flectra.tools.config.verify_admin_password('admin')
        ifinsecureandmaster_pwd:
            dispatch_rpc('db','change_admin_password',["admin",master_pwd])
        try:
            dispatch_rpc('db','drop',[master_pwd,name])
            request._cr=None #droppingadatabaseleadstoanunusablecursor
            returnhttp.local_redirect('/web/database/manager')
        exceptExceptionase:
            error="Databasedeletionerror:%s"%(str(e)orrepr(e))
            returnself._render_template(error=error)

    @http.route('/web/database/backup',type='http',auth="none",methods=['POST'],csrf=False)
    defbackup(self,master_pwd,name,backup_format='zip'):
        insecure=flectra.tools.config.verify_admin_password('admin')
        ifinsecureandmaster_pwd:
            dispatch_rpc('db','change_admin_password',["admin",master_pwd])
        try:
            flectra.service.db.check_super(master_pwd)
            ts=datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            filename="%s_%s.%s"%(name,ts,backup_format)
            headers=[
                ('Content-Type','application/octet-stream;charset=binary'),
                ('Content-Disposition',content_disposition(filename)),
            ]
            dump_stream=flectra.service.db.dump_db(name,None,backup_format)
            response=werkzeug.wrappers.Response(dump_stream,headers=headers,direct_passthrough=True)
            returnresponse
        exceptExceptionase:
            _logger.exception('Database.backup')
            error="Databasebackuperror:%s"%(str(e)orrepr(e))
            returnself._render_template(error=error)

    @http.route('/web/database/restore',type='http',auth="none",methods=['POST'],csrf=False)
    defrestore(self,master_pwd,backup_file,name,copy=False):
        insecure=flectra.tools.config.verify_admin_password('admin')
        ifinsecureandmaster_pwd:
            dispatch_rpc('db','change_admin_password',["admin",master_pwd])
        try:
            data_file=None
            db.check_super(master_pwd)
            withtempfile.NamedTemporaryFile(delete=False)asdata_file:
                backup_file.save(data_file)
            db.restore_db(name,data_file.name,str2bool(copy))
            returnhttp.local_redirect('/web/database/manager')
        exceptExceptionase:
            error="Databaserestoreerror:%s"%(str(e)orrepr(e))
            returnself._render_template(error=error)
        finally:
            ifdata_file:
                os.unlink(data_file.name)

    @http.route('/web/database/change_password',type='http',auth="none",methods=['POST'],csrf=False)
    defchange_password(self,master_pwd,master_pwd_new):
        try:
            dispatch_rpc('db','change_admin_password',[master_pwd,master_pwd_new])
            returnhttp.local_redirect('/web/database/manager')
        exceptExceptionase:
            error="Masterpasswordupdateerror:%s"%(str(e)orrepr(e))
            returnself._render_template(error=error)

    @http.route('/web/database/list',type='json',auth='none')
    deflist(self):
        """
        UsedbyMobileapplicationforlistingdatabase
        :return:Listofdatabases
        :rtype:list
        """
        returnhttp.db_list()

classSession(http.Controller):

    @http.route('/web/session/get_session_info',type='json',auth="none")
    defget_session_info(self):
        request.session.check_security()
        request.uid=request.session.uid
        returnrequest.env['ir.http'].session_info()

    @http.route('/web/session/authenticate',type='json',auth="none")
    defauthenticate(self,db,login,password,base_location=None):
        request.session.authenticate(db,login,password)
        returnrequest.env['ir.http'].session_info()

    @http.route('/web/session/change_password',type='json',auth="user")
    defchange_password(self,fields):
        old_password,new_password,confirm_password=operator.itemgetter('old_pwd','new_password','confirm_pwd')(
            {f['name']:f['value']forfinfields})
        ifnot(old_password.strip()andnew_password.strip()andconfirm_password.strip()):
            return{'error':_('Youcannotleaveanypasswordempty.'),'title':_('ChangePassword')}
        ifnew_password!=confirm_password:
            return{'error':_('Thenewpasswordanditsconfirmationmustbeidentical.'),'title':_('ChangePassword')}

        msg=_("Error,passwordnotchanged!")
        try:
            ifrequest.env['res.users'].change_password(old_password,new_password):
                return{'new_password':new_password}
        exceptAccessDeniedase:
            msg=e.args[0]
            ifmsg==AccessDenied().args[0]:
                msg=_('Theoldpasswordyouprovidedisincorrect,yourpasswordwasnotchanged.')
        exceptUserErrorase:
            msg=e.args[0]
        return{'title':_('ChangePassword'),'error':msg}

    @http.route('/web/session/get_lang_list',type='json',auth="none")
    defget_lang_list(self):
        try:
            returndispatch_rpc('db','list_lang',[])or[]
        exceptExceptionase:
            return{"error":e,"title":_("Languages")}

    @http.route('/web/session/modules',type='json',auth="user")
    defmodules(self):
        #returnallinstalledmodules.Webclientissmartenoughtonotloadamoduletwice
        returnmodule_installed(environment=request.env(user=flectra.SUPERUSER_ID))

    @http.route('/web/session/save_session_action',type='json',auth="user")
    defsave_session_action(self,the_action):
        """
        Thismethodstoreanactionobjectinthesessionobjectandreturnsaninteger
        identifyingthataction.Themethodget_session_action()canbeusedtoget
        backtheaction.

        :paramthe_action:Theactiontosaveinthesession.
        :typethe_action:anything
        :return:Akeyidentifyingthesavedaction.
        :rtype:integer
        """
        returnrequest.session.save_action(the_action)

    @http.route('/web/session/get_session_action',type='json',auth="user")
    defget_session_action(self,key):
        """
        Getsbackapreviouslysavedaction.ThismethodcanreturnNoneiftheaction
        wassavedsincetoomuchtime(thiscaseshouldbehandledinasmartway).

        :paramkey:Thekeygivenbysave_session_action()
        :typekey:integer
        :return:ThesavedactionorNone.
        :rtype:anything
        """
        returnrequest.session.get_action(key)

    @http.route('/web/session/check',type='json',auth="user")
    defcheck(self):
        request.session.check_security()
        returnNone

    @http.route('/web/session/account',type='json',auth="user")
    defaccount(self):
        ICP=request.env['ir.config_parameter'].sudo()
        params={
            'response_type':'token',
            'client_id':ICP.get_param('database.uuid')or'',
            'state':json.dumps({'d':request.db,'u':ICP.get_param('web.base.url')}),
            'scope':'userinfo',
        }
        return'https://accounts.flectrahq.com/oauth2/auth?'+url_encode(params)

    @http.route('/web/session/destroy',type='json',auth="user")
    defdestroy(self):
        request.session.logout()

    @http.route('/web/session/logout',type='http',auth="none")
    deflogout(self,redirect='/web'):
        request.session.logout(keep_db=True)
        returnwerkzeug.utils.redirect(redirect,303)


classDataSet(http.Controller):

    @http.route('/web/dataset/search_read',type='json',auth="user")
    defsearch_read(self,model,fields=False,offset=0,limit=False,domain=None,sort=None):
        returnself.do_search_read(model,fields,offset,limit,domain,sort)

    defdo_search_read(self,model,fields=False,offset=0,limit=False,domain=None,sort=None):
        """Performsasearch()followedbyaread()(ifneeded)usingthe
        providedsearchcriteria

        :paramstrmodel:thenameofthemodeltosearchon
        :paramfields:alistofthefieldstoreturnintheresultrecords
        :typefields:[str]
        :paramintoffset:fromwhichindexshouldtheresultsstartbeingreturned
        :paramintlimit:themaximumnumberofrecordstoreturn
        :paramlistdomain:thesearchdomainforthequery
        :paramlistsort:sortingdirectives
        :returns:Astructure(dict)withtwokeys:ids(alltheidsmatching
                  the(domain,context)pair)andrecords(paginatedrecords
                  matchingfieldsselectionset)
        :rtype:list
        """
        Model=request.env[model]
        returnModel.web_search_read(domain,fields,offset=offset,limit=limit,order=sort)

    @http.route('/web/dataset/load',type='json',auth="user")
    defload(self,model,id,fields):
        value={}
        r=request.env[model].browse([id]).read()
        ifr:
            value=r[0]
        return{'value':value}

    defcall_common(self,model,method,args,domain_id=None,context_id=None):
        returnself._call_kw(model,method,args,{})

    def_call_kw(self,model,method,args,kwargs):
        check_method_name(method)
        returncall_kw(request.env[model],method,args,kwargs)

    @http.route('/web/dataset/call',type='json',auth="user")
    defcall(self,model,method,args,domain_id=None,context_id=None):
        returnself._call_kw(model,method,args,{})

    @http.route(['/web/dataset/call_kw','/web/dataset/call_kw/<path:path>'],type='json',auth="user")
    defcall_kw(self,model,method,args,kwargs,path=None):
        returnself._call_kw(model,method,args,kwargs)

    @http.route('/web/dataset/call_button',type='json',auth="user")
    defcall_button(self,model,method,args,kwargs):
        action=self._call_kw(model,method,args,kwargs)
        ifisinstance(action,dict)andaction.get('type')!='':
            returnclean_action(action,env=request.env)
        returnFalse

    @http.route('/web/dataset/resequence',type='json',auth="user")
    defresequence(self,model,ids,field='sequence',offset=0):
        """Re-sequencesanumberofrecordsinthemodel,bytheirids

        There-sequencingstartsatthefirstmodelof``ids``,thesequence
        numberisincrementedbyoneaftereachrecordandstartsat``offset``

        :paramids:identifiersoftherecordstoresequence,inthenewsequenceorder
        :typeids:list(id)
        :paramstrfield:fieldusedforsequencespecification,defaultsto
                          "sequence"
        :paramintoffset:sequencenumberforfirstrecordin``ids``,allows
                           startingtheresequencingfromanarbitrarynumber,
                           defaultsto``0``
        """
        m=request.env[model]
        ifnotm.fields_get([field]):
            returnFalse
        #python2.6hasnostartparameter
        fori,recordinenumerate(m.browse(ids)):
            record.write({field:i+offset})
        returnTrue

classView(http.Controller):

    @http.route('/web/view/edit_custom',type='json',auth="user")
    defedit_custom(self,custom_id,arch):
        """
        Editacustomview

        :paramintcustom_id:theidoftheeditedcustomview
        :paramstrarch:theeditedarchofthecustomview
        :returns:dictwithacknowledgedoperation(resultsettoTrue)
        """
        custom_view=request.env['ir.ui.view.custom'].browse(custom_id)
        custom_view.write({'arch':arch})
        return{'result':True}

classBinary(http.Controller):

    @staticmethod
    defplaceholder(image='placeholder.png'):
        image_path=image.lstrip('/').split('/')if'/'inimageelse['web','static','src','img',image]
        withtools.file_open(get_resource_path(*image_path),'rb')asfd:
            returnfd.read()

    @http.route(['/web/content',
        '/web/content/<string:xmlid>',
        '/web/content/<string:xmlid>/<string:filename>',
        '/web/content/<int:id>',
        '/web/content/<int:id>/<string:filename>',
        '/web/content/<int:id>-<string:unique>',
        '/web/content/<int:id>-<string:unique>/<string:filename>',
        '/web/content/<int:id>-<string:unique>/<path:extra>/<string:filename>',
        '/web/content/<string:model>/<int:id>/<string:field>',
        '/web/content/<string:model>/<int:id>/<string:field>/<string:filename>'],type='http',auth="public")
    defcontent_common(self,xmlid=None,model='ir.attachment',id=None,field='datas',
                       filename=None,filename_field='name',unique=None,mimetype=None,
                       download=None,data=None,token=None,access_token=None,**kw):

        status,headers,content=request.env['ir.http'].binary_content(
            xmlid=xmlid,model=model,id=id,field=field,unique=unique,filename=filename,
            filename_field=filename_field,download=download,mimetype=mimetype,access_token=access_token)

        ifstatus!=200:
            returnrequest.env['ir.http']._response_by_status(status,headers,content)
        else:
            content_base64=base64.b64decode(content)
            headers.append(('Content-Length',len(content_base64)))
            response=request.make_response(content_base64,headers)
        iftoken:
            response.set_cookie('fileToken',token)
        returnresponse

    @http.route(['/web/partner_image',
        '/web/partner_image/<int:rec_id>',
        '/web/partner_image/<int:rec_id>/<string:field>',
        '/web/partner_image/<int:rec_id>/<string:field>/<string:model>/'],type='http',auth="public")
    defcontent_image_partner(self,rec_id,field='image_128',model='res.partner',**kwargs):
        #otherkwargsareignoredonpurpose
        returnself._content_image(id=rec_id,model='res.partner',field=field,
            placeholder='user_placeholder.jpg')

    @http.route(['/web/image',
        '/web/image/<string:xmlid>',
        '/web/image/<string:xmlid>/<string:filename>',
        '/web/image/<string:xmlid>/<int:width>x<int:height>',
        '/web/image/<string:xmlid>/<int:width>x<int:height>/<string:filename>',
        '/web/image/<string:model>/<int:id>/<string:field>',
        '/web/image/<string:model>/<int:id>/<string:field>/<string:filename>',
        '/web/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>',
        '/web/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>/<string:filename>',
        '/web/image/<int:id>',
        '/web/image/<int:id>/<string:filename>',
        '/web/image/<int:id>/<int:width>x<int:height>',
        '/web/image/<int:id>/<int:width>x<int:height>/<string:filename>',
        '/web/image/<int:id>-<string:unique>',
        '/web/image/<int:id>-<string:unique>/<string:filename>',
        '/web/image/<int:id>-<string:unique>/<int:width>x<int:height>',
        '/web/image/<int:id>-<string:unique>/<int:width>x<int:height>/<string:filename>'],type='http',auth="public")
    defcontent_image(self,xmlid=None,model='ir.attachment',id=None,field='datas',
                      filename_field='name',unique=None,filename=None,mimetype=None,
                      download=None,width=0,height=0,crop=False,access_token=None,
                      **kwargs):
        #otherkwargsareignoredonpurpose
        returnself._content_image(xmlid=xmlid,model=model,id=id,field=field,
            filename_field=filename_field,unique=unique,filename=filename,mimetype=mimetype,
            download=download,width=width,height=height,crop=crop,
            quality=int(kwargs.get('quality',0)),access_token=access_token)

    def_content_image(self,xmlid=None,model='ir.attachment',id=None,field='datas',
                       filename_field='name',unique=None,filename=None,mimetype=None,
                       download=None,width=0,height=0,crop=False,quality=0,access_token=None,
                       placeholder=None,**kwargs):
        status,headers,image_base64=request.env['ir.http'].binary_content(
            xmlid=xmlid,model=model,id=id,field=field,unique=unique,filename=filename,
            filename_field=filename_field,download=download,mimetype=mimetype,
            default_mimetype='image/png',access_token=access_token)

        returnBinary._content_image_get_response(
            status,headers,image_base64,model=model,id=id,field=field,download=download,
            width=width,height=height,crop=crop,quality=quality,
            placeholder=placeholder)

    @staticmethod
    def_content_image_get_response(
            status,headers,image_base64,model='ir.attachment',id=None,
            field='datas',download=None,width=0,height=0,crop=False,
            quality=0,placeholder='placeholder.png'):
        ifstatusin[301,304]or(status!=200anddownload):
            returnrequest.env['ir.http']._response_by_status(status,headers,image_base64)
        ifnotimage_base64:
            ifplaceholderisNoneandmodelinrequest.env:
                #Trytobrowsetherecordincaseaspecificplaceholder
                #issupposedtobeused.(eg:Unassignedusersonatask)
                record=request.env[model].browse(int(id))ifidelserequest.env[model]
                placeholder_filename=record._get_placeholder_filename(field=field)
                placeholder_content=Binary.placeholder(image=placeholder_filename)
            else:
                placeholder_content=Binary.placeholder()
            #Sincewesetaplaceholderforanymissingimage,thestatusmustbe200.Incaseone
            #wantstoconfigureaspecific404page(e.g.thoughnginx),a404statuswillcause
            #troubles.
            status=200
            image_base64=base64.b64encode(placeholder_content)

            ifnot(widthorheight):
                width,height=flectra.tools.image_guess_size_from_field_name(field)

        try:
            image_base64=image_process(image_base64,size=(int(width),int(height)),crop=crop,quality=int(quality))
        exceptException:
            returnrequest.not_found()

        content=base64.b64decode(image_base64)
        headers=http.set_safe_image_headers(headers,content)
        response=request.make_response(content,headers)
        response.status_code=status
        returnresponse

    #backwardcompatibility
    @http.route(['/web/binary/image'],type='http',auth="public")
    defcontent_image_backward_compatibility(self,model,id,field,resize=None,**kw):
        width=None
        height=None
        ifresize:
            width,height=resize.split(",")
        returnself.content_image(model=model,id=id,field=field,width=width,height=height)


    @http.route('/web/binary/upload',type='http',auth="user")
    @serialize_exception
    defupload(self,ufile,callback=None):
        #TODO:mightbeusefultohaveaconfigurationflagformax-lengthfileuploads
        out="""<scriptlanguage="javascript"type="text/javascript">
                    varwin=window.top.window;
                    win.jQuery(win).trigger(%s,%s);
                </script>"""
        try:
            data=ufile.read()
            args=[len(data),ufile.filename,
                    ufile.content_type,pycompat.to_text(base64.b64encode(data))]
        exceptExceptionase:
            args=[False,str(e)]
        returnout%(json.dumps(clean(callback)),json.dumps(args))ifcallbackelsejson.dumps(args)

    @http.route('/web/binary/upload_attachment',type='http',auth="user")
    @serialize_exception
    defupload_attachment(self,model,id,ufile,callback=None):
        files=request.httprequest.files.getlist('ufile')
        Model=request.env['ir.attachment']
        out="""<scriptlanguage="javascript"type="text/javascript">
                    varwin=window.top.window;
                    win.jQuery(win).trigger(%s,%s);
                </script>"""
        args=[]
        forufileinfiles:

            filename=ufile.filename
            ifrequest.httprequest.user_agent.browser=='safari':
                #SafarisendsNFDUTF-8(whereéiscomposedby'e'and[accent])
                #weneedtosenditthesamestuff,otherwiseit'llfail
                filename=unicodedata.normalize('NFD',ufile.filename)

            try:
                attachment=Model.create({
                    'name':filename,
                    'datas':base64.encodebytes(ufile.read()),
                    'res_model':model,
                    'res_id':int(id)
                })
                attachment._post_add_create()
            exceptAccessError:
                args.append({'error':_("Youarenotallowedtouploadanattachmenthere.")})
            exceptException:
                args.append({'error':_("Somethinghorriblehappened")})
                _logger.exception("Failtouploadattachment%s"%ufile.filename)
            else:
                args.append({
                    'filename':clean(filename),
                    'mimetype':ufile.content_type,
                    'id':attachment.id,
                    'size':attachment.file_size
                })
        returnout%(json.dumps(clean(callback)),json.dumps(args))ifcallbackelsejson.dumps(args)

    @http.route([
        '/web/binary/company_logo',
        '/logo',
        '/logo.png',
    ],type='http',auth="none",cors="*")
    defcompany_logo(self,dbname=None,**kw):
        imgname='logo'
        imgext='.png'
        placeholder=functools.partial(get_resource_path,'web','static','src','img')
        uid=None
        ifrequest.session.db:
            dbname=request.session.db
            uid=request.session.uid
        elifdbnameisNone:
            dbname=db_monodb()

        ifnotuid:
            uid=flectra.SUPERUSER_ID

        ifnotdbname:
            response=http.send_file(placeholder(imgname+imgext))
        else:
            try:
                #createanemptyregistry
                registry=flectra.modules.registry.Registry(dbname)
                withregistry.cursor()ascr:
                    company=int(kw['company'])ifkwandkw.get('company')elseFalse
                    ifcompany:
                        cr.execute("""SELECTlogo_web,write_date
                                        FROMres_company
                                       WHEREid=%s
                                   """,(company,))
                    else:
                        cr.execute("""SELECTc.logo_web,c.write_date
                                        FROMres_usersu
                                   LEFTJOINres_companyc
                                          ONc.id=u.company_id
                                       WHEREu.id=%s
                                   """,(uid,))
                    row=cr.fetchone()
                    ifrowandrow[0]:
                        image_base64=base64.b64decode(row[0])
                        image_data=io.BytesIO(image_base64)
                        mimetype=guess_mimetype(image_base64,default='image/png')
                        imgext='.'+mimetype.split('/')[1]
                        ifimgext=='.svg+xml':
                            imgext='.svg'
                        response=http.send_file(image_data,filename=imgname+imgext,mimetype=mimetype,mtime=row[1])
                    else:
                        response=http.send_file(placeholder('nologo.png'))
            exceptException:
                response=http.send_file(placeholder(imgname+imgext))

        returnresponse

    @http.route(['/web/sign/get_fonts','/web/sign/get_fonts/<string:fontname>'],type='json',auth='public')
    defget_fonts(self,fontname=None):
        """Thisroutewillreturnalistofbase64encodedfonts.

        Thosefontswillbeproposedtotheuserwhencreatingasignature
        usingmode'auto'.

        :return:base64encodedfonts
        :rtype:list
        """


        fonts=[]
        iffontname:
            module_path=get_module_path('web')
            fonts_folder_path=os.path.join(module_path,'static/src/fonts/sign/')
            module_resource_path=get_resource_path('web','static/src/fonts/sign/'+fontname)
            iffonts_folder_pathandmodule_resource_path:
                fonts_folder_path=os.path.join(os.path.normpath(fonts_folder_path),'')
                module_resource_path=os.path.normpath(module_resource_path)
                ifmodule_resource_path.startswith(fonts_folder_path):
                    withfile_open(module_resource_path,'rb')asfont_file:
                        font=base64.b64encode(font_file.read())
                        fonts.append(font)
        else:
            current_dir=os.path.dirname(os.path.abspath(__file__))
            fonts_directory=os.path.join(current_dir,'..','static','src','fonts','sign')
            font_filenames=sorted([fnforfninos.listdir(fonts_directory)iffn.endswith(('.ttf','.otf','.woff','.woff2'))])

            forfilenameinfont_filenames:
                font_file=open(os.path.join(fonts_directory,filename),'rb')
                font=base64.b64encode(font_file.read())
                fonts.append(font)
        returnfonts

classAction(http.Controller):

    @http.route('/web/action/load',type='json',auth="user")
    defload(self,action_id,additional_context=None):
        Actions=request.env['ir.actions.actions']
        value=False
        try:
            action_id=int(action_id)
        exceptValueError:
            try:
                action=request.env.ref(action_id)
                assertaction._name.startswith('ir.actions.')
                action_id=action.id
            exceptException:
                action_id=0  #forcefailedread

        base_action=Actions.browse([action_id]).sudo().read(['type'])
        ifbase_action:
            ctx=dict(request.context)
            action_type=base_action[0]['type']
            ifaction_type=='ir.actions.report':
                ctx.update({'bin_size':True})
            ifadditional_context:
                ctx.update(additional_context)
            request.context=ctx
            action=request.env[action_type].sudo().browse([action_id]).read()
            ifaction:
                value=clean_action(action[0],env=request.env)
        returnvalue

    @http.route('/web/action/run',type='json',auth="user")
    defrun(self,action_id):
        action=request.env['ir.actions.server'].browse([action_id])
        result=action.run()
        returnclean_action(result,env=action.env)ifresultelseFalse

classExport(http.Controller):

    @http.route('/web/export/formats',type='json',auth="user")
    defformats(self):
        """Returnsallvalidexportformats

        :returns:foreachexportformat,apairofidentifierandprintablename
        :rtype:[(str,str)]
        """
        return[
            {'tag':'xlsx','label':'XLSX','error':Noneifxlsxwriterelse"XlsxWriter0.9.3required"},
            {'tag':'csv','label':'CSV'},
        ]

    deffields_get(self,model):
        Model=request.env[model]
        fields=Model.fields_get()
        returnfields

    @http.route('/web/export/get_fields',type='json',auth="user")
    defget_fields(self,model,prefix='',parent_name='',
                   import_compat=True,parent_field_type=None,
                   parent_field=None,exclude=None):

        fields=self.fields_get(model)
        ifimport_compat:
            ifparent_field_typein['many2one','many2many']:
                rec_name=request.env[model]._rec_name_fallback()
                fields={'id':fields['id'],rec_name:fields[rec_name]}
        else:
            fields['.id']={**fields['id']}

        fields['id']['string']=_('ExternalID')

        ifparent_field:
            parent_field['string']=_('ExternalID')
            fields['id']=parent_field

        fields_sequence=sorted(fields.items(),
            key=lambdafield:flectra.tools.ustr(field[1].get('string','').lower()))

        records=[]
        forfield_name,fieldinfields_sequence:
            ifimport_compatandnotfield_name=='id':
                ifexcludeandfield_nameinexclude:
                    continue
                iffield.get('readonly'):
                    #Ifnoneofthefield'sstatesunsetsreadonly,skipthefield
                    ifall(dict(attrs).get('readonly',True)
                           forattrsinfield.get('states',{}).values()):
                        continue
            ifnotfield.get('exportable',True):
                continue

            id=prefix+(prefixand'/'or'')+field_name
            val=id
            iffield_name=='name'andimport_compatandparent_field_typein['many2one','many2many']:
                #Addnamefieldwhenexpandm2oandm2mfieldsinimport-compatiblemode
                val=prefix
            name=parent_name+(parent_nameand'/'or'')+field['string']
            record={'id':id,'string':name,
                      'value':val,'children':False,
                      'field_type':field.get('type'),
                      'required':field.get('required'),
                      'relation_field':field.get('relation_field')}
            records.append(record)

            iflen(id.split('/'))<3and'relation'infield:
                ref=field.pop('relation')
                record['value']+='/id'
                record['params']={'model':ref,'prefix':id,'name':name,'parent_field':field}
                record['children']=True

        returnrecords

    @http.route('/web/export/namelist',type='json',auth="user")
    defnamelist(self,model,export_id):
        #TODO:namelistreallyhasnoreasontobeinPython(althoughitertools.groupbyhelps)
        export=request.env['ir.exports'].browse([export_id]).read()[0]
        export_fields_list=request.env['ir.exports.line'].browse(export['export_fields']).read()

        fields_data=self.fields_info(
            model,[f['name']forfinexport_fields_list])

        return[
            {'name':field['name'],'label':fields_data[field['name']]}
            forfieldinexport_fields_list
        ]

    deffields_info(self,model,export_fields):
        info={}
        fields=self.fields_get(model)
        if".id"inexport_fields:
            fields['.id']=fields.get('id',{'string':'ID'})

        #Tomakefieldsretrievalmoreefficient,fetchallsub-fieldsofa
        #givenfieldatthesametime.Becausetheorderintheexportlistis
        #arbitrary,thisrequiresorderingallsub-fieldsofagivenfield
        #togethersotheycanbefetchedatthesametime
        #
        #Worksthefollowingway:
        #*sortthelistoffieldstoexport,thedefaultsortingorderwill
        #  putthefielditself(ifpresent,forxmlid)andallofits
        #  sub-fieldsrightafterit
        #*then,groupon:thefirstfieldofthepath(whichisthesamefor
        #  afieldandforitssubfieldsandthelengthofsplittingonthe
        #  first'/',whichbasicallymeansgroupingthefieldononesideand
        #  allofthesubfieldsontheother.Thisway,wehavethefield(for
        #  thexmlid)withlength1,andallofthesubfieldswiththesame
        #  basebutalength"flag"of2
        #*ifwehaveanormalfield(length1),justaddittotheinfo
        #  mapping(withitsstring)as-is
        #*otherwise,recursivelycallfields_infoviagraft_subfields.
        #  allgraft_subfieldsdoesistaketheresultoffields_info(onthe
        #  field'smodel)andprependthecurrentbase(currentfield),which
        #  rebuildsthewholesub-treeforthefield
        #
        #result:becausewe'renotfetchingthefields_getforhalfthe
        #databasemodels,fetchinganamelistwithadozenfields(including
        #relationaldata)fallsfrom~6sto~300ms(ontheleadsmodel).
        #exportlistswithnosub-fields(e.g.import_compatiblelistswith
        #noo2m)areevenmoreefficient(fromthesame6sto~170ms,as
        #there'sasinglefields_gettoexecute)
        for(base,length),subfieldsinitertools.groupby(
                sorted(export_fields),
                lambdafield:(field.split('/',1)[0],len(field.split('/',1)))):
            subfields=list(subfields)
            iflength==2:
                #subfieldsisaseqof$base/*rest,andnotloadedyet
                info.update(self.graft_subfields(
                    fields[base]['relation'],base,fields[base]['string'],
                    subfields
                ))
            elifbaseinfields:
                info[base]=fields[base]['string']

        returninfo

    defgraft_subfields(self,model,prefix,prefix_string,fields):
        export_fields=[field.split('/',1)[1]forfieldinfields]
        return(
            (prefix+'/'+k,prefix_string+'/'+v)
            fork,vinself.fields_info(model,export_fields).items())

classExportFormat(object):

    @property
    defcontent_type(self):
        """Providestheformat'scontenttype"""
        raiseNotImplementedError()

    deffilename(self,base):
        """Createsavalidfilenamefortheformat(withextension)fromthe
         providedbasename(exension-less)
        """
        raiseNotImplementedError()

    deffrom_data(self,fields,rows):
        """ConversionmethodfromFlectra'sexportdatatowhateverthe
        currentexportclassoutputs

        :paramslistfields:alistoffieldstoexport
        :paramslistrows:alistofrecordstoexport
        :returns:
        :rtype:bytes
        """
        raiseNotImplementedError()

    deffrom_group_data(self,fields,groups):
        raiseNotImplementedError()

    defbase(self,data,token):
        params=json.loads(data)
        model,fields,ids,domain,import_compat=\
            operator.itemgetter('model','fields','ids','domain','import_compat')(params)

        Model=request.env[model].with_context(import_compat=import_compat,**params.get('context',{}))
        ifnotModel._is_an_ordinary_table():
            fields=[fieldforfieldinfieldsiffield['name']!='id']

        field_names=[f['name']forfinfields]
        ifimport_compat:
            columns_headers=field_names
        else:
            columns_headers=[val['label'].strip()forvalinfields]

        groupby=params.get('groupby')
        ifnotimport_compatandgroupby:
            groupby_type=[Model._fields[x.split(':')[0]].typeforxingroupby]
            domain=[('id','in',ids)]ifidselsedomain
            groups_data=Model.read_group(domain,[xifx!='.id'else'id'forxinfield_names],groupby,lazy=False)

            #read_group(lazy=False)returnsadictonlyforfinalgroups(withactualdata),
            #notforintermediarygroups.Thefullgrouptreemustbere-constructed.
            tree=GroupsTreeNode(Model,field_names,groupby,groupby_type)
            forleafingroups_data:
                tree.insert_leaf(leaf)

            response_data=self.from_group_data(fields,tree)
        else:
            records=Model.browse(ids)ifidselseModel.search(domain,offset=0,limit=False,order=False)

            export_data=records.export_data(field_names).get('datas',[])
            response_data=self.from_data(columns_headers,export_data)

        returnrequest.make_response(response_data,
            headers=[('Content-Disposition',
                            content_disposition(self.filename(model))),
                     ('Content-Type',self.content_type)],
            cookies={'fileToken':token})

classCSVExport(ExportFormat,http.Controller):

    @http.route('/web/export/csv',type='http',auth="user")
    @serialize_exception
    defindex(self,data,token):
        returnself.base(data,token)

    @property
    defcontent_type(self):
        return'text/csv;charset=utf8'

    deffilename(self,base):
        returnbase+'.csv'

    deffrom_group_data(self,fields,groups):
        raiseUserError(_("Exportinggroupeddatatocsvisnotsupported."))

    deffrom_data(self,fields,rows):
        fp=io.BytesIO()
        writer=pycompat.csv_writer(fp,quoting=1)

        writer.writerow(fields)

        fordatainrows:
            row=[]
            fordindata:
                #Spreadsheetappstendtodetectformulasonleading=,+and-
                ifisinstance(d,str)andd.startswith(('=','-','+')):
                    d="'"+d

                row.append(pycompat.to_text(d))
            writer.writerow(row)

        returnfp.getvalue()

classExcelExport(ExportFormat,http.Controller):

    @http.route('/web/export/xlsx',type='http',auth="user")
    @serialize_exception
    defindex(self,data,token):
        returnself.base(data,token)

    @property
    defcontent_type(self):
        return'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    deffilename(self,base):
        returnbase+'.xlsx'

    deffrom_group_data(self,fields,groups):
        withGroupExportXlsxWriter(fields,groups.count)asxlsx_writer:
            x,y=1,0
            forgroup_name,groupingroups.children.items():
                x,y=xlsx_writer.write_group(x,y,group_name,group)

        returnxlsx_writer.value

    deffrom_data(self,fields,rows):
        withExportXlsxWriter(fields,len(rows))asxlsx_writer:
            forrow_index,rowinenumerate(rows):
                forcell_index,cell_valueinenumerate(row):
                    ifisinstance(cell_value,(list,tuple)):
                        cell_value=pycompat.to_text(cell_value)
                    xlsx_writer.write_cell(row_index+1,cell_index,cell_value)

        returnxlsx_writer.value


classReportController(http.Controller):

    #------------------------------------------------------
    #Reportcontrollers
    #------------------------------------------------------
    @http.route([
        '/report/<converter>/<reportname>',
        '/report/<converter>/<reportname>/<docids>',
    ],type='http',auth='user',website=True)
    defreport_routes(self,reportname,docids=None,converter=None,**data):
        report=request.env['ir.actions.report']._get_report_from_name(reportname)
        context=dict(request.env.context)

        ifdocids:
            docids=[int(i)foriindocids.split(',')]
        ifdata.get('options'):
            data.update(json.loads(data.pop('options')))
        ifdata.get('context'):
            #Ignore'lang'here,becausethecontextindataistheonefromthewebclient*but*if
            #theuserexplicitelywantstochangethelang,thismechanismoverwritesit.
            data['context']=json.loads(data['context'])
            ifdata['context'].get('lang')andnotdata.get('force_context_lang'):
                deldata['context']['lang']
            context.update(data['context'])
        ifconverter=='html':
            html=report.with_context(context)._render_qweb_html(docids,data=data)[0]
            returnrequest.make_response(html)
        elifconverter=='pdf':
            pdf=report.with_context(context)._render_qweb_pdf(docids,data=data)[0]
            pdfhttpheaders=[('Content-Type','application/pdf'),('Content-Length',len(pdf))]
            returnrequest.make_response(pdf,headers=pdfhttpheaders)
        elifconverter=='text':
            text=report.with_context(context)._render_qweb_text(docids,data=data)[0]
            texthttpheaders=[('Content-Type','text/plain'),('Content-Length',len(text))]
            returnrequest.make_response(text,headers=texthttpheaders)
        else:
            raisewerkzeug.exceptions.HTTPException(description='Converter%snotimplemented.'%converter)

    #------------------------------------------------------
    #Misc.routeutils
    #------------------------------------------------------
    @http.route(['/report/barcode','/report/barcode/<type>/<path:value>'],type='http',auth="public")
    defreport_barcode(self,type,value,**kwargs):
        """Contollerabletorenderbarcodeimagesthankstoreportlab.
        Samples::

            <imgt-att-src="'/report/barcode/QR/%s'%o.name"/>
            <imgt-att-src="'/report/barcode/?type=%s&amp;value=%s&amp;width=%s&amp;height=%s'%
                ('QR',o.name,200,200)"/>

        :paramtype:Acceptedtypes:'Codabar','Code11','Code128','EAN13','EAN8','Extended39',
        'Extended93','FIM','I2of5','MSI','POSTNET','QR','Standard39','Standard93',
        'UPCA','USPS_4State'
        :paramwidth:Pixelwidthofthebarcode
        :paramheight:Pixelheightofthebarcode
        :paramhumanreadable:Acceptedvalues:0(default)or1.1willinsertthereadablevalue
        atthebottomoftheoutputimage
        :paramquiet:Acceptedvalues:0(default)or1.1willdisplaywhite
        marginsonleftandright.
        :parammask:ThemaskcodetobeusedwhenrenderingthisQR-code.
                     Masksallowaddingelementsontopofthegeneratedimage,
                     suchastheSwisscrossinthecenterofQR-billcodes.
        :parambarLevel:QRcodeErrorCorrectionLevels.Defaultis'L'.
        ref:https://hg.reportlab.com/hg-public/reportlab/file/830157489e00/src/reportlab/graphics/barcode/qr.py#l101
        """
        try:
            barcode=request.env['ir.actions.report'].barcode(type,value,**kwargs)
        except(ValueError,AttributeError):
            raisewerkzeug.exceptions.HTTPException(description='Cannotconvertintobarcode.')

        returnrequest.make_response(barcode,headers=[('Content-Type','image/png')])

    @http.route(['/report/download'],type='http',auth="user")
    defreport_download(self,data,token,context=None):
        """Thisfunctionisusedby'action_manager_report.js'inordertotriggerthedownloadof
        apdf/controllerreport.

        :paramdata:ajavascriptarrayJSON.stringifiedcontaingreportinternalurl([0])and
        type[1]
        :returns:Responsewithafiletokencookieandanattachmentheader
        """
        requestcontent=json.loads(data)
        url,type=requestcontent[0],requestcontent[1]
        try:
            iftypein['qweb-pdf','qweb-text']:
                converter='pdf'iftype=='qweb-pdf'else'text'
                extension='pdf'iftype=='qweb-pdf'else'txt'

                pattern='/report/pdf/'iftype=='qweb-pdf'else'/report/text/'
                reportname=url.split(pattern)[1].split('?')[0]

                docids=None
                if'/'inreportname:
                    reportname,docids=reportname.split('/')

                ifdocids:
                    #Genericreport:
                    response=self.report_routes(reportname,docids=docids,converter=converter,context=context)
                else:
                    #Particularreport:
                    data=dict(url_decode(url.split('?')[1]).items()) #decodingtheargsrepresentedinJSON
                    if'context'indata:
                        context,data_context=json.loads(contextor'{}'),json.loads(data.pop('context'))
                        context=json.dumps({**context,**data_context})
                    response=self.report_routes(reportname,converter=converter,context=context,**data)

                report=request.env['ir.actions.report']._get_report_from_name(reportname)
                filename="%s.%s"%(report.name,extension)

                ifdocids:
                    ids=[int(x)forxindocids.split(",")]
                    obj=request.env[report.model].browse(ids)
                    ifreport.print_report_nameandnotlen(obj)>1:
                        report_name=safe_eval(report.print_report_name,{'object':obj,'time':time})
                        filename="%s.%s"%(report_name,extension)
                response.headers.add('Content-Disposition',content_disposition(filename))
                response.set_cookie('fileToken',token)
                returnresponse
            else:
                return
        exceptExceptionase:
            se=_serialize_exception(e)
            error={
                'code':200,
                'message':"FlectraServerError",
                'data':se
            }
            res=request.make_response(html_escape(json.dumps(error)))
            raisewerkzeug.exceptions.InternalServerError(response=res)frome

    @http.route(['/report/check_wkhtmltopdf'],type='json',auth="user")
    defcheck_wkhtmltopdf(self):
        returnrequest.env['ir.actions.report'].get_wkhtmltopdf_state()
