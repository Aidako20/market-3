#coding:utf-8
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcontextlibimportcontextmanager
fromdatetimeimportdatetime,timedelta
fromunittest.mockimportpatch

fromflectra.addons.base.tests.commonimportHttpCaseWithUserDemo
fromflectra.addons.website.toolsimportMockRequest
fromflectra.addons.website.models.website_visitorimportWebsiteVisitor
fromflectra.testsimportcommon,tagged


classMockVisitor(common.BaseCase):

    @contextmanager
    defmock_visitor_from_request(self,force_visitor=False):

        def_get_visitor_from_request(model,*args,**kwargs):
            returnforce_visitor

        withpatch.object(WebsiteVisitor,'_get_visitor_from_request',
                          autospec=True,wraps=WebsiteVisitor,
                          side_effect=_get_visitor_from_request)as_get_visitor_from_request_mock:
            yield


@tagged('-at_install','post_install','website_visitor')
classWebsiteVisitorTests(MockVisitor,HttpCaseWithUserDemo):

    defsetUp(self):
        super(WebsiteVisitorTests,self).setUp()

        self.website=self.env['website'].search([
            ('company_id','=',self.env.user.company_id.id)
        ],limit=1)
        self.cookies={}

        untracked_view=self.env['ir.ui.view'].create({
            'name':'UntackedView',
            'type':'qweb',
            'arch':'''<tname="Homepage"t-name="website.base_view">
                        <tt-call="website.layout">
                            Iamagenericpage²
                        </t>
                    </t>''',
            'key':'test.base_view',
            'track':False,
        })
        tracked_view=self.env['ir.ui.view'].create({
            'name':'TrackedView',
            'type':'qweb',
            'arch':'''<tname="Homepage"t-name="website.base_view">
                        <tt-call="website.layout">
                            Iamagenericpage
                        </t>
                    </t>''',
            'key':'test.base_view',
            'track':True,
        })
        tracked_view_2=self.env['ir.ui.view'].create({
            'name':'TrackedView2',
            'type':'qweb',
            'arch':'''<tname="OtherPage"t-name="website.base_view">
                        <tt-call="website.layout">
                            Iamagenericsecondpage
                        </t>
                    </t>''',
            'key':'test.base_view',
            'track':True,
        })
        [self.untracked_page,self.tracked_page,self.tracked_page_2]=self.env['website.page'].create([
            {
                'view_id':untracked_view.id,
                'url':'/untracked_view',
                'website_published':True,
            },
            {
                'view_id':tracked_view.id,
                'url':'/tracked_view',
                'website_published':True,
            },
            {
                'view_id':tracked_view_2.id,
                'url':'/tracked_view_2',
                'website_published':True,
            },
        ])

        self.user_portal=self.env['res.users'].search([('login','=','portal')])
        self.partner_portal=self.user_portal.partner_id
        ifnotself.user_portal:
            self.env['ir.config_parameter'].sudo().set_param('auth_password_policy.minlength',4)
            self.partner_portal=self.env['res.partner'].create({
                'name':'JoelWillis',
                'email':'joel.willis63@example.com',
            })
            self.user_portal=self.env['res.users'].create({
                'login':'portal',
                'password':'portal',
                'partner_id':self.partner_portal.id,
                'groups_id':[(6,0,[self.env.ref('base.group_portal').id])],
            })

    def_get_last_visitor(self):
        returnself.env['website.visitor'].search([],limit=1,order="idDESC")

    defassertPageTracked(self,visitor,page):
        """Checkapageisinvisitortrackingdata"""
        self.assertIn(page,visitor.website_track_ids.page_id)
        self.assertIn(page,visitor.page_ids)

    defassertVisitorTracking(self,visitor,pages):
        """Checkthewholetrackinghistoryofavisitor"""
        forpageinpages:
            self.assertPageTracked(visitor,page)
        self.assertEqual(
            len(visitor.website_track_ids),
            len(pages)
        )

    defassertVisitorDeactivated(self,visitor,main_visitor):
        """Temporarymethodtocheckthatavisitorhasbeende-activated/merged
        withothervisitor,notablyincaseoflogin(seeUser.authenticate()as
        wellasVisitor._link_to_visitor()).

        Asfinalresultdependsoninstalledmodules(seeoverrides)duetostable
        improvementslinkedtoEventOnline,thismethodcontainsahacktoavoid
        doingtoomuchoverridesjustforthatbehavior."""
        if'parent_id'inself.env['website.visitor']:
            self.assertTrue(bool(visitor))
            self.assertFalse(visitor.active)
            self.assertTrue(main_visitor.active)
            self.assertEqual(visitor.parent_id,main_visitor)
        else:
            self.assertFalse(visitor)
            self.assertTrue(bool(main_visitor))

    deftest_visitor_creation_on_tracked_page(self):
        """Testvariousflowsinvolvingvisitorcreationandupdate."""
        existing_visitors=self.env['website.visitor'].search([])
        existing_tracks=self.env['website.track'].search([])
        self.url_open(self.untracked_page.url)
        self.url_open(self.tracked_page.url)
        self.url_open(self.tracked_page.url)

        new_visitor=self.env['website.visitor'].search([('id','notin',existing_visitors.ids)])
        new_track=self.env['website.track'].search([('id','notin',existing_tracks.ids)])
        self.assertEqual(len(new_visitor),1,"1visitorshouldbecreated")
        self.assertEqual(len(new_track),1,"Thereshouldbe1trackedpage")
        self.assertEqual(new_visitor.visit_count,1)
        self.assertEqual(new_visitor.website_track_ids,new_track)
        self.assertVisitorTracking(new_visitor,self.tracked_page)

        #------------------------------------------------------------
        #Adminconnects
        #------------------------------------------------------------

        self.cookies={'visitor_uuid':new_visitor.access_token}
        withMockRequest(self.env,website=self.website,cookies=self.cookies):
            self.authenticate(self.user_admin.login,'admin')

        visitor_admin=new_visitor
        #visitapage
        self.url_open(self.tracked_page_2.url)

        #checktrackingandvisitor/usersync
        self.assertVisitorTracking(visitor_admin,self.tracked_page|self.tracked_page_2)
        self.assertEqual(visitor_admin.partner_id,self.partner_admin)
        self.assertEqual(visitor_admin.name,self.partner_admin.name)

        #------------------------------------------------------------
        #Portalconnects
        #------------------------------------------------------------

        withMockRequest(self.env,website=self.website,cookies=self.cookies):
            self.authenticate(self.user_portal.login,'portal')

        self.assertFalse(
            self.env['website.visitor'].search([('id','notin',(existing_visitors|visitor_admin).ids)]),
            "Noextravisitorshouldbecreated")

        #visitapage
        self.url_open(self.tracked_page.url)
        self.url_open(self.untracked_page.url)
        self.url_open(self.tracked_page_2.url)
        self.url_open(self.tracked_page_2.url) #2timetobesureitdoesnotrecordtwice

        #newvisitoriscreated
        new_visitors=self.env['website.visitor'].search([('id','notin',existing_visitors.ids)])
        self.assertEqual(len(new_visitors),2,"Oneextravisitorshouldbecreated")
        visitor_portal=new_visitors[0]
        self.assertEqual(visitor_portal.partner_id,self.partner_portal)
        self.assertEqual(visitor_portal.name,self.partner_portal.name)
        self.assertVisitorTracking(visitor_portal,self.tracked_page|self.tracked_page_2)

        #------------------------------------------------------------
        #Backtoanonymous
        #------------------------------------------------------------

        #portaluserdisconnects
        self.logout()

        #visitsomepages
        self.url_open(self.tracked_page.url)
        self.url_open(self.untracked_page.url)
        self.url_open(self.tracked_page_2.url)
        self.url_open(self.tracked_page_2.url) #2timetobesureitdoesnotrecordtwice

        #newvisitoriscreated
        new_visitors=self.env['website.visitor'].search([('id','notin',existing_visitors.ids)])
        self.assertEqual(len(new_visitors),3,"Oneextravisitorshouldbecreated")
        visitor_anonymous=new_visitors[0]
        self.cookies['visitor_uuid']=visitor_anonymous.access_token
        self.assertFalse(visitor_anonymous.name)
        self.assertFalse(visitor_anonymous.partner_id)
        self.assertVisitorTracking(visitor_anonymous,self.tracked_page|self.tracked_page_2)
        visitor_anonymous_tracks=visitor_anonymous.website_track_ids

        #------------------------------------------------------------
        #Adminconnectsagain
        #------------------------------------------------------------

        withMockRequest(self.env,website=self.website,cookies=self.cookies):
            self.authenticate(self.user_admin.login,'admin')

        #onevisitorisdeleted
        visitor_anonymous=self.env['website.visitor'].with_context(active_test=False).search([('id','=',visitor_anonymous.id)])
        self.assertVisitorDeactivated(visitor_anonymous,visitor_admin)
        new_visitors=self.env['website.visitor'].search([('id','notin',existing_visitors.ids)])
        self.assertEqual(new_visitors,visitor_admin|visitor_portal)
        visitor_admin=self.env['website.visitor'].search([('partner_id','=',self.partner_admin.id)])
        #tracksarelinked
        self.assertTrue(visitor_anonymous_tracks<visitor_admin.website_track_ids)
        self.assertEqual(len(visitor_admin.website_track_ids),4,"Thereshouldbe4trackedpagefortheadmin")

        #------------------------------------------------------------
        #Backtoanonymous
        #------------------------------------------------------------

        #admindisconnects
        self.logout()

        #visitsomepages
        self.url_open(self.tracked_page.url)
        self.url_open(self.untracked_page.url)
        self.url_open(self.tracked_page_2.url)
        self.url_open(self.tracked_page_2.url) #2timetobesureitdoesnotrecordtwice

        #newvisitorcreated
        new_visitors=self.env['website.visitor'].search([('id','notin',existing_visitors.ids)])
        self.assertEqual(len(new_visitors),3,"Oneextravisitorshouldbecreated")
        visitor_anonymous_2=new_visitors[0]
        self.cookies['visitor_uuid']=visitor_anonymous_2.access_token
        self.assertFalse(visitor_anonymous_2.name)
        self.assertFalse(visitor_anonymous_2.partner_id)
        self.assertVisitorTracking(visitor_anonymous_2,self.tracked_page|self.tracked_page_2)
        visitor_anonymous_2_tracks=visitor_anonymous_2.website_track_ids

        #------------------------------------------------------------
        #Portalconnectsagain
        #------------------------------------------------------------
        withMockRequest(self.env,website=self.website,cookies=self.cookies):
            self.authenticate(self.user_portal.login,'portal')

        #onevisitorisdeleted
        new_visitors=self.env['website.visitor'].search([('id','notin',existing_visitors.ids)])
        self.assertEqual(new_visitors,visitor_admin|visitor_portal)
        #tracksarelinked
        self.assertTrue(visitor_anonymous_2_tracks<visitor_portal.website_track_ids)
        self.assertEqual(len(visitor_portal.website_track_ids),4,"Thereshouldbe4trackedpagefortheportaluser")

        #simulatetheportalusercomesback30minlater
        fortrackinvisitor_portal.website_track_ids:
            track.write({'visit_datetime':track.visit_datetime-timedelta(minutes=30)})

        #visitapage
        self.url_open(self.tracked_page.url)
        visitor_portal.invalidate_cache(fnames=['website_track_ids'])
        #tracksarecreated
        self.assertEqual(len(visitor_portal.website_track_ids),5,"Thereshouldbe5trackedpagefortheportaluser")

        #simulatetheportalusercomesback8hourslater
        visitor_portal.write({'last_connection_datetime':visitor_portal.last_connection_datetime-timedelta(hours=8)})
        self.url_open(self.tracked_page.url)
        visitor_portal.invalidate_cache(fnames=['visit_count'])
        #checknumberofvisits
        self.assertEqual(visitor_portal.visit_count,2,"Thereshouldbe2visitsfortheportaluser")

    deftest_visitor_archive(self):
        """Testcronarchivinginactivevisitorsandtheirre-activationwhen
        authenticatinganuser."""
        self.env['ir.config_parameter'].sudo().set_param('website.visitor.live.days',7)

        partner_demo=self.partner_demo
        old_visitor=self.env['website.visitor'].create({
            'lang_id':self.env.ref('base.lang_en').id,
            'country_id':self.env.ref('base.be').id,
            'website_id':1,
            'partner_id':partner_demo.id,
        })
        self.assertTrue(old_visitor.active)
        self.assertEqual(partner_demo.visitor_ids,old_visitor,"Visitoranditspartnershouldbesynchronized")

        #archiveoldvisitor
        old_visitor.last_connection_datetime=datetime.now()-timedelta(days=8)
        self.env['website.visitor']._cron_archive_visitors()
        self.assertEqual(old_visitor.active,False,"Visitorshouldbearchivedafterinactivity")

        #reconnectwithnewvisitor.
        self.url_open(self.tracked_page.url)
        new_visitor=self._get_last_visitor()
        self.assertFalse(new_visitor.partner_id)
        self.assertTrue(new_visitor.id>old_visitor.id,"Anewvisitorshouldhavebeencreated.")
        self.assertVisitorTracking(new_visitor,self.tracked_page)

        withself.mock_visitor_from_request(force_visitor=new_visitor):
            self.authenticate('demo','demo')
        (new_visitor|old_visitor).flush()
        partner_demo.flush()
        partner_demo.invalidate_cache(fnames=['visitor_ids'])
        self.assertEqual(partner_demo.visitor_ids,old_visitor,"Thepartnervisitorshouldbebacktothe'old'visitor.")

        new_visitor=self.env['website.visitor'].search([('id','=',new_visitor.id)])
        self.assertEqual(len(new_visitor),0,"Thenewvisitorshouldbedeletedwhenvisitorauthenticateonceagain.")
        self.assertEqual(old_visitor.active,True,"Theoldvisitorshouldbereactivatedwhenvisitorauthenticatesonceagain.")
