#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.http_routing.models.ir_httpimportslugify
fromflectraimportapi,fields,models
fromflectra.tools.safe_evalimportsafe_eval


classPage(models.Model):
    _name='website.page'
    _inherits={'ir.ui.view':'view_id'}
    _inherit='website.published.multi.mixin'
    _description='Page'
    _order='website_id'

    url=fields.Char('PageURL')
    view_id=fields.Many2one('ir.ui.view',string='View',required=True,ondelete="cascade")
    website_indexed=fields.Boolean('IsIndexed',default=True)
    date_publish=fields.Datetime('PublishingDate')
    #Thisisneededtobeabletodisplayifpageisamenuin/website/pages
    menu_ids=fields.One2many('website.menu','page_id','RelatedMenus')
    is_homepage=fields.Boolean(compute='_compute_homepage',inverse='_set_homepage',string='Homepage')
    is_visible=fields.Boolean(compute='_compute_visible',string='IsVisible')

    cache_time=fields.Integer(default=3600,help='Timetocachethepage.(0=nocache)')
    cache_key_expr=fields.Char(help='Expression(tuple)toevaluatethecachedkey.\nE.g.:"(request.params.get("currency"),)"')

    #Pageoptions
    header_overlay=fields.Boolean()
    header_color=fields.Char()
    header_visible=fields.Boolean(default=True)
    footer_visible=fields.Boolean(default=True)

    #don'tusemixinwebsite_idbutusewebsite_idonir.ui.viewinstead
    website_id=fields.Many2one(related='view_id.website_id',store=True,readonly=False,ondelete='cascade')
    arch=fields.Text(related='view_id.arch',readonly=False,depends_context=('website_id',))

    def_compute_homepage(self):
        forpageinself:
            page.is_homepage=page==self.env['website'].get_current_website().homepage_id

    def_set_homepage(self):
        forpageinself:
            website=self.env['website'].get_current_website()
            ifpage.is_homepage:
                ifwebsite.homepage_id!=page:
                    website.write({'homepage_id':page.id})
            else:
                ifwebsite.homepage_id==page:
                    website.write({'homepage_id':None})

    def_compute_visible(self):
        forpageinself:
            page.is_visible=page.website_publishedand(
                notpage.date_publishorpage.date_publish<fields.Datetime.now()
            )

    def_is_most_specific_page(self,page_to_test):
        '''Thiswilltestifpage_to_testisthemostspecificpageinself.'''
        pages_for_url=self.sorted(key=lambdap:notp.website_id).filtered(lambdapage:page.url==page_to_test.url)

        #thisworksbecausepagesare_order'edbywebsite_id
        most_specific_page=pages_for_url[0]

        returnmost_specific_page==page_to_test

    defget_page_properties(self):
        self.ensure_one()
        res=self.read([
            'id','view_id','name','url','website_published','website_indexed','date_publish',
            'menu_ids','is_homepage','website_id','visibility','groups_id'
        ])[0]
        ifnotres['groups_id']:
            res['group_id']=self.env.ref('base.group_user').name_get()[0]
        eliflen(res['groups_id'])==1:
            res['group_id']=self.env['res.groups'].browse(res['groups_id']).name_get()[0]
        delres['groups_id']

        res['visibility_password']=res['visibility']=='password'andself.visibility_password_displayor''
        returnres

    @api.model
    defsave_page_info(self,website_id,data):
        website=self.env['website'].browse(website_id)
        page=self.browse(int(data['id']))

        #IfURLhasbeenedited,slugit
        original_url=page.url
        url=data['url']
        ifnoturl.startswith('/'):
            url='/'+url
        ifpage.url!=url:
            url='/'+slugify(url,max_length=1024,path=True)
            url=self.env['website'].get_unique_path(url)

        #Ifnamehaschanged,checkforkeyuniqueness
        ifpage.name!=data['name']:
            page_key=self.env['website'].get_unique_key(slugify(data['name']))
        else:
            page_key=page.key

        menu=self.env['website.menu'].search([('page_id','=',int(data['id']))])
        ifnotdata['is_menu']:
            #Ifthepageisnolongerinmenu,weshouldremoveitswebsite_menu
            ifmenu:
                menu.unlink()
        else:
            #Thepageisnowamenu,checkifhasalreadyone
            ifmenu:
                menu.write({'url':url})
            else:
                self.env['website.menu'].create({
                    'name':data['name'],
                    'url':url,
                    'page_id':data['id'],
                    'parent_id':website.menu_id.id,
                    'website_id':website.id,
                })

        #Editsviathepagemanagershouldn'ttriggertheCOW
        #mechanismandgeneratenewpages.Theusermanagespage
        #visibilitymanuallywithis_publishedhere.
        w_vals={
            'key':page_key,
            'name':data['name'],
            'url':url,
            'is_published':data['website_published'],
            'website_indexed':data['website_indexed'],
            'date_publish':data['date_publish']orNone,
            'is_homepage':data['is_homepage'],
            'visibility':data['visibility'],
        }
        ifpage.visibility=='restricted_group'anddata['visibility']!="restricted_group":
            w_vals['groups_id']=False
        elif'group_id'indata:
            w_vals['groups_id']=[data['group_id']]
        if'visibility_pwd'indata:
            w_vals['visibility_password_display']=data['visibility_pwd']or''

        page.with_context(no_cow=True).write(w_vals)

        #Createredirectifneeded
        ifdata['create_redirect']:
            self.env['website.rewrite'].create({
                'name':data['name'],
                'redirect_type':data['redirect_type'],
                'url_from':original_url,
                'url_to':url,
                'website_id':website.id,
            })

        returnurl

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        ifdefault:
            ifnotdefault.get('view_id'):
                view=self.env['ir.ui.view'].browse(self.view_id.id)
                new_view=view.copy({'website_id':default.get('website_id')})
                default['view_id']=new_view.id

            default['url']=default.get('url',self.env['website'].get_unique_path(self.url))
        returnsuper(Page,self).copy(default=default)

    @api.model
    defclone_page(self,page_id,page_name=None,clone_menu=True):
        """Cloneapage,givenitsidentifier
            :parampage_id:website.pageidentifier
        """
        page=self.browse(int(page_id))
        copy_param=dict(name=page_nameorpage.name,website_id=self.env['website'].get_current_website().id)
        ifpage_name:
            page_url='/'+slugify(page_name,max_length=1024,path=True)
            copy_param['url']=self.env['website'].get_unique_path(page_url)

        new_page=page.copy(copy_param)
        #Shouldnotclonemenuifthepagewasclonedfromonewebsitetoanother
        #Eg:Cloningagenericpage(nowebsite)willcreateapagewithawebsite,wecan'tclonemenu(notsamecontainer)
        ifclone_menuandnew_page.website_id==page.website_id:
            menu=self.env['website.menu'].search([('page_id','=',page_id)],limit=1)
            ifmenu:
                #Ifthepagebeingclonedhasamenu,cloneittoo
                menu.copy({'url':new_page.url,'name':new_page.name,'page_id':new_page.id})

        returnnew_page.url+'?enable_editor=1'

    defunlink(self):
        #Whenawebsite_pageisdeleted,theORMdoesnotdeleteits
        #ir_ui_view.Sowegottodeleteitourself,butonlyifthe
        #ir_ui_viewisnotusedbyanotherwebsite_page.
        forpageinself:
            #Otherpageslinkedtotheir_ui_viewofthepagebeingdeleted(willitevenbepossible?)
            pages_linked_to_iruiview=self.search(
                [('view_id','=',page.view_id.id),('id','!=',page.id)]
            )
            ifnotpages_linked_to_iruiviewandnotpage.view_id.inherit_children_ids:
                #Ifthereisnootherpageslinkedtothatir_ui_view,wecandeletetheir_ui_view
                page.view_id.unlink()
        #Makesurewebsite._get_menu_ids()willberecomputed
        self.clear_caches()
        returnsuper(Page,self).unlink()

    defwrite(self,vals):
        if'url'invalsandnotvals['url'].startswith('/'):
            vals['url']='/'+vals['url']
        self.clear_caches() #writeonpage==writeonviewthatinvalidcache
        returnsuper(Page,self).write(vals)

    defget_website_meta(self):
        self.ensure_one()
        returnself.view_id.get_website_meta()

    @staticmethod
    def_get_cached_blacklist():
        return('data-snippet="s_website_form"','data-no-page-cache=',)

    def_can_be_cached(self,response):
        """returnFalseifatleastoneblacklisted'swordispresentincontent"""
        blacklist=self._get_cached_blacklist()
        returnnotany(blackinstr(response)forblackinblacklist)

    def_get_cache_key(self,req):
        #Alwayscallmewithsuper()ATTHEENDtohavecache_key_exprappendedaslastelement
        #Itistheonlywayforendusertonotusecacheviaexpr.
        #E.g (Noneif'token'inrequest.paramselse1,) willbypasscache_time
        cache_key=(req.website.id,req.lang,req.httprequest.path)
        ifself.cache_key_expr: #e.g.(request.session.geoip.get('country_code'),)
            cache_key+=safe_eval(self.cache_key_expr,{'request':req})
        returncache_key

    def_get_cache_response(self,cache_key):
        """Returnthecachedresponsecorrespondingto``self``and``cache_key``.
        RaiseaKeyErroriftheitemisnotincache.
        """
        #HACK:weusethesameLRUasormcachetotakeadvantagefromits
        #distributedinvalidation,butwedon'texplicitlyuseormcache
        returnself.pool._Registry__cache[('website.page',_cached_response,self.id,cache_key)]

    def_set_cache_response(self,cache_key,response):
        """Putincachethegivenresponse."""
        self.pool._Registry__cache[('website.page',_cached_response,self.id,cache_key)]=response


#thisisjustadummyfunctiontobeusedasormcachekey
def_cached_response():
    pass
