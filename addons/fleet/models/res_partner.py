#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResPartner(models.Model):
    _inherit='res.partner'

    plan_to_change_car=fields.Boolean('PlanToChangeCar',default=False)
