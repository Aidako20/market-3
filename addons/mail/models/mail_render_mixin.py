#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbabel
importcopy
importfunctools
importlogging
importre

importdateutil.relativedeltaasrelativedelta
fromwerkzeugimporturls

fromflectraimport_,api,fields,models,tools
fromflectra.exceptionsimportUserError
fromflectra.toolsimportsafe_eval

_logger=logging.getLogger(__name__)


defformat_date(env,date,pattern=False,lang_code=False):
    try:
        returntools.format_date(env,date,date_format=pattern,lang_code=lang_code)
    exceptbabel.core.UnknownLocaleError:
        returndate


defformat_datetime(env,dt,tz=False,dt_format='medium',lang_code=False):
    try:
        returntools.format_datetime(env,dt,tz=tz,dt_format=dt_format,lang_code=lang_code)
    exceptbabel.core.UnknownLocaleError:
        returndt

try:
    #Weuseajinja2sandboxedenvironmenttorendermakotemplates.
    #Notethattherenderingdoesnotcoverallthemakosyntax,inparticular
    #arbitraryPythonstatementsarenotaccepted,andnotallexpressionsare
    #allowed:only"public"attributes(notstartingwith'_')ofobjectsmay
    #beaccessed.
    #Thisisdoneonpurpose:itpreventsincidentalormaliciousexecutionof
    #Pythoncodethatmaybreakthesecurityoftheserver.
    fromjinja2.sandboximportSandboxedEnvironment
    jinja_template_env=SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,              #donotoutputnewlineafterblocks
        autoescape=True,               #XML/HTMLautomaticescaping
    )
    jinja_template_env.globals.update({
        'str':str,
        'quote':urls.url_quote,
        'urlencode':urls.url_encode,
        'datetime':safe_eval.datetime,
        'len':len,
        'abs':abs,
        'min':min,
        'max':max,
        'sum':sum,
        'filter':filter,
        'reduce':functools.reduce,
        'map':map,
        'round':round,

        #dateutil.relativedeltaisanold-styleclassandcannotbedirectly
        #instanciatedwihtinajinja2expression,soalambda"proxy"is
        #isneeded,apparently.
        'relativedelta':lambda*a,**kw:relativedelta.relativedelta(*a,**kw),
    })
    jinja_safe_template_env=copy.copy(jinja_template_env)
    jinja_safe_template_env.autoescape=False
exceptImportError:
    _logger.warning("jinja2notavailable,templatingfeatureswillnotwork!")


classMailRenderMixin(models.AbstractModel):
    _name='mail.render.mixin'
    _description='MailRenderMixin'

    #languageforrendering
    lang=fields.Char(
        'Language',
        help="Optionaltranslationlanguage(ISOcode)toselectwhensendingoutanemail."
             "Ifnotset,theenglishversionwillbeused.Thisshouldusuallybeaplaceholderexpression"
             "thatprovidestheappropriatelanguage,e.g.${object.partner_id.lang}.")
    #expressionbuilder
    model_object_field=fields.Many2one(
        'ir.model.fields',string="Field",store=False,
        help="Selecttargetfieldfromtherelateddocumentmodel.\n"
             "Ifitisarelationshipfieldyouwillbeabletoselect"
             "atargetfieldatthedestinationoftherelationship.")
    sub_object=fields.Many2one(
        'ir.model','Sub-model',readonly=True,store=False,
        help="Whenarelationshipfieldisselectedasfirstfield,"
             "thisfieldshowsthedocumentmodeltherelationshipgoesto.")
    sub_model_object_field=fields.Many2one(
        'ir.model.fields','Sub-field',store=False,
        help="Whenarelationshipfieldisselectedasfirstfield,"
             "thisfieldletsyouselectthetargetfieldwithinthe"
             "destinationdocumentmodel(sub-model).")
    null_value=fields.Char('DefaultValue',store=False,help="Optionalvaluetouseifthetargetfieldisempty")
    copyvalue=fields.Char(
        'PlaceholderExpression',store=False,
        help="Finalplaceholderexpression,tobecopy-pastedinthedesiredtemplatefield.")

    @api.onchange('model_object_field','sub_model_object_field','null_value')
    def_onchange_dynamic_placeholder(self):
        """Generatethedynamicplaceholder"""
        ifself.model_object_field:
            ifself.model_object_field.ttypein['many2one','one2many','many2many']:
                model=self.env['ir.model']._get(self.model_object_field.relation)
                ifmodel:
                    self.sub_object=model.id
                    sub_field_name=self.sub_model_object_field.name
                    self.copyvalue=self._build_expression(self.model_object_field.name,
                                                            sub_field_name,self.null_valueorFalse)
            else:
                self.sub_object=False
                self.sub_model_object_field=False
                self.copyvalue=self._build_expression(self.model_object_field.name,False,self.null_valueorFalse)
        else:
            self.sub_object=False
            self.copyvalue=False
            self.sub_model_object_field=False
            self.null_value=False

    @api.model
    def_build_expression(self,field_name,sub_field_name,null_value):
        """Returnsaplaceholderexpressionforuseinatemplatefield,
        basedonthevaluesprovidedintheplaceholderassistant.

        :paramfield_name:mainfieldname
        :paramsub_field_name:subfieldname(M2O)
        :paramnull_value:defaultvalueifthetargetvalueisempty
        :return:finalplaceholderexpression"""
        expression=''
        iffield_name:
            expression="${object."+field_name
            ifsub_field_name:
                expression+="."+sub_field_name
            ifnull_value:
                expression+="or'''%s'''"%null_value
            expression+="}"
        returnexpression

    #------------------------------------------------------------
    #TOOLS
    #------------------------------------------------------------

    def_replace_local_links(self,html,base_url=None):
        """Replacelocallinksbyabsolutelinks.Itisrequiredinvarious
        cases,forexamplewhensendingemailsonchatterorsendingmass
        mailings.Itreplaces

         *hrefoflinks(mailtowillnotmatchtheregex)
         *srcofimages(base64hardcodeddatawillnotmatchtheregex)
         *stylingusingurllikebackground-image:url

        Itisdoneusingregexbecauseitisshortenthanusinganhtmlparser
        tocreateapotentiallycomplexsoupeandhopetohavearesultthat
        hasnotbeenharmed.
        """
        ifnothtml:
            returnhtml

        html=tools.ustr(html)

        def_sub_relative2absolute(match):
            #computeheretodoitonlyifreallynecessary+cachewillensureitisdoneonlyonce
            #ifnotbase_url
            ifnot_sub_relative2absolute.base_url:
                _sub_relative2absolute.base_url=self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            returnmatch.group(1)+urls.url_join(_sub_relative2absolute.base_url,match.group(2))

        _sub_relative2absolute.base_url=base_url
        html=re.sub(r"""(<img(?=\s)[^>]*\ssrc=")(/[^/][^"]+)""",_sub_relative2absolute,html)
        html=re.sub(r"""(<a(?=\s)[^>]*\shref=")(/[^/][^"]+)""",_sub_relative2absolute,html)
        html=re.sub(r"""(<[^>]+\bstyle="[^"]+\burl\('?)(/[^/'][^'")]+)""",_sub_relative2absolute,html)

        returnhtml

    @api.model
    def_render_encapsulate(self,layout_xmlid,html,add_context=None,context_record=None):
        try:
            template=self.env.ref(layout_xmlid,raise_if_not_found=True)
        exceptValueError:
            _logger.warning('QWebtemplate%snotfoundwhenrenderingencapsulationtemplate.'%(layout_xmlid))
        else:
            record_name=context_record.display_nameifcontext_recordelse''
            model_description=self.env['ir.model']._get(context_record._name).display_nameifcontext_recordelseFalse
            template_ctx={
                'body':html,
                'record_name':record_name,
                'model_description':model_description,
                'company':context_record['company_id']if(context_recordand'company_id'incontext_record)elseself.env.company,
                'record':context_record,
            }
            ifadd_context:
                template_ctx.update(**add_context)

            html=template._render(template_ctx,engine='ir.qweb',minimal_qcontext=True)
            html=self.env['mail.render.mixin']._replace_local_links(html)
        returnhtml

    @api.model
    def_prepend_preview(self,html,preview):
        """Preparetheemailbodybeforesending.Addthetextpreviewatthe
        beginningofthemail.Thepreviewtextisdisplayedbellowthemail
        subjectofmostmailclient(gmail,outlook...).

        :paramhtml:htmlcontentforwhichwewanttoprependapreview
        :parampreview:thepreviewtoaddbeforethehtmlcontent
        :return:htmlwithpreprendedpreview
        """
        ifpreview:
            preview=preview.strip()

        ifpreview:
            html_preview=f"""
                <divstyle="display:none;font-size:1px;height:0px;width:0px;opacity:0;">
                  {tools.html_escape(preview)}
                </div>
            """
            returntools.prepend_html_content(html,html_preview)
        returnhtml

    #------------------------------------------------------------
    #RENDERING
    #------------------------------------------------------------

    @api.model
    def_render_qweb_eval_context(self):
        """Prepareqwebevaluationcontext,containingforallrendering

          *``user``:currentuserbrowserecord;
          *``ctx```:currentcontext;
          *variousformattingtools;
        """
        render_context={
            'format_date':lambdadate,date_format=False,lang_code=False:format_date(self.env,date,date_format,lang_code),
            'format_datetime':lambdadt,tz=False,dt_format=False,lang_code=False:format_datetime(self.env,dt,tz,dt_format,lang_code),
            'format_amount':lambdaamount,currency,lang_code=False:tools.format_amount(self.env,amount,currency,lang_code),
            'format_duration':lambdavalue:tools.format_duration(value),
            'user':self.env.user,
            'ctx':self._context,
        }
        returnrender_context

    @api.model
    def_render_template_qweb(self,template_src,model,res_ids,add_context=None):
        """RenderaQWebtemplate.

        :paramstrtemplate_src:sourceQWebtemplate.Itshouldbeastring
          XmlIDallowingtofetchanir.ui.view;
        :paramstrmodel:see``MailRenderMixin._render_field)``;
        :paramlistres_ids:see``MailRenderMixin._render_field)``;

        :paramdictadd_context:additionalcontexttogivetorenderer.It
          allowstoaddvaluestobaserenderingcontextgeneratedby
          ``MailRenderMixin._render_qweb_eval_context()``;

        :returndict:{res_id:stringofrenderedtemplatebasedonrecord}
        """
        view=self.env.ref(template_src,raise_if_not_found=False)orself.env['ir.ui.view']
        results=dict.fromkeys(res_ids,u"")
        ifnotview:
            returnresults

        #preparetemplatevariables
        variables=self._render_qweb_eval_context()
        ifadd_context:
            variables.update(**add_context)

        forrecordinself.env[model].browse(res_ids):
            variables['object']=record
            try:
                render_result=view._render(variables,engine='ir.qweb',minimal_qcontext=True)
            exceptExceptionase:
                _logger.info("Failedtorendertemplate:%s(%d)"%(template_src,view.id),exc_info=True)
                raiseUserError(_("Failedtorendertemplate:%s(%d)",template_src,view.id))
            results[record.id]=render_result

        returnresults

    @api.model
    def_render_jinja_eval_context(self):
        """Preparejinjaevaluationcontext,containingforallrendering

          *``user``:currentuserbrowserecord;
          *``ctx```:currentcontext,namedctxtoavoidclashwithjinja
            internalsthatalreadyusescontext;
          *variousformattingtools;
        """
        render_context={
            'format_date':lambdadate,date_format=False,lang_code=False:format_date(self.env,date,date_format,lang_code),
            'format_datetime':lambdadt,tz=False,dt_format=False,lang_code=False:format_datetime(self.env,dt,tz,dt_format,lang_code),
            'format_amount':lambdaamount,currency,lang_code=False:tools.format_amount(self.env,amount,currency,lang_code),
            'format_duration':lambdavalue:tools.format_duration(value),
            'user':self.env.user,
            'ctx':self._context,
        }
        returnrender_context

    @api.model
    def_render_template_jinja(self,template_txt,model,res_ids,add_context=None):
        """Renderastring-basedtemplateonrecordsgivenbyamodelandalist
        ofIDs,usingjinja.

        Inadditiontothegenericevaluationcontextgivenby_render_jinja_eval_context
        somenewvariablesareadded,dependingoneachrecord

          *``object``:recordbasedonwhichthetemplateisrendered;

        :paramstrtemplate_txt:templatetexttorender
        :paramstrmodel:modelnameofrecordsonwhichwewanttoperformrendering
        :paramlistres_ids:listofidsofrecords(allbelongingtosamemodel)

        :returndict:{res_id:stringofrenderedtemplatebasedonrecord}
        """
        #TDEFIXME:removethatbrol(6dde919bb9850912f618b561cd2141bffe41340c)
        no_autoescape=self._context.get('safe')
        results=dict.fromkeys(res_ids,u"")
        ifnottemplate_txt:
            returnresults

        #trytoloadthetemplate
        try:
            jinja_env=jinja_safe_template_envifno_autoescapeelsejinja_template_env
            template=jinja_env.from_string(tools.ustr(template_txt))
        exceptException:
            _logger.info("Failedtoloadtemplate%r",template_txt,exc_info=True)
            returnresults

        #preparetemplatevariables
        variables=self._render_jinja_eval_context()
        ifadd_context:
            variables.update(**add_context)
        safe_eval.check_values(variables)

        #TDECHECKME
        #records=self.env[model].browse(itforitinres_idsifit) #filtertoavoidbrowsing[None]
        ifany(risNoneforrinres_ids):
            raiseValueError(_('UnsuspectedNone'))

        forrecordinself.env[model].browse(res_ids):
            variables['object']=record
            try:
                render_result=template.render(variables)
            exceptExceptionase:
                _logger.info("Failedtorendertemplate:%s"%e,exc_info=True)
                raiseUserError(_("Failedtorendertemplate:%s",e))
            ifrender_result==u"False":
                render_result=u""
            results[record.id]=render_result

        returnresults

    @api.model
    def_render_template_postprocess(self,rendered):
        """Toolmethodforpostprocessing.Inthismethodweensurelocal
        links('/shop/Basil-1')arereplacedbygloballinks('https://www.
        mygardin.com/hop/Basil-1').

        :paramrendered:resultof``_render_template``

        :returndict:updatedversionofrendered
        """
        forres_id,htmlinrendered.items():
            rendered[res_id]=self._replace_local_links(html)
        returnrendered

    @api.model
    def_render_template(self,template_src,model,res_ids,engine='jinja',add_context=None,post_process=False):
        """Renderthegivenstringonrecordsdesignedbymodel/res_idsusing
        thegivenrenderingengine.Currentlyonlyjinjaorqwebaresupported.

        :paramstrtemplate_src:templatetexttorender(jinja)orxmlidofview(qweb)
          thiscouldbecleanedbuthey,weareinarush
        :paramstrmodel:modelnameofrecordsonwhichwewanttoperformrendering
        :paramlistres_ids:listofidsofrecords(allbelongingtosamemodel)
        :paramstringengine:jinja
        :parampost_process:see``MailRenderMixin._render_field``;

        :returndict:{res_id:stringofrenderedtemplatebasedonrecord}
        """
        ifnotisinstance(res_ids,(list,tuple)):
            raiseValueError(_('TemplaterenderingshouldbecalledonlyusingonalistofIDs.'))
        ifenginenotin('jinja','qweb'):
            raiseValueError(_('Templaterenderingsupportsonlyjinjaorqweb.'))

        ifengine=='qweb':
            rendered=self._render_template_qweb(template_src,model,res_ids,add_context=add_context)
        else:
            rendered=self._render_template_jinja(template_src,model,res_ids,add_context=add_context)
        ifpost_process:
            rendered=self._render_template_postprocess(rendered)

        returnrendered

    def_render_lang(self,res_ids):
        """Givensomerecordids,returnthelangforeachrecordbasedon
        langfieldoftemplateorthroughspecificcontext-basedkey.

        :paramlistres_ids:listofidsofrecords(allbelongingtosamemodel
          definedbyself.model)

        :returndict:{res_id:langcode(i.e.en_US)}
        """
        self.ensure_one()
        ifnotisinstance(res_ids,(list,tuple)):
            raiseValueError(_('TemplaterenderingforlanguageshouldbecalledwithalistofIDs.'))

        ifself.env.context.get('template_preview_lang'):
            returndict((res_id,self.env.context['template_preview_lang'])forres_idinres_ids)
        else:
            rendered_langs=self._render_template(self.lang,self.model,res_ids)
            returndict((res_id,lang)
                        forres_id,langinrendered_langs.items())

    def_classify_per_lang(self,res_ids):
        """Givensomerecordids,returnforcomputedeachlangacontextualized
        templateanditssubsetofres_ids.

        :paramlistres_ids:listofidsofrecords(allbelongingtosamemodel
          definedbyself.model)

        :returndict:{lang:(templatewithlang=lang_codeifspecificlangcomputed
          ortemplate,res_idstargetedbythatlanguage}
        """
        self.ensure_one()

        lang_to_res_ids={}
        forres_id,langinself._render_lang(res_ids).items():
            lang_to_res_ids.setdefault(lang,[]).append(res_id)

        returndict(
            (lang,(self.with_context(lang=lang)iflangelseself,lang_res_ids))
            forlang,lang_res_idsinlang_to_res_ids.items()
        )

    def_render_field(self,field,res_ids,
                      compute_lang=False,set_lang=False,
                      post_process=False):
        """Givensomerecordids,renderatemplatelocatedonfieldonall
        records.``field``shouldbeafieldofself(i.e.``body_html``on
        ``mail.template``).res_idsarerecordIDslinkedto``model``field
        onself.

        :paramlistres_ids:listofidsofrecords(allbelongingtosamemodel
          definedby``self.model``)

        :parambooleancompute_lang:computelanguagetorenderontranslated
          versionofthetemplateinsteadofdefault(probablyenglish)one.
          Languagewillbecomputedbasedon``self.lang``;
        :paramstringset_lang:forcelanguageforrendering.Itshouldbea
          validlangcodematchinganactivateres.lang.Checkedonlyif
          ``compute_lang``isFalse;
        :parambooleanpost_process:performapostprocessingonrenderedresult
          (notablyhtmllinksmanagement).See``_render_template_postprocess``);

        :returndict:{res_id:stringofrenderedtemplatebasedonrecord}
        """
        self.ensure_one()
        ifcompute_lang:
            templates_res_ids=self._classify_per_lang(res_ids)
        elifset_lang:
            templates_res_ids={set_lang:(self.with_context(lang=set_lang),res_ids)}
        else:
            templates_res_ids={self._context.get('lang'):(self,res_ids)}

        returndict(
            (res_id,rendered)
            forlang,(template,tpl_res_ids)intemplates_res_ids.items()
            forres_id,renderedintemplate._render_template(
                template[field],template.model,tpl_res_ids,
                post_process=post_process
            ).items()
        )
