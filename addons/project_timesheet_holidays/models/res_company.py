#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classCompany(models.Model):
    _inherit='res.company'

    leave_timesheet_project_id=fields.Many2one(
        'project.project',string="InternalProject",
        help="Defaultprojectvaluefortimesheetgeneratedfromtimeofftype.")
    leave_timesheet_task_id=fields.Many2one(
        'project.task',string="TimeOffTask",
        domain="[('project_id','=',leave_timesheet_project_id)]")

    @api.constrains('leave_timesheet_project_id')
    def_check_leave_timesheet_project_id_company(self):
        forcompanyinself:
            ifcompany.leave_timesheet_project_id:
                ifcompany.leave_timesheet_project_id.sudo().company_id!=company:
                    raiseValidationError(_('TheInternalProjectofacompanyshouldbeinthatcompany.'))

    definit(self):
        forcompanyinself.search([('leave_timesheet_project_id','=',False)]):
            company=company.with_company(company)
            project=company.env['project.project'].search([
                ('name','=',_('Internal')),
                ('allow_timesheets','=',True),
                ('company_id','=',company.id),
            ],limit=1)
            ifnotproject:
                project=company.env['project.project'].create({
                    'name':_('Internal'),
                    'allow_timesheets':True,
                    'company_id':company.id,
                })
            company.write({
                'leave_timesheet_project_id':project.id,
            })
            ifnotcompany.leave_timesheet_task_id:
                task=company.env['project.task'].create({
                    'name':_('TimeOff'),
                    'project_id':company.leave_timesheet_project_id.id,
                    'active':False,
                    'company_id':company.id,
                })
                company.write({
                    'leave_timesheet_task_id':task.id,
                })

    def_create_internal_project_task(self):
        projects=super()._create_internal_project_task()
        forprojectinprojects:
            company=project.company_id
            company=company.with_company(company)
            ifnotcompany.leave_timesheet_project_id:
                company.write({
                    'leave_timesheet_project_id':project.id,
                })
            ifnotcompany.leave_timesheet_task_id:
                task=company.env['project.task'].sudo().create({
                    'name':_('TimeOff'),
                    'project_id':company.leave_timesheet_project_id.id,
                    'active':False,
                    'company_id':company.id,
                })
                company.write({
                    'leave_timesheet_task_id':task.id,
                })
