#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importre

importflectra.tests
fromflectra.toolsimportmute_logger


defbreak_view(view,fr='<p>placeholder</p>',to='<pt-field="not.exist"/>'):
    view.arch=view.arch.replace(fr,to)


@flectra.tests.common.tagged('post_install','-at_install')
classTestWebsiteResetViews(flectra.tests.HttpCase):

    deffix_it(self,page,mode='soft'):
        self.authenticate("admin","admin")
        resp=self.url_open(page)
        self.assertEqual(resp.status_code,500,"Waiting500")
        self.assertTrue('<buttondata-mode="soft"class="reset_templates_button'inresp.text)
        data={'view_id':self.find_template(resp),'redirect':page,'mode':mode}
        resp=self.url_open('/website/reset_template',data)
        self.assertEqual(resp.status_code,200,"Waiting200")

    deffind_template(self,response):
        find=re.search(r'<input.*type="hidden".*name="view_id".*value="([0-9]+)?"',response.text)
        returnfindandfind.group(1)

    defsetUp(self):
        super(TestWebsiteResetViews,self).setUp()
        self.Website=self.env['website']
        self.View=self.env['ir.ui.view']
        self.test_view=self.Website.viewref('test_website.test_view')

    @mute_logger('flectra.addons.http_routing.models.ir_http')
    deftest_01_reset_specific_page_view(self):
        self.test_page_view=self.Website.viewref('test_website.test_page_view')
        total_views=self.View.search_count([('type','=','qweb')])
        #TriggerCOWthenbreaktheQWEBXMLonit
        break_view(self.test_page_view.with_context(website_id=1))
        self.assertEqual(total_views+1,self.View.search_count([('type','=','qweb')]),"MissingCOWview")
        self.fix_it('/test_page_view')

    @mute_logger('flectra.addons.http_routing.models.ir_http')
    deftest_02_reset_specific_view_controller(self):
        total_views=self.View.search_count([('type','=','qweb')])
        #TriggerCOWthenbreaktheQWEBXMLonit
        #`t-att-data="not.exist"`willtestthecasewhereexception.htmlcontainsbranding
        break_view(self.test_view.with_context(website_id=1),to='<pt-att-data="not.exist"/>')
        self.assertEqual(total_views+1,self.View.search_count([('type','=','qweb')]),"MissingCOWview")
        self.fix_it('/test_view')

    @mute_logger('flectra.addons.http_routing.models.ir_http')
    deftest_03_reset_specific_view_controller_t_called(self):
        self.test_view_to_be_t_called=self.Website.viewref('test_website.test_view_to_be_t_called')

        total_views=self.View.search_count([('type','=','qweb')])
        #TriggerCOWthenbreaktheQWEBXMLonit
        break_view(self.test_view_to_be_t_called.with_context(website_id=1))
        break_view(self.test_view,to='<tt-call="test_website.test_view_to_be_t_called"/>')
        self.assertEqual(total_views+1,self.View.search_count([('type','=','qweb')]),"MissingCOWview")
        self.fix_it('/test_view')

    @mute_logger('flectra.addons.http_routing.models.ir_http')
    deftest_04_reset_specific_view_controller_inherit(self):
        self.test_view_child_broken=self.Website.viewref('test_website.test_view_child_broken')

        #Activateandbreaktheinheritedview
        self.test_view_child_broken.active=True
        break_view(self.test_view_child_broken.with_context(website_id=1,load_all_views=True))

        self.fix_it('/test_view')

    #Thistestworkinreallife,butnotintestmodesincewecannotrollbacksavepoint.
    #@mute_logger('flectra.addons.http_routing.models.ir_http','flectra.addons.website.models.ir_ui_view')
    #deftest_05_reset_specific_view_controller_broken_request(self):
    #    total_views=self.View.search_count([('type','=','qweb')])
    #    #TriggerCOWthenbreaktheQWEBXMLonit
    #    break_view(self.test_view.with_context(website_id=1),to='<tt-esc="request.env[\'website\'].browse(\'a\').name"/>')
    #    self.assertEqual(total_views+1,self.View.search_count([('type','=','qweb')]),"MissingCOWview(1)")
    #    self.fix_it('/test_view')

    #alsomuteir.ui.viewas`get_view_id()`willraise"Couldnotfindviewobjectwithxml_id'not.exist'""
    @mute_logger('flectra.addons.http_routing.models.ir_http','flectra.addons.website.models.ir_ui_view')
    deftest_06_reset_specific_view_controller_inexisting_template(self):
        total_views=self.View.search_count([('type','=','qweb')])
        #TriggerCOWthenbreaktheQWEBXMLonit
        break_view(self.test_view.with_context(website_id=1),to='<tt-call="not.exist"/>')
        self.assertEqual(total_views+1,self.View.search_count([('type','=','qweb')]),"MissingCOWview(2)")
        self.fix_it('/test_view')

    @mute_logger('flectra.addons.http_routing.models.ir_http')
    deftest_07_reset_page_view_complete_flow(self):
        self.start_tour("/",'test_reset_page_view_complete_flow_part1',login="admin")
        self.fix_it('/test_page_view')
        self.start_tour("/",'test_reset_page_view_complete_flow_part2',login="admin")
        self.fix_it('/test_page_view')

    @mute_logger('flectra.addons.http_routing.models.ir_http')
    deftest_08_reset_specific_page_view_hard_mode(self):
        self.test_page_view=self.Website.viewref('test_website.test_page_view')
        total_views=self.View.search_count([('type','=','qweb')])
        #TriggerCOWthenbreaktheQWEBXMLonit
        break_view(self.test_page_view.with_context(website_id=1))
        #Breakitagaintohaveapreviousarchdifferentthanfilearch
        break_view(self.test_page_view.with_context(website_id=1))
        self.assertEqual(total_views+1,self.View.search_count([('type','=','qweb')]),"MissingCOWview")
        withself.assertRaises(AssertionError):
            #softresetshouldnotbeabletoresettheviewasprevious
            #versionisalsobroken
            self.fix_it('/test_page_view')
        self.fix_it('/test_page_view','hard')
