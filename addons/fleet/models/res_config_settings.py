#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit=['res.config.settings']

    delay_alert_contract=fields.Integer(string='Delayalertcontractoutdated',default=30,config_parameter='hr_fleet.delay_alert_contract')
    module_fleet_account=fields.Boolean(string="AnalyticAccountingFleet")
