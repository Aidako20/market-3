#coding:utf-8
fromlxmlimporthtml

fromflectra.addons.website.controllers.mainimportWebsite
fromflectra.addons.website.toolsimportMockRequest
fromflectra.testsimportcommon,HttpCase,tagged
fromflectra.tests.commonimportHOST
fromflectra.toolsimportconfig


@tagged('-at_install','post_install')
classTestPage(common.TransactionCase):
    defsetUp(self):
        super(TestPage,self).setUp()
        View=self.env['ir.ui.view']
        Page=self.env['website.page']
        Menu=self.env['website.menu']

        self.base_view=View.create({
            'name':'Base',
            'type':'qweb',
            'arch':'<div>content</div>',
            'key':'test.base_view',
        })

        self.extension_view=View.create({
            'name':'Extension',
            'mode':'extension',
            'inherit_id':self.base_view.id,
            'arch':'<divposition="inside">,extendedcontent</div>',
            'key':'test.extension_view',
        })

        self.page_1=Page.create({
            'view_id':self.base_view.id,
            'url':'/page_1',
        })

        self.page_1_menu=Menu.create({
            'name':'Page1menu',
            'page_id':self.page_1.id,
            'website_id':1,
        })

    deftest_copy_page(self):
        View=self.env['ir.ui.view']
        Page=self.env['website.page']
        Menu=self.env['website.menu']
        #Specificpage
        self.specific_view=View.create({
            'name':'Base',
            'type':'qweb',
            'arch':'<div>SpecificView</div>',
            'key':'test.specific_view',
        })
        self.page_specific=Page.create({
            'view_id':self.specific_view.id,
            'url':'/page_specific',
            'website_id':1,
        })
        self.page_specific_menu=Menu.create({
            'name':'PageSpecificmenu',
            'page_id':self.page_specific.id,
            'website_id':1,
        })
        total_pages=Page.search_count([])
        total_menus=Menu.search_count([])
        #CopyingaspecificpageshouldcreateanewpagewithanuniqueURL(suffixedby-X)
        Page.clone_page(self.page_specific.id,clone_menu=True)
        cloned_page=Page.search([('url','=','/page_specific-1')])
        cloned_menu=Menu.search([('url','=','/page_specific-1')])
        self.assertEqual(len(cloned_page),1,"ApagewithanURL/page_specific-1should'vebeencreated")
        self.assertEqual(Page.search_count([]),total_pages+1,"Shouldhaveclonedthepage")
        #Itshouldalsocopyitsmenuwithnewurl/name/page_id(ifthepagehasamenu)
        self.assertEqual(len(cloned_menu),1,"Aspecificpage(withamenu)beingclonedshouldhaveit'smenualsocloned")
        self.assertEqual(cloned_menu.page_id,cloned_page,"Thenewclonedmenuandthenewclonedpageshouldbelinked(m2o)")
        self.assertEqual(Menu.search_count([]),total_menus+1,"Shouldhaveclonedthepagemenu")
        Page.clone_page(self.page_specific.id,page_name="about-us",clone_menu=True)
        cloned_page_about_us=Page.search([('url','=','/about-us')])
        cloned_menu_about_us=Menu.search([('url','=','/about-us')])
        self.assertEqual(len(cloned_page_about_us),1,"ApagewithanURL/about-usshould'vebeencreated")
        self.assertEqual(len(cloned_menu_about_us),1,"Aspecificpage(withamenu)beingclonedshouldhaveit'smenualsocloned")
        self.assertEqual(cloned_menu_about_us.page_id,cloned_page_about_us,"Thenewclonedmenuandthenewclonedpageshouldbelinked(m2o)")
        #Itshouldalsocopyitsmenuwithnewurl/name/page_id(ifthepagehasamenu)
        self.assertEqual(Menu.search_count([]),total_menus+2,"Shouldhaveclonedthepagemenu")

        total_pages=Page.search_count([])
        total_menus=Menu.search_count([])

        #CopyingagenericpageshouldcreateaspecificpagewithsameURL
        Page.clone_page(self.page_1.id,clone_menu=True)
        cloned_generic_page=Page.search([('url','=','/page_1'),('id','!=',self.page_1.id),('website_id','!=',False)])
        self.assertEqual(len(cloned_generic_page),1,"Agenericpagebeingclonedshouldcreateaspecificoneforthecurrentwebsite")
        self.assertEqual(cloned_generic_page.url,self.page_1.url,"TheURLoftheclonedspecificpageshouldbethesameasthegenericpageithasbeenclonedfrom")
        self.assertEqual(Page.search_count([]),total_pages+1,"Shouldhaveclonedthegenericpageasaspecificpageforthiswebsite")
        self.assertEqual(Menu.search_count([]),total_menus,"Itshouldnotcreateanewmenuasthegenericpage'smenubelongtoanotherwebsite")
        #ExceptiftheURLalreadyexistsforthiswebsite(itsthecasenowthatwealreadycloneditonce)
        Page.clone_page(self.page_1.id,clone_menu=True)
        cloned_generic_page_2=Page.search([('url','=','/page_1-1'),('id','!=',self.page_1.id)])
        self.assertEqual(len(cloned_generic_page_2),1,"AgenericpagebeingclonedshouldcreateaspecificpagewithanewURLifthereisalreadyaspecificpagewiththatURL")

    deftest_cow_page(self):
        Menu=self.env['website.menu']
        Page=self.env['website.page']
        View=self.env['ir.ui.view']

        #backendwrite,noCOW
        total_pages=Page.search_count([])
        total_menus=Menu.search_count([])
        total_views=View.search_count([])
        self.page_1.write({'arch':'<div>modifiedbasecontent</div>'})
        self.assertEqual(total_pages,Page.search_count([]))
        self.assertEqual(total_menus,Menu.search_count([]))
        self.assertEqual(total_views,View.search_count([]))

        #editthroughfrontend
        self.page_1.with_context(website_id=1).write({'arch':'<div>website1content</div>'})

        #1.shouldhavecreatedwebsite-specificcopiesfor:
        #   -page
        #   -viewx2(baseview+extensionview)
        #2.shouldnothavecreatedmenucopyasmenusarenotshared/COW
        #3.andshouldn'thavetouchedoriginalrecords
        self.assertEqual(total_pages+1,Page.search_count([]))
        self.assertEqual(total_menus,Menu.search_count([]))
        self.assertEqual(total_views+2,View.search_count([]))

        self.assertEqual(self.page_1.arch,'<div>modifiedbasecontent</div>')
        self.assertEqual(bool(self.page_1.website_id),False)

        new_page=Page.search([('url','=','/page_1'),('id','!=',self.page_1.id)])
        self.assertEqual(new_page.website_id.id,1)
        self.assertEqual(new_page.view_id.inherit_children_ids[0].website_id.id,1)
        self.assertEqual(new_page.arch,'<div>website1content</div>')

    deftest_cow_extension_view(self):
        '''testcowonextensionviewitself(likeweb_editorwoulddointhefrontend)'''
        Menu=self.env['website.menu']
        Page=self.env['website.page']
        View=self.env['ir.ui.view']

        #nothingspecialshouldhappenwheneditingthroughthebackend
        total_pages=Page.search_count([])
        total_menus=Menu.search_count([])
        total_views=View.search_count([])
        self.extension_view.write({'arch':'<div>modifiedextensioncontent</div>'})
        self.assertEqual(self.extension_view.arch,'<div>modifiedextensioncontent</div>')
        self.assertEqual(total_pages,Page.search_count([]))
        self.assertEqual(total_menus,Menu.search_count([]))
        self.assertEqual(total_views,View.search_count([]))

        #Wheneditingthroughthefrontendawebsite-specificcopy
        #fortheextensionviewshouldbecreated.Whenrenderingthe
        #originalwebsite.pageonwebsite1itwilllookdifferently
        #duetothisnewextensionview.
        self.extension_view.with_context(website_id=1).write({'arch':'<div>website1content</div>'})
        self.assertEqual(total_pages,Page.search_count([]))
        self.assertEqual(total_menus,Menu.search_count([]))
        self.assertEqual(total_views+1,View.search_count([]))

        self.assertEqual(self.extension_view.arch,'<div>modifiedextensioncontent</div>')
        self.assertEqual(bool(self.page_1.website_id),False)

        new_view=View.search([('name','=','Extension'),('website_id','=',1)])
        self.assertEqual(new_view.arch,'<div>website1content</div>')
        self.assertEqual(new_view.website_id.id,1)

    deftest_cou_page_backend(self):
        Page=self.env['website.page']
        View=self.env['ir.ui.view']

        #currentlytheviewunlinkofwebsite.pagecan'thandleviewswithinheritedviews
        self.extension_view.unlink()

        self.page_1.unlink()
        self.assertEqual(Page.search_count([('url','=','/page_1')]),0)
        self.assertEqual(View.search_count([('name','in',('Base','Extension'))]),0)

    deftest_cou_page_frontend(self):
        Page=self.env['website.page']
        View=self.env['ir.ui.view']
        Website=self.env['website']

        website2=self.env['website'].create({
            'name':'MySecondWebsite',
            'domain':'',
        })

        #currentlytheviewunlinkofwebsite.pagecan'thandleviewswithinheritedviews
        self.extension_view.unlink()

        website_id=1
        self.page_1.with_context(website_id=website_id).unlink()

        self.assertEqual(bool(self.base_view.exists()),False)
        self.assertEqual(bool(self.page_1.exists()),False)
        #NotCOUbutdeletingapagewilldeleteitsmenu(cascade)
        self.assertEqual(bool(self.page_1_menu.exists()),False)

        pages=Page.search([('url','=','/page_1')])
        self.assertEqual(len(pages),Website.search_count([])-1,"Aspecificpageforeverywebsiteshouldhavebeencreated,exceptfortheonefromwherewedeletedthegenericone.")
        self.assertTrue(website_idnotinpages.mapped('website_id').ids,"Thewebsitefromwhichwedeletedthegenericpageshouldnothaveaspecificone.")
        self.assertTrue(website_idnotinView.search([('name','in',('Base','Extension'))]).mapped('website_id').ids,"Sameforviews")

@tagged('-at_install','post_install')
classWithContext(HttpCase):
    defsetUp(self):
        super().setUp()
        Page=self.env['website.page']
        View=self.env['ir.ui.view']
        base_view=View.create({
            'name':'Base',
            'type':'qweb',
            'arch':'''<tname="Homepage"t-name="website.base_view">
                        <tt-call="website.layout">
                            Iamagenericpage
                        </t>
                    </t>''',
            'key':'test.base_view',
        })
        self.page=Page.create({
            'view_id':base_view.id,
            'url':'/page_1',
            'is_published':True,
        })

    deftest_unpublished_page(self):
        specific_page=self.page.copy({'website_id':self.env['website'].get_current_website().id})
        specific_page.write({'is_published':False,'arch':self.page.arch.replace('Iamagenericpage','Iamaspecificpage')})

        self.authenticate(None,None)
        r=self.url_open(specific_page.url)
        self.assertEqual(r.status_code,404,"Restrictedusersshouldseea404andnotthegenericoneasweunpublishedthespecificone")

        self.authenticate('admin','admin')
        r=self.url_open(specific_page.url)
        self.assertEqual(r.status_code,200,"Adminshouldseethespecificunpublishedpage")
        self.assertEqual('Iamaspecificpage'inr.text,True,"Adminshouldseethespecificunpublishedpage")

    deftest_search(self):
        dbname=common.get_db_name()
        admin_uid=self.env.ref('base.user_admin').id
        website=self.env['website'].get_current_website()

        robot=self.xmlrpc_object.execute(
            dbname,admin_uid,'admin',
            'website','search_pages',[website.id],'info'
        )
        self.assertIn({'loc':'/website/info'},robot)

        pages=self.xmlrpc_object.execute(
            dbname,admin_uid,'admin',
            'website','search_pages',[website.id],'page'
        )
        self.assertIn(
            '/page_1',
            [p['loc']forpinpages],
        )

    deftest_homepage_not_slash_url(self):
        website=self.env['website'].browse([1])
        #Setanotherpage(/page_1)ashomepage
        website.write({
            'homepage_id':self.page.id,
            'domain':f"http://{HOST}:{config['http_port']}",
        })
        assertself.page.url!='/'

        r=self.url_open('/')
        r.raise_for_status()
        self.assertEqual(r.status_code,200,
                         "Thereshouldbenocrashwhenapublicuserisaccessing`/`whichisreroutingtoanotherpagewithadifferentURL.")
        root_html=html.fromstring(r.content)
        canonical_url=root_html.xpath('//link[@rel="canonical"]')[0].attrib['href']
        self.assertEqual(canonical_url,website.domain+"/")

    deftest_page_url_case_insensitive_match(self):
        r=self.url_open('/page_1')
        self.assertEqual(r.status_code,200,"ReachingpageURL,commoncase")
        r2=self.url_open('/Page_1',allow_redirects=False)
        self.assertEqual(r2.status_code,302,"URLexistsonlyindifferentcasing,shouldredirecttoit")
        self.assertTrue(r2.headers.get('Location').endswith('/page_1'),"Shouldredirect/Page_1to/page_1")

@tagged('-at_install','post_install')
classTestNewPage(common.TransactionCase):
    deftest_new_page_used_key(self):
        website=self.env.ref('website.default_website')
        controller=Website()
        withMockRequest(self.env,website=website):
            controller.pagenew(path="snippets")
        pages=self.env['website.page'].search([('url','=','/snippets')])
        self.assertEqual(len(pages),1,"Exactlyonepageshouldbeat/snippets.")
        self.assertNotEqual(pages.key,"website.snippets","Page'skeycannotbewebsite.snippets.")
