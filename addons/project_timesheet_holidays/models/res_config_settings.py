#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    leave_timesheet_project_id=fields.Many2one(
        related='company_id.leave_timesheet_project_id',required=True,string="InternalProject",
        domain="[('company_id','=',company_id)]",readonly=False)
    leave_timesheet_task_id=fields.Many2one(
        related='company_id.leave_timesheet_task_id',string="TimeOffTask",readonly=False,
        domain="[('company_id','=',company_id),('project_id','=?',leave_timesheet_project_id)]")

    @api.onchange('leave_timesheet_project_id')
    def_onchange_timesheet_project_id(self):
        ifself.leave_timesheet_project_id!=self.leave_timesheet_task_id.project_id:
            self.leave_timesheet_task_id=False

    @api.onchange('leave_timesheet_task_id')
    def_onchange_timesheet_task_id(self):
        ifself.leave_timesheet_task_id:
            self.leave_timesheet_project_id=self.leave_timesheet_task_id.project_id
