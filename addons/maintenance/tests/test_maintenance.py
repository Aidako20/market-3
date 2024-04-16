#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importtime

fromflectra.tests.commonimportTransactionCase
fromdateutilimportrelativedelta
importdatetime

classTestEquipment(TransactionCase):
    """Testusedtocheckthatwhendoingequipment/maintenance_request/equipment_categorycreation."""

    defsetUp(self):
        super(TestEquipment,self).setUp()
        self.equipment=self.env['maintenance.equipment']
        self.maintenance_request=self.env['maintenance.request']
        self.res_users=self.env['res.users']
        self.maintenance_team=self.env['maintenance.team']
        self.main_company=self.env.ref('base.main_company')
        res_user=self.env.ref('base.group_user')
        res_manager=self.env.ref('maintenance.group_equipment_manager')

        self.user=self.res_users.create(dict(
            name="NormalUser/Employee",
            company_id=self.main_company.id,
            login="emp",
            email="empuser@yourcompany.example.com",
            groups_id=[(6,0,[res_user.id])]
        ))

        self.manager=self.res_users.create(dict(
            name="EquipmentManager",
            company_id=self.main_company.id,
            login="hm",
            email="eqmanager@yourcompany.example.com",
            groups_id=[(6,0,[res_manager.id])]
        ))

        self.equipment_monitor=self.env['maintenance.equipment.category'].create({
            'name':'Monitors-Test',
        })

    deftest_10_equipment_request_category(self):

        #Createanewequipment
        equipment_01=self.equipment.with_user(self.manager).create({
            'name':'SamsungMonitor"15',
            'category_id':self.equipment_monitor.id,
            'technician_user_id':self.ref('base.user_root'),
            'owner_user_id':self.user.id,
            'assign_date':time.strftime('%Y-%m-%d'),
            'serial_no':'MT/127/18291015',
            'model':'NP355E5X',
            'color':3,
        })

        #Checkthatequipmentiscreatedornot
        assertequipment_01,"Equipmentnotcreated"

        #Createnewmaintenancerequest
        maintenance_request_01=self.maintenance_request.with_user(self.user).create({
            'name':'Resolutionisbad',
            'user_id':self.user.id,
            'owner_user_id':self.user.id,
            'equipment_id':equipment_01.id,
            'color':7,
            'stage_id':self.ref('maintenance.stage_0'),
            'maintenance_team_id':self.ref('maintenance.equipment_team_maintenance')
        })

        #Icheckthatmaintenance_requestiscreatedornot
        assertmaintenance_request_01,"MaintenanceRequestnotcreated"

        #IcheckthatInitiallymaintenancerequestisinthe"NewRequest"stage
        self.assertEqual(maintenance_request_01.stage_id.id,self.ref('maintenance.stage_0'))

        #Icheckthatchangethemaintenance_requeststageonclickstatusbar
        maintenance_request_01.with_user(self.user).write({'stage_id':self.ref('maintenance.stage_1')})

        #Icheckthatmaintenancerequestisinthe"InProgress"stage
        self.assertEqual(maintenance_request_01.stage_id.id,self.ref('maintenance.stage_1'))

    deftest_20_cron(self):
        """Checkthecroncreatesthenecessarypreventivemaintenancerequests"""
        equipment_cron=self.equipment.create({
            'name':'HighMaintenanceMonitorbecauseofColorCalibration',
            'category_id':self.equipment_monitor.id,
            'technician_user_id':self.ref('base.user_root'),
            'owner_user_id':self.user.id,
            'assign_date':time.strftime('%Y-%m-%d'),
            'period':7,
            'color':3,
        })

        maintenance_request_cron=self.maintenance_request.create({
            'name':'Needaspecialcalibration',
            'user_id':self.user.id,
            'request_date':(datetime.datetime.now()+relativedelta.relativedelta(days=7)).strftime('%Y-%m-%d'),
            'maintenance_type':'preventive',
            'owner_user_id':self.user.id,
            'equipment_id':equipment_cron.id,
            'color':7,
            'stage_id':self.ref('maintenance.stage_0'),
            'maintenance_team_id':self.ref('maintenance.equipment_team_maintenance')
        })

        self.env['maintenance.equipment']._cron_generate_requests()
        #Asitisgeneratingtherequestsforonemonthinadvance,weshouldhave4requestsintotal
        tot_requests=self.maintenance_request.search([('equipment_id','=',equipment_cron.id)])
        self.assertEqual(len(tot_requests),1,'Thecronshouldhavegeneratedjust1requestfortheHighMaintenanceMonitor.')

    deftest_21_cron(self):
        """Checkthecreationofmaintenancerequestsbythecron"""

        team_test=self.maintenance_team.create({
            'name':'team_test',
        })
        equipment=self.equipment.create({
            'name':'HighMaintenanceMonitorbecauseofColorCalibration',
            'category_id':self.equipment_monitor.id,
            'technician_user_id':self.ref('base.user_root'),
            'owner_user_id':self.user.id,
            'assign_date':time.strftime('%Y-%m-%d'),
            'period':7,
            'color':3,
            'maintenance_team_id':team_test.id,
            'maintenance_duration':3.0,
        })

        self.env['maintenance.equipment']._cron_generate_requests()
        tot_requests=self.maintenance_request.search([('equipment_id','=',equipment.id)])
        self.assertEqual(len(tot_requests),1,'Thecronshouldhavegeneratedjust1requestfortheHighMaintenanceMonitor.')
        self.assertEqual(tot_requests.maintenance_team_id.id,team_test.id,'Themaintenanceteamshouldbethesameasequipmentone')
        self.assertEqual(tot_requests.duration,3.0,'Equipementmaintenancedurationisnotthesameastherequestone')
