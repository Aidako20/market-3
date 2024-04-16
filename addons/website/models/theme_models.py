#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importthreading
fromflectraimportapi,fields,models
fromflectra.tools.translateimportxml_translate
fromflectra.modules.moduleimportget_resource_from_path

_logger=logging.getLogger(__name__)


classThemeView(models.Model):
    _name='theme.ir.ui.view'
    _description='ThemeUIView'

    defcompute_arch_fs(self):
        if'install_filename'notinself._context:
            return''
        path_info=get_resource_from_path(self._context['install_filename'])
        ifpath_info:
            return'/'.join(path_info[0:2])

    name=fields.Char(required=True)
    key=fields.Char()
    type=fields.Char()
    priority=fields.Integer(default=16,required=True)
    mode=fields.Selection([('primary',"Baseview"),('extension',"ExtensionView")])
    active=fields.Boolean(default=True)
    arch=fields.Text(translate=xml_translate)
    arch_fs=fields.Char(default=compute_arch_fs)
    inherit_id=fields.Reference(selection=[('ir.ui.view','ir.ui.view'),('theme.ir.ui.view','theme.ir.ui.view')])
    copy_ids=fields.One2many('ir.ui.view','theme_template_id','Viewsusingacopyofme',copy=False,readonly=True)
    customize_show=fields.Boolean()

    def_convert_to_base_model(self,website,**kwargs):
        self.ensure_one()
        inherit=self.inherit_id
        ifself.inherit_idandself.inherit_id._name=='theme.ir.ui.view':
            inherit=self.inherit_id.with_context(active_test=False).copy_ids.filtered(lambdax:x.website_id==website)
            ifnotinherit:
                #inherit_idnotyetcreated,addtothequeue
                returnFalse

        ifinheritandinherit.website_id!=website:
            website_specific_inherit=self.env['ir.ui.view'].with_context(active_test=False).search([
                ('key','=',inherit.key),
                ('website_id','=',website.id)
            ],limit=1)
            ifwebsite_specific_inherit:
                inherit=website_specific_inherit

        new_view={
            'type':self.typeor'qweb',
            'name':self.name,
            'arch':self.arch,
            'key':self.key,
            'inherit_id':inheritandinherit.id,
            'arch_fs':self.arch_fs,
            'priority':self.priority,
            'active':self.active,
            'theme_template_id':self.id,
            'website_id':website.id,
            'customize_show':self.customize_show,
        }

        ifself.mode: #ifnotprovided,itwillbecomputedautomatically(ifinherit_idornot)
            new_view['mode']=self.mode

        returnnew_view


classThemeAttachment(models.Model):
    _name='theme.ir.attachment'
    _description='ThemeAttachments'

    name=fields.Char(required=True)
    key=fields.Char(required=True)
    url=fields.Char()
    copy_ids=fields.One2many('ir.attachment','theme_template_id','Attachmentusingacopyofme',copy=False,readonly=True)


    def_convert_to_base_model(self,website,**kwargs):
        self.ensure_one()
        new_attach={
            'key':self.key,
            'public':True,
            'res_model':'ir.ui.view',
            'type':'url',
            'name':self.name,
            'url':self.url,
            'website_id':website.id,
            'theme_template_id':self.id,
        }
        returnnew_attach


classThemeMenu(models.Model):
    _name='theme.website.menu'
    _description='WebsiteThemeMenu'

    name=fields.Char(required=True,translate=True)
    url=fields.Char(default='')
    page_id=fields.Many2one('theme.website.page',ondelete='cascade')
    new_window=fields.Boolean('NewWindow')
    sequence=fields.Integer()
    parent_id=fields.Many2one('theme.website.menu',index=True,ondelete="cascade")
    copy_ids=fields.One2many('website.menu','theme_template_id','Menuusingacopyofme',copy=False,readonly=True)

    def_convert_to_base_model(self,website,**kwargs):
        self.ensure_one()
        page_id=self.page_id.copy_ids.filtered(lambdax:x.website_id==website)
        parent_id=self.parent_id.copy_ids.filtered(lambdax:x.website_id==website)
        new_menu={
            'name':self.name,
            'url':self.url,
            'page_id':page_idandpage_id.idorFalse,
            'new_window':self.new_window,
            'sequence':self.sequence,
            'parent_id':parent_idandparent_id.idorFalse,
            'website_id':website.id,
            'theme_template_id':self.id,
        }
        returnnew_menu


classThemePage(models.Model):
    _name='theme.website.page'
    _description='WebsiteThemePage'

    url=fields.Char()
    view_id=fields.Many2one('theme.ir.ui.view',required=True,ondelete="cascade")
    website_indexed=fields.Boolean('PageIndexed',default=True)
    copy_ids=fields.One2many('website.page','theme_template_id','Pageusingacopyofme',copy=False,readonly=True)

    def_convert_to_base_model(self,website,**kwargs):
        self.ensure_one()
        view_id=self.view_id.copy_ids.filtered(lambdax:x.website_id==website)
        ifnotview_id:
            #inherit_idnotyetcreated,addtothequeue
            returnFalse

        new_page={
            'url':self.url,
            'view_id':view_id.id,
            'website_indexed':self.website_indexed,
            'website_id':website.id,
            'theme_template_id':self.id,
        }
        returnnew_page


classTheme(models.AbstractModel):
    _name='theme.utils'
    _description='ThemeUtils'
    _auto=False

    _header_templates=[
        'website.template_header_hamburger',
        'website.template_header_vertical',
        'website.template_header_sidebar',
        'website.template_header_slogan',
        'website.template_header_contact',
        'website.template_header_minimalist',
        'website.template_header_boxed',
        'website.template_header_centered_logo',
        'website.template_header_image',
        'website.template_header_hamburger_full',
        'website.template_header_magazine',
        #Defaultone,keepitlast
        'website.template_header_default',
    ]
    _footer_templates=[
        'website.template_footer_descriptive',
        'website.template_footer_centered',
        'website.template_footer_links',
        'website.template_footer_minimalist',
        'website.template_footer_contact',
        'website.template_footer_call_to_action',
        'website.template_footer_headline',
        #Defaultone,keepitlast
        'website.footer_custom',
    ]

    def_post_copy(self,mod):
        #Callspecificthemepostcopy
        theme_post_copy='_%s_post_copy'%mod.name
        ifhasattr(self,theme_post_copy):
            _logger.info('Executingmethod%s'%theme_post_copy)
            method=getattr(self,theme_post_copy)
            returnmethod(mod)
        returnFalse

    @api.model
    def_reset_default_config(self):
        #Reinitializesomecsscustomizations
        self.env['web_editor.assets'].make_scss_customization(
            '/website/static/src/scss/options/user_values.scss',
            {
                'font':'null',
                'headings-font':'null',
                'navbar-font':'null',
                'buttons-font':'null',
                'color-palettes-number':'null',
                'btn-ripple':'null',
                'header-template':'null',
                'footer-template':'null',
                'footer-scrolltop':'null',
            }
        )

        #Reinitializeeffets
        self.disable_view('website.option_ripple_effect')

        #Reinitializeheadertemplates
        forviewinself._header_templates[:-1]:
            self.disable_view(view)
        self.enable_view(self._header_templates[-1])

        #Reinitializefootertemplates
        forviewinself._footer_templates[:-1]:
            self.disable_view(view)
        self.enable_view(self._footer_templates[-1])

        #Reinitializefooterscrolltoptemplate
        self.disable_view('website.option_footer_scrolltop')

    @api.model
    def_toggle_view(self,xml_id,active):
        obj=self.env.ref(xml_id)
        website=self.env['website'].get_current_website()
        ifobj._name=='theme.ir.ui.view':
            obj=obj.with_context(active_test=False)
            obj=obj.copy_ids.filtered(lambdax:x.website_id==website)
        else:
            #Ifathemepostcopywantstoenable/disableaview,thisisto
            #enable/disableagivenfunctionalitywhichisdisabled/enabled
            #bydefault.Soifapostcopyaskstoenable/disableaviewwhich
            #isalreadyenabled/disabled,wewouldnotconsideritotherwiseit
            #wouldCOWtheviewfornothing.
            View=self.env['ir.ui.view'].with_context(active_test=False)
            has_specific=obj.keyandView.search_count([
                ('key','=',obj.key),
                ('website_id','=',website.id)
            ])>=1
            ifnothas_specificandactive==obj.active:
                return
        obj.write({'active':active})

    @api.model
    defenable_view(self,xml_id):
        ifxml_idinself._header_templates:
            forviewinself._header_templates:
                self.disable_view(view)
        elifxml_idinself._footer_templates:
            forviewinself._footer_templates:
                self.disable_view(view)
        self._toggle_view(xml_id,True)

    @api.model
    defdisable_view(self,xml_id):
        self._toggle_view(xml_id,False)

    @api.model
    defenable_header_off_canvas(self):
        """Enablingoffcanvasrequiretoenablequitealotoftemplateso
            thisshortcutwasmadetomakeiteasier.
        """
        self.enable_view("website.option_header_off_canvas")
        self.enable_view("website.option_header_off_canvas_template_header_hamburger")
        self.enable_view("website.option_header_off_canvas_template_header_sidebar")
        self.enable_view("website.option_header_off_canvas_template_header_hamburger_full")


classIrUiView(models.Model):
    _inherit='ir.ui.view'

    theme_template_id=fields.Many2one('theme.ir.ui.view',copy=False)

    defwrite(self,vals):
        #Duringathememoduleupdate,themeviews'copiesreceivinganarch
        #updateshouldnotbeconsideredas`arch_updated`,asthisisnota
        #usermadechange.
        test_mode=getattr(threading.currentThread(),'testing',False)
        ifnot(test_modeorself.pool._init):
            returnsuper().write(vals)
        no_arch_updated_views=other_views=self.env['ir.ui.view']
        forrecordinself:
            #Donotmarktheviewasuserupdatediforiginalviewarchissimilar
            arch=vals.get('arch',vals.get('arch_base'))
            ifrecord.theme_template_idandrecord.theme_template_id.arch==arch:
                no_arch_updated_views+=record
            else:
                other_views+=record
        res=super(IrUiView,other_views).write(vals)
        ifno_arch_updated_views:
            vals['arch_updated']=False
            res&=super(IrUiView,no_arch_updated_views).write(vals)
        returnres

classIrAttachment(models.Model):
    _inherit='ir.attachment'

    key=fields.Char(copy=False)
    theme_template_id=fields.Many2one('theme.ir.attachment',copy=False)


classWebsiteMenu(models.Model):
    _inherit='website.menu'

    theme_template_id=fields.Many2one('theme.website.menu',copy=False)


classWebsitePage(models.Model):
    _inherit='website.page'

    theme_template_id=fields.Many2one('theme.website.page',copy=False)
