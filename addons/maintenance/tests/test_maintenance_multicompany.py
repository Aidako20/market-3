#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importtime

fromflectra.tests.commonimportTransactionCase
fromflectra.exceptionsimportAccessError


classTestEquipmentMulticompany(TransactionCase):

    deftest_00_equipment_multicompany_user(self):
        """TestCheckmaintenancewithequipmentmanageranduserinmulticompanyenvironment"""

        #Usefullmodels
        Equipment=self.env['maintenance.equipment']
        MaintenanceRequest=self.env['maintenance.request']
        Category=self.env['maintenance.equipment.category']
        ResUsers=self.env['res.users']
        ResCompany=self.env['res.company']
        MaintenanceTeam=self.env['maintenance.team']

        #Usefullreference.
        group_user=self.env.ref('base.group_user')
        group_manager=self.env.ref('maintenance.group_equipment_manager')

        #CompanyA
        company_a=ResCompany.create({
            'name':'CompanyA',
            'currency_id':self.env.ref('base.USD').id,
        })

        #Createonechildcompanyhavingparentcompanyis'Yourcompany'
        company_b=ResCompany.create({
            'name':'CompanyB',
            'currency_id':self.env.ref('base.USD').id,
        })

        #Createequipmentmanager.
        cids=[company_a.id,company_b.id]
        equipment_manager=ResUsers.create({
            'name':'EquipmentManager',
            'company_id':company_a.id,
            'login':'e_equipment_manager',
            'email':'eqmanager@yourcompany.example.com',
            'groups_id':[(6,0,[group_manager.id])],
            'company_ids':[(6,0,[company_a.id,company_b.id])]
        })

        #Createequipmentuser
        user=ResUsers.create({
            'name':'NormalUser/Employee',
            'company_id':company_b.id,
            'login':'emp',
            'email':'empuser@yourcompany.example.com',
            'groups_id':[(6,0,[group_user.id])],
            'company_ids':[(6,0,[company_b.id])]
        })

        #createamaintenanceteamforcompanyAuser
        team=MaintenanceTeam.with_user(equipment_manager).create({
            'name':'Metrology',
            'company_id':company_a.id,
        })
        #createamaintenanceteamforcompanyBuser
        teamb=MaintenanceTeam.with_user(equipment_manager).with_context(allowed_company_ids=cids).create({
            'name':'Subcontractor',
            'company_id':company_b.id,
        })

        #Usershouldnotabletocreateequipmentcategory.
        withself.assertRaises(AccessError):
            Category.with_user(user).create({
                'name':'Software',
                'company_id':company_b.id,
                'technician_user_id':user.id,
            })

        #createequipmentcategoryforequipmentmanager
        category_1=Category.with_user(equipment_manager).with_context(allowed_company_ids=cids).create({
            'name':'Monitors-Test',
            'company_id':company_b.id,
            'technician_user_id':equipment_manager.id,
        })

        #createequipmentcategoryforequipmentmanager
        Category.with_user(equipment_manager).with_context(allowed_company_ids=cids).create({
            'name':'Computers-Test',
            'company_id':company_b.id,
            'technician_user_id':equipment_manager.id,
        })

        #createequipmentcategoryforequipmentuser
        Category.with_user(equipment_manager).create({
            'name':'Phones-Test',
            'company_id':company_a.id,
            'technician_user_id':equipment_manager.id,
        })

        #Checkcategoryforuserequipment_manageranduser
        self.assertEqual(Category.with_user(equipment_manager).with_context(allowed_company_ids=cids).search_count([]),3)
        self.assertEqual(Category.with_user(user).search_count([]),2)

        #Usershouldnotabletocreateequipment.
        withself.assertRaises(AccessError):
            Equipment.with_user(user).create({
                'name':'SamsungMonitor15',
                'category_id':category_1.id,
                'assign_date':time.strftime('%Y-%m-%d'),
                'company_id':company_b.id,
                'owner_user_id':user.id,
            })

        Equipment.with_user(equipment_manager).with_context(allowed_company_ids=cids).create({
            'name':'AcerLaptop',
            'category_id':category_1.id,
            'assign_date':time.strftime('%Y-%m-%d'),
            'company_id':company_b.id,
            'owner_user_id':user.id,
        })

        #createanequipmentforuser
        Equipment.with_user(equipment_manager).with_context(allowed_company_ids=cids).create({
            'name':'HPLaptop',
            'category_id':category_1.id,
            'assign_date':time.strftime('%Y-%m-%d'),
            'company_id':company_b.id,
            'owner_user_id':equipment_manager.id,
        })
        #Nowtherearetotal2equipmentscreatedandcanviewbyequipment_manageruser
        self.assertEqual(Equipment.with_user(equipment_manager).with_context(allowed_company_ids=cids).search_count([]),2)

        #Andthereistotal1equipmentcanbeviewbyNormalUser(Whichuserisfollowers)
        self.assertEqual(Equipment.with_user(user).search_count([]),1)

        #createanequipmentteamBYuser
        withself.assertRaises(AccessError):
            MaintenanceTeam.with_user(user).create({
                'name':'Subcontractor',
                'company_id':company_b.id,
            })

        #createanequipmentcategoryBYuser
        withself.assertRaises(AccessError):
            Category.with_user(user).create({
                'name':'Computers',
                'company_id':company_b.id,
                'technician_user_id':user.id,
            })

        #createanmaintenancestageBYuser
        withself.assertRaises(AccessError):
            self.env['maintenance.stage'].with_user(user).create({
                'name':'identifycorrectivemaintenancerequirements',
            })

        #Createanmaintenancerequestfor(UserFollower).
        MaintenanceRequest.with_user(user).create({
            'name':'Somekeysarenotworking',
            'company_id':company_b.id,
            'user_id':user.id,
            'owner_user_id':user.id,
        })

        #Createanmaintenancerequestforequipment_manager(AdminFollower)
        MaintenanceRequest.with_user(equipment_manager).create({
            'name':'Batterydrainsfast',
            'company_id':company_a.id,
            'user_id':equipment_manager.id,
            'owner_user_id':equipment_manager.id,
        })

        #Nowhereistotal1maintenancerequestcanbeviewbyNormalUser
        self.assertEqual(MaintenanceRequest.with_user(equipment_manager).with_context(allowed_company_ids=cids).search_count([]),2)
        self.assertEqual(MaintenanceRequest.with_user(user).search_count([]),1)
