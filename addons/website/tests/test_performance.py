#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportHttpCase

EXTRA_REQUEST=5
"""Duringtests,thequeryon'base_registry_signaling,base_cache_signaling'
    won'tbeexecutedonhotstate,but6newqueriesrelatedtothetestcursor
    willbeadded:
        SAVEPOINT"test_cursor_4"
        SAVEPOINT"test_cursor_4"
        ROLLBACKTOSAVEPOINT"test_cursor_4"
        SAVEPOINT"test_cursor_5"
        [..usualSQLQueries..]
        SAVEPOINT"test_cursor_5"
        ROLLBACKTOSAVEPOINT"test_cursor_5"
"""


classUtilPerf(HttpCase):
    def_get_url_hot_query(self,url):
        url+=('?'notinurland'?'or'')+'&nocache'

        #ensureworkerisinhotstate
        self.url_open(url)
        self.url_open(url)

        sql_count=self.registry.test_cr.sql_log_count
        self.url_open(url)
        returnself.registry.test_cr.sql_log_count-sql_count-EXTRA_REQUEST


classTestStandardPerformance(UtilPerf):
    deftest_10_perf_sql_img_controller(self):
        self.authenticate('demo','demo')
        url='/web/image/res.users/2/image_256'
        self.assertEqual(self._get_url_hot_query(url),7)

    deftest_20_perf_sql_img_controller_bis(self):
        url='/web/image/website/1/favicon'
        self.assertEqual(self._get_url_hot_query(url),4)
        self.authenticate('portal','portal')
        self.assertEqual(self._get_url_hot_query(url),4)


classTestWebsitePerformance(UtilPerf):

    defsetUp(self):
        super().setUp()
        self.page,self.menu=self._create_page_with_menu('/sql_page')

    def_create_page_with_menu(self,url):
        name=url[1:]
        website=self.env['website'].browse(1)
        page=self.env['website.page'].create({
            'url':url,
            'name':name,
            'type':'qweb',
            'arch':'<tname="%s"t-name="website.page_test_%s">\
                       <tt-call="website.layout">\
                         <divid="wrap"><divclass="oe_structure"/></div>\
                       </t>\
                     </t>'%(name,name),
            'key':'website.page_test_%s'%name,
            'is_published':True,
            'website_id':website.id,
            'track':False,
        })
        menu=self.env['website.menu'].create({
            'name':name,
            'url':url,
            'page_id':page.id,
            'website_id':website.id,
            'parent_id':website.menu_id.id
        })
        return(page,menu)

    deftest_10_perf_sql_queries_page(self):
        #standarduntrackedwebsite.page
        self.assertEqual(self._get_url_hot_query(self.page.url),11)
        self.menu.unlink()
        self.assertEqual(self._get_url_hot_query(self.page.url),13)

    deftest_15_perf_sql_queries_page(self):
        #standardtrackedwebsite.page
        self.page.track=True
        self.assertEqual(self._get_url_hot_query(self.page.url),19)
        self.menu.unlink()
        self.assertEqual(self._get_url_hot_query(self.page.url),21)

    deftest_20_perf_sql_queries_homepage(self):
        #homepage"/"hasitsowncontroller
        self.assertEqual(self._get_url_hot_query('/'),20)

    deftest_30_perf_sql_queries_page_no_layout(self):
        #website.pagewithnocalltolayouttemplates
        self.page.arch='<div>Iamablankpage</div>'
        self.assertEqual(self._get_url_hot_query(self.page.url),9)

    deftest_40_perf_sql_queries_page_multi_level_menu(self):
        #menustructureshouldnotimpactSQLrequests
        _,menu_a=self._create_page_with_menu('/a')
        _,menu_aa=self._create_page_with_menu('/aa')
        _,menu_b=self._create_page_with_menu('/b')
        _,menu_bb=self._create_page_with_menu('/bb')
        _,menu_bbb=self._create_page_with_menu('/bbb')
        _,menu_bbbb=self._create_page_with_menu('/bbbb')
        _,menu_bbbbb=self._create_page_with_menu('/bbbbb')
        self._create_page_with_menu('c')
        menu_bbbbb.parent_id=menu_bbbb
        menu_bbbb.parent_id=menu_bbb
        menu_bbb.parent_id=menu_bb
        menu_bb.parent_id=menu_b
        menu_aa.parent_id=menu_a

        self.assertEqual(self._get_url_hot_query(self.page.url),11)

    deftest_50_perf_sql_web_content(self):
        #assetsroute/web/content/..
        self.url_open('/') #createassetsattachments
        assets_url=self.env['ir.attachment'].search([('url','=like','/web/content/%/web.assets_common%.js')],limit=1).url
        self.assertEqual(self._get_url_hot_query(assets_url),2)
