#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classHrEmployee(models.Model):
    _inherit='hr.employee'

    timesheet_cost=fields.Monetary('TimesheetCost',currency_field='currency_id',
    	groups="hr.group_hr_user",default=0.0)
    currency_id=fields.Many2one('res.currency',related='company_id.currency_id',readonly=True)
