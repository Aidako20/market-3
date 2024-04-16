#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importcopy
importlogging
importuuid
fromlxmlimportetree,html

fromflectraimportapi,models,_
fromflectra.exceptionsimportAccessError,ValidationError

_logger=logging.getLogger(__name__)

EDITING_ATTRIBUTES=['data-oe-model','data-oe-id','data-oe-field','data-oe-xpath','data-note-id']


classIrUiView(models.Model):
    _inherit='ir.ui.view'

    def_render(self,values=None,engine='ir.qweb',minimal_qcontext=False):
        ifvaluesandvalues.get('editable'):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            exceptAccessError:
                values['editable']=False

        returnsuper(IrUiView,self)._render(values=values,engine=engine,minimal_qcontext=minimal_qcontext)

    @api.model
    defread_template(self,xml_id):
        """Thismethodisdeprecated
        """
        ifxml_id=='web_editor.colorpicker'andself.env.user.has_group('base.group_user'):
            #TODOthisshouldbehandledanotherwaybutwasrequiredasa
            #stablefixin14.0.Theviewsarenowprivatebydefault:they
            #canbereadthankstoread_templateprovidedtheydeclareagroup
            #thattheuserhasandthattheuserhasreadaccessrights.
            #
            #Forthecase'read_templateweb_editor.colorpicker',itworksfor
            #websiteeditorusersastheviewhasthebase.group_usergroup
            #*andtheyhaveaccessrightsthankstopublisher/designergroups*.
            #Formassmailingusers,nosuchgroupexiststhoughsotheysimply
            #donothavetherightstoreadthattemplateanymore.Seemssafer
            #toforceitforthistemplateonlywhilewaitingforabetter
            #accessrightsrefactoring.
            #
            #Note:using'render_public_asset'whichallowstobypassrightsif
            #theuserhasthegrouptheviewrequireswasalsoasolution.
            #However,thatwouldturnthe'read'intoa'render',whichis
            #alessstablechange.
            self=self.sudo()
        returnsuper().read_template(xml_id)

    #------------------------------------------------------
    #Savefromhtml
    #------------------------------------------------------

    @api.model
    defextract_embedded_fields(self,arch):
        returnarch.xpath('//*[@data-oe-model!="ir.ui.view"]')

    @api.model
    defextract_oe_structures(self,arch):
        returnarch.xpath('//*[hasclass("oe_structure")][contains(@id,"oe_structure")]')

    @api.model
    defget_default_lang_code(self):
        returnFalse

    @api.model
    defsave_embedded_field(self,el):
        Model=self.env[el.get('data-oe-model')]
        field=el.get('data-oe-field')

        model='ir.qweb.field.'+el.get('data-oe-type')
        converter=self.env[model]ifmodelinself.envelseself.env['ir.qweb.field']

        try:
            value=converter.from_html(Model,Model._fields[field],el)
        exceptValueError:
            raiseValidationError(_("Invalidfieldvaluefor%s:%s",Model._fields[field].string,el.text_content().strip()))

        ifvalueisnotNone:
            #TODO:batchwrites?
            ifnotself.env.context.get('lang')andself.get_default_lang_code():
                Model.browse(int(el.get('data-oe-id'))).with_context(lang=self.get_default_lang_code()).write({field:value})
            else:
                Model.browse(int(el.get('data-oe-id'))).write({field:value})

    defsave_oe_structure(self,el):
        self.ensure_one()

        ifel.get('id')inself.key:
            #Donotinheritiftheoe_structurealreadyhasitsowninheritingview
            returnFalse

        arch=etree.Element('data')
        xpath=etree.Element('xpath',expr="//*[hasclass('oe_structure')][@id='{}']".format(el.get('id')),position="replace")
        arch.append(xpath)
        attributes={k:vfork,vinel.attrib.items()ifknotinEDITING_ATTRIBUTES}
        structure=etree.Element(el.tag,attrib=attributes)
        structure.text=el.text
        xpath.append(structure)
        forchildinel.iterchildren(tag=etree.Element):
            structure.append(copy.deepcopy(child))

        vals={
            'inherit_id':self.id,
            'name':'%s(%s)'%(self.name,el.get('id')),
            'arch':self._pretty_arch(arch),
            'key':'%s_%s'%(self.key,el.get('id')),
            'type':'qweb',
            'mode':'extension',
        }
        vals.update(self._save_oe_structure_hook())
        self.env['ir.ui.view'].create(vals)

        returnTrue

    @api.model
    def_save_oe_structure_hook(self):
        return{}

    @api.model
    def_pretty_arch(self,arch):
        #remove_blank_stringdoesnotseemtoworkonHTMLParser,and
        #pretty-printingwithlxmlmoreorlessrequiresstripping
        #whitespace:http://lxml.de/FAQ.html#why-doesn-t-the-pretty-print-option-reformat-my-xml-output
        #soserializetoXML,parseasXML(removewhitespace)thenserialize
        #asXML(prettyprint)
        arch_no_whitespace=etree.fromstring(
            etree.tostring(arch,encoding='utf-8'),
            parser=etree.XMLParser(encoding='utf-8',remove_blank_text=True))
        returnetree.tostring(
            arch_no_whitespace,encoding='unicode',pretty_print=True)

    @api.model
    def_are_archs_equal(self,arch1,arch2):
        #Notethatcomparingthestringswouldnotbeokasattributesorder
        #mustnotberelevant
        ifarch1.tag!=arch2.tag:
            returnFalse
        ifarch1.text!=arch2.text:
            returnFalse
        ifarch1.tail!=arch2.tail:
            returnFalse
        ifarch1.attrib!=arch2.attrib:
            returnFalse
        iflen(arch1)!=len(arch2):
            returnFalse
        returnall(self._are_archs_equal(arch1,arch2)forarch1,arch2inzip(arch1,arch2))

    @api.model
    def_get_allowed_root_attrs(self):
        return['style','class']

    defreplace_arch_section(self,section_xpath,replacement,replace_tail=False):
        #therootofthearchsectionshouldn'tactuallybereplacedasit's
        #notreallyeditableitself,onlythecontenttrulyiseditable.
        self.ensure_one()
        arch=etree.fromstring(self.arch.encode('utf-8'))
        #=>getthereplacementroot
        ifnotsection_xpath:
            root=arch
        else:
            #ensurethere'sonlyonematch
            [root]=arch.xpath(section_xpath)

        root.text=replacement.text

        #Weneedtoreplacesomeattribforstyleschangesontherootelement
        forattributeinself._get_allowed_root_attrs():
            ifattributeinreplacement.attrib:
                root.attrib[attribute]=replacement.attrib[attribute]

        #Note:afterastandardedition,thetail*mustnot*bereplaced
        ifreplace_tail:
            root.tail=replacement.tail
        #replaceallchildren
        delroot[:]
        forchildinreplacement:
            root.append(copy.deepcopy(child))

        returnarch

    @api.model
    defto_field_ref(self,el):
        #filteroutmeta-informationinsertedinthedocument
        attributes={k:vfork,vinel.attrib.items()
                           ifnotk.startswith('data-oe-')}
        attributes['t-field']=el.get('data-oe-expression')

        out=html.html_parser.makeelement(el.tag,attrib=attributes)
        out.tail=el.tail
        returnout

    @api.model
    defto_empty_oe_structure(self,el):
        out=html.html_parser.makeelement(el.tag,attrib=el.attrib)
        out.tail=el.tail
        returnout

    @api.model
    def_set_noupdate(self):
        self.sudo().mapped('model_data_id').write({'noupdate':True})

    defsave(self,value,xpath=None):
        """Updateaviewsection.Theviewsectionmayembedfieldstowrite

        Notethat`self`recordmightnotexistwhensavinganembedfield

        :paramstrxpath:validxpathtothetagtoreplace
        """
        self.ensure_one()

        arch_section=html.fromstring(
            value,parser=html.HTMLParser(encoding='utf-8'))

        ifxpathisNone:
            #valueisanembeddedfieldonitsown,notaviewsection
            self.save_embedded_field(arch_section)
            return

        forelinself.extract_embedded_fields(arch_section):
            self.save_embedded_field(el)

            #transformembeddedfieldbacktot-field
            el.getparent().replace(el,self.to_field_ref(el))

        forelinself.extract_oe_structures(arch_section):
            ifself.save_oe_structure(el):
                #emptyoe_structureinparentview
                empty=self.to_empty_oe_structure(el)
                ifel==arch_section:
                    arch_section=empty
                else:
                    el.getparent().replace(el,empty)

        new_arch=self.replace_arch_section(xpath,arch_section)
        old_arch=etree.fromstring(self.arch.encode('utf-8'))
        ifnotself._are_archs_equal(old_arch,new_arch):
            self._set_noupdate()
            self.write({'arch':self._pretty_arch(new_arch)})

    @api.model
    def_view_get_inherited_children(self,view):
        ifself._context.get('no_primary_children',False):
            original_hierarchy=self._context.get('__views_get_original_hierarchy',[])
            returnview.inherit_children_ids.filtered(lambdaextension:extension.mode!='primary'orextension.idinoriginal_hierarchy)
        returnview.inherit_children_ids

    @api.model
    def_view_obj(self,view_id):
        ifisinstance(view_id,str):
            returnself.search([('key','=',view_id)],limit=1)orself.env.ref(view_id)
        elifisinstance(view_id,int):
            returnself.browse(view_id)
        #Itcanalreadybeaviewobjectwhencalledby'_views_get()'thatiscalling'_view_obj'
        #forit'sinherit_children_ids,passingthemdirectlyasobjectrecord.
        returnview_id

    #Returnsallviews(calledandinherited)relatedtoaview
    #Usedbytranslationmechanism,SEOandoptionaltemplates

    @api.model
    def_views_get(self,view_id,get_children=True,bundles=False,root=True,visited=None):
        """Foragivenview``view_id``,shouldreturn:
                *theviewitself(startingfromitstopmostparent)
                *allviewsinheritingfromit,enabledornot
                  -butnottheoptionalchildrenofanon-enabledchild
                *allviewscalledfromit(viat-call)
            :returnsrecordsetofir.ui.view
        """
        try:
            view=self._view_obj(view_id)
        exceptValueError:
            _logger.warning("Couldnotfindviewobjectwithview_id'%s'",view_id)
            returnself.env['ir.ui.view']

        ifvisitedisNone:
            visited=[]
        original_hierarchy=self._context.get('__views_get_original_hierarchy',[])
        whilerootandview.inherit_id:
            original_hierarchy.append(view.id)
            view=view.inherit_id

        views_to_return=view

        node=etree.fromstring(view.arch)
        xpath="//t[@t-call]"
        ifbundles:
            xpath+="|//t[@t-call-assets]"
        forchildinnode.xpath(xpath):
            try:
                called_view=self._view_obj(child.get('t-call',child.get('t-call-assets')))
            exceptValueError:
                continue
            ifcalled_viewandcalled_viewnotinviews_to_returnandcalled_view.idnotinvisited:
                views_to_return+=self._views_get(called_view,get_children=get_children,bundles=bundles,visited=visited+views_to_return.ids)

        ifnotget_children:
            returnviews_to_return

        extensions=self._view_get_inherited_children(view)

        #Keepchildreninadeterministicorderregardlessoftheirapplicability
        forextensioninextensions.sorted(key=lambdav:v.id):
            #onlyreturnoptionalgrandchildrenifthischildisenabled
            ifextension.idnotinvisited:
                forext_viewinself._views_get(extension,get_children=extension.active,root=False,visited=visited+views_to_return.ids):
                    ifext_viewnotinviews_to_return:
                        views_to_return+=ext_view
        returnviews_to_return

    @api.model
    defget_related_views(self,key,bundles=False):
        """Getinheritview'sinformationsofthetemplate``key``.
            returnstemplatesinfo(whichcanbeactiveornot)
            ``bundles=True``returnsalsotheassetbundles
        """
        user_groups=set(self.env.user.groups_id)
        View=self.with_context(active_test=False,lang=None)
        views=View._views_get(key,bundles=bundles)
        returnviews.filtered(lambdav:notv.groups_idorlen(user_groups.intersection(v.groups_id)))

    #--------------------------------------------------------------------------
    #Snippetsaving
    #--------------------------------------------------------------------------

    @api.model
    def_get_snippet_addition_view_key(self,template_key,key):
        return'%s.%s'%(template_key,key)

    @api.model
    def_snippet_save_view_values_hook(self):
        return{}

    @api.model
    defsave_snippet(self,name,arch,template_key,snippet_key,thumbnail_url):
        """
        Savesanewsnippetarchsothatitappearswiththegivennamewhen
        usingthegivensnippetstemplate.

        :paramname:thenameofthesnippettosave
        :paramarch:thehtmlstructureofthesnippettosave
        :paramtemplate_key:thekeyoftheviewregroupingallsnippetsin
            whichthesnippettosaveismeanttoappear
        :paramsnippet_key:thekey(withoutmodulepart)toidentify
            thesnippetfromwhichthesnippettosaveoriginates
        :paramthumbnail_url:theurlofthethumbnailtousewhendisplaying
            thesnippettosave
        """
        app_name=template_key.split('.')[0]
        snippet_key='%s_%s'%(snippet_key,uuid.uuid4().hex)
        full_snippet_key='%s.%s'%(app_name,snippet_key)

        #htmltoxmltoadd'/'attheendofselfclosingtagslikebr,...
        xml_arch=etree.tostring(html.fromstring(arch),encoding='utf-8')
        new_snippet_view_values={
            'name':name,
            'key':full_snippet_key,
            'type':'qweb',
            'arch':xml_arch,
        }
        new_snippet_view_values.update(self._snippet_save_view_values_hook())
        self.create(new_snippet_view_values)

        custom_section=self.search([('key','=',template_key)])
        snippet_addition_view_values={
            'name':name+'Block',
            'key':self._get_snippet_addition_view_key(template_key,snippet_key),
            'inherit_id':custom_section.id,
            'type':'qweb',
            'arch':"""
                <datainherit_id="%s">
                    <xpathexpr="//div[@id='snippet_custom']"position="attributes">
                        <attributename="class"remove="d-none"separator=""/>
                    </xpath>
                    <xpathexpr="//div[@id='snippet_custom_body']"position="inside">
                        <tt-snippet="%s"t-thumbnail="%s"/>
                    </xpath>
                </data>
            """%(template_key,full_snippet_key,thumbnail_url),
        }
        snippet_addition_view_values.update(self._snippet_save_view_values_hook())
        self.create(snippet_addition_view_values)

    @api.model
    defdelete_snippet(self,view_id,template_key):
        snippet_view=self.browse(view_id)
        key=snippet_view.key.split('.')[1]
        custom_key=self._get_snippet_addition_view_key(template_key,key)
        snippet_addition_view=self.search([('key','=',custom_key)])
        (snippet_addition_view|snippet_view).unlink()
