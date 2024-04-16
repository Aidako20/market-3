#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta

fromflectraimportapi,fields,models


classHrDepartureWizard(models.TransientModel):
    _inherit='hr.departure.wizard'

    cancel_leaves=fields.Boolean("CancelFutureLeaves",default=True)

    defaction_register_departure(self):
        super(HrDepartureWizard,self).action_register_departure()
        ifself.cancel_leaves:
            future_leaves=self.env['hr.leave'].search([('employee_id','=',self.employee_id.id),
                                                         ('date_to','>',self.departure_date),
                                                         ('state','notin',['cancel','refuse'])])
            future_leaves.write({'state':'cancel'})
