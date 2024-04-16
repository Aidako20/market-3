#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.testsimportcommon,new_test_user


classTestFleet(common.SavepointCase):

    deftest_manager_create_vehicle(self):
        manager=new_test_user(self.env,"testfleetmanager",groups="fleet.fleet_group_manager,base.group_partner_manager")
        user=new_test_user(self.env,"testbaseuser",groups="base.group_user")
        brand=self.env["fleet.vehicle.model.brand"].create({
            "name":"Audi",
        })
        model=self.env["fleet.vehicle.model"].create({
            "brand_id":brand.id,
            "name":"A3",
        })
        car=self.env["fleet.vehicle"].with_user(manager).create({
            "model_id":model.id,
            "driver_id":user.partner_id.id,
            "plan_to_change_car":False
        })
        car.with_user(manager).plan_to_change_car=True
