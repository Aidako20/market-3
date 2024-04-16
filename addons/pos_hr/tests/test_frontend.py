#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttools
fromflectra.apiimportEnvironment
fromflectra.toolsimportDEFAULT_SERVER_DATE_FORMAT
fromdatetimeimportdate,timedelta

fromflectra.testsimportForm,tagged,new_test_user
fromflectra.addons.point_of_sale.tests.test_frontendimportTestPointOfSaleHttpCommon


classTestPosHrHttpCommon(TestPointOfSaleHttpCommon):
    defsetUp(self):
        super().setUp()
        self.main_pos_config.write({"module_pos_hr":True})

        #Adminemployee
        self.env.ref("hr.employee_admin").write(
            {"name":"MitchellAdmin","pin":False}
        )

        #Useremployee
        emp1=self.env.ref("hr.employee_han")
        emp1_user=new_test_user(
            self.env,
            login="emp1_user",
            groups="base.group_user",
            name="PosEmployee1",
            email="emp1_user@pos.com",
        )
        emp1.write({"name":"PosEmployee1","pin":"2580","user_id":emp1_user.id})

        #Non-useremployee
        emp2=self.env.ref("hr.employee_jve")
        emp2.write({"name":"PosEmployee2","pin":"1234"})

        withForm(self.main_pos_config)asconfig:
            config.employee_ids.add(emp1)
            config.employee_ids.add(emp2)


@tagged("post_install","-at_install")
classTestUi(TestPosHrHttpCommon):
    deftest_01_pos_hr_tour(self):
        #openasession,the/pos/uicontrollerwillredirecttoit
        self.main_pos_config.open_session_cb(check_coa=False)

        self.start_tour(
            "/pos/ui?config_id=%d"%self.main_pos_config.id,
            "PosHrTour",
            login="admin",
        )
