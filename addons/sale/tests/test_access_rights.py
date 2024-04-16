#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.sale.tests.commonimportTestSaleCommon
fromflectra.exceptionsimportAccessError,UserError,ValidationError
fromflectra.testsimportHttpCase,tagged


@tagged('post_install','-at_install')
classTestAccessRights(TestSaleCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company_data['default_user_salesman_2']=cls.env['res.users'].with_context(no_reset_password=True).create({
            'name':'default_user_salesman_2',
            'login':'default_user_salesman_2.comp%s'%cls.company_data['company'].id,
            'email':'default_user_salesman_2@example.com',
            'signature':'--\nMark',
            'notification_type':'email',
            'groups_id':[(6,0,cls.env.ref('sales_team.group_sale_salesman').ids)],
            'company_ids':[(6,0,cls.company_data['company'].ids)],
            'company_id':cls.company_data['company'].id,
        })

        #CreatetheSOwithaspecificsalesperson
        cls.order=cls.env['sale.order'].with_context(tracking_disable=True).create({
            'partner_id':cls.partner_a.id,
            'user_id':cls.company_data['default_user_salesman'].id
        })

    deftest_access_sales_manager(self):
        """Testsalesmanager'saccessrights"""
        SaleOrder=self.env['sale.order'].with_context(tracking_disable=True)
        #ManagercanseetheSOwhichisassignedtoanothersalesperson
        self.order.read()
        #ManagercanchangeasalespersonoftheSO
        self.order.write({'user_id':self.company_data['default_user_salesman'].id})
        #ManagercancreatetheSOforothersalesperson
        sale_order=SaleOrder.create({
            'partner_id':self.partner_a.id,
            'user_id':self.company_data['default_user_salesman'].id
        })
        self.assertIn(sale_order.id,SaleOrder.search([]).ids,'SalesmanagershouldbeabletocreatetheSOofothersalesperson')
        #ManagercanconfirmtheSO
        sale_order.action_confirm()
        #ManagercannotdeleteconfirmedSO
        withself.assertRaises(UserError):
            sale_order.unlink()
        #ManagercandeletetheSOofothersalespersonifSOisin'draft'or'cancel'state
        self.order.unlink()
        self.assertNotIn(self.order.id,SaleOrder.search([]).ids,'SalesmanagershouldbeabletodeletetheSO')

        #ManagercancreateaSalesTeam
        india_channel=self.env['crm.team'].with_context(tracking_disable=True).create({
            'name':'India',
        })
        self.assertIn(india_channel.id,self.env['crm.team'].search([]).ids,'SalesmanagershouldbeabletocreateaSalesTeam')
        #ManagercaneditaSalesTeam
        india_channel.write({'name':'new_india'})
        self.assertEqual(india_channel.name,'new_india','SalesmanagershouldbeabletoeditaSalesTeam')
        #ManagercandeleteaSalesTeam
        india_channel.unlink()
        self.assertNotIn(india_channel.id,self.env['crm.team'].search([]).ids,'SalesmanagershouldbeabletodeleteaSalesTeam')

    deftest_access_sales_person(self):
        """TestSalesperson'saccessrights"""
        #Salespersoncanseeonlytheirownsalesorder
        withself.assertRaises(AccessError):
            self.order.with_user(self.company_data['default_user_salesman_2']).read()
        #NowassigntheSOtothemselves
        self.order.write({'user_id':self.company_data['default_user_salesman_2'].id})
        self.order.with_user(self.company_data['default_user_salesman_2']).read()
        #SalespersoncanchangeaSalesTeamofSO
        self.order.with_user(self.company_data['default_user_salesman_2']).write({'team_id':self.company_data['default_sale_team'].id})
        #Salespersoncan'tcreatetheSOofothersalesperson
        withself.assertRaises(AccessError):
            self.env['sale.order'].with_user(self.company_data['default_user_salesman_2']).create({
                'partner_id':self.partner_a.id,
                'user_id':self.company_data['default_user_salesman'].id
            })
        #Salespersoncan'tdeletetheSO
        withself.assertRaises(AccessError):
            self.order.with_user(self.company_data['default_user_salesman_2']).unlink()
        #SalespersoncanconfirmtheSO
        self.order.with_user(self.company_data['default_user_salesman_2']).action_confirm()

    deftest_access_portal_user(self):
        """Testportaluser'saccessrights"""
        #PortalusercanseetheconfirmedSOforwhichtheyareassignedasacustomer
        withself.assertRaises(AccessError):
            self.order.with_user(self.company_data['default_user_portal']).read()

        self.order.partner_id=self.company_data['default_user_portal'].partner_id
        self.order.action_confirm()
        #Portalusercan'tedittheSO
        withself.assertRaises(AccessError):
            self.order.with_user(self.company_data['default_user_portal']).write({'team_id':self.company_data['default_sale_team'].id})
        #Portalusercan'tcreatetheSO
        withself.assertRaises(AccessError):
            self.env['sale.order'].with_user(self.company_data['default_user_portal']).create({
                'partner_id':self.partner_a.id,
            })
        #Portalusercan'tdeletetheSOwhichisin'draft'or'cancel'state
        self.order.action_cancel()
        withself.assertRaises(AccessError):
            self.order.with_user(self.company_data['default_user_portal']).unlink()

    deftest_access_employee(self):
        """Testclassicemployee'saccessrights"""
        #Employeecan'tseeanySO
        withself.assertRaises(AccessError):
            self.order.with_user(self.company_data['default_user_employee']).read()
        #Employeecan'tedittheSO
        withself.assertRaises(AccessError):
            self.order.with_user(self.company_data['default_user_employee']).write({'team_id':self.company_data['default_sale_team'].id})
        #Employeecan'tcreatetheSO
        withself.assertRaises(AccessError):
            self.env['sale.order'].with_user(self.company_data['default_user_employee']).create({
                'partner_id':self.partner_a.id,
            })
        #Employeecan'tdeletetheSO
        withself.assertRaises(AccessError):
            self.order.with_user(self.company_data['default_user_employee']).unlink()

@tagged('post_install','-at_install')
classTestAccessRightsControllers(HttpCase):

    deftest_access_controller(self):

        portal_so=self.env.ref("sale.portal_sale_order_2").sudo()
        portal_so._portal_ensure_token()
        token=portal_so.access_token

        private_so=self.env.ref("sale.sale_order_1")

        self.authenticate(None,None)

        #Testpublicusercan'tprintanorderwithoutatoken
        req=self.url_open(
            url='/my/orders/%s?report_type=pdf'%portal_so.id,
            allow_redirects=False,
        )
        self.assertEqual(req.status_code,302)

        #orwitharandomtoken
        req=self.url_open(
            url='/my/orders/%s?access_token=%s&report_type=pdf'%(
                portal_so.id,
                "foo",
            ),
            allow_redirects=False,
        )
        self.assertEqual(req.status_code,302)

        #butworksfinewiththerighttoken
        req=self.url_open(
            url='/my/orders/%s?access_token=%s&report_type=pdf'%(
                portal_so.id,
                token,
            ),
            allow_redirects=False,
        )
        self.assertEqual(req.status_code,200)

        self.authenticate("portal","portal")

        #donotneedthetokenwhenloggedin
        req=self.url_open(
            url='/my/orders/%s?report_type=pdf'%portal_so.id,
            allow_redirects=False,
        )
        self.assertEqual(req.status_code,200)

        #butstillcan'taccessanotherorder
        req=self.url_open(
            url='/my/orders/%s?report_type=pdf'%private_so.id,
            allow_redirects=False,
        )
        self.assertEqual(req.status_code,302)
