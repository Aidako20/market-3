#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importos
importuuid
importwerkzeug

fromflectraimportapi,fields,models
fromflectraimporttools
fromflectra.addonsimportwebsite
fromflectra.exceptionsimportAccessError
fromflectra.osvimportexpression
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classView(models.Model):

    _name="ir.ui.view"
    _inherit=["ir.ui.view","website.seo.metadata"]

    website_id=fields.Many2one('website',ondelete='cascade',string="Website")
    page_ids=fields.One2many('website.page','view_id')
    first_page_id=fields.Many2one('website.page',string='WebsitePage',help='Firstpagelinkedtothisview',compute='_compute_first_page_id')
    track=fields.Boolean(string='Track',default=False,help="Allowtospecifyforonepageofthewebsitetobetrackableornot")
    visibility=fields.Selection([('','All'),('connected','SignedIn'),('restricted_group','RestrictedGroup'),('password','WithPassword')],default='')
    visibility_password=fields.Char(groups='base.group_system',copy=False)
    visibility_password_display=fields.Char(compute='_get_pwd',inverse='_set_pwd',groups='website.group_website_designer')

    @api.depends('visibility_password')
    def_get_pwd(self):
        forrinself:
            r.visibility_password_display=r.sudo().visibility_passwordand'********'or''

    def_set_pwd(self):
        crypt_context=self.env.user._crypt_context()
        forrinself:
            ifr.type=='qweb':
                r.sudo().visibility_password=r.visibility_password_displayandcrypt_context.encrypt(r.visibility_password_display)or''
                r.visibility=r.visibility #doublecheckaccess

    def_compute_first_page_id(self):
        forviewinself:
            view.first_page_id=self.env['website.page'].search([('view_id','=',view.id)],limit=1)

    defname_get(self):
        if(notself._context.get('display_website')andnotself.env.user.has_group('website.group_multi_website'))or\
                notself._context.get('display_website'):
            returnsuper(View,self).name_get()

        res=[]
        forviewinself:
            view_name=view.name
            ifview.website_id:
                view_name+='[%s]'%view.website_id.name
            res.append((view.id,view_name))
        returnres

    defwrite(self,vals):
        '''COWforir.ui.view.Thiswayeditingwebsitesdoesnotimpactother
        websites.Alsothiswaynewlycreatedwebsiteswillonly
        containthedefaultviews.
        '''
        current_website_id=self.env.context.get('website_id')
        ifnotcurrent_website_idorself.env.context.get('no_cow'):
            returnsuper(View,self).write(vals)

        #Weneedtoconsiderinactiveviewswhenhandlingmulti-websitecow
        #feature(tocopyinactivechildrenviews,tosearchforspecific
        #views,...)
        #Website-specificviewsneedtobeupdatedfirstbecausetheymight
        #berelocatedtonewidsbythecowiftheyareinvolvedinthe
        #inheritancetree.
        forviewinself.with_context(active_test=False).sorted(key='website_id',reverse=True):
            #Makesureviewswhicharewritteninawebsitecontextreceive
            #avaluefortheir'key'field
            ifnotview.keyandnotvals.get('key'):
                view.with_context(no_cow=True).key='website.key_%s'%str(uuid.uuid4())[:6]

            pages=view.page_ids

            #Disablecacheofpageifweguesssomedynamiccontent(formwithcsrf,...)
            ifvals.get('arch'):
                to_invalidate=pages.filtered(
                    lambdap:p.cache_timeandnotp._can_be_cached(vals['arch'])
                )
                to_invalidateand_logger.info('Disablecacheforpage%s'%to_invalidate)
                to_invalidate.cache_time=0

            #NoneedofCOWiftheviewisalreadyspecific
            ifview.website_id:
                super(View,view).write(vals)
                continue

            #EnsurethecacheofthepagesstayconsistentwhendoingCOW.
            #Thisisnecessarywhenwritingviewfieldsfromapagerecord
            #becausethegenericpagewillputthegivenvaluesonitscache
            #butinrealitythevalueswereonlymeanttogoonthespecific
            #page.Invalidateallfieldsandnotonlythoseinvalsbecause
            #otherfieldscouldhavebeenchangedimplicitlytoo.
            pages.flush(records=pages)
            pages.invalidate_cache(ids=pages.ids)

            #Ifalreadyaspecificviewforthisgenericview,writeonit
            website_specific_view=view.search([
                ('key','=',view.key),
                ('website_id','=',current_website_id)
            ],limit=1)
            ifwebsite_specific_view:
                super(View,website_specific_view).write(vals)
                continue

            #Setkeytoavoidcopy()togenerateanuniquekeyaswewantthe
            #specificviewtohavethesamekey
            copy_vals={'website_id':current_website_id,'key':view.key}
            #Copywiththe'inherit_id'fieldvaluethatwillbewrittento
            #ensurethecopiedview'svalidationworks
            ifvals.get('inherit_id'):
                copy_vals['inherit_id']=vals['inherit_id']
            website_specific_view=view.copy(copy_vals)

            view._create_website_specific_pages_for_view(website_specific_view,
                                                         view.env['website'].browse(current_website_id))

            forinherit_childinview.inherit_children_ids.filter_duplicate().sorted(key=lambdav:(v.priority,v.id)):
                ifinherit_child.website_id.id==current_website_id:
                    #Inthecasethechildwasalreadyspecifictothecurrent
                    #website,wecannotjustreattachittothenewspecific
                    #parent:wehavetocopyitthereandremoveitfromthe
                    #originaltree.Indeed,theorderofchildren'id'fields
                    #mustremainthesamesothattheinheritanceisapplied
                    #inthesameorderinthecopiedtree.
                    child=inherit_child.copy({'inherit_id':website_specific_view.id,'key':inherit_child.key})
                    inherit_child.inherit_children_ids.write({'inherit_id':child.id})
                    inherit_child.unlink()
                else:
                    #TriggerCOWoninheritingviews
                    inherit_child.write({'inherit_id':website_specific_view.id})

            super(View,website_specific_view).write(vals)

        returnTrue

    def_load_records_write_on_cow(self,cow_view,inherit_id,values):
        inherit_id=self.search([
            ('key','=',self.browse(inherit_id).key),
            ('website_id','in',(False,cow_view.website_id.id)),
        ],order='website_id',limit=1).id
        values['inherit_id']=inherit_id
        cow_view.with_context(no_cow=True).write(values)

    def_create_all_specific_views(self,processed_modules):
        """Whencreatingagenericchildview,weshould
            alsocreatethatviewunderspecificviewtrees(COW'd).
            Toplevelview(noinherit_id)donotneedthatbehaviorasthey
            willbesharedbetweenwebsitessincethereisnospecificyet.
        """
        #Onlyforthemodulesbeingprocessed
        regex='^(%s)[.]'%'|'.join(processed_modules)
        #RetrievetheviewsthroughaSQlquerytoavoidORMqueriesinsideofforloop
        #Retrievesalltheviewsthataremissingtheirspecificcounterpartwithallthe
        #specificviewparentidandtheirwebsiteidinonequery
        query="""
            SELECTgeneric.id,ARRAY[array_agg(spec_parent.id),array_agg(spec_parent.website_id)]
              FROMir_ui_viewgeneric
        INNERJOINir_ui_viewgeneric_parentONgeneric_parent.id=generic.inherit_id
        INNERJOINir_ui_viewspec_parentONspec_parent.key=generic_parent.key
         LEFTJOINir_ui_viewspecificONspecific.key=generic.keyANDspecific.website_id=spec_parent.website_id
             WHEREgeneric.type='qweb'
               ANDgeneric.website_idISNULL
               ANDgeneric.key~%s
               ANDspec_parent.website_idISNOTNULL
               ANDspecific.idISNULL
          GROUPBYgeneric.id
        """
        self.env.cr.execute(query,(regex,))
        result=dict(self.env.cr.fetchall())

        forrecordinself.browse(result.keys()):
            specific_parent_view_ids,website_ids=result[record.id]
            forspecific_parent_view_id,website_idinzip(specific_parent_view_ids,website_ids):
                record.with_context(website_id=website_id).write({
                    'inherit_id':specific_parent_view_id,
                })
        super(View,self)._create_all_specific_views(processed_modules)

    defunlink(self):
        '''ThisimplementsCOU(copy-on-unlink).Whendeletingagenericpage
        website-specificpageswillbecreatedsoonlythecurrent
        websiteisaffected.
        '''
        current_website_id=self._context.get('website_id')

        ifcurrent_website_idandnotself._context.get('no_cow'):
            forviewinself.filtered(lambdaview:notview.website_id):
                forwinself.env['website'].search([('id','!=',current_website_id)]):
                    #reusetheCOWmechanismtocreate
                    #website-specificcopies,itwilltake
                    #careofcreatingpagesandmenus.
                    view.with_context(website_id=w.id).write({'name':view.name})

        specific_views=self.env['ir.ui.view']
        ifselfandself.pool._init:
            forviewinself.filtered(lambdaview:notview.website_id):
                specific_views+=view._get_specific_views()

        result=super(View,self+specific_views).unlink()
        self.clear_caches()
        returnresult

    def_create_website_specific_pages_for_view(self,new_view,website):
        forpageinself.page_ids:
            #createnewpagesforthisview
            new_page=page.copy({
                'view_id':new_view.id,
                'is_published':page.is_published,
            })
            page.menu_ids.filtered(lambdam:m.website_id.id==website.id).page_id=new_page.id

    @api.model
    defget_related_views(self,key,bundles=False):
        '''Makethisonlyreturnmostspecificviewsforwebsite.'''
        #get_related_viewscanbecalledthroughwebsite=Falseroutes
        #(e.g./web_editor/get_assets_editor_resources),sowebsite
        #dispatch_parametersmaynotbeadded.Manuallyset
        #website_id.(Itwillthenalwaysfallbackonawebsite,this
        #methodshouldneverbecalledinagenericcontext,evenfor
        #tests)
        self=self.with_context(website_id=self.env['website'].get_current_website().id)
        returnsuper(View,self).get_related_views(key,bundles=bundles)

    deffilter_duplicate(self):
        """Filtercurrentrecordsetonlykeepingthemostsuitableviewperdistinctkey.
            Everynon-accessibleviewwillberemovedfromtheset:
              *Innonwebsitecontext,everyviewwithawebsitewillberemoved
              *Inawebsitecontext,everyviewfromanotherwebsite
        """
        current_website_id=self._context.get('website_id')
        most_specific_views=self.env['ir.ui.view']
        ifnotcurrent_website_id:
            returnself.filtered(lambdaview:notview.website_id)

        forviewinself:
            #specificview:additifit'sforthecurrentwebsiteandignore
            #itifit'sforanotherwebsite
            ifview.website_idandview.website_id.id==current_website_id:
                most_specific_views|=view
            #genericview:additonlyif,forthecurrentwebsite,thereisno
            #specificviewforthisview(basedonthesame`key`attribute)
            elifnotview.website_idandnotany(view.key==view2.keyandview2.website_idandview2.website_id.id==current_website_idforview2inself):
                most_specific_views|=view

        returnmost_specific_views

    @api.model
    def_view_get_inherited_children(self,view):
        extensions=super(View,self)._view_get_inherited_children(view)
        returnextensions.filter_duplicate()

    @api.model
    def_view_obj(self,view_id):
        '''Givenanxml_idoraview_id,returnthecorrespondingviewrecord.
            Incaseofwebsitecontext,returnthemostspecificone.
            :paramview_id:eitherastringxml_idoranintegerview_id
            :return:Theviewrecordoremptyrecordset
        '''
        ifisinstance(view_id,str)orisinstance(view_id,int):
            returnself.env['website'].viewref(view_id)
        else:
            #Itcanalreadybeaviewobjectwhencalledby'_views_get()'thatiscalling'_view_obj'
            #forit'sinherit_children_ids,passingthemdirectlyasobjectrecord.(Notethatitmight
            #beaview_idfromanotherwebsitebutitwillbefilteredin'get_related_views()')
            returnview_idifview_id._name=='ir.ui.view'elseself.env['ir.ui.view']

    @api.model
    def_get_inheriting_views_arch_domain(self,model):
        domain=super(View,self)._get_inheriting_views_arch_domain(model)
        current_website=self.env['website'].browse(self._context.get('website_id'))
        website_views_domain=current_website.website_domain()
        #whenrenderingforthewebsitewehavetoincludeinactiveviews
        #wewillpreferinactivewebsite-specificviewsoveractivegenericones
        ifcurrent_website:
            domain=[leafforleafindomainif'active'notinleaf]
        returnexpression.AND([website_views_domain,domain])

    @api.model
    defget_inheriting_views_arch(self,model):
        ifnotself._context.get('website_id'):
            returnsuper(View,self).get_inheriting_views_arch(model)

        views=super(View,self.with_context(active_test=False)).get_inheriting_views_arch(model)
        #preferinactivewebsite-specificviewsoveractivegenericones
        returnviews.filter_duplicate().filtered('active')

    @api.model
    def_get_filter_xmlid_query(self):
        """ThismethodaddsomespecificviewthatdonothaveXMLID
        """
        ifnotself._context.get('website_id'):
            returnsuper()._get_filter_xmlid_query()
        else:
            return"""SELECTres_id
                    FROM  ir_model_data
                    WHERE res_idIN%(res_ids)s
                        ANDmodel='ir.ui.view'
                        ANDmodule IN%(modules)s
                    UNION
                    SELECTsview.id
                    FROM  ir_ui_viewsview
                        INNERJOINir_ui_viewoviewUSING(key)
                        INNERJOINir_model_datad
                                ONoview.id=d.res_id
                                    ANDd.model='ir.ui.view'
                                    ANDd.module IN%(modules)s
                    WHERE sview.idIN%(res_ids)s
                        ANDsview.website_idISNOTNULL
                        ANDoview.website_idISNULL;
                    """

    @api.model
    @tools.ormcache_context('self.env.uid','self.env.su','xml_id',keys=('website_id',))
    defget_view_id(self,xml_id):
        """Ifawebsite_idisinthecontextandthegivenxml_idisnotanint
        thentrytogettheidofthespecificviewforthatwebsite,but
        fallbacktotheidofthegenericviewifthereisnospecific.

        Ifnowebsite_idisinthecontext,itmightrandomlyreturnthegeneric
        orthespecificview,soit'sprobablynotrecommandedtousethis
        method.`viewref`isprobablymoresuitable.

        Archivedviewsareignored(unlesstheactive_testcontextisset,but
        thentheormcache_contextwillnotworkasexpected).
        """
        if'website_id'inself._contextandnotisinstance(xml_id,int):
            current_website=self.env['website'].browse(self._context.get('website_id'))
            domain=['&',('key','=',xml_id)]+current_website.website_domain()

            view=self.sudo().search(domain,order='website_id',limit=1)
            ifnotview:
                _logger.warning("Couldnotfindviewobjectwithxml_id'%s'",xml_id)
                raiseValueError('View%rinwebsite%rnotfound'%(xml_id,self._context['website_id']))
            returnview.id
        returnsuper(View,self.sudo()).get_view_id(xml_id)

    @api.model
    defread_template(self,xml_id):
        """Thismethodisdeprecated
        """
        view=self._view_obj(self.get_view_id(xml_id))
        ifview.visibilityandview._handle_visibility(do_raise=False):
            self=self.sudo()
        returnsuper(View,self).read_template(xml_id)

    def_get_original_view(self):
        """Givenaview,retrievetheoriginalviewitwasCOW'dfrom.
        Thegivenviewmightalreadybetheoriginalone.Inthatcaseitwill
        (andshould)returnitself.
        """
        self.ensure_one()
        domain=[('key','=',self.key),('model_data_id','!=',None)]
        returnself.with_context(active_test=False).search(domain,limit=1) #Uselesslimithasmultiplexmlidshouldnotbepossible

    def_handle_visibility(self,do_raise=True):
        """Checkthevisibilitysetonthemainviewandraise403ifyoushouldnothaveaccess.
            Orderis:Public,Connected,Hasgroup,Password

            Itonlycheckthevisibilityonthemaincontent,othersviewscalledstayavailableinrpc.
        """
        error=False

        self=self.sudo()

        ifself.visibilityandnotrequest.env.user.has_group('website.group_website_designer'):
            if(self.visibility=='connected'andrequest.website.is_public_user()):
                error=werkzeug.exceptions.Forbidden()
            elifself.visibility=='password'and\
                    (request.website.is_public_user()orself.idnotinrequest.session.get('views_unlock',[])):
                pwd=request.params.get('visibility_password')
                ifpwdandself.env.user._crypt_context().verify(
                        pwd,self.sudo().visibility_password):
                    request.session.setdefault('views_unlock',list()).append(self.id)
                else:
                    error=werkzeug.exceptions.Forbidden('website_visibility_password_required')

            ifself.visibilitynotin('password','connected'):
                try:
                    self._check_view_access()
                exceptAccessError:
                    error=werkzeug.exceptions.Forbidden()

        iferror:
            ifdo_raise:
                raiseerror
            else:
                returnFalse
        returnTrue

    def_render(self,values=None,engine='ir.qweb',minimal_qcontext=False):
        """Renderthetemplate.Ifwebsiteisenabledonrequest,thenextendrenderingcontextwithwebsitevalues."""
        self._handle_visibility(do_raise=True)
        new_context=dict(self._context)
        ifrequestandgetattr(request,'is_frontend',False):

            editable=request.website.is_publisher()
            translatable=editableandself._context.get('lang')!=request.website.default_lang_id.code
            editable=nottranslatableandeditable

            #ineditmodeir.ui.viewwilltagnodes
            ifnottranslatableandnotself.env.context.get('rendering_bundle'):
                ifeditable:
                    new_context=dict(self._context,inherit_branding=True)
                elifrequest.env.user.has_group('website.group_website_publisher'):
                    new_context=dict(self._context,inherit_branding_auto=True)
            ifvaluesand'main_object'invalues:
                ifrequest.env.user.has_group('website.group_website_publisher'):
                    func=getattr(values['main_object'],'get_backend_menu_id',False)
                    values['backend_menu_id']=funcandfunc()orself.env['ir.model.data'].xmlid_to_res_id('website.menu_website_configuration')

        ifself._context!=new_context:
            self=self.with_context(new_context)
        returnsuper(View,self)._render(values,engine=engine,minimal_qcontext=minimal_qcontext)

    @api.model
    def_prepare_qcontext(self):
        """Returnstheqcontext:renderingcontextwithwebsitespecificvalue(required
            torenderwebsitelayouttemplate)
        """
        qcontext=super(View,self)._prepare_qcontext()

        ifrequestandgetattr(request,'is_frontend',False):
            Website=self.env['website']
            editable=request.website.is_publisher()
            translatable=editableandself._context.get('lang')!=request.env['ir.http']._get_default_lang().code
            editable=nottranslatableandeditable

            cur=Website.get_current_website()
            ifself.env.user.has_group('website.group_website_publisher')andself.env.user.has_group('website.group_multi_website'):
                qcontext['multi_website_websites_current']={'website_id':cur.id,'name':cur.name,'domain':cur._get_http_domain()}
                qcontext['multi_website_websites']=[
                    {'website_id':website.id,'name':website.name,'domain':website._get_http_domain()}
                    forwebsiteinWebsite.search([])ifwebsite!=cur
                ]

                cur_company=self.env.company
                qcontext['multi_website_companies_current']={'company_id':cur_company.id,'name':cur_company.name}
                qcontext['multi_website_companies']=[
                    {'company_id':comp.id,'name':comp.name}
                    forcompinself.env.user.company_idsifcomp!=cur_company
                ]

            qcontext.update(dict(
                main_object=self,
                website=request.website,
                is_view_active=request.website.is_view_active,
                res_company=request.website.company_id.sudo(),
                translatable=translatable,
                editable=editable,
            ))

        returnqcontext

    @api.model
    defget_default_lang_code(self):
        website_id=self.env.context.get('website_id')
        ifwebsite_id:
            lang_code=self.env['website'].browse(website_id).default_lang_id.code
            returnlang_code
        else:
            returnsuper(View,self).get_default_lang_code()

    defredirect_to_page_manager(self):
        return{
            'type':'ir.actions.act_url',
            'url':'/website/pages',
            'target':'self',
        }

    def_read_template_keys(self):
        returnsuper(View,self)._read_template_keys()+['website_id']

    @api.model
    def_save_oe_structure_hook(self):
        res=super(View,self)._save_oe_structure_hook()
        res['website_id']=self.env['website'].get_current_website().id
        returnres

    @api.model
    def_set_noupdate(self):
        '''Ifwebsiteisinstalled,anycallto`save`fromthefrontendwill
        actuallywriteonthespecificview(orcreateitifnotexistyet).
        Inthatcase,wedon'twanttoflagthegenericviewasnoupdate.
        '''
        ifnotself._context.get('website_id'):
            super(View,self)._set_noupdate()

    defsave(self,value,xpath=None):
        self.ensure_one()
        current_website=self.env['website'].get_current_website()
        #xpathconditionisimportanttobesureweareeditingaviewandnot
        #afieldasinthatcase`self`mightnotexist(checkcommitmessage)
        ifxpathandself.keyandcurrent_website:
            #Thefirsttimeagenericviewisedited,ifmultipleeditableparts
            #wereeditedatthesametime,multiplecalltothismethodwillbe
            #donebutthefirstonemaycreateawebsitespecificview.Soifthere
            #alreadyisawebsitespecificview,weneedtodivertthesupertoit.
            website_specific_view=self.env['ir.ui.view'].search([
                ('key','=',self.key),
                ('website_id','=',current_website.id)
            ],limit=1)
            ifwebsite_specific_view:
                self=website_specific_view
        super(View,self).save(value,xpath=xpath)

    @api.model
    def_get_allowed_root_attrs(self):
        #Relatedtotheseoptions:
        #background-video,background-shapes,parallax
        returnsuper()._get_allowed_root_attrs()+[
            'data-bg-video-src','data-shape','data-scroll-background-ratio',
        ]

    #--------------------------------------------------------------------------
    #Snippetsaving
    #--------------------------------------------------------------------------

    @api.model
    def_snippet_save_view_values_hook(self):
        res=super()._snippet_save_view_values_hook()
        website_id=self.env.context.get('website_id')
        ifwebsite_id:
            res['website_id']=website_id
        returnres
