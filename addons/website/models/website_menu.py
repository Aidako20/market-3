#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug.exceptions
importwerkzeug.urls

fromflectraimportapi,fields,models
fromflectra.httpimportrequest
fromflectra.tools.translateimporthtml_translate


classMenu(models.Model):

    _name="website.menu"
    _description="WebsiteMenu"

    _parent_store=True
    _order="sequence,id"

    def_default_sequence(self):
        menu=self.search([],limit=1,order="sequenceDESC")
        returnmenu.sequenceor0

    def_compute_field_is_mega_menu(self):
        formenuinself:
            menu.is_mega_menu=bool(menu.mega_menu_content)

    def_set_field_is_mega_menu(self):
        formenuinself:
            ifmenu.is_mega_menu:
                ifnotmenu.mega_menu_content:
                    default_content=self.env['ir.ui.view']._render_template('website.s_mega_menu_multi_menus')
                    menu.mega_menu_content=default_content.decode()
            else:
                menu.mega_menu_content=False
                menu.mega_menu_classes=False

    name=fields.Char('Menu',required=True,translate=True)
    url=fields.Char('Url',default='')
    page_id=fields.Many2one('website.page','RelatedPage',ondelete='cascade')
    new_window=fields.Boolean('NewWindow')
    sequence=fields.Integer(default=_default_sequence)
    website_id=fields.Many2one('website','Website',ondelete='cascade')
    parent_id=fields.Many2one('website.menu','ParentMenu',index=True,ondelete="cascade")
    child_id=fields.One2many('website.menu','parent_id',string='ChildMenus')
    parent_path=fields.Char(index=True)
    is_visible=fields.Boolean(compute='_compute_visible',string='IsVisible')
    group_ids=fields.Many2many('res.groups',string='VisibleGroups',
                                 help="Userneedtobeatleastinoneofthesegroupstoseethemenu")
    is_mega_menu=fields.Boolean(compute=_compute_field_is_mega_menu,inverse=_set_field_is_mega_menu)
    mega_menu_content=fields.Html(translate=html_translate,sanitize=False,prefetch=True)
    mega_menu_classes=fields.Char()

    defname_get(self):
        ifnotself._context.get('display_website')andnotself.env.user.has_group('website.group_multi_website'):
            returnsuper(Menu,self).name_get()

        res=[]
        formenuinself:
            menu_name=menu.name
            ifmenu.website_id:
                menu_name+='[%s]'%menu.website_id.name
            res.append((menu.id,menu_name))
        returnres

    @api.model
    defcreate(self,vals):
        '''Incaseamenuwithoutawebsite_idistryingtobecreated,weduplicate
            itforeverywebsite.
            Note:Particularyusefulwheninstallingamodulethataddsamenulike
                  /shop.Soeverywebsitehastheshopmenu.
                  Becarefultoreturncorrectrecordforir.model.dataxml_idincase
                  ofdefaultmainmenuscreation.
        '''
        self.clear_caches()
        #Onlyusedwhencreatingwebsite_data.xmldefaultmenu
        ifvals.get('url')=='/default-main-menu':
            returnsuper(Menu,self).create(vals)

        if'website_id'invals:
            returnsuper(Menu,self).create(vals)
        elifself._context.get('website_id'):
            vals['website_id']=self._context.get('website_id')
            returnsuper(Menu,self).create(vals)
        else:
            #createforeverysite
            forwebsiteinself.env['website'].search([]):
                w_vals=dict(vals,**{
                    'website_id':website.id,
                    'parent_id':website.menu_id.id,
                })
                res=super(Menu,self).create(w_vals)
            #ifcreatingadefaultmenu,weshouldalsosaveitassuch
            default_menu=self.env.ref('website.main_menu',raise_if_not_found=False)
            ifdefault_menuandvals.get('parent_id')==default_menu.id:
                res=super(Menu,self).create(vals)
        returnres #Onlyonerecordisreturnedbutmultiplecouldhavebeencreated

    defwrite(self,values):
        res=super().write(values)
        if'website_id'invaluesor'group_ids'invaluesor'sequence'invalues:
            self.clear_caches()
        returnres

    defunlink(self):
        self.clear_caches()
        default_menu=self.env.ref('website.main_menu',raise_if_not_found=False)
        menus_to_remove=self
        formenuinself.filtered(lambdam:default_menuandm.parent_id.id==default_menu.id):
            menus_to_remove|=self.env['website.menu'].search([('url','=',menu.url),
                                                                ('website_id','!=',False),
                                                                ('id','!=',menu.id)])
        returnsuper(Menu,menus_to_remove).unlink()

    def_compute_visible(self):
        formenuinself:
            visible=True
            ifmenu.page_idandnotmenu.user_has_groups('base.group_user'):
                page_sudo=menu.page_id.sudo()
                if(notpage_sudo.is_visible
                    or(notpage_sudo.view_id._handle_visibility(do_raise=False)
                        andpage_sudo.view_id.visibility!="password")):
                    visible=False
            menu.is_visible=visible

    @api.model
    defclean_url(self):
        #cleantheurlwithheuristic
        ifself.page_id:
            url=self.page_id.sudo().url
        else:
            url=self.url
            ifurlandnotself.url.startswith('/'):
                if'@'inself.url:
                    ifnotself.url.startswith('mailto'):
                        url='mailto:%s'%self.url
                elifnotself.url.startswith('http'):
                    url='/%s'%self.url
        returnurl

    #wouldbebettertotakeamenu_idasargument
    @api.model
    defget_tree(self,website_id,menu_id=None):
        defmake_tree(node):
            is_homepage=bool(node.page_idandself.env['website'].browse(website_id).homepage_id.id==node.page_id.id)
            menu_node={
                'fields':{
                    'id':node.id,
                    'name':node.name,
                    'url':node.page_id.urlifnode.page_idelsenode.url,
                    'new_window':node.new_window,
                    'is_mega_menu':node.is_mega_menu,
                    'sequence':node.sequence,
                    'parent_id':node.parent_id.id,
                },
                'children':[],
                'is_homepage':is_homepage,
            }
            forchildinnode.child_id:
                menu_node['children'].append(make_tree(child))
            returnmenu_node

        menu=menu_idandself.browse(menu_id)orself.env['website'].browse(website_id).menu_id
        returnmake_tree(menu)

    @api.model
    defsave(self,website_id,data):
        defreplace_id(old_id,new_id):
            formenuindata['data']:
                ifmenu['id']==old_id:
                    menu['id']=new_id
                ifmenu['parent_id']==old_id:
                    menu['parent_id']=new_id
        to_delete=data['to_delete']
        ifto_delete:
            self.browse(to_delete).unlink()
        formenuindata['data']:
            mid=menu['id']
            #newmenuareprefixedbynew-
            ifisinstance(mid,str):
                new_menu=self.create({'name':menu['name'],'website_id':website_id})
                replace_id(mid,new_menu.id)
        formenuindata['data']:
            menu_id=self.browse(menu['id'])
            #Checkiftheurlmatchawebsite.page(tosetthem2orelation),
            #exceptifthemenuurlcontains'#',wethenunsetthepage_id
            if'#'inmenu['url']:
                #Multiplecasepossible
                #1.`#`=>menucontainer(dropdown,..)
                #2.`#anchor`=>anchoroncurrentpage
                #3.`/url#something`=>validinternalURL
                #4.https://google.com#smth=>validexternalURL
                ifmenu_id.page_id:
                    menu_id.page_id=None
                ifrequestandmenu['url'].startswith('#')andlen(menu['url'])>1:
                    #Workingoncase2.:prefixanchorwithrefererURL
                    referer_url=werkzeug.urls.url_parse(request.httprequest.headers.get('Referer','')).path
                    menu['url']=referer_url+menu['url']
            else:
                domain=self.env["website"].website_domain(website_id)+[
                    "|",
                    ("url","=",menu["url"]),
                    ("url","=","/"+menu["url"]),
                ]
                page=self.env["website.page"].search(domain,limit=1)
                ifpage:
                    menu['page_id']=page.id
                    menu['url']=page.url
                elifmenu_id.page_id:
                    try:
                        #apageshouldn'thavethesameurlasacontroller
                        rule,arguments=self.env['ir.http']._match(menu['url'])
                        menu_id.page_id=None
                    exceptwerkzeug.exceptions.NotFound:
                        menu_id.page_id.write({'url':menu['url']})
            menu_id.write(menu)

        returnTrue
