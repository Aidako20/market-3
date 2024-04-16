#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittest.mockimportpatch

fromflectra.exceptionsimportAccessError
fromflectra.tests.commonimportTransactionCase
fromflectra.addons.crm.tests.commonimportTestCrmCommon
fromflectra.addons.mail.tests.commonimportmail_new_test_user


classTestPartnerAssign(TransactionCase):

    defsetUp(self):
        super(TestPartnerAssign,self).setUp()

        self.customer_uk=self.env['res.partner'].create({
            'name':'Nigel',
            'country_id':self.env.ref('base.uk').id,
            'city':'Birmingham',
            'zip':'B463AG',
            'street':'CannonHillPark',
        })
        self.lead_uk=self.env['crm.lead'].create({
            'type':'opportunity',
            'name':'OfficeDesignandArchitecture',
            'partner_id':self.customer_uk.id
        })

        defgeo_find(addr,**kw):
            return{
                'Wavre,Belgium':(50.7158956,4.6128075),
                'CannonHillPark,B463AGBirmingham,UnitedKingdom':(52.45216,-1.898578),
            }.get(addr)

        patcher=patch('flectra.addons.base_geolocalize.models.base_geocoder.GeoCoder.geo_find',wraps=geo_find)
        patcher.start()
        self.addCleanup(patcher.stop)

    deftest_partner_assign(self):
        """Testtheautomaticassignationusinggeolocalisation"""
        partner_be=self.env['res.partner'].create({
            "name":"Agrolait",
            "is_company":True,
            "city":"Wavre",
            "zip":"1300",
            "country_id":self.env.ref("base.be").id,
            "street":"69ruedeNamur",
            "partner_weight":10,
        })
        partner_uk=self.env['res.partner'].create({
            "name":"ThinkBigSystems",
            "is_company":True,
            "city":"London",
            "country_id":self.env.ref("base.uk").id,
            "street":"89LingfieldTower",
            "partner_weight":10,
        })

        lead=self.lead_uk

        #InordertotestfindnearestPartnerfunctionalityandassigntoopportunity,
        #ISetGeoLattitudeandLongitudeaccordingtopartneraddress.
        partner_be.geo_localize()

        #IcheckGeoLatitudeandLongitudeofpartnerafterset
        self.assertTrue(50<partner_be.partner_latitude<51,"Latitudeiswrong:50<%s<51"%partner_be.partner_latitude)
        self.assertTrue(3<partner_be.partner_longitude<5,"Longitudeiswrong:3<%s<5"%partner_be.partner_longitude)

        #Iassignnearestpartnertoopportunity.
        lead.assign_partner()

        #IcheckassignedpartnerofopportunitywhoisnearestGeoLatitudeandLongitudeofopportunity.
        self.assertEqual(lead.partner_assigned_id,partner_uk,"Opportuniyisnotassignednearestpartner")
        self.assertTrue(50<lead.partner_latitude<55,"Latitudeiswrong:50<%s<55"%lead.partner_latitude)
        self.assertTrue(-4<lead.partner_longitude<-1,"Longitudeiswrong:-4<%s<-1"%lead.partner_longitude)
        self.assertTrue(lead.date_partner_assign,"PartnerAssignmentDateshouldbeset")

        #Iforwardthisopportunitytoitsnearestpartner.
        context=dict(self.env.context,default_model='crm.lead',default_res_id=lead.id,active_ids=lead.ids)
        lead_forwarded=self.env['crm.lead.forward.to.partner'].with_context(context).create({})
        try:
            lead_forwarded.action_forward()
        except:
            pass


classTestPartnerLeadPortal(TestCrmCommon):

    defsetUp(self):
        super(TestPartnerLeadPortal,self).setUp()
        #PartnerGrade
        self.grade=self.env['res.partner.grade'].create({
            'name':"GradeTest",
            'partner_weight':42,
            'sequence':3,
        })
        #Integratinguser/partner,havingasalesman
        self.user_portal=mail_new_test_user(
            self.env,login='user_portal',
            name='PatrickPortal',email='portal@test.example.com',
            company_id=self.env.ref("base.main_company").id,
            grade_id=self.grade.id,
            user_id=self.user_sales_manager.id,
            notification_type='inbox',
            groups='base.group_portal',
        )

        #Newlead,assignedtothenewportal
        self.lead_portal=self.env['crm.lead'].with_context(mail_notrack=True).create({
            'type':"lead",
            'name':"Testleadnew",
            'user_id':False,
            'team_id':False,
            'description':"Thisisthedescriptionofthetestnewlead.",
            'partner_assigned_id':self.user_portal.partner_id.id
        })

    deftest_partner_lead_accept(self):
        """Testanintegratingpartneracceptingthelead"""
        self.lead_portal.with_user(self.user_portal).partner_interested(comment="Ohyeah,Itakethatlead!")
        self.assertEqual(self.lead_portal.type,'opportunity')

    deftest_partner_lead_decline(self):
        """Testanintegratingpartnerdeclinethelead"""
        self.lead_portal.with_user(self.user_portal).partner_desinterested(comment="Nothanks,Ihaveenoughleads!",contacted=True,spam=False)

        self.assertFalse(self.lead_portal.partner_assigned_id.id,'Thepartner_assigned_idofthedeclinedleadshouldbeFalse.')
        self.assertTrue(self.user_portal.partner_idinself.lead_portal.sudo().partner_declined_ids,'Partnerwhohasdeclinedtheleadshouldbeinthedeclined_partner_ids.')

    deftest_lead_access_right(self):
        """Testanotherportalusercannotwriteoneveryleads"""
        #portaluserhavingnoright
        poor_portal_user=self.env['res.users'].with_context({'no_reset_password':True,'mail_notrack':True}).create({
            'name':'PoorPartner(notintegratingone)',
            'email':'poor.partner@ododo.com',
            'login':'poorpartner',
            'groups_id':[(6,0,[self.env.ref('base.group_portal').id])],
        })
        #trytoacceptaleadthatisnotmine
        withself.assertRaises(AccessError):
            self.lead_portal.with_user(poor_portal_user).partner_interested(comment="Ohyeah,Itakethatlead!")

    deftest_lead_creation(self):
        """Testtheopportinutycreationfromportal"""
        data=self.env['crm.lead'].with_user(self.user_portal).create_opp_portal({
            'title':"L'oursbleu",
            'description':'Agoodjoke',
            'contact_name':'RenaudRutten',
        })
        opportunity=self.env['crm.lead'].browse(data['id'])
        salesmanteam=self.env['crm.team']._get_default_team_id(user_id=self.user_portal.user_id.id)

        self.assertEqual(opportunity.team_id,salesmanteam,'Thecreatedopportunityshouldhavethesameteamasthesalesmandefaultteamoftheopportunitycreator.')
        self.assertEqual(opportunity.partner_assigned_id,self.user_portal.partner_id,'AssignedPartnerofcreatedopportunityisthe(portal)creator.')

    deftest_portal_mixin_url(self):
        record_action=self.lead_portal.get_access_action(self.user_portal.id)
        self.assertEqual(record_action['url'],'/my/opportunity/%s'%self.lead_portal.id)
        self.assertEqual(record_action['type'],'ir.actions.act_url')
