#coding:utf-8

importjson

fromflectra.testsimportcommon


classTestMenu(common.TransactionCase):
    defsetUp(self):
        super(TestMenu,self).setUp()
        self.nb_website=self.env['website'].search_count([])

    deftest_01_menu_got_duplicated(self):
        Menu=self.env['website.menu']
        total_menu_items=Menu.search_count([])

        self.menu_root=Menu.create({
            'name':'Root',
        })

        self.menu_child=Menu.create({
            'name':'Child',
            'parent_id':self.menu_root.id,
        })

        self.assertEqual(total_menu_items+self.nb_website*2,Menu.search_count([]),"Creatingamenuwithoutawebsite_idshouldcreatethismenuforeverywebsite_id")

    deftest_02_menu_count(self):
        Menu=self.env['website.menu']
        total_menu_items=Menu.search_count([])

        top_menu=self.env['website'].get_current_website().menu_id
        data=[
            {
                'id':'new-1',
                'parent_id':top_menu.id,
                'name':'NewMenuSpecific1',
                'url':'/new-specific-1',
                'is_mega_menu':False,
            },
            {
                'id':'new-2',
                'parent_id':top_menu.id,
                'name':'NewMenuSpecific2',
                'url':'/new-specific-2',
                'is_mega_menu':False,
            }
        ]
        Menu.save(1,{'data':data,'to_delete':[]})

        self.assertEqual(total_menu_items+2,Menu.search_count([]),"Creating2newmenusshouldcreateonly2menusrecords")

    deftest_03_default_menu_for_new_website(self):
        Website=self.env['website']
        Menu=self.env['website.menu']
        total_menu_items=Menu.search_count([])

        #Simulatingwebsite.menucreatedonmoduleinstall(blog,shop,forum..)thatwillbecreatedondefaultmenutree
        default_menu=self.env.ref('website.main_menu')
        Menu.create({
            'name':'SubDefaultMenu',
            'parent_id':default_menu.id,
        })
        self.assertEqual(total_menu_items+1+self.nb_website,Menu.search_count([]),"Creatingadefaultchildmenushouldcreateitassuchandcopyitoneverywebsite")

        #Ensurenewwebsitegotatopmenu
        total_menus=Menu.search_count([])
        Website.create({'name':'newwebsite'})
        self.assertEqual(total_menus+4,Menu.search_count([]),"Newwebsite'sbootstrapingshouldhaveduplicatedefaultmenutree(Top/Home/Contactus/SubDefaultMenu)")

    deftest_04_specific_menu_translation(self):
        Translation=self.env['ir.translation']
        Menu=self.env['website.menu']
        existing_menus=Menu.search([])

        default_menu=self.env.ref('website.main_menu')
        template_menu=Menu.create({
            'parent_id':default_menu.id,
            'name':'Menuinenglish',
            'url':'turlututu',
        })
        new_menus=Menu.search([])-existing_menus
        specific1,specific2=new_menus.with_context(lang='fr_FR')-template_menu

        #createfr_FRtranslationfortemplatemenu
        self.env.ref('base.lang_fr').active=True
        template_menu.with_context(lang='fr_FR').name='Menuenfrançais'
        Translation.search([
            ('name','=','website.menu,name'),('res_id','=',template_menu.id),
        ]).module='website'
        self.assertEqual(specific1.name,'Menuinenglish',
                         'Translatingtemplatemenudoesnottranslatespecificmenu')

        #havedifferenttranslationforspecificwebsite
        specific1.name='Menuinfrench'

        #loadingtranslationaddmissingspecifictranslation
        Translation._load_module_terms(['website'],['fr_FR'])
        Menu.invalidate_cache(['name'])
        self.assertEqual(specific1.name,'Menuinfrench',
                         'Loadtranslationwithoutoverwritingkeepexistingtranslation')
        self.assertEqual(specific2.name,'Menuenfrançais',
                         'Loadtranslationaddmissingtranslationfromtemplatemenu')

        #loadingtranslationwithoverwritesyncalltranslationsfrommenutemplate
        Translation._load_module_terms(['website'],['fr_FR'],overwrite=True)
        Menu.invalidate_cache(['name'])
        self.assertEqual(specific1.name,'Menuenfrançais',
                         'Loadtranslationwithoverwritingupdateexistingmenufromtemplate')

    deftest_05_default_menu_unlink(self):
        Menu=self.env['website.menu']
        total_menu_items=Menu.search_count([])

        default_menu=self.env.ref('website.main_menu')
        default_menu.child_id[0].unlink()
        self.assertEqual(total_menu_items-1-self.nb_website,Menu.search_count([]),"Deletingadefaultmenuitemshoulddeleteits'copies'(sameURL)fromwebsite'smenutrees.Inthiscase,thedefaultchildmenuanditscopiesonwebsite1andwebsite2")


classTestMenuHttp(common.HttpCase):
    defsetUp(self):
        super().setUp()
        self.page_url='/page_specific'
        self.page=self.env['website.page'].create({
            'url':self.page_url,
            'website_id':1,
            #ir.ui.viewproperties
            'name':'Base',
            'type':'qweb',
            'arch':'<div>SpecificView</div>',
            'key':'test.specific_view',
        })
        self.menu=self.env['website.menu'].create({
            'name':'PageSpecificmenu',
            'page_id':self.page.id,
            'url':self.page_url,
            'website_id':1,
        })

    defsimulate_rpc_save_menu(self,data,to_delete=None):
        self.authenticate("admin","admin")
        #`Menu.save(1,{'data':[data],'to_delete':[]})`wouldhavebeen
        #idealbutneedafullfrontendcontexttogenerateroutingmaps,
        #routerandregistry,evenMockRequestisnotenough
        self.url_open('/web/dataset/call_kw',data=json.dumps({
            "params":{
                'model':'website.menu',
                'method':'save',
                'args':[1,{'data':[data],'to_delete':to_deleteor[]}],
                'kwargs':{},
            },
        }),headers={"Content-Type":"application/json","Referer":self.page.get_base_url()+self.page_url})

    deftest_01_menu_page_m2o(self):
        #EnsurethattheM2orelationtestedlaterinthetestisproperlyset.
        self.assertTrue(self.menu.page_id,"M2oshouldhavebeensetbythesetup")
        #EditthemenuURLtoa'reserved'URL
        data={
            'id':self.menu.id,
            'parent_id':self.menu.parent_id.id,
            'name':self.menu.name,
            'url':'/website/info',
        }
        self.simulate_rpc_save_menu(data)

        self.assertFalse(self.menu.page_id,"M2oshouldhavebeenunsetasthisisareservedURL.")
        self.assertEqual(self.menu.url,'/website/info',"MenuURLshouldhavechanged.")
        self.assertEqual(self.page.url,self.page_url,"Page'sURLshouldn'thavechanged.")

        #3.EditthemenuURLbacktothepageURL
        data['url']=self.page_url
        self.env['website.menu'].save(1,{'data':[data],'to_delete':[]})
        self.assertEqual(self.menu.page_id,self.page,
                         "M2oshouldhavebeensetback,astherewasapagefoundwiththenewURLsetonthemenu.")
        self.assertTrue(self.page.url==self.menu.url==self.page_url)

    deftest_02_menu_anchors(self):
        #EnsurethattheM2orelationtestedlaterinthetestisproperlyset.
        self.assertTrue(self.menu.page_id,"M2oshouldhavebeensetbythesetup")
        #EditthemenuURLtoananchor
        data={
            'id':self.menu.id,
            'parent_id':self.menu.parent_id.id,
            'name':self.menu.name,
            'url':'#anchor',
        }
        self.simulate_rpc_save_menu(data)
        self.assertFalse(self.menu.page_id,"M2oshouldhavebeenunsetasthisisananchorURL.")
        self.assertEqual(self.menu.url,self.page_url+'#anchor',"PageURLshouldhavebeenproperlyprefixedwiththerefererurl")
        self.assertEqual(self.page.url,self.page_url,"PageURLshouldnothavechanged")
