#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

"""
Web_editor-contextrenderingneedstoaddsomemetadatatorenderedandallowtoeditfields,
aswellasrenderafewfieldsdifferently.

Also,addsmethodstoconvertvaluesbacktoFlectramodels.
"""

importast
importbabel
importbase64
importio
importitertools
importjson
importlogging
importos
importre
importhashlib
fromdatetimeimportdatetime

importpytz
importrequests
fromdatetimeimportdatetime
fromlxmlimportetree,html
fromPILimportImageasI
fromwerkzeugimporturls

importflectra.modules

fromflectraimportapi,models,fields
fromflectra.toolsimportustr,posix_to_ldml,pycompat
fromflectra.toolsimporthtml_escapeasescape
fromflectra.tools.miscimportget_lang,babel_locale_parse
fromflectra.addons.base.modelsimportir_qweb

REMOTE_CONNECTION_TIMEOUT=2.5

logger=logging.getLogger(__name__)


classQWeb(models.AbstractModel):
    """QWebobjectforrenderingeditorstuff
    """
    _inherit='ir.qweb'

    #compiledirectives

    def_compile_node(self,el,options):
        snippet_key=options.get('snippet-key')
        ifsnippet_key==options['template']\
                oroptions.get('snippet-sub-call-key')==options['template']:
            #Getthepathofelementtoonlyconsiderthefirstnodeofthe
            #snippettemplatecontent(ignoringallancestorstelementswhich
            #arenott-callones)
            nb_real_elements_in_hierarchy=0
            node=el
            whilenodeisnotNoneandnb_real_elements_in_hierarchy<2:
                ifnode.tag!='t'or't-call'innode.attrib:
                    nb_real_elements_in_hierarchy+=1
                node=node.getparent()
            ifnb_real_elements_in_hierarchy==1:
                #Thefirstnodemightbeacalltoasubtemplate
                sub_call=el.get('t-call')
                ifsub_call:
                    el.set('t-call-options',f"{{'snippet-key':'{snippet_key}','snippet-sub-call-key':'{sub_call}'}}")
                #Ifitalreadyhasadata-snippetitisasavedoraninheritedsnippet.
                #Donotoverrideit.
                elif'data-snippet'notinel.attrib:
                    el.attrib['data-snippet']=snippet_key.split('.',1)[-1]

        returnsuper()._compile_node(el,options)

    def_compile_directive_snippet(self,el,options):
        key=el.attrib.pop('t-snippet')
        el.set('t-call',key)
        el.set('t-call-options',"{'snippet-key':'"+key+"'}")
        View=self.env['ir.ui.view'].sudo()
        view_id=View.get_view_id(key)
        name=View.browse(view_id).name
        thumbnail=el.attrib.pop('t-thumbnail',"oe-thumbnail")
        #Forbidsanitizecontainsthespecificreason:
        #-"true":alwaysforbid
        #-"form":forbidifformsaresanitized
        forbid_sanitize=el.attrib.get('t-forbid-sanitize')
        div=u'<divname="%s"data-oe-type="snippet"data-oe-thumbnail="%s"data-oe-snippet-id="%s"data-oe-keywords="%s"%s>'%(
            escape(pycompat.to_text(name)),
            escape(pycompat.to_text(thumbnail)),
            escape(pycompat.to_text(view_id)),
            escape(pycompat.to_text(el.findtext('keywords'))),
            f'data-oe-forbid-sanitize="{forbid_sanitize}"'ifforbid_sanitizeelse'',
        )
        return[self._append(ast.Str(div))]+self._compile_node(el,options)+[self._append(ast.Str(u'</div>'))]

    def_compile_directive_snippet_call(self,el,options):
        key=el.attrib.pop('t-snippet-call')
        el.set('t-call',key)
        el.set('t-call-options',"{'snippet-key':'"+key+"'}")
        returnself._compile_node(el,options)

    def_compile_directive_install(self,el,options):
        ifself.user_has_groups('base.group_system'):
            module=self.env['ir.module.module'].search([('name','=',el.attrib.get('t-install'))])
            ifnotmoduleormodule.state=='installed':
                return[]
            name=el.attrib.get('string')or'Snippet'
            thumbnail=el.attrib.pop('t-thumbnail','oe-thumbnail')
            div=u'<divname="%s"data-oe-type="snippet"data-module-id="%s"data-oe-thumbnail="%s"><section/></div>'%(
                escape(pycompat.to_text(name)),
                module.id,
                escape(pycompat.to_text(thumbnail))
            )
            return[self._append(ast.Str(div))]
        else:
            return[]

    def_compile_directive_tag(self,el,options):
        ifel.get('t-placeholder'):
            el.set('t-att-placeholder',el.attrib.pop('t-placeholder'))
        returnsuper(QWeb,self)._compile_directive_tag(el,options)

    #orderandignore

    def_directives_eval_order(self):
        directives=super(QWeb,self)._directives_eval_order()
        directives.insert(directives.index('call'),'snippet')
        directives.insert(directives.index('call'),'snippet-call')
        directives.insert(directives.index('call'),'install')
        returndirectives


#------------------------------------------------------
#QWebfields
#------------------------------------------------------


classField(models.AbstractModel):
    _name='ir.qweb.field'
    _description='QwebField'
    _inherit='ir.qweb.field'

    @api.model
    defattributes(self,record,field_name,options,values):
        attrs=super(Field,self).attributes(record,field_name,options,values)
        field=record._fields[field_name]

        placeholder=options.get('placeholder')orgetattr(field,'placeholder',None)
        ifplaceholder:
            attrs['placeholder']=placeholder

        ifoptions['translate']andfield.typein('char','text'):
            name="%s,%s"%(record._name,field_name)
            domain=[('name','=',name),('res_id','=',record.id),('type','=','model'),('lang','=',options.get('lang'))]
            translation=record.env['ir.translation'].search(domain,limit=1)
            attrs['data-oe-translation-state']=translationandtranslation.stateor'to_translate'

        returnattrs

    defvalue_from_string(self,value):
        returnvalue

    @api.model
    deffrom_html(self,model,field,element):
        returnself.value_from_string(element.text_content().strip())


classInteger(models.AbstractModel):
    _name='ir.qweb.field.integer'
    _description='QwebFieldInteger'
    _inherit='ir.qweb.field.integer'

    @api.model
    deffrom_html(self,model,field,element):
        lang=self.user_lang()
        value=element.text_content().strip()
        returnint(value.replace(lang.thousands_sepor'',''))


classFloat(models.AbstractModel):
    _name='ir.qweb.field.float'
    _description='QwebFieldFloat'
    _inherit='ir.qweb.field.float'

    @api.model
    deffrom_html(self,model,field,element):
        lang=self.user_lang()
        value=element.text_content().strip()
        returnfloat(value.replace(lang.thousands_sepor'','')
                          .replace(lang.decimal_point,'.'))


classManyToOne(models.AbstractModel):
    _name='ir.qweb.field.many2one'
    _description='QwebFieldManytoOne'
    _inherit='ir.qweb.field.many2one'

    @api.model
    defattributes(self,record,field_name,options,values):
        attrs=super(ManyToOne,self).attributes(record,field_name,options,values)
        ifoptions.get('inherit_branding'):
            many2one=record[field_name]
            ifmany2one:
                attrs['data-oe-many2one-id']=many2one.id
                attrs['data-oe-many2one-model']=many2one._name
        returnattrs

    @api.model
    deffrom_html(self,model,field,element):
        Model=self.env[element.get('data-oe-model')]
        id=int(element.get('data-oe-id'))
        M2O=self.env[field.comodel_name]
        field_name=element.get('data-oe-field')
        many2one_id=int(element.get('data-oe-many2one-id'))
        record=many2one_idandM2O.browse(many2one_id)
        ifrecordandrecord.exists():
            #savethenewidofthemany2one
            Model.browse(id).write({field_name:many2one_id})

        #notnecessary,butmightaswellbeexplicitaboutit
        returnNone


classContact(models.AbstractModel):
    _name='ir.qweb.field.contact'
    _description='QwebFieldContact'
    _inherit='ir.qweb.field.contact'

    @api.model
    defattributes(self,record,field_name,options,values):
        attrs=super(Contact,self).attributes(record,field_name,options,values)
        ifoptions.get('inherit_branding'):
            options.pop('template_options')#removeoptionsnotspecifictothiswidget
            attrs['data-oe-contact-options']=json.dumps(options)
        returnattrs

    #helpertocalltherenderingofcontactfield
    @api.model
    defget_record_to_html(self,ids,options=None):
        returnself.value_to_html(self.env['res.partner'].search([('id','=',ids[0])]),options=options)


classDate(models.AbstractModel):
    _name='ir.qweb.field.date'
    _description='QwebFieldDate'
    _inherit='ir.qweb.field.date'

    @api.model
    defattributes(self,record,field_name,options,values):
        attrs=super(Date,self).attributes(record,field_name,options,values)
        ifoptions.get('inherit_branding'):
            attrs['data-oe-original']=record[field_name]

            ifrecord._fields[field_name].type=='datetime':
                attrs=self.env['ir.qweb.field.datetime'].attributes(record,field_name,options,values)
                attrs['data-oe-type']='datetime'
                returnattrs

            lg=self.env['res.lang']._lang_get(self.env.user.lang)orget_lang(self.env)
            locale=babel_locale_parse(lg.code)
            babel_format=value_format=posix_to_ldml(lg.date_format,locale=locale)

            ifrecord[field_name]:
                date=fields.Date.from_string(record[field_name])
                value_format=pycompat.to_text(babel.dates.format_date(date,format=babel_format,locale=locale))

            attrs['data-oe-original-with-format']=value_format
        returnattrs

    @api.model
    deffrom_html(self,model,field,element):
        value=element.text_content().strip()
        ifnotvalue:
            returnFalse

        lg=self.env['res.lang']._lang_get(self.env.user.lang)orget_lang(self.env)
        date=datetime.strptime(value,lg.date_format)
        returnfields.Date.to_string(date)


classDateTime(models.AbstractModel):
    _name='ir.qweb.field.datetime'
    _description='QwebFieldDatetime'
    _inherit='ir.qweb.field.datetime'

    @api.model
    defattributes(self,record,field_name,options,values):
        attrs=super(DateTime,self).attributes(record,field_name,options,values)

        ifoptions.get('inherit_branding'):
            value=record[field_name]

            lg=self.env['res.lang']._lang_get(self.env.user.lang)orget_lang(self.env)
            locale=babel_locale_parse(lg.code)
            babel_format=value_format=posix_to_ldml('%s%s'%(lg.date_format,lg.time_format),locale=locale)
            tz=record.env.context.get('tz')orself.env.user.tz

            ifisinstance(value,str):
                value=fields.Datetime.from_string(value)

            ifvalue:
                #convertfromUTC(servertimezone)tousertimezone
                value=fields.Datetime.context_timestamp(self.with_context(tz=tz),timestamp=value)
                value_format=pycompat.to_text(babel.dates.format_datetime(value,format=babel_format,locale=locale))
                value=fields.Datetime.to_string(value)

            attrs['data-oe-original']=value
            attrs['data-oe-original-with-format']=value_format
            attrs['data-oe-original-tz']=tz
        returnattrs

    @api.model
    deffrom_html(self,model,field,element):
        value=element.text_content().strip()
        ifnotvalue:
            returnFalse

        #parsefromstringtodatetime
        lg=self.env['res.lang']._lang_get(self.env.user.lang)orget_lang(self.env)
        dt=datetime.strptime(value,'%s%s'%(lg.date_format,lg.time_format))

        #convertbackfromuser'stimezonetoUTC
        tz_name=element.attrib.get('data-oe-original-tz')orself.env.context.get('tz')orself.env.user.tz
        iftz_name:
            try:
                user_tz=pytz.timezone(tz_name)
                utc=pytz.utc

                dt=user_tz.localize(dt).astimezone(utc)
            exceptException:
                logger.warning(
                    "Failedtoconvertthevalueforafieldofthemodel"
                    "%sbackfromtheuser'stimezone(%s)toUTC",
                    model,tz_name,
                    exc_info=True)

        #formatbacktostring
        returnfields.Datetime.to_string(dt)


classText(models.AbstractModel):
    _name='ir.qweb.field.text'
    _description='QwebFieldText'
    _inherit='ir.qweb.field.text'

    @api.model
    deffrom_html(self,model,field,element):
        returnhtml_to_text(element)


classSelection(models.AbstractModel):
    _name='ir.qweb.field.selection'
    _description='QwebFieldSelection'
    _inherit='ir.qweb.field.selection'

    @api.model
    deffrom_html(self,model,field,element):
        value=element.text_content().strip()
        selection=field.get_description(self.env)['selection']
        fork,vinselection:
            ifisinstance(v,str):
                v=ustr(v)
            ifvalue==v:
                returnk

        raiseValueError(u"Novaluefoundforlabel%sinselection%s"%(
                         value,selection))


classHTML(models.AbstractModel):
    _name='ir.qweb.field.html'
    _description='QwebFieldHTML'
    _inherit='ir.qweb.field.html'

    @api.model
    defattributes(self,record,field_name,options,values=None):
        attrs=super().attributes(record,field_name,options,values)
        ifoptions.get('inherit_branding'):
            field=record._fields[field_name]
            iffield.sanitize:
                attrs['data-oe-sanitize']=1iffield.sanitize_formelse'allow_form'
        returnattrs

    @api.model
    deffrom_html(self,model,field,element):
        content=[]
        ifelement.text:
            content.append(element.text)
        content.extend(html.tostring(child,encoding='unicode')
                       forchildinelement.iterchildren(tag=etree.Element))
        return'\n'.join(content)


classImage(models.AbstractModel):
    """
    Widgetoptions:

    ``class``
        setasattributeonthegenerated<img>tag
    """
    _name='ir.qweb.field.image'
    _description='QwebFieldImage'
    _inherit='ir.qweb.field.image'

    local_url_re=re.compile(r'^/(?P<module>[^]]+)/static/(?P<rest>.+)$')

    @api.model
    deffrom_html(self,model,field,element):
        ifelement.find('img')isNone:
            returnFalse
        url=element.find('img').get('src')

        url_object=urls.url_parse(url)
        ifurl_object.path.startswith('/web/image'):
            fragments=url_object.path.split('/')
            query=url_object.decode_query()
            url_id=fragments[3].split('-')[0]
            #ir.attachmentimageurls:/web/image/<id>[-<checksum>][/...]
            ifurl_id.isdigit():
                model='ir.attachment'
                oid=url_id
                field='datas'
            #urlofbinaryfieldonmodel:/web/image/<model>/<id>/<field>[/...]
            else:
                model=query.get('model',fragments[3])
                oid=query.get('id',fragments[4])
                field=query.get('field',fragments[5])
            item=self.env[model].browse(int(oid))
            returnitem[field]

        ifself.local_url_re.match(url_object.path):
            returnself.load_local_url(url)

        returnself.load_remote_url(url)

    defload_local_url(self,url):
        match=self.local_url_re.match(urls.url_parse(url).path)

        rest=match.group('rest')
        forsepinos.sep,os.altsep:
            ifsepandsep!='/':
                rest.replace(sep,'/')

        path=flectra.modules.get_module_resource(
            match.group('module'),'static',*(rest.split('/')))

        ifnotpath:
            returnNone

        try:
            withopen(path,'rb')asf:
                #forcecompleteimageloadtoensureit'svalidimagedata
                image=I.open(f)
                image.load()
                f.seek(0)
                returnbase64.b64encode(f.read())
        exceptException:
            logger.exception("Failedtoloadlocalimage%r",url)
            returnNone

    defload_remote_url(self,url):
        try:
            #shouldprobablyremoveremoteURLsentirely:
            #*infields,downloadingthemwithoutblowinguptheserverisa
            #  challenge
            #*inviews,maytriggermixedcontentwarningsifHTTPSCMS
            #  linkingtoHTTPimages
            #implementdrag&dropimageuploadtomitigate?

            req=requests.get(url,timeout=REMOTE_CONNECTION_TIMEOUT)
            #PILneedsaseekablefile-likeimagesowrapresultinIObuffer
            image=I.open(io.BytesIO(req.content))
            #forceacompleteloadoftheimagedatatovalidateit
            image.load()
        exceptException:
            logger.warning("Failedtoloadremoteimage%r",url,exc_info=True)
            returnNone

        #don'tuseoriginaldataincaseweirdstuffwassmuggledin,with
        #luckPILwillremovesomeofit?
        out=io.BytesIO()
        image.save(out,image.format)
        returnbase64.b64encode(out.getvalue())


classMonetary(models.AbstractModel):
    _name='ir.qweb.field.monetary'
    _inherit='ir.qweb.field.monetary'

    @api.model
    deffrom_html(self,model,field,element):
        lang=self.user_lang()

        value=element.find('span').text.strip()

        returnfloat(value.replace(lang.thousands_sepor'','')
                          .replace(lang.decimal_point,'.'))


classDuration(models.AbstractModel):
    _name='ir.qweb.field.duration'
    _description='QwebFieldDuration'
    _inherit='ir.qweb.field.duration'

    @api.model
    defattributes(self,record,field_name,options,values):
        attrs=super(Duration,self).attributes(record,field_name,options,values)
        ifoptions.get('inherit_branding'):
            attrs['data-oe-original']=record[field_name]
        returnattrs

    @api.model
    deffrom_html(self,model,field,element):
        value=element.text_content().strip()

        #non-localizedvalue
        returnfloat(value)


classRelativeDatetime(models.AbstractModel):
    _name='ir.qweb.field.relative'
    _description='QwebFieldRelative'
    _inherit='ir.qweb.field.relative'

    #getformattingfromir.qweb.field.relativebutedition/savefromdatetime


classQwebView(models.AbstractModel):
    _name='ir.qweb.field.qweb'
    _description='QwebFieldqweb'
    _inherit='ir.qweb.field.qweb'


defhtml_to_text(element):
    """ConvertsHTMLcontentwithHTML-specifiedlinebreaks(br,p,div,...)
    inroughlyequivalenttextualcontent.

    Usedtoreplaceandfixuptheroundtrippingoftextandm2o:whenusing
    libxml2.8.0(butnot2.9.1)andparsingHTMLwithlxml.html.fromstring
    whitespacetextnodes(textnodescomposed*solely*ofwhitespace)are
    strippedoutwithnorecourse,andfundamentallyrelyingonnewlines
    beinginthetext(e.g.insertedduringuseredition)isprobablypoorform
    anyway.

    ->thisutilityfunctioncollapseswhitespacesequencesandreplaces
       nodesbyroughlycorrespondinglinebreaks
       *parepre-andpost-fixedby2newlines
       *brarereplacedbyasinglenewline
       *block-levelelementsnotalreadymentionedarepre-andpost-fixedby
         asinglenewline

    oughtbesomewhatsimilar(butmuchlesshigh-tech)toaaronsw'shtml2text.
    thelatterproducesfull-blownmarkdown,ourtext->htmlconverteronly
    replacesnewlinesby<br>elementsatthispointsowe'rerevertingthat,
    andafewmorenewline-ishelementsincasetheusertriedtoadd
    newlines/paragraphsintothetextfield

    :paramelement:lxml.htmlcontent
    :returns:correspondingpure-textoutput
    """

    #outputisalistofstr|int.Integersarepaddingrequests(inminimum
    #numberofnewlines).Whenmultiplepaddingrequests,foldthemintothe
    #biggestone
    output=[]
    _wrap(element,output)

    #removeanyleadingortailingwhitespace,replacesequencesof
    #(whitespace)\n(whitespace)byasinglenewline,where(whitespace)isa
    #non-newlinewhitespaceinthiscase
    returnre.sub(
        r'[\t\r\f]*\n[\t\r\f]*',
        '\n',
        ''.join(_realize_padding(output)).strip())

_PADDED_BLOCK=set('ph1h2h3h4h5h6'.split())
#https://developer.mozilla.org/en-US/docs/HTML/Block-level_elementsminusp
_MISC_BLOCK=set((
    'addressarticleasideaudioblockquotecanvasdddldivfigcaptionfigure'
    'footerformheaderhgrouphroloutputpresectiontfootulvideo'
).split())


def_collapse_whitespace(text):
    """Collapsessequencesofwhitespacecharactersin``text``toasingle
    space
    """
    returnre.sub('\s+','',text)


def_realize_padding(it):
    """Foldandconvertpaddingrequests:integersintheoutputsequenceare
    requestsforatleastnnewlinesofpadding.Runsthereofcanbecollapsed
    intothelargestrequestsandconvertedtonewlines.
    """
    padding=0
    foriteminit:
        ifisinstance(item,int):
            padding=max(padding,item)
            continue

        ifpadding:
            yield'\n'*padding
            padding=0

        yielditem
    #leftoverpaddingirrelevantastheoutputwillbestripped


def_wrap(element,output,wrapper=u''):
    """Recursivelyextractstextfrom``element``(via_element_to_text),and
    wrapsitallin``wrapper``.Extractedtextisaddedto``output``

    :typewrapper:basestring|int
    """
    output.append(wrapper)
    ifelement.text:
        output.append(_collapse_whitespace(element.text))
    forchildinelement:
        _element_to_text(child,output)
    output.append(wrapper)


def_element_to_text(e,output):
    ife.tag=='br':
        output.append(u'\n')
    elife.tagin_PADDED_BLOCK:
        _wrap(e,output,2)
    elife.tagin_MISC_BLOCK:
        _wrap(e,output,1)
    else:
        #inline
        _wrap(e,output)

    ife.tail:
        output.append(_collapse_whitespace(e.tail))
